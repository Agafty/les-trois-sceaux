using Godot;

/// <summary>
/// Sceau restauré (récompense d'un boss) : ajoute son id à la liste des sceaux de GameState, sauvegardée.
/// Le compteur de progression du jeu est le nombre de sceaux (3 à la fin). L'image est
/// art/items/sceau_racines.png (propriété Icon du .tres).
/// </summary>
[GlobalClass]
public partial class SealEffect : PickupEffect
{
    /// <summary>Identifiant du sceau, ex. « racines ».</summary>
    [Export] public string SealId { get; set; } = "racines";

    public override bool CanApply(Player player, GameState state) => !string.IsNullOrEmpty(SealId);

    public override void Apply(Player player, GameState state) => state.AddSeal(SealId);
}
