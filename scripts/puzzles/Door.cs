using Godot;

/// <summary>
/// Porte de donjon : un corps solide qui remplit une case et bloque la Sortie posée dessous.
/// - Cle : Brann pousse dessus avec une petite clé, elle est consommée (comme dans A Link to the Past).
/// - GrandeCle : demande la grande clé du donjon, non consommée.
/// - Ennemis : fermée tant que des ennemis de la salle sont vivants (la salle appelle <see cref="NotifyRoomCleared"/>).
/// - Interrupteur : ouverte de l'extérieur par <see cref="Open"/> (l'interrupteur viendra à l'étape suivante).
/// Une Porte peut aussi être un obstacle d'overworld sans Sortie : voir <see cref="Appearance"/> (pont-levis, tronc, rocher, éboulis), de taille libre.
/// L'état « ouverte » est mémorisé dans GameState sous l'Id : les deux faces d'une même porte, une par salle,
/// partagent le même Id et donc le même état.
/// </summary>
public partial class Door : StaticBody2D
{
    /// <summary>La porte vient de s'ouvrir (pas émis quand elle est déjà ouverte au chargement de la salle).</summary>
    [Signal]
    public delegate void OpenedEventHandler(string doorId);

    /// <summary>Groupe Godot de toutes les portes : un interrupteur retrouve sa cible par Id dans ce groupe.</summary>
    public static readonly StringName GroupName = "portes";

    /// <summary>Identifiant unique, ex. "donjon1_porte_01". Vide : la porte s'ouvre mais l'état n'est pas mémorisé.</summary>
    [Export] public string Id { get; set; } = "";

    [Export] public DoorKind Kind { get; set; } = DoorKind.Cle;

    /// <summary>
    /// Apparence (propriété Tiled « apparence ») : « porte » (défaut, image choisie d'après le type), « pont_levis », « tronc », « rocher »,
    /// « eboulis ». Image art/puzzles/porte_&lt;apparence&gt;.png : une image de la taille de la porte, ou deux (fermée puis ouverte) côte à côte.
    /// Sans fichier, un placeholder est dessiné par le code.
    /// </summary>
    [Export] public string Appearance { get; set; } = DoorRules.DefaultAppearance;

    /// <summary>Zone du donjon (celle de la Room), pour retrouver la grande clé. Réglée par la Room.</summary>
    [Export] public string Zone { get; set; } = "";

    /// <summary>Taille de la case occupée (px). Réglée par la Room d'après le rectangle Tiled.</summary>
    [Export] public Vector2 CellSize { get; set; } = new(32f, 32f);

    /// <summary>Pour une porte « ennemis » : la salle contient des ennemis vivants à l'arrivée (réglé par la Room).</summary>
    public bool RoomHasEnemies { get; set; }

    /// <summary>Durée (s) pendant laquelle Brann doit pousser vers la porte avant qu'elle s'ouvre.</summary>
    [Export(PropertyHint.Range, "0.05,1,0.05")] public float PushDuration { get; set; } = 0.25f;

    public bool IsOpen => _open;

    /// <summary>Porte ouverte refermée le temps d'un combat de boss (voir <see cref="LockForEncounter"/>).</summary>
    public bool IsLockedForEncounter => _locked;

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName MoveLeft = "move_left";
    private static readonly StringName MoveRight = "move_right";
    private static readonly StringName MoveUp = "move_up";
    private static readonly StringName MoveDown = "move_down";
    private const float MinPushDot = 0.6f; // Brann doit vraiment avancer vers la porte (pas la longer)
    private const float FadeDuration = 0.25f;

    private static readonly System.Collections.Generic.Dictionary<string, Texture2D> PlaceholderCache = new();

    private Sprite2D _sprite;
    private CollisionShape2D _shape;
    private Area2D _contact;
    private GameState _state;
    private Player _player;
    private float _pushTime;
    private bool _open;
    private bool _locked;
    private Tween _fadeTween;
    private bool _contactConnected;

