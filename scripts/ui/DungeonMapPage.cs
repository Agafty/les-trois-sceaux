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
    private static readonly Vector2 LegendOrigin = new(236, 84);

    private static readonly Color VisitedFill = new(0.85f, 0.72f, 0.40f);
    private static readonly Color VisitedBorder = new(0.35f, 0.25f, 0.12f);
    private static readonly Color OutlineColor = new(0.55f, 0.62f, 0.75f);
    private static readonly Color LinkColor = new(0.9f, 0.8f, 0.5f);
    private static readonly Color BrannColor = new(0.45f, 0.95f, 0.45f);
    private static readonly Color BossColor = new(0.9f, 0.2f, 0.2f);
    private static readonly Color StairsColor = new(1f, 1f, 1f);
    private static readonly Color FallColor = new(0.1f, 0.05f, 0.15f);

    private Label _title;
    private Label _floorLabel;
    private Label _noMapLabel;
    private Label _noItemLabel;
    private Label _help;
    private Label _legendBrann;
    private Label _legendBoss;
    private Label _legendStairs;
    private Label _legendFall;

    private Texture2D _texFrame;
    private Texture2D _texVisited;
    private Texture2D _texUnknown;
    private Texture2D _texBrann;
    private Texture2D _texBoss;
    private Texture2D _texStairs;
    private Texture2D _texFall;
    private StyleBox _background;

    private DungeonLayout _layout;
    private MapRoomState[] _states = System.Array.Empty<MapRoomState>();
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
        _background = CreateBackground();

        _title = CreateLabel(new Vector2(0, 14), Size.X, 12);
        _title.HorizontalAlignment = HorizontalAlignment.Center;
        _floorLabel = CreateLabel(new Vector2(LegendOrigin.X, 44), 110, 12);
        _noMapLabel = CreateLabel(new Vector2(16, 110), Size.X - 32, 12);
        _noMapLabel.HorizontalAlignment = HorizontalAlignment.Center;
        _noItemLabel = CreateLabel(new Vector2(LegendOrigin.X, 168), 112, 40);
        _noItemLabel.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _help = CreateLabel(new Vector2(16, 224), Size.X - 32, 12);
        _help.HorizontalAlignment = HorizontalAlignment.Center;

        _legendBrann = CreateLegendLabel(0);
        _legendBoss = CreateLegendLabel(1);
        _legendStairs = CreateLegendLabel(2);
        _legendFall = CreateLegendLabel(3);
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
        _legendBrann.Text = Tr("CARTE_LEG_BRANN");
        _legendBoss.Text = Tr("CARTE_LEG_BOSS");
        _legendStairs.Text = Tr("CARTE_LEG_ESCALIER");
        _legendFall.Text = Tr("CARTE_LEG_TROU");
    }

    // ---------------------------------------------------------------- dessin

    public override void _Draw()
    {
        DrawStyleBox(_background, new Rect2(Vector2.Zero, Size));
        if (_layout == null) return;

        var rooms = _layout.Rooms;
        // Liens d'abord (sous les salles).
        foreach (var (a, b) in _layout.Links)
        {
            int ia = IndexOf(a), ib = IndexOf(b);
            if (ia < 0 || ib < 0) continue;
            if (rooms[ia].Floor != _floor || rooms[ib].Floor != _floor) continue;
            if (!DungeonMap.ShowLink(_states[ia], _states[ib])) continue;
            DrawLine(RoomRect(rooms[ia]).GetCenter(), RoomRect(rooms[ib]).GetCenter(), LinkColor, 3f);
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
            if (_blinkOn && room.Id == _currentRoomId)
                DrawBrannIcon(rect.GetCenter());
        }

        // Légende : mêmes symboles que sur la carte.
        DrawBrannIcon(LegendOrigin + new Vector2(6, 6));
        if (_hasCompass) DrawBossIcon(LegendOrigin + new Vector2(6, 24));
        DrawStairsIcon(LegendOrigin + new Vector2(1, 38));
        DrawFallIcon(LegendOrigin + new Vector2(1, 56));
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
        // Les lignes de légende sont espacées de 18 px, texte à droite de l'icône.
        float y = LegendOrigin.Y + (row == 0 ? 0 : row == 1 ? 18 : row == 2 ? 36 : 54);
        return CreateLabel(new Vector2(LegendOrigin.X + 20, y), 100, 12);
    }
}
