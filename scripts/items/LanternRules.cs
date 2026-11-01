/// <summary>
/// Règles pures de la lanterne (sans Godot) : réglages de lumière, lecture de la propriété de carte « obscurite »,
/// distance et temps de présence nécessaires pour allumer une torche ou ouvrir un mur à rune.
/// </summary>
public static class LanternRules
{
    /// <summary>Id de l'objet (resources/items/lanterne.tres) : la lanterne est passive, possédée = portée allumée.</summary>
    public const string ItemId = "lanterne";

    /// <summary>Décalage du centre de la lumière devant Brann (px, dans la direction du regard).</summary>
    public const float LightOffset = 40f;
    public const float LightRadius = 120f;
    /// <summary>Petit halo permanent autour de Brann dans une salle sombre (avec ou sans lanterne).</summary>
    public const float HaloRadius = 48f;
    /// <summary>Lumière d'une torche ou d'un brasero allumé dans une salle sombre.</summary>
    public const float TorchLightRadius = 96f;
    /// <summary>Lueur d'un mur à rune fermé (visible dans le noir).</summary>
    public const float RuneGlowRadius = 40f;

    /// <summary>Distance (px) et présence (s) pour allumer une torche.</summary>
    public const float TorchReach = 40f;
    public const float TorchDwell = 0.5f;
    /// <summary>Distance (px) et présence (s) pour ouvrir un mur à rune.</summary>
    public const float RuneReach = 64f;
    public const float RuneDwell = 0.8f;

    /// <summary>Teinte d'ambiance d'une salle en pénombre (bleu sombre).</summary>
    public const float AmbientR = 0.30f;
    public const float AmbientG = 0.34f;
    public const float AmbientB = 0.55f;

    /// <summary>Valeur de la propriété de carte « obscurite » : vide ou « non » = clair, « penombre ». Faux si inconnue (traitée comme clair).</summary>
    public static bool TryParseDarkness(string value, out bool dark)
    {
        dark = false;
        if (string.IsNullOrWhiteSpace(value)) return true;
        switch (value.Trim().ToLowerInvariant())
        {
            case "non": return true;
            case "penombre": dark = true; return true;
            default: return false;
        }
    }

    /// <summary>Vrai si les deux points sont à moins de <paramref name="radius"/> (inclus) l'un de l'autre.</summary>
    public static bool IsNear(float ax, float ay, float bx, float by, float radius)
    {
        float dx = ax - bx, dy = ay - by;
        return dx * dx + dy * dy <= radius * radius;
    }

    /// <summary>Temps de présence cumulé : il grandit tant que Brann est à portée et retombe à zéro dès qu'il s'éloigne.</summary>
    public static float Advance(float timer, bool near, float delta) => near ? timer + delta : 0f;

    /// <summary>Vrai quand la présence a duré assez longtemps.</summary>
    public static bool IsReached(float timer, float required) => timer >= required;
}
