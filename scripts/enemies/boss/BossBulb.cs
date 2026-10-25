using Godot;

/// <summary>
/// Bulbe de corruption posé sur les bois de Sylve : une cible de flèche (groupe « cible_fleche », <see cref="IArrowTarget"/>).
/// Une flèche le détruit ; l'épée ne lui fait rien (<see cref="IMeleeTarget"/> : simple éclat « rien ne passe »).
/// Image art/bosses/sylve/bulbe.png : cases de <see cref="FrameSize"/> px, 0-1 intact (boucle), 2-4 éclatement puis le bulbe disparaît.
/// </summary>
public partial class BossBulb : Area2D, IArrowTarget, IMeleeTarget
{
    /// <summary>Le bulbe vient d'être touché par une flèche (il éclate).</summary>
    [Signal]
    public delegate void DestroyedEventHandler();

    [Export(PropertyHint.File, "*.png")] public string TexturePath { get; set; } = "res://art/bosses/sylve/bulbe.png";

    /// <summary>Taille d'une case de la planche (px).</summary>
    [Export(PropertyHint.Range, "8,64,1")] public int FrameSize { get; set; } = 16;

    /// <summary>Case de départ de l'éclatement (les cases d'avant sont l'état intact).</summary>
    [Export] public int BurstFirstFrame { get; set; } = 2;

    /// <summary>Durée (s) d'une case, intact ou éclatement.</summary>
    [Export(PropertyHint.Range, "0.02,1,0.01")] public float FrameTime { get; set; } = 0.12f;

    /// <summary>Vrai tant que le bulbe peut être détruit (faux avant le début du combat).</summary>
    public bool Armed
    {
        get => _armed;
        set
        {
            _armed = value;
            if (!IsInsideTree()) return;
            if (value && !IsDestroyed && !IsInGroup(Arrow.TargetGroup)) AddToGroup(Arrow.TargetGroup);
            else if (!value && IsInGroup(Arrow.TargetGroup)) RemoveFromGroup(Arrow.TargetGroup);
        }
    }

    public bool IsDestroyed { get; private set; }

    private Sprite2D _sprite;
    private bool _armed;
    private float _animTime;
    private Tween _flash;

    public override void _Ready()
    {
        _sprite = GetNode<Sprite2D>("Sprite2D");
        if (ResourceLoader.Exists(TexturePath))
        {
            var texture = GD.Load<Texture2D>(TexturePath);
            _sprite.Texture = texture;
            _sprite.Hframes = Mathf.Max(1, texture.GetWidth() / FrameSize);
        }
        else
            GD.PushWarning($"Bulbe : image absente ({TexturePath}).");
        Armed = _armed; // applique le groupe maintenant que le nœud est dans l'arbre
    }

    public override void _Process(double delta)
    {
        if (_sprite.Texture == null || !Visible) return;
        _animTime += (float)delta;
        int step = (int)(_animTime / FrameTime);
        if (!IsDestroyed)
        {
            _sprite.Frame = Mathf.Min(step % Mathf.Max(1, BurstFirstFrame), _sprite.Hframes - 1);
            if (_armed) // le combat a commencé : les bulbes pulsent pour dire « tire ici »
            {
                float pulse = 0.5f + 0.5f * Mathf.Sin(_animTime * 7f);
                _sprite.Scale = Vector2.One * (1f + 0.25f * pulse);
                if (_flash == null || !_flash.IsRunning())
                    _sprite.Modulate = new Color(1f + 0.6f * pulse, 1f + 0.3f * pulse, 1f + 0.6f * pulse);
            }
            return;
        }
        int frame = BurstFirstFrame + step;
        if (frame >= _sprite.Hframes)
        {
            Visible = false; // éclatement terminé
            return;
        }
        _sprite.Frame = frame;
    }

    public void OnArrowHit(Vector2 position, Vector2 direction)
    {
        if (!_armed || IsDestroyed) return;
        IsDestroyed = true;
        _sprite.Scale = Vector2.One;
        _sprite.Modulate = Colors.White;
        _animTime = 0f; // l'éclatement repart de sa première case
        RemoveFromGroup(Arrow.TargetGroup);
        SetDeferred(Area2D.PropertyName.Monitorable, false);
        EmitSignal(SignalName.Destroyed);
    }

    // Épée : le bulbe est protégé, un éclat clair le montre (le boss lui-même est invulnérable pendant cette phase).
    public void OnMeleeHit(Vector2 position)
    {
        if (!_armed || IsDestroyed) return;
        _flash?.Kill();
        _sprite.Modulate = new Color(2.5f, 2.5f, 2.5f);
        _flash = CreateTween();
        _flash.TweenProperty(_sprite, "modulate", Colors.White, 0.15f);
    }
}
