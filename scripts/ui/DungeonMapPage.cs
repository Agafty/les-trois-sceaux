using Godot;

/// <summary>
/// Page « carte du donjon » du menu pause. Elle se pose par-dessus la page d'inventaire (même position et taille,
/// fond opaque) et est pilotée par <see cref="InventoryMenu"/> : Open / Close / ChangeFloor.
/// Tout est dessiné par le code (_Draw) ; les images de art/ui/carte/ sont facultatives, un dessin de secours les remplace.
/// Le dessin n'est refait que quand l'état change ou au clignotement de Brann (toutes les 0,4 s), pas à chaque frame.
/// </summary>
public partial class DungeonMapPage : Control
{
    public const string FloorGround = DungeonLayout.FloorGround;
    public const string FloorBasement = DungeonLayout.FloorBasement;

    private const string ArtFolder = "res://art/ui/carte/";
    private const float BlinkPeriod = 0.4f;

    // Géométrie locale (la page mesure 360x250).
    private const int ColumnPitch = 48;
    private const int RowPitch = 34;
    private static readonly Vector2 RoomSize = new(36, 22);
    private static readonly Vector2 GridOrigin = new(28, 44);
    private static readonly Vector2 LegendOrigin = new(236, 70);
    private const int LegendPitch = 14;

    private static readonly Color VisitedFill = new(0.85f, 0.72f, 0.40f);
    private static readonly Color VisitedBorder = new(0.35f, 0.25f, 0.12f);
    private static readonly Color OutlineColor = new(0.55f, 0.62f, 0.75f);
    private static readonly Color LinkColor = new(0.9f, 0.8f, 0.5f);
    private static readonly Color BrannColor = new(0.45f, 0.95f, 0.45f);
    private static readonly Color BossColor = new(0.9f, 0.2f, 0.2f);
    private static readonly Color StairsColor = new(1f, 1f, 1f);
    private static readonly Color FallColor = new(0.1f, 0.05f, 0.15f);
    private static readonly Color CurrentRoomColor = new(0.3f, 0.95f, 1f);
    private static readonly Color TintGround = new(0.45f, 0.30f, 0.10f, 0.18f);
    private static readonly Color TintBasement = new(0.05f, 0.10f, 0.40f, 0.40f);
    private static readonly Color ChestColor = new(0.65f, 0.38f, 0.12f);
    private static readonly Color BigChestColor = new(0.95f, 0.75f, 0.15f);
    private static readonly Color DoorBackdrop = new(0.08f, 0.05f, 0.05f);
    private static readonly Color DoorKeyColor = new(1f, 0.85f, 0.2f);
    private static readonly Color DoorBossKeyColor = new(1f, 0.5f, 0.1f);
    private static readonly Color DoorEnemiesColor = new(0.85f, 0.2f, 0.2f);
    private static readonly Color DoorSwitchColor = new(0.3f, 0.6f, 1f);

    private Label _title;
    private Label _floorLabel;
    private Label _noMapLabel;
    private Label _noItemLabel;
    private Label _help;
    private Label _legendBrann;
    private Label _legendBoss;
    private Label _legendStairs;
    private Label _legendFall;
    private Label _legendChest;
    private Label _legendKeyDoor;
    private Label _roomName;

    private Texture2D _texFrame;
    private Texture2D _texVisited;
    private Texture2D _texUnknown;
    private Texture2D _texBrann;
    private Texture2D _texBoss;
    private Texture2D _texStairs;
    private Texture2D _texFall;
    private Texture2D _texChest;
    private Texture2D _texBigChest;
    private Texture2D _texKey;
    private StyleBox _background;

    private DungeonLayout _layout;
    private MapRoomState[] _states = System.Array.Empty<MapRoomState>();
    // Pré-calculés à l'ouverture pour ne rien allouer ni chercher dans _Draw.
    private int[] _chestKinds = System.Array.Empty<int>(); // 0 aucun, 1 coffre, 2 grand coffre à ouvrir
    private int[] _linkA = System.Array.Empty<int>();
    private int[] _linkB = System.Array.Empty<int>();
    private bool[] _linkOpen = System.Array.Empty<bool>();
    private bool _hasCompass;
    private bool _hasMap;
    private string _currentRoomId = "";
    private string _floor = FloorGround;
    private bool _blinkOn = true;
    private float _blinkTimer;

