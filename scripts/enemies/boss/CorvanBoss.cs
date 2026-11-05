using System.Collections.Generic;
using Godot;

/// <summary>
/// Corvan puis Morvath : le boss final (arène du château, id « chateau_boss_corvan »). Machine à états en quatre temps,
/// composée des composants habituels (Health, HurtBox) ; règles pures dans <see cref="CorvanRules"/>.
/// <list type="number">
/// <item>Phase 1, le marteau (8 PV) : Corvan marche vers Brann, puis annonce un (deux à mi-vie) cercle d'ombre au sol, frappe, et reste
/// « marteau coincé » <see cref="StuckSeconds"/> secondes : seul moment où l'épée le blesse.</item>
/// <item>Transition : à 0 PV le code lance la cinématique « chateau_morvath_prend » ; le boss est inactif tant qu'elle joue, puis il est
/// agrandi, rempli à 9 PV et deux petits cœurs tombent.</item>
/// <item>Phase 2, trois manches de 3 PV, toujours dans le même ordre : ronces (3 bulbes à l'arc), pierre (2 bombes,
/// <see cref="IBombDestructible"/>), eau (3 bulles que la lanterne révèle, <see cref="BossBubble"/>). Tant que la couche est là, la
/// <c>HurtBox</c> « Couche » est invincible et émet <c>Blocked</c> ; une fois brisée, il est étourdi <see cref="StunSeconds"/> secondes
/// (vulnérable à l'épée) et deux petits cœurs tombent. Une icône de l'objet à utiliser flotte au-dessus de lui.</item>
/// <item>Finale : l'Œil de Morvath se détache, saute entre les Marqueurs « morvath_oeil_N », reste <see cref="EyeHoldSeconds"/> secondes
/// vulnérable et tire un orbe lent ; 2 PV. À sa mort : victoire (boss mémorisé, porte rouverte), puis la cinématique « chateau_corvan_vaincu » pose
/// « morvath_vaincu » et sauvegarde elle-même (la Room la relance si le jeu est quitté en cours de scène).</item>
/// </list>
/// Une seule attaque à la fois, toujours annoncée ; annonces, fenêtres de coup et écoute de l'Œil sont multipliées par l'option d'aide
/// (<c>GameState.PuzzleTimeMultiplier</c>, plafond x2, 0 = x2 comme Ondine). Aucun coup ne retire plus d'un cœur et demi.
/// Images : art/bosses/corvan/ (voir <see cref="CorvanBoss.ExpectedAnimations"/>) ; sans elles, des substituts sont dessinés.
/// </summary>
public partial class CorvanBoss : Boss, IBombDestructible
{
    private enum State
    {
        Dormant, Chase, Announce, Stuck, Transition,
        RoundIntro, RoundIdle, RoundWarn, RoundAttack, Stunned,
        Release, EyeMove, EyeHold, Victory,
    }

    [ExportGroup("Début du combat")]
    /// <summary>Distance (px) dont Brann doit s'éloigner de son point d'arrivée pour que le combat commence (la porte se referme).</summary>
    [Export(PropertyHint.Range, "32,300,8")] public float StartDistance { get; set; } = 96f;

    [ExportGroup("Phase 1 : le marteau")]
    [Export(PropertyHint.Range, "10,100,1")] public float ChaseSpeed { get; set; } = 40f;
    /// <summary>Durée maximale (s) de la marche avant l'annonce du coup.</summary>
    [Export(PropertyHint.Range, "0.5,6,0.1")] public float ChaseMaxSeconds { get; set; } = 2.5f;
    /// <summary>Distance (px) à laquelle Corvan annonce le coup.</summary>
    [Export(PropertyHint.Range, "24,160,2")] public float StrikeDistance { get; set; } = 72f;
    /// <summary>Annonce du coup (s), multipliée par l'option d'aide (plafond x2).</summary>
    [Export(PropertyHint.Range, "0.5,4,0.1")] public float HammerAnnounceSeconds { get; set; } = 1.2f;
    [Export(PropertyHint.Range, "16,96,1")] public float HammerRadius { get; set; } = 56f;
    /// <summary>Écart (px) entre les bords des deux cercles à mi-vie (une case).</summary>
    [Export(PropertyHint.Range, "16,96,1")] public float HammerGap { get; set; } = 32f;
    /// <summary>Marteau coincé (s) : la fenêtre de coups d'épée, multipliée par l'option d'aide (plafond x2).</summary>
    [Export(PropertyHint.Range, "1,8,0.1")] public float StuckSeconds { get; set; } = 2.5f;
    [Export(PropertyHint.Range, "10,60,1")] public float ContactRadius { get; set; } = 24f;
    [Export(PropertyHint.Range, "0.2,2,0.1")] public float ContactCooldown { get; set; } = 0.8f;

    [ExportGroup("Phase 2 : les trois couches")]
    /// <summary>Annonce de chaque nouvelle couche (s), multipliée par l'option d'aide (plafond x2).</summary>
    [Export(PropertyHint.Range, "0.5,5,0.1")] public float RoundIntroSeconds { get; set; } = 2f;
    /// <summary>Pause (s) entre deux attaques d'ambiance.</summary>
    [Export(PropertyHint.Range, "0.5,6,0.1")] public float AttackGapSeconds { get; set; } = 2.2f;
    /// <summary>Annonce d'une attaque d'ambiance (s), multipliée par l'option d'aide (plafond x2).</summary>
    [Export(PropertyHint.Range, "0.5,4,0.1")] public float AttackAnnounceSeconds { get; set; } = 1.5f;
    /// <summary>Étourdissement après la couche brisée (s), multiplié par l'option d'aide (plafond x2).</summary>
    [Export(PropertyHint.Range, "1,10,0.5")] public float StunSeconds { get; set; } = 4f;
    [Export(PropertyHint.Range, "1,4,1")] public int StoneBombsNeeded { get; set; } = 2;
    [Export(PropertyHint.Range, "1,5,1")] public int BubbleCount { get; set; } = 3;
    [Export(PropertyHint.Range, "1,3,1")] public int MaxRocks { get; set; } = 3;
    [Export(PropertyHint.Range, "8,40,1")] public float ThornRadius { get; set; } = 18f;
    [Export(PropertyHint.Range, "0.3,3,0.1")] public float ThornActiveSeconds { get; set; } = 1f;
    [Export(PropertyHint.Range, "16,64,1")] public float WaveRadius { get; set; } = 30f;
    [Export(PropertyHint.Range, "0.3,3,0.1")] public float PuddleSeconds { get; set; } = 1f;

    [ExportGroup("Finale : l'Œil")]
    [Export(PropertyHint.Range, "1,6,0.1")] public float EyeHoldSeconds { get; set; } = 2.5f;
    /// <summary>Anneau doré d'arrivée (s), avant que l'Œil soit vulnérable.</summary>
    [Export(PropertyHint.Range, "0.3,3,0.1")] public float EyeRingSeconds { get; set; } = 1f;
    [Export(PropertyHint.Range, "0.5,3,0.1")] public float EyeCollapseSeconds { get; set; } = 1.8f;

    [ExportGroup("Ravitaillement")]
    /// <summary>Flèches en dessous desquelles un paquet apparaît (manche des ronces et finale).</summary>
    [Export(PropertyHint.Range, "1,30,1")] public int ArrowsBelow { get; set; } = 10;
    /// <summary>Bombes en dessous desquelles un paquet apparaît (manche de la pierre).</summary>
    [Export(PropertyHint.Range, "1,10,1")] public int BombsBelow { get; set; } = 3;
    [Export(PropertyHint.Range, "1,20,0.5")] public float SupplyDelay { get; set; } = 3f;
    [Export(PropertyHint.Range, "5,60,1")] public float SupplyLifetime { get; set; } = 30f;
    [Export(PropertyHint.Range, "32,300,8")] public float SupplyMinDistance { get; set; } = 110f;

    /// <summary>Noms d'animations que le graphiste peut fournir (art/bosses/corvan/*.tres) ; à défaut, des substituts de art/characters/.</summary>
    public static readonly string[] ExpectedAnimations =
    {
        "corvan_frames.tres (64x64) : idle_down, walk_down, leve, leve_tenu, coup, coince, touche, genoux",
        "corvan_corrompu_frames.tres (96x96) : idle, coup, touche, transition, etourdi",
        "corvan_corrompu_ronces_liane / _pierre / _eau _frames.tres (calques 96x96) : idle, coup, touche, brise, flash",
        "oeil_frames.tres (32x32) : idle, deplace, tir, touche",
        "bulle_eau_frames.tres : flotte, revelee, eclate",
        "conseil_fleche.png, conseil_bombe.png, conseil_lanterne.png",
    };

