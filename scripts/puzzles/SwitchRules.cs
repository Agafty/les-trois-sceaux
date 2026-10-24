/// <summary>Règles pures des interrupteurs (sans Godot) : lecture de la propriété Tiled « mode ».</summary>
public static class SwitchRules
{
    /// <summary>
    /// Convertit la valeur Tiled « mode » (fleche, epee). Une valeur absente ou vide donne « fleche »
    /// (les premières cartes n'ont pas la propriété) ; une valeur inconnue renvoie faux, avec « fleche » en repli.
    /// </summary>
    public static bool TryParseMode(string value, out SwitchMode mode)
    {
        mode = SwitchMode.Fleche;
        if (string.IsNullOrEmpty(value) || value == "fleche") return true;
        if (value == "epee")
        {
            mode = SwitchMode.Epee;
            return true;
        }
        return false;
    }

    /// <summary>Nom de fichier de l'image (art/puzzles/interrupteur_&lt;nom&gt;.png).</summary>
    public static string TextureName(SwitchMode mode) => mode == SwitchMode.Epee ? "epee" : "fleche";
}
