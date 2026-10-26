using System;
using System.Text.Json;

/// <summary>JSON &lt;-&gt; <see cref="OptionsData"/>. Classe C# pure. Ne lève jamais d'exception : un contenu invalide donne false.</summary>
public static class OptionsSerializer
{
    private static readonly JsonSerializerOptions Options = new() { WriteIndented = true };

    public static string Serialize(OptionsData data) => JsonSerializer.Serialize(data, Options);

    public static bool TryDeserialize(string json, out OptionsData data)
    {
        data = null;
        try
        {
            var parsed = JsonSerializer.Deserialize<OptionsData>(json, Options);
            // Version inconnue (0) ou plus récente que ce jeu : on ne devine pas, valeurs par défaut.
            if (parsed == null || parsed.Version < 1 || parsed.Version > OptionsData.CurrentVersion) return false;
            OptionsRules.Normalize(parsed);
            data = parsed;
            return true;
        }
        catch (Exception e) when (e is JsonException or ArgumentException or NotSupportedException or InvalidOperationException)
        {
            return false;
        }
    }
}