    /// <summary>Phase en cours (1 = marteau, 2 = couches et Œil ; 0 avant le combat).</summary>
    public int Phase => _state == State.Dormant ? 0 : _phase2 ? 2 : 1;
    public string StateName => _state.ToString();
    /// <summary>Manche en cours (0 ronces, 1 pierre, 2 eau).</summary>
    public int Round => _round;
    public bool LayerBroken => _layerBroken;
    public bool IsDefeated => _state == State.Victory;
    public bool EyeReleased => _eyeActive;
    public int BulbsLeft => _bulbsLeft;
    public int BubblesLeft => CountLiveBubbles();
    public int StoneHits => _stoneHits;
    public int HealthLeft => _health?.CurrentHealth ?? 0;

    public Vector2 BombHalfExtents => new(32f, 44f);

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName AnimIdle = "idle";
    private static readonly StringName AnimWalk = "walk_down";
    private static readonly StringName AnimHammerUp = "leve";
    private static readonly StringName AnimStuck = "coince";
    private static readonly StringName AnimKneel = "genoux";
    private static readonly StringName AnimStunned = "etourdi";
    private static readonly StringName AnimAttack = "coup";
    private static readonly StringName AnimTransition = "transition";
    private static readonly StringName AnimCollapse = "genoux"; // l'effondrement final est celui de Corvan normal
    private static readonly StringName AnimBreak = "brise";
    private static readonly StringName AnimMove = "deplace";
    private static readonly StringName AnimShoot = "tir";
    private static readonly StringName AnimFlash = "touche";
    private static readonly StringName AnimEyeIdle = "idle";
    private static readonly StringName AltIdle = "idle_down"; // Corvan de phase 1 : idle_down ; phase 2 et calques : idle

    private const string FramesDir = "res://art/bosses/corvan/";
    private const string ThornScenePath = "res://scenes/enemies/boss/ronces_sol.tscn";
    private const string RockScenePath = "res://scenes/enemies/boss/rocher_chute.tscn";
    private const string BubbleScenePath = "res://scenes/enemies/boss/bulle_eau.tscn";
    private const string OrbScenePath = "res://scenes/enemies/projectile_orbe.tscn";
    private const string ArrowsPackPath = "res://scenes/items/fleches.tscn";
    private const string BombsPackPath = "res://scenes/items/bombes_paquet.tscn";
    private const string HeartPath = "res://scenes/items/coeur.tscn";
    private const string CinePrends = "chateau_morvath_prend";
    private const string CineVaincu = "chateau_corvan_vaincu";
    private const string DefeatedFlag = "morvath_vaincu";
    private const int MaxSupplyPoints = 4;
    private static readonly StringName OrbGroup = "corvan_orbes";

    private static readonly Color[] LayerTint =
    {
        new(0.25f, 0.75f, 0.25f, 0.6f), // ronces
        new(0.65f, 0.65f, 0.7f, 0.75f), // pierre
        new(0.2f, 0.4f, 0.95f, 0.55f), // eau
    };
    private static readonly Color EyeRingColor = new(1f, 0.85f, 0.2f);
    private static readonly Color ShadowColor = new(0f, 0f, 0f, 0.28f);
    private static readonly Vector2[] ShadowSmall = BuildShadow(1f);
    private static readonly Vector2[] ShadowBig = BuildShadow(1.5f);

    private readonly RandomNumberGenerator _rng = new();
    private readonly List<FallingRock> _rocks = new();
    private readonly List<BossBubble> _bubbles = new();
    private readonly bool[] _hinted = new bool[CorvanRules.RoundCount];
    private readonly float[] _circleX = new float[2];
    private readonly float[] _circleY = new float[2];
    private readonly float[] _supplyX = new float[MaxSupplyPoints];
    private readonly float[] _supplyY = new float[MaxSupplyPoints];
    private readonly float[] _eyeX = new float[3];
    private readonly float[] _eyeY = new float[3];
    private int _circleCount;
    private int _supplyCount;
    private int _supplyKind = -1;
    private int _eyeCount;
    private bool _pointsLoaded;

    private State _state = State.Dormant;
    private bool _phase2;
    private bool _ready;
    private bool _ended;
    private bool _hasArrival;
    private Vector2 _arrival;
    private Vector2 _home;
    private float _timer;
    private float _animTime;
    private float _contactTimer;
    private float _hintCooldown;
    private float _supplyTimer;
    private float _grace;
    private int _round;
    private bool _layerBroken;
    private bool _heartsDropped;
    private int _stoneHits;
    private int _bulbsLeft;
    private float _puddleTimer;
    private Vector2 _puddleCenter;
    private int _attackKind;
    private Node _supplyPack;
    private StringName _bodyAnim;
    private float _bodySize = 64f;

    // Cinématique lancée par le code (transition, victoire).
    private CinematicPlayer _cine;
    private string _cineId = "";
    private bool _cineWaiting;
    private bool _cineStarted;
    private bool _cineFinished;
    private float _cineRetry;
    private float _cineTimeout;
    private bool _cineEndless;
    private ScenarioWatcher _watcher;

    // L'Œil détaché.
    private bool _eyeActive;
    private int _eyeIndex = -1;
    private Vector2 _eyeFrom;
    private Vector2 _eyeTo;
    private float _eyeMoveTime;
    private bool _eyeShot;
    private bool _eyeCharging;

    private Node2D _visual;
    private AnimatedSprite2D _body;
    private AnimatedSprite2D _layerSprite;
    private Sprite2D _icon;
    private Node2D _bulbRoot;
    private BossBulb[] _bulbs;
    private Health _health;
    private HurtBox _layerBox;
    private HurtBox _bodyBox;
    private CollisionShape2D _layerShape;
    private Node2D _eye;
    private AnimatedSprite2D _eyeSprite;
    private Health _eyeHealth;
    private HurtBox _eyeBox;
    private Player _player;
    private HurtBox _playerHurt;
    private GameState _gameState;
    private Room _room;
    private Tween _flash;
    private Tween _pop;
    private PackedScene _thornScene;
    private PackedScene _rockScene;
    private PackedScene _bubbleScene;
    private PackedScene _orbScene;
    private PackedScene _arrowsScene;
    private PackedScene _bombsScene;
    private PackedScene _heartScene;
    private SpriteFrames _frames1;
    private SpriteFrames _frames2;
    private bool _real1;
    private bool _real2;
    private readonly SpriteFrames[] _layerFrames = new SpriteFrames[CorvanRules.RoundCount];
    private readonly bool[] _layerReal = new bool[CorvanRules.RoundCount];
    private Texture2D[] _icons;
    private Texture2D _shadow1;
    private Texture2D _shadow2;
    private Sprite2D _shadow;

    public override void _EnterTree() => Bomb.Register(this);

    public override void _Ready()
    {
        _rng.Randomize();
        _gameState = GetNode<GameState>("/root/GameState");
        if (_gameState.IsCollected(BossId))
        {
            QueueFree(); // déjà vaincu : la salle ne devrait pas l'instancier
            return;
        }

        _home = GlobalPosition;
        _visual = GetNode<Node2D>("Visuel");
        _body = _visual.GetNode<AnimatedSprite2D>("Sprite");
        _layerSprite = _visual.GetNode<AnimatedSprite2D>("Calque");
        _icon = _visual.GetNode<Sprite2D>("Icone");
        _bulbRoot = GetNode<Node2D>("Bulbes");
        _bulbs = new BossBulb[_bulbRoot.GetChildCount()];
        for (int i = 0; i < _bulbs.Length; i++)
        {
            _bulbs[i] = _bulbRoot.GetChild<BossBulb>(i);
            _bulbs[i].Destroyed += OnBulbDestroyed;
        }
        _bulbRoot.Visible = false;

        _health = GetNode<Health>("Health");
        _health.SetValues(CorvanRules.Phase1Health, CorvanRules.Phase1Health);
        _health.Died += OnDied;
        _layerBox = GetNode<HurtBox>("Couche");
        _layerBox.Invincible = true; // toujours : le coup rebondit tant que la couche est là
        _layerBox.Blocked += OnBlocked;
        _layerShape = _layerBox.GetNode<CollisionShape2D>("CollisionShape2D");
        _bodyBox = GetNode<HurtBox>("Corps");
        _bodyBox.Hit += OnHit;

        _eye = GetNode<Node2D>("Oeil");
        _eyeSprite = _eye.GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _eyeHealth = _eye.GetNode<Health>("Health");
        _eyeHealth.SetValues(CorvanRules.EyeHealth, CorvanRules.EyeHealth);
        _eyeHealth.Died += OnEyeDied;
        _eyeBox = _eye.GetNode<HurtBox>("HurtBox");
        _eyeBox.Hit += OnEyeHit;
        _eyeSprite.AnimationFinished += OnEyeAnimationFinished;
        _eye.Visible = false;
        _eyeBox.SetDeferred(Area2D.PropertyName.Monitorable, false);

        _thornScene = GD.Load<PackedScene>(ThornScenePath);
        _rockScene = GD.Load<PackedScene>(RockScenePath);
        _bubbleScene = GD.Load<PackedScene>(BubbleScenePath);
        _orbScene = GD.Load<PackedScene>(OrbScenePath);
        _arrowsScene = GD.Load<PackedScene>(ArrowsPackPath);
        _bombsScene = GD.Load<PackedScene>(BombsPackPath);
        _heartScene = GD.Load<PackedScene>(HeartPath);
        if (ArenaBounds.Size == Vector2.Zero)
            ArenaBounds = new Rect2(90f, 90f, 460f, 524f);

        LoadVisuals();
        _room = FindRoom();
        _ready = true;
        SetState(State.Dormant, 0f);
        PlayBody(AnimIdle);
    }

