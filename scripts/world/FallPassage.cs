using System.Collections.Generic;
using Godot;

/// <summary>
/// Trou de passage (objet Tiled « Chute ») : quand le centre des pieds de Brann entre dans la zone, il tombe (même animation
/// qu'une fosse, mais sans perdre de PV), puis le jeu charge la carte <see cref="TargetScene"/> au Spawn <see cref="TargetSpawn"/>
/// (étage du dessous) ; Brann y arrive avec <see cref="ArrivalInvincibility"/> secondes d'invincibilité. Un ennemi dont le centre
/// des pieds entre dans la zone disparaît sans butin, comme dans une fosse. Ne pas confondre avec les tuiles 58 à 66
/// (fosse mortelle, voir <see cref="HoleRules"/> et <see cref="HoleWatcher"/>). La zone est une Area2D : elle ne bloque personne.
/// </summary>
public partial class FallPassage : Area2D
{
    /// <summary>Identifiant (ex. "donjon1_chute_01"), pour les messages.</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Chemin de la scène d'arrivée (propriété Tiled « cible_carte »).</summary>
    [Export(PropertyHint.File, "*.tscn")] public string TargetScene { get; set; } = "";

    /// <summary>Id du Spawn d'arrivée (propriété Tiled « cible_spawn »).</summary>
    [Export] public string TargetSpawn { get; set; } = "";

    /// <summary>Invincibilité (s) de Brann à son arrivée.</summary>
    [Export(PropertyHint.Range, "0,5,0.1")] public float ArrivalInvincibility { get; set; } = 1f;

    /// <summary>Durée (s) de la chute d'un ennemi.</summary>
    [Export(PropertyHint.Range, "0.1,2,0.05")] public float EnemyFallDuration { get; set; } = 0.4f;

    private readonly List<Node2D> _inside = new();
    private SceneManager _sceneManager;
    private GameState _state;
    private CollisionShape2D _shapeNode;
    private bool _targetExists;
    private System.Func<bool> _leave;
    private System.Action _grantInvincibility;

    public override void _Ready()
    {
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        _state = GetNode<GameState>("/root/GameState");
        _shapeNode = GetNode<CollisionShape2D>("CollisionShape2D");
        SetPhysicsProcess(false); // actif seulement quand un corps est dans la zone
        _leave = Leave; // délégués créés une seule fois
        _grantInvincibility = GrantArrivalInvincibility;
        _targetExists = !string.IsNullOrEmpty(TargetScene) && ResourceLoader.Exists(TargetScene);
        if (!_targetExists)
            GD.PushWarning($"Chute {Id} : la carte d'arrivée « {TargetScene} » n'existe pas : Brann ne tombera pas.");
        BodyEntered += OnBodyEntered;
        BodyExited += OnBodyExited;
    }

    public override void _ExitTree()
    {
        BodyEntered -= OnBodyEntered;
        BodyExited -= OnBodyExited;
    }

    private void OnBodyEntered(Node2D body)
    {
        // Brann et les ennemis (corps avec un nœud Health) ; les blocs, portes... sont ignorés.
        if (body is not Player && !(body is CharacterBody2D && body.HasNode("Health"))) return;
        if (!_inside.Contains(body)) _inside.Add(body);
        SetPhysicsProcess(true);
    }

    private void OnBodyExited(Node2D body)
    {
        _inside.Remove(body);
        if (_inside.Count == 0) SetPhysicsProcess(false);
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_sceneManager.IsTransitioning || _shapeNode.Shape is not RectangleShape2D rect) return;
        var area = new Rect2(_shapeNode.GlobalPosition - rect.Size * 0.5f, rect.Size);

        for (int i = _inside.Count - 1; i >= 0; i--)
        {
            var body = _inside[i];
            if (!IsInstanceValid(body) || !body.IsInsideTree() || body.IsQueuedForDeletion())
            {
                _inside.RemoveAt(i);
                continue;
            }
            if (!area.HasPoint(body.GlobalPosition + Player.FeetOffset)) continue;

            if (body is Player player)
            {
                if (!player.IsDead && !player.IsFalling && _targetExists)
                    player.FallThrough(_leave, (GetTree().CurrentScene as Room)?.EntryPosition ?? player.GlobalPosition);
            }
            else
            {
                _inside.RemoveAt(i);
                FallEffects.DropEnemy(this, body, EnemyFallDuration);
            }
        }
        if (_inside.Count == 0) SetPhysicsProcess(false);
    }

    private bool Leave()
    {
        return _sceneManager.GoToScene(TargetScene, TargetSpawn, _grantInvincibility, "chute");
    }

    // Appelé écran noir, juste avant le chargement : la nouvelle salle (Brann) lira cette valeur.
    private void GrantArrivalInvincibility() => _state.PendingArrivalInvincibility = ArrivalInvincibility;
}
