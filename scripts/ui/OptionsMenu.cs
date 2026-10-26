using Godot;

/// <summary>
/// Écran d'options : volumes musique et bruitages, plein écran, échelle de la fenêtre, aide au jeune joueur, langue.
/// Il est instancié par l'écran titre et par le menu pause (scenes/ui/options.tscn) : appeler <see cref="Open"/>, puis
/// attendre le signal <see cref="Closed"/>. Chaque changement est appliqué tout de suite (<see cref="GameOptions"/>) ;
/// le fichier user://options.json est écrit à la fermeture.
/// Navigation (clavier et manette) : haut/bas = ligne, gauche/droite = valeur, valider = changer (ou « Retour »), pause = retour.
/// Pas de remappage des touches pour l'instant (prévu plus tard).
/// </summary>
public partial class OptionsMenu : Control
{
    [Signal]
    public delegate void ClosedEventHandler();

    private enum Row { Music, Sfx, Fullscreen, Scale, Help, Language, Back }

    private const int RowCount = 7;
    private const int RowHeight = 22;

    private static readonly StringName ActionUp = "move_up";
    private static readonly StringName ActionDown = "move_down";
    private static readonly StringName ActionLeft = "move_left";
    private static readonly StringName ActionRight = "move_right";
    private static readonly StringName ActionUiUp = "ui_up";
    private static readonly StringName ActionUiDown = "ui_down";
    private static readonly StringName ActionUiLeft = "ui_left";
    private static readonly StringName ActionUiRight = "ui_right";
    private static readonly StringName ActionAttack = "attack";
    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName ActionAccept = "ui_accept";
    private static readonly StringName ActionBack = "pause";
    private static readonly StringName PanelStyleName = "panel";

    private static readonly Vector2 PanelPos = new(120, 40);
    private static readonly Vector2 PanelSize = new(400, 270);
    private static readonly Color SelectedColor = new(1f, 0.85f, 0.4f);
    private static readonly Color DimColor = new(0.55f, 0.55f, 0.6f);

    private readonly Label[] _names = new Label[RowCount];
    private readonly Label[] _values = new Label[RowCount];
    private Label _title;
    private Label _hint;
    private int _selected;
    private bool _open;
    private bool _skipInput; // ignore l'image d'ouverture : l'appui qui a ouvert le menu ne doit pas le valider

    public bool IsOpen => _open;

    public override void _Ready()
    {
        ProcessMode = ProcessModeEnum.Always; // continue de tourner quand le menu pause fige le jeu
        Visible = false;
        SetProcess(false);
        SetAnchorsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop; // bloque les clics vers ce qui est dessous
        BuildUi();
    }

    public override void _ExitTree()
    {
        if (_open) GameOptions.Save(); // fermeture brutale du jeu avec le menu ouvert : on garde les réglages
    }

    public void Open()
    {
        _open = true;
        _skipInput = true;
        _selected = 0;
        Visible = true;
        SetProcess(true);
        Refresh();
        AudioManager.Play(Sfx.MenuValide);
    }

    private void Close()
    {
        _open = false;
        Visible = false;
        SetProcess(false);
        GameOptions.Save();
        AudioManager.Play(Sfx.MenuRetour);
        EmitSignal(SignalName.Closed);
    }

    // Actif seulement quand le menu est ouvert (SetProcess). IsActionJustPressed : vrai uniquement à l'image de l'appui.
    public override void _Process(double delta)
    {
        if (_skipInput)
        {
            _skipInput = false;
            return;
        }

        if (Input.IsActionJustPressed(ActionDown) || Input.IsActionJustPressed(ActionUiDown))
            MoveSelection(1);
        else if (Input.IsActionJustPressed(ActionUp) || Input.IsActionJustPressed(ActionUiUp))
            MoveSelection(-1);
        else if (Input.IsActionJustPressed(ActionRight) || Input.IsActionJustPressed(ActionUiRight))
            ChangeValue(1);
        else if (Input.IsActionJustPressed(ActionLeft) || Input.IsActionJustPressed(ActionUiLeft))
            ChangeValue(-1);
        else if (Input.IsActionJustPressed(ActionAttack) || Input.IsActionJustPressed(ActionInteract)
                 || Input.IsActionJustPressed(ActionAccept))
            Validate();
        else if (Input.IsActionJustPressed(ActionBack))
            Close();
    }

    private void MoveSelection(int step)
    {
        _selected = (_selected + step + RowCount) % RowCount;
        AudioManager.Play(Sfx.MenuDeplace);
        Refresh();
    }

    private void Validate()
    {
        var row = (Row)_selected;
        if (row == Row.Back) Close();
        else if (row != Row.Music && row != Row.Sfx) ChangeValue(1); // les volumes se règlent avec gauche/droite
    }