    public override void _ExitTree()
    {
        Bomb.Unregister(this);
        if (!_ready) return;
        UnhookCinematic();
        ClearAttackEffects();
        ClearBubbles();
        FreeSupplyPack();
        if (_health != null) _health.Died -= OnDied;
        if (_layerBox != null) _layerBox.Blocked -= OnBlocked;
        if (_bodyBox != null) _bodyBox.Hit -= OnHit;
        if (_eyeHealth != null) _eyeHealth.Died -= OnEyeDied;
        if (_eyeBox != null) _eyeBox.Hit -= OnEyeHit;
        if (_eyeSprite != null) _eyeSprite.AnimationFinished -= OnEyeAnimationFinished;
        if (_bulbs != null)
            foreach (var bulb in _bulbs)
                if (IsInstanceValid(bulb)) bulb.Destroyed -= OnBulbDestroyed;
    }

    // --- Boucle ---------------------------------------------------------------------------------

    public override void _PhysicsProcess(double delta)
    {
        if (!_ready) return;
        float dt = (float)delta;
        _animTime += dt;
        if (_hintCooldown > 0f) _hintCooldown -= dt;
        if (_contactTimer > 0f) _contactTimer -= dt;
        if (_grace > 0f) _grace -= dt;
        FindPlayer();

        if (_player != null && _player.IsDead && _state != State.Victory)
        {
            // Brann est tombé : le boss se calme en attendant le rechargement (ou la reprise à l'antichambre).
            if (!_ended && _state != State.Dormant)
            {
                _ended = true;
                EmitSignal(Boss.SignalName.EncounterEnded);
            }
            return;
        }

        UpdateCinematicWait(dt);
        _timer -= dt;
        if (_phase2 && _state != State.Victory && _state != State.Transition) UpdateSupply(dt);
        UpdatePuddle(dt);
        UpdateIcon();

        switch (_state)
        {
            case State.Dormant: UpdateDormant(); break;
            case State.Chase: UpdateChase(dt); break;
            case State.Announce: UpdateAnnounce(); break;
            case State.Stuck: UpdateStuck(); break;
            case State.Transition: UpdateTransition(dt); break;
            case State.RoundIntro: if (_timer <= 0f) BeginRoundIdle(); break;
            case State.RoundIdle: if (_timer <= 0f) BeginRoundWarn(); break;
            case State.RoundWarn: if (_timer <= 0f) BeginRoundAttack(); break;
            case State.RoundAttack: if (_timer <= 0f) EndRoundAttack(); break;
            case State.Stunned: UpdateStunned(); break;
            case State.Release: UpdateRelease(); break;
            case State.EyeMove: UpdateEyeMove(dt); break;
            case State.EyeHold: UpdateEyeHold(); break;
        }
    }

    private void UpdateDormant()
    {
        if (_player == null) return;
        if (!_hasArrival)
        {
            _arrival = EntryPoint ?? _player.GlobalPosition;
            _hasArrival = true;
            return;
        }
        // Le défi (dialogue de Corvan) passe avant : le combat ne commence ni pendant une cinématique, ni juste avant qu'elle parte.
        if (CinematicPlayer.Active || (_room?.Cinematics?.IsPlaying ?? false)) return;
        _watcher ??= _room?.GetNodeOrNull<ScenarioWatcher>("Scenarios"); // créé par la Room après le boss : cherché jusqu'à ce qu'il existe
        if (_watcher != null && IsInstanceValid(_watcher) && _watcher.HasPendingPointScenario()) return;
        if (_player.GlobalPosition.DistanceSquaredTo(_arrival) >= StartDistance * StartDistance)
            StartEncounter();
    }

    private void StartEncounter()
    {
        foreach (var door in ArenaDoors)
            if (IsInstanceValid(door)) door.LockForEncounter();
        AddCollisionExceptionWith(_player); // Corvan traverse Brann (le contact le blesse) : il ne s'arrête que sur murs et piliers
        EmitSignal(Boss.SignalName.EncounterStarted);
        AudioManager.Play(Sfx.BossRugit);
        EmitSignal(Boss.SignalName.HintRequested, "BOSS_CORVAN_CONSEIL_1", 8f);
        EmitProgress();
        ShakeCamera(3f, 0.6f);
        BeginChase();
    }

    // --- Phase 1 : le marteau ---------------------------------------------------------------------

    private void BeginChase()
    {
        SetState(State.Chase, ChaseMaxSeconds);
        PlayBody(AnimWalk);
    }

    private void UpdateChase(float dt)
    {
        if (_player == null) return;
        var to = PlayerFeet() - GlobalPosition;
        float dist = to.Length();
        if (dist <= StrikeDistance || _timer <= 0f)
        {
            BeginAnnounce();
            return;
        }
        Velocity = to / dist * ChaseSpeed;
        MoveAndSlide();
        // Contact : un demi-cœur, sans rafale (Brann est ensuite invincible un instant).
        if (_contactTimer <= 0f && dist < ContactRadius && _playerHurt != null && IsInstanceValid(_playerHurt))
        {
            _contactTimer = ContactCooldown;
            _playerHurt.ReceiveHit(CorvanRules.ContactDamage, GlobalPosition);
        }
    }

    private void BeginAnnounce()
    {
        float seconds = CorvanRules.HelpSeconds(HammerAnnounceSeconds, _gameState.PuzzleTimeMultiplier);
        SetState(State.Announce, seconds);
        PlayBody(AnimHammerUp);
        AudioManager.PlayAt(Sfx.BossCharge, GlobalPosition);

        var floor = ArenaBounds.Grow(30f);
        var target = ClampTo(floor, PlayerFeet());
        _circleCount = CorvanRules.HammerCircleCount(_health.CurrentHealth, CorvanRules.Phase1Health);
        _circleX[0] = target.X;
        _circleY[0] = target.Y;
        if (_circleCount > 1)
        {
            // Le second cercle est posé de côté, avec une case d'écart entre les deux bords : Brann peut toujours fuir de l'autre côté.
            var away = target - GlobalPosition;
            var side = away.LengthSquared() > 1f ? new Vector2(-away.Y, away.X).Normalized() : Vector2.Right;
            float sign = _rng.Randf() < 0.5f ? -1f : 1f;
            float offset = HammerRadius * 2f + HammerGap;
            var second = target + side * sign * offset;
            if (!floor.HasPoint(second)) second = target - side * sign * offset;
            second = ClampTo(floor, second);
            _circleX[1] = second.X;
            _circleY[1] = second.Y;
        }
        for (int i = 0; i < _circleCount; i++)
            SpawnMark(CorvanGroundMark.Kind.HammerWarn, new Vector2(_circleX[i], _circleY[i]), HammerRadius, seconds)
                .UseImage(FramesDir + "ombre_marteau_frames.tres", "remplit", Vector2.Zero);
    }

    private void UpdateAnnounce()
    {
        if (_timer > 0f) return;
        // Le coup : poussière, dégâts à qui est dans un cercle, puis le marteau reste coincé.
        AudioManager.PlayAt(Sfx.Eboulement, GlobalPosition);
        ShakeCamera(4f, 0.4f);
        var feet = _player != null ? PlayerFeet() : Vector2.Zero;
        for (int i = 0; i < _circleCount; i++)
        {
            var center = new Vector2(_circleX[i], _circleY[i]);
            SpawnMark(CorvanGroundMark.Kind.HammerImpact, center, HammerRadius, 0.4f)
                .UseImage(FramesDir + "poussiere_frames.tres", "impact", new Vector2(0f, -8f));
            if (_player != null && _playerHurt != null && IsInstanceValid(_playerHurt)
                && CorvanRules.InCircle(feet.X - center.X, feet.Y - center.Y, HammerRadius))
                _playerHurt.ReceiveHit(CorvanRules.HammerDamage, center);
        }
        SetState(State.Stuck, CorvanRules.HelpSeconds(StuckSeconds, _gameState.PuzzleTimeMultiplier));
        PlayBody(AnimStuck);
    }

