using Godot;

/// <summary>
/// Effet d'un ramassable (donnée éditable dans l'inspecteur). Le Pickup décide du « comment »
/// (détection, rebond, durée de vie) ; l'effet décide du « quoi » et de s'il peut s'appliquer.
/// </summary>
[GlobalClass]
public abstract partial class PickupEffect : Resource
{
    /// <summary>Icône montrée quand l'effet est obtenu dans un coffre (vide : voir <see cref="GetIcon"/>).</summary>
    [Export] public Texture2D Icon { get; set; }

    /// <summary>Clé de traduction du nom montré dans un coffre (« Vous obtenez : ... »).</summary>
    [Export] public string NameKey { get; set; } = "";

    public virtual Texture2D GetIcon() => Icon;

    public virtual string GetNameKey() => NameKey;

    /// <summary>Faux si l'objet doit rester au sol (ex. cœur à vie pleine).</summary>
    public abstract bool CanApply(Player player, GameState state);

    public abstract void Apply(Player player, GameState state);
}
