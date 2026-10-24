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

    private HitBox _hitBox;
    private Vector2 _direction = Vector2.Right;
    private float _travelled;
    private bool _done;

    public override void Begin(Player user, Vector2 direction)
    {
        _direction = direction;
        Rotation = direction.Angle(); // le sprite pointe vers la droite : on le tourne
    }

    public override void _Ready()
    {
        _hitBox = GetNode<HitBox>("HitBox");
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
        if (_travelled >= MaxDistance) Despawn();
    }

    private void OnAreaEntered(Area2D area) => TryHitTarget(area);

    private void OnBodyEntered(Node2D body)
    {
        TryHitTarget(body);
        // Les CharacterBody2D (Brann, ennemis) ne sont pas des murs : les ennemis sont gérés par leur HurtBox
        // (zone), Brann est ignoré. Tout le reste (TileMapLayer, StaticBody2D) arrête la flèche.
        if (body is CharacterBody2D) return;
        Despawn();
    }

    private void TryHitTarget(Node2D node)
    {
        if (_done || !node.IsInGroup(TargetGroup) || node is not IArrowTarget target) return;
        target.OnArrowHit(GlobalPosition, _direction);
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