    private void UpdateStuck()
    {
        if (_timer <= 0f) BeginChase(); // le marteau se libère
    }

    private void OnHit(int damage, Vector2 fromPosition)
    {
        // Died arrive avant Hit : si la vie est tombée à 0, l'état a déjà changé.
        if (_state != State.Stuck && _state != State.Stunned) return;
        FlashBody(new Color(4f, 4f, 4f), 0.12f);
        EmitProgress();
    }

    private void OnDied()
    {
        EmitProgress();
        if (!_phase2) BeginTransition();
        else FinishRound();
    }

    // --- Transition -------------------------------------------------------------------------------

    private void BeginTransition()
    {
        ClearAttackEffects();
        SetState(State.Transition, 0f);
        PlayBody(AnimKneel);
        AudioManager.Play(Sfx.BossAssomme);
        ShakeCamera(4f, 0.8f);
        StartCinematic(CinePrends);
    }

    private void UpdateTransition(float dt)
    {
        // Corvan regagne sa place pendant que la cinématique joue.
        var to = _home - GlobalPosition;
        if (to.LengthSquared() > 4f)
        {
            Velocity = to.Normalized() * 120f;
            MoveAndSlide();
        }
        if (_cineFinished && !_cineWaiting) BeginPhase2();
    }

    private void BeginPhase2()
    {
        _phase2 = true;
        _round = 0;
        GlobalPosition = _home;
        SetBodyFrames(_body, _frames2, _real2, 96f);
        _bodySize = 96f;
        if (_shadow != null && _shadow2 != null) { _shadow.Texture = _shadow2; _shadow.Offset = new Vector2(-48f, -93f); }
        _bodyAnim = null;
        PlayBody(AnimTransition);
        _pop?.Kill();
        _body.Scale *= 0.7f;
        _pop = CreateTween();
        _pop.TweenProperty(_body, "scale", _real2 ? Vector2.One : Vector2.One * (96f / 32f), 0.5f).SetTrans(Tween.TransitionType.Back).SetEase(Tween.EaseType.Out);
        Callable.From(DropHearts).CallDeferred();
        EmitSignal(Boss.SignalName.HintRequested, "BOSS_CORVAN_CONSEIL_2", 8f);
        _hinted[0] = true;
        BeginRoundIntro(0);
    }

    // --- Phase 2 : manches ------------------------------------------------------------------------

    private void BeginRoundIntro(int round)
    {
        _round = round;
        _layerBroken = false;
        _heartsDropped = false;
        _stoneHits = 0;
        _health.SetValues(CorvanRules.RoundHealth, CorvanRules.RoundHealth);
        ClearAttackEffects();
        SetState(State.RoundIntro, CorvanRules.HelpSeconds(RoundIntroSeconds, _gameState.PuzzleTimeMultiplier));
        if (round > 0) PlayBody(AnimIdle); // la première fois, l'animation « transition » (Morvath se relève) continue
        SetupLayer(round);
        EmitProgress();
        if (!_hinted[round])
        {
            _hinted[round] = true;
            EmitSignal(Boss.SignalName.HintRequested, CorvanRules.RoundHintKey(round), 8f);
        }
        AudioManager.PlayAt(Sfx.BossCharge, GlobalPosition);
        FlashBody(LayerTint[round] * 3f, 0.5f);
        _supplyTimer = SupplyDelay;
        // Différé : ce code peut tourner dans un signal de physique (mort, bombe, flèche) où l'ajout d'une Area2D est interdit.
        if (round == CorvanRules.RoundWater) Callable.From(SpawnBubbles).CallDeferred();
    }

    // La couche de la manche : calque coloré, bulbes (ronces), forme de la zone qui bloque les coups.
    private void SetupLayer(int round)
    {
        _layerSprite.Visible = true;
        SetBodyFrames(_layerSprite, _layerReal[round] ? _layerFrames[round] : _frames2, _layerReal[round], 96f);
        _layerSprite.SelfModulate = _layerReal[round] ? Colors.White : LayerTint[round];
        _layerSprite.Play(ResolveAnim(_layerSprite.SpriteFrames, AnimIdle) ?? AltIdle);
        if (round == CorvanRules.RoundThorns)
        {
            _bulbsLeft = _bulbs.Length;
            _bulbRoot.Visible = true;
            foreach (var bulb in _bulbs)
                if (IsInstanceValid(bulb)) bulb.Armed = true;
        }
        _icon.Texture = _icons != null ? _icons[round] : null;
    }

    private void BeginRoundIdle()
    {
        SetState(State.RoundIdle, AttackGapSeconds);
        PlayBody(AnimIdle);
    }

    private void BeginRoundWarn()
    {
        float warn = CorvanRules.HelpSeconds(AttackAnnounceSeconds, _gameState.PuzzleTimeMultiplier);
        _attackKind = _round;
        SetState(State.RoundWarn, warn);
        PlayBody(AnimAttack);
        AudioManager.PlayAt(Sfx.BossCharge, GlobalPosition);
        switch (_round)
        {
            case CorvanRules.RoundThorns: StartThorns(warn); break;
            case CorvanRules.RoundStone: StartRocks(warn); break;
            default: StartWave(warn); break;
        }
    }

    private void BeginRoundAttack()
    {
        // Les ronces et les rochers frappent d'eux-mêmes ; l'eau devient une flaque.
        float seconds = _round == CorvanRules.RoundWater ? PuddleSeconds : ThornActiveSeconds;
        SetState(State.RoundAttack, seconds + 0.2f);
        if (_round == CorvanRules.RoundWater && _player != null)
        {
            _puddleCenter = _puddleCenterPending;
            _puddleTimer = PuddleSeconds;
            SpawnMark(CorvanGroundMark.Kind.Puddle, _puddleCenter, WaveRadius, PuddleSeconds);
            TryPuddleHit();
        }
        PlayBody(AnimIdle);
    }

    private void EndRoundAttack()
    {
        if (_layerBroken) BeginStunned();
        else BeginRoundIdle();
    }

    // La couche cède : tout ce qui menace est effacé, il est étourdi et deux petits cœurs tombent (une fois par manche).
    private void BreakLayer()
    {
        if (_layerBroken || !_phase2 || _state == State.Transition || _state == State.Victory) return;
        _layerBroken = true;
        ClearAttackEffects();
        AudioManager.PlayAt(Sfx.BossAssomme, GlobalPosition);
        ShakeCamera(4f, 0.5f);
        FlashBody(new Color(3f, 3f, 3.5f), 0.4f);
        if (_layerSprite.SpriteFrames != null && _layerSprite.SpriteFrames.HasAnimation(AnimBreak))
            _layerSprite.Play(AnimBreak);
        else
            _layerSprite.Visible = false;
        if (_round == CorvanRules.RoundThorns) _bulbRoot.Visible = false;
        if (!_heartsDropped)
        {
            _heartsDropped = true;
            Callable.From(DropHearts).CallDeferred();
        }
        BeginStunned();
    }

    private void BeginStunned()
    {
        SetState(State.Stunned, CorvanRules.HelpSeconds(StunSeconds, _gameState.PuzzleTimeMultiplier));
        PlayBody(AnimStunned);
        if (_layerSprite.Visible && !(_layerSprite.SpriteFrames?.HasAnimation(AnimBreak) ?? false)) _layerSprite.Visible = false;
    }

    private void UpdateStunned()
    {
        if (_layerSprite.Visible && _layerBroken && !_layerSprite.IsPlaying()) _layerSprite.Visible = false;
        if (_timer <= 0f) BeginRoundIdle(); // l'étourdissement passe : la couche ne revient pas, la prochaine attaque l'étourdira de nouveau
    }

    // 0 PV dans la manche : la couche suivante, ou la finale.
    private void FinishRound()
    {
        ClearAttackEffects();
        ClearBubbles();
        _layerSprite.Visible = false;
        _bulbRoot.Visible = false;
        if (_round + 1 < CorvanRules.RoundCount) BeginRoundIntro(_round + 1);
        else BeginRelease();
    }

    // --- Attaques d'ambiance ---------------------------------------------------------------------

    private Vector2 _puddleCenterPending;