    public override void _Ready()
    {
        SetPhysicsProcess(false); // activé seulement quand Brann touche la porte
        AddToGroup(GroupName);
        _state = GetNode<GameState>("/root/GameState");
        _sprite = GetNode<Sprite2D>("Sprite2D");
        _shape = GetNode<CollisionShape2D>("CollisionShape2D");
        _contact = GetNode<Area2D>("ZoneContact");

        if (string.IsNullOrEmpty(Id) && Appearance == DoorRules.DefaultAppearance)
            GD.PushWarning($"Porte sans Id ({GetPath()}) : son état ne sera pas mémorisé.");

        ResizeShapes();
        SetupSprite();

        bool alreadyOpen = !string.IsNullOrEmpty(Id) && _state.IsCollected(Id);
        bool nothingToFight = Kind == DoorKind.Ennemis && !RoomHasEnemies;
        if (alreadyOpen || nothingToFight)
        {
            ApplyOpen(false);
            return;
        }

        if (DoorRules.OpensByPushing(Kind))
        {
            _contact.BodyEntered += OnBodyEntered;
            _contact.BodyExited += OnBodyExited;
            _contactConnected = true;
        }
    }

    public override void _ExitTree()
    {
        if (_contactConnected && _contact != null)
        {
            _contact.BodyEntered -= OnBodyEntered;
            _contact.BodyExited -= OnBodyExited;
            _contactConnected = false;
        }
    }

    /// <summary>
    /// Referme une porte ouverte pour la durée d'un combat de boss : solide et visible de nouveau, la Sortie derrière est ignorée.
    /// Rien n'est mémorisé (l'état « ouverte » reste dans GameState) : si la salle est rechargée, la porte est ouverte.
    /// Sans effet si la porte n'est pas ouverte.
    /// </summary>
    public void LockForEncounter()
    {
        if (!_open || _locked) return;
        _locked = true;
        _open = false;
        _fadeTween?.Kill();
        _shape.SetDeferred(CollisionShape2D.PropertyName.Disabled, false);
        _sprite.Visible = true;
        _sprite.Modulate = Colors.White;
        _sprite.Frame = 0;
    }

    /// <summary>Rouvre la porte refermée par <see cref="LockForEncounter"/> (victoire). Sans effet sinon.</summary>
    public void UnlockAfterEncounter()
    {
        if (!_locked) return;
        _locked = false;
        ApplyOpen(true);
        EmitSignal(SignalName.Opened, Id);
    }

    /// <summary>Ouvre la porte quelle que soit sa nature (interrupteur, cinématique...). Sans effet si elle est déjà ouverte.</summary>
    public void Open()
    {
        if (_open || _locked) return; // refermée pour un combat : seule la victoire la rouvre
        if (!string.IsNullOrEmpty(Id))
            _state.MarkCollected(Id);
        ApplyOpen(true);
        EmitSignal(SignalName.Opened, Id);
    }

    /// <summary>
    /// Ouvre la porte « id » de la salle courante (groupe « portes »). Si cette salle n'a aucune face de cette porte,
    /// l'ouverture est quand même mémorisée dans GameState (l'autre face la lira ouverte) et la méthode renvoie faux.
    /// Sert aux interrupteurs, plaques de pression et torches.
    /// </summary>
    public static bool OpenById(SceneTree tree, GameState state, string id)
    {
        // Appelé une fois par résolution d'énigme : l'allocation de la liste de nœuds est sans importance.
        foreach (var node in tree.GetNodesInGroup(GroupName))
        {
            if (node is Door door && door.Id == id)
            {
                door.Open();
                return true;
            }
        }
        state.MarkCollected(id);
        return false;
    }

    /// <summary>Appelé par la salle quand le dernier ennemi est mort : ouvre les portes « ennemis ».</summary>
    public void NotifyRoomCleared()
    {
        if (Kind == DoorKind.Ennemis) Open();
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_open || _player == null) return;
        if (!IsInstanceValid(_player))
        {
            _player = null;
            SetPhysicsProcess(false);
            return;
        }
        if (_player.IsDead) return;

