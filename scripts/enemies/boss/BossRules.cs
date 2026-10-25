using System;

/// <summary>
/// Règles pures des combats de boss (sans Godot) : lecture des noms Tiled, identifiants, durées, progression, géométrie.
/// </summary>
public static class BossRules
{
    /// <summary>Préfixe du rectangle ou point Tiled qui marque l'apparition d'un boss (« boss_sylve »).</summary>
    public const string MarkerPrefix = "boss_";

    /// <summary>Nom du rectangle Tiled qui marque un pilier de l'arène.</summary>
    public const string PillarName = "pilier";

    /// <summary>Plafond de l'allongement de l'assommement quand l'option d'aide vaut « illimité » (0).</summary>
    public const float UnlimitedStunFactor = 4f;

    /// <summary>« boss_sylve » donne « sylve ». Faux si le nom ne commence pas par « boss_ » ou si le reste n'est pas un nom simple.</summary>
    public static bool TryParseMarker(string markerName, out string boss)
    {
        boss = "";
        if (markerName == null || !markerName.StartsWith(MarkerPrefix, StringComparison.Ordinal)) return false;
        string name = markerName.Substring(MarkerPrefix.Length);
        if (!RoomObjectCatalog.IsSafeName(name)) return false;
        boss = name;
        return true;
    }

    /// <summary>Scène du boss : scenes/enemies/boss/&lt;nom&gt;.tscn.</summary>
    public static string ScenePath(string boss) => $"res://scenes/enemies/boss/{boss}.tscn";

    /// <summary>Identifiant mémorisé dans GameState quand le boss est vaincu, ex. « donjon1_boss_sylve ».</summary>
    public static string BossId(string zone, string boss) =>
        string.IsNullOrEmpty(zone) ? $"boss_{boss}" : $"{zone}_boss_{boss}";

    /// <summary>Identifiant unique d'une récompense du boss (« receptacle », « sceau »).</summary>
    public static string RewardId(string bossId, string reward) => $"{bossId}_{reward}";

    /// <summary>
    /// Durée de l'assommement : la durée de base multipliée par l'option d'aide (GameState.PuzzleTimeMultiplier).
    /// 0 = illimité pour les énigmes ; pour un assommement on prend alors le plafond (<see cref="UnlimitedStunFactor"/>).
    /// </summary>
    public static float StunDuration(float baseSeconds, float helpMultiplier)
    {
        float factor = helpMultiplier <= 0f ? UnlimitedStunFactor : helpMultiplier;
        return Math.Max(0f, baseSeconds) * factor;
    }

    /// <summary>Fraction de vie restante de la barre (1 = plein, 0 = vaincu) : unités restantes sur unités totales.</summary>
    public static float Progress(int unitsLeft, int unitsTotal)
    {
        if (unitsTotal <= 0) return 0f;
        return Math.Clamp(unitsLeft, 0, unitsTotal) / (float)unitsTotal;
    }

    /// <summary>Vrai si le point (px, py) est dans le rectangle (rx, ry, rw, rh) agrandi de <paramref name="margin"/> de chaque côté.</summary>
    public static bool IsInsideRect(float px, float py, float rx, float ry, float rw, float rh, float margin)
    {
        return px >= rx - margin && px <= rx + rw + margin && py >= ry - margin && py <= ry + rh + margin;
    }

    /// <summary>
    /// Distance parcourue depuis (ox, oy) dans la direction unitaire (dx, dy) avant de sortir du rectangle (rx, ry, rw, rh).
    /// 0 si l'origine est déjà dehors ; sert à ne pas dessiner l'avertissement d'une charge à travers un mur.
    /// </summary>
    public static float DistanceToRectEdge(float ox, float oy, float dx, float dy, float rx, float ry, float rw, float rh)
    {
        if (ox < rx || ox > rx + rw || oy < ry || oy > ry + rh) return 0f;
        float best = float.MaxValue;
        if (dx > 1e-6f) best = Math.Min(best, (rx + rw - ox) / dx);
        else if (dx < -1e-6f) best = Math.Min(best, (rx - ox) / dx);
        if (dy > 1e-6f) best = Math.Min(best, (ry + rh - oy) / dy);
        else if (dy < -1e-6f) best = Math.Min(best, (ry - oy) / dy);
        return best == float.MaxValue ? 0f : Math.Max(0f, best);
    }
}