    // Ronces : une ligne de pointes qui part d'un pilier, dans l'axe où Brann se trouve le plus près.
    private void StartThorns(float warn)
    {
        if (_player == null || _thornScene == null) return;
        var feet = PlayerFeet();
        var floor = ArenaBounds.Grow(30f);
        Rect2 pillar = Pillars.Count > 0 ? Pillars[_rng.RandiRange(0, Pillars.Count - 1)] : new Rect2(floor.GetCenter() - new Vector2(32f, 32f), new Vector2(64f, 64f));
        var c = pillar.GetCenter();
        bool vertical = Mathf.Abs(feet.X - c.X) <= Mathf.Abs(feet.Y - c.Y);
        float sign = (vertical ? feet.Y - c.Y : feet.X - c.X) >= 0f ? 1f : -1f;
        var dir = vertical ? new Vector2(0f, sign) : new Vector2(sign, 0f);
        float startDist = (vertical ? pillar.Size.Y : pillar.Size.X) * 0.5f + 20f;
        float limit = vertical ? (sign > 0f ? floor.End.Y - c.Y : c.Y - floor.Position.Y) : (sign > 0f ? floor.End.X - c.X : c.X - floor.Position.X);
        int count = CorvanRules.ThornCount(limit - startDist, 32f, 14);
        for (int i = 0; i < count; i++)
        {
            var p = c + dir * (startDist + 32f * i);
            if (IsInsidePillar(p, 8f)) continue;
            var thorn = _thornScene.Instantiate<ThornEruption>();
            thorn.WarnDuration = warn;
            thorn.ActiveDuration = ThornActiveSeconds;
            thorn.Radius = ThornRadius;
            thorn.GetNode<HitBox>("HitBox").Damage = CorvanRules.AmbientDamage;
            GetParent().AddChild(thorn);
            thorn.GlobalPosition = p - new Vector2(0f, ThornEruption.SortOffset);
        }
    }

    // Pierre : jusqu'à trois rochers, dont un sur Brann (ombre d'abord, comme Gorm).
    private void StartRocks(float warn)
    {
        if (_player == null || _rockScene == null) return;
        PruneRocks();
        var floor = ArenaBounds.Grow(30f);
        var target = ClampTo(floor, PlayerFeet());
        for (int i = 0; i < MaxRocks; i++)
        {
            var pos = target;
            if (i > 0)
            {
                bool placed = false;
                for (int attempt = 0; attempt < 8 && !placed; attempt++)
                {
                    var candidate = ClampTo(floor, target + Vector2.Right.Rotated(_rng.RandfRange(0f, Mathf.Tau)) * _rng.RandfRange(48f, 130f));
                    if (IsInsidePillar(candidate, 16f)) continue;
                    pos = candidate;
                    placed = true;
                }
                if (!placed) continue;
            }
            var rock = _rockScene.Instantiate<FallingRock>();
            rock.WarnDuration = warn;
            rock.GetNode<HitBox>("HitBox").Damage = CorvanRules.AmbientDamage;
            GetParent().AddChild(rock);
            rock.GlobalPosition = pos - new Vector2(0f, FallingRock.SortOffset);
            _rocks.Add(rock);
        }
    }

    // Eau : anneau d'ondes à l'endroit où se trouve Brann (il ne le suit pas), puis flaque.
    private void StartWave(float warn)
    {
        if (_player == null) return;
        _puddleCenterPending = ClampTo(ArenaBounds.Grow(30f), PlayerFeet());
        SpawnMark(CorvanGroundMark.Kind.WaveRing, _puddleCenterPending, WaveRadius, warn);
        AudioManager.Play(Sfx.Glou);
    }

    private void UpdatePuddle(float dt)
    {
        if (_puddleTimer <= 0f) return;
        _puddleTimer -= dt;
        if (_puddleTimer > 0f && _puddleTimer < PuddleSeconds * 0.5f && _puddleTimer + dt >= PuddleSeconds * 0.5f) TryPuddleHit();
    }

    private void TryPuddleHit()
    {
        if (_player == null || _playerHurt == null || !IsInstanceValid(_playerHurt)) return;
        var feet = PlayerFeet();
        if (CorvanRules.InCircle(feet.X - _puddleCenter.X, feet.Y - _puddleCenter.Y, WaveRadius))
            _playerHurt.ReceiveHit(CorvanRules.WaterDamage, _puddleCenter);
    }

    private bool IsInsidePillar(Vector2 p, float margin)
    {
        for (int i = 0; i < Pillars.Count; i++)
        {
            var r = Pillars[i];
            if (BossRules.IsInsideRect(p.X, p.Y, r.Position.X, r.Position.Y, r.Size.X, r.Size.Y, margin)) return true;
        }
        return false;
    }

    private void PruneRocks()
    {
        for (int i = _rocks.Count - 1; i >= 0; i--)
            if (!IsInstanceValid(_rocks[i]) || _rocks[i].IsQueuedForDeletion()) _rocks.RemoveAt(i);
    }

    // Efface tout ce qui menace : ronces, rochers, orbes de l'Œil, cercles et anneaux.
    private void ClearAttackEffects()
    {
        foreach (var rock in _rocks)
            if (IsInstanceValid(rock)) rock.QueueFree();
        _rocks.Clear();
        _puddleTimer = 0f;
        if (!IsInsideTree()) return;
        foreach (var node in GetTree().GetNodesInGroup(CorvanGroundMark.GroupName))
            if (node is CorvanGroundMark mark && mark.GetParent() == _room) mark.QueueFree();
        foreach (var node in GetTree().GetNodesInGroup(OrbGroup))
            if (node is Node orb && GetParent() != null && orb.GetParent() == GetParent()) orb.QueueFree();
        foreach (var node in GetTree().GetNodesInGroup(ThornEruption.GroupName))
            if (node is Node thorn && GetParent() != null && thorn.GetParent() == GetParent()) thorn.QueueFree();
    }

    // --- Couches : ronces (bulbes), pierre (bombes), eau (bulles) -------------------------------

    private void OnBulbDestroyed()
    {
        if (_bulbsLeft <= 0) return;
        _bulbsLeft--;
        AudioManager.PlayAt(Sfx.FlecheImpact, GlobalPosition);
        if (_bulbsLeft == 0 && _phase2 && _round == CorvanRules.RoundThorns) BreakLayer();
    }

    /// <summary>Une bombe explose à portée : arrache la couche de pierre (manche 2 seulement, jamais deux fois pour la même explosion).</summary>
    public void OnBombExplosion(Vector2 center)
    {
        if (!_ready || !_phase2 || _round != CorvanRules.RoundStone || _layerBroken) return;
        if (_state == State.Transition || _state == State.Victory || _state == State.Dormant) return;
        if (_grace > 0f) return;
        _grace = 0.4f;
        _stoneHits++;
        FlashBody(new Color(4f, 4f, 4f), 0.2f);
        ShakeCamera(4f, 0.4f);
        AudioManager.PlayAt(Sfx.BossAssomme, GlobalPosition);
        if (_stoneHits >= StoneBombsNeeded) BreakLayer();
    }

    private void SpawnBubbles()
    {
        if (!IsInsideTree() || !_phase2 || _round != CorvanRules.RoundWater || _layerBroken) return;
        ClearBubbles();
        if (_bubbleScene == null) return;
        // La lumière de la lanterne n'existe pas dans une salle claire : un cercle clair suit Brann pour montrer sa portée.
        if (_player != null)
        {
            var guide = new CorvanGroundMark { Name = "GuideLanterne" };
            (_room ?? GetParent())?.AddChild(guide);
            guide.BeginGuide(_player);
            PlaceMarkUnderEntities(guide);
        }
        for (int i = 0; i < BubbleCount; i++)
        {
            var bubble = _bubbleScene.Instantiate<BossBubble>();
            bubble.OrbitCenter = _home + new Vector2(0f, -40f);
            bubble.Phase = i * Mathf.Tau / BubbleCount;
            bubble.OrbitRadius = 62f + 8f * (i % 2);
            bubble.Popped += OnBubblePopped;
            GetParent().AddChild(bubble);
            _bubbles.Add(bubble);
        }
    }

    private void OnBubblePopped()
    {
        for (int i = _bubbles.Count - 1; i >= 0; i--)
            if (!IsInstanceValid(_bubbles[i]) || _bubbles[i].IsQueuedForDeletion() || !_bubbles[i].IsInsideTree()) _bubbles.RemoveAt(i);
        // Le signal est émis avant le QueueFree : on retire celle qui vient d'éclater en comptant les bulles encore vivantes.
        if (_phase2 && _round == CorvanRules.RoundWater && !_layerBroken && CountLiveBubbles() == 0) BreakLayer();
    }

    private int CountLiveBubbles()
    {
        int live = 0;
        for (int i = 0; i < _bubbles.Count; i++)
            if (IsInstanceValid(_bubbles[i]) && !_bubbles[i].IsQueuedForDeletion() && !_bubbles[i].IsPopped) live++;
        return live;
    }

    private void ClearBubbles()
    {
        foreach (var bubble in _bubbles)
        {
            if (!IsInstanceValid(bubble)) continue;
            bubble.Popped -= OnBubblePopped;
            bubble.QueueFree();
        }
        _bubbles.Clear();
        if (!IsInsideTree()) return;
        foreach (var node in GetTree().GetNodesInGroup(CorvanGroundMark.GroupName))
            if (node is CorvanGroundMark mark && mark.Name == "GuideLanterne") mark.QueueFree();
    }

