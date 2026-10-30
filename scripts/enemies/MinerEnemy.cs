using Godot;

/// <summary>
/// Mineur maudit : ennemi « Spécial ». Son bouclier de pierre bloque l'épée et les flèches venues de face
/// (<see cref="HurtBox.BlockFilter"/> : signal Blocked, retour bleu et son, aucun dégât) ; de côté ou de dos il est vulnérable.
/// Il se tourne vers Brann avec un temps de réaction, ce qui permet de le contourner.
/// Une explosion de bombe à portée (<see cref="IBombDestructible"/>) le fait tomber : étourdi sans bouclier, vulnérable
/// <see cref="StunDuration"/> secondes, puis il se relève. Le souffle lui-même ne le blesse pas (courte immunité).
/// </summary>
public partial class MinerEnemy : CharacterBody2D, IBombDestructible
{
    private enum State { Errance, Poursuite, Recul, Etourdi }

    [ExportGroup("Mouvement")]
    [Export] public float WanderSpeed { get; set; } = 22f;
    [Export] public float ChaseSpeed { get; set; } = 32f;
    [Export] public float DetectionRadius { get; set; } = 110f;
    [Export] public float MinWanderTime { get; set; } = 1.0f;
    [Export] public float MaxWanderTime { get; set; } = 2.5f;
    /// <summary>Délai (s) entre deux changements de direction du bouclier quand il suit Brann.</summary>
    [Export] public float TurnDelay { get; set; } = 0.6f;

    [ExportGroup("Bouclier")]
    /// <summary>Cosinus minimal entre le regard et la direction du coup pour qu'il soit bloqué (0.5 = 60° de chaque côté).</summary>
    [Export(PropertyHint.Range, "-1,1,0.05")] public float BlockCosine { get; set; } = 0.5f;

    [ExportGroup("Chute")]
    [Export] public float StunDuration { get; set; } = 4f;
    /// <summary>Après l'explosion, durée (s) pendant laquelle le souffle de la bombe ne le blesse pas.</summary>
    [Export] public float BlastGrace { get; set; } = 0.3f;
    [Export] public float BlastKnockback { get; set; } = 120f;

    [ExportGroup("Recul")]
    [Export] public float KnockbackSpeed { get; set; } = 110f;
    [Export] public float KnockbackDuration { get; set; } = 0.12f;

    private static readonly NodePath ModulateProp = "modulate";
    private static PackedScene _deathScene;
    private Tween _flashTween;
    private static readonly StringName PlayerGroup = "player";
    private static readonly Vector2[] Dirs = { Vector2.Down, Vector2.Up, Vector2.Left, Vector2.Right };
    // [bouclier ? 0 : 1][direction] ; ordre des directions = Dirs.
    private static readonly StringName[][] Walk =
    {
        new StringName[] { "walk_down", "walk_up", "walk_left", "walk_right" },
        new StringName[] { "walk_down_noshield", "walk_up_noshield", "walk_left_noshield", "walk_right_noshield" },
    };
    private static readonly StringName[][] Idle =
    {
        new StringName[] { "idle_down", "idle_up", "idle_left", "idle_right" },
        new StringName[] { "idle_down_noshield", "idle_up_noshield", "idle_left_noshield", "idle_right_noshield" },
    };

    private readonly RandomNumberGenerator _rng = new();
    private State _state = State.Errance;
    private int _facing; // index dans Dirs
    private Vector2 _wanderDir;
    private Vector2 _knockback;
    private float _timer;
    private float _turnTimer;
    private float _graceTimer;

    private AnimatedSprite2D _sprite;
    private HurtBox _hurtBox;
    private HitBox _hitBox;
    private Health _health;
    private Node2D _player;
    private bool _dead;

    /// <summary>Vrai tant que le mineur est à terre (vulnérable de partout).</summary>
    public bool IsStunned => _state == State.Etourdi;

    public Vector2 BombHalfExtents => new(11f, 15f);

    public override void _EnterTree() => Bomb.Register(this);

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _hurtBox.BlockFilter = ShieldBlocks;
        _hurtBox.Blocked += OnBlocked;
        _hurtBox.Hit += OnHit;
        _hitBox = GetNode<HitBox>("HitBox");
        _health = GetNode<Health>("Health");
        _health.Died += OnDied;

