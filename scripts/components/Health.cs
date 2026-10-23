using Godot;

public partial class Health : Node
{
    [Signal]
    public delegate void DamagedEventHandler(int amount);

    [Signal]
    public delegate void DiedEventHandler();

    [Signal]
    public delegate void HealthChangedEventHandler(int current, int max);

    [Export]
    public int MaxHealth { get; set; } = 10;

    public int CurrentHealth { get; private set; }

    public override void _Ready()
    {
        CurrentHealth = MaxHealth;
    }

    public void Damage(int amount)
    {
        if (CurrentHealth <= 0) return;

        int before = CurrentHealth;
        CurrentHealth = Mathf.Max(CurrentHealth - amount, 0);
        EmitSignal(SignalName.Damaged, amount);
        if (CurrentHealth != before)
            EmitSignal(SignalName.HealthChanged, CurrentHealth, MaxHealth);

        if (CurrentHealth == 0)
            EmitSignal(SignalName.Died);
    }

    public void Heal(int amount)
    {
        if (CurrentHealth <= 0 || amount <= 0) return;

        int before = CurrentHealth;
        CurrentHealth = Mathf.Min(CurrentHealth + amount, MaxHealth);
        if (CurrentHealth != before)
            EmitSignal(SignalName.HealthChanged, CurrentHealth, MaxHealth);
    }
}
