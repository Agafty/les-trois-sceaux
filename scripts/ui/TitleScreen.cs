using System.Globalization;
using Godot;

/// <summary>
/// Écran titre : Nouvelle partie / Continuer / Quitter, puis choix d'un des 3 emplacements.
/// Les lignes sont de simples Label ; la navigation (clavier et manette) lit les actions de l'Input Map
/// (move_up / move_down, attack / interact / ui_accept pour valider, pause pour revenir en arrière).
/// Ce n'est pas une Room : SaveSystem.Save (donc F10 et la sauvegarde auto) y est refusé.
/// </summary>
public partial class TitleScreen : Control
{
    /// <summary>Salle où commence une nouvelle partie (premier Spawn de la carte).</summary>
    [Export(PropertyHint.File, "*.tscn")]
    public string NewGameScenePath { get; set; } = "res://scenes/rooms/salle_test_room.tscn";

    private enum Page { Main, Slots, Confirm }
    private enum SlotState { Empty, Ok, Unreadable }

    private static readonly StringName ActionUp = "move_up";
    private static readonly StringName ActionDown = "move_down";
    private static readonly StringName ActionAttack = "attack";
    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName ActionAccept = "ui_accept";
    private static readonly StringName ActionUiUp = "ui_up";
    private static readonly StringName ActionUiDown = "ui_down";
    private static readonly StringName ActionBack = "pause";

    private const int ScreenWidth = 640;
    private const int RowHeight = 20;
    private const int MaxRows = SaveSystem.SlotCount + 1; // 3 emplacements + « Retour »
    private const string LogoPath = "res://art/ui/logo.png";

    private static readonly Color SelectedColor = new(1f, 0.85f, 0.4f);
    private static readonly Color DimColor = new(0.55f, 0.55f, 0.6f);
    private static readonly Color ErrorColor = new(1f, 0.5f, 0.45f);

    private SaveSystem _saveSystem;
    private SceneManager _sceneManager;
    private Label _heading;
    private Label _message;
    private readonly Label[] _rows = new Label[MaxRows];
    private readonly string[] _texts = new string[MaxRows];
    private readonly bool[] _dimmed = new bool[MaxRows];
    private readonly SlotState[] _slotStates = new SlotState[SaveSystem.SlotCount];

    private Page _page = Page.Main;
    private bool _newGame; // vrai = « Nouvelle partie », faux = « Continuer »
    private int _rowCount;
    private int _selected;
    private int _pendingSlot; // emplacement en attente de confirmation
    private float _menuTop = 200;
    // Une transition a été lancée depuis ce menu. Si elle se termine alors que l'écran titre existe encore,
    // c'est qu'elle a échoué (en cas de succès, l'écran titre est détruit pendant le fondu).
    private bool _launched;
    private bool _anySave;
    private readonly string[] _slotTexts = new string[SaveSystem.SlotCount]; // résumés lus une fois

    public override void _Ready()
    {
        _saveSystem = GetNode<SaveSystem>("/root/SaveSystem");
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");

        BuildUi();
        LoadSlotCache();
        ShowMain(0);
    }

    // IsActionJustPressed ne renvoie vrai qu'à l'image de l'appui, y compris pour un stick de manette
    // (pas besoin de gérer le « rebond » à la main).
    public override void _Process(double delta)
    {
        if (_launched && !_sceneManager.IsTransitioning)
        {
            if (_newGame) _saveSystem.CancelNewGame();
            _launched = false; // la transition a échoué : le menu redevient utilisable
            ShowError(Tr(_newGame ? "TITLE_ERR_START" : "TITLE_ERR_UNREADABLE"));
            return;
        }
        if (_launched || _sceneManager.IsTransitioning) return; // bloque aussi la double validation

        if (Input.IsActionJustPressed(ActionDown) || Input.IsActionJustPressed(ActionUiDown))
            MoveSelection(1);
        else if (Input.IsActionJustPressed(ActionUp) || Input.IsActionJustPressed(ActionUiUp))
            MoveSelection(-1);
        else if (Input.IsActionJustPressed(ActionAttack) || Input.IsActionJustPressed(ActionInteract)
                 || Input.IsActionJustPressed(ActionAccept))
            Validate();
        else if (Input.IsActionJustPressed(ActionBack))
            GoBack();
    }

