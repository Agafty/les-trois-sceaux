using Godot;

/// <summary>
/// Zone de capture d'une <see cref="Chicken"/> : Brann qui la touche en marchant, ou un coup d'épée (<see cref="IMeleeTarget"/>),
/// l'attrape. C'est un Area2D sur la couche 1 : la HitBox de l'épée (masque 1, Melee) prévient les zones de ce type, comme pour un buisson.
/// </summary>
public partial class ChickenZone : Area2D, IMeleeTarget
{
    /// <summary>La zone a été touchée par l'épée.</summary>
    [Signal]
    public delegate void SwordHitEventHandler();

    public void OnMeleeHit(Vector2 position)
    {
        EmitSignal(SignalName.SwordHit);
    }
}
