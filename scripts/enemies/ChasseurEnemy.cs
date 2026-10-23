using Godot;

/// <summary>
/// Ennemi « Chasseur » : erre lentement, annonce puis charge en ligne droite
/// quand le joueur est proche, s'étourdit s'il se cogne à un mur.
/// </summary>
public partial class ChasseurEnemy : CharacterBody2D
{
    private enum State { Errance, Annonce, Charge, Etourdi, Pause, Recul }

    [ExportGroup("Errance")]
    [Export] public float WanderSpeed { get; set; } = 25f;
    [Export] public float MinWanderTime { get; set; } = 1.0f;
    [Export] public float MaxWanderTime { get; set; } = 2.5f;

    [ExportGroup("Chasse")]
    [Export] public float DetectionRadius { get; set; } = 96f;
    [Export] public float WindupDuration { get; set; } = 0.4f;
    [Export] public float WindupShake { get; set; } = 1.5f;
    [Export] public float ChargeSpeed { get; set; } = 150f;
    [Export] public float ChargeMaxDuration { get; set; } = 1.2f;
    [Export] public float StunDuration { get; set; } = 1.0f;
    [Export] public float PauseDuration { get; set; } = 0.4f;
    [Export] public float Cooldown { get; set; } = 1.0f;

    [ExportGroup("Recul")]
    [Export] public float KnockbackSpeed { get; set; } = 160f;
    [Export] public float KnockbackDuration { get; set; } = 0.15f;

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName[] MoveAnims = { "move_down", "move_up", "move_left", "move_right" };
    private static readonly StringName[] ChargeAnims = { "charge_down", "charge_up", "charge_left", "charge_right" };
    private static readonly StringName StunnedLeft = "stunned_left";
    private static readonly StringName StunnedRight = "stunned_right";
    private static readonly Vector2[] Dirs = { Vector2.Down, Vector2.Up, Vector2.Left, Vector2.Right };

    private readonly RandomNumberGenerator _rng = new();
    private State _state = State.Errance;
    private int _facing; // index dans Dirs
    private Vector2 _wanderDir;
    private float _timer;
    private float _cooldownTimer;
    private Vector2 _knockbackVelocity;

    private AnimatedSprite2D _sprite;
    private HurtBox _hurtBox;
    private Node2D _player;
    private Health _health;
    private bool _dead;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _hurtBox.Hit += OnHit;
        _health = GetNode<Health>("Health");
        _health.Died += OnDied;