    // --- Pages ------------------------------------------------------------------------------

    private void ShowMain(int selected)
    {
        _page = Page.Main;
        _heading.Text = "";
        _rowCount = 3;
        _texts[0] = Tr("TITLE_NEW");
        _texts[1] = Tr("TITLE_CONTINUE");
        _texts[2] = Tr("TITLE_QUIT");
        _dimmed[0] = false;
        _dimmed[1] = !_anySave; // grisé et non validable s'il n'y a aucune sauvegarde
        _dimmed[2] = false;
        _selected = selected;
        ClearMessage();
        Refresh();
    }

    private void ShowSlots(int selected)
    {
        _page = Page.Slots;
        _heading.Text = Tr(_newGame ? "TITLE_PICK_NEW" : "TITLE_PICK_LOAD");
        _rowCount = MaxRows;
        for (int i = 0; i < SaveSystem.SlotCount; i++)
        {
            _texts[i] = _slotTexts[i];
            _dimmed[i] = !_newGame && _slotStates[i] != SlotState.Ok; // rien à continuer ici
        }
        _texts[SaveSystem.SlotCount] = Tr("TITLE_BACK");
        _dimmed[SaveSystem.SlotCount] = false;
        _selected = selected;
        ClearMessage();
        Refresh();
    }

    private void ShowConfirm(int slot)
    {
        _page = Page.Confirm;
        _pendingSlot = slot;
        _heading.Text = string.Format(Tr("CONFIRM_OVERWRITE"), slot);
        _rowCount = 2;
        _texts[0] = Tr("CONFIRM_YES");
        _texts[1] = Tr("CONFIRM_NO");
        _dimmed[0] = false;
        _dimmed[1] = false;
        _selected = 1; // « Non » par défaut : on n'écrase pas par réflexe
        ClearMessage();
        Refresh();
    }

    // Lit les 3 emplacements une seule fois (les fichiers ne changent pas tant qu'on est sur l'écran titre).
    private void LoadSlotCache()
    {
        _anySave = false;
        for (int i = 0; i < SaveSystem.SlotCount; i++)
        {
            int slot = i + 1;
            if (!_saveSystem.HasSave(slot))
            {
                _slotStates[i] = SlotState.Empty;
                _slotTexts[i] = string.Format(Tr("SLOT_EMPTY"), slot);
                continue;
            }
            _anySave = true;
            if (_saveSystem.TryPeek(slot, out var data))
            {
                _slotStates[i] = SlotState.Ok;
                _slotTexts[i] = Summarize(slot, data);
            }
            else
            {
                _slotStates[i] = SlotState.Unreadable;
                _slotTexts[i] = string.Format(Tr("SLOT_UNREADABLE"), slot);
            }
        }
    }

