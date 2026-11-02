using System.Collections.Generic;
using Godot;

/// <summary>
/// Ondine, la Gardienne du Lac (boss du donjon 3). Deux phases, composées des composants habituels (Health, HurtBox).
/// Phase 1 « surgissement » : elle plonge (intouchable), un anneau d'ondes annonce le bassin où elle va surgir (visible dans le cercle de
/// lumière de la lanterne, un « glou » s'entend partout), elle surgit (éclaboussure d'un demi-cœur si Brann n'a pas bougé), reste exposée
/// <see cref="ExposedSeconds"/> secondes (seule la HurtBox « Armure » est vulnérable, à l'épée) puis replonge. L'armure a
/// <see cref="ArmorHealth"/> PV ; une apparition n'encaisse que <see cref="DamagePerAppearance"/> PV au plus (voir <see cref="OndineRules.AppearancesToBreak"/>).
/// Phase 2 « morceaux d'armure » : l'armure éclate, Ondine s'agenouille (invincible, inoffensive) et lâche quatre morceaux par vagues de deux
/// (scène morceau_armure : même comportement que l'Ombre noyée, figés et visibles dans la lanterne). Vaincue quand les quatre sont détruits.
/// Récompenses et réplique gérées par la salle (voir <see cref="Boss"/>). Images : art/bosses/ondine/.
/// </summary>
public partial class OndineBoss : Boss
{
    private enum State { Dormant, Dive, Announce, Surge, Exposed, Hurt, Plunge, Break, Kneel, Free, Done }

    [ExportGroup("Début du combat")]
    /// <summary>Distance (px) dont Brann doit s'éloigner de son point d'arrivée pour que le combat commence (la porte se referme).</summary>
    [Export(PropertyHint.Range, "32,300,8")] public float StartDistance { get; set; } = 96f;

    [ExportGroup("Phase 1 : surgissement")]
    /// <summary>Armure : PV à perdre avant la phase 2 (1 PV par coup d'épée normal, 2 avec l'épée trempée).</summary>
    [Export(PropertyHint.Range, "1,20,1")] public int ArmorHealth { get; set; } = 6;
    /// <summary>PV qu'une seule apparition peut encaisser au maximum : au-delà elle replonge (6 PV / 2 = trois apparitions).</summary>
    [Export(PropertyHint.Range, "1,6,1")] public int DamagePerAppearance { get; set; } = 2;
    [Export(PropertyHint.Range, "0.5,6,0.1")] public float DiveSeconds { get; set; } = 2f;
    /// <summary>Annonce (s), multipliée par l'option d'aide GameState.PuzzleTimeMultiplier (plafonnée à x2 ; 0 = illimité = x2).</summary>
    [Export(PropertyHint.Range, "0.5,5,0.1")] public float AnnounceBaseSeconds { get; set; } = 1.5f;
    [Export(PropertyHint.Range, "0.1,1.5,0.05")] public float SurgeSeconds { get; set; } = 0.4f;
    [Export(PropertyHint.Range, "1,10,0.5")] public float ExposedSeconds { get; set; } = 3.5f;
    [Export(PropertyHint.Range, "0.1,2,0.05")] public float HurtSeconds { get; set; } = 0.5f;
    [Export(PropertyHint.Range, "0.1,2,0.05")] public float PlungeSeconds { get; set; } = 0.5f;
    /// <summary>Un bassin n'est choisi que s'il est à moins de cette distance (px) de Brann (lanterne 160 px + marge).</summary>
    [Export(PropertyHint.Range, "64,400,8")] public float BasinRadius { get; set; } = 190f;
    /// <summary>Rayon (px) de l'éclaboussure autour du centre du bassin.</summary>
    [Export(PropertyHint.Range, "8,64,1")] public float SplashRadius { get; set; } = 28f;
    /// <summary>Dégâts de l'éclaboussure (1 PV = un demi-cœur).</summary>
    [Export(PropertyHint.Range, "1,4,1")] public int SplashDamage { get; set; } = 1;
    /// <summary>Opacité de l'anneau d'ondes hors du cercle de lumière de la lanterne (salle sombre).</summary>
    [Export(PropertyHint.Range, "0,1,0.01")] public float RingHiddenAlpha { get; set; } = 0.12f;

