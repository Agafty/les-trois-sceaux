using Godot;

/// <summary>
/// Poule du village (classe Tiled « Poule », mini-jeu de Pip). Elle flâne autour de son point de départ ; Brann l'attrape en marchant
/// dessus ou d'un coup d'épée (sans lui faire de mal). Elle caquette puis disparaît, et son id est mémorisé dans GameState :
/// elle ne revient pas. Quand les cinq sont attrapées, le flag <see cref="ChickenRules.AllCaughtFlag"/> est posé (Pip donne alors son quart de cœur).
/// Sprite : art/characters/poule_frames.tres (animations idle_/walk_/peck_ down, up, left, right ; peck = elle picore à l'arrêt) ; sans ce fichier, une image
/// provisoire est dessinée par le code.
/// </summary>
public partial class Chicken : CharacterBody2D
{
    /// <summary>La poule vient d'être attrapée : id et nombre de poules attrapées (cette poule comprise).</summary>
    [Signal]
    public delegate void CaughtEventHandler(string chickenId, int total);

    /// <summary>Id unique, ex. « village_poule_01 ».</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Rayon (px) de l'errance autour du point de départ.</summary>
    [Export(PropertyHint.Range, "0,128,1")] public float WanderRadius { get; set; } = 48f;

    [Export(PropertyHint.Range, "5,80,1")] public float WanderSpeed { get; set; } = 26f;

    public bool IsCaught => _caught;

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName[] IdleAnims = { "idle_down", "idle_up", "idle_left", "idle_right" };
    private static readonly StringName[] WalkAnims = { "walk_down", "walk_up", "walk_left", "walk_right" };
    private static readonly StringName[] PeckAnims = { "peck_down", "peck_up", "peck_left", "peck_right" };
    private const string FramesPath = "res://art/characters/poule_frames.tres";
    private static ImageTexture _placeholder;

    private AnimatedSprite2D _sprite;
    private Sprite2D _placeholderSprite;
    private ChickenZone _zone;
    private GameState _state;
    private Vector2 _home;
    private Vector2 _target;
    private float _wanderTimer;
    private float _walkTime;
    private bool _walking;
    private bool _caught;
    private int _facing;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _placeholderSprite = GetNode<Sprite2D>("Placeholder");
        _zone = GetNode<ChickenZone>("ZoneCapture");
        _state = GetNode<GameState>("/root/GameState");
        _home = GlobalPosition;
        if (string.IsNullOrEmpty(Id))
            GD.PushWarning($"Poule sans Id ({GetPath()}) : elle ne sera pas mémorisée.");

        if (ResourceLoader.Exists(FramesPath))
        {
            _sprite.SpriteFrames = GD.Load<SpriteFrames>(FramesPath);
            _placeholderSprite.Visible = false;
            PlayAnim(IdleAnims);
        }
        else
        {
            _sprite.Visible = false;
            _placeholderSprite.Texture = PlaceholderTexture();
        }

