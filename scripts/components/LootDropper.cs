using Godot;

/// <summary>
/// Composant à placer à côté du nœud Health d'un ennemi : à sa mort, tire dans la table
/// de butin et fait apparaître le résultat à la position de l'ennemi.
/// </summary>
public partial class LootDropper : Node
{
    [Export] public LootTable Table { get; set; }

    private Health _health;

    public override void _Ready()
    {
        _health = GetParent().GetNodeOrNull<Health>("Health");
        if (_health != null) _health.Died += OnDied;
    }

    public override void _ExitTree()
    {
        if (_health != null && IsInstanceValid(_health)) _health.Died -= OnDied;
    }

    private void OnDied()
    {
        if (Table == null) return;
        if (GetParent() is not Node2D enemy) return;
        var world = enemy.GetParent();
        if (world == null) return;

        var scene = Table.Roll();
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
