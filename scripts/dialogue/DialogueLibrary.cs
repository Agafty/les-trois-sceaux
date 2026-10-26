using System.Collections.Generic;
using Godot;

/// <summary>
/// Charge (une seule fois) les dialogues JSON de resources/dialogues/&lt;id&gt;.json. Un fichier absent ou invalide donne une erreur claire
/// puis null (le PNJ reste muet) : le jeu ne plante jamais pour un dialogue. Thread principal uniquement.
/// </summary>
public static class DialogueLibrary
{
    private const string Folder = "res://resources/dialogues/";
    private static readonly Dictionary<string, DialogueData> Cache = new();

    public static DialogueData Get(string id)
    {
        if (!RoomObjectCatalog.IsSafeName(id))
        {
            GD.PushError($"Dialogues : id invalide « {id} » (lettres minuscules, chiffres et _ seulement).");
            return null;
        }
        if (Cache.TryGetValue(id, out var cached)) return cached;

        DialogueData data = null;
        string path = $"{Folder}{id}.json";
        if (!FileAccess.FileExists(path))
        {
            GD.PushWarning($"Dialogues : fichier {path} introuvable, le personnage « {id} » restera muet.");
        }
        else
        {
            try
            {
                using var file = FileAccess.Open(path, FileAccess.ModeFlags.Read);
                if (file == null)
                    GD.PushError($"Dialogues : impossible d'ouvrir {path} ({FileAccess.GetOpenError()}).");
                else
                    data = DialogueData.Parse(file.GetAsText());
            }
            catch (System.FormatException e)
            {
                GD.PushError($"Dialogues : {path} invalide ({e.Message}).");
            }
        }
        Cache[id] = data; // même un échec est mémorisé : un seul message
        return data;
    }
}
