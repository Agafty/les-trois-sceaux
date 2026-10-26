/// <summary>Règles pures des portes (sans Godot) : lecture du type Tiled.</summary>
public static class DoorRules
{
    /// <summary>Convertit la valeur Tiled « type » (cle, grande_cle, ennemis, interrupteur). Faux si inconnue.</summary>
    public static bool TryParseKind(string value, out DoorKind kind)
    {
        switch (value)
        {
            case "cle": kind = DoorKind.Cle; return true;
            case "grande_cle": kind = DoorKind.GrandeCle; return true;
            case "ennemis": kind = DoorKind.Ennemis; return true;
            case "interrupteur": kind = DoorKind.Interrupteur; return true;
            default: kind = DoorKind.Cle; return false;
        }
    }

    /// <summary>Nom de fichier de l'image de la porte (art/puzzles/porte_&lt;nom&gt;.png).</summary>
    public static string TextureName(DoorKind kind) => kind switch
    {
        DoorKind.GrandeCle => "grande_cle",
        DoorKind.Ennemis => "ennemis",
        DoorKind.Interrupteur => "interrupteur",
        _ => "cle",
    };

    /// <summary>Vrai pour les portes qui s'ouvrent quand Brann pousse dessus.</summary>
    public static bool OpensByPushing(DoorKind kind) => kind == DoorKind.Cle || kind == DoorKind.GrandeCle;

    /// <summary>Apparence par défaut : une porte de bâtiment ou de donjon (image choisie d'après le type).</summary>
    public const string DefaultAppearance = "porte";

    /// <summary>Apparences connues (propriété Tiled « apparence » d'une Porte) ; image art/puzzles/porte_&lt;apparence&gt;.png.</summary>
    public static readonly string[] Appearances = { DefaultAppearance, "pont_levis", "tronc", "rocher", "eboulis" };

    /// <summary>Vrai si <paramref name="value"/> est une apparence connue. Vide = « porte ».</summary>
    public static bool TryParseAppearance(string value, out string appearance)
    {
        appearance = DefaultAppearance;
        if (string.IsNullOrEmpty(value)) return true;
        foreach (var known in Appearances)
        {
            if (known != value) continue;
            appearance = known;
            return true;
        }
        return false;
    }

    /// <summary>
    /// Nom de fichier de l'image (art/puzzles/porte_&lt;nom&gt;.png) : celui de l'apparence, sauf pour « porte » où
    /// c'est celui du type (cle, grande_cle, ennemis, interrupteur).
    /// </summary>
    public static string TextureName(DoorKind kind, string appearance) =>
        string.IsNullOrEmpty(appearance) || appearance == DefaultAppearance ? TextureName(kind) : appearance;

    /// <summary>
    /// Type de la porte quand la propriété « type » est vide : seul un obstacle qui n'est pas une porte (tronc, rocher...) peut
    /// s'en passer ; il ne s'ouvre alors que par le code (interrupteur) ou disparaît avec etape_max.
    /// </summary>
    public static bool TypeOptional(string appearance) => !string.IsNullOrEmpty(appearance) && appearance != DefaultAppearance;
}
