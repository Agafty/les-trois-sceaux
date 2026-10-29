/// <summary>Règle pure du butin de bombes « anti-blocage » (sans Godot), sur le modèle de <see cref="ArrowLootRule"/>.</summary>
public static class BombLootRule
{
    /// <summary>Vrai si un ennemi vaincu doit lâcher des bombes : Brann possède les bombes mais en a moins de <paramref name="threshold"/>.</summary>
    public static bool ShouldDrop(bool hasBombs, int bombs, int threshold) => hasBombs && bombs < threshold;
}
