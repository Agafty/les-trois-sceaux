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

    private static bool _hitStopActive;

    public override void _Ready()
    {
        AreaEntered += OnAreaEntered;
    }

    private void OnAreaEntered(Area2D area)
    {
        if (area is not HurtBox hurtBox) return;
        if (hurtBox.Team == Team) return;

        hurtBox.ReceiveHit(Damage, GlobalPosition);
        TriggerHitStop();
        ShakeCamera();
    }

    private void TriggerHitStop()
    {
        if (_hitStopActive) return;
        _hitStopActive = true;

        Engine.TimeScale = 0.05f;
        GetTree().CreateTimer(HitStopDuration, ignoreTimeScale: true).Timeout += () =>
        {
            Engine.TimeScale = 1f;
            _hitStopActive = false;
        };
    }

    private void ShakeCamera()
    {
        if (GetViewport().GetCamera2D() is CameraShake shake)
            shake.Shake(CameraShakeStrength, CameraShakeDuration);
    }
}
