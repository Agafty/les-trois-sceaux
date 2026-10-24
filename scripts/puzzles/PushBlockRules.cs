using System;
using System.Collections.Generic;

/// <summary>Règles pures du bloc poussable (sans Godot) : direction de poussée et alignement sur la grille.</summary>
public static class PushBlockRules
{
    /// <summary>
    /// Direction dans laquelle Brann pousse le bloc, d'après le vecteur Brann -> bloc (dx, dy) :
    /// l'axe dominant, dans le sens qui éloigne le bloc de Brann. Faux si Brann n'est pas assez en face
    /// du bloc (écart latéral supérieur à <paramref name="lateralTolerance"/> : il longe le bloc ou le touche par un coin).
    /// </summary>
    public static bool TryGetPushDirection(float dx, float dy, float lateralTolerance, out int dirX, out int dirY)
    {
        dirX = 0;
        dirY = 0;
        if (Math.Abs(dx) > Math.Abs(dy))
        {
            if (Math.Abs(dy) > lateralTolerance) return false;
            dirX = dx > 0f ? 1 : -1;
        }
        else
        {
            if (Math.Abs(dx) > lateralTolerance) return false;
            dirY = dy > 0f ? 1 : -1;
        }
        return true;
    }

    /// <summary>Centre de la case de grille (de côté <paramref name="cell"/>) qui contient la coordonnée.</summary>
    public static float SnapToCellCenter(float value, float cell)
    {
        return (float)Math.Floor(value / cell) * cell + cell * 0.5f;
    }

    /// <summary>Indice de la case de grille (de côté <paramref name="cell"/>) qui contient la coordonnée.</summary>
    public static int CellIndex(float value, float cell) => (int)Math.Floor(value / cell);

    /// <summary>
    /// Ajoute la case (cellX, cellY) et ses 8 voisines à l'ensemble des cases interdites au bloc
    /// (un Spawn, une Sortie ou une Porte : un bloc posé là ou à côté enfermerait Brann).
    /// </summary>
    public static void AddForbiddenAround(HashSet<(int, int)> forbidden, int cellX, int cellY)
    {
        for (int dx = -1; dx <= 1; dx++)
            for (int dy = -1; dy <= 1; dy++)
                forbidden.Add((cellX + dx, cellY + dy));
    }
}
