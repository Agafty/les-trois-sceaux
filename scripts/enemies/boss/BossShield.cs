using Godot;

/// <summary>
/// Zone qui « attrape » les coups d'épée donnés à Sylve quand son vrai point faible (la HurtBox) n'est pas touchable
/// (phase 1, transition). Sans elle, l'épée traverserait Sylve sans aucun retour et on croirait qu'elle ne marche pas.
/// Elle prévient le boss, qui montre un éclat et des étincelles. Activée/désactivée par le boss via Monitorable.
/// </summary>
public partial class BossShield : Area2D, IMeleeTarget
{
    /// <summary>L'épée vient de rebondir sur Sylve (position monde de la lame).</summary>
    [Signal]
    public delegate void SwordBouncedEventHandler(Vector2 position);

    public void OnMeleeHit(Vector2 position) => EmitSignal(SignalName.SwordBounced, position);
}