    /// <summary>Vrai si une carte de donjon est affichée (sinon : texte « Pas de carte ici »).</summary>
    public bool HasLayout => _layout != null;

    public string Floor => _floor;

    public override void _Ready()
    {
        MouseFilter = MouseFilterEnum.Ignore;
        Visible = false;
        SetProcess(false);

        _texFrame = LoadOptional("cadre.png");
        _texVisited = LoadOptional("salle_visitee.png");
        _texUnknown = LoadOptional("salle_inconnue.png");
        _texBrann = LoadOptional("icone_brann.png");
        _texBoss = LoadOptional("icone_boss.png");
        _texStairs = LoadOptional("icone_escalier.png");
        _texFall = LoadOptional("icone_chute.png");
        _texChest = LoadOptional("icone_coffre.png");
        _texBigChest = LoadOptional("icone_grand_coffre.png");
        _texKey = LoadOptional("icone_cle.png");
        _background = CreateBackground();

        _title = CreateLabel(new Vector2(0, 14), Size.X, 12);
        _title.HorizontalAlignment = HorizontalAlignment.Center;
        _floorLabel = CreateLabel(new Vector2(LegendOrigin.X, 44), 110, 12);
        _noMapLabel = CreateLabel(new Vector2(16, 110), Size.X - 32, 12);
        _noMapLabel.HorizontalAlignment = HorizontalAlignment.Center;
        _noItemLabel = CreateLabel(new Vector2(LegendOrigin.X, 160), 112, 40);
        _noItemLabel.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _roomName = CreateLabel(new Vector2(16, 208), Size.X - 32, 12);
        _roomName.HorizontalAlignment = HorizontalAlignment.Center;
        _help = CreateLabel(new Vector2(16, 224), Size.X - 32, 12);
        _help.HorizontalAlignment = HorizontalAlignment.Center;

        _legendBrann = CreateLegendLabel(0);
        _legendBoss = CreateLegendLabel(1);
        _legendStairs = CreateLegendLabel(2);
        _legendFall = CreateLegendLabel(3);
        _legendChest = CreateLegendLabel(4);
        _legendKeyDoor = CreateLegendLabel(5);
    }

    public override void _Process(double delta)
    {
        if (_layout == null) return;
        _blinkTimer += (float)delta;
        if (_blinkTimer < BlinkPeriod) return;
        _blinkTimer = 0f;
        _blinkOn = !_blinkOn;
        QueueRedraw();
    }

    /// <summary>Prépare et affiche la page pour la salle courante.</summary>
    public void Open(GameState state, Room room)
    {
        _layout = null;
        _currentRoomId = "";
        if (room != null && room.HasMapPosition)
        {
            _layout = DungeonMap.GetLayout(room.Zone);
            if (!string.IsNullOrEmpty(room.SceneFilePath))
                _currentRoomId = System.IO.Path.GetFileNameWithoutExtension(room.SceneFilePath);
        }

        if (_layout != null)
        {
            _hasMap = state.HasDungeonItem(_layout.Zone, DungeonItems.Map);
            _hasCompass = state.HasDungeonItem(_layout.Zone, DungeonItems.Compass);
            if (_states.Length != _layout.Rooms.Count) _states = new MapRoomState[_layout.Rooms.Count];
            for (int i = 0; i < _states.Length; i++)
            {
                var r = _layout.Rooms[i];
                _states[i] = DungeonMap.GetState(state.IsRoomVisited(_layout.Zone, r.Id), _hasMap);
            }
            PrepareDrawData(state);
            var here = _layout.Find(_currentRoomId);
            _floor = here != null ? here.Floor : room.MapFloor == FloorBasement ? FloorBasement : FloorGround;
        }

        _blinkOn = true;
        _blinkTimer = 0f;
        Visible = true;
        SetProcess(true);
        RefreshTexts();
        QueueRedraw();
    }

