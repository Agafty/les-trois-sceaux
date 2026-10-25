using Godot;

/// <summary>
/// Sylve, le Cerf des Racines (boss du Temple des Racines). Machine à états à deux phases, composée des composants habituels
/// (Health = coups d'épée restants, HurtBox, HitBox de contact) et de trois <see cref="BossBulb"/> sur ses bois.
/// Phase 1 : il patrouille au fond de l'arène et lance des ronces télégraphiées (<see cref="ThornEruption"/>). Il est invulnérable ;
/// les trois bulbes se détruisent à la flèche. Phase 2 : il charge en ligne droite vers Brann après une préparation visible ;
/// contre un pilier il est assommé et vulnérable à l'épée, contre un mur il s'arrête simplement. Après
/// <see cref="SwordHitsToDefeat"/> coups d'épée cumulés il est purifié (récompenses et réplique gérées par la salle).
/// L'ombre, le corps et le calque de corruption viennent de art/bosses/sylve/ (voir <see cref="SylveFrames"/>).
/// </summary>
public partial class SylveBoss : Boss
{
    private enum State { Dormant, Intro, Patrol, Cast, Transition, Recover, Reposition, Windup, Charge, Stunned, Hurt, Purify, Done }

    [ExportGroup("Début du combat")]
    /// <summary>Distance (px) dont Brann doit s'éloigner de son point d'arrivée pour que le combat commence (la porte se referme).</summary>
    [Export(PropertyHint.Range, "32,300,8")] public float StartDistance { get; set; } = 96f;
    [Export(PropertyHint.Range, "0.2,4,0.1")] public float IntroDuration { get; set; } = 1.2f;

    [ExportGroup("Vie")]
    /// <summary>Coups d'épée cumulés pour le vaincre (1 PV par coup). Défaut : 6 coups, soit au moins 2 assommements (3 coups au plus par assommement).</summary>
    [Export(PropertyHint.Range, "1,20,1")] public int SwordHitsToDefeat { get; set; } = 6;
    /// <summary>Coups qu'un seul assommement encaisse au maximum ; au-delà il se relève.</summary>
    [Export(PropertyHint.Range, "1,10,1")] public int HitsPerStun { get; set; } = 3;
    /// <summary>Durée (s) de l'assommement, multipliée par l'option d'aide GameState.PuzzleTimeMultiplier.</summary>
    [Export(PropertyHint.Range, "1,10,0.5")] public float StunSeconds { get; set; } = 3f;
    [Export(PropertyHint.Range, "0.2,3,0.1")] public float HurtSeconds { get; set; } = 0.8f;

    [ExportGroup("Phase 1 : ronces")]
    [Export(PropertyHint.Range, "0,100,1")] public float PatrolSpeed { get; set; } = 26f;
    [Export(PropertyHint.Range, "0,300,8")] public float PatrolHalfWidth { get; set; } = 140f;
    [Export(PropertyHint.Range, "1,10,0.5")] public float ThornInterval { get; set; } = 4f;
    [Export(PropertyHint.Range, "0.2,3,0.1")] public float CastSeconds { get; set; } = 0.9f;
    [Export(PropertyHint.Range, "1,4,1")] public int ThornCount { get; set; } = 2;
    /// <summary>Écart (px) des ronces supplémentaires autour de celle posée sur Brann.</summary>
    [Export(PropertyHint.Range, "16,120,4")] public float ThornSpread { get; set; } = 56f;

    /// <summary>Délai (s) avant qu'un paquet de flèches apparaisse quand Brann en manque (jamais coincé sans munitions).</summary>
    [Export(PropertyHint.Range, "2,20,0.5")] public float ArrowPackDelay { get; set; } = 6f;
    /// <summary>Brann reçoit un paquet tant qu'il a moins de (bulbes restants + cette marge) flèches.</summary>
    [Export(PropertyHint.Range, "0,6,1")] public int ArrowMargin { get; set; } = 2;
    /// <summary>Durée (s) pendant laquelle le paquet reste au sol.</summary>
    [Export(PropertyHint.Range, "4,30,1")] public float ArrowPackLifetime { get; set; } = 14f;

