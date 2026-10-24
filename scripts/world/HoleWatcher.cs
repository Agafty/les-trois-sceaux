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
    private int _holeSourceId = -1;
    private int _columns = 8;

    public override void _Ready()
    {
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        FindHoleSource();
        if (_holeSourceId < 0)
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
        if (Floor == null || _holeSourceId < 0) return false;
        var cell = Floor.LocalToMap(Floor.ToLocal(worldPosition));
        if (Floor.GetCellSourceId(cell) != _holeSourceId) return false;
        var atlas = Floor.GetCellAtlasCoords(cell);
        return HoleRules.IsHoleTileId(HoleRules.TileId(atlas.X, atlas.Y, _columns));
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

    // L'ennemi est figé, ne touche plus personne, rétrécit, puis est libéré SANS signal Died : pas de butin.
    // La salle voit son nœud quitter l'arbre et le compte comme parti (porte « ennemis »).
    private void StartEnemyFall(Node2D enemy)
    {
        enemy.ProcessMode = ProcessModeEnum.Disabled;
        if (enemy is CollisionObject2D body)
            body.CollisionLayer = 0;
        foreach (var child in enemy.GetChildren())
        {
            if (child is Area2D area)
            {
                area.SetDeferred(Area2D.PropertyName.Monitoring, false);
                area.SetDeferred(Area2D.PropertyName.Monitorable, false);
            }
        }

        // Tween rattaché à ce nœud (pas à l'ennemi, dont le traitement est désactivé).
        var tween = CreateTween();
        tween.SetParallel(true);
        tween.TweenProperty(enemy, "scale", new Vector2(0.1f, 0.1f), EnemyFallDuration);
        tween.TweenProperty(enemy, "modulate:a", 0f, EnemyFallDuration);
        tween.Chain().TweenCallback(Callable.From(() =>
        {
            if (IsInstanceValid(enemy)) enemy.QueueFree();
        }));
    }

    // Cherche, dans le tileset du calque, la source d'atlas qui est le tileset des trous (temple_racines).
    private void FindHoleSource()
    {
        var tileSet = Floor?.TileSet;
        if (tileSet == null) return;
        for (int i = 0; i < tileSet.GetSourceCount(); i++)
        {
            int id = tileSet.GetSourceId(i);
            if (tileSet.GetSource(id) is not TileSetAtlasSource atlas || atlas.Texture == null) continue;
            if (!atlas.Texture.ResourcePath.EndsWith("/temple_racines.png")) continue;
            _holeSourceId = id;
            _columns = atlas.GetAtlasGridSize().X;
            return;
        }
    }
}
