using System.Collections.Generic;
using Godot;

/// <summary>
/// Comportements de certaines tuiles du calque « Murs », reconnues par leur numéro (voir <see cref="TileRules"/>), sans rien
/// modifier dans les cartes .tmx. Créé et réglé par la <see cref="Room"/>.
/// - Buissons (foret 96-99, village 300) : une zone <see cref="BushCutter"/> est posée sur chaque case ; un coup d'épée retire la tuile
///   (pour cette visite de la salle seulement : la salle est rechargée depuis la carte), avec un bruit, des feuilles et parfois un butin.
/// - Ravins (village 80-95) : les flèches doivent passer au-dessus d'un ravin, comme au-dessus d'un trou, alors que Brann et les
///   ennemis ne le traversent pas. Or la collision d'une tuile est celle du tileset (couche 1, celle que les flèches voient). On sépare donc
///   les deux : les tuiles de ravin passent dans un calque « Ravin » qui ne fait que l'affichage, et leur collision (lue sur les polygones
///   du tileset) est refaite dans un corps statique de la couche 5 (<see cref="PhysicsLayers.Ravine"/>), que Brann et les ennemis ont dans leur masque.
/// </summary>
public partial class TileFeatures : Node2D
{
    /// <summary>Calque « Murs » de la carte.</summary>
    public TileMapLayer Walls { get; set; }

    /// <summary>Conteneur d'entités (tri en profondeur) où tombent les butins.</summary>
    public Node2D Entities { get; set; }

    private const string BushLootPath = "res://resources/loot/buisson.tres";

    private readonly Dictionary<Vector2I, BushCutter> _bushes = new();
    private readonly Dictionary<Vector2I, List<CollisionShape2D>> _ravineShapes = new();
    private TileMapLayer _ravineLayer;
    private StaticBody2D _ravineBody;
    private LootTable _bushLoot;
    private bool _lootLoaded;
    private int _bushCount;
    private int _ravineCount;

    /// <summary>Nombre de buissons coupables trouvés au chargement.</summary>
    public int BushCount => _bushCount;

    /// <summary>Nombre de cases de ravin trouvées au chargement.</summary>
    public int RavineCount => _ravineCount;

    /// <summary>Nombre de buissons encore debout.</summary>
    public int BushesLeft => _bushes.Count;

    /// <summary>Parcourt le calque une fois, au chargement de la salle.</summary>
    public void Setup()
    {
        if (Walls?.TileSet == null) return;

        // Sources d'atlas reconnues : id de source -> (nom du tileset, nombre de colonnes).
        var tileSet = Walls.TileSet;
        var sources = new Dictionary<int, (string Name, int Columns)>();
        for (int i = 0; i < tileSet.GetSourceCount(); i++)
        {
            int id = tileSet.GetSourceId(i);
            if (tileSet.GetSource(id) is not TileSetAtlasSource atlas || atlas.Texture == null) continue;
            string name = TileRules.TilesetNameFromTexturePath(atlas.Texture.ResourcePath);
            if (name == TileRules.ForestTileset || name == TileRules.VillageTileset)
                sources[id] = (name, atlas.GetAtlasGridSize().X);
        }
        if (sources.Count == 0) return;

        var ravineCells = new List<Vector2I>();
        foreach (var cell in Walls.GetUsedCells())
        {
            if (!sources.TryGetValue(Walls.GetCellSourceId(cell), out var source)) continue;
            var atlasCoords = Walls.GetCellAtlasCoords(cell);
            int tileId = TileRules.TileId(atlasCoords.X, atlasCoords.Y, source.Columns);
            if (TileRules.IsBush(source.Name, tileId))
                AddBush(cell);
            else if (TileRules.IsRavine(source.Name, tileId))
                ravineCells.Add(cell);
        }
        if (ravineCells.Count > 0)
            MoveRavineToOwnLayer(ravineCells);
    }

    // --- Buissons ---------------------------------------------------------------------------------

    private void AddBush(Vector2I cell)
    {
        var size = Walls.TileSet.TileSize;
        var cutter = new BushCutter
        {
            Name = $"Buisson_{cell.X}_{cell.Y}",
            Cell = cell,
            CollisionLayer = 1, // la couche vue par la HitBox de l'épée
            CollisionMask = 0,
            Monitoring = false, // elle est détectée, elle ne détecte rien
        };
        cutter.AddChild(new CollisionShape2D { Shape = new RectangleShape2D { Size = new Vector2(size.X, size.Y) } });
        AddChild(cutter);
        cutter.GlobalPosition = Walls.ToGlobal(Walls.MapToLocal(cell));
        cutter.CutRequested += OnCutRequested;
        _bushes[cell] = cutter;
        _bushCount++;
    }

    // Appelé pendant un calcul de physique (la HitBox de l'épée) : on modifie la carte et on crée des zones un peu plus tard.
    private void OnCutRequested(Vector2I cell) => Callable.From(() => CutBush(cell)).CallDeferred();

