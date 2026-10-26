using Godot;

/// <summary>Ajoute des rubis à la bourse.</summary>
[GlobalClass]
public partial class RupeeEffect : PickupEffect
{
    [Export] public int Amount { get; set; } = 1;

    public override StringName PickupSound => Sfx.Rubis;

    public override bool CanApply(Player player, GameState state) => true;

    public override void Apply(Player player, GameState state) => state.AddRupees(Amount);
}
