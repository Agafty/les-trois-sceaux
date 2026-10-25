using Godot;

public partial class HurtBox : Area2D
{
    [Signal]
    public delegate void HitEventHandler(int damage, Vector2 fromPosition);

    /// <summary>Un coup est arrivé alors que la zone était invincible : rien n'est infligé (retour visuel « rien ne passe » d'un boss).</summary>
    [Signal]
    public delegate void BlockedEventHandler(int damage, Vector2 fromPosition);

    [Export]
    public Team Team { get; set; } = Team.Ennemi;

    [Export]
    public float FlashDuration { get; set; } = 0.1f;

    public bool Invincible { get; set; }

    private Health _health;
    private CanvasItem _sprite;

    public override void _Ready()
    {
        _health = GetParent().GetNodeOrNull<Health>("Health");
        _sprite = GetParent().GetNodeOrNull<CanvasItem>("AnimatedSprite2D");
    }

    public void ReceiveHit(int damage, Vector2 fromPosition)
    {
        if (Invincible)
        {
            EmitSignal(SignalName.Blocked, damage, fromPosition);
            return;
        }

        _health?.Damage(damage);
        EmitSignal(SignalName.Hit, damage, fromPosition);
        FlashSprite();
    }

    private void FlashSprite()
    {
        if (_sprite == null) return;

        _sprite.Modulate = new Color(6f, 6f, 6f);
        CreateTween().TweenProperty(_sprite, "modulate", Colors.White, FlashDuration);
    }
}