    /// <summary>Coupe le buisson de cette case (retire la tuile, bruit, feuilles, butin). Sans effet s'il n'y en a plus. Public pour les tests.</summary>
    public void CutBush(Vector2I cell)
    {
        if (!IsInstanceValid(Walls) || !_bushes.Remove(cell, out var cutter)) return;
        Walls.EraseCell(cell);
        var center = cutter.GlobalPosition;
        if (IsInstanceValid(cutter)) cutter.QueueFree();

        AudioManager.PlayAt(Sfx.Buisson, center);
        SpawnLeaves(center);
        DropLoot(center);
    }

    private void SpawnLeaves(Vector2 center)
    {
        var leaves = new CpuParticles2D
        {
            Position = ToLocal(center),
            Emitting = true,
            OneShot = true,
            Amount = 10,
            Lifetime = 0.5,
            Explosiveness = 1f,
            Direction = Vector2.Up,
            Spread = 180f,
            InitialVelocityMin = 30f,
            InitialVelocityMax = 70f,
            Gravity = new Vector2(0f, 160f),
            ScaleAmountMin = 2f,
            ScaleAmountMax = 4f,
            Color = new Color(0.36f, 0.62f, 0.25f),
            ZIndex = 1,
        };
        leaves.Finished += leaves.QueueFree;
        AddChild(leaves);
    }

    private void DropLoot(Vector2 center)
    {
        if (!_lootLoaded)
        {
            _lootLoaded = true;
            _bushLoot = ResourceKeeper.Load<LootTable>(BushLootPath);
            LootDropper.PinTable(_bushLoot); // les lignes (LootEntry) sont aussi des ressources C#
        }
        var scene = _bushLoot?.Roll();
        if (scene == null || Entities == null || !IsInstanceValid(Entities)) return;
        var loot = scene.Instantiate<Node2D>();
        if (loot is Pickup pickup) ResourceKeeper.Pin(pickup.Effect);
        Entities.AddChild(loot);
        loot.GlobalPosition = center;
    }

    // --- Ravins -----------------------------------------------------------------------------------

    private void MoveRavineToOwnLayer(List<Vector2I> cells)
    {
        _ravineLayer = new TileMapLayer
        {
            Name = "Ravin",
            TileSet = Walls.TileSet,
            Position = Walls.Position,
            ZIndex = Walls.ZIndex,
            YSortEnabled = Walls.YSortEnabled,
            YSortOrigin = Walls.YSortOrigin,
            Modulate = Walls.Modulate,
            CollisionEnabled = false, // affichage seulement : la collision est dans _ravineBody
        };
        var parent = Walls.GetParent();
        parent.AddChild(_ravineLayer);
        parent.MoveChild(_ravineLayer, Walls.GetIndex() + 1);

        _ravineBody = new StaticBody2D { Name = "CorpsRavin", CollisionLayer = PhysicsLayers.Ravine, CollisionMask = 0 };
        AddChild(_ravineBody);
        _ravineBody.GlobalPosition = Vector2.Zero; // les formes sont données en coordonnées du monde

        foreach (var cell in cells)
        {
            var data = Walls.GetCellTileData(cell);
            var center = Walls.ToGlobal(Walls.MapToLocal(cell));
            var shapes = new List<CollisionShape2D>();
            int polygons = data != null ? data.GetCollisionPolygonsCount(0) : 0;
            for (int i = 0; i < polygons; i++)
            {
                var points = data.GetCollisionPolygonPoints(0, i); // relatifs au centre de la tuile
                if (points.Length < 3) continue;
                var world = new Vector2[points.Length];
                for (int p = 0; p < points.Length; p++) world[p] = points[p] + center;
                var shape = new CollisionShape2D { Shape = new ConvexPolygonShape2D { Points = world } };
                _ravineBody.AddChild(shape);
                shapes.Add(shape);
            }
            _ravineShapes[cell] = shapes;
            _ravineLayer.SetCell(cell, Walls.GetCellSourceId(cell), Walls.GetCellAtlasCoords(cell), Walls.GetCellAlternativeTile(cell));
            Walls.EraseCell(cell);
            _ravineCount++;
        }
    }

    /// <summary>
    /// Supprime la collision des cases de ravin dont le centre est dans ce rectangle (monde) : un pont-levis abaissé se pose sur le ravin.
    /// L'affichage ne change pas (c'est l'image du pont qui recouvre).
    /// </summary>
    public void ClearRavineUnder(Rect2 area)
    {
        if (_ravineShapes.Count == 0) return;
        var toClear = new List<Vector2I>();
        foreach (var pair in _ravineShapes)
        {
            var center = Walls.ToGlobal(Walls.MapToLocal(pair.Key));
            if (area.HasPoint(center)) toClear.Add(pair.Key);
        }
        foreach (var cell in toClear)
        {
            foreach (var shape in _ravineShapes[cell])
            {
                shape.SetDeferred(CollisionShape2D.PropertyName.Disabled, true);
                shape.QueueFree();
            }
            _ravineShapes.Remove(cell);
        }
    }
}
