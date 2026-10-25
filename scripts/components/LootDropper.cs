using Godot;

/// <summary>
/// Composant à placer à côté du nœud Health d'un ennemi : à sa mort, tire dans la table
/// de butin et fait apparaître le résultat à la position de l'ennemi.
/// Règle anti-blocage : si Brann a l'arc mais peu de flèches, l'ennemi lâche toujours des flèches
/// (désactivable avec <see cref="GuaranteeArrows"/>).
/// </summary>
public partial class LootDropper : Node
{
    [Export] public LootTable Table { get; set; }

    /// <summary>Décocher pour supprimer le butin de flèches garanti sur cet ennemi.</summary>
    [ExportGroup("Flèches garanties")]
    [Export] public bool GuaranteeArrows { get; set; } = true;

    /// <summary>Le butin garanti tombe si Brann a strictement moins de flèches que cette valeur.</summary>
    [Export(PropertyHint.Range, "1,30,1")] public int ArrowsBelow { get; set; } = 5;

    private const string ArrowsScenePath = "res://scenes/items/fleches.tscn";

    private Health _health;
    private GameState _state;

    public override void _Ready()
    {
        _state = GetNodeOrNull<GameState>("/root/GameState");
        PinTable(Table); // ressources C# : référence forte contre le ramasse-miettes (voir ResourceKeeper)
        _health = GetParent().GetNodeOrNull<Health>("Health");
        if (_health != null) _health.Died += OnDied;
    }

    private static void PinTable(LootTable table)
    {
        if (table == null) return;
        ResourceKeeper.Pin(table);
        if (table.Entries == null) return;
        for (int i = 0; i < table.Entries.Count; i++)
            ResourceKeeper.Pin(table.Entries[i]);
    }

    public override void _ExitTree()
    {
        if (_health != null && IsInstanceValid(_health)) _health.Died -= OnDied;
    }

    private void OnDied()
    {
        if (GetParent() is not Node2D enemy) return;
        var world = enemy.GetParent();
        if (world == null) return;

        // La table d'abord (cœurs, rubis...) ; les flèches garanties ne comblent que les tirages vides.
        PackedScene scene = Table?.Roll();
        if (scene == null && GuaranteeArrows && _state != null
            && ArrowLootRule.ShouldDrop(_state.HasItem(GameState.BowItemId), _state.GetQuantity(GameState.BowItemId), ArrowsBelow))
            scene = GD.Load<PackedScene>(ArrowsScenePath); // mis en cache par Godot
        if (scene == null) return;

        var loot = scene.Instantiate<Node2D>();
        // Différé : Died est émis pendant un callback physique (on ne peut pas ajouter un Area2D
        // à l'arbre à ce moment-là). Le parent survit à l'ennemi, donc pas de souci avec QueueFree.
        CallDeferredAdd(world, loot, enemy.GlobalPosition);
    }

    private static void CallDeferredAdd(Node world, Node2D loot, Vector2 pos)
    {
        Callable.From(() =>
        {
            if (!GodotObject.IsInstanceValid(world))
            {
                loot.Free();
                return;
            }
            world.AddChild(loot);
            loot.GlobalPosition = pos;
        }).CallDeferred();
    }
}
