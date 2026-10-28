using System.Collections.Generic;
using Godot;

/// <summary>
/// Charge (une seule fois) les cinématiques JSON de resources/cinematiques/&lt;id&gt;.json et le fichier scenarios.json
/// (déclencheurs et repères de repli). Un fichier absent ou invalide donne une erreur claire puis null : le jeu ne plante jamais pour ça.
/// Thread principal uniquement.
/// </summary>
public static class CinematicLibrary
{
    private const string Folder = "res://resources/cinematiques/";
    private const string ScenariosFile = "scenarios.json";
    private static readonly Dictionary<string, CinematicData> Cache = new();
    private static ScenarioFile _scenarios;
    private static bool _scenariosLoaded;

    public static CinematicData Get(string id)
    {
        if (!CinematicParser.IsName(id))
        {
            GD.PushError($"Cinématiques : id invalide « {id} ».");
            return null;
        }
        if (Cache.TryGetValue(id, out var cached)) return cached;

        CinematicData data = null;
        string path = $"{Folder}{id}.json";
        if (!FileAccess.FileExists(path))
            GD.PushError($"Cinématiques : fichier {path} introuvable.");
        else
        {
            string text = ReadAll(path);
            if (text != null)
            {
                if (CinematicParser.TryParse(text, out data, out var errors))
                {
                    if (data.Id != id)
                        GD.PushWarning($"Cinématiques : {path} porte l'id « {data.Id} » (le nom du fichier fait foi).");
                }
                else
                    GD.PushError($"Cinématiques : {path} invalide :\n  " + string.Join("\n  ", errors));
            }
        }
        Cache[id] = data; // même un échec est mémorisé : un seul message
        return data;
    }

    /// <summary>Vide les caches (tests).</summary>
    public static void Reset()
    {
        Cache.Clear();
        _scenarios = null;
        _scenariosLoaded = false;
    }

    private static ScenarioFile LoadScenarios()
    {
        if (_scenariosLoaded) return _scenarios;
        _scenariosLoaded = true;
        string path = Folder + ScenariosFile;
        if (!FileAccess.FileExists(path)) return null;
        string text = ReadAll(path);
        if (text != null && !CinematicParser.TryParseScenarios(text, out _scenarios, out var errors))
        {
            GD.PushError($"Cinématiques : {path} invalide :\n  " + string.Join("\n  ", errors));
            _scenarios = null;
        }
        return _scenarios;
    }

    /// <summary>Déclencheurs de repli de la salle (scenarios.json), dans l'ordre du fichier = ordre de priorité.</summary>
    public static List<ScenarioDef> GetFallbackScenarios(string roomStem)
    {
        var result = new List<ScenarioDef>();
        var file = LoadScenarios();
        if (file == null) return result;
        foreach (var s in file.Scenarios)
            if (s.Room == roomStem || s.Room.Length == 0)
                result.Add(s);
        return result;
    }

    public static bool TryGetFallbackPoint(string roomStem, string id, out Vector2 position)
    {
        position = Vector2.Zero;
        var file = LoadScenarios();
        if (file == null) return false;
        foreach (var p in file.Points)
            if (p.Room == roomStem && p.Id == id)
            {
                position = new Vector2(p.X, p.Y);
                return true;
            }
        return false;
    }

    private static string ReadAll(string path)
    {
        using var file = FileAccess.Open(path, FileAccess.ModeFlags.Read);
        if (file == null)
        {
            GD.PushError($"Cinématiques : impossible d'ouvrir {path} ({FileAccess.GetOpenError()}).");
            return null;
        }
        return file.GetAsText();
    }
}
