using Godot;

/// <summary>
/// Bombe posée par Brann : mèche qui clignote, puis explosion circulaire qui blesse ennemis ET joueur
/// (deux HitBox de camps opposés, car une HitBox ne blesse que le camp adverse) et prévient
/// les nœuds du groupe "destructible_bombe" à portée.
/// </summary>
public partial class Bomb : ItemUse
{
    public static readonly StringName DestructibleGroup = "destructible_bombe";

    [Export(PropertyHint.Range, "0.2,5,0.1")] public float FuseTime { get; set; } = 1.5f;
    [Export(PropertyHint.Range, "8,120,1")] public float ExplosionRadius { get; set; } = 40f;
    /// <summary>Dégâts aux ennemis (1 PV = un demi-cœur).</summary>
    [Export(PropertyHint.Range, "0,10,1")] public int EnemyDamage { get; set; } = 3;
    /// <summary>Dégâts au joueur : 1 = un demi-cœur seulement.</summary>
    [Export(PropertyHint.Range, "0,10,1")] public int PlayerDamage { get; set; } = 1;
    /// <summary>Durée pendant laquelle l'explosion peut toucher (secondes).</summary>
    [Export] public float ExplosionActiveTime { get; set; } = 0.1f;
    /// <summary>Durée totale de l'effet visuel avant disparition.</summary>
    [Export] public float ExplosionVisualTime { get; set; } = 0.3f;
    /// <summary>Marge ajoutée au rayon pour les destructibles (leur position est leur centre, une tuile fait 32 px).</summary>
    [Export] public float DestructibleMargin { get; set; } = 16f;
    /// <summary>Clignotements par seconde au début / à la fin de la mèche.</summary>
    [Export] public float BlinkRateStart { get; set; } = 4f;
    [Export] public float BlinkRateEnd { get; set; } = 14f;

    private HitBox _hitBoxEnemies;
    private HitBox _hitBoxPlayer;
    private Sprite2D _sprite;
    private Sprite2D _explosion;
    private const int ExplosionFrames = 6;
    private float _age;
    private bool _exploded;
    private float _blinkPhase;

    public override void Begin(Player user, Vector2 direction)
    {
        // La bombe est posée là où le Player l'a placée ; seul le grésillement de la mèche démarre ici.
        AudioManager.PlayAt(Sfx.BombeMeche, GlobalPosition);
    }

    public override void _Ready()
    {
        _sprite = GetNode<Sprite2D>("Sprite");
        _explosion = GetNode<Sprite2D>("Explosion");
        _hitBoxEnemies = GetNode<HitBox>("HitBoxEnnemis");
        _hitBoxPlayer = GetNode<HitBox>("HitBoxJoueur");
        _hitBoxEnemies.Damage = EnemyDamage;
        _hitBoxPlayer.Damage = PlayerDamage;
        SetRadius(_hitBoxEnemies);
        SetRadius(_hitBoxPlayer);
    }

    // Une forme neuve par bombe (une seule fois, dans _Ready) : on ne modifie jamais la ressource partagée du .tscn.
    private void SetRadius(HitBox box)
    {
        box.GetNode<CollisionShape2D>("CollisionShape2D").Shape = new CircleShape2D { Radius = ExplosionRadius };
    }

    public override void _PhysicsProcess(double delta)
    {
        float dt = (float)delta;
        _age += dt;

        if (!_exploded)
        {
            // Le clignotement accélère : la fréquence monte de BlinkRateStart à BlinkRateEnd.
            float t = Mathf.Clamp(_age / FuseTime, 0f, 1f);
            _blinkPhase += Mathf.Lerp(BlinkRateStart, BlinkRateEnd, t) * dt;
            // Frames 0/1 : bombe normale (première moitié de la mèche) ; 2/3 : rouge / blanc crème (seconde moitié).
            _sprite.Frame = (t < 0.5f ? 0 : 2) + (int)(_blinkPhase * 2f) % 2;
            if (_age >= FuseTime) Explode();
            return;
        }

        float sinceBlast = _age - FuseTime;
        if (sinceBlast >= ExplosionActiveTime && _hitBoxEnemies.Monitoring)
        {
            _hitBoxEnemies.Monitoring = false;
            _hitBoxPlayer.Monitoring = false;
        }
        // Frames 0-3 : phase dangereuse ; 4-5 : dissipation. Réparties sur ExplosionVisualTime.
        _explosion.Frame = Mathf.Min((int)(sinceBlast / ExplosionVisualTime * ExplosionFrames), ExplosionFrames - 1);
        if (sinceBlast >= ExplosionVisualTime) QueueFree();
    }

    private void Explode()
    {
        _exploded = true;
        AudioManager.PlayAt(Sfx.BombeExplosion, GlobalPosition);
        _sprite.Visible = false;
        _explosion.Visible = true;
        _explosion.Frame = 0;
        // Monitoring est activé ici, dans _PhysicsProcess (et non dans un callback de signal, où il faudrait
        // SetDeferred). Les zones déjà superposées émettent AreaEntered au pas de physique suivant.
        _hitBoxEnemies.Monitoring = true;
        _hitBoxPlayer.Monitoring = true;

        float reach = ExplosionRadius + DestructibleMargin;
        float reachSq = reach * reach;
        foreach (var node in GetTree().GetNodesInGroup(DestructibleGroup))
        {
            if (node is IBombDestructible target && node is Node2D n2d
                && n2d.GlobalPosition.DistanceSquaredTo(GlobalPosition) <= reachSq)
                target.OnBombExplosion(GlobalPosition);
        }
    }
}