        _rng.Randomize();
        PickWanderDirection();
    }

    public override void _ExitTree()
    {
        if (_hurtBox != null) _hurtBox.Hit -= OnHit;
        if (_health != null) _health.Died -= OnDied;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_dead) return;
        float dt = (float)delta;
        if (_cooldownTimer > 0f) _cooldownTimer -= dt;

        switch (_state)
        {
            case State.Errance: UpdateWander(dt); break;
            case State.Annonce: UpdateWindup(dt); break;
            case State.Charge: UpdateCharge(dt); break;
            case State.Etourdi: UpdateTimed(dt, State.Errance, 0f); break;
            case State.Pause: UpdateTimed(dt, State.Errance, 0f); break;
            case State.Recul: UpdateKnockback(dt); break;
        }
    }

    private void UpdateWander(float dt)
    {
        _timer -= dt;
        if (_timer <= 0f) PickWanderDirection();

        Velocity = _wanderDir * WanderSpeed;
        MoveAndSlide();

        if (_cooldownTimer <= 0f && PlayerInRange())
            StartWindup();
    }

    private void UpdateWindup(float dt)
    {
        _timer -= dt;
        // Petit tremblement du sprite pour télégraphier la charge.
        _sprite.Position = new Vector2(_rng.RandfRange(-WindupShake, WindupShake), 0f);
        if (_timer <= 0f) StartCharge();
    }

    private void UpdateCharge(float dt)
    {
        _timer -= dt;
        Velocity = Dirs[_facing] * ChargeSpeed;
        MoveAndSlide();

        if (HitSolidWall())
        {
            EnterState(State.Etourdi, StunDuration);
            return;
        }
        if (_timer <= 0f)
            EnterState(State.Pause, PauseDuration);
    }

    private void UpdateTimed(float dt, State next, float nextTime)
    {
        _timer -= dt;
        if (_timer <= 0f)
        {
            bool afterStun = _state == State.Etourdi;
            EnterState(next, nextTime);
            if (afterStun) _cooldownTimer = Cooldown;
            if (next == State.Errance) PickWanderDirection();
        }
    }

    private void UpdateKnockback(float dt)
    {
        _timer -= dt;
        Velocity = _knockbackVelocity;
        MoveAndSlide();
        if (_timer <= 0f)
        {
            EnterState(State.Errance, 0f);
            PickWanderDirection();
        }
    }

    private void StartWindup()
    {
        if (_player == null || !IsInstanceValid(_player)) return;
        _facing = CardinalToward(_player.GlobalPosition - GlobalPosition);
        EnterState(State.Annonce, WindupDuration);
    }

    private void StartCharge()
    {
        // Direction verrouillée au moment où la charge démarre : jamais corrigée ensuite.
        if (_player != null && IsInstanceValid(_player))
            _facing = CardinalToward(_player.GlobalPosition - GlobalPosition);
        EnterState(State.Charge, ChargeMaxDuration);
    }

    private void EnterState(State state, float duration)
    {
        _state = state;
        _timer = duration;
        _sprite.Position = Vector2.Zero;
        if (state == State.Pause) _cooldownTimer = Cooldown + duration;

        switch (state)
        {
            case State.Annonce: _sprite.Play(MoveAnims[_facing]); break;
            case State.Charge: _sprite.Play(ChargeAnims[_facing]); break;
            case State.Etourdi:
                _sprite.Play(_facing == 2 ? StunnedLeft : StunnedRight);
                Velocity = Vector2.Zero;
                break;
            case State.Pause:
            case State.Errance:
                _sprite.Play(MoveAnims[_facing]);
                break;
        }
    }

    // Le joueur est lui aussi un CharacterBody2D : le toucher n'étourdit pas.
    private bool HitSolidWall()
    {
        int count = GetSlideCollisionCount();
        for (int i = 0; i < count; i++)
        {
            if (GetSlideCollision(i).GetCollider() is not CharacterBody2D)
                return true;
        }
        return false;
    }

    private bool PlayerInRange()
    {
        if (_player == null || !IsInstanceValid(_player))
        {
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Node2D;
            if (_player == null) return false;
        }
        return GlobalPosition.DistanceSquaredTo(_player.GlobalPosition) <= DetectionRadius * DetectionRadius;
    }

    private static int CardinalToward(Vector2 v)
    {
        if (Mathf.Abs(v.X) > Mathf.Abs(v.Y)) return v.X < 0f ? 2 : 3;
        return v.Y < 0f ? 1 : 0;
    }

    private void PickWanderDirection()
    {
        _timer = _rng.RandfRange(MinWanderTime, MaxWanderTime);
        _wanderDir = Vector2.Right.Rotated(_rng.RandfRange(0f, Mathf.Tau));
        _facing = CardinalToward(_wanderDir);
        _sprite.Play(MoveAnims[_facing]);
    }

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_dead) return;
        // Interrompt la charge / l'annonce ; l'étourdissement est aussi remplacé par le recul.
        _knockbackVelocity = (GlobalPosition - fromPosition).Normalized() * KnockbackSpeed;
        _cooldownTimer = Cooldown;
        EnterState(State.Recul, KnockbackDuration);
        _sprite.Play(MoveAnims[_facing]);
    }

    private void OnDied()
    {
        _dead = true;
        var poof = GD.Load<PackedScene>("res://scenes/enemies/death_effect.tscn").Instantiate<Node2D>();
        GetParent().AddChild(poof);
        poof.GlobalPosition = GlobalPosition;
        QueueFree();
    }
}
