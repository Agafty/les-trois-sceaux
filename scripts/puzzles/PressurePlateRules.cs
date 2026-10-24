/// <summary>Règles pures des plaques de pression (sans Godot).</summary>
public static class PressurePlateRules
{
    /// <summary>Convertit la valeur Tiled « declencheur » (bloc, joueur, tous). Vide = « tous ». Faux si inconnue (repli « tous »).</summary>
    public static bool TryParseTrigger(string value, out PlateTrigger trigger)
    {
        trigger = PlateTrigger.Tous;
        switch (value)
        {
            case null:
            case "":
            case "tous": return true;
            case "bloc": trigger = PlateTrigger.Bloc; return true;
            case "joueur": trigger = PlateTrigger.Joueur; return true;
            default: return false;
        }
    }

    /// <summary>Vrai si ce type de corps peut enfoncer une plaque réglée sur <paramref name="trigger"/>.</summary>
    public static bool Accepts(PlateTrigger trigger, bool isBlock, bool isPlayer)
    {
        if (isBlock) return trigger != PlateTrigger.Joueur;
        if (isPlayer) return trigger != PlateTrigger.Bloc;
        return false;
    }

    /// <summary>Vrai si le point est dans la case centrée en (cellX, cellY) de côté <paramref name="cell"/> (bord haut/gauche inclus).</summary>
    public static bool IsInCell(float x, float y, float cellX, float cellY, float cell)
    {
        float half = cell * 0.5f;
        return x >= cellX - half && x < cellX + half && y >= cellY - half && y < cellY + half;
    }
}
