using System.Collections.Generic;

/// <summary>
/// Registre C# des objets sensibles à la lanterne (comme <see cref="Bomb.Register"/>) : <c>LanternLight</c> le parcourt
/// sans rechercher de nœuds ni allouer. Thread principal uniquement.
/// </summary>
public static class LanternRegistry
{
    private static readonly List<ILanternReactive> Items = new();

    /// <summary>Liste en lecture, à parcourir par indice en sens inverse (un objet peut se retirer pendant le parcours).</summary>
    public static List<ILanternReactive> All => Items;

    public static void Register(ILanternReactive target)
    {
        if (target == null || Items.Contains(target)) return;
        target.LanternTimer = 0f;
        Items.Add(target);
    }

    public static void Unregister(ILanternReactive target) => Items.Remove(target);
}
