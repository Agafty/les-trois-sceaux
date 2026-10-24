using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Godot;

/// <summary>
/// Coffre solide. Brann le touche par le bas, face vers le haut, et appuie sur « interact » :
/// le coffre s'ouvre, Brann brandit le contenu, le jeu est figé le temps de l'animation,
/// puis l'effet est appliqué. L'ouverture est mémorisée dans GameState (flag = Id).
/// </summary>
public partial class Chest : StaticBody2D
{
    /// <summary>Un coffre vient de finir de s'ouvrir (contenu déjà appliqué).</summary>
    [Signal]
    public delegate void OpenedEventHandler(string chestId, bool important);

    /// <summary>Identifiant unique en français, ex. "donjon1_coffre_03". Obligatoire.</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Contenu : un effet existant (rubis, clé, objet, quart de cœur...), comme un ramassable.</summary>
    [Export] public PickupEffect Effect { get; set; }

    /// <summary>Objet clé / grosse récompense : grand coffre, animation plus longue, sauvegarde automatique (plus tard).</summary>
    [Export] public bool Important { get; set; }

    /// <summary>Planche 2 cases (fermé, ouvert) du grand coffre, utilisée quand <see cref="Important"/> est vrai. Réglée dans coffre.tscn.</summary>
    [Export] public Texture2D ImportantTexture { get; set; }

    /// <summary>Largeur (px) de la collision du grand coffre (le petit utilise celle de la scène).</summary>
    [Export(PropertyHint.Range, "8,64,1")] public float ImportantBodyWidth { get; set; } = 28f;

    /// <summary>Écart horizontal maximal (px) entre Brann et le centre du coffre pour l'ouvrir.</summary>
    [Export(PropertyHint.Range, "4,64,1")] public float MaxHorizontalOffset { get; set; } = 20f;

    [Export(PropertyHint.Range, "0.2,5,0.1")] public float LiftDuration { get; set; } = 1f;

    [Export(PropertyHint.Range, "0.2,5,0.1")] public float ImportantLiftDuration { get; set; } = 2f;

    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName PlayerGroup = "player";
    private static readonly Vector2 IconOffset = new(0, -32); // au-dessus de la tête de Brann
    private static readonly Vector2 TextTop = new(0, 290);
    private const string ThemePath = "res://resources/ui/theme_jeu.tres";

    private const int ClosedFrame = 0;
    private const int OpenFrame = 1;

    // Coffres dont la zone contient Brann en ce moment : sert à n'ouvrir que le plus proche.
    private static readonly List<Chest> Candidates = new();
    private static Theme _theme;

    private Sprite2D _sprite;
    private Area2D _zone;
    private GameState _state;
    private SceneManager _sceneManager;
    private Player _playerInside;
    private Player _liftPlayer;
    private bool _opened;
    private bool _sequenceRunning;
    private bool _valid;
    private Node _temporaryIcon;
    private CanvasLayer _temporaryText;

    public override void _Ready()
    {
        SetPhysicsProcess(false); // activé seulement quand Brann est dans la zone
        _sprite = GetNode<Sprite2D>("Sprite2D");
        _zone = GetNode<Area2D>("ZoneInteraction");
        _state = GetNode<GameState>("/root/GameState");
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");

        if (Important)
            ApplyImportantLook();

        if (string.IsNullOrEmpty(Id))
        {
            GD.PushError($"Coffre sans Id ({GetPath()}) : il restera fermé. Donnez-lui un identifiant unique.");
            return;
        }
        if (Effect == null)
            GD.PushWarning($"Coffre {Id} : aucun Effect, il sera vide.");

        _valid = true;
        if (_state.IsCollected(Id))
        {
            _opened = true;
            _sprite.Frame = OpenFrame;
            _zone.SetDeferred(Area2D.PropertyName.Monitoring, false);
            return;
        }

        _sprite.Frame = ClosedFrame;
        _zone.BodyEntered += OnBodyEntered;
        _zone.BodyExited += OnBodyExited;
    }

    // Grand coffre : autre planche et collision plus large (forme dupliquée : la scène la partage entre instances).
    private void ApplyImportantLook()
    {
        if (ImportantTexture != null)
            _sprite.Texture = ImportantTexture;
        var shapeNode = GetNodeOrNull<CollisionShape2D>("CollisionShape2D");
        if (shapeNode?.Shape is RectangleShape2D rect)
        {
            var copy = (RectangleShape2D)rect.Duplicate();
            copy.Size = new Vector2(ImportantBodyWidth, rect.Size.Y);
            shapeNode.Shape = copy;
        }
    }

