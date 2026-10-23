using Godot;

/// <summary>Donne un objet d'inventaire (arc, bombes...). Le premier équipable obtenu est équipé d'office.</summary>
[GlobalClass]
public partial class GiveItemEffect : PickupEffect
{
    [Export] public ItemData Item { get; set; }

    [Export(PropertyHint.Range, "1,99,1")] public int Quantity { get; set; } = 1;

    // Bombes déjà au maximum : l'objet reste au sol.
    public override bool CanApply(Player player, GameState state) => Item != null && state.CanAddItem(Item);

    public override void Apply(Player player, GameState state) => state.AddItem(Item, Quantity);
}