        // Direction voulue par le joueur (touches ou manette) comparée à la direction de la porte.
        var input = Input.GetVector(MoveLeft, MoveRight, MoveUp, MoveDown);
        var toDoor = GlobalPosition - _player.GlobalPosition;
        if (input.LengthSquared() < 0.25f || toDoor.LengthSquared() < 1f || input.Normalized().Dot(toDoor.Normalized()) < MinPushDot)
        {
            _pushTime = 0f;
            return;
        }

        _pushTime += (float)delta;
        if (_pushTime >= PushDuration)
            TryUnlock();
    }

    private void TryUnlock()
    {
        _pushTime = 0f;
        if (Kind == DoorKind.Cle)
        {
            if (_state.Keys <= 0)
            {
                AudioManager.PlayAt(Sfx.PorteVerrouillee, GlobalPosition);
                return;
            }
            _state.AddKeys(-1);
            Open();
        }
        else if (Kind == DoorKind.GrandeCle)
        {
            if (_state.HasDungeonItem(Zone, DungeonItems.BigKey))
                Open(); // la grande clé n'est pas consommée
            else
                AudioManager.PlayAt(Sfx.PorteVerrouillee, GlobalPosition);
        }
    }

    private void OnBodyEntered(Node2D body)
    {
        if (!body.IsInGroup(PlayerGroup) || body is not Player player) return;
        _player = player;
        _pushTime = 0f;
        SetPhysicsProcess(true);
    }

    private void OnBodyExited(Node2D body)
    {
        if (body != _player) return;
        _player = null;
        SetPhysicsProcess(false);
    }

    // Passe à l'état « ouverte » : plus de collision, plus de détection, apparence ouverte.
    private void ApplyOpen(bool animate)
    {
        if (animate) AudioManager.PlayAt(Sfx.PorteOuvre, GlobalPosition);
        _open = true;
        _player = null;
        SetPhysicsProcess(false);
        _shape.SetDeferred(CollisionShape2D.PropertyName.Disabled, true);
        _contact.SetDeferred(Area2D.PropertyName.Monitoring, false);

        if (_sprite.Hframes > 1)
        {
            _sprite.Frame = 1; // l'image du graphiste montre la porte ouverte
            return;
        }
        if (!animate)
        {
            _sprite.Visible = false;
            return;
        }
        _fadeTween?.Kill();
        _fadeTween = CreateTween();
        _fadeTween.TweenProperty(_sprite, "modulate:a", 0f, FadeDuration);
        _fadeTween.TweenCallback(Callable.From(() => _sprite.Visible = false));
    }

    // Les formes de la scène sont partagées entre instances : on les duplique avant de changer la taille.
    private void ResizeShapes()
    {
        if (_shape.Shape is RectangleShape2D body && body.Size != CellSize)
        {
            var copy = (RectangleShape2D)body.Duplicate();
            copy.Size = CellSize;
            _shape.Shape = copy;
        }
        var contactShape = _contact.GetNode<CollisionShape2D>("CollisionShape2D");
        if (contactShape.Shape is RectangleShape2D zone)
        {
            var copy = (RectangleShape2D)zone.Duplicate();
            copy.Size = CellSize + new Vector2(12f, 12f); // dépasse de 6 px pour détecter Brann collé à la porte
            contactShape.Shape = copy;
        }
    }

    // Image du graphiste art/puzzles/porte_<type ou apparence>.png (une image de la taille de la porte, ou deux : fermée puis ouverte) ou, à défaut, un placeholder.
    private void SetupSprite()
    {
        int frameW = Mathf.Max(1, Mathf.RoundToInt(CellSize.X));
        int frameH = Mathf.Max(1, Mathf.RoundToInt(CellSize.Y));
        string textureName = DoorRules.TextureName(Kind, Appearance);
        string path = $"res://art/puzzles/porte_{textureName}.png";
        Texture2D texture = ResourceLoader.Exists(path) ? GD.Load<Texture2D>(path) : PlaceholderTexture(textureName, frameW, frameH);
        int width = texture.GetWidth();
        if ((width != frameW && width != frameW * 2) || texture.GetHeight() != frameH)
            GD.PushWarning($"{path} : {width}x{texture.GetHeight()} px, attendu {frameW}x{frameH} (fermée) ou {frameW * 2}x{frameH} (fermée + ouverte).");
        _sprite.Texture = texture;
        _sprite.Hframes = Mathf.Clamp(width / frameW, 1, 2);
        _sprite.Frame = 0;
    }

    private static Texture2D PlaceholderTexture(string textureName, int w, int h)
    {
        string key = $"{textureName}_{w}x{h}";
        if (PlaceholderCache.TryGetValue(key, out var cached) && GodotObject.IsInstanceValid(cached)) return cached;

        var wood = new Color(0.36f, 0.23f, 0.13f);
        var dark = new Color(0.11f, 0.08f, 0.13f);
        int frames = textureName == "pont_levis" ? 2 : 1;
        var image = Image.CreateEmpty(w * frames, h, false, Image.Format.Rgba8);
        switch (textureName)
        {
            case "pont_levis":
                // Image 1 : panneau relevé, debout et sombre. Image 2 : tablier abaissé, planches claires.
                image.FillRect(new Rect2I(0, 0, w, h), dark);
                image.FillRect(new Rect2I(3, 3, w - 6, h - 6), wood.Darkened(0.25f));
                for (int x = 3 + 8; x < w - 3; x += 8) image.FillRect(new Rect2I(x, 3, 2, h - 6), dark);
                image.FillRect(new Rect2I(w, 0, w, h), wood);
                for (int y = 6; y < h; y += 8) image.FillRect(new Rect2I(w, y, w, 2), dark);
                image.FillRect(new Rect2I(w, 0, 3, h), dark);
                image.FillRect(new Rect2I(w * 2 - 3, 0, 3, h), dark);
                break;
            case "tronc":
                image.FillRect(new Rect2I(0, h / 4, w, h / 2), wood);
                image.FillRect(new Rect2I(0, h / 4, w, 2), dark);
                image.FillRect(new Rect2I(0, h * 3 / 4 - 2, w, 2), dark);
                for (int x = 8; x < w; x += 16) image.FillRect(new Rect2I(x, h / 4 + 6, 2, h / 2 - 12), dark);
                break;
            case "rocher":
            case "eboulis":
                var stone = new Color(0.5f, 0.5f, 0.54f);
                image.FillRect(new Rect2I(1, 4, w - 2, h - 6), stone);
                image.FillRect(new Rect2I(1, 4, w - 2, 2), dark);
                image.FillRect(new Rect2I(1, h - 4, w - 2, 2), dark);
                for (int x = 6; x < w - 4; x += 12) image.FillRect(new Rect2I(x, 10, 2, h - 18), dark);
                break;
            default:
                var plate = textureName switch
                {
                    "grande_cle" => new Color(0.75f, 0.2f, 0.25f),
                    "ennemis" => new Color(0.6f, 0.6f, 0.65f),
                    "interrupteur" => new Color(0.25f, 0.5f, 0.85f),
                    _ => new Color(0.94f, 0.75f, 0.25f),
                };
                image.Fill(dark);
                image.FillRect(new Rect2I(2, 2, w - 4, h - 4), wood);
                image.FillRect(new Rect2I(w / 2 - 1, 2, 2, h - 4), dark); // joint central
                image.FillRect(new Rect2I(w / 2 - 5, h / 2 - 5, 10, 10), dark);
                image.FillRect(new Rect2I(w / 2 - 4, h / 2 - 4, 8, 8), plate); // serrure / plaque
                break;
        }
        var texture = ImageTexture.CreateFromImage(image);
        PlaceholderCache[key] = texture;
        return texture;
    }
}
