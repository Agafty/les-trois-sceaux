using Godot;

/// <summary>
/// Écran d'inventaire : ouvert/fermé par l'action « pause », met le jeu en pause (SceneTree.Paused).
/// Ce nœud est en ProcessMode Always, donc il continue de tourner pendant la pause ; tout le reste
/// du jeu (joueur, ennemis) est figé. Les nœuds sont créés dans _Ready ; les textures absentes
/// laissent des repères de secours.
/// </summary>
public partial class InventoryMenu : Control
{
    private const int Columns = 4;
    private const int Rows = 2;
    private const int SlotCount = Columns * Rows;
    private const int Pitch = 40; // 32 px de case + 8 px d'espace
    private const float FirstRepeatDelay = 0.35f;
    private const float RepeatDelay = 0.12f;

    private static readonly StringName ActionPause = "pause";
    private static readonly StringName ActionAttack = "attack";
    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName ActionUp = "move_up";
    private static readonly StringName ActionDown = "move_down";
    private static readonly StringName ActionLeft = "move_left";
    private static readonly StringName ActionRight = "move_right";
    private static readonly StringName ActionMapPage = "map_page";
    private static readonly StringName PanelStyleName = "panel";

    private static readonly Vector2 PanelPos = new(140, 50);
    private static readonly Vector2 PanelSize = new(360, 250);
    private static readonly Vector2 GridPos = new(244, 100);
    private static readonly Color EquippedTint = new(1f, 0.85f, 0.4f);

    private GameState _gameState;
    private SceneManager _sceneManager;
    private Label _title;
    private Label _name;
    private Label _description;
    private Label _mapHint;
    private DungeonMapPage _mapPage;
    private Control _cursor;
    private readonly TextureRect[] _frames = new TextureRect[SlotCount];
    private readonly TextureRect[] _icons = new TextureRect[SlotCount];
    private readonly TextureRect[][] _digits = new TextureRect[SlotCount][];
    private readonly ItemData[] _slotItems = new ItemData[SlotCount];
    private readonly AtlasTexture[] _digitTextures = new AtlasTexture[10];

    private bool _open;
    private bool _pausedByMenu;
    private bool _mapOpen;
    private int _selected;
    private Vector2I _heldDirection = Vector2I.Zero;
    private float _repeatTimer;

    public override void _Ready()
    {
        ProcessMode = ProcessModeEnum.Always;
        Visible = false;
        SetProcess(false);
        SetAnchorsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Ignore;

        _gameState = GetNode<GameState>("/root/GameState");
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");

        var digitsSheet = LoadTexture("res://art/ui/chiffres.png");
        for (int i = 0; i < _digitTextures.Length; i++)
            _digitTextures[i] = new AtlasTexture { Atlas = digitsSheet, Region = new Rect2(i * 8, 0, 8, 8) };

        BuildUi();
        _gameState.InventoryChanged += RefreshIfOpen;
        _gameState.EquippedItemChanged += OnEquippedChanged;
    }

    public override void _ExitTree()
    {
        if (_gameState != null)
        {
            _gameState.InventoryChanged -= RefreshIfOpen;
            _gameState.EquippedItemChanged -= OnEquippedChanged;
        }
        if (_pausedByMenu) GetTree().Paused = false; // ne jamais laisser le jeu figé
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (!@event.IsActionPressed(ActionPause) || @event.IsEcho()) return;

        if (_open) Close();
        else TryOpen();
        GetViewport().SetInputAsHandled();
    }

    // Actif seulement quand le menu est ouvert (SetProcess).
    public override void _Process(double delta)
    {
        if (Input.IsActionJustPressed(ActionMapPage))
        {
            AudioManager.Play(Sfx.MenuDeplace);
            if (_mapOpen) ShowInventoryPage();
            else ShowMapPage();
            return;
        }
        if (_mapOpen)
        {
            // Page carte : haut = rez-de-chaussée, bas = sous-sol. L'inventaire ne réagit pas.
            string floorBefore = _mapPage.Floor;
            if (Input.IsActionJustPressed(ActionUp)) _mapPage.SetFloor(DungeonMapPage.FloorGround);
            else if (Input.IsActionJustPressed(ActionDown)) _mapPage.SetFloor(DungeonMapPage.FloorBasement);
            if (_mapPage.Floor != floorBefore) AudioManager.Play(Sfx.MenuDeplace);
            return;
        }
        ProcessNavigation((float)delta);
        if (Input.IsActionJustPressed(ActionAttack) || Input.IsActionJustPressed(ActionInteract))
            ValidateSelection();
    }

