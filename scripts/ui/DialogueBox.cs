using Godot;

/// <summary>
/// Boîte de texte d'un personnage (nom, puis réplique) en bas de l'écran, même cadre que les indices. Le jeu n'est pas mis en pause :
/// elle se ferme quand le joueur appuie sur « interact » ou « attack » (après un court délai) ou au bout de <see cref="MaxSeconds"/>.
/// Les textes sont des clés de traduction (jamais en dur).
/// </summary>
public partial class DialogueBox : CanvasLayer
{
    /// <summary>Boîte ouverte sous ce nœud (null si aucune).</summary>
    public static DialogueBox Open(Node owner, string speakerKey, string textKey, float maxSeconds = 8f)
    {
        var box = new DialogueBox { Name = "BoiteDialogue", Layer = 6, MaxSeconds = maxSeconds };
        owner.AddChild(box);
        box.Build(speakerKey, textKey);
        return box;
    }

    public float MaxSeconds { get; set; } = 8f;

    /// <summary>Texte affiché (nom et réplique).</summary>
    public string Text => _label?.Text ?? "";

    private const string ThemePath = "res://resources/ui/theme_jeu.tres";
    private const float MinSeconds = 1.2f;
    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName ActionAttack = "attack";
    private static readonly Color BackColor = new(0.1f, 0.08f, 0.13f, 0.92f);
    private static readonly Rect2 BoxRect = new(16f, 272f, 608f, 64f);

    private Label _label;
    private float _age;

    private void Build(string speakerKey, string textKey)
    {
        var back = new ColorRect { Color = BackColor, Position = BoxRect.Position, Size = BoxRect.Size, MouseFilter = Control.MouseFilterEnum.Ignore };
        _label = new Label
        {
            Position = BoxRect.Position + new Vector2(8f, 6f),
            Size = BoxRect.Size - new Vector2(16f, 12f),
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            HorizontalAlignment = HorizontalAlignment.Left,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        var theme = GD.Load<Theme>(ThemePath);
        if (theme != null) _label.Theme = theme;
        string speaker = string.IsNullOrEmpty(speakerKey) ? "" : Tr(speakerKey) + "\n";
        _label.Text = speaker + Tr(textKey);
        AddChild(back);
        AddChild(_label);
    }

    public override void _Process(double delta)
    {
        _age += (float)delta;
        bool dismissed = _age >= MinSeconds
            && (Input.IsActionJustPressed(ActionInteract) || Input.IsActionJustPressed(ActionAttack));
        if (dismissed || _age >= MaxSeconds)
            QueueFree();
    }
}
