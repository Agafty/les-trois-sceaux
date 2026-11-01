using Godot;

/// <summary>
/// Crabe-armure : ennemi « Chasseur » du Sanctuaire Englouti. Il erre ; quand Brann est proche ET aligné avec lui
/// (même ligne ou même colonne), il annonce puis charge en ligne droite. Pendant la charge sa carapace bloque
/// l'épée et les flèches (<see cref="HurtBox.BlockFilter"/> : signal Blocked, éclat bleu, aucun dégât).
/// Contre un mur ou un pilier il s'étourdit (<see cref="StunDuration"/> s) : on peut le frapper. Hors charge il est
/// vulnérable de partout. Une bombe le blesse même pendant la charge (court créneau sans blocage après l'explosion).
/// </summary>
public partial class CrabeArmureEnemy : CharacterBody2D, IBombDestructible
{
    private enum State { Errance, Annonce, Charge, Etourdi, Pause, Recul }

    [ExportGroup("Errance")]
    [Export] public float WanderSpeed { get; set; } = 24f;
    [Export] public float MinWanderTime { get; set; } = 1.0f;
    [Export] public float MaxWanderTime { get; set; } = 2.5f;

    [ExportGroup("Charge")]
    /// <summary>Distance maximale (px) à laquelle Brann déclenche la charge.</summary>
    [Export] public float DetectionRadius { get; set; } = 150f;
    /// <summary>Écart latéral maximal (px) pour être « aligné » avec Brann.</summary>
    [Export] public float AlignTolerance { get; set; } = 18f;
    [Export] public float WindupDuration { get; set; } = 0.5f;
    [Export] public float WindupShake { get; set; } = 1.5f;
    [Export] public float ChargeSpeed { get; set; } = 140f;
    [Export] public float ChargeMaxDuration { get; set; } = 1.3f;
    [Export] public float StunDuration { get; set; } = 1.2f;
    [Export] public float PauseDuration { get; set; } = 0.4f;
    [Export] public float Cooldown { get; set; } = 1.2f;

    [ExportGroup("Recul")]
    [Export] public float KnockbackSpeed { get; set; } = 150f;
    [Export] public float KnockbackDuration { get; set; } = 0.15f;
    /// <summary>Après une explosion, durée (s) pendant laquelle la carapace ne bloque pas (le souffle le blesse).</summary>
    [Export] public float BlastWindow { get; set; } = 0.25f;

    private const string ChargeTexture = "res://art/enemies/crabe_armure_charge.png";
    private const string ChargeTextureRed = "res://art/enemies/crabe_armure_red_charge.png";
    private static readonly NodePath ModulateProp = "modulate";
    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName[] MoveAnims = { "move_down", "move_up", "move_left", "move_right" };
    private static readonly StringName[] ChargeAnims = { "charge_down", "charge_up", "charge_left", "charge_right" };
    private static readonly Vector2[] Dirs = { Vector2.Down, Vector2.Up, Vector2.Left, Vector2.Right };
    private static PackedScene _deathScene;

    private readonly RandomNumberGenerator _rng = new();
    private State _state = State.Errance;
    private int _facing; // index dans Dirs
    private Vector2 _wanderDir;
    private Vector2 _knockback;
    private float _timer;
    private float _cooldownTimer;
    private float _blastTimer;
    private float _losTimer;
    private bool _hasChargeAnims;
    private Tween _flashTween;

    private AnimatedSprite2D _sprite;
    private HurtBox _hurtBox;
    private Health _health;
    private Node2D _player;
    private bool _dead;

    /// <summary>Vrai pendant la charge (carapace fermée : les coups sont bloqués).</summary>
    public bool IsCharging => _state == State.Charge;
    /// <summary>Vrai tant que le crabe est étourdi après s'être cogné.</summary>
    public bool IsStunned => _state == State.Etourdi;

    public Vector2 BombHalfExtents => new(14f, 14f);

    public override void _EnterTree() => Bomb.Register(this);

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _hurtBox = GetNode<HurtBox>("HurtBox");
        _hurtBox.BlockFilter = ShellBlocks;
        _hurtBox.Blocked += OnBlocked;
        _hurtBox.Hit += OnHit;
        _health = GetNode<Health>("Health");
        _health.Died += OnDied;

