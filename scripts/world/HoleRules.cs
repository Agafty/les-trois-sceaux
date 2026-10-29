using System;

/// <summary>
/// Règles pures des trous (sans Godot). Le tileset du Temple des Racines n'a pas de collision ni de propriété sur les
/// trous : on les reconnaît à leur numéro de tuile (id local Tiled, ligne x 8 + colonne), 58 à 66 (voir art/tilesets/temple_racines_plan.md).
/// La réserve 67 à 71 (coins rentrants éventuels) n'est PAS reconnue : l'étendre ici seulement quand le graphiste y aura dessiné des trous.
/// </summary>
public static class HoleRules
{
    /// <summary>Première tuile de trou du tileset temple_racines (« trou »).</summary>
    public const int FirstHoleTileId = 58;

    /// <summary>Dernière tuile de trou (coin bas-droite). Toute la case d'une tuile de trou fait tomber.</summary>
    public const int LastHoleTileId = 66;

    /// <summary>Vrai si le numéro de tuile (id local du tileset temple_racines) est un trou.</summary>
    public static bool IsHoleTileId(int tileId) => tileId >= FirstHoleTileId && tileId <= LastHoleTileId;

    /// <summary>
    /// Vrai si l'image d'un tileset est de la famille qui porte les trous mortels en 58 à 66 : temple_racines et sa variante sous-sol,
    /// mine et sa variante sous-sol (mêmes numéros).
    /// </summary>
    public static bool IsHoleTilesetPath(string path)
    {
        if (string.IsNullOrEmpty(path)) return false;
        return path.EndsWith("/temple_racines.png", StringComparison.Ordinal) || path.EndsWith("/temple_racines_sous_sol.png", StringComparison.Ordinal)
            || path.EndsWith("/mine.png", StringComparison.Ordinal) || path.EndsWith("/mine_sous_sol.png", StringComparison.Ordinal);
    }

    /// <summary>Numéro de tuile (id local Tiled) d'une case de l'atlas.</summary>
    public static int TileId(int atlasX, int atlasY, int columns) => atlasY * columns + atlasX;

    /// <summary>Dégâts d'une chute : <paramref name="amount"/>, mais jamais mortels (il reste au moins 1 PV).</summary>
    public static int FallDamage(int currentHealth, int amount) => Math.Max(0, Math.Min(amount, currentHealth - 1));
}
