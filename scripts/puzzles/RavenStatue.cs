using Godot;

/// <summary>
/// Statue du corbeau : point de sauvegarde manuelle. Brann se place en face (sous la statue, regardant vers le haut)
/// et appuie sur « interact » : la vie est restaurée, la partie est sauvegardée dans l'emplacement courant,
/// et un court message s'affiche (sans mettre le jeu en pause).
/// </summary>
public partial class RavenStatue : StaticBody2D
{
    /// <summary>Identifiant unique en français, ex. "donjon1_statue_entree". Sert à repérer la statue (logs).</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Écart horizontal maximal (px) entre Brann et le centre de la statue.</summary>
    [Export(PropertyHint.Range, "4,64,1")] public float MaxHorizontalOffset { get; set; } = 24f;

    /// <summary>Durée d'affichage du message (secondes).</summary>
    [Export(PropertyHint.Range, "0.5,5,0.1")] public float MessageDuration { get; set; } = 1.5f;

    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName PlayerGroup = "player";
    private static readonly Vector2 MessagePosition = new(0, 290);
    private const string ThemePath = "res://resources/ui/theme_jeu.tres";
    private const string TexturePath = "res://art/puzzles/statue_corbeau.png";
    private const int FrameWidth = 32;
    private const int FallbackSlot = 1;

    private Sprite2D _sprite;
    private Area2D _zone;
    private Timer _messageTimer;
    private Label _message;
    private GameState _state;
    private SaveSystem _saveSystem;
    private SceneManager _sceneManager;
    private Player _playerInside;
    private static Theme _theme;

    public override void _Ready()
    {
        SetPhysicsProcess(false); // activé seulement quand Brann est dans la zone
        _sprite = GetNode<Sprite2D>("Sprite2D");
        _zone = GetNode<Area2D>("ZoneInteraction");
        _state = GetNode<GameState>("/root/GameState");
        _saveSystem = GetNode<SaveSystem>("/root/SaveSystem");
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");

        SetupSprite();
        BuildMessage();

        _zone.BodyEntered += OnBodyEntered;
        _zone.BodyExited += OnBodyExited;
    }

    public override void _ExitTree()
    {
        if (_zone == null) return;
        _zone.BodyEntered -= OnBodyEntered;
        _zone.BodyExited -= OnBodyExited;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_playerInside == null || !Input.IsActionJustPressed(ActionInteract)) return;
        if (!IsInstanceValid(_playerInside))
        {
            _playerInside = null;
            SetPhysicsProcess(false);
            return;
        }

        var player = _playerInside;
        if (player.IsDead || !player.CanInteract) return;
        if (player.FacingDirection != Vector2.Up) return; // face à la statue, par le bas
        if (Mathf.Abs(player.GlobalPosition.X - GlobalPosition.X) >= MaxHorizontalOffset) return;
        if (_sceneManager.IsTransitioning || GetTree().Paused) return;

        Activate(player);
    }

    private void Activate(Player player)
    {
        // 1) Vie pleine d'abord : la sauvegarde doit contenir la vie restaurée.
        //    Health.Heal émet HealthChanged -> Player -> GameState (sens unique, comme pour un cœur ramassé).
        var health = player.Health;
        if (health != null)
            health.Heal(health.MaxHealth - health.CurrentHealth);

        // 2) Sauvegarde. Sans partie lancée depuis l'écran titre (F6 sur une salle), il n'y a pas d'emplacement.
        int slot = _saveSystem.CurrentSlot;
        bool saved = false;
        if (slot == 0 && _saveSystem.HasSave(FallbackSlot))
        {
            // Lancement direct d'une salle : on n'écrase jamais une vraie sauvegarde.
            GD.Print($"Statue {Id} : aucune partie en cours et l'emplacement {FallbackSlot} est occupé, pas de sauvegarde. Lancez le jeu par l'écran titre.");
        }
        else
        {
            if (slot == 0)
            {
                slot = FallbackSlot;
                GD.Print($"Statue {Id} : aucune partie en cours (lancement direct d'une salle), sauvegarde dans l'emplacement {slot} (vide).");
            }
            saved = _saveSystem.Save(slot);
        }
        _message.Text = Tr(saved ? "SAVE_DONE" : "SAVE_FAILED");
        _message.Visible = true;
        if (_sprite.Hframes > 1) _sprite.Frame = 1; // 2e image = corbeau « éveillé », si le graphiste l'a prévue
        _messageTimer.Start(MessageDuration);
    }

    private void OnMessageTimeout()
    {
        _message.Visible = false;
        _sprite.Frame = 0;
    }

    private void OnBodyEntered(Node2D body)
    {
        if (!body.IsInGroup(PlayerGroup) || body is not Player player) return;
        _playerInside = player;
        SetPhysicsProcess(true);
    }

    private void OnBodyExited(Node2D body)
    {
        if (body != _playerInside) return;
        _playerInside = null;
        SetPhysicsProcess(false);
    }

    // Texture du graphiste si elle existe (32 px par image), sinon un rectangle de remplacement.
    private void SetupSprite()
    {
        Texture2D texture = ResourceLoader.Exists(TexturePath) ? GD.Load<Texture2D>(TexturePath) : null;
        if (texture == null)
        {
            var image = Image.CreateEmpty(FrameWidth, 64, false, Image.Format.Rgba8);
            image.Fill(new Color(0.25f, 0.22f, 0.32f));
            image.FillRect(new Rect2I(10, 8, 12, 12), new Color(0.75f, 0.7f, 0.9f)); // « tête » du corbeau
            texture = ImageTexture.CreateFromImage(image);
        }

        _sprite.Texture = texture;
        _sprite.Hframes = Mathf.Clamp(texture.GetWidth() / FrameWidth, 1, 2);
        _sprite.Frame = 0;
        _sprite.Offset = new Vector2(0, -texture.GetHeight() / 2f); // origine = pied de la statue
    }

    private void BuildMessage()
    {
        _message = new Label
        {
            Position = MessagePosition,
            Size = new Vector2(640, 20),
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        _theme ??= GD.Load<Theme>(ThemePath);
        if (_theme != null) _message.Theme = _theme;

        var layer = new CanvasLayer { Layer = 6 }; // au-dessus du HUD (5), sous le fondu (10)
        layer.AddChild(_message);
        AddChild(layer);

        _messageTimer = new Timer { OneShot = true };
        _messageTimer.Timeout += OnMessageTimeout;
        AddChild(_messageTimer);
    }
}
