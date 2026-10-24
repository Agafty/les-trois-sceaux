using Godot;

/// <summary>
/// Interrupteur : une zone (Area2D) qui ouvre une porte quand elle est activée.
/// - Mode Fleche : dans le groupe « cible_fleche », activé par une flèche (<see cref="IArrowTarget"/>) ; l'épée est sans effet.
/// - Mode Epee : activé par un coup d'épée (<see cref="IMeleeTarget"/>) ; les flèches l'ignorent.
/// L'activation ouvre la porte du groupe « portes » dont l'Id vaut <see cref="Target"/> (dans la salle courante ; l'autre face
/// de la porte lit son état ouvert dans GameState au chargement). L'interrupteur reste activé : son Id est mémorisé dans GameState.
/// </summary>
public partial class Switch : Area2D, IArrowTarget, IMeleeTarget
{
    /// <summary>L'interrupteur vient d'être activé (pas émis quand il est déjà activé au chargement de la salle).</summary>
    [Signal]
    public delegate void ActivatedEventHandler(string switchId);

    /// <summary>Identifiant unique, ex. "donjon1_interrupteur_01". Vide : l'état n'est pas mémorisé.</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Id de la porte à ouvrir, ex. "donjon1_porte_03".</summary>
    [Export] public string Target { get; set; } = "";

    [Export] public SwitchMode Mode { get; set; } = SwitchMode.Fleche;

    public bool IsActive => _active;

    private const int FrameSize = 32;
    private static readonly StringName DoorGroup = Door.GroupName;

    private Sprite2D _sprite;
    private GameState _state;
    private bool _active;

    public override void _Ready()
    {
        _state = GetNode<GameState>("/root/GameState");
        _sprite = GetNode<Sprite2D>("Sprite2D");

        if (string.IsNullOrEmpty(Id))
            GD.PushWarning($"Interrupteur sans Id ({GetPath()}) : son état ne sera pas mémorisé.");
        if (string.IsNullOrEmpty(Target))
            GD.PushWarning($"Interrupteur {Id} : aucune cible (propriété « cible »).");

        SetupSprite();

        if (!string.IsNullOrEmpty(Id) && _state.IsCollected(Id))
        {
            ApplyActive();
            return;
        }

        if (Mode == SwitchMode.Fleche)
            AddToGroup(Arrow.TargetGroup);
    }

    public void OnArrowHit(Vector2 position, Vector2 direction)
    {
        if (Mode == SwitchMode.Fleche) Activate();
    }

    public void OnMeleeHit(Vector2 position)
    {
        if (Mode == SwitchMode.Epee) Activate();
    }

    /// <summary>Active l'interrupteur et ouvre sa porte. Sans effet s'il est déjà activé.</summary>
    public void Activate()
    {
        if (_active) return;
        if (!string.IsNullOrEmpty(Id))
            _state.MarkCollected(Id);
        ApplyActive();
        OpenTarget();
        EmitSignal(SignalName.Activated, Id);
    }

    private void OpenTarget()
    {
        // Une seule fois par activation : l'allocation de la liste de nœuds est sans importance.
        foreach (var node in GetTree().GetNodesInGroup(DoorGroup))
        {
            if (node is Door door && door.Id == Target)
            {
                door.Open();
                return;
            }
        }
        // Porte absente de cette salle : on mémorise quand même son ouverture, l'autre face la lira ouverte.
        _state.MarkCollected(Target);
        GD.PushWarning($"Interrupteur {Id} : aucune porte « {Target} » dans cette salle (groupe « portes »), ouverture mémorisée.");
    }

    private void ApplyActive()
    {
        _active = true;
        _sprite.Frame = _sprite.Hframes > 1 ? 1 : 0;
        RemoveFromGroup(Arrow.TargetGroup);
        SetDeferred(Area2D.PropertyName.Monitorable, false); // plus de détection : les flèches passent
    }

    // Image art/puzzles/interrupteur_<mode>.png (32 px par image : inactif, puis activé) ; à défaut celle de la flèche.
    private void SetupSprite()
    {
        string path = $"res://art/puzzles/interrupteur_{SwitchRules.TextureName(Mode)}.png";
        if (!ResourceLoader.Exists(path))
            path = "res://art/puzzles/interrupteur_fleche.png";
        var texture = GD.Load<Texture2D>(path);
        if (texture == null)
        {
            GD.PushError($"Interrupteur {Id} : image introuvable ({path}).");
            return;
        }
        _sprite.Texture = texture;
        _sprite.Hframes = Mathf.Clamp(texture.GetWidth() / FrameSize, 1, 2);
        _sprite.Frame = 0;
    }
}
