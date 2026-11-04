using Godot;

/// <summary>
/// Bulle d'eau noire de la troisième manche de Corvan-Morvath. Hors de la lumière de la lanterne de Brann elle est presque invisible,
/// intouchable et elle tourne autour du boss ; dans le cercle de la lanterne elle apparaît, se fige et un coup (épée ou flèche) la crève.
/// Si Brann n'a pas la lanterne (ne devrait pas arriver), elle reste visible et figée pour ne jamais bloquer le combat.
/// Même principe que l'<see cref="OmbreNoyeeEnemy"/>, mais la salle est claire : la portée vient de la position de Brann, pas du halo.
/// Image facultative : art/bosses/corvan/bulle_eau_frames.tres (animations « flotte », « revelee » et « eclate ») ; à défaut, un disque dessiné par le code.
/// </summary>
public partial class BossBubble : Node2D
{
    /// <summary>La bulle vient d'être crevée.</summary>
    [Signal]
    public delegate void PoppedEventHandler();

    [Export] public string FramesPath { get; set; } = "res://art/bosses/corvan/bulle_eau_frames.tres";
    /// <summary>Opacité hors de la lumière.</summary>
    [Export(PropertyHint.Range, "0,1,0.01")] public float HiddenAlpha { get; set; } = 0.07f;
    [Export] public float FadeSpeed { get; set; } = 6f;

    /// <summary>Centre de l'orbite (monde) : réglé par le boss, qui ne bouge pas pendant la manche.</summary>
    public Vector2 OrbitCenter { get; set; }
    public float OrbitRadius { get; set; } = 70f;
    public float OrbitSpeed { get; set; } = 0.9f;
    public float Phase { get; set; }

    public bool IsRevealed => _revealed;
    public bool IsPopped => _dead;

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName AnimIdle = "flotte";
    private static readonly StringName AnimPop = "eclate";
    private static readonly StringName AnimRevealed = "revelee";

    private AnimatedSprite2D _sprite;
    private Health _health;
    private HurtBox _hurtBox;
    private GameState _state;
    private Player _player;
    private bool _revealed;
    private bool _hasFrames;
    private bool _dead;
    private float _alpha;
    private float _angle;
    private float _time;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _health = GetNode<Health>("Health");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _state = GetNode<GameState>("/root/GameState");
        _health.Died += OnDied;
        if (ResourceLoader.Exists(FramesPath))
        {
            var frames = GD.Load<SpriteFrames>(FramesPath);
            if (frames != null)
            {
                _sprite.SpriteFrames = frames;
                _hasFrames = true;
                _sprite.Play(AnimIdle);
            }
        }
        _sprite.Visible = _hasFrames;
        _angle = Phase;
        _alpha = HiddenAlpha;
        _hurtBox.Invincible = true;
        Place();
    }

    public override void _ExitTree()
    {
        if (_health != null) _health.Died -= OnDied;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_dead) return;
        float dt = (float)delta;
        _time += dt;
        if (_player == null || !IsInstanceValid(_player))
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Player;

        bool covered = IsCovered();
        if (covered != _revealed)
        {
            _revealed = covered;
            _hurtBox.Invincible = !covered;
            if (_hasFrames) _sprite.Play(covered ? AnimRevealed : AnimIdle);
        }
        _alpha = Mathf.MoveToward(_alpha, covered ? 1f : HiddenAlpha, FadeSpeed * dt);
        Modulate = new Color(1f, 1f, 1f, _alpha);
        if (!covered) _angle += OrbitSpeed * dt;
        Place();
        if (!_hasFrames) QueueRedraw();
    }

    // Dans le cercle de la lanterne (centre décalé devant Brann, rayon × 0,9 comme LanternLight.LanternCovers) ; sans lanterne : toujours.
    private bool IsCovered()
    {
        if (!_state.HasItem(LanternRules.ItemId)) return true;
        if (_player == null || _player.IsDead) return false;
        var center = _player.GlobalPosition + new Vector2(0f, 6f) + _player.FacingDirection * LanternRules.LightOffset;
        return LanternRules.IsNear(center.X, center.Y, GlobalPosition.X, GlobalPosition.Y, LanternRules.LightRadius * 0.9f);
    }

    private void Place()
    {
        float r = OrbitRadius + 8f * Mathf.Sin(_time * 1.7f + Phase);
        GlobalPosition = OrbitCenter + new Vector2(Mathf.Cos(_angle) * r, Mathf.Sin(_angle) * r * 0.6f);
    }

    private void OnDied()
    {
        _dead = true;
        _hurtBox.SetDeferred(Area2D.PropertyName.Monitorable, false);
        EmitSignal(SignalName.Popped);
        AudioManager.PlayAt(Sfx.Glou, GlobalPosition);
        if (_hasFrames && _sprite.SpriteFrames.HasAnimation(AnimPop))
        {
            Modulate = Colors.White;
            _sprite.Play(AnimPop);
            _sprite.AnimationFinished += QueueFree;
            return;
        }
        var tween = CreateTween();
        tween.TweenProperty(this, "scale", new Vector2(1.6f, 1.6f), 0.15f);
        tween.Parallel().TweenProperty(this, "modulate:a", 0f, 0.15f);
        tween.TweenCallback(Callable.From(QueueFree));
    }

    // Disque de remplacement tant que le graphiste n'a pas livré l'image.
    public override void _Draw()
    {
        if (_hasFrames) return;
        DrawCircle(Vector2.Zero, 11f, new Color(0.05f, 0.1f, 0.28f, 0.9f));
        DrawArc(Vector2.Zero, 11f, 0f, Mathf.Tau, 24, new Color(0.35f, 0.65f, 0.95f), 1.5f);
        DrawCircle(new Vector2(-3.5f, -4f), 2.5f, new Color(0.8f, 0.95f, 1f, 0.9f));
    }
}