    // Coup sur la couche : un éclat bleu montre que rien ne passe, et un rappel (sans spammer) dit quoi utiliser.
    private void OnBlocked(int damage, Vector2 fromPosition)
    {
        if (_state == State.Dormant || _state == State.Transition || _state == State.Victory) return;
        FlashBody(new Color(0.3f, 0.6f, 3f), 0.3f);
        AudioManager.PlayAt(Sfx.FlecheImpact, fromPosition);
        if (_hintCooldown <= 0f)
        {
            _hintCooldown = 10f;
            string key = _phase2 ? CorvanRules.RoundHintKey(_round) : "BOSS_CORVAN_CONSEIL_1";
            EmitSignal(Boss.SignalName.HintRequested, key, 6f);
        }
    }

    // --- Finale : l'Œil ---------------------------------------------------------------------------

    private void BeginRelease()
    {
        ClearAttackEffects();
        SetState(State.Release, EyeCollapseSeconds);
        SetBodyFrames(_body, _frames1, _real1, 64f);
        _bodySize = 64f;
        _body.Scale = _real1 ? Vector2.One : Vector2.One * 2f;
        if (_shadow != null && _shadow1 != null) { _shadow.Texture = _shadow1; _shadow.Offset = new Vector2(-32f, -62f); }
        _bodyAnim = null;
        PlayBody(AnimCollapse);
        _layerSprite.Visible = false;
        AudioManager.Play(Sfx.BossAssomme);
        ShakeCamera(5f, 0.8f);
        FlashBody(new Color(3f, 3f, 2.4f), 0.6f);
        EmitSignal(Boss.SignalName.HintRequested, "BOSS_CORVAN_CONSEIL_5", 8f);
        _eyeHealth.SetValues(CorvanRules.EyeHealth, CorvanRules.EyeHealth);
        EmitProgress();
        _supplyTimer = SupplyDelay;
    }

    private void UpdateRelease()
    {
        if (!_eyeActive && _timer < EyeCollapseSeconds * 0.5f)
        {
            _eyeActive = true;
            _eye.Visible = true;
            _eye.GlobalPosition = _home + new Vector2(0f, -70f);
            PlayEye(AnimEyeIdle);
        }
        if (_timer <= 0f) BeginEyeMove();
    }

    private void BeginEyeMove()
    {
        LoadPoints();
        int next = CorvanRules.NextEyePoint(_eyeCount, _eyeIndex, _rng.Randf());
        if (next < 0) { _eyeX[0] = _home.X; _eyeY[0] = _home.Y - 70f; _eyeCount = 1; next = 0; }
        _eyeIndex = next;
        _eyeFrom = _eye.GlobalPosition;
        _eyeTo = new Vector2(_eyeX[next], _eyeY[next]);
        _eyeMoveTime = 0f;
        _eyeShot = false;
        _eyeCharging = false;
        SetState(State.EyeMove, EyeRingSeconds);
        PlayEye(AnimMove);
        SpawnMark(CorvanGroundMark.Kind.WaveRing, _eyeTo, 34f, EyeRingSeconds, EyeRingColor)
            .UseImage(FramesDir + "oeil_anneau_frames.tres", "arrivee", Vector2.Zero);
    }

    private void UpdateEyeMove(float dt)
    {
        _eyeMoveTime += dt;
        float k = Mathf.Clamp(_eyeMoveTime / (EyeRingSeconds * 0.6f), 0f, 1f);
        _eye.GlobalPosition = _eyeFrom.Lerp(_eyeTo, Mathf.SmoothStep(0f, 1f, k));
        if (_timer <= 0f)
        {
            _eye.GlobalPosition = _eyeTo;
            SetState(State.EyeHold, CorvanRules.HelpSeconds(EyeHoldSeconds, _gameState.PuzzleTimeMultiplier));
            PlayEye(AnimEyeIdle);
        }
    }

    private void UpdateEyeHold()
    {
        // Annonce du tir : l'Œil s'illumine (0,6 s), puis l'orbe part vers Brann.
        float total = CorvanRules.HelpSeconds(EyeHoldSeconds, _gameState.PuzzleTimeMultiplier);
        float elapsed = total - _timer;
        float chargeAt = total * 0.28f;
        float fireAt = chargeAt + 0.6f;
        if (!_eyeShot && !_eyeCharging && elapsed >= chargeAt)
        {
            _eyeCharging = true;
            AudioManager.PlayAt(Sfx.BossCharge, _eye.GlobalPosition);
        }
        if (_eyeCharging)
        {
            float pulse = 1f + 1.5f * Mathf.Abs(Mathf.Sin(_animTime * 14f));
            _eyeSprite.SelfModulate = new Color(pulse, pulse, 1f);
        }
        if (!_eyeShot && elapsed >= fireAt)
        {
            _eyeShot = true;
            _eyeCharging = false;
            _eyeSprite.SelfModulate = Colors.White;
            FireOrb();
        }
        if (_timer <= 0f)
        {
            _eyeSprite.SelfModulate = Colors.White;
            BeginEyeMove();
        }
    }

    private void FireOrb()
    {
        if (_orbScene == null || _player == null) return;
        PlayEye(AnimShoot);
        var from = _eye.GlobalPosition;
        var orb = _orbScene.Instantiate<Projectile>();
        orb.GetNode<HitBox>("HitBox").Damage = CorvanRules.AmbientDamage;
        orb.Launch((_player.GlobalPosition + new Vector2(0f, -4f) - from).Normalized());
        orb.AddToGroup(OrbGroup);
        GetParent().AddChild(orb);
        orb.GlobalPosition = from;
    }

    private void OnEyeHit(int damage, Vector2 fromPosition)
    {
        if (_state != State.EyeHold) return;
        FlashEye();
        EmitProgress();
    }

    private void OnEyeAnimationFinished()
    {
        if (!_eyeActive) return;
        if (_state == State.Victory) { _eye.Visible = false; return; } // fin de l'éclat de mort
        if (_eyeSprite.Animation == AnimShoot || _eyeSprite.Animation == AnimFlash) PlayEye(AnimEyeIdle);
    }

    private void OnEyeDied()
    {
        EmitProgress();
        BeginVictory();
    }

    // --- Victoire ---------------------------------------------------------------------------------

    private void BeginVictory()
    {
        SetState(State.Victory, 0f);
        ClearAttackEffects();
        FreeSupplyPack();
        _eyeSprite.SelfModulate = Colors.White;
        _eyeBox.SetDeferred(Area2D.PropertyName.Monitorable, false);
        if (_eyeSprite.SpriteFrames != null && _eyeSprite.SpriteFrames.HasAnimation(AnimFlash)) _eyeSprite.Play(AnimFlash);
        else _eye.Visible = false;
        AudioManager.Play(Sfx.BossVaincu);
        ShakeCamera(5f, 1.0f);

        // Boss vaincu mémorisé tout de suite : le combat ne se rejoue pas.
        // morvath_vaincu et la sauvegarde viennent de la cinématique (étapes « drapeau » puis « sauvegarder »), jamais avant elle ;
        // si le jeu est quitté pendant la scène, la Room la relance (PendingCinematicWhenDefeated).
        _gameState.MarkCollected(BossId);
        foreach (var door in ArenaDoors)
            if (IsInstanceValid(door)) door.UnlockAfterEncounter();
        EmitSignal(Boss.SignalName.EncounterEnded);
        EmitSignal(Boss.SignalName.Defeated);

        // Corvan (écroulé) cède la place au vieil homme de la cinématique.
        _visual.Visible = false;
        StartCinematic(CineVaincu, true);
    }

    public override string EncounterMusic => MusicRules.FinalBattle;

    public override bool VictoryJingle => false; // la cinématique de fin (chateau_corvan_vaincu) enchaîne

    public override string PendingCinematicWhenDefeated(GameState state) =>
        state.IsCollected(DefeatedFlag) ? "" : CineVaincu;

    // --- Cinématiques lancées par le code ---------------------------------------------------------

    private void StartCinematic(string id, bool endless = false)
    {
        _cineEndless = endless; // la victoire réessaie sans limite : on ne reste jamais coincé dans l'arène
        UnhookCinematic();
        _cineId = id;
        _cineFinished = false;
        _cineStarted = false;
        _cine = _room?.Cinematics;
        if (_cine == null || CinematicLibrary.Get(id) == null)
        {
            GD.PushWarning($"Corvan : cinématique « {id} » indisponible, la suite du combat continue sans elle.");
            _cineWaiting = false;
            _cineFinished = true;
            return;
        }
        _cine.Finished += OnCinematicFinished;
        _cineWaiting = true;
        _cineRetry = 0f;
        _cineTimeout = 8f;
    }

