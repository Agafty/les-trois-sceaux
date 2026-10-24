using Godot;

/// <summary>
/// Point d'accroche des flèches : tout nœud touchable à distance (interrupteur à cristal, cible...)
/// doit (1) être dans le groupe Godot "cible_fleche", (2) implémenter cette interface et
/// (3) avoir une zone ou un corps de collision que la flèche peut toucher (couche 1 par défaut).
/// La flèche appelle OnArrowHit puis disparaît. Une cible qui doit arrêter la flèche sans réagir
/// n'a pas besoin de cette interface : un simple StaticBody2D l'arrête déjà.
/// </summary>
public interface IArrowTarget
{
    /// <summary>Appelé quand une flèche touche la cible. position = point d'impact (monde), direction = sens du tir (vecteur unité).</summary>
    void OnArrowHit(Vector2 position, Vector2 direction);
}
