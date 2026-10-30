using System.Collections.Generic;
using Godot;

/// <summary>
/// Gorm, le golem de la Mine (boss du donjon 2). Machine à états à deux phases, composée des composants habituels.
/// Phase 1 « armure » : il marche lentement vers Brann et frappe le sol (tremblement, rochers annoncés par leur ombre,
/// <see cref="FallingRock"/>). L'épée et les flèches rebondissent ; une bombe qui explose à portée (il est
/// <see cref="IBombDestructible"/>) arrache une plaque d'armure (plein, brisé, nu). Si Brann manque de bombes, un paquet apparaît
/// sur un Marqueur « gorm_bombes_N » de la salle. Phase 2 « cristal » : plus d'armure ; après chaque frappe du sol il reste étourdi
/// <see cref="StunSeconds"/> secondes, cristal exposé : l'épée lui fait des dégâts (<see cref="SwordHitsToDefeat"/> coups au total).
/// Récompenses et réplique gérées par la salle (voir <see cref="Boss"/>). Images : art/bosses/gorm/ (voir <see cref="GormFrames"/>).
/// </summary>
public partial class GormBoss : Boss, IBombDestructible
{
    private enum State { Dormant, Intro, Chase, Windup, Slam, Stunned, Hurt, Transition, Recover, Purify, Done }

    [ExportGroup("Début du combat")]
    /// <summary>Distance (px) dont Brann doit s'éloigner de son point d'arrivée pour que le combat commence (la porte se referme).</summary>
    [Export(PropertyHint.Range, "32,300,8")] public float StartDistance { get; set; } = 96f;
    [Export(PropertyHint.Range, "0.2,4,0.1")] public float IntroDuration { get; set; } = 1.4f;

    [ExportGroup("Vie")]
    /// <summary>Coups d'épée (1 PV chacun) pour vaincre Gorm en phase 2. Défaut : 6, comme Sylve.</summary>
    [Export(PropertyHint.Range, "1,20,1")] public int SwordHitsToDefeat { get; set; } = 6;
    /// <summary>Coups qu'un seul étourdissement encaisse au maximum ; au-delà il se relève.</summary>
    [Export(PropertyHint.Range, "1,10,1")] public int HitsPerStun { get; set; } = 3;
    /// <summary>Durée (s) de l'étourdissement, multipliée par l'option d'aide GameState.PuzzleTimeMultiplier.</summary>
    [Export(PropertyHint.Range, "1,10,0.5")] public float StunSeconds { get; set; } = 4f;
    [Export(PropertyHint.Range, "0.2,3,0.1")] public float HurtSeconds { get; set; } = 0.8f;
    [Export(PropertyHint.Range, "0.2,3,0.1")] public float RecoverSeconds { get; set; } = 0.7f;
    [Export(PropertyHint.Range, "0.5,4,0.1")] public float TransitionSeconds { get; set; } = 1.6f;
    /// <summary>Délai (s) de grâce, sans contact dangereux, quand il se relève.</summary>
    [Export(PropertyHint.Range, "0,1,0.05")] public float GraceSeconds { get; set; } = 0.4f;

    [ExportGroup("Déplacement")]
    [Export(PropertyHint.Range, "0,100,1")] public float ChaseSpeed1 { get; set; } = 26f;
    [Export(PropertyHint.Range, "0,100,1")] public float ChaseSpeed2 { get; set; } = 34f;

