using Godot;

/// <summary>
/// Corps solide d'un interrupteur (levier, cible au sol) : Brann et les blocs ne passent plus à travers.
/// La zone de détection reste l'Area2D du <see cref="Switch"/> (épée, flèche). Tant que l'interrupteur n'est pas résolu,
/// ce corps arrête la flèche comme un mur, mais lui fait d'abord activer l'interrupteur (sinon un tir de côté ou à bout portant
/// pourrait être arrêté sans effet). Une fois résolu (<see cref="Switch.IsFrozen"/>), la flèche le traverse ; il reste solide pour Brann.
/// </summary>
public partial class SwitchBody : StaticBody2D, IArrowInteractor
{
    public bool OnArrowTouch(Arrow arrow)
    {
        if (GetParent() is not Switch sw || sw.IsFrozen) return false; // résolu : la flèche passe
        sw.OnArrowHit(arrow.GlobalPosition, Vector2.Right.Rotated(arrow.Rotation));
        return true; // la flèche s'arrête
    }
}
