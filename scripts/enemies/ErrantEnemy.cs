using Godot;

public partial class ErrantEnemy : CharacterBody2D
{
    [Export]
    public float Speed { get; set; } = 30f;

    [Export]
    public float MinWanderTime { get; set; } = 1.0f;

    [Export]
    public float MaxWanderTime { get; set; } = 2.5f;

    private Vector2 _direction = Vector2.Zero;
    private float _wanderTimer;
    private readonly RandomNumberGenerator _rng = new();

    public override void _Ready()
    {
        _rng.Randomize();
        PickNewDirection();

        var health = GetNodeOrNull<Health>("Health");
        if (health != null)
            health.Died += OnDied;
    }

    public override void _PhysicsProcess(double delta)
    {
        _wanderTimer -= (float)delta;
        if (_wanderTimer <= 0f)
            PickNewDirection();

        Velocity = _direction * Speed;
        MoveAndSlide();
    }

    private void PickNewDirection()
    {
        _wanderTimer = _rng.RandfRange(MinWanderTime, MaxWanderTime);
        var angle = _rng.RandfRange(0f, Mathf.Tau);
        _direction = Vector2.Right.Rotated(angle);
    }

    private void OnDied()
    {
        var poof = GD.Load<PackedScene>("res://scenes/enemies/death_effect.tscn").Instantiate<Node2D>();
        GetParent().AddChild(poof);
        poof.GlobalPosition = GlobalPosition;
        QueueFree();
    }
}
