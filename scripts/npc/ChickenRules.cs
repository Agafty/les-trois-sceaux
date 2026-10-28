using System.Collections.Generic;

/// <summary>
/// Règles du mini-jeu des poules de Pip (classe C# pure, sans Godot). Chaque poule attrapée est mémorisée par son id
/// (« village_poule_01 »...) parmi les ids uniques de GameState : le compteur est calculé, jamais stocké.
/// </summary>
public static class ChickenRules
{
    /// <summary>Début de l'id de toute poule du village.</summary>
    public const string IdPrefix = "village_poule_";

    /// <summary>Nombre de poules à attraper.</summary>
    public const int Total = 5;

    /// <summary>Id mémorisé quand les cinq sont attrapées : les dialogues de Pip s'en servent (flags: ["poules_toutes"]).</summary>
    public const string AllCaughtFlag = "poules_toutes";

    /// <summary>Id de la récompense (quart de cœur de Pip), mémorisé une fois donnée.</summary>
    public const string RewardId = "village_quart_coeur_poules";

    public static bool IsChickenId(string id) => id != null && id.StartsWith(IdPrefix, System.StringComparison.Ordinal);

    public static int Count(IEnumerable<string> collectedIds)
    {
        int count = 0;
        foreach (var id in collectedIds)
            if (IsChickenId(id)) count++;
        return count;
    }

    public static bool AllCaught(int count) => count >= Total;
}
