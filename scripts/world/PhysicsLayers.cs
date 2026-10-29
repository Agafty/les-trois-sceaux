using Godot;

/// <summary>
/// Couches de collision 2D du projet (les noms sont déclarés dans project.godot, section [layer_names]).
/// La couche 1 (par défaut) est celle des murs, des corps et des zones de combat. La couche 5 « ravin » ne contient que
/// les cases de ravin : Brann, les ennemis et les blocs la voient (masque), pas les flèches ni le test de mur de l'arc.
/// </summary>
public static class PhysicsLayers
{
    /// <summary>Couche 5 (bit 4) : ravins.</summary>
    public const uint Ravine = 1u << 4;

    /// <summary>Groupe Godot des ennemis volants (chauve-souris) : la Room ne leur ajoute pas la couche ravin et ne les surveille pas pour les trous.</summary>
    public static readonly StringName FlyingGroup = "vol";

    /// <summary>Ajoute la couche des ravins au masque d'un corps qui doit être arrêté par eux (Brann, ennemis, PNJ).</summary>
    public static void BlockedByRavine(Node node)
    {
        if (node is CollisionObject2D body) body.CollisionMask |= Ravine;
    }
}
