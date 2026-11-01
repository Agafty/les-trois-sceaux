using Godot;

/// <summary>
/// Petit menu « Système » du menu pause : Retour à l'écran titre / Quitter le jeu, avec confirmation Oui/Non
/// (Non par défaut). Même principe que <see cref="OptionsMenu"/> : <see cref="Open"/>, puis signal <see cref="Closed"/>
/// (annulation). Si le joueur confirme, le menu déclenche lui-même le retour au titre (fondu) ou ferme le jeu et émet
/// <see cref="LeaveRequested"/> pour que le menu pause se referme et remette le jeu hors pause.
/// </summary>
public partial class SystemMenu : Control
{
    [Signal]
    public delegate void ClosedEventHandler();

    /// <summary>Le joueur a confirmé : le menu pause doit se refermer (le jeu sort de la pause).</summary>
    [Signal]
    public delegate void LeaveRequestedEventHandler();

    private enum Page { Choice, Confirm }

    private const string TitleScenePath = "res://scenes/ui/ecran_titre.tscn";
    private const int RowHeight = 22;

    private static readonly StringName ActionUp = "move_up";
    private static readonly StringName ActionDown = "move_down";
    private static readonly StringName ActionUiUp = "ui_up";
    private static readonly StringName ActionUiDown = "ui_down";
    private static readonly StringName ActionAttack = "attack";
    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName ActionAccept = "ui_accept";
    private static readonly StringName ActionBack = "pause";
    private static readonly StringName ActionSelf = "quit_page";
    private static readonly StringName PanelStyleName = "panel";

    private static readonly Vector2 PanelPos = new(150, 100);
    private static readonly Vector2 PanelSize = new(340, 170);
    private static readonly Color SelectedColor = new(1f, 0.85f, 0.4f);

    private readonly Label[] _rows = new Label[3];
    private readonly string[] _texts = new string[3];
    private Label _heading;
    private Page _page;
    private bool _toTitle; // choix en cours de confirmation : vrai = titre, faux = quitter
    private int _rowCount;
    private int _selected;
    private bool _open;
    private bool _skipInput;
    private SceneManager _sceneManager;

    public bool IsOpen => _open;

    public override void _Ready()
    {
        ProcessMode = ProcessModeEnum.Always;
        Visible = false;
        SetProcess(false);
        SetAnchorsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop;
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        BuildUi();
    }

    public void Open()
    {
        _open = true;
        _skipInput = true; // l'appui qui ouvre le menu ne doit pas le valider
        Visible = true;
        SetProcess(true);
        ShowChoice(0);
        AudioManager.Play(Sfx.MenuValide);
    }

    private void Close()
    {
        _open = false;
        Visible = false;
        SetProcess(false);
        TextReader.Stop(TextSource.Dialogue);
        AudioManager.Play(Sfx.MenuRetour);
        EmitSignal(SignalName.Closed);
    }

    public override void _Process(double delta)
    {
        if (_skipInput)
        {
            _skipInput = false;
            return;
        }
        if (_sceneManager.IsTransitioning) return; // retour au titre en cours : plus de choix possible

        if (Input.IsActionJustPressed(ActionDown) || Input.IsActionJustPressed(ActionUiDown)) Move(1);
        else if (Input.IsActionJustPressed(ActionUp) || Input.IsActionJustPressed(ActionUiUp)) Move(-1);
        else if (Input.IsActionJustPressed(ActionAttack) || Input.IsActionJustPressed(ActionInteract)
                 || Input.IsActionJustPressed(ActionAccept)) Validate();
        else if (Input.IsActionJustPressed(ActionBack) || Input.IsActionJustPressed(ActionSelf)) GoBack();
    }

    private void ShowChoice(int selected)
    {
        _page = Page.Choice;
        _heading.Text = Tr("MENU_SYSTEME");
        _rowCount = 3;
        _texts[0] = Tr("MENU_RETOUR_TITRE");
        _texts[1] = Tr("MENU_QUITTER_JEU");
        _texts[2] = Tr("MENU_RETOUR");
        _selected = selected;
        Refresh();
        SpeakSelected();
    }