    [ExportGroup("Phase 2 : charges")]
    [Export(PropertyHint.Range, "0.3,3,0.1")] public float WindupSeconds { get; set; } = 1.0f;
    /// <summary>Part de la préparation pendant laquelle il suit encore Brann ; ensuite la direction est verrouillée.</summary>
    [Export(PropertyHint.Range, "0,1,0.05")] public float AimTrackFraction { get; set; } = 0.6f;
    [Export(PropertyHint.Range, "50,500,10")] public float ChargeSpeed { get; set; } = 230f;
    [Export(PropertyHint.Range, "100,1000,10")] public float ChargeMaxDistance { get; set; } = 560f;
    [Export(PropertyHint.Range, "0.2,4,0.1")] public float RecoverSeconds { get; set; } = 1.0f;
    /// <summary>Pause (s) après un choc contre un mur.</summary>
    [Export(PropertyHint.Range, "0.2,4,0.1")] public float WallBumpSeconds { get; set; } = 0.8f;
    [Export(PropertyHint.Range, "0.5,4,0.1")] public float TransitionSeconds { get; set; } = 1.6f;
    /// <summary>Marge (px) autour d'un pilier dans laquelle un choc compte comme « contre le pilier ».</summary>
    [Export(PropertyHint.Range, "0,24,1")] public float PillarMargin { get; set; } = 8f;

    /// <summary>Distance (px) à parcourir pour qu'un choc compte : en dessous, il était déjà collé à l'obstacle (pas d'assommement).</summary>
    [Export(PropertyHint.Range, "0,32,1")] public float MinChargeToStun { get; set; } = 6f;
    /// <summary>Durée (s) du pas de côté quand Sylve est collé à un obstacle sur la ligne de sa charge.</summary>
    [Export(PropertyHint.Range, "0.2,2,0.1")] public float RepositionSeconds { get; set; } = 0.7f;
    [Export(PropertyHint.Range, "0,200,5")] public float RepositionSpeed { get; set; } = 110f;
    /// <summary>Délai (s) de grâce, sans contact dangereux, quand il se relève d'un assommement ou d'un coup.</summary>
    [Export(PropertyHint.Range, "0,1,0.05")] public float GraceSeconds { get; set; } = 0.3f;

    [ExportGroup("Contact")]
    /// <summary>Intervalle (s) auquel le contact est réarmé tant que Brann reste dans Sylve et n'est pas protégé.</summary>
    [Export(PropertyHint.Range, "0.2,2,0.1")] public float ContactPulse { get; set; } = 0.5f;

    [ExportGroup("Victoire")]
    [Export(PropertyHint.Range, "1,8,0.5")] public float PurifySeconds { get; set; } = 3f;
    /// <summary>Délai (s) après la victoire avant que Sylve se fonde dans la lumière.</summary>
    [Export(PropertyHint.Range, "1,15,0.5")] public float LingerSeconds { get; set; } = 7f;

    [ExportGroup("Images")]
    [Export(PropertyHint.File, "*.png")] public string BodyPath { get; set; } = "res://art/bosses/sylve/sylve.png";
    [Export(PropertyHint.File, "*.png")] public string ThornsPath { get; set; } = "res://art/bosses/sylve/sylve_ronces.png";
    [Export(PropertyHint.File, "*.png")] public string SideBodyPath { get; set; } = "res://art/bosses/sylve/sylve_cote.png";
    [Export(PropertyHint.File, "*.png")] public string SideThornsPath { get; set; } = "res://art/bosses/sylve/sylve_cote_ronces.png";
    [Export(PropertyHint.File, "*.png")] public string ShadowPath { get; set; } = "res://art/bosses/sylve/sylve_ombre.png";

