using System;
using System.Collections.Generic;

/// <summary>Une ligne d'inventaire sauvegardée : id de l'objet et quantité (1 pour un objet sans quantité).</summary>
public class SaveInventoryEntry
{
    public string Id { get; set; } = "";
    public int Quantity { get; set; } = 1;
}

/// <summary>
/// Contenu d'un fichier de sauvegarde. Classe C# pure (aucune dépendance à Godot) :
/// sérialisée en JSON par <see cref="SaveSerializer"/> et testable hors du moteur.
/// </summary>
public class SaveData
{
    /// <summary>Version du format écrite par cette version du jeu. À incrémenter quand le format change.</summary>
    public const int CurrentVersion = 2;

    /// <summary>0 = absente du fichier : sera rejetée par la migration. SaveSystem écrit CurrentVersion à la sauvegarde.</summary>
    public int Version { get; set; }
    public DateTime SavedAtUtc { get; set; }
    public double PlayTimeSeconds { get; set; }

    public int Health { get; set; }
    public int MaxHealth { get; set; }
    public int HeartPieces { get; set; }
    public int Rupees { get; set; }
    public int Keys { get; set; }

    /// <summary>Objets possédés, dans l'ordre d'obtention (une liste garde l'ordre, contrairement à un dictionnaire).</summary>
    public List<SaveInventoryEntry> Inventory { get; set; } = new();
    public string EquippedItemId { get; set; } = "";

    /// <summary>Ids uniques déjà utilisés : coffres, ramassables uniques, portes ouvertes...</summary>
    public List<string> CollectedIds { get; set; } = new();

    /// <summary>Version 2. Objets de donjon possédés, sous la forme « zone/type » (ex. « donjon1/grande_cle »).</summary>
    public List<string> DungeonItems { get; set; } = new();

    /// <summary>Version 2. Plumes de corbeau trouvées.</summary>
    public int RavenFeathers { get; set; }

    /// <summary>Position de reprise : chemin de la scène (carte) et id du Spawn, jamais des coordonnées.</summary>
    public string ScenePath { get; set; } = "";
    public string SpawnId { get; set; } = "";
}
