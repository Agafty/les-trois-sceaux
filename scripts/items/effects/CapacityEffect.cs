using Godot;

/// <summary>
/// Amélioration de capacité (grand carquois, grand sac de bombes) : fixe le bonus de quantité maximale d'un objet à <see cref="Bonus"/>
/// (arc +20 = 30 à 50 flèches, bombes +10 = 10 à 20) et remplit le stock au nouveau maximum, comme dans A Link to the Past.
/// Refusée si le bonus est déjà acquis, ou si l'objet n'est pas encore possédé (on n'achète pas un carquois sans arc).
/// </summary>
[GlobalClass]
public partial class CapacityEffect : PickupEffect
{
    /// <summary>Id de l'objet amélioré (« arc » pour les flèches, « bombes »).</summary>
    [Export] public string ItemId { get; set; } = "";

    /// <summary>Bonus TOTAL de capacité une fois l'amélioration acquise (pas un ajout).</summary>
    [Export(PropertyHint.Range, "1,90,1")] public int Bonus { get; set; } = 20;

    /// <summary>Vrai si l'objet amélioré n'est pas possédé (sert au message de la boutique).</summary>
    public bool IsMissingItem(GameState state) => !state.HasItem(ItemId);

    public override bool CanApply(Player player, GameState state) =>
        !string.IsNullOrEmpty(ItemId) && state.HasItem(ItemId) && state.GetCapacityBonus(ItemId) < Bonus;

    public override void Apply(Player player, GameState state) => state.UpgradeCapacity(ItemId, Bonus);
}
