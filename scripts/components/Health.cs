using Godot;

public partial class Health : Node
{
    [Signal]
    public delegate void DamagedEventHandler(int amount);

    [Signal]
    public delegate void DiedEventHandler();

    [Signal]
    public delegate void HealthChangedEventHandler(int current, int max);

    /// <summary>Plafond de la vie max du joueur : 9 cœurs = 18 PV.</summary>
    public const int MaxHealthCap = GameState.MaxPlayerHealth;

    [Export]
    public int MaxHealth { get; set; } = 10;

    public int CurrentHealth { get; private set; }

    public override void _Ready()
    {
        CurrentHealth = MaxHealth;
    }

    /// <summary>
    /// Fixe directement la vie (restauration depuis GameState). N'émet aucun signal,
    /// donc ni Died ni HealthChanged : évite les boucles avec l'état global.
    /// </summary>
    public void SetValues(int current, int max)
    {
        MaxHealth = max;
        CurrentHealth = Mathf.Clamp(current, 0, max);
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

    /// <summary>
    /// Augmente la vie maximale (réceptacle de cœur), plafonnée à <see cref="MaxHealthCap"/>.
    /// Si <paramref name="healFully"/> est vrai, la vie est remplie. Émet HealthChanged.
    /// </summary>
    public bool IncreaseMax(int amount, bool healFully)
    {
        if (amount <= 0 || CurrentHealth <= 0 || MaxHealth >= MaxHealthCap) return false;

        MaxHealth = Mathf.Min(MaxHealth + amount, MaxHealthCap);
        if (healFully)
            CurrentHealth = MaxHealth;
        EmitSignal(SignalName.HealthChanged, CurrentHealth, MaxHealth);
        return true;
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
