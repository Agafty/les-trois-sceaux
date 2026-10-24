using Godot;

/// <summary>
/// Corps ou zone avec lequel une flèche interagit sans être une simple cible : torche, brasero...
/// Quand la flèche le touche, elle appelle <see cref="OnArrowTouch"/> ; la valeur renvoyée dit si la flèche s'arrête.
/// Un nœud qui implémente cette interface n'a pas besoin d'être dans le groupe « cible_fleche ».
/// </summary>
public interface IArrowInteractor
{
    /// <summary>Renvoie vrai si la flèche disparaît, faux si elle continue son vol (elle traverse).</summary>
    bool OnArrowTouch(Arrow arrow);
}
