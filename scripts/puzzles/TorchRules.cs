/// <summary>Règles pures des torches (sans Godot) : lecture de Tiled, durée d'allumage et image à afficher.</summary>
public static class TorchRules
{
    /// <summary>Secondes avant l'extinction pendant lesquelles la flamme rétrécit.</summary>
    public const float ShrinkSeconds = 3f;

    public const int UnlitFrame = 0;
    public const int FirstFlameFrame = 1;
    public const int FlameFrameCount = 4;
    public const int FirstShrinkFrame = 5;
    public const int ShrinkFrameCount = 2;

    /// <summary>Convertit la propriété Tiled « etat » : « allumee » donne vrai, « eteinte » ou vide donne faux. Renvoie faux si la valeur est inconnue.</summary>
    public static bool TryParseLit(string value, out bool lit)
    {
        lit = false;
        if (string.IsNullOrEmpty(value)) return true;
        value = value.ToLowerInvariant();
        if (value == "eteinte") return true;
        if (value == "allumee")
        {
            lit = true;
            return true;
        }
        return false;
    }

    /// <summary>Durée réelle d'allumage (s) : 0 = reste allumée. Le multiplicateur d'aide s'applique ; 0 ou moins = illimité.</summary>
    public static float EffectiveDuration(float duration, float multiplier)
    {
        if (duration <= 0f || multiplier <= 0f) return 0f;
        return duration * multiplier;
    }

    /// <summary>Image d'une flamme qui brûle (boucle de 4 images à 8 images/s).</summary>
    public static int FlameFrame(float time) => FirstFlameFrame + (int)(time * 8f) % FlameFrameCount;

    /// <summary>Image d'une flamme qui rétrécit (2 images alternées, 4 changements par seconde).</summary>
    public static int ShrinkFrame(float time) => FirstShrinkFrame + (int)(time * 4f) % ShrinkFrameCount;

    /// <summary>Vrai quand il reste assez peu de temps pour que la flamme rétrécisse.</summary>
    public static bool IsShrinking(float remaining) => remaining > 0f && remaining <= ShrinkSeconds;
}
