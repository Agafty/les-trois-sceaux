using System.Collections.Generic;
using Godot;

/// <summary>
/// Mur fissuré ou éboulis (classe Tiled « MurFissure ») qu'une bombe fait disparaître. Un corps solide qui remplit son rectangle Tiled,
/// dans le groupe « destructible_bombe » (<see cref="IBombDestructible"/>) : la bombe à portée appelle <see cref="OnBombExplosion"/>.
/// - Apparence « mur » (défaut) ou « eboulis ». L'état « détruit » est mémorisé dans GameState sous l'Id (MarkCollected) ;
///   une salle rechargée montre donc directement le passage ouvert.
/// - Le dessin vient du tileset de la carte : si la tuile sous le rectangle est une tuile fermée connue (village 136-139 et 142, intérieurs 67,
///   voir <see cref="TileRules"/>), elle est retirée du calque « Murs » à la destruction et remplacée par la version ouverte si le tileset en a une.
///   Si la carte a déjà posé la tuile ouverte dessous (143, 140, 141), le mur dessine lui-même la tuile fermée par-dessus, qui disparaît à la destruction.
///   Sans aucune tuile reconnue, il dessine art/puzzles/porte_eboulis.png (éboulis) ou un placeholder.
/// - Une Sortie posée sous le même rectangle n'est active qu'une fois le mur détruit (la Room le vérifie).
/// </summary>
public partial class CrackedWall : StaticBody2D, IBombDestructible
{
    /// <summary>Le mur vient d'être détruit (pas émis quand il est déjà détruit au chargement de la salle).</summary>
    [Signal]
    public delegate void DestroyedEventHandler(string wallId);

    /// <summary>Identifiant unique, ex. « village_mur_fissure_cave ». Vide : le mur se détruit mais l'état n'est pas mémorisé.</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>« mur » (défaut) ou « eboulis ».</summary>
    [Export] public string Appearance { get; set; } = WallRules.DefaultAppearance;

    /// <summary>Taille du rectangle (px). Réglée par la Room d'après le rectangle Tiled.</summary>
    [Export] public Vector2 CellSize { get; set; } = new(32f, 32f);

    /// <summary>Calques de la carte, réglés par la Room avant l'entrée dans l'arbre (nuls : le mur dessine un placeholder).</summary>
    public TileMapLayer WallsLayer { get; set; }
    public TileMapLayer FloorLayer { get; set; }
    public TileMapLayer DecorLayer { get; set; }

    public bool IsDestroyed => _destroyed;

    /// <summary>Demi-taille du rectangle : la bombe mesure sa portée jusqu'au bord (voir <see cref="IBombDestructible"/>).</summary>
    public Vector2 BombHalfExtents => CellSize * 0.5f;

    private sealed class ClosedCell
    {
        public Vector2I Cell;
        public string Tileset;
        public int TileId;
    }

    private GameState _state;
    private CollisionShape2D _shape;
    private readonly List<ClosedCell> _closedCells = new(); // tuiles fermées du calque Murs, à retirer
    private readonly List<Sprite2D> _overlays = new();     // tuiles fermées dessinées par le mur lui-même
    private Sprite2D _fallback;
    private bool _destroyed;

    public override void _Ready()
    {
        AddToGroup(Bomb.DestructibleGroup);
        _state = GetNode<GameState>("/root/GameState");
        _shape = GetNode<CollisionShape2D>("CollisionShape2D");
        if (string.IsNullOrEmpty(Id))
            GD.PushWarning($"MurFissure sans Id ({GetPath()}) : son état ne sera pas mémorisé.");

        if (_shape.Shape is RectangleShape2D rect && rect.Size != CellSize)
        {
            var copy = (RectangleShape2D)rect.Duplicate(); // la forme de la scène est partagée entre instances
            copy.Size = CellSize;
            _shape.Shape = copy;
        }

        ScanTiles();
        if (!string.IsNullOrEmpty(Id) && _state.IsCollected(Id))
        {
            ApplyDestroyed(false);
            return;
        }
        if (_closedCells.Count == 0 && _overlays.Count == 0)
            SetupFallbackSprite();
    }