    private void TryOpen()
    {
        if (GetTree().Paused) return; // un autre système a déjà mis le jeu en pause
        if (_sceneManager.IsTransitioning) return;
        if (GetTree().GetFirstNodeInGroup("player") is Player { IsDead: true }) return;

        Engine.TimeScale = 1f; // sécurité : jamais de menu au ralenti (hit-stop en cours)
        _open = true;
        _mapOpen = false;
        _mapPage.Close();
        _heldDirection = Vector2I.Zero;
        Visible = true;
        GetTree().Paused = true;
        _pausedByMenu = true;
        SetProcess(true);
        Refresh();
        AudioManager.Play(Sfx.MenuValide);
    }

    private void Close()
    {
        _open = false;
        _mapOpen = false;
        AudioManager.Play(Sfx.MenuRetour);
        _mapPage.Close();
        Visible = false;
        SetProcess(false);
        if (_pausedByMenu)
            GetTree().Paused = false;
        _pausedByMenu = false;
    }

    private void ProcessNavigation(float delta)
    {
        int dx = (Input.IsActionPressed(ActionRight) ? 1 : 0) - (Input.IsActionPressed(ActionLeft) ? 1 : 0);
        int dy = (Input.IsActionPressed(ActionDown) ? 1 : 0) - (Input.IsActionPressed(ActionUp) ? 1 : 0);
        if (dx != 0) dy = 0; // pas de diagonale dans une grille
        var direction = new Vector2I(dx, dy);

        if (direction == Vector2I.Zero)
        {
            _heldDirection = Vector2I.Zero;
            return;
        }

        if (direction != _heldDirection)
        {
            _heldDirection = direction;
            _repeatTimer = FirstRepeatDelay;
            MoveCursor(direction);
            return;
        }

        _repeatTimer -= delta;
        if (_repeatTimer > 0f) return;
        _repeatTimer = RepeatDelay;
        MoveCursor(direction);
    }

    private void MoveCursor(Vector2I direction)
    {
        int column = Mathf.Clamp(_selected % Columns + direction.X, 0, Columns - 1);
        int row = Mathf.Clamp(_selected / Columns + direction.Y, 0, Rows - 1);
        int index = row * Columns + column;
        if (index == _selected) return;
        _selected = index;
        AudioManager.Play(Sfx.MenuDeplace);
        UpdateCursor();
    }

    private void ShowMapPage()
    {
        _mapOpen = true;
        _heldDirection = Vector2I.Zero;
        _mapPage.Open(_gameState, GetTree().CurrentScene as Room);
    }

    private void ShowInventoryPage()
    {
        _mapOpen = false;
        _heldDirection = Vector2I.Zero;
        _mapPage.Close();
    }

    private void ValidateSelection()
    {
        var item = _slotItems[_selected];
        if (item != null && _gameState.Equip(item.Id)) // refuse silencieusement les non-équipables
            AudioManager.Play(Sfx.MenuValide);
    }

    private void OnEquippedChanged(string itemId) => RefreshIfOpen();

    private void RefreshIfOpen()
    {
        if (_open) Refresh();
    }

    private void Refresh()
    {
        _title.Text = Tr("MENU_INVENTAIRE");
        _mapHint.Text = Tr("INVENTAIRE_AIDE_CARTE");
        var ids = _gameState.InventoryIds;
        for (int i = 0; i < SlotCount; i++)
        {
            var item = i < ids.Count ? _gameState.GetItemData(ids[i]) : null;
            _slotItems[i] = item;
            _icons[i].Texture = item?.Icon;
            _frames[i].Modulate = item != null && item.Id == _gameState.EquippedItemId ? EquippedTint : Colors.White;

            bool showCount = item != null && item.HasQuantity;
            _digits[i][0].Visible = showCount;
            _digits[i][1].Visible = showCount;
            if (showCount)
            {
                int value = Mathf.Clamp(_gameState.GetQuantity(item.Id), 0, 99);
                _digits[i][0].Texture = _digitTextures[value / 10];
                _digits[i][1].Texture = _digitTextures[value % 10];
            }
        }
        UpdateCursor();
    }

