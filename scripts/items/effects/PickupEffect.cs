using Godot;

/// <summary>
/// Effet d'un ramassable (donnée éditable dans l'inspecteur). Le Pickup décide du « comment »
/// (détection, rebond, durée de vie) ; l'effet décide du « quoi » et de s'il peut s'appliquer.
/// </summary>
[GlobalClass]
public abstract partial class PickupEffect : Resource
{
    /// <summary>Faux si l'objet doit rester au sol (ex. cœur à vie pleine).</summary>
    public abstract bool CanApply(Player player, GameState state);

    public abstract void Apply(Player player, GameState state);
}
