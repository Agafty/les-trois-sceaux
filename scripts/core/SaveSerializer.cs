using System;
using System.Text.Json;

/// <summary>
/// Conversion SaveData &lt;-&gt; JSON et migration des anciennes versions. Classe C# pure (sans Godot).
/// Ne lève jamais d'exception pour un contenu invalide : renvoie false et un message d'erreur.
/// </summary>
public static class SaveSerializer
{
    private static readonly JsonSerializerOptions Options = new() { WriteIndented = true };

    public static string Serialize(SaveData data) => JsonSerializer.Serialize(data, Options);

    public static bool TryDeserialize(string json, out SaveData data, out string error)
    {
        data = null;
        error = "";
        try
        {
            var parsed = JsonSerializer.Deserialize<SaveData>(json, Options);
            if (parsed == null)
            {
                error = "fichier vide";
                return false;
            }
            if (!Migrate(parsed, out error))
                return false;
            Normalize(parsed);
            data = parsed;
            return true;
        }
        catch (Exception e) when (e is JsonException or ArgumentException or NotSupportedException)
        {
            error = "JSON invalide : " + e.Message;
            return false;
        }
    }

    // Un JSON peut contenir null ou omettre des champs : on remet des valeurs sûres.
    private static void Normalize(SaveData d)
    {
        d.Inventory ??= new();
        d.Inventory.RemoveAll(e => e == null);
        foreach (var e in d.Inventory) e.Id ??= "";
        d.CollectedIds ??= new();
        d.CollectedIds.RemoveAll(string.IsNullOrEmpty);
        d.DungeonItems ??= new();
        d.DungeonItems.RemoveAll(string.IsNullOrEmpty);
        if (d.RavenFeathers < 0) d.RavenFeathers = 0;
        d.EquippedItemId ??= "";
        d.ScenePath ??= "";
        d.SpawnId ??= "";
        if (!double.IsFinite(d.PlayTimeSeconds) || d.PlayTimeSeconds < 0) d.PlayTimeSeconds = 0;
    }

    /// <summary>
    /// Met à niveau les données jusqu'à <see cref="SaveData.CurrentVersion"/>.
    /// Chaque ancienne version a son case qui adapte les champs, monte Version d'un cran puis fait « goto » vers le suivant.
    /// Pour un futur format 3 : « case 2: ...adapter...; data.Version = 3; goto case 3; » puis « case 3: return true; ».
    /// </summary>
    public static bool Migrate(SaveData data, out string error)
    {
        error = "";
        if (data.Version > SaveData.CurrentVersion)
        {
            error = $"sauvegarde d'une version plus récente ({data.Version}) que le jeu ({SaveData.CurrentVersion})";
            return false;
        }
        switch (data.Version)
        {
            case 1:
                // Version 1 -> 2 : ajout des objets de donjon et des plumes (absents = aucun).
                data.DungeonItems = new();
                data.RavenFeathers = 0;
                data.Version = 2;
                goto case 2;
            case 2:
                return true; // rien à migrer
            case 0:
                error = "numéro de version absent";
                return false;
            default:
                error = $"version de sauvegarde inconnue ({data.Version})";
                return false;
        }
    }
}