    /// <summary>Calcule coffres restants et état des portes (appelé à l'ouverture, jamais dans _Draw).</summary>
    private void PrepareDrawData(GameState state)
    {
        var rooms = _layout.Rooms;
        var links = _layout.Links;
        if (_chestKinds.Length != rooms.Count) _chestKinds = new int[rooms.Count];
        if (_linkA.Length != links.Count)
        {
            _linkA = new int[links.Count];
            _linkB = new int[links.Count];
            _linkOpen = new bool[links.Count];
        }
        for (int i = 0; i < rooms.Count; i++)
        {
            int left = 0;
            foreach (var id in rooms[i].ChestIds)
                if (!state.IsCollected(id)) left++;
            _chestKinds[i] = left == 0 ? 0 : rooms[i].HasBigChest ? 2 : 1;
        }
        for (int j = 0; j < links.Count; j++)
        {
            _linkA[j] = IndexOf(links[j].A);
            _linkB[j] = IndexOf(links[j].B);
            _linkOpen[j] = links[j].Kind == MapDoorKind.Free || state.IsCollected(links[j].DoorId);
        }
    }

    public void Close()
    {
        Visible = false;
        SetProcess(false);
    }

    /// <summary>Bascule vers l'étage voulu (« rdc » ou « sous_sol »). Sans effet s'il n'y a pas de carte.</summary>
    public void SetFloor(string floor)
    {
        if (_layout == null || floor == _floor) return;
        _floor = floor;
        RefreshTexts();
        QueueRedraw();
    }

    private void RefreshTexts()
    {
        bool has = _layout != null;
        _title.Text = Tr("MENU_CARTE");
        _noMapLabel.Visible = !has;
        _noMapLabel.Text = Tr("CARTE_AUCUNE");
        _help.Text = Tr("CARTE_AIDE");

        _floorLabel.Visible = has;
        _floorLabel.Text = Tr(_floor == FloorBasement ? "CARTE_ETAGE_SOUS_SOL" : "CARTE_ETAGE_RDC");
        _noItemLabel.Visible = has && !_hasMap;
        _noItemLabel.Text = Tr("CARTE_SANS_CARTE");

        _legendBrann.Visible = has;
        _legendBoss.Visible = has && _hasCompass;
        _legendStairs.Visible = has;
        _legendFall.Visible = has;
        _legendChest.Visible = has;
        _legendKeyDoor.Visible = has;
        _roomName.Visible = has;
        var current = has ? _layout.Find(_currentRoomId) : null;
        _roomName.Text = current != null && !string.IsNullOrEmpty(current.NameKey) ? Tr(current.NameKey) : "";
        _legendBrann.Text = Tr("CARTE_LEG_BRANN");
        _legendBoss.Text = Tr("CARTE_LEG_BOSS");
        _legendStairs.Text = Tr("CARTE_LEG_ESCALIER");
        _legendFall.Text = Tr("CARTE_LEG_TROU");
        _legendChest.Text = Tr("CARTE_LEG_COFFRE");
        _legendKeyDoor.Text = Tr("CARTE_LEG_PORTE_CLE");
    }

    // ---------------------------------------------------------------- dessin

