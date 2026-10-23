using Godot;

/// <summary>
/// Quart de cœur : au 4e, la vie max augmente de <see cref="BonusMaxHealth"/> PV (soin complet).
/// Reste au sol quand la vie max est au plafond.
/// </summary>
[GlobalClass]
public partial class HeartPieceEffect : PickupEffect
{
    [Export] public int BonusMaxHealth { get; set; } = 2;

    public override bool CanApply(Player player, GameState state)
    {
        var health = player.Health;
        return health != null && health.CurrentHealth > 0 && health.MaxHealth < Health.MaxHealthCap;
    }

    public override void Apply(Player player, GameState state)
    {
        if (state.AddHeartPiece())
            player.Health?.IncreaseMax(BonusMaxHealth, true);
    }
}
