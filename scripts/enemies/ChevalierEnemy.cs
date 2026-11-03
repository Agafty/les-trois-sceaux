using Godot;

/// <summary>
/// Chevalier corrompu (château) : chasseur à bouclier, sur le modèle du <see cref="MinerEnemy"/>.
/// Cycle : rôde près de son point, voit Brann à moins de <see cref="DetectionRadius"/> avec une ligne dégagée, le poursuit
/// (bouclier tourné vers lui avec un temps de réaction), puis à portée : annonce (<see cref="WindupTime"/>), deux coups
/// espacés de <see cref="StrikeInterval"/>, et récupération (<see cref="RecoveryTime"/>) bouclier baissé, vulnérable de partout.
/// Le bouclier (<see cref="HurtBox.BlockFilter"/>) bloque épée et flèches venues de face, jamais de côté ni de dos.
/// Une bombe à portée (<see cref="IBombDestructible"/>) le fait tomber <see cref="StunDuration"/> secondes (souffle sans dégât).
/// Dégâts (1 PV = un demi-cœur) : contact = HitBox « HitBox », coups d'épée = HitBox « CoupHitBox » (Damage réglé dans la scène).
/// </summary>
public partial class ChevalierEnemy : CharacterBody2D, IBombDestructible
{
    private enum State { Rode, Poursuite, Annonce, Frappe, Recuperation, Etourdi }

    [ExportGroup("Mouvement")]
    [Export] public float WanderSpeed { get; set; } = 36f;
    /// <summary>Distance maximale (px) de son point de départ en rôdant.</summary>
    [Export] public float WanderRadius { get; set; } = 64f;
    [Export] public float ChaseSpeed { get; set; } = 64f;
    [Export] public float DetectionRadius { get; set; } = 160f;
    [Export] public float MinWanderTime { get; set; } = 1.2f;
    [Export] public float MaxWanderTime { get; set; } = 2.6f;

    [ExportGroup("Bouclier")]
    /// <summary>Cosinus minimal entre le regard et la direction du coup pour qu'il soit bloqué (0.5 = 60° de chaque côté).</summary>
    [Export(PropertyHint.Range, "-1,1,0.05")] public float BlockCosine { get; set; } = 0.5f;
    /// <summary>Délai (s) entre deux changements de direction du bouclier quand il suit Brann.</summary>
    [Export] public float TurnDelay { get; set; } = 0.6f;

    [ExportGroup("Attaque")]
    /// <summary>Distance (px, centre à centre) à laquelle il s'arrête pour frapper.</summary>
    [Export] public float AttackRange { get; set; } = 40f;
    [Export] public float WindupTime { get; set; } = 0.6f;
    [Export] public int StrikeCount { get; set; } = 2;
    [Export] public float StrikeInterval { get; set; } = 0.45f;
    /// <summary>Durée (s) pendant laquelle la zone de coup est active à chaque coup.</summary>
    [Export] public float StrikeActiveTime { get; set; } = 0.15f;
    /// <summary>Portée (px) de la zone de coup, mesurée depuis le bord du corps.</summary>
    [Export] public float StrikeReach { get; set; } = 24f;
    [Export] public float StrikeWidth { get; set; } = 30f;
    [Export] public float RecoveryTime { get; set; } = 1.2f;

    [ExportGroup("Chute")]
    [Export] public float StunDuration { get; set; } = 4f;
    /// <summary>Après l'explosion, durée (s) pendant laquelle le souffle de la bombe ne le blesse pas.</summary>
    [Export] public float BlastGrace { get; set; } = 0.3f;
    [Export] public float BlastKnockback { get; set; } = 120f;

    [ExportGroup("Recul")]
    [Export] public float KnockbackSpeed { get; set; } = 90f;
    [Export] public float KnockbackDuration { get; set; } = 0.1f;

    private const float BodyRadius = 11f;
    private static readonly StringName PlayerGroup = "player";
    private static readonly NodePath ModulateProp = "modulate";
    private static readonly Vector2[] Dirs = { Vector2.Down, Vector2.Up, Vector2.Left, Vector2.Right };
    private static readonly string[] DirNames = { "down", "up", "left", "right" };
    private static readonly Color WindupColor = new(1.7f, 0.55f, 0.55f);
    private static readonly Color RecoveryColor = new(1f, 1f, 0.7f);
    private static PackedScene _deathScene;

