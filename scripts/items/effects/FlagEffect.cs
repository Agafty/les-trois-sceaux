using Godot;

/// <summary>
/// Objet d'histoire sans inventaire : pose un drapeau dans GameState (ex. « epee_bois », « epee_corvan ») ou ne fait rien de plus que
/// montrer son nom (le charbon : c'est l'id unique du ramassable qui est mémorisé). Sert aux objets de l'ouverture.
/// </summary>
[GlobalClass]
public partial class FlagEffect : PickupEffect
{
    /// <summary>Drapeau posé à l'obtention (vide : aucun).</summary>
    [Export] public string Flag { get; set; } = "";

    public override bool CanApply(Player player, GameState state) => true;

    public override void Apply(Player player, GameState state)
    {
        if (!string.IsNullOrEmpty(Flag)) state.MarkCollected(Flag);
    }
}