    private void UpdateCursor()
    {
        _cursor.Position = SlotPosition(_selected);
        var item = _slotItems[_selected];
        _name.Text = item != null ? Tr(item.NameKey) : "";
        _description.Text = item != null ? Tr(item.DescriptionKey) : "";
    }

    private static Vector2 SlotPosition(int index) =>
        GridPos + new Vector2(index % Columns * Pitch, index / Columns * Pitch);

    private static Texture2D LoadTexture(string path)
    {
        if (ResourceLoader.Exists(path))
            return GD.Load<Texture2D>(path);
        GD.PushWarning($"Texture de l'inventaire absente : {path}");
        return null;
    }

    private void BuildUi()
    {
        var dim = new ColorRect { Color = new Color(0, 0, 0, 0.5f), MouseFilter = MouseFilterEnum.Ignore };
        dim.SetAnchorsPreset(LayoutPreset.FullRect);
        AddChild(dim);

        AddChild(CreatePanel());

        _title = CreateLabel(new Vector2(PanelPos.X, PanelPos.Y + 14), PanelSize.X, 12);
        _title.HorizontalAlignment = HorizontalAlignment.Center;

        var frameTexture = LoadTexture("res://art/ui/cadre_objet.png");
        for (int i = 0; i < SlotCount; i++)
        {
            var origin = SlotPosition(i);
            _frames[i] = CreateRect(frameTexture, origin);
            _icons[i] = CreateRect(null, origin + new Vector2(4, 4));
            _digits[i] = new[]
            {
                CreateRect(null, origin + new Vector2(15, 23)),
                CreateRect(null, origin + new Vector2(23, 23)),
            };
        }

        _cursor = CreateCursor();
        AddChild(_cursor);

        _name = CreateLabel(new Vector2(PanelPos.X + 16, 200), PanelSize.X - 32, 12);
        _description = CreateLabel(new Vector2(PanelPos.X + 16, 218), PanelSize.X - 32, 60);
        _description.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _mapHint = CreateLabel(new Vector2(PanelPos.X + 16, PanelPos.Y + PanelSize.Y - 18), PanelSize.X - 32, 12);
        _mapHint.HorizontalAlignment = HorizontalAlignment.Right;

        // Page carte : en dernier pour être dessinée par-dessus l'inventaire.
        _mapPage = new DungeonMapPage { Position = PanelPos, Size = PanelSize };
        AddChild(_mapPage);
    }

    private Control CreatePanel()
    {
        var texture = LoadTexture("res://art/ui/panneau.png");
        if (texture != null)
        {
            return new NinePatchRect
            {
                Texture = texture,
                Position = PanelPos,
                Size = PanelSize,
                PatchMarginLeft = 8,
                PatchMarginTop = 8,
                PatchMarginRight = 8,
                PatchMarginBottom = 8,
                MouseFilter = MouseFilterEnum.Ignore,
            };
        }

        // Secours tant que panneau.png n'existe pas.
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

    private Control CreateCursor()
    {
        var texture = LoadTexture("res://art/ui/curseur_inventaire.png");
        if (texture != null)
            return new TextureRect { Texture = texture, Size = new Vector2(32, 32), MouseFilter = MouseFilterEnum.Ignore };

        var style = new StyleBoxFlat { BgColor = new Color(0, 0, 0, 0), BorderColor = Colors.White };
        style.SetBorderWidthAll(2);
        var panel = new Panel { Size = new Vector2(32, 32), MouseFilter = MouseFilterEnum.Ignore };
        panel.AddThemeStyleboxOverride(PanelStyleName, style);
        return panel;
    }

    private TextureRect CreateRect(Texture2D texture, Vector2 position)
    {
        var rect = new TextureRect
        {
            Texture = texture,
            Position = position,
            StretchMode = TextureRect.StretchModeEnum.Keep,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        AddChild(rect);
        return rect;
    }

    private Label CreateLabel(Vector2 position, float width, float height)
    {
        var label = new Label { Position = position, Size = new Vector2(width, height), MouseFilter = MouseFilterEnum.Ignore };
        AddChild(label);
        return label;
    }
}