    // Animations par direction (ordre de Dirs). Les animations facultatives retombent sur idle_* / walk_* :
    // windup_* (annonce), attack_* (coup), recover_* (récupération), fallen_* (à terre).
    private readonly StringName[] _walk = new StringName[4];
    private readonly StringName[] _windup = new StringName[4];
    private readonly StringName[] _attack = new StringName[4];
    private readonly StringName[] _recover = new StringName[4];
    private readonly StringName[] _fallen = new StringName[4];

    private readonly RandomNumberGenerator _rng = new();
    private readonly Godot.Collections.Array<Rid> _excluded = new();
    private State _state = State.Rode;
    private int _facing;
    private Vector2 _home;
    private Vector2 _wanderDir;
    private Vector2 _knockback;
    private float _knockTimer;
    private float _timer;
    private float _turnTimer;
    private float _graceTimer;
    private float _losTimer;
    private float _strikeActiveTimer;
    private int _strikesDone;

    private AnimatedSprite2D _sprite;
    private HurtBox _hurtBox;
    private HitBox _contactBox;
    private HitBox _strikeBox;
    private CollisionShape2D _strikeShapeNode;
    private RectangleShape2D _strikeShape;
    private Health _health;
    private Node2D _player;
    private Tween _flashTween;
    private bool _dead;

    /// <summary>Vrai tant que le chevalier est à terre (vulnérable de partout).</summary>
    public bool IsStunned => _state == State.Etourdi;

    /// <summary>Vrai quand le bouclier est baissé (récupération ou chute) : fenêtre pour frapper de face.</summary>
    public bool IsOpen => _state == State.Recuperation || _state == State.Etourdi;

    public Vector2 BombHalfExtents => new(11f, 15f);

    public override void _EnterTree() => Bomb.Register(this);

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _hurtBox.BlockFilter = ShieldBlocks;
        _hurtBox.Blocked += OnBlocked;
        _hurtBox.Hit += OnHit;
        _contactBox = GetNode<HitBox>("HitBox");
        _strikeBox = GetNode<HitBox>("CoupHitBox");
        _strikeShapeNode = _strikeBox.GetNode<CollisionShape2D>("CollisionShape2D");
        _strikeShape = (RectangleShape2D)_strikeShapeNode.Shape;
        _strikeBox.Monitoring = false;
        _health = GetNode<Health>("Health");
        _health.Died += OnDied;

        for (int i = 0; i < 4; i++)
        {
            StringName idle = "idle_" + DirNames[i];
            _walk[i] = FirstExisting("walk_" + DirNames[i], idle);
            _windup[i] = FirstExisting("windup_" + DirNames[i], idle);
            _attack[i] = FirstExisting("attack_" + DirNames[i], _windup[i]);
            _recover[i] = FirstExisting("recover_" + DirNames[i], idle);
            _fallen[i] = FirstExisting("fallen_" + DirNames[i], idle);
        }

        _rng.Randomize();
        _home = GlobalPosition;
        PickWanderDirection();
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
        if (_losTimer > 0f) _losTimer -= dt;
        _timer -= dt;
        if (_strikeActiveTimer > 0f)
        {
            _strikeActiveTimer -= dt;
            if (_strikeActiveTimer <= 0f) _strikeBox.SetDeferred(Area2D.PropertyName.Monitoring, false);
        }