    // Lancée dès que possible (une autre cinématique ou un état de Brann peuvent la retarder) ; abandonnée après un délai.
    private void UpdateCinematicWait(float dt)
    {
        if (!_cineWaiting || _cineStarted) return;
        _cineTimeout -= dt;
        _cineRetry -= dt;
        if (_cineRetry > 0f && (_cineTimeout > 0f || _cineEndless)) return;
        _cineRetry = 0.2f;
        if (_cineTimeout <= 0f && !_cineEndless)
        {
            GD.PushWarning($"Corvan : la cinématique « {_cineId} » n'a pas pu démarrer, la suite continue sans elle.");
            _cineWaiting = false;
            _cineFinished = true;
            UnhookCinematic();
            return;
        }
        if (_cine == null || !IsInstanceValid(_cine) || _cine.IsPlaying) return;
        var data = CinematicLibrary.Get(_cineId);
        SafePlay(_cine, data);
        _cineStarted = _cine.IsPlaying;
    }

    // Play est asynchrone : IsPlaying passe à vrai tout de suite ; une exception serait sinon avalée en silence.
    private static async void SafePlay(CinematicPlayer cine, CinematicData data)
    {
        try { await cine.Play(data); }
        catch (System.Exception e) { GD.PushError($"Corvan : cinématique « {data?.Id} » interrompue : {e.Message}"); }
    }

    private void OnCinematicFinished(string id, bool skipped)
    {
        if (id != _cineId) return;
        _cineWaiting = false;
        _cineFinished = true;
        UnhookCinematic();
    }

    private void UnhookCinematic()
    {
        if (_cine != null && IsInstanceValid(_cine)) _cine.Finished -= OnCinematicFinished;
        _cine = null;
    }

    // --- Ravitaillement et cœurs ------------------------------------------------------------------

    // Brann ne reste jamais coincé : s'il manque de flèches (ronces, finale) ou de bombes (pierre), un paquet apparaît sur un Marqueur.
    private void UpdateSupply(float dt)
    {
        bool arrows = (_state == State.Release || _state == State.EyeMove || _state == State.EyeHold)
            || (_round == CorvanRules.RoundThorns && !_layerBroken && _bulbsLeft > 0 && _state != State.Release);
        bool bombs = _round == CorvanRules.RoundStone && !_layerBroken && _stoneHits < StoneBombsNeeded
            && _state != State.Release && _state != State.EyeMove && _state != State.EyeHold;
        int kind = arrows ? 0 : bombs ? 1 : -1;
        if (kind < 0 || _state == State.Stunned)
        {
            _supplyTimer = SupplyDelay;
            return;
        }
        bool packExists = _supplyPack != null && IsInstanceValid(_supplyPack) && !_supplyPack.IsQueuedForDeletion();
        bool needed = kind == 0
            ? CorvanRules.NeedsSupply(_gameState.HasItem(GameState.BowItemId), _gameState.GetQuantity(GameState.BowItemId), ArrowsBelow, packExists)
            : CorvanRules.NeedsSupply(_gameState.HasItem(GameState.BombItemId), _gameState.GetQuantity(GameState.BombItemId), BombsBelow, packExists);
        if (!needed)
        {
            _supplyTimer = SupplyDelay;
            return;
        }
        _supplyTimer -= dt;
        if (_supplyTimer > 0f) return;
        _supplyTimer = SupplyDelay;
        var scene = kind == 0 ? _arrowsScene : _bombsScene;
        if (scene == null) return;
        LoadPoints();
        SelectSupplyPoints(kind);
        var from = _player != null ? _player.GlobalPosition : GlobalPosition;
        int i = GormRules.PickSupplyPoint(_supplyX, _supplyY, _supplyCount, GlobalPosition.X, GlobalPosition.Y, from.X, from.Y, SupplyMinDistance);
        if (i < 0) return;
        var pack = scene.Instantiate<Pickup>();
        pack.Lifetime = SupplyLifetime;
        GetParent().AddChild(pack); // le Pickup épingle son effet (ResourceKeeper.Pin) dans son _Ready
        pack.GlobalPosition = new Vector2(_supplyX[i], _supplyY[i]);
        _supplyPack = pack;
    }

    private void FreeSupplyPack()
    {
        if (_supplyPack != null && IsInstanceValid(_supplyPack)) _supplyPack.QueueFree();
        _supplyPack = null;
    }

    private void DropHearts()
    {
        if (!IsInsideTree()) return;
        if (_heartScene == null) return;
        string[] ids = { "corvan_coeur_1", "corvan_coeur_2" };
        var fallback = new[] { new Vector2(304f, 368f), new Vector2(304f, 528f) };
        for (int i = 0; i < ids.Length; i++)
        {
            var spot = fallback[i];
            if (_room != null && _room.TryGetPoint(ids[i], out var p)) spot = p;
            var heart = _heartScene.Instantiate<Pickup>();
            heart.Lifetime = 25f;
            GetParent().AddChild(heart);
            heart.GlobalPosition = spot;
        }
    }

    // Marqueurs de la carte ; à défaut, les coins de l'arène (ravitaillement) et trois points en haut (Œil).
    private void LoadPoints()
    {
        if (_pointsLoaded) return;
        _pointsLoaded = true;
        for (int i = 1; i <= 3 && _room != null; i++)
        {
            if (!_room.TryGetPoint("morvath_oeil_" + i, out var p)) break;
            _eyeX[_eyeCount] = p.X;
            _eyeY[_eyeCount] = p.Y;
            _eyeCount++;
        }
        if (_eyeCount > 0) return;
        _eyeX[0] = 112f; _eyeY[0] = 144f;
        _eyeX[1] = 528f; _eyeY[1] = 144f;
        _eyeX[2] = 304f; _eyeY[2] = 80f;
        _eyeCount = 3;
    }

    private void SelectSupplyPoints(int kind)
    {
        if (_supplyKind == kind) return;
        _supplyKind = kind;
        _supplyCount = 0;
        string prefix = kind == 0 ? "corvan_fleches_" : "corvan_bombes_";
        for (int i = 1; i <= 2 && _room != null; i++)
        {
            if (!_room.TryGetPoint(prefix + i, out var p)) break;
            _supplyX[_supplyCount] = p.X;
            _supplyY[_supplyCount] = p.Y;
            _supplyCount++;
        }
        if (_supplyCount > 0) return;
        float y = kind == 0 ? 368f : 528f;
        _supplyX[0] = 80f; _supplyY[0] = y;
        _supplyX[1] = 560f; _supplyY[1] = y;
        _supplyCount = 2;
    }

    // --- États, défense, affichage ----------------------------------------------------------------

    private void SetState(State state, float seconds)
    {
        _state = state;
        _timer = seconds;
        _animTime = 0f;
        Velocity = Vector2.Zero;
        ApplyDefence();
        QueueRedraw(); // l'ombre de substitut ne change qu'avec l'état
    }

    // Qui est touchable ? Le corps seulement marteau coincé (phase 1) ou étourdi (phase 2) ; sinon la « Couche » renvoie le coup.
    private void ApplyDefence()
    {
        bool vulnerable = _state == State.Stuck || _state == State.Stunned;
        bool bodyActive = _state != State.Dormant && _state != State.Transition && _state != State.Release
            && _state != State.EyeMove && _state != State.EyeHold && _state != State.Victory;
        _bodyBox.Invincible = !vulnerable;
        _bodyBox.SetDeferred(Area2D.PropertyName.Monitorable, vulnerable);
        // Manche des ronces : un bulbe est au milieu du torse, donc la couche n'intercepte rien (les flèches doivent atteindre les bulbes) ;
        // un coup d'épée sur un bulbe fait un éclat « rien ne passe » (BossBulb est un IMeleeTarget).
        bool thornsOpen = _phase2 && _round == CorvanRules.RoundThorns && !_layerBroken;
        _layerBox.SetDeferred(Area2D.PropertyName.Monitorable, bodyActive && !vulnerable && !thornsOpen && !_layerBroken);

        bool eyeVulnerable = _state == State.EyeHold;
        _eyeBox.Invincible = !eyeVulnerable;
        _eyeBox.SetDeferred(Area2D.PropertyName.Monitorable, eyeVulnerable);
    }

    private void EmitProgress()
    {
        float fraction;
        if (_eyeActive) fraction = CorvanRules.EyeProgress(_eyeHealth.CurrentHealth);
        else if (_phase2) fraction = CorvanRules.Phase2Progress(_round, _health.CurrentHealth);
        else fraction = CorvanRules.Phase1Progress(_health.CurrentHealth);
        if (_state == State.Transition) fraction = 0f;
        EmitSignal(Boss.SignalName.ProgressChanged, fraction);
    }

