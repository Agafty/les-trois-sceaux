using System;

/// <summary>
/// Règles pures d'Ondine (sans Godot, donc testables) : choix du bassin où elle surgit, durée de l'annonce, progression de la barre de vie,
/// éclaboussure, taille des vagues de morceaux d'armure.
/// </summary>
public static class OndineRules
{
    /// <summary>Annonce « illimitée » (option d'aide = 0) : pas infinie, juste longue (le double de la base).</summary>
    public const float UnlimitedAnnounceFactor = 2f;

    /// <summary>Plafond du multiplicateur d'aide pour l'annonce (x2 au maximum : au-delà elle devient trop molle).</summary>
    public const float MaxAnnounceFactor = 2f;

    /// <summary>
    /// Durée de l'annonce : la base multipliée par l'option d'aide (1, 2, ou 0 = illimité), plafonnée à x2.
    /// </summary>
    public static float AnnounceSeconds(float baseSeconds, float helpMultiplier)
    {
        float factor = helpMultiplier <= 0f ? UnlimitedAnnounceFactor : Math.Min(helpMultiplier, MaxAnnounceFactor);
        return Math.Max(0f, baseSeconds) * factor;
    }

    /// <summary>
    /// Choisit le bassin du prochain surgissement. Parmi les bassins à moins de <paramref name="radius"/> du joueur et différents du dernier,
    /// un au hasard (<paramref name="random01"/> dans [0, 1[) ; s'il n'y en a aucun, le plus proche du joueur (toujours différent du dernier
    /// s'il y a plus d'un bassin). -1 si la liste est vide.
    /// </summary>
    public static int PickBasin(float[] xs, float[] ys, int count, float px, float py, int last, float radius, float random01)
    {
        if (count <= 0) return -1;
        float r2 = radius * radius;
        int candidates = 0;
        for (int i = 0; i < count; i++)
            if (i != last && DistSq(xs[i], ys[i], px, py) <= r2) candidates++;
        if (candidates > 0)
        {
            int pick = Math.Min((int)(Math.Clamp(random01, 0f, 0.999999f) * candidates), candidates - 1);
            for (int i = 0; i < count; i++)
            {
                if (i == last || DistSq(xs[i], ys[i], px, py) > r2) continue;
                if (pick-- == 0) return i;
            }
        }
        int best = -1;
        float bestD = float.MaxValue;
        for (int i = 0; i < count; i++)
        {
            if (i == last && count > 1) continue;
            float d = DistSq(xs[i], ys[i], px, py);
            if (d < bestD) { bestD = d; best = i; }
        }
        return best;
    }

    /// <summary>Vrai si Brann (pieds) est assez près du centre du bassin pour prendre l'éclaboussure.</summary>
    public static bool SplashHits(float dx, float dy, float radius) => dx * dx + dy * dy < radius * radius;

    /// <summary>Fraction de vie de la barre : PV d'armure restants plus morceaux restants, sur le total (armure + morceaux).</summary>
    public static float Progress(int armorLeft, int armorMax, int piecesLeft, int piecesTotal) =>
        BossRules.Progress(Math.Max(0, armorLeft) + Math.Max(0, piecesLeft), Math.Max(0, armorMax) + Math.Max(0, piecesTotal));

    /// <summary>Nombre de morceaux de la prochaine vague : la taille d'une vague, ou ce qui reste à lancer.</summary>
    public static int NextWaveSize(int spawned, int total, int waveSize) => Math.Max(0, Math.Min(waveSize, total - spawned));

    /// <summary>Apparitions nécessaires pour briser l'armure si chaque apparition encaisse au plus <paramref name="cap"/> PV (et que Brann les atteint).</summary>
    public static int AppearancesToBreak(int armor, int damagePerHit, int cap)
    {
        int dmg = Math.Max(1, damagePerHit);
        int hits = (int)Math.Ceiling(Math.Max(1, cap) / (double)dmg);
        return (int)Math.Ceiling(Math.Max(0, armor) / (double)(hits * dmg));
    }

    private static float DistSq(float ax, float ay, float bx, float by)
    {
        float dx = ax - bx, dy = ay - by;
        return dx * dx + dy * dy;
    }
}