        switch (_state)
        {
            case State.Rode:
                UpdateWander(dt);
                break;
            case State.Poursuite:
                UpdateChase(dt);
                break;
            case State.Annonce:
                Move(Vector2.Zero, dt);
                if (_timer <= 0f) EnterState(State.Frappe, 0f);
                break;
            case State.Frappe:
                Move(Vector2.Zero, dt);
                UpdateStrikes();
                break;
            case State.Recuperation:
                Move(Vector2.Zero, dt);
                if (_timer <= 0f) EnterState(State.Poursuite, 0f);
                break;
            case State.Etourdi:
                Move(Vector2.Zero, dt);
                if (_timer <= 0f) GetUp();
                break;
        }
    }

    // Déplacement unique : la vitesse voulue plus la poussée d'un coup reçu (qui s'estompe), sans changer d'état.
    private void Move(Vector2 wanted, float dt)
    {
        if (_knockTimer > 0f)
        {
            _knockTimer -= dt;
            wanted += _knockback;
        }
        Velocity = wanted;
        if (wanted != Vector2.Zero) MoveAndSlide();
    }

    private void UpdateWander(float dt)
    {
        if (_timer <= 0f) PickWanderDirection();
        Move(_wanderDir * WanderSpeed, dt);
        if (_losTimer <= 0f && TryGetPlayer(out var p)
            && p.GlobalPosition.DistanceSquaredTo(GlobalPosition) <= DetectionRadius * DetectionRadius)
        {
            _losTimer = 0.3f; // pas de rayon à chaque image
            if (HasLineOfSight(GlobalPosition, p.GlobalPosition)) EnterState(State.Poursuite, 0f);
        }
    }

    private void UpdateChase(float dt)
    {
        if (!TryGetPlayer(out var p) || GlobalPosition.DistanceSquaredTo(p.GlobalPosition) > DetectionRadius * DetectionRadius * 2.25f)
        {
            EnterState(State.Rode, 0f);
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
                PlayAnim();
            }
            _turnTimer = TurnDelay;
        }
        var toPlayer = p.GlobalPosition - GlobalPosition;
        if (toPlayer.LengthSquared() <= AttackRange * AttackRange)
        {
            _facing = CardinalToward(toPlayer); // il se fige face à Brann pour la série
            EnterState(State.Annonce, WindupTime);
            return;
        }
        Move(toPlayer.Normalized() * ChaseSpeed, dt);
    }

    private void UpdateStrikes()
    {
        if (_timer > 0f) return;
        if (_strikesDone >= StrikeCount)
        {
            EnterState(State.Recuperation, RecoveryTime);
            return;
        }
        Strike();
        _strikesDone++;
        _timer = _strikesDone >= StrikeCount ? StrikeActiveTime + 0.1f : StrikeInterval;
    }

    // Zone de coup devant lui, dans la direction du bouclier ; active StrikeActiveTime secondes.
    private void Strike()
    {
        bool horizontal = _facing >= 2;
        _strikeShape.Size = horizontal ? new Vector2(StrikeReach, StrikeWidth) : new Vector2(StrikeWidth, StrikeReach);
        _strikeShapeNode.Position = Dirs[_facing] * (BodyRadius + StrikeReach * 0.5f) + new Vector2(0f, 4f);
        _strikeBox.SetDeferred(Area2D.PropertyName.Monitoring, true);
        _strikeActiveTimer = StrikeActiveTime;
        _sprite.Play(_attack[_facing]);
        AudioManager.PlayAt(Sfx.Epee, GlobalPosition);
    }

    // Filtre du HurtBox : vrai = coup bloqué. La position reçue est celle du corps attaquant (Brann), ou de la HitBox pour une flèche.
    private bool ShieldBlocks(Vector2 fromPosition)
    {
        if (_dead) return false;
        if (_graceTimer > 0f) return true; // souffle de la bombe : il tombe, mais n'est pas blessé
        if (IsOpen) return false;
        var toAttacker = (fromPosition - _hurtBox.GlobalPosition).Normalized();
        return Dirs[_facing].Dot(toAttacker) >= BlockCosine;
    }

    private void OnBlocked(int damage, Vector2 fromPosition)
    {
        if (_graceTimer > 0f) return; // simple souffle : pas d'étincelle de bouclier
        AudioManager.PlayAt(Sfx.FlecheImpact, fromPosition);
        _flashTween?.Kill();
        _sprite.Modulate = new Color(0.3f, 0.6f, 3f);
        _flashTween = CreateTween();
        _flashTween.TweenProperty(_sprite, ModulateProp, StateColor(_state), 0.25f);
    }

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_dead || _state == State.Etourdi) return; // à terre : il ne bouge pas sous les coups
        _knockback = (GlobalPosition - fromPosition).Normalized() * KnockbackSpeed;
        _knockTimer = KnockbackDuration;
    }

    /// <summary>Une bombe explose : s'il est à portée, le chevalier tombe.</summary>
    public void OnBombExplosion(Vector2 center)
    {
        if (_dead) return;
        _graceTimer = BlastGrace;
        _knockback = (GlobalPosition - center).Normalized() * BlastKnockback;
        _knockTimer = KnockbackDuration * 2f;
        EnterState(State.Etourdi, StunDuration);
        AudioManager.PlayAt(Sfx.BossAssomme, GlobalPosition);
    }

    private void GetUp()
    {
        _sprite.RotationDegrees = 0f;
        _sprite.Position = Vector2.Zero;
        EnterState(State.Poursuite, 0f);
    }

    private void EnterState(State state, float duration)
    {
        // Le bouclier se retourne aussitôt en reprenant la chasse depuis le repos, la chute ou la fatigue.
        if (state == State.Poursuite) _turnTimer = 0f;
        var previous = _state;
        _state = state;
        _timer = duration;
        _flashTween?.Kill();
        _sprite.Modulate = StateColor(state);

        // Les coups en cours s'arrêtent si on quitte la série (étourdi pendant un coup).
        if (state != State.Frappe && _strikeActiveTimer > 0f)
        {
            _strikeActiveTimer = 0f;
            _strikeBox.SetDeferred(Area2D.PropertyName.Monitoring, false);
        }
        if (state == State.Frappe) _strikesDone = 0;
        if (state == State.Etourdi)
        {
            _sprite.RotationDegrees = _facing == 2 ? -90f : 90f;
            _sprite.Position = new Vector2(0f, 6f);
            _contactBox.SetDeferred(Area2D.PropertyName.Monitoring, false);
        }
        else if (previous == State.Etourdi)
        {
            _contactBox.SetDeferred(Area2D.PropertyName.Monitoring, true);
        }
        if (state != State.Frappe) PlayAnim();
    }

    private static Color StateColor(State state) =>
        state == State.Annonce || state == State.Frappe ? WindupColor : state == State.Recuperation ? RecoveryColor : Colors.White;

    private void PlayAnim()
    {
        switch (_state)
        {
            case State.Annonce: _sprite.Play(_windup[_facing]); break;
            case State.Recuperation: _sprite.Play(_recover[_facing]); break;
            case State.Etourdi: _sprite.Play(_fallen[_facing]); break;
            case State.Frappe: _sprite.Play(_attack[_facing]); break;
            default: _sprite.Play(_walk[_facing]); break;
        }
    }

    private StringName FirstExisting(string wanted, StringName fallback)
    {
        var frames = _sprite.SpriteFrames;
        return frames != null && frames.HasAnimation(wanted) ? wanted : fallback;
    }

    private bool TryGetPlayer(out Node2D player)
    {
        if (_player == null || !IsInstanceValid(_player))
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Node2D;
        player = _player;
        return player != null && player is not Player { IsDead: true };
    }

    // Rayon physique couche 1 vers Brann ; les CharacterBody2D (Brann, ennemis) sont ignorés. Lancé à 3 Hz au plus.
    private bool HasLineOfSight(Vector2 from, Vector2 to)
    {
        var space = GetWorld2D().DirectSpaceState;
        var query = PhysicsRayQueryParameters2D.Create(from, to, 1);
        _excluded.Clear();
        _excluded.Add(GetRid());
        for (int i = 0; i < 6; i++)
        {
            query.Exclude = _excluded; // Exclude renvoie une copie : on réassigne la liste à chaque tour
            var hit = space.IntersectRay(query);
            if (hit.Count == 0) return true;
            if (hit["collider"].AsGodotObject() is CharacterBody2D body)
            {
                _excluded.Add(body.GetRid());
                continue;
            }
            return false;
        }
        return false;
    }

    private static int CardinalToward(Vector2 v)
    {
        if (Mathf.Abs(v.X) > Mathf.Abs(v.Y)) return v.X < 0f ? 2 : 3;
        return v.Y < 0f ? 1 : 0;
    }

    private void PickWanderDirection()
    {
        _timer = _rng.RandfRange(MinWanderTime, MaxWanderTime);
        var fromHome = GlobalPosition - _home;
        _wanderDir = fromHome.LengthSquared() > WanderRadius * WanderRadius
            ? -fromHome.Normalized()
            : Vector2.Right.Rotated(_rng.RandfRange(0f, Mathf.Tau));
        _facing = CardinalToward(_wanderDir);
        PlayAnim();
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
