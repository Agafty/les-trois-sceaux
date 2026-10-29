using Godot;

/// <summary>
/// Chauve-souris des mines : ennemi « Chasseur » volant. Elle flotte au hasard, puis fonce sur Brann en zigzag
/// (trajectoire sinusoïdale, difficile à toucher), et s'éloigne un instant après avoir mordu.
/// Elle vole : groupe « vol » (la Room ne lui met pas la couche ravin et ne la fait pas tomber dans les trous),
/// et elle n'a aucune couche de collision (Brann passe dessous) ; elle ne se heurte qu'aux murs (masque 1).
/// </summary>
public partial class BatEnemy : CharacterBody2D
{
    private enum State { Errance, Chasse, Retrait, Recul }

    [ExportGroup("Errance")]
    [Export] public float WanderSpeed { get; set; } = 35f;
    [Export] public float MinWanderTime { get; set; } = 0.6f;
    [Export] public float MaxWanderTime { get; set; } = 1.4f;

    [ExportGroup("Chasse")]
    [Export] public float DetectionRadius { get; set; } = 120f;
    [Export] public float ChaseSpeed { get; set; } = 75f;
    /// <summary>Amplitude (px/s) du balancement latéral du zigzag.</summary>
    [Export] public float ZigzagAmplitude { get; set; } = 70f;
    /// <summary>Fréquence (rad/s) du zigzag.</summary>
    [Export] public float ZigzagFrequency { get; set; } = 6f;
    [Export] public float RetreatDuration { get; set; } = 0.8f;
    [Export] public float RetreatSpeed { get; set; } = 80f;

    [ExportGroup("Recul")]
    [Export] public float KnockbackSpeed { get; set; } = 140f;
    [Export] public float KnockbackDuration { get; set; } = 0.12f;

    private static PackedScene _deathScene;
    private static readonly StringName PlayerGroup = "player";

    private readonly RandomNumberGenerator _rng = new();
    private State _state = State.Errance;
    private Vector2 _dir;
    private Vector2 _knockback;
    private float _timer;
    private float _phase;

    private HurtBox _hurtBox;
    private HitBox _hitBox;
    private Health _health;
    private Node2D _player;
    private bool _dead;

    public override void _Ready()
    {
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _hurtBox.Hit += OnHit;
        _hitBox = GetNode<HitBox>("HitBox");
        _hitBox.HitLanded += OnBit;
        _health = GetNode<Health>("Health");
        _health.Died += OnDied;

        _rng.Randomize();
        _phase = _rng.RandfRange(0f, Mathf.Tau);
        PickWanderDirection();
    }

    public override void _ExitTree()
    {
        if (_hurtBox != null) _hurtBox.Hit -= OnHit;
        if (_hitBox != null) _hitBox.HitLanded -= OnBit;
        if (_health != null) _health.Died -= OnDied;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_dead) return;
        float dt = (float)delta;
        _timer -= dt;
        _phase += ZigzagFrequency * dt;

        switch (_state)
        {
            case State.Errance:
                if (_timer <= 0f) PickWanderDirection();
                // Léger flottement même au repos : le vol n'est jamais rectiligne.
                Velocity = _dir * WanderSpeed + _dir.Orthogonal() * (Mathf.Sin(_phase) * WanderSpeed * 0.5f);
                if (PlayerInRange()) _state = State.Chasse;
                break;

            case State.Chasse:
                if (!TryGetPlayer(out var target) || GlobalPosition.DistanceSquaredTo(target.GlobalPosition) > DetectionRadius * DetectionRadius * 2.25f)
                {
                    _state = State.Errance;
                    PickWanderDirection();
                    return;
                }
                var toPlayer = (target.GlobalPosition - GlobalPosition).Normalized();
                Velocity = toPlayer * ChaseSpeed + toPlayer.Orthogonal() * (Mathf.Sin(_phase) * ZigzagAmplitude);
                break;

            case State.Retrait:
                Velocity = _dir * RetreatSpeed + _dir.Orthogonal() * (Mathf.Sin(_phase) * ZigzagAmplitude * 0.5f);
                if (_timer <= 0f) _state = State.Errance;
                break;

            case State.Recul:
                Velocity = _knockback;
                if (_timer <= 0f) _state = State.Chasse;
                break;
        }

        MoveAndSlide();
        // Seuls les murs la font rebondir : Brann et les autres corps (CharacterBody2D) sont ignorés.
        int count = GetSlideCollisionCount();
        for (int i = 0; i < count; i++)
        {
            var hit = GetSlideCollision(i);
            if (hit.GetCollider() is CharacterBody2D) continue;
            OnWallHit(hit.GetNormal());
            break;
        }
    }

    // Seuls les murs sont solides pour elle : on rebondit, et on inverse le zigzag pour ne pas rester collée.
    private void OnWallHit(Vector2 normal)
    {
        _dir = _dir.Bounce(normal).Normalized();
        _phase += Mathf.Pi;
        if (_state == State.Errance) _timer = _rng.RandfRange(MinWanderTime, MaxWanderTime);
    }

    private void PickWanderDirection()
    {
        _timer = _rng.RandfRange(MinWanderTime, MaxWanderTime);
        _dir = Vector2.Right.Rotated(_rng.RandfRange(0f, Mathf.Tau));
    }

    private bool TryGetPlayer(out Node2D player)
    {
        if (_player == null || !IsInstanceValid(_player))
        {
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Node2D;
            if (_player is PhysicsBody2D body) AddCollisionExceptionWith(body); // elle vole au-dessus de Brann : pas de poussée mutuelle
        }
        player = _player;
        return player != null && player is not Player { IsDead: true };
    }

    private bool PlayerInRange()
    {
        return TryGetPlayer(out var p)
            && GlobalPosition.DistanceSquaredTo(p.GlobalPosition) <= DetectionRadius * DetectionRadius;
    }

    // Elle vient de mordre Brann : elle s'écarte quelques instants avant de revenir.
    private void OnBit()
    {
        if (_dead) return;
        _dir = TryGetPlayer(out var p) ? (GlobalPosition - p.GlobalPosition).Normalized() : Vector2.Up;
        _state = State.Retrait;
        _timer = RetreatDuration;
    }

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_dead) return;
        _knockback = (GlobalPosition - fromPosition).Normalized() * KnockbackSpeed;
        _state = State.Recul;
        _timer = KnockbackDuration;
    }

    private void OnDied()
    {
        _dead = true;
        var poof = (_deathScene ??= GD.Load<PackedScene>("res://scenes/enemies/death_effect.tscn")).Instantiate<Node2D>();
        GetParent().AddChild(poof);
        poof.GlobalPosition = GlobalPosition;
        QueueFree();
    }
}
