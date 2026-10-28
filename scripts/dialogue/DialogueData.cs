using System;
using System.Collections.Generic;
using System.Text.Json;

/// <summary>
/// Dialogues d'un personnage, lus depuis resources/dialogues/&lt;id&gt;.json (classe C# pure, testable hors du moteur).
/// Format : { "speaker": "PNJ_HULDA", "entries": [ { "stage": 0, "flags": [], "not_flags": [], "cycle": false, "lines": ["CLE1", "CLE2"], "reward": { "contenu": "quart_coeur", "id": "village_quart_coeur_poules" } } ] }
/// (« reward » est facultatif : récompense donnée à la fin de la conversation, une seule fois grâce à son id.)
/// </summary>
public sealed class DialogueData
{
    /// <summary>Clé de traduction du nom affiché.</summary>
    public string Speaker { get; init; } = "";

    public IReadOnlyList<DialogueEntry> Entries { get; init; } = Array.Empty<DialogueEntry>();

    /// <summary>Lit un JSON de dialogues. Lève <see cref="FormatException"/> avec un message clair s'il est invalide.</summary>
    public static DialogueData Parse(string json)
    {
        try
        {
            using var doc = JsonDocument.Parse(json, new JsonDocumentOptions { CommentHandling = JsonCommentHandling.Skip, AllowTrailingCommas = true });
            var root = doc.RootElement;
            if (root.ValueKind != JsonValueKind.Object) throw new FormatException("la racine doit être un objet");

            string speaker = root.TryGetProperty("speaker", out var s) && s.ValueKind == JsonValueKind.String ? s.GetString() ?? "" : "";
            var entries = new List<DialogueEntry>();
            if (root.TryGetProperty("entries", out var list))
            {
                if (list.ValueKind != JsonValueKind.Array) throw new FormatException("« entries » doit être une liste");
                int index = 0;
                foreach (var e in list.EnumerateArray())
                    entries.Add(ParseEntry(e, index++));
            }
            return new DialogueData { Speaker = speaker, Entries = entries };
        }
        catch (JsonException ex)
        {
            throw new FormatException("JSON invalide : " + ex.Message, ex);
        }
    }

    private static DialogueEntry ParseEntry(JsonElement e, int index)
    {
        if (e.ValueKind != JsonValueKind.Object) throw new FormatException($"entrée {index} : un objet est attendu");
        int? stage = null;
        if (e.TryGetProperty("stage", out var st))
        {
            if (st.ValueKind != JsonValueKind.Number || !st.TryGetInt32(out int value) || value < 0 || value > StoryRules.MaxStage)
                throw new FormatException($"entrée {index} : « stage » doit être un entier de 0 à {StoryRules.MaxStage}");
            stage = value;
        }
        var lines = ReadStrings(e, "lines", index);
        if (lines.Count == 0) throw new FormatException($"entrée {index} : « lines » est vide ou absente");
        return new DialogueEntry
        {
            Stage = stage,
            Flags = ReadStrings(e, "flags", index),
            NotFlags = ReadStrings(e, "not_flags", index),
            Reward = ReadReward(e, index),
            Cycle = e.TryGetProperty("cycle", out var c) && c.ValueKind == JsonValueKind.True,
            Lines = lines,
        };
    }

    private static DialogueReward ReadReward(JsonElement e, int index)
    {
        if (!e.TryGetProperty("reward", out var r)) return null;
        if (r.ValueKind != JsonValueKind.Object) throw new FormatException($"entrée {index} : « reward » doit être un objet {{ \"contenu\": ..., \"id\": ... }}");
        string content = r.TryGetProperty("contenu", out var c) && c.ValueKind == JsonValueKind.String ? c.GetString() ?? "" : "";
        string id = r.TryGetProperty("id", out var i) && i.ValueKind == JsonValueKind.String ? i.GetString() ?? "" : "";
        if (!RoomObjectCatalog.IsSafeName(content)) throw new FormatException($"entrée {index} : « reward.contenu » invalide (nom de fichier de resources/pickups/ en minuscules)");
        if (!RoomObjectCatalog.IsSafeName(id)) throw new FormatException($"entrée {index} : « reward.id » invalide (minuscules, chiffres et _)");
        return new DialogueReward { Content = content, Id = id };
    }

    private static List<string> ReadStrings(JsonElement e, string name, int index)
    {
        var result = new List<string>();
        if (!e.TryGetProperty(name, out var arr)) return result;
        if (arr.ValueKind != JsonValueKind.Array) throw new FormatException($"entrée {index} : « {name} » doit être une liste de textes");
        foreach (var item in arr.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.String || string.IsNullOrEmpty(item.GetString()))
                throw new FormatException($"entrée {index} : « {name} » ne contient que des textes non vides");
            result.Add(item.GetString());
        }
        return result;
    }
}
