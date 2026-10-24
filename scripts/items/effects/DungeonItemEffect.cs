using Godot;

/// <summary>
/// Objet propre à un donjon : carte, boussole ou grande clé. La zone du donjon est celle de la salle courante
/// (propriété Zone de Room), donc le même fichier .tres sert à tous les donjons.
/// </summary>
[GlobalClass]
public partial class DungeonItemEffect : PickupEffect
{
    /// <summary>« carte », « boussole » ou « grande_cle » (voir <see cref="DungeonItems"/>).</summary>
    [Export(PropertyHint.Enum, "carte,boussole,grande_cle")] public string Kind { get; set; } = DungeonItems.Map;

    // Déjà possédé : le contenu reste inutilisable (le coffre avertit, un ramassable reste au sol).
    public override bool CanApply(Player player, GameState state) =>
        !state.HasDungeonItem(Room.ZoneOf(player), Kind);

    public override void Apply(Player player, GameState state) =>
        state.AddDungeonItem(Room.ZoneOf(player), Kind);
}
