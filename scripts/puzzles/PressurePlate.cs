using System.Collections.Generic;
using Godot;

/// <summary>
/// Plaque de pression : une case de 32x32 enfoncée tant qu'un <see cref="PushBlock"/> (centre dans la case) ou Brann
/// (centre des pieds dans la case) est dessus, selon <see cref="Trigger"/>. Quand toutes les plaques de même
/// <see cref="Target"/> sont enfoncées en même temps, la porte (groupe « portes », Id = Target) s'ouvre pour de bon :
/// l'ouverture est mémorisée par l'id de la porte, comme pour un interrupteur. L'état des plaques elles-mêmes n'est pas sauvegardé.
/// Image : art/puzzles/plaque_pression.png (2 images de 32 px : relevée, enfoncée), sinon un placeholder dessiné par le code.
/// </summary>
public partial class PressurePlate : Area2D
{
    /// <summary>La plaque vient de s'enfoncer ou de se relever.</summary>
    [Signal]
    public delegate void PressedChangedEventHandler(bool pressed);

    /// <summary>Identifiant (ex. "donjon1_plaque_01"). Non mémorisé : sert aux messages.</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Id de la porte (type « interrupteur ») à ouvrir quand toutes les plaques de même cible sont enfoncées.</summary>
    [Export] public string Target { get; set; } = "";

    [Export] public PlateTrigger Trigger { get; set; } = PlateTrigger.Tous;

    /// <summary>Côté d'une case (px).</summary>
    [Export(PropertyHint.Range, "8,128,1")] public float CellSize { get; set; } = 32f;

    public bool IsPressed => _pressed;

    /// <summary>Groupe Godot de toutes les plaques (retrouver celles de même cible).</summary>
    public static readonly StringName GroupName = "plaques";

    private const int FrameSize = 32;
    private const string TexturePath = "res://art/puzzles/plaque_pression.png";
    private static readonly StringName PlayerGroup = "player";
    private static Texture2D _placeholder;

    private readonly List<Node2D> _inside = new();
    private Sprite2D _sprite;
    private GameState _state;
    private bool _pressed;
    private bool _solved; // la porte était déjà ouverte au chargement : la plaque est dessinée enfoncée

    public override void _Ready()
    {
        _state = GetNode<GameState>("/root/GameState");
        _sprite = GetNode<Sprite2D>("Sprite2D");
        AddToGroup(GroupName);
        SetPhysicsProcess(false); // actif seulement quand un corps est sur la plaque

        if (string.IsNullOrEmpty(Target))
            GD.PushWarning($"Plaque de pression {Id} : aucune cible (propriété « cible »).");

        SetupSprite();
        if (!string.IsNullOrEmpty(Target) && _state.IsCollected(Target))
        {
            _solved = true;
            ApplyFrame();
        }
        BodyEntered += OnBodyEntered;
        BodyExited += OnBodyExited;
    }

    public override void _ExitTree()
    {
        BodyEntered -= OnBodyEntered;
        BodyExited -= OnBodyExited;
    }

    public override void _PhysicsProcess(double delta) => Refresh();

    private void OnBodyEntered(Node2D body)
    {
        bool isBlock = body is PushBlock;
        bool isPlayer = body.IsInGroup(PlayerGroup);
        if (!PressurePlateRules.Accepts(Trigger, isBlock, isPlayer)) return;
        if (!_inside.Contains(body)) _inside.Add(body);
        SetPhysicsProcess(true);
        Refresh();
    }

    private void OnBodyExited(Node2D body)
    {
        _inside.Remove(body);
        Refresh();
    }

    // Une plaque est enfoncée si le centre d'un corps accepté est dans sa case (centre des pieds pour Brann).
    private void Refresh()
    {
        bool pressed = false;
        var center = GlobalPosition;
        for (int i = _inside.Count - 1; i >= 0; i--)
        {
            var body = _inside[i];
            if (!IsInstanceValid(body) || !body.IsInsideTree())
            {
                _inside.RemoveAt(i);
                continue;
            }
            if (body is PushBlock { IsSliding: true }) continue; // un bloc en mouvement n'enfonce pas la plaque
            var point = body is PushBlock ? body.GlobalPosition : body.GlobalPosition + Player.FeetOffset;
            if (body is Player { IsDead: true }) continue;
            if (PressurePlateRules.IsInCell(point.X, point.Y, center.X, center.Y, CellSize))
                pressed = true;
        }
        if (_inside.Count == 0)
            SetPhysicsProcess(false);
        SetPressed(pressed);
    }

    private void SetPressed(bool pressed)
    {
        if (pressed == _pressed) return;
        _pressed = pressed;
        ApplyFrame();
        EmitSignal(SignalName.PressedChanged, pressed);
        if (pressed)
        {
            AudioManager.PlayAt(Sfx.Plaque, GlobalPosition);
            TryOpenTarget();
        }
    }

    // Toutes les plaques de même cible enfoncées ensemble : la porte s'ouvre (et le reste). Se produit rarement.
    private void TryOpenTarget()
    {
        if (string.IsNullOrEmpty(Target) || _state.IsCollected(Target)) return;
        foreach (var node in GetTree().GetNodesInGroup(GroupName))
            if (node is PressurePlate other && other.Target == Target && !other.IsPressed)
                return;
        if (!Door.OpenById(GetTree(), _state, Target))
            GD.PushWarning($"Plaque {Id} : aucune porte « {Target} » dans cette salle (groupe « portes »), ouverture mémorisée.");
    }

    private void ApplyFrame() => _sprite.Frame = (_pressed || _solved) && _sprite.Hframes > 1 ? 1 : 0;

    private void SetupSprite()
    {
        Texture2D texture;
        if (ResourceLoader.Exists(TexturePath))
            texture = GD.Load<Texture2D>(TexturePath);
        else
            texture = _placeholder ??= BuildPlaceholder();
        _sprite.Texture = texture;
        _sprite.Hframes = Mathf.Clamp(texture.GetWidth() / FrameSize, 1, 2);
        _sprite.Frame = 0;
    }

    // Placeholder : dalle claire en relief (relevée), puis dalle sombre en creux (enfoncée).
    private static Texture2D BuildPlaceholder()
    {
        var image = Image.CreateEmpty(FrameSize * 2, FrameSize, false, Image.Format.Rgba8);
        image.Fill(new Color(0, 0, 0, 0));
        var edge = new Color(0.1f, 0.09f, 0.14f);
        DrawPlate(image, 0, edge, new Color(0.62f, 0.6f, 0.7f), new Color(0.78f, 0.76f, 0.86f));
        DrawPlate(image, FrameSize, edge, new Color(0.38f, 0.36f, 0.46f), new Color(0.3f, 0.28f, 0.38f));
        return ImageTexture.CreateFromImage(image);
    }

    private static void DrawPlate(Image image, int x, Color edge, Color face, Color highlight)
    {
        image.FillRect(new Rect2I(x + 3, 3, 26, 26), edge);
        image.FillRect(new Rect2I(x + 5, 5, 22, 22), face);
        image.FillRect(new Rect2I(x + 5, 5, 22, 2), highlight);
        image.FillRect(new Rect2I(x + 5, 5, 2, 22), highlight);
    }
}