    [ExportGroup("Phase 2 : morceaux d'armure")]
    [Export(PropertyHint.Range, "1,8,1")] public int PieceCount { get; set; } = 4;
    [Export(PropertyHint.Range, "1,4,1")] public int WaveSize { get; set; } = 2;
    [Export(PropertyHint.Range, "0.5,6,0.1")] public float BreakSeconds { get; set; } = 1.6f;
    /// <summary>Pause (s) entre le début de la phase 2 (ou la fin d'une vague) et le lâcher de la vague suivante.</summary>
    [Export(PropertyHint.Range, "0.2,6,0.1")] public float WaveDelay { get; set; } = 1.2f;
    [Export] public string PieceScenePath { get; set; } = "res://scenes/enemies/boss/morceau_armure.tscn";

    [ExportGroup("Victoire")]
    [Export(PropertyHint.Range, "1,8,0.5")] public float FreeSeconds { get; set; } = 2.5f;
    [Export(PropertyHint.Range, "1,15,0.5")] public float LingerSeconds { get; set; } = 7f;

    /// <summary>Phase en cours (1 ou 2 ; 0 avant le combat).</summary>
    public int Phase => _state == State.Dormant ? 0 : _phase2 ? 2 : 1;
    public string StateName => _state.ToString();
    public bool IsDefeated => _state == State.Free || _state == State.Done;
    public int ArmorLeft => _health?.CurrentHealth ?? ArmorHealth;
    public int PiecesLeft => PieceCount - _piecesKilled;
    /// <summary>Morceaux d'armure en vie (tests et débogage).</summary>
    public int PiecesAlive => _pieces.Count;

    private static readonly StringName PlayerGroup = "player";
    private static readonly NodePath LanternNode = "Lanterne";
    private static readonly StringName AnimCache = "cache";
    private static readonly StringName AnimSurge = "surgit";
    private static readonly StringName AnimPlunge = "plonge";
    private static readonly StringName AnimIdle = "idle";
    private static readonly StringName AnimHurt = "touche";
    private static readonly StringName AnimBreak = "eclate";
    private static readonly StringName AnimKneel = "agenouillee";
    private static readonly StringName AnimFree = "liberee";
    private static readonly StringName RingAnnounce = "annonce";
    private static readonly StringName RingPulse = "pulse";
    private static readonly StringName FloatAnim = "float";
    private const int MaxBasins = 6;
    private const float SplashSeconds = 0.35f;
    private const float RingAnnounceNaturalSeconds = 0.8f; // 4 images à 5 images/s dans anneau_frames.tres

    // Repli si la carte n'a pas les Marqueurs « ondine_surgit_N » : centres des six bassins de salle_boss.tmx.
    private static readonly Vector2[] FallbackBasins =
    {
        new(112f, 144f), new(528f, 144f), new(112f, 336f), new(528f, 336f), new(112f, 528f), new(528f, 528f),
    };
    private static readonly string[] PieceFramesPaths =
    {
        "res://resources/enemies/morceau_casque_frames.tres",
        "res://resources/enemies/morceau_plastron_frames.tres",
        "res://resources/enemies/morceau_gantelet_frames.tres",
        "res://resources/enemies/morceau_gantelet_frames.tres",
    };

    private readonly RandomNumberGenerator _rng = new();
    private readonly float[] _basinX = new float[MaxBasins];
    private readonly float[] _basinY = new float[MaxBasins];
    private int _basinCount;
    private bool _basinsLoaded;
    private int _lastBasin = -1;
    private readonly List<Health> _pieces = new();

    private State _state = State.Dormant;
    private bool _phase2;
    private bool _ready;
    private bool _ended;
    private bool _hasArrival;
    private Vector2 _arrival;
    private Vector2 _home;
    private float _timer;
    private float _animTime;
    private int _hitsThisAppearance;
    private float _splashTime;
    private int _piecesSpawned;
    private int _piecesKilled;
    private bool _dark;
    private bool _darkChecked;
    private PackedScene _pieceScene;
    private SpriteFrames[] _pieceFrames;

