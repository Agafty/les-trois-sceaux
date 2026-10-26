using System.Collections.Generic;
using Godot;

/// <summary>
/// Zone « parle / achète » : une Area2D à poser en enfant d'un PNJ ou d'un article. Quand Brann est dedans, qu'il regarde vers le
/// propriétaire de la zone (le nœud parent) et appuie sur « interact », le signal <see cref="Interacted"/> est émis.
/// Plusieurs zones proches : seule la plus proche de Brann répond. Rien ne se passe si le jeu est en pause, en transition ou si Brann
/// est occupé (attaque, touché, mort).
/// Principe Godot : « appeler vers le bas, signaler vers le haut » — la zone ne connaît pas son propriétaire, elle émet un signal.
/// </summary>
public partial class InteractionZone : Area2D
{
    /// <summary>Brann a appuyé sur « interact » face à l'objet.</summary>
    [Signal]
    public delegate void InteractedEventHandler(Player player);

    /// <summary>Brann doit regarder vers l'objet (1 = exactement, 0 = n'importe quel côté). 0,5 = à 60° près.</summary>
    [Export(PropertyHint.Range, "0,1,0.05")] public float MinFacingDot { get; set; } = 0.5f;

    /// <summary>Faux : la zone est désactivée (objet déjà vendu...).</summary>
    public bool Enabled { get; set; } = true;

    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName PlayerGroup = "player";
    private static readonly List<InteractionZone> Candidates = new();

    private Player _player;
    private Node2D _owner2D;
    private SceneManager _sceneManager;
    private ulong _blockedUntilMs;

    public override void _Ready()
    {
        SetPhysicsProcess(false); // activé seulement quand Brann est dans la zone
        _owner2D = GetParent() as Node2D;
        _sceneManager = GetNodeOrNull<SceneManager>("/root/SceneManager");
        BodyEntered += OnBodyEntered;
        BodyExited += OnBodyExited;
    }

    public override void _ExitTree()
    {
        Candidates.Remove(this);
        BodyEntered -= OnBodyEntered;
        BodyExited -= OnBodyExited;
    }

    /// <summary>Ignore « interact » pendant ce délai (évite de relancer la conversation avec la touche qui vient de la fermer).</summary>
    public void BlockFor(float seconds) => _blockedUntilMs = Time.GetTicksMsec() + (ulong)(seconds * 1000f);

    public override void _PhysicsProcess(double delta)
    {
        if (!Enabled || _player == null || !Input.IsActionJustPressed(ActionInteract)) return;
        TryInteract(_player);
    }

    /// <summary>Même contrôles que l'appui sur la touche ; public pour les tests. Renvoie vrai si le signal a été émis.</summary>
    public bool TryInteract(Player player)
    {
        if (!Enabled || !IsInstanceValid(player) || Time.GetTicksMsec() < _blockedUntilMs) return false;
        if (player.IsDead || !player.CanInteract) return false;
        if (GetTree().Paused || (_sceneManager != null && _sceneManager.IsTransitioning)) return false;
        if (!IsFacing(player)) return false;
        if (!IsClosest(player)) return false;
        EmitSignal(SignalName.Interacted, player);
        return true;
    }

    private bool IsFacing(Player player)
    {
        if (_owner2D == null || MinFacingDot <= 0f) return true;
        var toOwner = _owner2D.GlobalPosition - player.GlobalPosition;
        if (toOwner.LengthSquared() < 1f) return true;
        return player.FacingDirection.Dot(toOwner.Normalized()) >= MinFacingDot;
    }

    private bool IsClosest(Player player)
    {
        if (_owner2D == null) return true;
        float mine = _owner2D.GlobalPosition.DistanceSquaredTo(player.GlobalPosition);
        for (int i = 0; i < Candidates.Count; i++)
        {
            var other = Candidates[i];
            if (other == this || !other.Enabled || other._owner2D == null) continue;
            if (other._owner2D.GlobalPosition.DistanceSquaredTo(player.GlobalPosition) < mine) return false;
        }
        return true;
    }

    private void OnBodyEntered(Node2D body)
    {
        if (!body.IsInGroup(PlayerGroup) || body is not Player player) return;
        _player = player;
        if (!Candidates.Contains(this)) Candidates.Add(this);
        SetPhysicsProcess(true);
    }

    private void OnBodyExited(Node2D body)
    {
        if (body != _player) return;
        _player = null;
        Candidates.Remove(this);
        SetPhysicsProcess(false);
    }
}
