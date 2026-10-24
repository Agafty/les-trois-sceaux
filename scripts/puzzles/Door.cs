using Godot;

/// <summary>
/// Porte de donjon : un corps solide qui remplit une case et bloque la Sortie posée dessous.
/// - Cle : Brann pousse dessus avec une petite clé, elle est consommée (comme dans A Link to the Past).
/// - GrandeCle : demande la grande clé du donjon, non consommée.
/// - Ennemis : fermée tant que des ennemis de la salle sont vivants (la salle appelle <see cref="NotifyRoomCleared"/>).
/// - Interrupteur : ouverte de l'extérieur par <see cref="Open"/> (l'interrupteur viendra à l'étape suivante).
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

    /// <summary>Zone du donjon (celle de la Room), pour retrouver la grande clé. Réglée par la Room.</summary>
    [Export] public string Zone { get; set; } = "";

    /// <summary>Taille de la case occupée (px). Réglée par la Room d'après le rectangle Tiled.</summary>
    [Export] public Vector2 CellSize { get; set; } = new(32f, 32f);

    /// <summary>Pour une porte « ennemis » : la salle contient des ennemis vivants à l'arrivée (réglé par la Room).</summary>
    public bool RoomHasEnemies { get; set; }

    /// <summary>Durée (s) pendant laquelle Brann doit pousser vers la porte avant qu'elle s'ouvre.</summary>
    [Export(PropertyHint.Range, "0.05,1,0.05")] public float PushDuration { get; set; } = 0.25f;

    public bool IsOpen => _open;

    private static readonly StringName PlayerGroup = "player";
    private static readonly StringName MoveLeft = "move_left";
    private static readonly StringName MoveRight = "move_right";
    private static readonly StringName MoveUp = "move_up";
    private static readonly StringName MoveDown = "move_down";
    private const float MinPushDot = 0.6f; // Brann doit vraiment avancer vers la porte (pas la longer)
    private const float FadeDuration = 0.25f;
    private const int FrameSize = 32;

    private static readonly Texture2D[] PlaceholderCache = new Texture2D[4];

    private Sprite2D _sprite;
    private CollisionShape2D _shape;
    private Area2D _contact;
    private GameState _state;
    private Player _player;
    private float _pushTime;
    private bool _open;
    private bool _contactConnected;

    public override void _Ready()
    {
        SetPhysicsProcess(false); // activé seulement quand Brann touche la porte
        AddToGroup(GroupName);
        _state = GetNode<GameState>("/root/GameState");
        _sprite = GetNode<Sprite2D>("Sprite2D");
        _shape = GetNode<CollisionShape2D>("CollisionShape2D");
        _contact = GetNode<Area2D>("ZoneContact");

        if (string.IsNullOrEmpty(Id))
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

    /// <summary>Ouvre la porte quelle que soit sa nature (interrupteur, cinématique...). Sans effet si elle est déjà ouverte.</summary>
    public void Open()
    {
        if (_open) return;
        if (!string.IsNullOrEmpty(Id))
            _state.MarkCollected(Id);
        ApplyOpen(true);
        EmitSignal(SignalName.Opened, Id);
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
            if (_state.Keys <= 0) return;
            _state.AddKeys(-1);
            Open();
        }
        else if (Kind == DoorKind.GrandeCle)
        {
            if (_state.HasDungeonItem(Zone, DungeonItems.BigKey))
                Open(); // la grande clé n'est pas consommée
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
        var tween = CreateTween();
        tween.TweenProperty(_sprite, "modulate:a", 0f, FadeDuration);
        tween.TweenCallback(Callable.From(() => _sprite.Visible = false));
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

    // Image du graphiste art/puzzles/porte_<type>.png (32 px par image : fermée, puis ouverte) ou, à défaut, un placeholder.
    private void SetupSprite()
    {
        string path = $"res://art/puzzles/porte_{DoorRules.TextureName(Kind)}.png";
        Texture2D texture = ResourceLoader.Exists(path) ? GD.Load<Texture2D>(path) : PlaceholderTexture(Kind);
        int width = texture.GetWidth();
        if (width != FrameSize && width != FrameSize * 2)
            GD.PushWarning($"{path} : largeur {width} px, attendu 32 (fermée) ou 64 (fermée + ouverte).");
        _sprite.Texture = texture;
        _sprite.Hframes = Mathf.Clamp(texture.GetWidth() / FrameSize, 1, 2);
        _sprite.Frame = 0;
    }

    private static Texture2D PlaceholderTexture(DoorKind kind)
    {
        int index = (int)kind;
        if (PlaceholderCache[index] != null) return PlaceholderCache[index];

        var wood = new Color(0.36f, 0.23f, 0.13f);
        var dark = new Color(0.11f, 0.08f, 0.13f);
        var plate = kind switch
        {
            DoorKind.GrandeCle => new Color(0.75f, 0.2f, 0.25f),
            DoorKind.Ennemis => new Color(0.6f, 0.6f, 0.65f),
            DoorKind.Interrupteur => new Color(0.25f, 0.5f, 0.85f),
            _ => new Color(0.94f, 0.75f, 0.25f),
        };

        var image = Image.CreateEmpty(FrameSize, FrameSize, false, Image.Format.Rgba8);
        image.Fill(dark);
        image.FillRect(new Rect2I(2, 2, FrameSize - 4, FrameSize - 4), wood);
        image.FillRect(new Rect2I(FrameSize / 2 - 1, 2, 2, FrameSize - 4), dark); // joint central
        image.FillRect(new Rect2I(11, 11, 10, 10), dark);
        image.FillRect(new Rect2I(12, 12, 8, 8), plate); // serrure / plaque
        PlaceholderCache[index] = ImageTexture.CreateFromImage(image);
        return PlaceholderCache[index];
    }
}
