using System.Collections.Generic;
using Godot;

/// <summary>
/// Surveille les trous d'une salle (tuiles du calque « Sol » reconnues par <see cref="HoleRules"/>) et fait tomber
/// Brann et les ennemis dont le centre des pieds est au-dessus d'une de ces tuiles. Créé par la <see cref="Room"/>.
/// - Brann : <see cref="Player.Fall"/> (animation, 1 PV de moins, retour au point d'entrée).
/// - Ennemi : il rétrécit puis disparaît, sans mourir (pas de butin) ; la salle le décompte quand il quitte l'arbre.
/// Les flèches et les bombes ne sont pas surveillées : elles passent au-dessus des trous.
/// Aucune chute pendant un changement de salle.
/// </summary>
public partial class HoleWatcher : Node
{
    /// <summary>Calque de tuiles du sol (« Sol ») contenant les trous.</summary>
    public TileMapLayer Floor { get; set; }

    public Player Player { get; set; }

    /// <summary>Où Brann réapparaît après une chute (point d'entrée de la salle).</summary>
    public Vector2 RespawnPosition { get; set; }

    /// <summary>Décalage (px) entre l'origine d'un personnage et le centre de ses pieds.</summary>
    [Export] public Vector2 FootOffset { get; set; } = Player.FeetOffset;

    /// <summary>Durée (s) de la chute d'un ennemi.</summary>
    [Export(PropertyHint.Range, "0.1,2,0.05")] public float EnemyFallDuration { get; set; } = 0.4f;

    private sealed class Tracked
    {
        public Node2D Node;
        public Health Health;
    }

    private readonly List<Tracked> _enemies = new();
    private SceneManager _sceneManager;
    // Sources d'atlas qui sont des tilesets de trous (temple_racines et sa variante sous-sol, même numérotation) -> nombre de colonnes.
    private readonly Dictionary<int, int> _holeSources = new();

    public override void _Ready()
    {
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        FindHoleSource();
        if (_holeSources.Count == 0)
        {
            SetPhysicsProcess(false); // cette salle n'utilise pas le tileset des trous
        }
    }

    /// <summary>Surveille un ennemi (appelé par la salle à sa création).</summary>
    public void Track(Node2D enemy)
    {
        _enemies.Add(new Tracked { Node = enemy, Health = enemy.GetNodeOrNull<Health>("Health") });
    }

    /// <summary>Vrai si la position (monde) est au-dessus d'une tuile de trou.</summary>
    public bool IsHoleAt(Vector2 worldPosition)
    {
        if (Floor == null || _holeSources.Count == 0) return false;
        var cell = Floor.LocalToMap(Floor.ToLocal(worldPosition));
        if (!_holeSources.TryGetValue(Floor.GetCellSourceId(cell), out int columns)) return false;
        var atlas = Floor.GetCellAtlasCoords(cell);
        return HoleRules.IsHoleTileId(HoleRules.TileId(atlas.X, atlas.Y, columns));
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_sceneManager.IsTransitioning) return;

        if (Player != null && IsInstanceValid(Player) && !Player.IsDead && IsHoleAt(Player.GlobalPosition + FootOffset))
            Player.Fall(RespawnPosition);

        for (int i = _enemies.Count - 1; i >= 0; i--)
        {
            var entry = _enemies[i];
            if (!IsInstanceValid(entry.Node) || entry.Node.IsQueuedForDeletion() || !entry.Node.IsInsideTree()
                || (entry.Health != null && IsInstanceValid(entry.Health) && entry.Health.CurrentHealth <= 0))
            {
                _enemies.RemoveAt(i); // mort ou déjà parti : plus de surveillance
                continue;
            }
            if (!IsHoleAt(entry.Node.GlobalPosition + FootOffset)) continue;

            _enemies.RemoveAt(i);
            StartEnemyFall(entry.Node);
        }
    }

    // L'ennemi est figé, rétrécit, puis disparaît sans butin (voir FallEffects.DropEnemy).
    private void StartEnemyFall(Node2D enemy) => FallEffects.DropEnemy(this, enemy, EnemyFallDuration);

    // Cherche, dans le tileset du calque, les sources d'atlas des trous (temple_racines et temple_racines_sous_sol).
    private void FindHoleSource()
    {
        var tileSet = Floor?.TileSet;
        if (tileSet == null) return;
        for (int i = 0; i < tileSet.GetSourceCount(); i++)
        {
            int id = tileSet.GetSourceId(i);
            if (tileSet.GetSource(id) is not TileSetAtlasSource atlas || atlas.Texture == null) continue;
            string path = atlas.Texture.ResourcePath;
            if (!path.EndsWith("/temple_racines.png") && !path.EndsWith("/temple_racines_sous_sol.png")) continue;
            _holeSources[id] = atlas.GetAtlasGridSize().X;
        }
    }
}