    private Node2D _visual;
    private Sprite2D _shadow;
    private AnimatedSprite2D _body;
    private AnimatedSprite2D _armor;
    private AnimatedSprite2D _ring;
    private Health _health;
    private HurtBox _armorBox;
    private Player _player;
    private HurtBox _playerHurt;
    private LanternLight _lantern;
    private GameState _gameState;
    private Tween _flash;

    public override void _Ready()
    {
        _rng.Randomize();
        _gameState = GetNode<GameState>("/root/GameState");
        if (_gameState.IsCollected(BossId))
        {
            QueueFree(); // déjà vaincue : la salle ne devrait pas l'instancier
            return;
        }

        _home = GlobalPosition;
        _visual = GetNode<Node2D>("Visuel");
        _shadow = _visual.GetNode<Sprite2D>("Ombre");
        _body = _visual.GetNode<AnimatedSprite2D>("Corps");
        _armor = _visual.GetNode<AnimatedSprite2D>("ArmureCalque");
        _ring = GetNode<AnimatedSprite2D>("Anneau");
        _health = GetNode<Health>("Health");
        _health.SetValues(ArmorHealth, ArmorHealth);
        _health.Died += OnDied;
        _armorBox = GetNode<HurtBox>("Armure");
        _armorBox.Hit += OnHit;
        _ring.AnimationFinished += OnRingFinished;

        _pieceScene = GD.Load<PackedScene>(PieceScenePath);
        _pieceFrames = new SpriteFrames[PieceFramesPaths.Length];
        for (int i = 0; i < PieceFramesPaths.Length; i++)
        {
            _pieceFrames[i] = GD.Load<SpriteFrames>(PieceFramesPaths[i]);
            if (_pieceFrames[i] == null) GD.PushWarning($"Ondine : images de morceau d'armure introuvables ({PieceFramesPaths[i]}).");
        }

        _shadow.Visible = false;
        _ring.Visible = false;
        _ready = true;
        SetState(State.Dormant, 0f);
    }

    public override void _ExitTree()
    {
        if (!_ready) return;
        if (_health != null) _health.Died -= OnDied;
        if (_armorBox != null) _armorBox.Hit -= OnHit;
        if (_ring != null) _ring.AnimationFinished -= OnRingFinished;
        ClearPieces();
    }

    // --- Boucle ---------------------------------------------------------------------------------

