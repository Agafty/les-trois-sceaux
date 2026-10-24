/// <summary>Règle pure du butin de flèches « anti-blocage » (sans Godot).</summary>
public static class ArrowLootRule
{
    /// <summary>Vrai si un ennemi vaincu doit lâcher des flèches : Brann a l'arc mais moins de <paramref name="threshold"/> flèches.</summary>
    public static bool ShouldDrop(bool hasBow, int arrows, int threshold) => hasBow && arrows < threshold;
}
