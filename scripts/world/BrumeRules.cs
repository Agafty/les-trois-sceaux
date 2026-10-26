using System;
using System.Globalization;

/// <summary>
/// Règles pures (sans Godot) de la brume d'un rectangle Tiled de classe « Brume » : la propriété « densite » liste une valeur
/// entre 0 (aucune brume) et 1 (opaque) par étape de l'histoire, de 0 à <see cref="StoryRules.MaxStage"/>.
/// </summary>
public static class BrumeRules
{
    /// <summary>Nombre de valeurs attendues : une par étape (0 à 4).</summary>
    public const int ValueCount = StoryRules.MaxStage + 1;

    /// <summary>Lit « 0.5,0.8,0.45,0.3,0.7 » (point ou virgule décimale acceptés si la liste est séparée par « ; »). Faux si vide ou illisible.</summary>
    public static bool TryParse(string text, out float[] densities)
    {
        densities = null;
        if (string.IsNullOrWhiteSpace(text)) return false;
        var parts = text.Split(text.Contains(';') ? ';' : ',');
        var result = new float[parts.Length];
        for (int i = 0; i < parts.Length; i++)
        {
            string token = parts[i].Trim().Replace(',', '.');
            if (!float.TryParse(token, NumberStyles.Float, CultureInfo.InvariantCulture, out float value)) return false;
            result[i] = Math.Clamp(value, 0f, 1f);
        }
        densities = result;
        return true;
    }

    /// <summary>Densité à l'étape donnée ; si la liste est plus courte que l'étape, la dernière valeur est reprise.</summary>
    public static float DensityFor(float[] densities, int stage)
    {
        if (densities == null || densities.Length == 0) return 0f;
        return densities[Math.Clamp(stage, 0, densities.Length - 1)];
    }
}