        _rng.Randomize();
        PickWanderDirection();
        PlayAnim(true);
    }

    public override void _ExitTree()
    {
        Bomb.Unregister(this);
        if (_hurtBox != null)
        {
            _hurtBox.BlockFilter = null;
            _hurtBox.Blocked -= OnBlocked;
            _hurtBox.Hit -= OnHit;
        }
        if (_health != null) _health.Died -= OnDied;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_dead) return;
        float dt = (float)delta;
        if (_graceTimer > 0f) _graceTimer -= dt;
        _timer -= dt;

        switch (_state)
        {
            case State.Errance:
                if (_timer <= 0f) PickWanderDirection();
                Velocity = _wanderDir * WanderSpeed;
                MoveAndSlide();
                if (PlayerInRange()) EnterState(State.Poursuite, 0f);
                break;

            case State.Poursuite:
                UpdateChase(dt);
                break;

            case State.Recul:
                Velocity = _knockback;
                MoveAndSlide();
                if (_timer <= 0f) EnterState(State.Poursuite, 0f);
                break;

            case State.Etourdi:
                // Glisse un peu sous la poussée du souffle, puis reste à terre.
                _knockback = _knockback.MoveToward(Vector2.Zero, 400f * dt);
                Velocity = _knockback;
                MoveAndSlide();
                if (_timer <= 0f) GetUp();
                break;
        }
    }

    private void UpdateChase(float dt)
    {
        if (!TryGetPlayer(out var p) || GlobalPosition.DistanceSquaredTo(p.GlobalPosition) > DetectionRadius * DetectionRadius * 2.25f)
        {
            EnterState(State.Errance, 0f);
            return;
        }
        // Le bouclier suit Brann avec un temps de réaction : en le contournant vite, on le prend de côté.
        _turnTimer -= dt;
        if (_turnTimer <= 0f)
        {
            int wanted = CardinalToward(p.GlobalPosition - GlobalPosition);
            if (wanted != _facing)
            {
                _facing = wanted;
                PlayAnim(true);
            }
            _turnTimer = TurnDelay;
        }
        Velocity = (p.GlobalPosition - GlobalPosition).Normalized() * ChaseSpeed;
        MoveAndSlide();
    }

    // Filtre du HurtBox : vrai = coup bloqué. La position reçue est celle du corps attaquant (Brann), ou de la HitBox pour une flèche.
    private bool ShieldBlocks(Vector2 fromPosition)
    {
        if (_dead) return false;
        if (_graceTimer > 0f) return true; // souffle de la bombe : il tombe, mais n'est pas blessé
        if (_state == State.Etourdi) return false;
        var toAttacker = (fromPosition - _hurtBox.GlobalPosition).Normalized();
        return Dirs[_facing].Dot(toAttacker) >= BlockCosine;
    }

    private void OnBlocked(int damage, Vector2 fromPosition)
    {
        if (_graceTimer > 0f) return; // simple souffle : pas d'étincelle de bouclier
        // « Rien ne passe » : éclat bleu et bruit de choc, comme le boss Sylve.
        AudioManager.PlayAt(Sfx.FlecheImpact, fromPosition);
        _sprite.Modulate = new Color(0.3f, 0.6f, 3f);
        _flashTween?.Kill();
        _flashTween = CreateTween();
        _flashTween.TweenProperty(_sprite, ModulateProp, Colors.White, 0.25f);
    }

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_dead || _state == State.Etourdi) return; // à terre : il ne bouge pas sous les coups
        _knockback = (GlobalPosition - fromPosition).Normalized() * KnockbackSpeed;
        EnterState(State.Recul, KnockbackDuration);
    }

    /// <summary>Une bombe explose : s'il est à portée, le mineur tombe.</summary>
    public void OnBombExplosion(Vector2 center)
    {
        if (_dead) return;
        _graceTimer = BlastGrace;
        _knockback = (GlobalPosition - center).Normalized() * BlastKnockback;
        EnterState(State.Etourdi, StunDuration);
        AudioManager.PlayAt(Sfx.BossAssomme, GlobalPosition);
    }

    private void GetUp()
    {
        _sprite.RotationDegrees = 0f;
        _sprite.Position = Vector2.Zero;
        _hitBox.SetDeferred(Area2D.PropertyName.Monitoring, true);
        EnterState(State.Poursuite, 0f);
    }

    private void EnterState(State state, float duration)
    {
        // Le bouclier ne se retourne aussitôt qu'en reprenant la chasse depuis l'errance ou la chute, pas après un recul.
        if (state == State.Poursuite && (_state == State.Errance || _state == State.Etourdi)) _turnTimer = 0f;
        _state = state;
        _timer = duration;
        if (state == State.Etourdi)
        {
            // À terre : sans bouclier, couché sur le côté, et il ne mord plus.
            _sprite.RotationDegrees = _facing == 2 ? -90f : 90f;
            _sprite.Position = new Vector2(0f, 6f);
            _hitBox.SetDeferred(Area2D.PropertyName.Monitoring, false);
        }
        PlayAnim(state != State.Etourdi);
    }

    private void PlayAnim(bool shield)
    {
        int s = shield ? 0 : 1;
        _sprite.Play(_state == State.Etourdi ? Idle[s][_facing] : Walk[s][_facing]);
    }

    private bool TryGetPlayer(out Node2D player)
    {
        if (_player == null || !IsInstanceValid(_player))
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Node2D;
        player = _player;
        return player != null && player is not Player { IsDead: true };
    }

    private bool PlayerInRange()
    {
        return TryGetPlayer(out var p)
            && GlobalPosition.DistanceSquaredTo(p.GlobalPosition) <= DetectionRadius * DetectionRadius;
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
        PlayAnim(true);
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