    public void OnBombExplosion(Vector2 center)
    {
        if (_destroyed) return;
        ApplyDestroyed(true);
        if (!string.IsNullOrEmpty(Id)) _state.MarkCollected(Id);
        EmitSignal(SignalName.Destroyed, Id);
    }

    // --- Tuiles -----------------------------------------------------------------------------------

    private void ScanTiles()
    {
        if (WallsLayer?.TileSet == null) return;
        var topLeft = GlobalPosition - CellSize * 0.5f + new Vector2(1f, 1f);
        var bottomRight = GlobalPosition + CellSize * 0.5f - new Vector2(1f, 1f);
        var first = WallsLayer.LocalToMap(WallsLayer.ToLocal(topLeft));
        var last = WallsLayer.LocalToMap(WallsLayer.ToLocal(bottomRight));
        for (int y = first.Y; y <= last.Y; y++)
        {
            for (int x = first.X; x <= last.X; x++)
            {
                var cell = new Vector2I(x, y);
                string tileset;
                int tileId;
                if (TryReadTile(WallsLayer, cell, out tileset, out tileId))
                {
                    if (TileRules.IsBreakable(tileset, tileId))
                    {
                        _closedCells.Add(new ClosedCell { Cell = cell, Tileset = tileset, TileId = tileId });
                        continue;
                    }
                    if (TileRules.TryGetClosedTile(tileset, tileId, out int closedId))
                    {
                        AddOverlay(cell, tileset, closedId);
                        continue;
                    }
                }
                // Tuile ouverte déjà posée dans « Decor » (mur ouvert) ou « Sol » (éboulis dégagé) : on dessine la fermée par-dessus.
                if (DecorLayer != null && TryReadTile(DecorLayer, cell, out tileset, out tileId)
                    && TileRules.TryGetClosedTile(tileset, tileId, out int closedFromDecor))
                {
                    AddOverlay(cell, tileset, closedFromDecor);
                    continue;
                }
                if (FloorLayer != null && TryReadTile(FloorLayer, cell, out tileset, out tileId)
                    && TileRules.TryGetClosedTile(tileset, tileId, out int closedFromFloor))
                    AddOverlay(cell, tileset, closedFromFloor);
            }
        }
    }

    private static bool TryReadTile(TileMapLayer layer, Vector2I cell, out string tileset, out int tileId)
    {
        tileset = "";
        tileId = -1;
        int source = layer.GetCellSourceId(cell);
        if (source < 0 || layer.TileSet.GetSource(source) is not TileSetAtlasSource atlas || atlas.Texture == null) return false;
        var coords = layer.GetCellAtlasCoords(cell);
        tileset = TileRules.TilesetNameFromTexturePath(atlas.Texture.ResourcePath);
        tileId = TileRules.TileId(coords.X, coords.Y, atlas.GetAtlasGridSize().X);
        return tileset != "";
    }

    private static bool FindAtlas(TileSet tileSet, string tilesetName, out int sourceId, out TileSetAtlasSource atlas)
    {
        for (int i = 0; i < tileSet.GetSourceCount(); i++)
        {
            int id = tileSet.GetSourceId(i);
            if (tileSet.GetSource(id) is TileSetAtlasSource candidate && candidate.Texture != null
                && TileRules.TilesetNameFromTexturePath(candidate.Texture.ResourcePath) == tilesetName)
            {
                sourceId = id;
                atlas = candidate;
                return true;
            }
        }
        sourceId = -1;
        atlas = null;
        return false;
    }

    private void AddOverlay(Vector2I cell, string tileset, int closedId)
    {
        if (!FindAtlas(WallsLayer.TileSet, tileset, out _, out var atlas)) return;
        int columns = atlas.GetAtlasGridSize().X;
        var tileSize = WallsLayer.TileSet.TileSize;
        var sprite = new Sprite2D
        {
            Texture = atlas.Texture,
            RegionEnabled = true,
            RegionRect = new Rect2(closedId % columns * tileSize.X, closedId / columns * tileSize.Y, tileSize.X, tileSize.Y),
        };
        AddChild(sprite);
        sprite.GlobalPosition = WallsLayer.ToGlobal(WallsLayer.MapToLocal(cell));
        _overlays.Add(sprite);
    }