    [ExportGroup("Frappe du sol")]
    /// <summary>Intervalle (s) entre deux frappes en phase 1 (mesuré depuis la fin de la précédente).</summary>
    [Export(PropertyHint.Range, "1,15,0.5")] public float StrikeInterval1 { get; set; } = 5f;
    [Export(PropertyHint.Range, "1,15,0.5")] public float StrikeInterval2 { get; set; } = 3f;
    /// <summary>Préparation (s) : Gorm lève les bras avant le coup.</summary>
    [Export(PropertyHint.Range, "0.3,3,0.1")] public float WindupSeconds { get; set; } = 1.0f;
    /// <summary>Durée (s) du bras posé au sol après le coup (en phase 2 il enchaîne sur l'étourdissement).</summary>
    [Export(PropertyHint.Range, "0.1,2,0.1")] public float SlamSeconds { get; set; } = 0.6f;
    /// <summary>Rochers par frappe (un tombe sur Brann, les autres autour).</summary>
    [Export(PropertyHint.Range, "1,10,1")] public int RocksPhase1 { get; set; } = 3;
    [Export(PropertyHint.Range, "1,10,1")] public int RocksPhase2 { get; set; } = 5;
    /// <summary>Distance maximale (px) des rochers supplémentaires autour de Brann.</summary>
    [Export(PropertyHint.Range, "32,240,8")] public float RockSpread { get; set; } = 120f;
    /// <summary>Durée (s) d'avertissement de l'ombre d'un rocher.</summary>
    [Export(PropertyHint.Range, "0.4,3,0.05")] public float RockWarnSeconds { get; set; } = 1.0f;

    /// <summary>Écart minimal (px) entre deux rochers d'une même frappe.</summary>
    [Export(PropertyHint.Range, "16,96,2")] public float RockMinGap { get; set; } = 36f;
    /// <summary>Délai minimal (s) entre deux rappels de conseil quand Brann tape l'armure.</summary>
    [Export(PropertyHint.Range, "2,30,1")] public float HintCooldownSeconds { get; set; } = 8f;

    [ExportGroup("Ravitaillement en bombes")]
    /// <summary>Brann reçoit un paquet de bombes quand il en a moins que cela (et qu'il reste une plaque).</summary>
    [Export(PropertyHint.Range, "1,10,1")] public int BombSupplyBelow { get; set; } = 2;
    /// <summary>Délai (s) avant l'apparition du paquet.</summary>
    [Export(PropertyHint.Range, "1,20,0.5")] public float BombPackDelay { get; set; } = 3f;
    [Export(PropertyHint.Range, "5,60,1")] public float BombPackLifetime { get; set; } = 30f;
    /// <summary>Nombre de Marqueurs « gorm_bombes_N » à lire dans la carte (N = 1 à ce nombre).</summary>
    [Export(PropertyHint.Range, "1,8,1")] public int SupplyPointCount { get; set; } = 4;
    /// <summary>Le paquet n'apparaît pas à moins de cette distance (px) de Gorm.</summary>
    [Export(PropertyHint.Range, "32,300,8")] public float BombPackMinDistance { get; set; } = 110f;

    [ExportGroup("Contact")]
    [Export(PropertyHint.Range, "0.2,2,0.1")] public float ContactPulse { get; set; } = 0.5f;

    [ExportGroup("Victoire")]
    [Export(PropertyHint.Range, "1,8,0.5")] public float PurifySeconds { get; set; } = 3f;
    [Export(PropertyHint.Range, "1,15,0.5")] public float LingerSeconds { get; set; } = 7f;

    [ExportGroup("Images")]
    [Export(PropertyHint.File, "*.png")] public string ShadowPath { get; set; } = "res://art/bosses/gorm/gorm_ombre.png";

    /// <summary>Phase en cours (1 ou 2 ; 0 avant le combat).</summary>
    public int Phase => _state == State.Dormant ? 0 : _phase2 ? 2 : 1;
    public string StateName => _state.ToString();
    public int PlatesLeft => GormRules.PlatesLeft(_armor);
    public bool IsStunned => _state == State.Stunned;
    public bool IsDefeated => _state == State.Purify || _state == State.Done;
    public int SwordHitsLeft => _health?.CurrentHealth ?? SwordHitsToDefeat;
    /// <summary>Rochers en cours de chute (tests et débogage).</summary>
    public int RocksActive => _rocks.Count;

    public Vector2 BombHalfExtents => new(30f, 36f);

    private static readonly StringName PlayerGroup = "player";
    private static readonly Vector2 VisualPos = new(0f, 28f);
    private static readonly Color StarColor = new(1f, 0.92f, 0.3f);
    private const int MaxSupplyPoints = 8;

