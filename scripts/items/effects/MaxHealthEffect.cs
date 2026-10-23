using Godot;

/// <summary>Réceptacle de cœur : augmente la vie max (2 = un cœur) et soigne complètement.</summary>
[GlobalClass]
public partial class MaxHealthEffect : PickupEffect
{
    [Export] public int Amount { get; set; } = 2;

    public override bool CanApply(Player player, GameState state)
    {
        var health = player.Health;
        return health != null && health.CurrentHealth > 0 && health.MaxHealth < Health.MaxHealthCap;
    }

    public override void Apply(Player player, GameState state) => player.Health?.IncreaseMax(Amount, true);
}
