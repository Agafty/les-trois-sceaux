using Godot;

/// <summary>
/// Autoload : état global de la partie. Pour l'instant, seulement la bourse de rubis.
/// Étendu en Phase 3 (inventaire, coffres ouverts, sauvegarde...).
/// </summary>
public partial class GameState : Node
{
    public const int MaxRupees = 300;

    [Signal]
    public delegate void RupeesChangedEventHandler(int total);

    public int Rupees { get; private set; }

    /// <summary>Ajoute (ou retire si négatif) des rubis, borné entre 0 et <see cref="MaxRupees"/>.</summary>
    public void AddRupees(int amount)
    {
        int newTotal = Mathf.Clamp(Rupees + amount, 0, MaxRupees);
        if (newTotal == Rupees) return;

        Rupees = newTotal;
        EmitSignal(SignalName.RupeesChanged, Rupees);
        GD.Print($"Rubis : {Rupees}/{MaxRupees}");
    }
}