    private readonly RandomNumberGenerator _rng = new();
    private readonly List<FallingRock> _rocks = new();
    private readonly float[] _supplyX = new float[MaxSupplyPoints];
    private readonly float[] _supplyY = new float[MaxSupplyPoints];
    private int _supplyCount;
    private bool _supplyLoaded;

    private State _state = State.Dormant;
    private bool _phase2;
    private int _armor;
    private float _timer;
    private float _animTime;
    private float _strikeTimer;
    private float _pulseTimer;
    private bool _pulseOff;
    private bool _contactOn;
    private float _grace;
    private int _hitsThisStun;
    private bool _ended;
    private bool _ready;
    private bool _moving;
    private bool _hasArrival;
    private Vector2 _arrival;
    private float _hintCooldown;
    private float _bombBlockGrace;
    private float _bombTimer;
    private Node _bombPack;
    private PackedScene _bombPackScene;
    private PackedScene _rockScene;
    private int _lastCell = -1;
    private Vector2 _sparkPos;
    private float _sparkTime;
    private Vector2[] _placedRocks;

    private Node2D _visual;
    private Sprite2D _shadow;
    private Sprite2D _body;
    private Sprite2D _corruption;
    private Health _health;
    private HurtBox _armorBox;
    private HurtBox _crystalBox;
    private HitBox _hitBox;
    private Player _player;
    private HurtBox _playerHurt;
    private GameState _gameState;
    private Tween _flash;
    private Tween _blink;

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

        _visual = GetNode<Node2D>("Visuel");
        _shadow = _visual.GetNode<Sprite2D>("Ombre");
        _body = _visual.GetNode<Sprite2D>("Corps");
        _corruption = _visual.GetNode<Sprite2D>("Corruption");
        _visual.Position = VisualPos;

        _health = GetNode<Health>("Health");
        _health.SetValues(SwordHitsToDefeat, SwordHitsToDefeat);
        _health.Died += OnDied;
        _armorBox = GetNode<HurtBox>("Armure");
        _armorBox.Invincible = true; // toujours : l'épée et les flèches rebondissent sur l'armure et sur le corps de pierre
        _armorBox.Blocked += OnBlocked;
        _crystalBox = GetNode<HurtBox>("Cristal");
        _crystalBox.Hit += OnHit;
        _hitBox = GetNode<HitBox>("HitBox");

        _rockScene = GD.Load<PackedScene>("res://scenes/enemies/boss/rocher_chute.tscn");
        _bombPackScene = GD.Load<PackedScene>("res://scenes/items/bombes_paquet.tscn");
        var shadowTexture = ResourceLoader.Exists(ShadowPath) ? GD.Load<Texture2D>(ShadowPath) : null;
        if (shadowTexture != null) _shadow.Texture = shadowTexture;
        if (ArenaBounds.Size == Vector2.Zero)
            ArenaBounds = new Rect2(58f, 58f, 524f, 588f);
        _placedRocks = new Vector2[Mathf.Max(RocksPhase1, RocksPhase2)];