    // Place la version ouverte d'une tuile dans son calque (« Sol » pour l'éboulis dégagé, « Decor » pour le mur ouvert).
    private void PlaceOpenedTile(Vector2I cell, string tileset, int openId, string layerName)
    {
        var layer = layerName == "Sol" ? FloorLayer : DecorLayer;
        if (layer?.TileSet == null || !FindAtlas(layer.TileSet, tileset, out int sourceId, out var atlas)) return;
        int columns = atlas.GetAtlasGridSize().X;
        layer.SetCell(cell, sourceId, new Vector2I(openId % columns, openId / columns));
    }

    // --- Image de secours -------------------------------------------------------------------------

    private void SetupFallbackSprite()
    {
        int w = Mathf.Max(1, Mathf.RoundToInt(CellSize.X));
        int h = Mathf.Max(1, Mathf.RoundToInt(CellSize.Y));
        string path = $"res://art/puzzles/porte_{Appearance}.png";
        Texture2D texture = Appearance == WallRules.RubbleAppearance && ResourceLoader.Exists(path)
            ? GD.Load<Texture2D>(path)
            : PlaceholderTexture(Appearance, w, h);
        _fallback = new Sprite2D { Texture = texture, Hframes = Mathf.Clamp(texture.GetWidth() / w, 1, 2) };
        AddChild(_fallback);
    }

    private static Texture2D PlaceholderTexture(string appearance, int w, int h)
    {
        var image = Image.CreateEmpty(w, h, false, Image.Format.Rgba8);
        var stone = appearance == WallRules.RubbleAppearance ? new Color(0.5f, 0.5f, 0.54f) : new Color(0.42f, 0.4f, 0.46f);
        var dark = new Color(0.11f, 0.08f, 0.13f);
        image.FillRect(new Rect2I(0, 0, w, h), stone);
        image.FillRect(new Rect2I(0, 0, w, 2), dark);
        image.FillRect(new Rect2I(0, h - 2, w, 2), dark);
        for (int y = 4; y < h - 4; y += 3) // une fissure en zigzag
            image.FillRect(new Rect2I(w / 2 + ((y / 3) % 2 == 0 ? -3 : 3), y, 2, 3), dark);
        return ImageTexture.CreateFromImage(image);
    }

    // --- Destruction ------------------------------------------------------------------------------

    private void ApplyDestroyed(bool animate)
    {
        _destroyed = true;
        RemoveFromGroup(Bomb.DestructibleGroup);
        _shape.SetDeferred(CollisionShape2D.PropertyName.Disabled, true);
        foreach (var closed in _closedCells)
        {
            WallsLayer.EraseCell(closed.Cell);
            if (TileRules.TryGetOpenedTile(closed.Tileset, closed.TileId, out int openId, out string layerName))
                PlaceOpenedTile(closed.Cell, closed.Tileset, openId, layerName);
        }
        foreach (var overlay in _overlays) overlay.Visible = false;
        if (_fallback != null) _fallback.Visible = false;
        if (animate)
        {
            AudioManager.PlayAt(Sfx.Eboulement, GlobalPosition);
            SpawnDebris();
            if (GetViewport().GetCamera2D() is CameraShake shake) shake.Shake(2f, 0.2f);
        }
    }

    // Petits cailloux gris qui retombent (un seul jet, effacé tout seul).
    private void SpawnDebris()
    {
        var debris = new CpuParticles2D
        {
            Emitting = true,
            OneShot = true,
            Amount = 18,
            Lifetime = 0.7,
            Explosiveness = 1f,
            EmissionShape = CpuParticles2D.EmissionShapeEnum.Rectangle,
            EmissionRectExtents = CellSize * 0.5f,
            Direction = new Vector2(0f, -1f),
            Spread = 180f,
            InitialVelocityMin = 25f,
            InitialVelocityMax = 70f,
            Gravity = new Vector2(0f, 180f),
            ScaleAmountMin = 2f,
            ScaleAmountMax = 4f,
            Color = new Color(0.55f, 0.53f, 0.58f),
        };
        AddChild(debris);
        debris.Finished += debris.QueueFree;
    }
}
