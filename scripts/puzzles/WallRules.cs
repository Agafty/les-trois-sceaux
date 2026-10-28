/// <summary>Règles pures (sans Godot) du mur fissuré : apparences reconnues pour la propriété Tiled « apparence ».</summary>
public static class WallRules
{
    public const string DefaultAppearance = "mur";
    public const string RubbleAppearance = "eboulis";

    /// <summary>Lit la propriété « apparence » : vide = « mur ». Faux (et « mur » en sortie) si la valeur est inconnue.</summary>
    public static bool TryParseAppearance(string value, out string appearance)
    {
        appearance = DefaultAppearance;
        if (string.IsNullOrEmpty(value) || value == DefaultAppearance) return true;
        if (value == RubbleAppearance)
        {
            appearance = RubbleAppearance;
            return true;
        }
        return false;
    }
}
