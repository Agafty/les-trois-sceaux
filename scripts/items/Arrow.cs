using Godot;

/// <summary>
/// Flèche tirée par l'arc : vole en ligne droite dans la direction du regard, blesse les ennemis
/// (HitBox du camp Joueur : elle ne peut pas blesser Brann), prévient les nœuds du groupe
/// "cible_fleche" (IArrowTarget) et disparaît au premier impact ou après MaxDistance.
/// </summary>
public partial class Arrow : ItemUse
{
    public static readonly StringName TargetGroup = "cible_fleche";

    [Export(PropertyHint.Range, "50,800,10")] public float Speed { get; set; } = 300f;
    /// <summary>Dégâts aux ennemis (1 PV = un demi-cœur).</summary>
    [Export(PropertyHint.Range, "0,10,1")] public int Damage { get; set; } = 2;
    /// <summary>Distance maximale parcourue (pixels) avant disparition.</summary>
    [Export(PropertyHint.Range, "32,1000,8")] public float MaxDistance { get; set; } = 320f;

    /// <summary>La flèche est enflammée : elle l'est restée jusqu'à la fin de son vol et peut allumer une torche.</summary>
    public bool IsBurning => _burning;

    private const string BurningTexturePath = "res://art/items/fleche_enflammee.png";
    private const int FlameFrameSize = 32;
    private const float FlameFrameRate = 12f;
    private static Texture2D _burningTexture;

    private HitBox _hitBox;
    private Sprite2D _sprite;
    private bool _burning;
    private float _animTime;
    private Vector2 _direction = Vector2.Right;
    private float _travelled;
    private bool _done;

    public override void Begin(Player user, Vector2 direction)
    {
        _direction = direction;
        Rotation = direction.Angle(); // le sprite pointe vers la droite : on le tourne
        AudioManager.Play(Sfx.FlecheTir);
    }

    public override void _Ready()
    {
        _hitBox = GetNode<HitBox>("HitBox");
        _sprite = GetNodeOrNull<Sprite2D>("Sprite");
        _hitBox.Damage = Damage;
        // Le script HitBox blesse déjà les HurtBox ennemies ; on s'abonne en plus pour savoir quand la flèche a touché.
        _hitBox.HitLanded += Despawn;
        _hitBox.AreaEntered += OnAreaEntered;
        _hitBox.BodyEntered += OnBodyEntered;
    }

    public override void _ExitTree()
    {
        // Le HitBox est un enfant (libéré avec nous) : on se désabonne par propreté.
        _hitBox.HitLanded -= Despawn;
        _hitBox.AreaEntered -= OnAreaEntered;
        _hitBox.BodyEntered -= OnBodyEntered;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_done) return;
        float step = Speed * (float)delta;
        Position += _direction * step;
        _travelled += step;
        if (_burning && _sprite != null && _sprite.Hframes > 1)
        {
            _animTime += (float)delta;
            _sprite.Frame = (int)(_animTime * FlameFrameRate) % _sprite.Hframes;
        }
        if (_travelled >= MaxDistance) Despawn();
    }

    /// <summary>
    /// Enflamme la flèche pour le reste de son vol (sprite art/items/fleche_enflammee.png, 3 images en boucle ;
    /// à défaut, la flèche normale est teintée en orange). Sans effet si elle brûle déjà.
    /// </summary>
    public void Ignite()
    {
        if (_burning) return;
        _burning = true;
        AudioManager.PlayAt(Sfx.FlecheEnflammee, GlobalPosition);
        if (_sprite == null) return;
        if (_burningTexture == null && ResourceLoader.Exists(BurningTexturePath))
            _burningTexture = GD.Load<Texture2D>(BurningTexturePath);
        if (_burningTexture != null)
        {
            _sprite.Texture = _burningTexture;
            _sprite.Hframes = Mathf.Max(1, _burningTexture.GetWidth() / FlameFrameSize);
            _sprite.Frame = 0;
        }
        else
        {
            _sprite.Modulate = new Color(1f, 0.6f, 0.2f);
        }
    }

    private void OnAreaEntered(Area2D area) => TryHitTarget(area);

    private void OnBodyEntered(Node2D body)
    {
        if (body is IArrowInteractor)
        {
            // Retour anticipé voulu : le test « mur » plus bas arrêterait la flèche, or une torche allumée doit la laisser passer.
            TryHitTarget(body); // c'est lui qui décide si la flèche s'arrête (torche éteinte) ou passe (torche allumée)
            return;
        }
        TryHitTarget(body);
        // Les CharacterBody2D (Brann, ennemis) ne sont pas des murs : les ennemis sont gérés par leur HurtBox
        // (zone), Brann est ignoré. Tout le reste (TileMapLayer, StaticBody2D) arrête la flèche.
        if (body is CharacterBody2D) return;
        if (!_done) AudioManager.PlayAt(Sfx.FlecheImpact, GlobalPosition);
        Despawn();
    }

    private void TryHitTarget(Node2D node)
    {
        if (_done) return;
        if (node is IArrowInteractor interactor)
        {
            if (interactor.OnArrowTouch(this))
            {
                AudioManager.PlayAt(Sfx.FlecheImpact, GlobalPosition);
                Despawn(); // torche éteinte : la flèche s'arrête (allumée, OnArrowTouch renvoie faux et elle passe)
            }
            return;
        }
        if (!node.IsInGroup(TargetGroup) || node is not IArrowTarget target) return;
        target.OnArrowHit(GlobalPosition, _direction);
        AudioManager.PlayAt(Sfx.FlecheImpact, GlobalPosition);
        Despawn();
    }

    private void Despawn()
    {
        if (_done) return;
        _done = true;
        _hitBox.SetDeferred(Area2D.PropertyName.Monitoring, false); // plus aucune détection pendant la suppression
        QueueFree();
    }
}
