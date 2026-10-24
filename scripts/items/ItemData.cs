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

    /// <summary>Scène d'utilisation (use_item) : son script hérite de ItemUse. Vide = l'objet n'a pas encore d'effet.</summary>
    [Export] public PackedScene UseScene { get; set; }

    /// <summary>Unités consommées à chaque utilisation (si l'objet a une quantité).</summary>
    [Export(PropertyHint.Range, "0,10,1")] public int UseCost { get; set; } = 1;

    /// <summary>Nombre maximal d'instances de UseScene en même temps (0 = illimité). Bombes : 1.</summary>
    [Export(PropertyHint.Range, "0,10,1")] public int MaxSimultaneous { get; set; }

    /// <summary>
    /// Si un mur gêne le point de pose : vrai = l'utilisation est annulée sans rien consommer (flèche) ;
    /// faux = l'objet est posé contre le mur (bombe).
    /// </summary>
    [Export] public bool CancelIfBlocked { get; set; }

    /// <summary>Distance de pose devant Brann (px, depuis ses pieds). 0 = valeur par défaut du Player.</summary>
    [Export(PropertyHint.Range, "0,64,1")] public float UseDistance { get; set; }

    /// <summary>
    /// Pour CancelIfBlocked : longueur (px) dont on prolonge la vérification de mur au-delà du point de pose
    /// (la pointe de la flèche), pour qu'un mur juste devant la pointe annule aussi le tir.
    /// </summary>
    [Export(PropertyHint.Range, "0,64,1")] public float BlockCheckExtra { get; set; }

    public bool HasQuantity => MaxQuantity > 0;
}