        _zone.BodyEntered += OnBodyEntered;
        _zone.SwordHit += OnSwordHit;
        SetPhysicsProcess(WanderRadius > 0f);
        _wanderTimer = 0.5f + GD.Randf() * 2f;
    }

    public override void _ExitTree()
    {
        if (_zone == null) return;
        _zone.BodyEntered -= OnBodyEntered;
        _zone.SwordHit -= OnSwordHit;
    }

    // --- Capture ----------------------------------------------------------------------------------

    private void OnBodyEntered(Node2D body)
    {
        if (body.IsInGroup(PlayerGroup) && body is Player { IsDead: false })
            Catch();
    }

    private void OnSwordHit() => Catch();

    /// <summary>Attrape la poule (touchée par Brann ou son épée). Sans effet si elle l'est déjà.</summary>
    public void Catch()
    {
        if (_caught) return;
        _caught = true;
        SetPhysicsProcess(false);
        _zone.SetDeferred(Area2D.PropertyName.Monitoring, false);
        _zone.SetDeferred(Area2D.PropertyName.Monitorable, false);
        AudioManager.PlayAt(Sfx.Poule, GlobalPosition);

        _state.MarkCollected(Id);
        int total = _state.Chickens;
        if (ChickenRules.AllCaught(total))
            _state.MarkCollected(ChickenRules.AllCaughtFlag);
        EmitSignal(SignalName.Caught, Id, total);

        // Petit bond puis disparition en fondu.
        var tween = CreateTween();
        tween.SetParallel(true);
        tween.TweenProperty(this, "position:y", Position.Y - 14f, 0.3).SetEase(Tween.EaseType.Out);
        tween.TweenProperty(this, "modulate:a", 0f, 0.3);
        tween.SetParallel(false);
        tween.TweenCallback(Callable.From(QueueFree));
    }

    // --- Errance ----------------------------------------------------------------------------------

    public override void _PhysicsProcess(double delta)
    {
        float dt = (float)delta;
        if (_walking)
        {
            _walkTime += dt;
            var toTarget = _target - GlobalPosition;
            if (toTarget.LengthSquared() < 4f || _walkTime > 3f)
            {
                StopWalking();
                return;
            }
            Velocity = toTarget.Normalized() * WanderSpeed;
            MoveAndSlide();
            if (GetSlideCollisionCount() > 0) StopWalking();
            return;
        }

        _wanderTimer -= dt;
        if (_wanderTimer > 0f) return;
        float angle = GD.Randf() * Mathf.Tau;
        _target = _home + new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)) * (WanderRadius * GD.Randf());
        _walking = true;
        _walkTime = 0f;
        Face(_target - GlobalPosition);
        PlayAnim(WalkAnims);
    }

    private void StopWalking()
    {
        _walking = false;
        Velocity = Vector2.Zero;
        _wanderTimer = 1f + GD.Randf() * 2.5f;
        PlayAnim(GD.Randf() < 0.5f ? PeckAnims : IdleAnims); // une fois sur deux, elle picore pendant la pause
    }

    private void Face(Vector2 direction)
    {
        if (direction.LengthSquared() < 0.01f) return;
        _facing = Mathf.Abs(direction.X) > Mathf.Abs(direction.Y)
            ? (direction.X < 0f ? 2 : 3)
            : (direction.Y < 0f ? 1 : 0);
        if (direction.X != 0f) _placeholderSprite.FlipH = direction.X < 0f;
    }

    private void PlayAnim(StringName[] anims)
    {
        if (_sprite?.SpriteFrames != null && _sprite.SpriteFrames.HasAnimation(anims[_facing]))
            _sprite.Play(anims[_facing]);
    }

    // Poule provisoire 16x16 : corps blanc, crête rouge, bec jaune (regarde vers la droite).
    private static ImageTexture PlaceholderTexture()
    {
        if (_placeholder != null && IsInstanceValid(_placeholder)) return _placeholder;
        var image = Image.CreateEmpty(16, 16, false, Image.Format.Rgba8);
        var white = new Color(0.96f, 0.95f, 0.9f);
        var shade = new Color(0.78f, 0.76f, 0.72f);
        var red = new Color(0.82f, 0.18f, 0.2f);
        var yellow = new Color(0.95f, 0.75f, 0.2f);
        var dark = new Color(0.11f, 0.08f, 0.13f);
        image.FillRect(new Rect2I(3, 6, 9, 7), white);
        image.FillRect(new Rect2I(3, 11, 9, 2), shade);
        image.FillRect(new Rect2I(10, 3, 4, 5), white);
        image.FillRect(new Rect2I(11, 1, 2, 2), red);
        image.FillRect(new Rect2I(14, 5, 2, 2), yellow);
        image.FillRect(new Rect2I(12, 4, 1, 1), dark);
        image.FillRect(new Rect2I(5, 13, 1, 2), yellow);
        image.FillRect(new Rect2I(8, 13, 1, 2), yellow);
        image.FillRect(new Rect2I(1, 7, 2, 3), shade);
        _placeholder = ImageTexture.CreateFromImage(image);
        return _placeholder;
    }
}
