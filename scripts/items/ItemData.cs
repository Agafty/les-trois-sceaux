using Godot;

/// <summary>
/// Description d'un objet d'inventaire (donnée pure, éditable dans l'inspecteur).
/// Les fichiers .tres vivent dans resources/items/ ; GameState les charge tous au démarrage.
/// </summary>
[GlobalClass]
public partial class ItemData : Resource
{
    /// <summary>Identifiant stable (sauvegarde, cartes Tiled), ex. "arc".</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Clé de traduction du nom (affichée via Tr()).</summary>
    [Export] public string NameKey { get; set; } = "";

    /// <summary>Clé de traduction de la description (affichée via Tr()).</summary>
    [Export] public string DescriptionKey { get; set; } = "";

    /// <summary>Icône 24x24.</summary>
    [Export] public Texture2D Icon { get; set; }

    [Export] public ItemType Type { get; set; } = ItemType.Equipable;

    /// <summary>Quantité maximale ; 0 = objet sans quantité (on le possède ou non).</summary>
    [Export(PropertyHint.Range, "0,99,1")] public int MaxQuantity { get; set; }

    public bool HasQuantity => MaxQuantity > 0;
}
