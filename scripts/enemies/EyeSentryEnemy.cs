using Godot;

/// <summary>
/// Œil de Morvath : sentinelle immobile logée dans une case de mur (niche). Paupière fermée tant que Brann est loin ou hors de vue ;
/// à moins de <see cref="WakeRadius"/> avec une ligne dégagée, la paupière s'ouvre (<see cref="OpenDuration"/>, annonce),
/// puis il tire un orbe lent visé sur Brann toutes les <see cref="FireInterval"/> secondes.
/// <para>
/// Le corps ne bouge JAMAIS (aucun MoveAndSlide) et n'a aucune couche de collision : la physique ne le chasse donc pas du mur
/// où le point Tiled le place. L'orbe part du bord de la case, du côté libre (point testé une fois) qui regarde le mieux Brann,
/// car un projectile créé dans le mur disparaîtrait aussitôt. Sa HurtBox dépasse de la case de quelques pixels pour qu'une flèche
/// le touche avant que le mur ne l'arrête. 1 PV ; compte comme ennemi pour une porte « ennemis » (Health).
/// </para>
/// </summary>
public partial class EyeSentryEnemy : CharacterBody2D, IBombDestructible
{
    private enum State { Ferme, Ouverture, Eveille }

    [ExportGroup("Détection")]
    /// <summary>Distance (px) à laquelle la paupière s'ouvre : 8 cases.</summary>
    [Export] public float WakeRadius { get; set; } = 256f;
    [Export] public float OpenDuration { get; set; } = 0.8f;
    /// <summary>Intervalle (s) entre deux contrôles de la ligne de vue.</summary>
    [Export] public float SightInterval { get; set; } = 0.25f;

    [ExportGroup("Tir")]
    [Export] public PackedScene ProjectileScene { get; set; }
    [Export] public float FireInterval { get; set; } = 2.5f;
    /// <summary>Délai (s) entre l'ouverture complète de la paupière et le premier tir.</summary>
    [Export] public float FirstShotDelay { get; set; } = 0.4f;
    /// <summary>Distance (px) du centre du corps au point de départ de l'orbe (le demi-côté d'une case est 16).</summary>
    [Export] public float SpawnClearance { get; set; } = 21f;

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName AnimClosed = "closed";
    private static readonly StringName AnimOpen = "open";
    private static readonly StringName AnimIdleOpen = "idle_open";
    private static readonly StringName AnimShoot = "shoot";
    private static readonly Vector2[] Sides = { Vector2.Down, Vector2.Up, Vector2.Left, Vector2.Right };
    private static PackedScene _deathScene;

    private readonly bool[] _sideOpen = new bool[4];
    private readonly Godot.Collections.Array<Rid> _excluded = new();
    private State _state = State.Ferme;
    private float _timer;
    private float _sightTimer;
    private float _fireTimer;
    private bool _sidesChecked;
    private int _physicsFrames;
    private bool _anySide;
    private bool _dead;

    private AnimatedSprite2D _sprite;
    private Health _health;
    private Node2D _player;

    public Vector2 BombHalfExtents => new(16f, 16f);

    public override void _EnterTree() => Bomb.Register(this);

