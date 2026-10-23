using Godot;

/// <summary>Une ligne de table de butin : une scène à faire apparaître et son poids relatif.</summary>
[GlobalClass]
public partial class LootEntry : Resource
{
    [Export] public PackedScene Scene { get; set; }

    [Export(PropertyHint.Range, "0,100,0.5")]
    public float Weight { get; set; } = 1f;
}
