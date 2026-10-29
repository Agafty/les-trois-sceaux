using Godot;

/// <summary>
/// Prologue : trois écrans de texte sur fond noir au lancement d'une Nouvelle partie, avant la forge.
/// N'importe quelle touche ou bouton passe à l'écran suivant (un texte qui s'affiche encore est d'abord affiché en entier) ;
/// « pause » (Échap / Start) passe tout le prologue. À la fin : fondu vers <see cref="NextScene"/> (réglée par l'écran titre).
/// Ce n'est pas une Room : SaveSystem ne sauvegarde rien ici, la sauvegarde de départ se fait à l'arrivée dans la forge.
/// </summary>
public partial class PrologueScreen : Control
{
    /// <summary>Salle d'arrivée après le prologue et son point d'entrée (réglés par TitleScreen avant d'arriver ici).</summary>
    public static string NextScene { get; set; } = "res://scenes/rooms/forge_room.tscn";
    public static string NextSpawn { get; set; } = "depuis_village";

    private static readonly string[] PageKeys = { "PROLOGUE_1", "PROLOGUE_2", "PROLOGUE_3" };
    private static readonly StringName ActionSkip = "pause";
    private const float FadeInSeconds = 1.2f;
    private const float InputDelay = 0.5f;
    private const string ThemePath = "res://resources/ui/theme_jeu.tres";

    private SceneManager _sceneManager;
    private Label _text;
    private Label _next;
    private int _page = -1;
    private float _age;
    private bool _leaving;

    public override void _Ready()
    {
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        var theme = GD.Load<Theme>(ThemePath);
        if (theme != null) Theme = theme;

        var back = new ColorRect { Color = Colors.Black, MouseFilter = MouseFilterEnum.Ignore };
        back.SetAnchorsPreset(LayoutPreset.FullRect);
        AddChild(back);

        _text = new Label
        {
            Position = new Vector2(80f, 110f),
            Size = new Vector2(480f, 140f),
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        AddChild(_text);

        _next = new Label
        {
            Text = Tr("PROLOGUE_NEXT"),
            Position = new Vector2(80f, 300f),
            Size = new Vector2(480f, 16f),
            HorizontalAlignment = HorizontalAlignment.Center,
            Modulate = new Color(1f, 1f, 1f, 0.6f),
            MouseFilter = MouseFilterEnum.Ignore,
        };
        AddChild(_next);

        var skip = new Label
        {
            Text = Tr("PROLOGUE_SKIP"),
            Position = new Vector2(400f, 8f),
            Size = new Vector2(232f, 16f),
            HorizontalAlignment = HorizontalAlignment.Right,
            Modulate = new Color(1f, 1f, 1f, 0.45f),
            MouseFilter = MouseFilterEnum.Ignore,
        };
        AddChild(skip);

        ShowPage(0);
    }

    private void ShowPage(int index)
    {
        _page = index;
        _age = 0f;
        _text.Text = Tr(PageKeys[index]);
        _text.Modulate = new Color(1f, 1f, 1f, 0f);
        _next.Visible = false;
    }

    public override void _Process(double delta)
    {
        if (_leaving)
        {
            Leave(); // le fondu précédent était peut-être encore en cours : on réessaie
            return;
        }
        _age += (float)delta;
        float alpha = Mathf.Clamp(_age / FadeInSeconds, 0f, 1f);
        _text.Modulate = new Color(1f, 1f, 1f, alpha);
        _next.Visible = alpha >= 1f && ((int)(_age * 2f) & 1) == 0; // clignote quand le texte est entier
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (_leaving || !@event.IsPressed() || @event.IsEcho()) return;
        if (@event is not (InputEventKey or InputEventJoypadButton or InputEventMouseButton or InputEventAction)) return;
        if (@event.IsActionPressed(ActionSkip))
        {
            Leave();
            GetViewport().SetInputAsHandled();
            return;
        }
        if (_age < InputDelay) return;
        if (_age < FadeInSeconds)
        {
            _age = FadeInSeconds; // texte affiché en entier d'abord
        }
        else if (_page + 1 < PageKeys.Length)
            ShowPage(_page + 1);
        else
            Leave();
        GetViewport().SetInputAsHandled();
    }

    private void Leave()
    {
        _leaving = true;
        if (_sceneManager.GoToScene(NextScene, NextSpawn))
            SetProcess(false);
    }
}
