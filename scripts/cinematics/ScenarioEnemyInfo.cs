using Godot;

/// <summary>
/// Un ennemi de la carte marqué « apparition = scenario » : la salle retient son type, sa variante, son groupe (propriété Tiled « groupe », facultative)
/// et sa position, mais ne le crée que lorsqu'une cinématique le demande (action « apparaitre » cible « ennemis »).
/// </summary>
public sealed class ScenarioEnemyInfo
{
    public string Type { get; }
    public string Variant { get; }
    public string Group { get; }
    public Vector2 Position { get; }

    public ScenarioEnemyInfo(string type, string variant, string group, Vector2 position)
    {
        Type = type;
        Variant = variant;
        Group = group;
        Position = position;
    }
}