    /// <summary>Phase en cours (1 ou 2 ; 0 avant le combat).</summary>
    public int Phase => _state == State.Dormant ? 0 : _phase2 ? 2 : 1;

    /// <summary>Nom lisible de l'état courant (tests et débogage).</summary>
    public string StateName => _state.ToString();

    public int BulbsLeft => _bulbsLeft;
    public bool IsStunned => _state == State.Stunned;
    public bool IsDefeated => _state == State.Purify || _state == State.Done;
    public int SwordHitsLeft => _health?.CurrentHealth ?? SwordHitsToDefeat;

    private static readonly StringName PlayerGroup = "player";
    private static readonly Vector2 DefaultVisualPos = new(0f, 24f);
    private static readonly Color AimWarn = new(1f, 0.6f, 0.2f, 0.35f);
    private static readonly Color AimLocked = new(1f, 0.15f, 0.15f, 0.6f);
    private static readonly Color StarColor = new(1f, 0.92f, 0.3f);

    private readonly RandomNumberGenerator _rng = new();
    private State _state = State.Dormant;
    private bool _phase2;
    private float _timer;
    private float _animTime;
    private float _thornTimer;
    private float _pulseTimer;
    private bool _pulseOff;
    private bool _contactOn;
    private int _patrolDir = 1;
    private int _hitsThisStun;
    private int _bulbsLeft;
    private int _bulbTotal;
    private Vector2 _aim = Vector2.Down;
    private Vector2 _arrival;
    private bool _hasArrival;
    private float _chargeTravelled;
    private Vector2 _home;
    private bool _sideSheet;
    private bool _drawAim;
    private float _aimLength;
    private float _grace;
    private float _arrowTimer;
    private Node _arrowPack;
    private PackedScene _arrowPackScene;
    private bool _ended;
    private Vector2 _repositionDir;

    private Node2D _visual;
    private Sprite2D _shadow;
    private Sprite2D _body;
    private Sprite2D _thorns;
    private BossBulb[] _bulbs;
    private Health _health;
    private HurtBox _hurtBox;
    private HitBox _hitBox;
    private Player _player;
    private HurtBox _playerHurt;
    private GameState _gameState;
    private PackedScene _thornScene;
    private Texture2D _frontBody, _frontThorns, _sideBody, _sideThorns;
    private Tween _flash;
    private Tween _blink;
    private int _lastFrame = -1;
    private bool _ready;

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
        _thorns = _visual.GetNode<Sprite2D>("Ronces");
        var bulbRoot = _visual.GetNode<Node2D>("Bulbes");
        _bulbs = new BossBulb[bulbRoot.GetChildCount()];
        for (int i = 0; i < _bulbs.Length; i++)
        {
            _bulbs[i] = bulbRoot.GetChild<BossBulb>(i);
            _bulbs[i].Destroyed += OnBulbDestroyed;
        }
        _bulbTotal = _bulbsLeft = _bulbs.Length;

        _health = GetNode<Health>("Health");
        _health.SetValues(SwordHitsToDefeat, SwordHitsToDefeat);
        _health.Died += OnDied;
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _hurtBox.Hit += OnHit;
        _hurtBox.Blocked += OnBlocked;
        _hitBox = GetNode<HitBox>("HitBox");

        _thornScene = GD.Load<PackedScene>("res://scenes/enemies/boss/ronces_sol.tscn");
        _arrowPackScene = GD.Load<PackedScene>("res://scenes/items/fleches.tscn");
        _arrowTimer = ArrowPackDelay;
        _frontBody = LoadTexture(BodyPath);
        _frontThorns = LoadTexture(ThornsPath);
        _sideBody = LoadTexture(SideBodyPath);
        _sideThorns = LoadTexture(SideThornsPath);
        var shadowTexture = LoadTexture(ShadowPath);
        if (shadowTexture != null) _shadow.Texture = shadowTexture;

