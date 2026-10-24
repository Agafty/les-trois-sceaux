using Godot;

/// <summary>Donne un objet d'inventaire (arc, bombes...). Le premier équipable obtenu est équipé d'office.</summary>
[GlobalClass]
public partial class GiveItemEffect : PickupEffect
{
    [Export] public ItemData Item { get; set; }

    [Export(PropertyHint.Range, "1,99,1")] public int Quantity { get; set; } = 1;

    /// <summary>Vrai pour des munitions (flèches = quantité de l'arc) : sans l'objet, le ramassable reste au sol.</summary>
    [Export] public bool OnlyIfOwned { get; set; }

    /// <summary>Icône affichée au sol à la place de celle de l'objet (ex. une flèche plutôt qu'un arc).</summary>
    [Export] public Texture2D PickupIcon { get; set; }

    // Objet déjà au maximum (ou munitions sans l'arc) : le ramassable reste au sol.
    public override bool CanApply(Player player, GameState state) =>
        Item != null && state.CanAddItem(Item) && (!OnlyIfOwned || state.HasItem(Item.Id));

    public override void Apply(Player player, GameState state) => state.AddItem(Item, Quantity);
}