    public override void _ExitTree()
    {
        Candidates.Remove(this);
        if (_zone != null)
        {
            _zone.BodyEntered -= OnBodyEntered;
            _zone.BodyExited -= OnBodyExited;
        }
        // Salle déchargée en pleine animation : on dépause, et la récompense n'est jamais perdue.
        if (_sequenceRunning)
        {
            _sequenceRunning = false;
            try
            {
                var tree = GetTree();
                if (tree != null) tree.Paused = false;
                CleanupTemporaryNodes();
                Complete(_liftPlayer);
            }
            catch (Exception e)
            {
                GD.PushError($"Coffre {Id} (fermeture de la salle) : {e}");
            }
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        if (!_valid || _opened || _playerInside == null) return;
        if (!Input.IsActionJustPressed(ActionInteract)) return;

        if (!IsInstanceValid(_playerInside))
        {
            _playerInside = null;
            return;
        }
        var player = _playerInside;
        if (player.IsDead || !player.CanInteract) return;
        if (player.FacingDirection != Vector2.Up) return; // le coffre s'ouvre par le bas
        if (Mathf.Abs(player.GlobalPosition.X - GlobalPosition.X) >= MaxHorizontalOffset) return; // pas en face
        if (_sceneManager.IsTransitioning || GetTree().Paused) return;
        if (!IsClosestCandidate(player)) return;

        _ = OpenAsync(player);
    }

    // Plusieurs coffres côte à côte : seul le plus proche de Brann répond (les autres cèdent).
    private bool IsClosestCandidate(Player player)
    {
        float mine = GlobalPosition.DistanceSquaredTo(player.GlobalPosition);
        for (int i = 0; i < Candidates.Count; i++)
        {
            var other = Candidates[i];
            if (other == this || other._opened || !other._valid) continue;
            if (other.GlobalPosition.DistanceSquaredTo(player.GlobalPosition) < mine) return false;
        }
        return true;
    }

    private void OnBodyEntered(Node2D body)
    {
        if (!body.IsInGroup(PlayerGroup) || body is not Player player) return;
        _playerInside = player;
        if (!Candidates.Contains(this)) Candidates.Add(this);
        SetPhysicsProcess(true);
    }

    private void OnBodyExited(Node2D body)
    {
        if (body != _playerInside) return;
        _playerInside = null;
        Candidates.Remove(this);
        SetPhysicsProcess(false);
    }

    private async Task OpenAsync(Player player)
    {
        _opened = true;
        _sequenceRunning = true;
        _liftPlayer = player;
        _playerInside = null;
        Candidates.Remove(this);
        SetPhysicsProcess(false);
        var tree = GetTree();
        try
        {
            // Contenu sans effet possible (objet au max, vie au plafond) : erreur de level design, le coffre s'ouvre quand même.
            if (Effect != null && !Effect.CanApply(player, _state))
                GD.PushWarning($"Coffre {Id} : son contenu ne peut pas s'appliquer (objet déjà au maximum ?). Revoyez le level design.");

            _sprite.Frame = OpenFrame;
            _zone.SetDeferred(Area2D.PropertyName.Monitoring, false);
            player.BeginLift();
            ShowReward(player);
            tree.Paused = true; // tout le monde se fige, sauf ce qui est en ProcessMode Always

            float duration = Important ? ImportantLiftDuration : LiftDuration;
            // Minuteur « Always » (continue en pause) et indépendant du TimeScale (hit-stop éventuel).
            await ToSignal(tree.CreateTimer(duration, true, false, true), SceneTreeTimer.SignalName.Timeout);

            if (!_sequenceRunning) return; // salle déchargée : _ExitTree a déjà tout terminé
            _sequenceRunning = false;
            CleanupTemporaryNodes();
            tree.Paused = false;
            if (IsInstanceValid(player)) player.EndLift();
            Complete(player);
        }
        catch (Exception e)
        {
            GD.PushError($"Coffre {Id} : {e}");
            if (_sequenceRunning)
            {
                _sequenceRunning = false;
                if (IsInstanceValid(tree)) tree.Paused = false; // le jeu ne doit jamais rester figé
                try { CleanupTemporaryNodes(); } catch (Exception) { /* nœuds déjà détruits */ }
                _state.MarkCollected(Id);
            }
        }
    }

    // Applique le contenu puis mémorise l'ouverture (dans cet ordre : « ouvert » seulement une fois servi).
    private void Complete(Player player)
    {
        try
        {
            if (Effect != null && player != null && IsInstanceValid(player))
                Effect.Apply(player, _state);
        }
        finally
        {
            _state.MarkCollected(Id);
        }
        EmitSignal(SignalName.Opened, Id, Important);
        if (Important) _state.NotifyImportantChestOpened(Id);
    }

    // Icône au-dessus de la tête de Brann (enfant du joueur) et texte en bas de l'écran (CanvasLayer).
    private void ShowReward(Player player)
    {
        var icon = Effect?.GetIcon();
        if (icon != null)
        {
            // Les petites icônes (16 px) sont doublées pour rester lisibles à côté de Brann (32 px).
            float scale = Mathf.Max(icon.GetWidth(), icon.GetHeight()) <= 16 ? 2f : 1f;
            var sprite = new Sprite2D { Texture = icon, Position = IconOffset, Scale = new Vector2(scale, scale), ZIndex = 1 };
            player.AddChild(sprite);
            _temporaryIcon = sprite;
        }

        var nameKey = Effect?.GetNameKey();
        if (string.IsNullOrEmpty(nameKey)) return;

        var label = new Label
        {
            Text = string.Format(Tr("CHEST_OBTAIN"), Tr(nameKey)),
            Position = TextTop,
            Size = new Vector2(640, 20),
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        _theme ??= GD.Load<Theme>(ThemePath);
        if (_theme != null) label.Theme = _theme;

        _temporaryText = new CanvasLayer { Layer = 6 }; // au-dessus du HUD (5), sous le fondu (10)
        _temporaryText.AddChild(label);
        AddChild(_temporaryText);
    }

    private void CleanupTemporaryNodes()
    {
        if (IsInstanceValid(_temporaryIcon)) _temporaryIcon.QueueFree();
        if (IsInstanceValid(_temporaryText)) _temporaryText.QueueFree();
        _temporaryIcon = null;
        _temporaryText = null;
    }
}