        _ready = true;
        SetState(State.Dormant, 0f);
        ApplyPose(GormFrames.Idle, true);
        StartBlink();
    }

    public override void _ExitTree()
    {
        Bomb.Unregister(this);
        if (!_ready) return;
        ClearRocks();
        FreeBombPack();
        if (_health != null) _health.Died -= OnDied;
        if (_armorBox != null) _armorBox.Blocked -= OnBlocked;
        if (_crystalBox != null) _crystalBox.Hit -= OnHit;
    }

    // --- Boucle ---------------------------------------------------------------------------------

    public override void _PhysicsProcess(double delta)
    {
        if (!_ready || _state == State.Done) return;
        float dt = (float)delta;
        _animTime += dt;
        if (_hintCooldown > 0f) _hintCooldown -= dt;
        if (_bombBlockGrace > 0f) _bombBlockGrace -= dt;
        if (_sparkTime > 0f)
        {
            _sparkTime -= dt;
            QueueRedraw();
        }
        FindPlayer();

        if (_player != null && _player.IsDead && _state != State.Purify)
        {
            // Brann est tombé : Gorm se calme en attendant le rechargement de la salle.
            if (_contactOn) SetContact(false);
            if (!_ended && _state != State.Dormant)
            {
                _ended = true;
                EmitSignal(Boss.SignalName.EncounterEnded);
            }
            ApplyPose(GormFrames.Idle, true);
            return;
        }

        UpdateContactPulse(dt);
        _timer -= dt;
        if (_state != State.Dormant && _state != State.Purify) UpdateBombSupply(dt);

        switch (_state)
        {
            case State.Dormant: UpdateDormant(); break;
            case State.Intro: UpdateIntro(); break;
            case State.Chase: UpdateChase(dt); break;
            case State.Windup: UpdateWindup(); break;
            case State.Slam: UpdateSlam(); break;
            case State.Stunned: UpdateStunned(); break;
            case State.Hurt: UpdateHurt(); break;
            case State.Transition: UpdateTransition(); break;
            case State.Recover: UpdateRecover(dt); break;
            case State.Purify: UpdatePurify(); break;
        }
    }

    private void UpdateDormant()
    {
        ApplyPose(GormFrames.Idle, true);
        if (_player == null) return;
        if (!_hasArrival)
        {
            _arrival = EntryPoint ?? _player.GlobalPosition;
            _hasArrival = true;
            return;
        }
        if (_player.GlobalPosition.DistanceSquaredTo(_arrival) >= StartDistance * StartDistance)
            StartEncounter();
    }

    private void StartEncounter()
    {
        foreach (var door in ArenaDoors)
            if (IsInstanceValid(door)) door.LockForEncounter();
        AddCollisionExceptionWith(_player); // Gorm traverse Brann (le contact le blesse) : il ne s'arrête que sur les murs et les piliers
        EmitSignal(Boss.SignalName.EncounterStarted);
        AudioManager.Play(Sfx.BossRugit);
        EmitSignal(Boss.SignalName.HintRequested, "BOSS_GORM_CONSEIL_1", 7f);
        EmitProgress();
        ShakeCamera(3f, 0.8f);
        SetState(State.Intro, IntroDuration);
    }

    private void UpdateIntro()
    {
        ApplyPose(GormFrames.RaiseHigh, false);
        ShakeVisual(1.5f);
        if (_timer <= 0f) BeginChase();
    }

    private void BeginChase()
    {
        _strikeTimer = _phase2 ? StrikeInterval2 : StrikeInterval1;
        SetState(State.Chase, 0f);
    }

    private void UpdateChase(float dt)
    {
        _strikeTimer -= dt;
        _moving = false;
        if (_player != null)
        {
            var to = _player.GlobalPosition + Player.FeetOffset - GlobalPosition;
            if (to.LengthSquared() > 20f * 20f)
            {
                _moving = true;
                Velocity = to.Normalized() * (_phase2 ? ChaseSpeed2 : ChaseSpeed1);
                MoveAndSlide();
            }
        }
        ApplyPose(_moving ? GormFrames.Walk : GormFrames.Idle, true);
        if (_strikeTimer <= 0f) SetState(State.Windup, WindupSeconds);
    }

    private void UpdateWindup()
    {
        bool high = (WindupSeconds - _timer) > WindupSeconds * 0.4f;
        ApplyPose(high ? GormFrames.RaiseHigh : GormFrames.RaiseLow, false);
        ShakeVisual(high ? 2f : 1f);
        if (_timer > 0f) return;
        _visual.Position = VisualPos;
        Strike();
        SetState(State.Slam, SlamSeconds);
    }

    // Le coup : tremblement, bruit, et les rochers dont l'ombre prévient.
    private void Strike()
    {
        AudioManager.PlayAt(Sfx.Eboulement, GlobalPosition);
        ShakeCamera(_phase2 ? 5f : 4f, 0.6f);
        SpawnRocks(_phase2 ? RocksPhase2 : RocksPhase1);
    }

    private void UpdateSlam()
    {
        ApplyPose(_animTime < 0.2f ? GormFrames.Slam : GormFrames.SlamEnd, false);
        if (_timer > 0f) return;
        if (_phase2) BeginStun();
        else Recover(RecoverSeconds, true);
    }

    private void BeginStun()
    {
        _hitsThisStun = 0;
        AudioManager.PlayAt(Sfx.BossAssomme, GlobalPosition);
        SetState(State.Stunned, BossRules.StunDuration(StunSeconds, _gameState.PuzzleTimeMultiplier));
    }

    private void UpdateStunned()
    {
        ApplyPose(GormFrames.Stunned, true);
        QueueRedraw(); // étoiles
        if (_timer <= 0f) Recover(RecoverSeconds, true);
    }

    private void UpdateHurt()
    {
        ApplyPose(GormFrames.Hurt, false);
        if (_timer > 0f) return;
        if (GormRules.PlatesLeft(_armor) == 0 && !_phase2) BeginTransition();
        else Recover(RecoverSeconds, true);
    }

    private void BeginTransition()
    {
        ClearRocks();
        ShakeCamera(4f, 0.8f);
        SetState(State.Transition, TransitionSeconds);
    }

    private void UpdateTransition()
    {
        ApplyPose(GormFrames.Hurt, false);
        ShakeVisual(2f);
        if (_timer > 0f) return;
        _visual.Position = VisualPos;
        _phase2 = true;
        EmitSignal(Boss.SignalName.HintRequested, "BOSS_GORM_CONSEIL_3", 8f);
        Recover(RecoverSeconds + 0.5f, true);
    }

    private void Recover(float seconds, bool withGrace)
    {
        _grace = withGrace ? GraceSeconds : 0f;
        SetState(State.Recover, seconds);
    }

    private void UpdateRecover(float dt)
    {
        ApplyPose(GormFrames.Idle, true);
        if (_grace > 0f)
        {
            _grace -= dt;
            if (_grace <= 0f) SetContact(true);
        }
        if (_timer <= 0f) BeginChase();
    }

    private void UpdatePurify()
    {
        ApplyPose(GormFrames.Death, false);
        if (_timer <= 0f) FinishVictory();
    }

    // --- Changements d'état ---------------------------------------------------------------------

    private void SetState(State state, float seconds)
    {
        if (state != State.Recover) _grace = 0f;
        bool redraw = _state == State.Stunned || state == State.Stunned;
        _state = state;
        _timer = seconds;
        _animTime = 0f;
        _lastCell = -1;
        _pulseTimer = ContactPulse;
        Velocity = Vector2.Zero;
        if (redraw) QueueRedraw();
        if (state != State.Windup && state != State.Intro && state != State.Transition) _visual.Position = VisualPos;
        ApplyDefence();
    }

    // Quand est-il vulnérable, touchable, dangereux ? Tout se décide ici, à chaque changement d'état.
    private void ApplyDefence()
    {
        bool alive = _state != State.Dormant && _state != State.Purify && _state != State.Done;
        _armorBox.SetDeferred(Area2D.PropertyName.Monitorable, alive);
        // Le cristal n'est touchable que pendant l'étourdissement de la phase 2.
        bool exposed = _state == State.Stunned && _phase2;
        _crystalBox.Invincible = !exposed;
        _crystalBox.SetDeferred(Area2D.PropertyName.Monitorable, exposed);

        bool dangerous = _state == State.Chase || _state == State.Windup || _state == State.Slam
            || (_state == State.Recover && _grace <= 0f);
        SetContact(dangerous);
    }

    private void SetContact(bool on)
    {
        _contactOn = on;
        _pulseOff = false;
        _hitBox.SetDeferred(Area2D.PropertyName.Monitoring, on);
    }

    // Tant que Brann reste dans Gorm et n'est pas protégé, le contact est réarmé régulièrement (une Area2D ne signale qu'une entrée).
    private void UpdateContactPulse(float dt)
    {
        if (!_contactOn) return;
        if (_pulseOff)
        {
            _hitBox.Monitoring = true;
            _pulseOff = false;
            return;
        }
        _pulseTimer -= dt;
        if (_pulseTimer > 0f) return;
        _pulseTimer = ContactPulse;
        if (_playerHurt != null && IsInstanceValid(_playerHurt) && !_playerHurt.Invincible)
        {
            _hitBox.Monitoring = false;
            _pulseOff = true;
        }
    }

    private void FindPlayer()
    {
        if (_player != null && IsInstanceValid(_player)) return;
        _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Player;
        _playerHurt = _player?.GetNodeOrNull<HurtBox>("HurtBox");
    }

    // --- Bombes : plaques d'armure et ravitaillement --------------------------------------------

    /// <summary>Une bombe explose à portée : arrache une plaque d'armure (phase 1 seulement, jamais pendant un coup encaissé).</summary>
    public void OnBombExplosion(Vector2 center)
    {
        if (!_ready || _phase2 || IsDefeated) return;
        if (_state == State.Dormant || _state == State.Intro || _state == State.Hurt || _state == State.Transition) return;
        _bombBlockGrace = 0.5f; // le souffle frappe aussi la zone invincible : pas d'éclat bleu « rien ne passe » en plus
        _armor = GormRules.NextArmor(_armor);
        _lastCell = -1;
        FlashVisual(new Color(4f, 4f, 4f), 0.2f);
        ShakeCamera(4f, 0.4f);
        AudioManager.PlayAt(Sfx.BossAssomme, GlobalPosition);
        EmitProgress();
        SetState(State.Hurt, HurtSeconds);
    }

    // Brann ne reste jamais coincé : s'il a les bombes mais en manque pour les plaques restantes, un paquet apparaît sur un Marqueur libre.
    private void UpdateBombSupply(float dt)
    {
        if (_phase2 || _state == State.Intro) return;
        bool packExists = _bombPack != null && IsInstanceValid(_bombPack) && !_bombPack.IsQueuedForDeletion();
        bool needed = GormRules.NeedsBombSupply(_gameState.HasItem(GameState.BombItemId), _gameState.GetQuantity(GameState.BombItemId),
            GormRules.PlatesLeft(_armor), BombSupplyBelow, packExists);
        if (!needed)
        {
            _bombTimer = BombPackDelay;
            return;
        }
        _bombTimer -= dt;
        if (_bombTimer > 0f || _bombPackScene == null) return;
        _bombTimer = BombPackDelay;
        LoadSupplyPoints();
        var from = _player != null ? _player.GlobalPosition : GlobalPosition;
        int i = GormRules.PickSupplyPoint(_supplyX, _supplyY, _supplyCount, GlobalPosition.X, GlobalPosition.Y, from.X, from.Y, BombPackMinDistance);
        if (i < 0) return;
        var pack = _bombPackScene.Instantiate<Pickup>();
        pack.Lifetime = BombPackLifetime;
        GetParent().AddChild(pack); // le Pickup épingle son effet (ResourceKeeper.Pin) dans son _Ready
        pack.GlobalPosition = new Vector2(_supplyX[i], _supplyY[i]);
        _bombPack = pack;
    }

    // Marqueurs « gorm_bombes_1 » à « _N » de la carte (Room.TryGetPoint) ; à défaut, les quatre coins de l'arène.
    private void LoadSupplyPoints()
    {
        if (_supplyLoaded) return;
        _supplyLoaded = true;
        Room room = null;
        for (Node n = GetParent(); n != null && room == null; n = n.GetParent()) room = n as Room;
        for (int i = 1; i <= SupplyPointCount && i <= MaxSupplyPoints && room != null; i++)
        {
            if (!room.TryGetPoint("gorm_bombes_" + i, out var p)) break;
            _supplyX[_supplyCount] = p.X;
            _supplyY[_supplyCount] = p.Y;
            _supplyCount++;
        }
        if (_supplyCount > 0) return;
        AddSupplyPoint(ArenaBounds.Position + new Vector2(8f, 8f));
        AddSupplyPoint(new Vector2(ArenaBounds.End.X - 8f, ArenaBounds.Position.Y + 8f));
        AddSupplyPoint(new Vector2(ArenaBounds.Position.X + 8f, ArenaBounds.End.Y - 8f));
        AddSupplyPoint(ArenaBounds.End - new Vector2(8f, 8f));
    }

    private void AddSupplyPoint(Vector2 p)
    {
        _supplyX[_supplyCount] = p.X;
        _supplyY[_supplyCount] = p.Y;
        _supplyCount++;
    }

    // --- Rochers --------------------------------------------------------------------------------

    private void SpawnRocks(int count)
    {
        if (_player == null || _rockScene == null) return;
        PruneRocks();
        if (count > _placedRocks.Length) count = _placedRocks.Length;
        var target = _player.GlobalPosition + Player.FeetOffset;
        _placedRocks[0] = target;
        PlaceRock(target); // le premier tombe exactement sur Brann : il doit bouger
        int n = 1;
        for (int i = 1; i < count; i++)
        {
            for (int attempt = 0; attempt < 8; attempt++)
            {
                var pos = target + Vector2.Right.Rotated(_rng.RandfRange(0f, Mathf.Tau)) * _rng.RandfRange(40f, RockSpread);
                pos = new Vector2(
                    Mathf.Clamp(pos.X, ArenaBounds.Position.X, ArenaBounds.End.X),
                    Mathf.Clamp(pos.Y, ArenaBounds.Position.Y, ArenaBounds.End.Y));
                if (!IsFreeRockSpot(pos, n)) continue;
                _placedRocks[n++] = pos;
                PlaceRock(pos);
                break;
            }
        }
    }

    private bool IsFreeRockSpot(Vector2 pos, int placedCount)
    {
        for (int i = 0; i < Pillars.Count; i++)
        {
            var r = Pillars[i];
            if (BossRules.IsInsideRect(pos.X, pos.Y, r.Position.X, r.Position.Y, r.Size.X, r.Size.Y, 16f)) return false;
        }
        for (int i = 0; i < placedCount; i++)
            if (pos.DistanceSquaredTo(_placedRocks[i]) < RockMinGap * RockMinGap) return false;
        return true;
    }

    private void PlaceRock(Vector2 impact)
    {
        var rock = _rockScene.Instantiate<FallingRock>();
        rock.WarnDuration = RockWarnSeconds;
        GetParent().AddChild(rock);
        rock.GlobalPosition = impact - new Vector2(0f, FallingRock.SortOffset);
        _rocks.Add(rock);
    }

    private void PruneRocks()
    {
        for (int i = _rocks.Count - 1; i >= 0; i--)
            if (!IsInstanceValid(_rocks[i]) || _rocks[i].IsQueuedForDeletion()) _rocks.RemoveAt(i);
    }

    private void ClearRocks()
    {
        foreach (var rock in _rocks)
            if (IsInstanceValid(rock)) rock.QueueFree();
        _rocks.Clear();
    }

    // --- Coups reçus ----------------------------------------------------------------------------

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_state != State.Stunned) return; // vaincu ou autre : Died s'en occupe
        _hitsThisStun += Mathf.Max(1, damage);
        FlashVisual(new Color(4f, 4f, 4f), 0.12f);
        EmitProgress();
        if (_health.CurrentHealth > 0 && _hitsThisStun >= HitsPerStun)
            SetState(State.Hurt, HurtSeconds);
    }

    // Armure et corps de pierre : un éclat bleu montre que le coup n'a rien fait ; un conseil rappelle (sans spammer) qu'il faut une bombe.
    private void OnBlocked(int damage, Vector2 fromPosition)
    {
        if (_phase2 || _state == State.Stunned || _state == State.Hurt || _bombBlockGrace > 0f) return;
        FlashVisual(new Color(0.3f, 0.6f, 3f), 0.3f);
        AudioManager.PlayAt(Sfx.FlecheImpact, fromPosition);
        _sparkPos = ToLocal(fromPosition);
        _sparkTime = 0.25f;
        QueueRedraw();
        if (_hintCooldown <= 0f && !_phase2 && _state != State.Dormant)
        {
            _hintCooldown = HintCooldownSeconds;
            EmitSignal(Boss.SignalName.HintRequested, "BOSS_GORM_CONSEIL_2", 6f);
        }
    }

    private void OnDied()
    {
        // Health.Damage émet Died avant que la HurtBox émette Hit : OnHit trouvera l'état « purification » et ne fera rien.
        EmitProgress();
        BeginPurify();
    }

    // --- Victoire -------------------------------------------------------------------------------

    private void FreeBombPack()
    {
        if (_bombPack != null && IsInstanceValid(_bombPack)) _bombPack.QueueFree();
        _bombPack = null;
    }

    private void BeginPurify()
    {
        ClearRocks();
        FreeBombPack();
        _blink?.Kill();
        _armor = GormRules.PlateCount;
        _lastCell = -1;
        SetState(State.Purify, PurifySeconds);
        AudioManager.Play(Sfx.BossVaincu);
        ShakeCamera(4f, 0.8f);
        FlashVisual(new Color(3f, 3f, 2.2f), 0.5f);
        var fade = CreateTween();
        fade.TweenProperty(_corruption, "modulate:a", 0f, PurifySeconds * 0.7f);
    }

    private void FinishVictory()
    {
        _state = State.Done;
        _gameState.MarkCollected(BossId);
        foreach (var door in ArenaDoors)
            if (IsInstanceValid(door)) door.UnlockAfterEncounter();
        _gameState.NotifyBossDefeated(BossId); // sauvegarde automatique
        EmitSignal(Boss.SignalName.EncounterEnded);
        EmitSignal(Boss.SignalName.Defeated);

        var tween = CreateTween();
        tween.TweenInterval(LingerSeconds);
        tween.TweenProperty(_visual, "modulate:a", 0f, 1.5f);
        tween.TweenCallback(Callable.From(QueueFree));
    }

    // --- Affichage ------------------------------------------------------------------------------

    // Case de la planche : ligne = armure, colonne = animation. Les deux calques (corps, corruption) ont les mêmes cases.
    private void ApplyPose(GormFrames.Clip clip, bool loop)
    {
        int cell = GormRules.FrameIndex(_armor, clip.ColumnAt(_animTime, loop));
        if (cell == _lastCell) return;
        _lastCell = cell;
        _body.Frame = cell;
        _corruption.Frame = cell;
    }

    // La corruption clignote (calque séparé) tant que Gorm n'est pas purifié.
    private void StartBlink()
    {
        _blink?.Kill();
        _blink = CreateTween().SetLoops();
        _blink.TweenProperty(_corruption, "modulate:a", 0.55f, 0.5f);
        _blink.TweenProperty(_corruption, "modulate:a", 1f, 0.5f);
    }

    private void FlashVisual(Color color, float seconds)
    {
        _flash?.Kill();
        _body.Modulate = color;
        _flash = CreateTween();
        _flash.TweenProperty(_body, "modulate", Colors.White, seconds);
    }

    private void ShakeVisual(float amount)
    {
        _visual.Position = VisualPos + new Vector2(_rng.RandfRange(-amount, amount), 0f);
    }

    private void ShakeCamera(float strength, float seconds)
    {
        if (GetViewport().GetCamera2D() is CameraShake shake)
            shake.Shake(strength, seconds);
    }

    private void EmitProgress()
    {
        EmitSignal(Boss.SignalName.ProgressChanged,
            GormRules.Progress(GormRules.PlatesLeft(_armor), _health.CurrentHealth, SwordHitsToDefeat));
    }

    // Étincelles du coup bloqué et étoiles de l'étourdissement.
    public override void _Draw()
    {
        if (_sparkTime > 0f)
        {
            float k = _sparkTime / 0.25f;
            for (int i = 0; i < 6; i++)
            {
                var d = Vector2.Right.Rotated(i * Mathf.Tau / 6f + 0.3f);
                DrawLine(_sparkPos + d * (4f + 10f * (1f - k)), _sparkPos + d * (10f + 14f * (1f - k)), new Color(0.8f, 0.9f, 1f, k), 2f);
            }
        }
        if (_state == State.Stunned)
        {
            for (int i = 0; i < 3; i++)
            {
                float a = _animTime * 4f + i * Mathf.Tau / 3f;
                DrawCircle(new Vector2(Mathf.Cos(a) * 24f, -52f + Mathf.Sin(a) * 6f), 3f, StarColor);
            }
        }
    }
}
