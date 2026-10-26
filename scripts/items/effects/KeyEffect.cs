using Godot;

/// <summary>Ajoute des petites clés.</summary>
[GlobalClass]
public partial class KeyEffect : PickupEffect
{
    [Export] public int Amount { get; set; } = 1;

    public override StringName PickupSound => Sfx.Cle;

    public override bool CanApply(Player player, GameState state) => true;

    public override void Apply(Player player, GameState state) => state.AddKeys(Amount);
}