    private void ShowConfirm(bool toTitle)
    {
        _page = Page.Confirm;
        _toTitle = toTitle;
        _heading.Text = Tr(toTitle ? "CONFIRM_RETOUR_TITRE" : "CONFIRM_QUITTER") + "\n" + Tr("CONFIRM_PERTE_PROGRESSION");
        _rowCount = 2;
        _texts[0] = Tr("CONFIRM_YES");
        _texts[1] = Tr("CONFIRM_NO");
        _selected = 1; // « Non » par défaut
        Refresh();
        TextReader.Speak(_heading.Text + " " + _texts[_selected], TextSource.Dialogue);
    }

    private void Move(int step)
    {
        _selected = (_selected + step + _rowCount) % _rowCount;
        AudioManager.Play(Sfx.MenuDeplace);
        Refresh();
        SpeakSelected();
    }

    private void SpeakSelected() => TextReader.Speak(_texts[_selected], TextSource.Dialogue);

    private void GoBack()
    {
        if (_page == Page.Confirm)
        {
            AudioManager.Play(Sfx.MenuRetour);
            ShowChoice(_toTitle ? 0 : 1);
        }
        else Close();
    }

    private void Validate()
    {
        if (_page == Page.Choice)
        {
            if (_selected == 2) { Close(); return; }
            AudioManager.Play(Sfx.MenuValide);
            ShowConfirm(_selected == 0);
            return;
        }

        if (_selected == 1) { GoBack(); return; } // Non
        TextReader.Stop();
        if (_toTitle) ReturnToTitle();
        else GetTree().Quit();
    }

    private void ReturnToTitle()
    {
        if (!ResourceLoader.Exists(TitleScenePath))
        {
            GD.PushError($"Écran titre introuvable : {TitleScenePath}");
            return;
        }
        // Le jeu sort de la pause avant le fondu (le fondu est un tween qui ne tourne pas en pause).
        // L'état de la partie n'est pas touché ici : « Continuer » le remplace par la sauvegarde choisie,
        // « Nouvelle partie » le remet à zéro (voir TitleScreen / SaveSystem.StartNewGame).
        if (_sceneManager.IsTransitioning) return; // rien n'a changé : le joueur reste dans le menu
        _open = false;
        Visible = false;
        SetProcess(false);
        EmitSignal(SignalName.LeaveRequested);
        Engine.TimeScale = 1f;
        _sceneManager.ResetSpawnId();
        _sceneManager.GoToScene(TitleScenePath);
    }

    private void Refresh()
    {
        for (int i = 0; i < _rows.Length; i++)
        {
            var row = _rows[i];
            row.Visible = i < _rowCount;
            if (!row.Visible) continue;
            bool selected = i == _selected;
            row.Text = (selected ? "> " : "  ") + _texts[i];
            row.Modulate = selected ? SelectedColor : Colors.White;
        }
    }

    private void BuildUi()
    {
        var dim = new ColorRect { Color = new Color(0, 0, 0, 0.6f), MouseFilter = MouseFilterEnum.Ignore };
        dim.SetAnchorsPreset(LayoutPreset.FullRect);
        AddChild(dim);

        var style = new StyleBoxFlat { BgColor = new Color(0.1f, 0.1f, 0.2f), BorderColor = new Color(0.9f, 0.8f, 0.5f) };
        style.SetBorderWidthAll(2);
        var panel = new Panel { Position = PanelPos, Size = PanelSize, MouseFilter = MouseFilterEnum.Ignore };
        panel.AddThemeStyleboxOverride(PanelStyleName, style);
        AddChild(panel);

        _heading = CreateLabel(new Vector2(PanelPos.X + 8, PanelPos.Y + 12), PanelSize.X - 16, 52);
        _heading.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        for (int i = 0; i < _rows.Length; i++)
            _rows[i] = CreateLabel(new Vector2(PanelPos.X, PanelPos.Y + 82 + i * RowHeight), PanelSize.X, 16);
    }

    private Label CreateLabel(Vector2 position, float width, float height)
    {
        var label = new Label
        {
            Position = position,
            Size = new Vector2(width, height),
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        AddChild(label);
        return label;
    }
}