    // Les listes (échelle, aide, langue) bouclent ; les volumes s'arrêtent à 0 et à 100.
    private void ChangeValue(int direction)
    {
        var o = GameOptions.Current;
        switch ((Row)_selected)
        {
            case Row.Music:
                int music = OptionsRules.StepVolume(o.MusicVolume, direction);
                if (music == o.MusicVolume) return;
                o.MusicVolume = music;
                GameOptions.ApplyAudio();
                AudioManager.Play(Sfx.MenuDeplace);
                break;
            case Row.Sfx:
                int sfx = OptionsRules.StepVolume(o.SfxVolume, direction);
                if (sfx == o.SfxVolume) return;
                o.SfxVolume = sfx;
                GameOptions.ApplyAudio();
                AudioManager.Play(Sfx.MenuValide); // son de test au nouveau volume
                break;
            case Row.Fullscreen:
                o.Fullscreen = !o.Fullscreen;
                GameOptions.ApplyDisplay();
                AudioManager.Play(Sfx.MenuDeplace);
                break;
            case Row.Scale:
                o.WindowScale = OptionsRules.CycleScale(o.WindowScale, direction);
                GameOptions.ApplyDisplay();
                AudioManager.Play(Sfx.MenuDeplace);
                break;
            case Row.Help:
                o.PuzzleTimeMultiplier = OptionsRules.CycleHelp(o.PuzzleTimeMultiplier, direction);
                GameOptions.ApplyHelp();
                AudioManager.Play(Sfx.MenuDeplace);
                break;
            case Row.Language:
                o.Language = OptionsRules.CycleLanguage(o.Language, direction);
                GameOptions.ApplyLanguage();
                AudioManager.Play(Sfx.MenuDeplace);
                break;
            default:
                return;
        }
        Refresh();
    }

    // Réécrit tous les textes (rare : ouverture et changements), donc les chaînes construites ici ne coûtent rien.
    private void Refresh()
    {
        var o = GameOptions.Current;
        _title.Text = Tr("OPT_TITLE");
        _hint.Text = Tr("OPT_HINT");

        SetRow(Row.Music, Tr("OPT_MUSIC"), o.MusicVolume + "%", false);
        SetRow(Row.Sfx, Tr("OPT_SFX"), o.SfxVolume + "%", false);
        SetRow(Row.Fullscreen, Tr("OPT_FULLSCREEN"), Tr(o.Fullscreen ? "OPT_ON" : "OPT_OFF"), false);
        // L'échelle ne sert à rien en plein écran : grisée (elle reste réglable pour le prochain retour en fenêtre).
        SetRow(Row.Scale, Tr("OPT_SCALE"), o.WindowScale == 0 ? Tr("OPT_SCALE_AUTO") : "x" + o.WindowScale, o.Fullscreen);
        SetRow(Row.Help, Tr("OPT_HELP"), Tr(o.PuzzleTimeMultiplier switch
        {
            0 => "OPT_HELP_NONE",
            2 => "OPT_HELP_DOUBLE",
            _ => "OPT_HELP_NORMAL",
        }), false);
        SetRow(Row.Language, Tr("OPT_LANGUAGE"), Tr(o.Language == "en" ? "OPT_LANG_EN" : "OPT_LANG_FR"), false);
        SetRow(Row.Back, Tr("TITLE_BACK"), "", false);
    }

    private void SetRow(Row row, string name, string value, bool dimmed)
    {
        int i = (int)row;
        bool selected = i == _selected;
        var color = selected ? SelectedColor : dimmed ? DimColor : Colors.White;
        _names[i].Text = (selected ? "> " : "  ") + name;
        _names[i].Modulate = color;
        _values[i].Text = value.Length > 0 && selected ? "< " + value + " >" : value;
        _values[i].Modulate = color;
    }

    private void BuildUi()
    {
        var dim = new ColorRect { Color = new Color(0, 0, 0, 0.6f), MouseFilter = MouseFilterEnum.Ignore };
        dim.SetAnchorsPreset(LayoutPreset.FullRect);
        AddChild(dim);
        AddChild(CreatePanel());

        _title = CreateLabel(new Vector2(PanelPos.X, PanelPos.Y + 14), PanelSize.X);
        _title.HorizontalAlignment = HorizontalAlignment.Center;

        float top = PanelPos.Y + 46;
        for (int i = 0; i < RowCount; i++)
        {
            float y = top + i * RowHeight;
            _names[i] = CreateLabel(new Vector2(PanelPos.X + 28, y), 190);
            _values[i] = CreateLabel(new Vector2(PanelPos.X + 220, y), 150);
            _values[i].HorizontalAlignment = HorizontalAlignment.Center;
        }

        _hint = CreateLabel(new Vector2(PanelPos.X + 16, PanelPos.Y + PanelSize.Y - 22), PanelSize.X - 32);
        _hint.HorizontalAlignment = HorizontalAlignment.Center;
        _hint.Modulate = DimColor;
    }

    private Control CreatePanel()
    {
        const string path = "res://art/ui/panneau.png";
        if (ResourceLoader.Exists(path))
        {
            return new NinePatchRect
            {
                Texture = GD.Load<Texture2D>(path),
                Position = PanelPos,
                Size = PanelSize,
                PatchMarginLeft = 8,
                PatchMarginTop = 8,
                PatchMarginRight = 8,
                PatchMarginBottom = 8,
                MouseFilter = MouseFilterEnum.Ignore,
            };
        }

        var style = new StyleBoxFlat
        {
            BgColor = new Color(0.1f, 0.1f, 0.2f),
            BorderColor = new Color(0.9f, 0.8f, 0.5f),
        };
        style.SetBorderWidthAll(2);
        var panel = new Panel { Position = PanelPos, Size = PanelSize, MouseFilter = MouseFilterEnum.Ignore };
        panel.AddThemeStyleboxOverride(PanelStyleName, style);
        return panel;
    }

    private Label CreateLabel(Vector2 position, float width)
    {
        var label = new Label { Position = position, Size = new Vector2(width, 14), MouseFilter = MouseFilterEnum.Ignore };
        AddChild(label);
        return label;
    }
}