    public override void _PhysicsProcess(double delta)
    {
        if (!_ready || _state == State.Done) return;
        float dt = (float)delta;
        _animTime += dt;
        if (_splashTime > 0f)
        {
            _splashTime -= dt;
            QueueRedraw();
        }
        FindPlayer();
        if (!_darkChecked)
        {
            _dark = Room.IsDarkRoom(this); // la Room lit « obscurite » avant d'ajouter le boss, mais on reste prudent
            _darkChecked = true;
        }

        if (_player != null && _player.IsDead && !IsDefeated)
        {
            // Brann est tombé : Ondine se calme en attendant le rechargement de la salle.
            if (!_ended && _state != State.Dormant)
            {
                _ended = true;
                EmitSignal(Boss.SignalName.EncounterEnded);
            }
            return;
        }

        _timer -= dt;
        switch (_state)
        {
            case State.Dormant: UpdateDormant(); break;
            case State.Dive: if (_timer <= 0f) BeginAnnounce(); break;
            case State.Announce: UpdateAnnounce(); break;
            case State.Surge: UpdateSurge(); break;
            case State.Exposed: UpdateExposed(); break;
            case State.Hurt: if (_timer <= 0f) BeginPlunge(); break;
            case State.Plunge: if (_timer <= 0f) BeginDive(); break;
            case State.Break: UpdateBreak(); break;
            case State.Kneel: UpdateKneel(); break;
            case State.Free: if (_timer <= 0f) FinishVictory(); break;
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
        if (_player.GlobalPosition.DistanceSquaredTo(_arrival) >= StartDistance * StartDistance)
            StartEncounter();
    }

    private void StartEncounter()
    {
        foreach (var door in ArenaDoors)
            if (IsInstanceValid(door)) door.LockForEncounter();
        EmitSignal(Boss.SignalName.EncounterStarted);
        AudioManager.Play(Sfx.BossRugit);
        EmitSignal(Boss.SignalName.HintRequested, "BOSS_ONDINE_CONSEIL_1", 8f);
        EmitProgress();
        LoadBasins();
        BeginDive();
    }

    // --- Phase 1 : surgissement -----------------------------------------------------------------

    private void BeginDive()
    {
        _hitsThisAppearance = 0;
        SetState(State.Dive, DiveSeconds);
    }

    private void BeginAnnounce()
    {
        var from = _player != null ? _player.GlobalPosition + Player.FeetOffset : _home;
        int i = OndineRules.PickBasin(_basinX, _basinY, _basinCount, from.X, from.Y, _lastBasin, BasinRadius, _rng.Randf());
        if (i < 0)
        {
            SetState(State.Dive, DiveSeconds); // aucun bassin : on attend (ne devrait pas arriver)
            return;
        }
        _lastBasin = i;
        GlobalPosition = new Vector2(_basinX[i], _basinY[i]);
        float seconds = OndineRules.AnnounceSeconds(AnnounceBaseSeconds, _gameState.PuzzleTimeMultiplier);
        SetState(State.Announce, seconds);
        _ring.Visible = true;
        _ring.SpeedScale = RingAnnounceNaturalSeconds / Mathf.Max(0.1f, seconds); // l'animation d'annonce s'étale sur toute l'annonce
        _ring.Play(RingAnnounce);
        UpdateRingAlpha();
        AudioManager.Play(Sfx.Glou); // entendu partout, sans position
    }

    private void UpdateAnnounce()
    {
        UpdateRingAlpha();
        if (_timer > 0f) return;
        _ring.Visible = false;
        _ring.Stop();
        SetState(State.Surge, SurgeSeconds);
        PlayBoth(AnimSurge);
        AudioManager.PlayAt(Sfx.BossCharge, GlobalPosition);
        ShakeCamera(2f, 0.2f);
        _splashTime = SplashSeconds;
        if (_player != null && _playerHurt != null && IsInstanceValid(_playerHurt))
        {
            var d = _player.GlobalPosition + Player.FeetOffset - GlobalPosition;
            if (OndineRules.SplashHits(d.X, d.Y, SplashRadius))
                _playerHurt.ReceiveHit(SplashDamage, GlobalPosition);
        }
    }

    private void UpdateSurge()
    {
        if (_timer > 0f) return;
        SetState(State.Exposed, ExposedSeconds);
        PlayBoth(AnimIdle);
    }

    private void UpdateExposed()
    {
        // L'armure clignote tant qu'elle est vulnérable.
        float a = 0.7f + 0.3f * Mathf.Sin(_animTime * 14f);
        _armor.SelfModulate = new Color(1f, 1f, 1f, a);
        if (_timer <= 0f) BeginPlunge();
    }

    private void BeginPlunge()
    {
        SetState(State.Plunge, PlungeSeconds);
        PlayBoth(AnimPlunge);
    }

    // L'anneau n'est lisible que dans la lumière de la lanterne (salle sombre, lanterne possédée) : c'est son rôle.
    private void UpdateRingAlpha()
    {
        float alpha = 1f;
        if (_dark && _gameState.HasItem(LanternRules.ItemId) && _player != null)
        {
            if (_lantern == null || !IsInstanceValid(_lantern)) _lantern = _player.GetNodeOrNull<LanternLight>(LanternNode);
            if (_lantern != null && !_lantern.LanternCovers(GlobalPosition)) alpha = RingHiddenAlpha;
        }
        _ring.SelfModulate = new Color(1f, 1f, 1f, alpha);
    }

    private void OnRingFinished()
    {
        if (_state != State.Announce) return;
        _ring.SpeedScale = 1f;
        _ring.Play(RingPulse);
    }

    // --- Coups reçus ----------------------------------------------------------------------------

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_state != State.Exposed) return; // vaincue (Died arrive avant Hit) ou autre : rien
        _hitsThisAppearance += Mathf.Max(1, damage);
        FlashBody(new Color(4f, 4f, 4f), 0.12f);
        EmitProgress();
        if (_health.CurrentHealth > 0 && _hitsThisAppearance >= DamagePerAppearance)
        {
            SetState(State.Hurt, HurtSeconds);
            PlayBoth(AnimHurt);
        }
    }

    private void OnDied()
    {
        // Health.Damage émet Died avant que la HurtBox émette Hit : OnHit trouvera l'état « Break » et ne fera rien.
        _phase2 = true;
        EmitProgress();
        SetState(State.Break, BreakSeconds);
        PlayBoth(AnimBreak);
        AudioManager.PlayAt(Sfx.BossAssomme, GlobalPosition);
        ShakeCamera(4f, 0.8f);
        FlashBody(new Color(3f, 3f, 3.5f), 0.4f);
    }

    // --- Phase 2 : morceaux d'armure ------------------------------------------------------------

    private void UpdateBreak()
    {
        if (_timer > 0f) return;
        // Ondine, sans armure, retourne à sa place sur la carte (point boss_ondine) et s'agenouille.
        GlobalPosition = _home;
        SetState(State.Kneel, WaveDelay);
        _shadow.Visible = true;
        _body.Play(AnimKneel);
        EmitSignal(Boss.SignalName.HintRequested, "BOSS_ONDINE_CONSEIL_2", 8f);
    }

    private void UpdateKneel()
    {
        // Un morceau sorti de l'arbre sans Died ne doit jamais bloquer le combat : on le compte comme détruit.
        for (int i = _pieces.Count - 1; i >= 0; i--)
        {
            if (IsInstanceValid(_pieces[i])) continue;
            _pieces.RemoveAt(i);
            _piecesKilled++;
            EmitProgress();
        }
        if (_piecesKilled >= PieceCount && _pieces.Count == 0)
        {
            BeginFree();
            return;
        }
        if (_pieces.Count > 0 || _timer > 0f) return;
        int n = OndineRules.NextWaveSize(_piecesSpawned, PieceCount, WaveSize);
        if (n <= 0) return;
        for (int i = 0; i < n; i++) SpawnPiece(i, n);
        _timer = WaveDelay;
    }

    private void SpawnPiece(int index, int inWave)
    {
        if (_pieceScene == null) return;
        var piece = _pieceScene.Instantiate<CharacterBody2D>();
        var sprite = piece.GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        int kind = Mathf.Min(_piecesSpawned, _pieceFrames.Length - 1);
        if (_pieceFrames[kind] != null) sprite.SpriteFrames = _pieceFrames[kind];
        float side = inWave <= 1 ? 0f : (index == 0 ? -1f : 1f);
        GetParent().AddChild(piece);
        piece.GlobalPosition = _home + new Vector2(side * 26f, 8f);
        sprite.Play(FloatAnim);
        var health = piece.GetNode<Health>("Health");
        health.Died += OnPieceDied;
        _pieces.Add(health);
        _piecesSpawned++;
        AudioManager.PlayAt(Sfx.BossAssomme, piece.GlobalPosition);
    }

    private void OnPieceDied()
    {
        // Retire de la liste le morceau dont la vie est à 0 (un seul meurt par signal).
        for (int i = _pieces.Count - 1; i >= 0; i--)
        {
            if (IsInstanceValid(_pieces[i]) && _pieces[i].CurrentHealth > 0) continue;
            if (IsInstanceValid(_pieces[i])) _pieces[i].Died -= OnPieceDied;
            _pieces.RemoveAt(i);
            _piecesKilled++;
            break;
        }
        EmitProgress();
        if (_piecesKilled >= PieceCount && _state == State.Kneel) BeginFree();
    }

    private void ClearPieces()
    {
        for (int i = _pieces.Count - 1; i >= 0; i--)
        {
            var health = _pieces[i];
            if (!IsInstanceValid(health)) continue;
            health.Died -= OnPieceDied;
            health.GetParent()?.QueueFree();
        }
        _pieces.Clear();
    }

    // --- Victoire -------------------------------------------------------------------------------

    private void BeginFree()
    {
        SetState(State.Free, FreeSeconds);
        PlayBoth(AnimFree);
        AudioManager.Play(Sfx.BossVaincu);
        ShakeCamera(3f, 0.6f);
        FlashBody(new Color(3f, 3f, 2.6f), 0.5f);
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

    // --- États et affichage ---------------------------------------------------------------------

    private void SetState(State state, float seconds)
    {
        _state = state;
        _timer = seconds;
        _animTime = 0f;
        ApplyDefence();
        // Sous l'eau (attente, plongée, annonce) : invisible. Le calque d'armure existe jusqu'à son éclatement.
        bool hidden = state == State.Dormant || state == State.Dive || state == State.Announce;
        _visual.Visible = !hidden;
        _armor.Visible = !hidden && state != State.Kneel && state != State.Free && state != State.Done;
        if (state != State.Exposed) _armor.SelfModulate = Colors.White;
        if (state == State.Dive) _body.Play(AnimCache);
        if (state != State.Announce) _ring.Visible = false;
    }

    // Quand est-elle touchable ? Seulement exposée (phase 1) ; sinon la zone ne répond pas du tout.
    private void ApplyDefence()
    {
        bool exposed = _state == State.Exposed;
        _armorBox.Invincible = !exposed;
        _armorBox.SetDeferred(Area2D.PropertyName.Monitorable, exposed);
    }

    private void PlayBoth(StringName anim)
    {
        _body.Play(anim);
        if (_armor.SpriteFrames != null && _armor.SpriteFrames.HasAnimation(anim)) _armor.Play(anim);
    }

    private void FlashBody(Color color, float seconds)
    {
        _flash?.Kill();
        _body.Modulate = color;
        _flash = CreateTween();
        _flash.TweenProperty(_body, "modulate", Colors.White, seconds);
    }

    private void FindPlayer()
    {
        if (_player != null && IsInstanceValid(_player)) return;
        _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Player;
        _playerHurt = _player?.GetNodeOrNull<HurtBox>("HurtBox");
    }

    private void LoadBasins()
    {
        if (_basinsLoaded) return;
        _basinsLoaded = true;
        Room room = null;
        for (Node n = GetParent(); n != null && room == null; n = n.GetParent()) room = n as Room;
        for (int i = 1; i <= MaxBasins && room != null; i++)
        {
            if (!room.TryGetPoint("ondine_surgit_" + i, out var p)) break;
            _basinX[_basinCount] = p.X;
            _basinY[_basinCount] = p.Y;
            _basinCount++;
        }
        if (_basinCount > 0) return;
        for (int i = 0; i < MaxBasins; i++)
        {
            _basinX[i] = FallbackBasins[i].X;
            _basinY[i] = FallbackBasins[i].Y;
        }
        _basinCount = MaxBasins;
    }

    private void ShakeCamera(float strength, float seconds)
    {
        if (GetViewport().GetCamera2D() is CameraShake shake)
            shake.Shake(strength, seconds);
    }

    private void EmitProgress()
    {
        EmitSignal(Boss.SignalName.ProgressChanged,
            OndineRules.Progress(_health.CurrentHealth, ArmorHealth, PieceCount - _piecesKilled, PieceCount));
    }

    // Éclaboussure : un anneau clair qui s'élargit autour du bassin.
    public override void _Draw()
    {
        if (_splashTime <= 0f) return;
        float k = 1f - _splashTime / SplashSeconds;
        DrawArc(Vector2.Zero, SplashRadius * (0.4f + 0.6f * k), 0f, Mathf.Tau, 24, new Color(0.7f, 0.95f, 1f, 1f - k), 3f);
    }
}
