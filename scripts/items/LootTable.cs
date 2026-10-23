using Godot;
using Godot.Collections;

/// <summary>
/// Table de butin : avec une probabilité « rien », aucun objet ; sinon une entrée est tirée
/// selon son poids relatif (les poids n'ont pas besoin de totaliser 100).
/// </summary>
[GlobalClass]
public partial class LootTable : Resource
{
    [Export(PropertyHint.Range, "0,1,0.01")]
    public float NothingChance { get; set; } = 0.4f;

    [Export] public Array<LootEntry> Entries { get; set; } = new();

    /// <summary>Tire un butin ; renvoie null si « rien ».</summary>
    public PackedScene Roll()
    {
        if (Entries == null || Entries.Count == 0) return null;
        if (GD.Randf() < NothingChance) return null;

        float total = 0f;
        for (int i = 0; i < Entries.Count; i++)
            if (Entries[i] != null) total += Mathf.Max(0f, Entries[i].Weight);
        if (total <= 0f) return null;

        float pick = GD.Randf() * total;
        PackedScene last = null;
        for (int i = 0; i < Entries.Count; i++)
        {
            var entry = Entries[i];
            if (entry == null || entry.Weight <= 0f) continue;
            last = entry.Scene;
            pick -= entry.Weight;
            if (pick < 0f) return entry.Scene;
        }
        return last; // arrondi flottant : dernière entrée valide
    }
}
