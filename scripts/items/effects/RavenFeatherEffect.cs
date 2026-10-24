using Godot;

/// <summary>Plume de corbeau : ajoute 1 au compteur de GameState (sauvegardé).</summary>
[GlobalClass]
public partial class RavenFeatherEffect : PickupEffect
{
    public override bool CanApply(Player player, GameState state) => true;

    public override void Apply(Player player, GameState state) => state.AddRavenFeather();
}