    public override void _Draw()
    {
        DrawStyleBox(_background, new Rect2(Vector2.Zero, Size));
        if (_layout == null) return;

        DrawRect(new Rect2(8, 8, Size.X - 16, Size.Y - 16), _floor == FloorBasement ? TintBasement : TintGround, true);

        var rooms = _layout.Rooms;
        var links = _layout.Links;
        // Passages d'abord (sous les salles).
        for (int j = 0; j < links.Count; j++)
        {
            int ia = _linkA[j], ib = _linkB[j];
            if (ia < 0 || ib < 0) continue;
            if (rooms[ia].Floor != _floor || rooms[ib].Floor != _floor) continue;
            if (!DungeonMap.ShowLink(_states[ia], _states[ib])) continue;
            var kind = links[j].Kind;
            bool open = _linkOpen[j];
            var from = RoomRect(rooms[ia]).GetCenter();
            var to = RoomRect(rooms[ib]).GetCenter();
            DrawLine(from, to, open ? LinkColor : DoorColor(kind), 3f);
            if (kind != MapDoorKind.Free) DrawDoorMarker((from + to) / 2f, kind, open);
        }

        for (int i = 0; i < rooms.Count; i++)
        {
            var room = rooms[i];
            if (room.Floor != _floor || _states[i] == MapRoomState.Hidden) continue;
            var rect = RoomRect(room);
            DrawRoom(rect, _states[i]);

            if (DungeonMap.ShowBossIcon(room, _states[i], _hasCompass))
                DrawBossIcon(rect.GetCenter());
            if (_states[i] == MapRoomState.Visited)
            {
                if (room.HasStairs) DrawStairsIcon(rect.Position + new Vector2(4, 4));
                if (room.HasFall) DrawFallIcon(rect.Position + new Vector2(RoomSize.X - 8, 4));
            }
            if (_chestKinds[i] != 0 && DungeonMap.ShowChestIcon(_states[i], _hasCompass))
            {
                if (_chestKinds[i] == 2) DrawChestIcon(rect.Position + new Vector2(RoomSize.X - 14, RoomSize.Y - 11), true);
                else DrawChestIcon(rect.Position + new Vector2(RoomSize.X - 12, RoomSize.Y - 11), false);
            }
            if (room.Id == _currentRoomId)
            {
                DrawRect(rect.Grow(2f), CurrentRoomColor, false, 2f);
                if (_blinkOn) DrawBrannIcon(rect.GetCenter());
            }
        }

        // Légende : mêmes symboles que sur la carte.
        DrawBrannIcon(LegendOrigin + new Vector2(6, 6));
        if (_hasCompass) DrawBossIcon(LegendOrigin + new Vector2(6, LegendPitch + 6));
        DrawStairsIcon(LegendOrigin + new Vector2(1, LegendPitch * 2 + 1));
        DrawFallIcon(LegendOrigin + new Vector2(1, LegendPitch * 3 + 1));
        DrawChestIcon(LegendOrigin + new Vector2(1, LegendPitch * 4 + 2), false);
        DrawDoorMarker(LegendOrigin + new Vector2(6, LegendPitch * 5 + 6), MapDoorKind.Key, false);
    }

    private static Color DoorColor(MapDoorKind kind) => kind switch
    {
        MapDoorKind.Key => DoorKeyColor,
        MapDoorKind.BossKey => DoorBossKeyColor,
        MapDoorKind.Enemies => DoorEnemiesColor,
        MapDoorKind.Switch => DoorSwitchColor,
        _ => LinkColor,
    };

    /// <summary>Porte au milieu d'un passage : pleine si fermée (avec une clé pour les portes à clé), anneau si ouverte.</summary>
    private void DrawDoorMarker(Vector2 center, MapDoorKind kind, bool open)
    {
        var color = DoorColor(kind);
        bool isKey = kind == MapDoorKind.Key || kind == MapDoorKind.BossKey;
        if (open)
        {
            DrawRect(new Rect2(center - new Vector2(3, 3), new Vector2(6, 6)), color, false, 1f);
            return;
        }
        if (isKey)
        {
            DrawRect(new Rect2(center - new Vector2(5, 6), new Vector2(10, 12)), DoorBackdrop, true);
            if (_texKey != null) { DrawTexture(_texKey, center - _texKey.GetSize() / 2f, color); return; }
            DrawCircle(center + new Vector2(0, -2), 2.5f, color);
            DrawRect(new Rect2(center + new Vector2(-1, 0), new Vector2(2, 5)), color, true);
            return;
        }
        DrawRect(new Rect2(center - new Vector2(4, 4), new Vector2(8, 8)), DoorBackdrop, true);
        DrawRect(new Rect2(center - new Vector2(3, 3), new Vector2(6, 6)), color, true);
    }

    private void DrawChestIcon(Vector2 topLeft, bool big)
    {
        var tex = big ? _texBigChest : _texChest;
        if (tex != null) { DrawTexture(tex, topLeft); return; }
        var size = big ? new Vector2(10, 8) : new Vector2(8, 8);
        DrawRect(new Rect2(topLeft, size), big ? BigChestColor : ChestColor, true);
        DrawRect(new Rect2(topLeft, size), Colors.Black, false, 1f);
        DrawRect(new Rect2(topLeft + new Vector2(size.X / 2f - 1, 3), new Vector2(2, 2)), big ? Colors.Black : BigChestColor, true);
    }

