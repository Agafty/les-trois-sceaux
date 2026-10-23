using Godot;

/// <summary>
/// Projectile générique : avance en ligne droite, disparaît au contact d'une HurtBox
/// adverse (via la HitBox enfant), d'un mur, ou après sa durée de vie.
/// </summary>
public partial class Projectile : Area2D
{
    [Export] public float Speed { get; set; } = 110f;
    [Export] public float Lifetime { get; set; } = 3f;

    private Vector2 _direction = Vector2.Right;
    private float _age;
    private bool _dying;
    private HitBox _hitBox;

    /// <summary>Direction de vol (normalisée ici). À appeler avant ou juste après AddChild.</summary>
    public void Launch(Vector2 direction)
    {
        _direction = direction.LengthSquared() > 0.0001f ? direction.Normalized() : Vector2.Right;
    }

    public override void _Ready()
    {
        _hitBox = GetNode<HitBox>("HitBox");
        _hitBox.HitLanded += OnHitLanded;
        BodyEntered += OnBodyEntered;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_dying) return;
        float dt = (float)delta;
        GlobalPosition += _direction * Speed * dt;
        _age += dt;
        if (_age >= Lifetime) Die();
    }

    // QueueFree est différé : on coupe la HitBox tout de suite pour éviter un second coup.
    private void Die()
    {
        if (_dying) return;
        _dying = true;
        _hitBox.SetDeferred(Area2D.PropertyName.Monitoring, false);
        QueueFree();
    }

    private void OnHitLanded() => Die();

    // Les personnages (joueur, ennemis) sont des CharacterBody2D : ils sont ignorés ici,
    // seuls les murs (TileMapLayer, StaticBody2D) arrêtent le projectile.
    private void OnBodyEntered(Node2D body)
    {
        if (body is CharacterBody2D) return;
        Die();
    }
}
