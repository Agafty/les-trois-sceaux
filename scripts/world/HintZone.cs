using Godot;

/// <summary>
/// Rectangle d'indice (objet Tiled « indice_... » avec godot_node_type=area) : tant que Brann est dans la zone, la boîte de texte
/// de la salle (<see cref="HintBox"/>, partagée) affiche le texte traduit (clé = nom en majuscules, voir <see cref="HintRules"/>).
/// Choix : le texte s'affiche dès l'entrée dans la zone, sans bouton (plus simple pour un jeune joueur) et disparaît à la sortie.
/// Créé par la <see cref="Room"/>.
/// </summary>
public partial class HintZone : Node
{
    /// <summary>La zone Area2D importée depuis Tiled.</summary>
    public Area2D Zone { get; set; }

    /// <summary>Clé de traduction du texte (colonne « keys » de textes.csv).</summary>
    public string TextKey { get; set; } = "";

    /// <summary>La boîte de texte partagée de la salle.</summary>
    public HintBox Box { get; set; }

    /// <summary>Vrai tant que le texte de cette zone est celui qui est affiché.</summary>
    public bool IsShown => Box != null && Box.IsShown && Box.Text == Tr(TextKey);

    public override void _Ready()
    {
        if (Zone == null) return;
        Zone.BodyEntered += OnBodyEntered;
        Zone.BodyExited += OnBodyExited;
    }

    public override void _ExitTree()
    {
        if (Zone == null || !IsInstanceValid(Zone)) return;
        Zone.BodyEntered -= OnBodyEntered;
        Zone.BodyExited -= OnBodyExited;
    }

    private void OnBodyEntered(Node2D body)
    {
        if (body is Player) Box?.Enter(this);
    }

    private void OnBodyExited(Node2D body)
    {
        if (body is Player) Box?.Leave(this);
    }
}
