using Godot;

/// <summary>
/// Autoload : état persistant de la partie (rubis, vie du joueur, clés).
/// Étendu en Phase 3 (inventaire, coffres ouverts, sauvegarde...).
/// </summary>
public partial class GameState : Node
{
    public const int MaxRupees = 300;
    public const int StartMaxHealth = 6;
    public const int RespawnHealth = 6; // reprise avec 3 cœurs

    [Signal]
    public delegate void RupeesChangedEventHandler(int total);

    [Signal]
    public delegate void PlayerHealthChangedEventHandler(int current, int max);

    [Signal]
    public delegate void KeysChangedEventHandler(int total);

    public int Rupees { get; private set; }

    /// <summary>Points de vie du joueur (1 PV = un demi-cœur).</summary>
    public int PlayerHealth { get; private set; } = StartMaxHealth;

    public int PlayerMaxHealth { get; private set; } = StartMaxHealth;

    /// <summary>Petites clés possédées.</summary>
    public int Keys { get; private set; }

    /// <summary>Ajoute (ou retire si négatif) des rubis, borné entre 0 et <see cref="MaxRupees"/>.</summary>
    public void AddRupees(int amount)
    {
        int newTotal = Mathf.Clamp(Rupees + amount, 0, MaxRupees);
        if (newTotal == Rupees) return;

        Rupees = newTotal;
        EmitSignal(SignalName.RupeesChanged, Rupees);
    }

    /// <summary>Fixe la vie du joueur (et son maximum). N'émet le signal que si quelque chose change.</summary>
    public void SetPlayerHealth(int current, int max)
    {
        max = Mathf.Max(max + (max & 1), 2); // arrondi au pair (cœurs entiers)
        current = Mathf.Clamp(current, 0, max);
        if (current == PlayerHealth && max == PlayerMaxHealth) return;

        PlayerHealth = current;
        PlayerMaxHealth = max;
        EmitSignal(SignalName.PlayerHealthChanged, PlayerHealth, PlayerMaxHealth);
    }

    /// <summary>
    /// Prépare la reprise après la mort : stocke la vie de reprise SANS émettre de signal,
    /// pour que l'état ne reste jamais à 0 PV (sauvegarde) et que le HUD garde 0 cœur pendant l'animation de mort.
    /// </summary>
    public void PrepareRespawn()
    {
        PlayerHealth = Mathf.Min(RespawnHealth, PlayerMaxHealth);
    }

    /// <summary>Ajoute (ou retire si négatif) des petites clés, jamais sous 0.</summary>
    public void AddKeys(int amount)
    {
        int newTotal = Mathf.Max(Keys + amount, 0);
        if (newTotal == Keys) return;

        Keys = newTotal;
        EmitSignal(SignalName.KeysChanged, Keys);
    }
}
