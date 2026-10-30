using Godot;

public partial class HitBox : Area2D
{
    [Export]
    public Team Team { get; set; } = Team.Joueur;

    [Export]
    public int Damage { get; set; } = 1;

    [Export]
    public float HitStopDuration { get; set; } = 0.05f;

    [Export]
    public float CameraShakeStrength { get; set; } = 3f;

    [Export]
    public float CameraShakeDuration { get; set; } = 0.15f;

    /// <summary>Émis après qu'une HurtBox ennemie a été touchée (même si elle était invincible).</summary>
    [Signal]
    public delegate void HitLandedEventHandler();

    /// <summary>Vrai : après le premier coup infligé, cette HitBox ignore toute autre HurtBox (flèche).</summary>
    [Export]
    public bool SingleHit { get; set; }

    /// <summary>Vrai pour l'épée : cette HitBox prévient aussi les zones <see cref="IMeleeTarget"/> (interrupteur à l'épée...) qu'elle chevauche.</summary>
    [Export]
    public bool Melee { get; set; }

    private bool _hasHit;
    private Node2D _attacker; // corps qui porte cette HitBox (Brann pour l'épée) ; nul pour une flèche ou une bombe
    private static bool _hitStopActive;

    public override void _Ready()
    {
        AreaEntered += OnAreaEntered;
        for (Node n = GetParent(); n != null; n = n.GetParent())
        {
            if (n is CharacterBody2D body) { _attacker = body; break; }
        }
    }

    private void OnAreaEntered(Area2D area)
    {
        if (Melee && area is IMeleeTarget meleeTarget)
        {
            meleeTarget.OnMeleeHit(GlobalPosition);
            return;
        }
        if (area is not HurtBox hurtBox) return;
        if (hurtBox.Team == Team) return;
        if (SingleHit && _hasHit) return;
        _hasHit = true;

        hurtBox.ReceiveHitFrom(Damage, GlobalPosition, _attacker != null && IsInstanceValid(_attacker) ? _attacker.GlobalPosition : GlobalPosition);
        TriggerHitStop();
        ShakeCamera();
        EmitSignal(SignalName.HitLanded);
    }

    private void TriggerHitStop()
    {
        if (_hitStopActive) return;
        _hitStopActive = true;

        Engine.TimeScale = 0.05f;
        GetTree().CreateTimer(HitStopDuration, processAlways: true, processInPhysics: false, ignoreTimeScale: true).Timeout += () =>
        {
            Engine.TimeScale = 1f;
            _hitStopActive = false;
        };
    }

    private void ShakeCamera()
    {
        if (CameraShakeStrength <= 0f) return;
        if (GetViewport().GetCamera2D() is CameraShake shake)
            shake.Shake(CameraShakeStrength, CameraShakeDuration);
    }
}
