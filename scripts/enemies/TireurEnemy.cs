using Godot;

/// <summary>
/// Ennemi « Tireur » immobile (ex. Lutin des branches) : caché et invulnérable,
/// il apparaît quand le joueur approche, lance un projectile visé, reste exposé
/// un moment (fenêtre pour le frapper), puis se recache.
/// </summary>
public partial class TireurEnemy : CharacterBody2D
{
    private enum State { Cache, Apparition, Tir, Expose }

    [ExportGroup("Détection")]
    [Export] public float DetectionRadius { get; set; } = 160f;

    [ExportGroup("Cycle")]
    [Export] public float PeekDuration { get; set; } = 0.5f;
    [Export] public float ThrowDuration { get; set; } = 0.34f;
    [Export] public float ThrowReleaseTime { get; set; } = 0.17f;
    [Export] public float ExposedDuration { get; set; } = 1.0f;
    [Export] public float Cooldown { get; set; } = 1.5f;

    [ExportGroup("Projectile")]
    [Export] public PackedScene ProjectileScene { get; set; }
    [Export] public Vector2 ProjectileOffset { get; set; } = new Vector2(0f, 6f);

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName AnimHidden = "hidden";
    private static readonly StringName AnimPeek = "peek";
    private static readonly StringName AnimThrow = "throw";

    private State _state = State.Cache;
    private float _timer;
    private float _cooldownTimer;
    private bool _fired;
    private bool _dead;

    private AnimatedSprite2D _sprite;
    private HurtBox _hurtBox;
    private Health _health;
    private Node2D _player;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _health = GetNode<Health>("Health");
        _health.Died += OnDied;
        EnterState(State.Cache, 0f);
    }

    public override void _ExitTree()
    {
        if (_health != null) _health.Died -= OnDied;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_dead) return;
        float dt = (float)delta;
        if (_cooldownTimer > 0f) _cooldownTimer -= dt;

        switch (_state)
        {
            case State.Cache:
                if (_cooldownTimer <= 0f && PlayerInRange()) EnterState(State.Apparition, PeekDuration);
                break;
            case State.Apparition:
                _timer -= dt;
                if (_timer <= 0f) EnterState(State.Tir, ThrowDuration);
                break;
            case State.Tir:
                _timer -= dt;
                if (!_fired && _timer <= ThrowDuration - ThrowReleaseTime) Fire();
                if (_timer <= 0f) EnterState(State.Expose, ExposedDuration);
                break;
            case State.Expose:
                _timer -= dt;
                if (_timer <= 0f)
                {
                    _cooldownTimer = Cooldown;
                    EnterState(State.Cache, 0f);
                }
                break;
        }
    }

    private void EnterState(State state, float duration)
    {
        _state = state;
        _timer = duration;

        bool vulnerable = state != State.Cache;
        _hurtBox.Invincible = !vulnerable;
        // Caché : la HurtBox n'est plus détectable, l'épée ne la "touche" donc pas
        // (pas de hit-stop ni de tremblement dans le vide). Différé : on est peut-être
        // dans un callback de physique.
        _hurtBox.SetDeferred(Area2D.PropertyName.Monitorable, vulnerable);

        switch (state)
        {
            case State.Cache: _sprite.Play(AnimHidden); break;
            case State.Apparition:
            case State.Expose: _sprite.Play(AnimPeek); break;
            case State.Tir:
                _fired = false;
                _sprite.Play(AnimThrow);
                break;
        }
    }

    private void Fire()
    {
        _fired = true;
        if (ProjectileScene == null || !HasPlayer()) return;

        Vector2 origin = GlobalPosition + ProjectileOffset;
        Vector2 dir = _player.GlobalPosition - origin;

        var projectile = ProjectileScene.Instantiate<Projectile>();
        projectile.Launch(dir);
        // Ajouté au parent : il ne suit pas le lutin et survit à sa mort.
        GetParent().AddChild(projectile);
        projectile.GlobalPosition = origin;
    }

    private bool HasPlayer()
    {
        if (_player == null || !IsInstanceValid(_player))
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Node2D;
        return _player != null;
    }

    private bool PlayerInRange()
    {
        if (!HasPlayer()) return false;
        return GlobalPosition.DistanceSquaredTo(_player.GlobalPosition) <= DetectionRadius * DetectionRadius;
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
