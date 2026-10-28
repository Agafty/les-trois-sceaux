using Godot;

/// <summary>
/// Point d'accroche des bombes : tout nœud qui peut être détruit par une explosion (mur fissuré, rocher...)
/// doit (1) être dans le groupe Godot "destructible_bombe" et (2) implémenter cette interface.
/// La bombe appelle OnBombExplosion pour chaque nœud du groupe qui se trouve à portée.
/// </summary>
public interface IBombDestructible
{
    /// <summary>Appelé à l'explosion. center = position de la bombe (monde).</summary>
    void OnBombExplosion(Vector2 center);

    /// <summary>
    /// Demi-taille (px) du rectangle du destructible, centré sur sa position : la bombe mesure sa portée jusqu'au BORD de ce rectangle,
    /// pas jusqu'à son centre (un éboulis de deux cases se casse comme un mur d'une case). Défaut : une case de 32 px.
    /// </summary>
    Vector2 BombHalfExtents => new(16f, 16f);
}
