using Godot;

/// <summary>
/// Ombre noyée : ennemi « Spécial » du Sanctuaire Englouti. Dans une salle en pénombre elle est quasi invisible et rôde
/// vers Brann ; dès que le cercle de lumière de la lanterne la couvre (<see cref="LanternLight.LanternCovers"/>), elle
/// apparaît et se fige : on peut la frapper. Le halo de Brann et les torches ne la révèlent pas.
/// Dans une salle claire (ou sans lanterne portée) elle est visible et erre normalement : jamais obligatoire.
/// </summary>
public partial class OmbreNoyeeEnemy : CharacterBody2D
{
    [ExportGroup("Mouvement")]
    [Export] public float Speed { get; set; } = 36f;
    [Export] public float MinWanderTime { get; set; } = 1.0f;
    [Export] public float MaxWanderTime { get; set; } = 2.5f;
    /// <summary>Distance (px) en dessous de laquelle elle glisse vers Brann (salle sombre) au lieu d'errer.</summary>
    [Export] public float StalkRadius { get; set; } = 128f;

    [ExportGroup("Apparence")]
    /// <summary>Opacité cachée dans le noir (0 = invisible).</summary>
    [Export(PropertyHint.Range, "0,1,0.01")] public float HiddenAlpha { get; set; } = 0.06f;
    [Export] public float FadeSpeed { get; set; } = 6f;

    [ExportGroup("Recul")]
    [Export] public float KnockbackSpeed { get; set; } = 110f;
    [Export] public float KnockbackDuration { get; set; } = 0.12f;

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName FloatAnim = "float";
    private static readonly StringName RevealedAnim = "revealed";
    private static readonly NodePath LanternPath = "Lanterne";
    private static PackedScene _deathScene;

    private readonly RandomNumberGenerator _rng = new();
    private Vector2 _wanderDir;
    private Vector2 _knockback;
    private float _timer;
    private float _knockTimer;
    private float _alpha = 1f;
    private bool _dark;
    private bool _darkChecked;
    private bool _revealed;

    private AnimatedSprite2D _sprite;
    private HurtBox _hurtBox;
    private Health _health;
    private Player _player;
    private LanternLight _lantern;
    private bool _dead;

    /// <summary>Vrai quand la lanterne la couvre : visible et immobile.</summary>
    public bool IsRevealed => _revealed;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _hurtBox.Hit += OnHit;
        _health = GetNode<Health>("Health");
        _health.Died += OnDied;
        _rng.Randomize();
        PickWanderDirection();
        _sprite.Play(FloatAnim);
        // Pas de clignotement à l'apparition : la Room a déjà lu « obscurite » avant d'ajouter l'ennemi (sinon IsDarkRoom est faux
        // ici, et le premier pas de physique corrige).
        _dark = Room.IsDarkRoom(this);
        _alpha = _dark ? HiddenAlpha : 1f;
        _sprite.SelfModulate = new Color(1f, 1f, 1f, _alpha);
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
        // La Room lit « obscurite » dans son _Ready (où cet ennemi est créé) : on interroge au premier pas de physique.
        if (!_darkChecked)
        {
            _dark = Room.IsDarkRoom(this);
            _darkChecked = true;
        }

        bool hasPlayer = TryGetPlayer();
        if (_dark && hasPlayer && (_lantern == null || !IsInstanceValid(_lantern)))
            _lantern = _player.GetNodeOrNull<LanternLight>(LanternPath);
        bool lit = _dark && _lantern != null && _lantern.LanternCovers(GlobalPosition);
        SetRevealed(lit);

        float targetAlpha = !_dark || lit ? 1f : HiddenAlpha;
        _alpha = Mathf.MoveToward(_alpha, targetAlpha, FadeSpeed * dt);
        _sprite.SelfModulate = new Color(1f, 1f, 1f, _alpha);

        if (_knockTimer > 0f)
        {
            _knockTimer -= dt;
            Velocity = _knockback;
            MoveAndSlide();
            return;
        }
        if (lit) return; // figée par la lumière

        _timer -= dt;
        Vector2 dir = _wanderDir;
        if (_dark && hasPlayer)
        {
            var toPlayer = _player.GlobalPosition - GlobalPosition;
            if (toPlayer.LengthSquared() <= StalkRadius * StalkRadius) dir = toPlayer.Normalized();
        }
        if (_timer <= 0f || (GetSlideCollisionCount() > 0 && dir == _wanderDir)) PickWanderDirection();
        Velocity = dir * Speed;
        MoveAndSlide();
    }

    private void SetRevealed(bool revealed)
    {
        if (revealed == _revealed) return;
        _revealed = revealed;
        _sprite.Play(revealed ? RevealedAnim : FloatAnim);
    }

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_dead) return;
        _knockback = (GlobalPosition - fromPosition).Normalized() * KnockbackSpeed;
        _knockTimer = KnockbackDuration;
    }

    private bool TryGetPlayer()
    {
        if (_player == null || !IsInstanceValid(_player))
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Player;
        return _player != null && !_player.IsDead;
    }

    private void PickWanderDirection()
    {
        _timer = _rng.RandfRange(MinWanderTime, MaxWanderTime);
        _wanderDir = Vector2.Right.Rotated(_rng.RandfRange(0f, Mathf.Tau));
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
