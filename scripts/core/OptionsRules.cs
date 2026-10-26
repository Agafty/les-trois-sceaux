using System;

/// <summary>Règles pures (sans Godot) des options : valeurs permises, pas, cycles, échelle automatique de la fenêtre.</summary>
public static class OptionsRules
{
    public const int VolumeStep = 10;
    public const int MaxScale = 4;
    public const int BaseWidth = 640;
    public const int BaseHeight = 360;

    /// <summary>Hauteur réservée à la barre de titre et à la barre des tâches pour l'échelle automatique.</summary>
    public const int WindowDecorationMargin = 80;

    public static readonly string[] Languages = { "fr", "en" };

    /// <summary>Valeurs de l'aide au jeune joueur, dans l'ordre du menu : Normal, Doublé, Sans limite.</summary>
    public static readonly int[] HelpValues = { 1, 2, 0 };

    /// <summary>Remet toutes les valeurs dans leurs bornes (volume au pas de 10 le plus proche, échelle 0..4...).</summary>
    public static void Normalize(OptionsData d)
    {
        d.MusicVolume = NormalizeVolume(d.MusicVolume);
        d.SfxVolume = NormalizeVolume(d.SfxVolume);
        if (d.WindowScale < 0 || d.WindowScale > MaxScale) d.WindowScale = 0;
        if (Array.IndexOf(HelpValues, d.PuzzleTimeMultiplier) < 0) d.PuzzleTimeMultiplier = 1;
        if (d.Language == null || Array.IndexOf(Languages, d.Language) < 0) d.Language = "fr";
        d.Version = OptionsData.CurrentVersion;
    }

    public static int NormalizeVolume(int value)
    {
        int clamped = Math.Clamp(value, 0, 100);
        return (clamped + VolumeStep / 2) / VolumeStep * VolumeStep;
    }

    /// <summary>Volume décalé de <paramref name="direction"/> pas (-1 ou +1), borné à 0..100 (sans retour au début).</summary>
    public static int StepVolume(int value, int direction) =>
        Math.Clamp(NormalizeVolume(value) + Math.Sign(direction) * VolumeStep, 0, 100);

    /// <summary>Échelle suivante dans le cycle auto, ×1, ×2, ×3, ×4, auto (direction +1 ou -1).</summary>
    public static int CycleScale(int scale, int direction)
    {
        int count = MaxScale + 1;
        return ((scale + Math.Sign(direction)) % count + count) % count;
    }

    /// <summary>Position suivante dans <see cref="HelpValues"/> (direction +1 ou -1), en boucle.</summary>
    public static int CycleHelp(int value, int direction)
    {
        int index = Math.Max(0, Array.IndexOf(HelpValues, value));
        int count = HelpValues.Length;
        return HelpValues[((index + Math.Sign(direction)) % count + count) % count];
    }

    public static string CycleLanguage(string language, int direction)
    {
        int index = Math.Max(0, Array.IndexOf(Languages, language));
        int count = Languages.Length;
        return Languages[((index + Math.Sign(direction)) % count + count) % count];
    }

    /// <summary>Plus grande échelle entière (1 à 4) dont la fenêtre tient dans la zone utile de l'écran (au moins 1).</summary>
    public static int AutoScale(int usableWidth, int usableHeight)
    {
        int best = 1;
        for (int k = 2; k <= MaxScale; k++)
            if (BaseWidth * k <= usableWidth && BaseHeight * k + WindowDecorationMargin <= usableHeight)
                best = k;
        return best;
    }

    /// <summary>Échelle réellement appliquée : celle demandée (0 = auto), réduite si la fenêtre ne tient pas dans l'écran.</summary>
    public static int EffectiveScale(int requested, int usableWidth, int usableHeight)
    {
        int auto = AutoScale(usableWidth, usableHeight);
        return requested <= 0 ? auto : Math.Min(requested, auto);
    }
}
