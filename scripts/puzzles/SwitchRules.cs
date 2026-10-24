/// <summary>Règles pures des interrupteurs (sans Godot) : lecture des propriétés Tiled et choix des images.</summary>
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

    /// <summary>Un coup d'épée sans symbole est un levier (art/puzzles/levier.png).</summary>
    public static bool IsLever(SwitchMode mode, string symbol) => mode == SwitchMode.Epee && string.IsNullOrEmpty(symbol);

    /// <summary>
    /// Un interrupteur isolé, permanent et sans ordre garde le comportement des premières salles : son état est
    /// mémorisé par son id. Dans les autres cas (groupe, durée, ordre) l'état se réinitialise au rechargement de la salle
    /// (seule la porte ouverte est mémorisée).
    /// </summary>
    public static bool IsPersistent(int groupSize, int order, float duration) => groupSize <= 1 && order <= 0 && duration <= 0f;

    /// <summary>Multiplicateur d'aide valide : 0 = durées illimitées, sinon entre 1 et 4.</summary>
    public static float ClampTimeMultiplier(float value) => value <= 0f ? 0f : (value < 1f ? 1f : (value > 4f ? 4f : value));
}