    private int IndexOf(string id)
    {
        var rooms = _layout.Rooms;
        for (int i = 0; i < rooms.Count; i++)
            if (rooms[i].Id == id) return i;
        return -1;
    }

    private static Rect2 RoomRect(MapRoom room) =>
        new(GridOrigin + new Vector2(room.X * ColumnPitch, room.Y * RowPitch), RoomSize);

    private void DrawRoom(Rect2 rect, MapRoomState state)
    {
        var tex = state == MapRoomState.Visited ? _texVisited : _texUnknown;
        if (tex != null)
        {
            DrawTextureRect(tex, rect, false);
            return;
        }
        if (state == MapRoomState.Visited)
        {
            DrawRect(rect, VisitedFill, true);
            DrawRect(rect, VisitedBorder, false, 2f);
        }
        else
            DrawRect(rect, OutlineColor, false, 2f);
    }

    private void DrawBrannIcon(Vector2 center)
    {
        if (_texBrann != null) { DrawTexture(_texBrann, center - _texBrann.GetSize() / 2f); return; }
        DrawRect(new Rect2(center - new Vector2(4, 4), new Vector2(8, 8)), BrannColor, true);
        DrawRect(new Rect2(center - new Vector2(4, 4), new Vector2(8, 8)), Colors.Black, false, 1f);
    }

    private void DrawBossIcon(Vector2 center)
    {
        if (_texBoss != null) { DrawTexture(_texBoss, center - _texBoss.GetSize() / 2f); return; }
        DrawCircle(center, 5f, BossColor);
        DrawCircle(center, 2f, Colors.Black);
    }

    private void DrawStairsIcon(Vector2 topLeft)
    {
        if (_texStairs != null) { DrawTexture(_texStairs, topLeft); return; }
        DrawRect(new Rect2(topLeft + new Vector2(0, 6), new Vector2(4, 2)), StairsColor, true);
        DrawRect(new Rect2(topLeft + new Vector2(4, 3), new Vector2(4, 2)), StairsColor, true);
        DrawRect(new Rect2(topLeft + new Vector2(8, 0), new Vector2(4, 2)), StairsColor, true);
    }

    private void DrawFallIcon(Vector2 topLeft)
    {
        if (_texFall != null) { DrawTexture(_texFall, topLeft); return; }
        DrawCircle(topLeft + new Vector2(4, 4), 4f, FallColor);
        DrawArc(topLeft + new Vector2(4, 4), 4f, 0f, Mathf.Tau, 12, StairsColor, 1f);
    }

    // ---------------------------------------------------------------- construction

    private StyleBox CreateBackground()
    {
        var texture = _texFrame ?? LoadTexture("res://art/ui/panneau.png");
        if (texture != null)
        {
            var box = new StyleBoxTexture { Texture = texture };
            box.SetTextureMarginAll(8);
            return box;
        }
        var flat = new StyleBoxFlat { BgColor = new Color(0.1f, 0.1f, 0.2f), BorderColor = new Color(0.9f, 0.8f, 0.5f) };
        flat.SetBorderWidthAll(2);
        return flat;
    }

    private static Texture2D LoadOptional(string fileName)
    {
        string path = ArtFolder + fileName;
        return ResourceLoader.Exists(path) ? GD.Load<Texture2D>(path) : null;
    }

    private static Texture2D LoadTexture(string path) =>
        ResourceLoader.Exists(path) ? GD.Load<Texture2D>(path) : null;

    private Label CreateLabel(Vector2 position, float width, float height)
    {
        var label = new Label { Position = position, Size = new Vector2(width, height), MouseFilter = MouseFilterEnum.Ignore };
        AddChild(label);
        return label;
    }

    private Label CreateLegendLabel(int row)
    {
        // Les lignes de légende sont espacées de LegendPitch px, texte à droite de l'icône.
        float y = LegendOrigin.Y + row * LegendPitch;
        return CreateLabel(new Vector2(LegendOrigin.X + 20, y), 100, 12);
    }
}
