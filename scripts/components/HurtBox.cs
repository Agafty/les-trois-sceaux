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

    /// <summary>
    /// Faux : cette zone ne joue aucun bruitage de coup (le propriétaire gère le sien, ex. le boss).
    /// Sinon : ennemi touché = coup_ennemi, ennemi vaincu = ennemi_mort, Brann touché = brann_touche.
    /// </summary>
    [Export] public bool PlaySounds { get; set; } = true;

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

        bool wasAlive = _health == null || _health.CurrentHealth > 0;
        _health?.Damage(damage);
        if (PlaySounds && wasAlive)
            PlayHitSound(_health == null || _health.CurrentHealth > 0);
        EmitSignal(SignalName.Hit, damage, fromPosition);
        FlashSprite();
    }

    // Brann vaincu : son brann_mort joué par Player ; ici seulement le coup reçu.
    private void PlayHitSound(bool survived)
    {
        if (Team == Team.Ennemi)
            AudioManager.PlayAt(survived ? Sfx.CoupEnnemi : Sfx.EnnemiMort, GlobalPosition);
        else if (survived)
            AudioManager.Play(Sfx.BrannTouche);
    }

    private void FlashSprite()
    {
        if (_sprite == null) return;

        _sprite.Modulate = new Color(6f, 6f, 6f);
        CreateTween().TweenProperty(_sprite, "modulate", Colors.White, FlashDuration);
    }
}