    private void UpdateIcon()
    {
        bool show = _phase2 && _icon.Texture != null && (
            ((_state == State.RoundIntro || _state == State.RoundIdle || _state == State.RoundWarn || _state == State.RoundAttack) && !_layerBroken)
            || _state == State.Release || _state == State.EyeMove || _state == State.EyeHold);
        _icon.Visible = show;
        if (!show) return;
        // L'icône de l'objet à utiliser flotte au-dessus du boss (la flèche pour l'Œil).
        if (_state == State.Release || _state == State.EyeMove || _state == State.EyeHold)
            _icon.Texture = _icons != null ? _icons[0] : _icon.Texture;
        _icon.Position = new Vector2(0f, -(_bodySize + 18f) + 3f * Mathf.Sin(_animTime * 4f));
        var layerSprite = _layerSprite;
        if (layerSprite.Visible && !_layerBroken && (_state == State.RoundIdle || _state == State.RoundWarn))
            layerSprite.SelfModulate = _layerReal[_round]
                ? new Color(1f, 1f, 1f, 0.75f + 0.25f * Mathf.Sin(_animTime * 8f))
                : new Color(LayerTint[_round].R, LayerTint[_round].G, LayerTint[_round].B, LayerTint[_round].A * (0.75f + 0.25f * Mathf.Sin(_animTime * 8f)));
    }

    // --- Images (réelles si le graphiste les a livrées, sinon substituts) --------------------------

    private void LoadVisuals()
    {
        _frames1 = LoadFrames(FramesDir + "corvan_frames.tres", out _real1) ?? GD.Load<SpriteFrames>("res://art/characters/corvan_frames.tres");
        _frames2 = LoadFrames(FramesDir + "corvan_corrompu_frames.tres", out _real2) ?? GD.Load<SpriteFrames>("res://art/characters/corvan_corrupted_frames.tres");
        string[] layerFiles = { "corvan_corrompu_ronces_liane_frames.tres", "corvan_corrompu_pierre_frames.tres", "corvan_corrompu_eau_frames.tres" };
        for (int i = 0; i < layerFiles.Length; i++)
            _layerFrames[i] = LoadFrames(FramesDir + layerFiles[i], out _layerReal[i]);
        _icons = new Texture2D[3];
        string[] iconFiles = { "conseil_fleche.png", "conseil_bombe.png", "conseil_lanterne.png" };
        string[] items = { GameStateIds.Bow, GameStateIds.Bombs, GameStateIds.Lantern };
        for (int i = 0; i < 3; i++)
        {
            string path = FramesDir + iconFiles[i];
            _icons[i] = ResourceLoader.Exists(path) ? GD.Load<Texture2D>(path) : _gameState.GetItemData(items[i])?.Icon;
        }

        SetBodyFrames(_body, _frames1, _real1, 64f);
        _bodySize = 64f;
        _layerSprite.Visible = false;
        _icon.Visible = false;
        _shadow1 = LoadTexture(FramesDir + "corvan_ombre.png");
        _shadow2 = LoadTexture(FramesDir + "corvan_corrompu_ombre.png");
        _shadow = _visual.GetNodeOrNull<Sprite2D>("Ombre");
        if (_shadow != null)
        {
            _shadow.Texture = _shadow1;
            _shadow.Centered = false;
            _shadow.Offset = new Vector2(-32f, -62f);
        }

        var eyeFrames = LoadFrames(FramesDir + "oeil_frames.tres", out _);
        if (eyeFrames == null)
        {
            eyeFrames = GD.Load<SpriteFrames>("res://art/enemies/oeil_morvath_frames.tres");
            if (eyeFrames != null) _eyeSprite.Scale = Vector2.One * 1.4f;
        }
        if (eyeFrames != null) _eyeSprite.SpriteFrames = eyeFrames;
        _eye.ZIndex = 1;
    }

    private static Texture2D LoadTexture(string path) => ResourceLoader.Exists(path) ? GD.Load<Texture2D>(path) : null;

    private static SpriteFrames LoadFrames(string path, out bool real)
    {
        real = ResourceLoader.Exists(path);
        return real ? GD.Load<SpriteFrames>(path) : null;
    }

    // Place un sprite d'une taille voulue : image réelle (taille native) ou substitut 32x32 agrandi.
    private static void SetBodyFrames(AnimatedSprite2D sprite, SpriteFrames frames, bool real, float size)
    {
        if (frames == null) return;
        sprite.SpriteFrames = frames;
        sprite.Centered = false;
        if (real)
        {
            sprite.Scale = Vector2.One;
            sprite.Offset = new Vector2(-size * 0.5f, size > 64f ? -93f : -62f); // origines indiquées par corvan.json
        }
        else
        {
            sprite.Scale = Vector2.One * (size / 32f);
            sprite.Offset = new Vector2(-16f, -31f);
        }
    }

    private static StringName ResolveAnim(SpriteFrames frames, StringName wanted)
    {
        if (frames == null) return null;
        if (frames.HasAnimation(wanted)) return wanted;
        if (wanted == AnimIdle && frames.HasAnimation(AltIdle)) return AltIdle;
        return null;
    }

    private void PlayBody(StringName anim)
    {
        if (_bodyAnim == anim) return;
        _bodyAnim = anim;
        var name = ResolveAnim(_body.SpriteFrames, anim);
        if (name != null) _body.Play(name);
        if (_layerSprite.Visible && !_layerBroken && _layerSprite.SpriteFrames != null)
        {
            // Le calque suit le corps quand il a la même animation (idle, coup, touche), sinon il reste en idle.
            var layerName = ResolveAnim(_layerSprite.SpriteFrames, anim) ?? ResolveAnim(_layerSprite.SpriteFrames, AnimIdle);
            if (layerName != null) _layerSprite.Play(layerName);
        }
    }

    private void PlayEye(StringName anim)
    {
        if (_eyeSprite.SpriteFrames != null && _eyeSprite.SpriteFrames.HasAnimation(anim)) _eyeSprite.Play(anim);
    }

    private void FlashBody(Color color, float seconds)
    {
        _flash?.Kill();
        _body.Modulate = color;
        _flash = CreateTween();
        _flash.TweenProperty(_body, "modulate", Colors.White, seconds);
    }

    private void FlashEye()
    {
        _eyeSprite.Modulate = new Color(5f, 5f, 5f);
        CreateTween().TweenProperty(_eyeSprite, "modulate", Colors.White, 0.15f);
    }

    // --- Utilitaires ------------------------------------------------------------------------------

    private Vector2 PlayerFeet() => _player.GlobalPosition + Player.FeetOffset;

    private static Vector2 ClampTo(Rect2 rect, Vector2 p) =>
        new(Mathf.Clamp(p.X, rect.Position.X, rect.End.X), Mathf.Clamp(p.Y, rect.Position.Y, rect.End.Y));

    private void FindPlayer()
    {
        if (_player != null && IsInstanceValid(_player)) return;
        _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Player;
        _playerHurt = _player?.GetNodeOrNull<HurtBox>("HurtBox");
    }

    private Room FindRoom()
    {
        for (Node n = GetParent(); n != null; n = n.GetParent())
            if (n is Room room) return room;
        return null;
    }

    private CorvanGroundMark SpawnMark(CorvanGroundMark.Kind kind, Vector2 center, float radius, float seconds, Color? tint = null)
    {
        var mark = new CorvanGroundMark { Name = "Marque" };
        (_room ?? GetParent()).AddChild(mark);
        mark.GlobalPosition = center;
        mark.Begin(kind, radius, seconds, tint);
        PlaceMarkUnderEntities(mark);
        return mark;
    }

    // Posé au sol : juste au-dessus de la carte, sous les personnages (comme les décors de cinématique).
    private void PlaceMarkUnderEntities(Node2D mark)
    {
        var map = _room?.GetNodeOrNull("Map");
        if (map != null && mark.GetParent() == _room) _room.MoveChild(mark, map.GetIndex() + 1);
    }

    private void ShakeCamera(float strength, float seconds)
    {
        if (GetViewport().GetCamera2D() is CameraShake shake)
            shake.Shake(strength, seconds);
    }

    // Ombre ovale sous le boss (substitut tant que l'image n'existe pas).
    public override void _Draw()
    {
        if (!_ready || _state == State.Victory || _shadow1 != null) return;
        DrawColoredPolygon(_phase2 ? ShadowBig : ShadowSmall, ShadowColor);
    }

    private static Vector2[] BuildShadow(float scale)
    {
        var pts = new Vector2[20];
        for (int i = 0; i < pts.Length; i++)
        {
            float a = Mathf.Tau * i / pts.Length;
            pts[i] = new Vector2(Mathf.Cos(a) * 22f * scale, Mathf.Sin(a) * 8f * scale - 2f);
        }
        return pts;
    }
}