        _home = GlobalPosition;
        if (EntryPoint.HasValue)
        {
            _arrival = EntryPoint.Value;
            _hasArrival = true;
        }
        if (ArenaBounds.Size == Vector2.Zero)
            ArenaBounds = new Rect2(48f, 48f, 544f, 608f);

        _ready = true;
        ShowSheet(false);
        _thornTimer = 2f;
        SetState(State.Dormant, 0f);
        StartBlink();
    }

    public override void _ExitTree()
    {
        if (!_ready) return;
        if (_health != null) _health.Died -= OnDied;
        if (_hurtBox != null)
        {
            _hurtBox.Hit -= OnHit;
            _hurtBox.Blocked -= OnBlocked;
        }
        if (_bulbs != null)
            foreach (var bulb in _bulbs)
                if (IsInstanceValid(bulb)) bulb.Destroyed -= OnBulbDestroyed;
    }

    // --- Boucle ---------------------------------------------------------------------------------

    public override void _PhysicsProcess(double delta)
    {
        if (!_ready || _state == State.Done) return;
        float dt = (float)delta;
        _animTime += dt;
        FindPlayer();

        if (_player != null && _player.IsDead && _state != State.Purify)
        {
            // Brann est tombé : Sylve se calme en attendant le rechargement de la salle.
            if (_contactOn) SetContact(false);
            if (!_ended && _state != State.Dormant)
            {
                _ended = true;
                EmitSignal(Boss.SignalName.EncounterEnded); // la barre de vie se cache
            }
            _drawAim = false;
            QueueRedraw();
            ApplyPose(SylveFrames.Idle, false);
            return;
        }

        UpdateContactPulse(dt);
        _timer -= dt;
        if (_state == State.Patrol || _state == State.Cast) UpdateArrowSupply(dt);

        switch (_state)
        {
            case State.Dormant: UpdateDormant(); break;
            case State.Intro: UpdateIntro(); break;
            case State.Patrol: UpdatePatrol(dt); break;
            case State.Cast: UpdateCast(); break;
            case State.Transition: UpdateTransition(); break;
            case State.Recover: UpdateRecover(dt); break;
            case State.Reposition: UpdateReposition(); break;
            case State.Windup: UpdateWindup(); break;
            case State.Charge: UpdateCharge(dt); break;
            case State.Stunned: UpdateStunned(); break;
            case State.Hurt: UpdateHurt(); break;
            case State.Purify: UpdatePurify(); break;
        }
    }

    private void UpdateDormant()
    {
        ApplyPose(SylveFrames.Idle, false);
        if (_player == null) return;
        if (!_hasArrival)
        {
            _arrival = _player.GlobalPosition;
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
        foreach (var bulb in _bulbs) bulb.Armed = true;
        AddCollisionExceptionWith(_player); // Sylve traverse Brann (le contact le blesse) : il ne s'arrête que sur les murs et les piliers
        EmitSignal(Boss.SignalName.EncounterStarted);
        EmitProgress();
        ShakeCamera(3f, 0.6f);
        SetState(State.Intro, IntroDuration);
    }

    private void UpdateIntro()
    {
        ApplyPose(SylveFrames.Windup, false);
        ShakeVisual(1.5f);
        if (_timer <= 0f)
        {
            _visual.Position = DefaultVisualPos;
            SetState(State.Patrol, 0f);
        }
    }

    private void UpdatePatrol(float dt)
    {
        _thornTimer -= dt;
        float x = GlobalPosition.X;
        if (x >= _home.X + PatrolHalfWidth) _patrolDir = -1;
        else if (x <= _home.X - PatrolHalfWidth) _patrolDir = 1;
        Velocity = new Vector2(_patrolDir * PatrolSpeed, 0f);
        MoveAndSlide();
        ApplyPose(SylveFrames.Walk, false);

        if (_thornTimer <= 0f)
            SetState(State.Cast, CastSeconds);
    }

    private void UpdateCast()
    {
        ApplyPose(SylveFrames.Windup, false);
        ShakeVisual(1f);
        if (_timer > 0f) return;
        _visual.Position = DefaultVisualPos;
        _thornTimer = ThornInterval;
        SetState(State.Patrol, 0f);
    }

    private void UpdateTransition()
    {
        ApplyPose(SylveFrames.Hurt, false);
        ShakeVisual(2f);
        if (_timer > 0f) return;
        _visual.Position = DefaultVisualPos;
        _phase2 = true;
        SetState(State.Recover, RecoverSeconds + 0.5f);
    }

    private void UpdateRecover(float dt)
    {
        ApplyPose(SylveFrames.Idle, false);
        if (_grace > 0f)
        {
            _grace -= dt;
            if (_grace <= 0f) SetContact(true);
        }
        if (_timer <= 0f) BeginWindup();
    }

    // Collé à un obstacle sur la ligne de la charge : un pas de côté (vers Brann si possible), puis nouvelle préparation.
    private void BeginReposition()
    {
        var side = new Vector2(-_aim.Y, _aim.X);
        if (_player != null && side.Dot(_player.GlobalPosition - GlobalPosition) < 0f) side = -side;
        if (TestMove(GlobalTransform, side * 8f)) side = -side;
        _repositionDir = side;
        SetState(State.Reposition, RepositionSeconds);
    }

    private void UpdateReposition()
    {
        ApplyPose(SylveFrames.Walk, false);
        MoveAndCollide(_repositionDir * RepositionSpeed * (float)GetPhysicsProcessDeltaTime());
        if (_timer <= 0f) BeginWindup();
    }

    // Retour au calme après un assommement ou un coup : un court instant sans contact dangereux.
    private void Recover(float seconds, bool withGrace)
    {
        _grace = withGrace ? GraceSeconds : 0f;
        SetState(State.Recover, seconds);
    }

    private void BeginWindup()
    {
        SetState(State.Windup, WindupSeconds);
        UpdateAim();
    }

    private void UpdateWindup()
    {
        float elapsed = WindupSeconds - _timer;
        if (elapsed < WindupSeconds * AimTrackFraction)
            UpdateAim();
        _drawAim = true;
        _aimLength = Mathf.Min(ChargeMaxDistance, BossRules.DistanceToRectEdge(
            GlobalPosition.X, GlobalPosition.Y, _aim.X, _aim.Y, ArenaBounds.Position.X, ArenaBounds.Position.Y, ArenaBounds.Size.X, ArenaBounds.Size.Y));
        bool side = Mathf.Abs(_aim.X) > Mathf.Abs(_aim.Y);
        ApplyPose(side ? SylveFrames.SideWindup : SylveFrames.Windup, side);
        ShakeVisual(2f);
        QueueRedraw();
        if (_timer > 0f) return;

        _visual.Position = DefaultVisualPos;
        if (TestMove(GlobalTransform, _aim * 6f))
        {
            BeginReposition(); // déjà collé à un obstacle sur la ligne de charge
            QueueRedraw();
            return;
        }
        _chargeTravelled = 0f;
        SetState(State.Charge, 0f);
        QueueRedraw();
    }

    private void UpdateAim()
    {
        if (_player == null) return;
        var toPlayer = _player.GlobalPosition + Player.FeetOffset - GlobalPosition;
        if (toPlayer.LengthSquared() > 1f) _aim = toPlayer.Normalized();
    }

    private void UpdateCharge(float dt)
    {
        bool side = Mathf.Abs(_aim.X) > Mathf.Abs(_aim.Y);
        ApplyPose(side ? SylveFrames.SideCharge : SylveFrames.Charge, side);

        float step = ChargeSpeed * dt;
        var collision = MoveAndCollide(_aim * step);
        _chargeTravelled += step;
        if (collision != null)
        {
            float moved = _chargeTravelled - step + collision.GetTravel().Length(); // distance réellement parcourue
            if (moved >= MinChargeToStun && HitPillar(collision.GetPosition()))
            {
                BeginStun();
                return;
            }
            ShakeCamera(2f, 0.2f); // un mur : il s'arrête simplement
            SetState(State.Recover, WallBumpSeconds);
            return;
        }
        if (_chargeTravelled >= ChargeMaxDistance)
            SetState(State.Recover, RecoverSeconds);
    }

    private bool HitPillar(Vector2 point)
    {
        for (int i = 0; i < Pillars.Count; i++)
        {
            var r = Pillars[i];
            if (BossRules.IsInsideRect(point.X, point.Y, r.Position.X, r.Position.Y, r.Size.X, r.Size.Y, PillarMargin))
                return true;
        }
        return false;
    }

    private void BeginStun()
    {
        _hitsThisStun = 0;
        ShakeCamera(5f, 0.35f);
        SetState(State.Stunned, BossRules.StunDuration(StunSeconds, _gameState.PuzzleTimeMultiplier));
    }

    private void UpdateStunned()
    {
        ApplyPose(SylveFrames.Stunned, false);
        QueueRedraw(); // étoiles
        if (_timer <= 0f) Recover(RecoverSeconds, true);
    }

    private void UpdateHurt()
    {
        ApplyPose(SylveFrames.Hurt, false);
        if (_timer <= 0f) Recover(RecoverSeconds, true);
    }

    private void UpdatePurify()
    {
        ApplyPose(SylveFrames.Purified, false);
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
        _lastFrame = -1;
        _drawAim = false;
        _pulseTimer = ContactPulse;
        Velocity = Vector2.Zero;
        if (redraw) QueueRedraw();
        if (state != State.Windup && state != State.Charge) ShowSheet(false);

        if (state == State.Cast) SpawnThorns();
        ApplyDefence();
    }

    // Quand est-il vulnérable, touchable, dangereux ? Tout se décide ici, à chaque changement d'état.
    private void ApplyDefence()
    {
        bool bodyTouchable = _phase2 && _state != State.Transition && _state != State.Purify && _state != State.Done;
        _hurtBox.SetDeferred(Area2D.PropertyName.Monitorable, bodyTouchable);
        _hurtBox.Invincible = _state != State.Stunned;

        bool dangerous = _state == State.Patrol || _state == State.Cast || _state == State.Windup
            || _state == State.Charge || _state == State.Reposition || (_state == State.Recover && _grace <= 0f);
        SetContact(dangerous);
    }

    private void SetContact(bool on)
    {
        _contactOn = on;
        _pulseOff = false;
        _hitBox.SetDeferred(Area2D.PropertyName.Monitoring, on);
    }

    // Tant que Brann reste dans Sylve et n'est pas protégé, le contact est réarmé régulièrement (une Area2D ne signale qu'une entrée).
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

    // Brann ne reste jamais coincé : s'il a l'arc mais trop peu de flèches pour les bulbes restants, un paquet apparaît
    // au centre de l'arène (hors de la ligne de tir de Sylve), un seul à la fois, au bout de ArrowPackDelay.
    private void UpdateArrowSupply(float dt)
    {
        bool packExists = _arrowPack != null && IsInstanceValid(_arrowPack) && !_arrowPack.IsQueuedForDeletion();
        bool needed = !packExists && _gameState.HasItem(GameState.BowItemId)
            && _gameState.GetQuantity(GameState.BowItemId) < _bulbsLeft + ArrowMargin;
        if (!needed)
        {
            _arrowTimer = ArrowPackDelay;
            return;
        }
        _arrowTimer -= dt;
        if (_arrowTimer > 0f || _arrowPackScene == null) return;
        _arrowTimer = ArrowPackDelay;
        var pack = _arrowPackScene.Instantiate<Pickup>();
        pack.Lifetime = ArrowPackLifetime;
        GetParent().AddChild(pack); // le Pickup épingle son effet (ResourceKeeper.Pin) dans son _Ready
        pack.GlobalPosition = ArenaBounds.GetCenter();
        _arrowPack = pack;
    }

    // --- Phase 1 : ronces -----------------------------------------------------------------------

    private void SpawnThorns()
    {
        if (_player == null || _thornScene == null) return;
        var parent = GetParent();
        var target = _player.GlobalPosition + Player.FeetOffset;
        for (int i = 0; i < ThornCount; i++)
        {
            var pos = target;
            if (i > 0)
            {
                float angle = _rng.RandfRange(0f, Mathf.Tau);
                pos += Vector2.Right.Rotated(angle) * ThornSpread;
                pos = new Vector2(
                    Mathf.Clamp(pos.X, ArenaBounds.Position.X + 24f, ArenaBounds.End.X - 24f),
                    Mathf.Clamp(pos.Y, ArenaBounds.Position.Y + 24f, ArenaBounds.End.Y - 24f));
            }
            var thorn = _thornScene.Instantiate<ThornEruption>();
            parent.AddChild(thorn);
            thorn.GlobalPosition = pos - new Vector2(0f, ThornEruption.SortOffset);
        }
    }

    private void ClearThorns()
    {
        foreach (var node in GetTree().GetNodesInGroup(ThornEruption.GroupName))
            node.QueueFree();
    }

    private void OnBulbDestroyed()
    {
        if (_bulbsLeft <= 0) return;
        _bulbsLeft--;
        FlashVisual(new Color(2f, 1.2f, 2f), 0.2f);
        ShakeCamera(2f, 0.25f);
        EmitProgress();
        if (_bulbsLeft == 0 && !_phase2 && _state != State.Transition)
        {
            ClearThorns();
            ShakeCamera(4f, 0.7f);
            SetState(State.Transition, TransitionSeconds);
        }
    }

    // --- Coups reçus ----------------------------------------------------------------------------

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_state != State.Stunned) return; // vaincu ou autre : Died s'en occupe
        _hitsThisStun += Mathf.Max(1, damage); // dégâts réels : une flèche (2) compte double
        FlashVisual(new Color(4f, 4f, 4f), 0.12f);
        EmitProgress();
        if (_health.CurrentHealth > 0 && _hitsThisStun >= HitsPerStun)
            SetState(State.Hurt, HurtSeconds);
    }

    // Invincible : un petit éclat bleuté montre que le coup n'a rien fait.
    private void OnBlocked(int damage, Vector2 fromPosition) => FlashVisual(new Color(0.65f, 0.75f, 1.4f), 0.15f);

    private void OnDied()
    {
        // Health.Damage émet Died avant que la HurtBox émette Hit : OnHit trouvera l'état « purification » et ne fera rien.
        EmitProgress();
        BeginPurify();
    }

    // --- Victoire -------------------------------------------------------------------------------

    private void BeginPurify()
    {
        ClearThorns();
        _blink?.Kill();
        SetState(State.Purify, PurifySeconds);
        ShakeCamera(4f, 0.8f);
        FlashVisual(new Color(3f, 3f, 2.2f), 0.5f);
        // Les ronces noires tombent : elles glissent vers le sol en s'effaçant.
        _thorns.Modulate = Colors.White;
        var fall = CreateTween().SetParallel();
        fall.TweenProperty(_thorns, "position:y", _thorns.Position.Y + 28f, PurifySeconds * 0.7f).SetTrans(Tween.TransitionType.Quad).SetEase(Tween.EaseType.In);
        fall.TweenProperty(_thorns, "modulate:a", 0f, PurifySeconds * 0.7f);
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

        // Après la réplique, Sylve se fond dans la lumière.
        var tween = CreateTween();
        tween.TweenInterval(LingerSeconds);
        tween.TweenProperty(_visual, "modulate:a", 0f, 1.5f);
        tween.TweenCallback(Callable.From(QueueFree));
    }

    // --- Affichage ------------------------------------------------------------------------------

    private static Texture2D LoadTexture(string path)
    {
        if (ResourceLoader.Exists(path)) return GD.Load<Texture2D>(path);
        GD.PushWarning($"Sylve : image absente ({path}).");
        return null;
    }

    private void ShowSheet(bool side)
    {
        _sideSheet = side;
        var body = side ? _sideBody : _frontBody;
        var thorns = side ? _sideThorns : _frontThorns;
        if (_body.Texture != body)
        {
            _body.Texture = body;
            _body.Hframes = body != null ? Mathf.Max(1, body.GetWidth() / SylveFrames.CellSize) : 1;
            _lastFrame = -1;
        }
        if (_thorns.Texture != thorns)
        {
            _thorns.Texture = thorns;
            _thorns.Hframes = thorns != null ? Mathf.Max(1, thorns.GetWidth() / SylveFrames.CellSize) : 1;
            _lastFrame = -1;
        }
        bool flip = side && _aim.X > 0f; // la planche de côté regarde à gauche
        _body.FlipH = flip;
        _thorns.FlipH = flip;
    }

    // Choisit la planche (face ou côté), la case de l'animation et replace les bulbes sur les bois.
    private void ApplyPose(SylveFrames.Clip clip, bool side)
    {
        if (side != _sideSheet) ShowSheet(side);
        bool flip = side && _aim.X > 0f; // la planche de côté regarde à gauche
        _body.FlipH = flip;
        _thorns.FlipH = flip;
        int frame = clip.FrameAt(_animTime);
        if (frame == _lastFrame) return;
        _lastFrame = frame;
        _body.Frame = Mathf.Min(frame, _body.Hframes - 1);
        _thorns.Frame = Mathf.Min(frame, _thorns.Hframes - 1);
        if (!side) PlaceBulbs(frame);
    }

    private void PlaceBulbs(int frame)
    {
        for (int i = 0; i < _bulbs.Length && i < 3; i++)
        {
            int x = SylveFrames.BulbCoord(frame, i, false);
            if (x < 0) continue;
            int y = SylveFrames.BulbCoord(frame, i, true);
            _bulbs[i].Position = new Vector2(x - SylveFrames.OriginX, y - SylveFrames.OriginY);
        }
    }

    // La corruption clignote (calque séparé) tant que Sylve n'est pas purifié.
    private void StartBlink()
    {
        _blink?.Kill();
        _blink = CreateTween().SetLoops();
        _blink.TweenProperty(_thorns, "modulate:a", 0.55f, 0.5f);
        _blink.TweenProperty(_thorns, "modulate:a", 1f, 0.5f);
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
        _visual.Position = DefaultVisualPos + new Vector2(_rng.RandfRange(-amount, amount), 0f);
    }

    private void ShakeCamera(float strength, float seconds)
    {
        if (GetViewport().GetCamera2D() is CameraShake shake)
            shake.Shake(strength, seconds);
    }

    private void EmitProgress()
    {
        EmitSignal(Boss.SignalName.ProgressChanged,
            BossRules.Progress(_bulbsLeft + _health.CurrentHealth, _bulbTotal + SwordHitsToDefeat));
    }

    // Avertissement de charge (bande qui devient rouge quand la direction est verrouillée) et étoiles de l'assommement.
    public override void _Draw()
    {
        if (_state == State.Windup && _drawAim && _aimLength > 0f)
        {
            bool locked = (WindupSeconds - _timer) >= WindupSeconds * AimTrackFraction;
            DrawLine(Vector2.Zero, _aim * _aimLength, locked ? AimLocked : AimWarn, locked ? 18f : 10f);
        }
        if (_state == State.Stunned)
        {
            for (int i = 0; i < 3; i++)
            {
                float a = _animTime * 4f + i * Mathf.Tau / 3f;
                DrawCircle(new Vector2(Mathf.Cos(a) * 22f, -52f + Mathf.Sin(a) * 6f), 3f, StarColor);
            }
        }
    }
}
