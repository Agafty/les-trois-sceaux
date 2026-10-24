using Godot;

/// <summary>
/// Zone (Area2D) touchable par un coup d'épée : une <see cref="HitBox"/> marquée <c>Melee</c> (l'épée de Brann)
/// appelle OnMeleeHit quand elle la chevauche pendant une attaque. Les flèches ne la déclenchent pas
/// (elles passent par <see cref="IArrowTarget"/>). La zone doit être sur une couche vue par la HitBox (couche 1).
/// </summary>
public interface IMeleeTarget
{
    /// <summary>Appelé quand l'épée touche la zone. position = position de la HitBox de l'épée (monde).</summary>
    void OnMeleeHit(Vector2 position);
}