        _hasChargeAnims = EnsureChargeAnimations(_sprite.SpriteFrames);
        _rng.Randomize();
        PickWanderDirection();
    }

    public override void _ExitTree()
    {
        Bomb.Unregister(this);
        _flashTween?.Kill();
        if (_hurtBox != null)
        {
            _hurtBox.BlockFilter = null;
            _hurtBox.Blocked -= OnBlocked;
            _hurtBox.Hit -= OnHit;
        }
        if (_health != null) _health.Died -= OnDied;
    }

    // Les animations de charge viennent de art/enemies/crabe_armure_charge.png (64x128 : 2 images x 4 directions, ordre bas/haut/gauche/droite).
    // Elles sont ajoutées une fois aux SpriteFrames (ressource partagée, jamais enregistrée) car le .tres est dans art/.
    // La variante rouge a sa planche art/enemies/crabe_armure_red_charge.png ; sans fichier, repli sur la marche accélérée.
    private static bool EnsureChargeAnimations(SpriteFrames frames)
    {
        if (frames == null) return false;
        if (frames.HasAnimation(ChargeAnims[0])) return true;
        string path = frames.ResourcePath.Contains("_red") ? ChargeTextureRed : ChargeTexture;
        if (!ResourceLoader.Exists(path)) return false;
        var tex = GD.Load<Texture2D>(path);
        if (tex == null) return false;
        for (int d = 0; d < 4; d++)
        {
            frames.AddAnimation(ChargeAnims[d]);
            frames.SetAnimationSpeed(ChargeAnims[d], 10f);
            frames.SetAnimationLoop(ChargeAnims[d], true);
            for (int f = 0; f < 2; f++)
            {
                var atlas = new AtlasTexture { Atlas = tex, Region = new Rect2(f * 32, d * 32, 32, 32) };
                frames.AddFrame(ChargeAnims[d], atlas);
            }
        }
        return true;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_dead) return;
        float dt = (float)delta;
        if (_cooldownTimer > 0f) _cooldownTimer -= dt;
        if (_blastTimer > 0f) _blastTimer -= dt;
        if (_losTimer > 0f) _losTimer -= dt;

        switch (_state)
        {
            case State.Errance: UpdateWander(dt); break;
            case State.Annonce: UpdateWindup(dt); break;
            case State.Charge: UpdateCharge(dt); break;
            case State.Etourdi: UpdateStun(dt); break;
            case State.Pause: UpdateTimed(dt); break;
            case State.Recul: UpdateKnockback(dt); break;
        }
    }

    private void UpdateWander(float dt)
    {
        _timer -= dt;
        if (_timer <= 0f || HitSolidWall()) PickWanderDirection();

        Velocity = _wanderDir * WanderSpeed;
        MoveAndSlide();

        if (_cooldownTimer <= 0f && TryGetAlignedFacing(out int facing))
        {
            _facing = facing;
            EnterState(State.Annonce, WindupDuration);
        }
    }

    private void UpdateWindup(float dt)
    {
        _timer -= dt;
        _sprite.Position = new Vector2(_rng.RandfRange(-WindupShake, WindupShake), 0f); // tremblement : la charge est annoncée
        if (_timer <= 0f)
        {
            // Direction verrouillée au départ : jamais corrigée ensuite.
            if (!TryGetPlayer(out var p))
            {
                // Brann n'est plus là (mort, parti) : pas de charge dans le vide, retour à l'errance.
                _cooldownTimer = Cooldown;
                EnterState(State.Errance, 0f);
                PickWanderDirection();
                return;
            }
            _facing = CardinalToward(p.GlobalPosition - GlobalPosition);
            EnterState(State.Charge, ChargeMaxDuration);
        }
    }

    private void UpdateCharge(float dt)
    {
        _timer -= dt;
        Velocity = Dirs[_facing] * ChargeSpeed;
        MoveAndSlide();

        if (HitFrontWall())
        {
            AudioManager.PlayAt(Sfx.BossAssomme, GlobalPosition);
            EnterState(State.Etourdi, StunDuration);
        }
        else if (_timer <= 0f || HitBody())
            // Fin de charge : durée écoulée, ou contre Brann / un autre ennemi (pas d'étourdissement).
            EnterState(State.Pause, PauseDuration);
    }

    private void UpdateStun(float dt)
    {
        _timer -= dt;
        Velocity = Vector2.Zero;
        if (_timer <= 0f)
        {
            _cooldownTimer = Cooldown;
            EnterState(State.Errance, 0f);
            PickWanderDirection();
        }
    }

    private void UpdateTimed(float dt)
    {
        _timer -= dt;
        if (_timer <= 0f)
        {
            EnterState(State.Errance, 0f);
            PickWanderDirection();
        }
    }

    private void UpdateKnockback(float dt)
    {
        _timer -= dt;
        Velocity = _knockback;
        MoveAndSlide();
        if (_timer <= 0f)
        {
            EnterState(State.Errance, 0f);
            PickWanderDirection();
        }
    }

    private void EnterState(State state, float duration)
    {
        _state = state;
        _timer = duration;
        _sprite.Position = Vector2.Zero;
        if (state == State.Pause) _cooldownTimer = Cooldown + duration;

        switch (state)
        {
            case State.Charge:
                _sprite.Play(_hasChargeAnims ? ChargeAnims[_facing] : MoveAnims[_facing]);
                _sprite.SpeedScale = _hasChargeAnims ? 1f : 2f;
                break;
            case State.Etourdi:
                _sprite.SpeedScale = 1f;
                _sprite.Play(MoveAnims[_facing]);
                _sprite.Pause(); // immobile : lisible comme « étourdi »
                Velocity = Vector2.Zero;
                break;
            default:
                _sprite.SpeedScale = 1f;
                _sprite.Play(MoveAnims[_facing]);
                break;
        }
    }

    // Les autres corps (Brann, ennemis) ne comptent pas : seul un mur, un pilier ou une porte étourdit.
    private bool HitSolidWall()
    {
        int count = GetSlideCollisionCount();
        for (int i = 0; i < count; i++)
        {
            if (GetSlideCollision(i).GetCollider() is not CharacterBody2D)
                return true;
        }
        return false;
    }

    // Choc de face seulement : la normale de la collision s'oppose à la direction de charge (seuil -0,8 : pas d'étourdissement en frôlant un mur ou en mordant 2-3 px sur l'arête d'un pilier).
    private bool HitFrontWall()
    {
        int count = GetSlideCollisionCount();
        var dir = Dirs[_facing];
        for (int i = 0; i < count; i++)
        {
            var c = GetSlideCollision(i);
            if (c.GetCollider() is not CharacterBody2D && c.GetNormal().Dot(dir) < -0.8f)
                return true;
        }
        return false;
    }

    private bool HitBody()
    {
        int count = GetSlideCollisionCount();
        for (int i = 0; i < count; i++)
        {
            if (GetSlideCollision(i).GetCollider() is CharacterBody2D)
                return true;
        }
        return false;
    }

    // Brann est proche et aligné sur une ligne/colonne : renvoie la direction cardinale de la charge.
    private bool TryGetAlignedFacing(out int facing)
    {
        facing = 0;
        if (!TryGetPlayer(out var p)) return false;
        var d = p.GlobalPosition - GlobalPosition;
        if (d.LengthSquared() > DetectionRadius * DetectionRadius) return false;
        if (Mathf.Min(Mathf.Abs(d.X), Mathf.Abs(d.Y)) > AlignTolerance) return false;
        if (_losTimer > 0f) return false;
        if (!HasLineOfSight(GlobalPosition, p.GlobalPosition))
        {
            _losTimer = 0.3f; // pas de rayon à chaque image tant que Brann est derrière un mur
            return false;
        }
        facing = CardinalToward(d);
        return true;
    }

    // Rayon physique couche 1 vers Brann ; les CharacterBody2D (Brann, ennemis) sont ignorés. Lancé seulement quand les autres conditions sont remplies.
    private bool HasLineOfSight(Vector2 from, Vector2 to)
    {
        var space = GetWorld2D().DirectSpaceState;
        var query = PhysicsRayQueryParameters2D.Create(from, to, 1);
        var excluded = new Godot.Collections.Array<Rid> { GetRid() };
        for (int i = 0; i < 6; i++)
        {
            query.Exclude = excluded;
            var hit = space.IntersectRay(query);
            if (hit.Count == 0) return true;
            if (hit["collider"].AsGodotObject() is CharacterBody2D body)
            {
                excluded.Add(body.GetRid()); // Exclude renvoie une copie : on réassigne la liste à chaque tour
                continue;
            }
            return false;
        }
        return false;
    }

    // Filtre du HurtBox : vrai = coup bloqué (uniquement pendant la charge, hors souffle de bombe).
    private bool ShellBlocks(Vector2 attackerPosition) => !_dead && _state == State.Charge && _blastTimer <= 0f;

    private void OnBlocked(int damage, Vector2 fromPosition)
    {
        AudioManager.PlayAt(Sfx.FlecheImpact, fromPosition);
        _sprite.Modulate = new Color(0.3f, 0.6f, 3f);
        _flashTween?.Kill();
        _flashTween = CreateTween();
        _flashTween.TweenProperty(_sprite, ModulateProp, Colors.White, 0.25f);
    }

    private void OnHit(int damage, Vector2 fromPosition)
    {
        if (_dead) return;
        _knockback = (GlobalPosition - fromPosition).Normalized() * KnockbackSpeed;
        _cooldownTimer = Cooldown;
        EnterState(State.Recul, KnockbackDuration);
    }

    /// <summary>Une bombe explose à portée : la carapace ne bloque pas le souffle qui arrive à l'image suivante.</summary>
    public void OnBombExplosion(Vector2 center) => _blastTimer = BlastWindow;

    private bool TryGetPlayer(out Node2D player)
    {
        if (_player == null || !IsInstanceValid(_player))
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Node2D;
        player = _player;
        return player != null && player is not Player { IsDead: true };
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
        _sprite.Play(MoveAnims[_facing]);
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