    /// <summary>Une explosion à portée le détruit (dégâts mortels via Health).</summary>
    public void OnBombExplosion(Vector2 center)
    {
        if (!_dead) _health?.Damage(_health.CurrentHealth);
    }

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        _health = GetNode<Health>("Health");
        _health.Died += OnDied;
        _sprite.AnimationFinished += OnAnimationFinished;
        _sprite.Play(AnimClosed);
    }

    public override void _ExitTree()
    {
        Bomb.Unregister(this);
        if (_health != null) _health.Died -= OnDied;
        if (_sprite != null) _sprite.AnimationFinished -= OnAnimationFinished;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_dead) return;
        // Les tuiles de mur ne sont enregistrées qu'après quelques tours de physique : test au 3e tour.
        if (!_sidesChecked && ++_physicsFrames >= 3) CheckOpenSides();
        if (!_sidesChecked) return;
        if (!_anySide) return;
        float dt = (float)delta;

        switch (_state)
        {
            case State.Ferme:
                _sightTimer -= dt;
                if (_sightTimer > 0f) break;
                _sightTimer = SightInterval;
                if (CanShoot(out _, out _)) EnterOpening();
                break;

            case State.Ouverture:
                _timer -= dt;
                if (_timer <= 0f)
                {
                    _state = State.Eveille;
                    _fireTimer = FirstShotDelay;
                    _sightTimer = SightInterval;
                    _sprite.Play(AnimIdleOpen);
                }
                break;

            case State.Eveille:
                _fireTimer -= dt;
                _sightTimer -= dt;
                if (_fireTimer > 0f) break;
                if (CanShoot(out var origin, out var direction))
                {
                    Fire(origin, direction);
                    _fireTimer = FireInterval;
                }
                else
                {
                    // Brann est parti ou caché : la paupière se referme.
                    _state = State.Ferme;
                    _sightTimer = SightInterval;
                    _sprite.Play(AnimClosed);
                }
                break;
        }
    }

    // Teste une fois quelles faces de la case sont libres (aucun mur à 24 px du centre). Sans face libre : l'œil ne tire pas.
    private void CheckOpenSides()
    {
        _sidesChecked = true;
        var space = GetWorld2D().DirectSpaceState;
        var query = new PhysicsPointQueryParameters2D { CollisionMask = 1 };
        _excluded.Clear();
        _excluded.Add(GetRid());
        query.Exclude = _excluded;
        for (int i = 0; i < 4; i++)
        {
            query.Position = GlobalPosition + Sides[i] * 24f;
            _sideOpen[i] = space.IntersectPoint(query, 1).Count == 0;
            _anySide |= _sideOpen[i];
        }
        if (!_anySide) GD.PushWarning($"Œil de Morvath en {GlobalPosition} : aucune face libre autour de sa case, il ne tirera pas.");
    }

    private void EnterOpening()
    {
        _state = State.Ouverture;
        _timer = OpenDuration;
        _sprite.Play(AnimOpen);
    }

    private void Fire(Vector2 origin, Vector2 direction)
    {
        _sprite.Play(AnimShoot);
        if (ProjectileScene == null) return;
        var orb = ProjectileScene.Instantiate<Projectile>();
        orb.Launch(direction);
        // Ajouté au parent : l'orbe survit à la mort de l'œil.
        GetParent().AddChild(orb);
        orb.GlobalPosition = origin;
    }

    // Brann à portée, vivant, et une face libre qui le regarde avec une ligne dégagée depuis le point de départ de l'orbe.
    private bool CanShoot(out Vector2 origin, out Vector2 direction)
    {
        origin = GlobalPosition;
        direction = Vector2.Down;
        if (!TryGetPlayer(out var p)) return false;
        var toPlayer = p.GlobalPosition - GlobalPosition;
        if (toPlayer.LengthSquared() > WakeRadius * WakeRadius) return false;

        var wanted = toPlayer.Normalized();
        int best = -1;
        float bestDot = 0.2f; // au moins ~78° de la normale de la face
        for (int i = 0; i < 4; i++)
        {
            if (!_sideOpen[i]) continue;
            float dot = Sides[i].Dot(wanted);
            if (dot > bestDot) { bestDot = dot; best = i; }
        }
        if (best < 0) return false;

        origin = GlobalPosition + Sides[best] * SpawnClearance;
        direction = (p.GlobalPosition - origin).Normalized();
        return HasLineOfSight(origin, p.GlobalPosition);
    }

    // Rayon physique couche 1 ; les CharacterBody2D (Brann, ennemis) sont ignorés. Appelé à 4 Hz au plus (ou à chaque tir).
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

    private void OnAnimationFinished()
    {
        // Le tir est une animation courte non bouclée : l'œil reste ensuite ouvert.
        if (!_dead && _state == State.Eveille && _sprite.Animation == AnimShoot) _sprite.Play(AnimIdleOpen);
    }

    private bool TryGetPlayer(out Node2D player)
    {
        if (_player == null || !IsInstanceValid(_player))
            _player = GetTree().GetFirstNodeInGroup(PlayerGroup) as Node2D;
        player = _player;
        return player != null && player is not Player { IsDead: true };
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
