using System;

/// <summary>
/// Règles pures du combat de Gorm (sans Godot) : plaques d'armure, ravitaillement en bombes, découpage de la planche.
/// </summary>
public static class GormRules
{
    /// <summary>Nombre de plaques d'armure à faire sauter (plein, brisé, nu = niveaux 0, 1, 2).</summary>
    public const int PlateCount = 2;

    /// <summary>Plaques encore en place pour un niveau d'armure donné (0 = armure pleine, 2 = nu).</summary>
    public static int PlatesLeft(int armorLevel) => PlateCount - Math.Clamp(armorLevel, 0, PlateCount);

    /// <summary>Niveau d'armure après l'arrachement d'une plaque (plafonné à « nu »).</summary>
    public static int NextArmor(int armorLevel) => Math.Min(PlateCount, Math.Max(0, armorLevel) + 1);

    /// <summary>
    /// Faut-il ravitailler Brann en bombes ? Oui s'il possède les bombes, en a moins de <paramref name="below"/>, qu'il reste une plaque
    /// à arracher et qu'aucun paquet n'est déjà au sol.
    /// </summary>
    public static bool NeedsBombSupply(bool hasBombs, int quantity, int platesLeft, int below, bool packOnGround)
        => hasBombs && !packOnGround && platesLeft > 0 && quantity < below;

    /// <summary>
    /// Choisit le point de ravitaillement : parmi ceux à au moins <paramref name="minDistanceFromBoss"/> de Gorm, le plus proche de Brann ;
    /// si aucun ne convient, le plus éloigné de Gorm. -1 s'il n'y a aucun point.
    /// </summary>
    public static int PickSupplyPoint(float[] xs, float[] ys, int count, float bossX, float bossY, float playerX, float playerY, float minDistanceFromBoss)
    {
        int best = -1;
        float bestToPlayer = float.MaxValue;
        int farthest = -1;
        float farthestToBoss = -1f;
        for (int i = 0; i < count; i++)
        {
            float toBoss = Distance(xs[i], ys[i], bossX, bossY);
            if (toBoss > farthestToBoss)
            {
                farthestToBoss = toBoss;
                farthest = i;
            }
            if (toBoss < minDistanceFromBoss) continue;
            float toPlayer = Distance(xs[i], ys[i], playerX, playerY);
            if (toPlayer < bestToPlayer)
            {
                bestToPlayer = toPlayer;
                best = i;
            }
        }
        return best >= 0 ? best : farthest;
    }

    /// <summary>Progression de la barre : plaques restantes + coups d'épée restants sur le total.</summary>
    public static float Progress(int platesLeft, int swordHitsLeft, int swordHitsTotal)
        => BossRules.Progress(platesLeft + swordHitsLeft, PlateCount + swordHitsTotal);

    /// <summary>Case de la planche gorm.png (17 colonnes, 3 lignes : plein, brisé, nu) pour une ligne et une colonne.</summary>
    public static int FrameIndex(int armorLevel, int column) => Math.Clamp(armorLevel, 0, PlateCount) * GormFrames.Columns + column;

    private static float Distance(float ax, float ay, float bx, float by)
    {
        float dx = ax - bx, dy = ay - by;
        return MathF.Sqrt(dx * dx + dy * dy);
    }
}
