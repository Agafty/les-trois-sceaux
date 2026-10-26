using Godot;

/// <summary>Rend des PV (1 cœur = 2 PV). Reste au sol si la vie est pleine.</summary>
[GlobalClass]
public partial class HealEffect : PickupEffect
{
    [Export] public int Amount { get; set; } = 2;

    public override StringName PickupSound => Sfx.Coeur;

    public override bool CanApply(Player player, GameState state)
    {
        var health = player.Health;
        return health != null && health.CurrentHealth > 0 && health.CurrentHealth < health.MaxHealth;
    }

    public override void Apply(Player player, GameState state) => player.Health?.Heal(Amount);
}