    private string Summarize(int slot, SaveData data)
    {
        int hearts = Mathf.Max(1, (data.MaxHealth + 1) / 2);
        double seconds = System.Math.Max(0, data.PlayTimeSeconds);
        int hours = (int)(seconds / 3600);
        int minutes = (int)(seconds / 60) % 60;
        string time = hours + ":" + minutes.ToString("00", CultureInfo.InvariantCulture);
        string date = data.SavedAtUtc.ToLocalTime().ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture);
        return string.Format(Tr(hearts == 1 ? "SLOT_SUMMARY_ONE" : "SLOT_SUMMARY"), slot, hearts, time, date);
    }

    // --- Actions ----------------------------------------------------------------------------

    private void MoveSelection(int step)
    {
        _selected = (_selected + step + _rowCount) % _rowCount;
        ClearMessage();
        Refresh();
    }

    private void GoBack()
    {
        if (_page == Page.Slots) ShowMain(_newGame ? 0 : 1);
        else if (_page == Page.Confirm) ShowSlots(_pendingSlot - 1);
    }

    private void Validate()
    {
        switch (_page)
        {
            case Page.Main:
                if (_selected == 2)
                {
                    GetTree().Quit();
                    return;
                }
                if (_selected == 1 && !_anySave) return; // rien à continuer
                _newGame = _selected == 0;
                ShowSlots(0);
                break;

            case Page.Slots:
                if (_selected == SaveSystem.SlotCount)
                {
                    ShowMain(_newGame ? 0 : 1);
                    return;
                }
                ValidateSlot(_selected + 1);
                break;

            case Page.Confirm:
                if (_selected == 0) StartNewGame(_pendingSlot);
                else ShowSlots(_pendingSlot - 1);
                break;
        }
    }

    private void ValidateSlot(int slot)
    {
        var state = _slotStates[slot - 1];
        if (_newGame)
        {
            if (state == SlotState.Empty) StartNewGame(slot);
            else ShowConfirm(slot); // occupé ou illisible : on demande avant d'écraser
            return;
        }

        if (state == SlotState.Empty) return; // rien à continuer
        if (state == SlotState.Unreadable)
        {
            ShowError(Tr("TITLE_ERR_UNREADABLE"));
            return;
        }

        if (_saveSystem.Load(slot))
            _launched = true;
        else
            ShowError(Tr("TITLE_ERR_UNREADABLE")); // lisible mais inutilisable (salle disparue...) : même message
    }

    private void StartNewGame(int slot)
    {
        if (!ResourceLoader.Exists(NewGameScenePath))
        {
            GD.PushError($"Salle de départ introuvable : {NewGameScenePath}");
            ShowError(Tr("TITLE_ERR_START"));
            return;
        }
        // La remise à zéro de l'état n'a lieu qu'une fois l'écran noir (beforeChange), comme pour Load :
        // si la transition échoue, rien n'a été modifié.
        if (!_sceneManager.GoToScene(NewGameScenePath, "", () => _saveSystem.StartNewGame(slot)))
        {
            ShowError(Tr("TITLE_ERR_START"));
            return;
        }
        _launched = true;
    }

    // --- Affichage --------------------------------------------------------------------------

    private void ShowError(string text)
    {
        _message.Text = text;
        _message.Modulate = ErrorColor;
    }

    private void ClearMessage() => _message.Text = "";

    private void Refresh()
    {
        float top = _menuTop + (_heading.Text.Length > 0 ? RowHeight : 0);
        for (int i = 0; i < MaxRows; i++)
        {
            var row = _rows[i];
            row.Visible = i < _rowCount;
            if (!row.Visible) continue;
            bool selected = i == _selected;
            row.Position = new Vector2(0, top + i * RowHeight);
            row.Text = (selected ? "> " : "  ") + _texts[i];
            row.Modulate = selected ? SelectedColor : _dimmed[i] ? DimColor : Colors.White;
        }
    }

    private void BuildUi()
    {
        float logoBottom;
        var logo = ResourceLoader.Exists(LogoPath) ? GD.Load<Texture2D>(LogoPath) : null;
        if (logo != null)
        {
            var rect = new TextureRect
            {
                Texture = logo,
                StretchMode = TextureRect.StretchModeEnum.Keep,
                Position = new Vector2((ScreenWidth - logo.GetWidth()) / 2f, 16),
                MouseFilter = MouseFilterEnum.Ignore,
            };
            AddChild(rect);
            logoBottom = 16 + logo.GetHeight();
        }
        else
        {
            // Pas encore de logo : le titre en texte, agrandi x2 (la police bitmap reste nette en multiple entier).
            var title = CreateLabel(new Vector2(0, 70), ScreenWidth / 2f);
            title.Text = Tr("TITLE_GAME");
            title.Scale = new Vector2(2, 2);
            logoBottom = 70 + 28;
        }

        _menuTop = Mathf.Clamp(logoBottom + 28, 180, 230);
        _heading = CreateLabel(new Vector2(0, _menuTop), ScreenWidth);
        for (int i = 0; i < MaxRows; i++)
            _rows[i] = CreateLabel(new Vector2(0, _menuTop + i * RowHeight), ScreenWidth);
        _message = CreateLabel(new Vector2(0, 320), ScreenWidth);
    }

    private Label CreateLabel(Vector2 position, float width)
    {
        var label = new Label
        {
            Position = position,
            Size = new Vector2(width, 14),
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        AddChild(label);
        return label;
    }
}
