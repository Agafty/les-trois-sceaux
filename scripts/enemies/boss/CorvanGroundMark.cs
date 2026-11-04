using Godot;

/// <summary>
/// Marque dessinée au sol par Corvan : cercle d'ombre du marteau qui se remplit, poussière de l'impact, anneau d'ondes de l'eau noire,
/// flaque. Dessinée par le code (aucune image) ; se supprime toute seule après sa durée. Elle est posée juste au-dessus de la carte
/// (sous Brann et les ennemis) par <see cref="CorvanBoss"/>. Le nœud est à la position monde du centre du cercle.
/// </summary>
public partial class CorvanGroundMark : Node2D
{
    public enum Kind { HammerWarn, HammerImpact, WaveRing, Puddle, LanternGuide }

    /// <summary>Groupe de toutes les marques en cours (le boss les efface quand il change d'état).</summary>
    public static readonly StringName GroupName = "corvan_marques";

    private static readonly Color WarnFill = new(0.12f, 0.02f, 0.2f, 0.45f);
    private static readonly Color WarnCore = new(0.45f, 0.08f, 0.55f, 0.55f);
    private static readonly Color WarnRing = new(0.85f, 0.35f, 0.9f, 0.95f);
    private static readonly Color ImpactColor = new(0.95f, 0.9f, 0.8f, 1f);
    private static readonly Color WaveColor = new(0.25f, 0.55f, 0.8f, 1f);
    private static readonly Color PuddleColor = new(0.05f, 0.1f, 0.25f, 0.75f);

    private Kind _kind;
    private float _radius = 56f;
    private float _duration = 1f;
    private float _age;
    private Player _follow;
    private Color _tint = WaveColor;
    private AnimatedSprite2D _image;

    /// <summary>Cercle d'ombre du marteau : se remplit pendant <paramref name="seconds"/>, le coup tombe quand il est plein.</summary>
    public void Begin(Kind kind, float radius, float seconds, Color? tint = null)
    {
        _kind = kind;
        _tint = tint ?? WaveColor;
        _radius = radius;
        _duration = Mathf.Max(0.05f, seconds);
        _age = 0f;
        AddToGroup(GroupName);
        QueueRedraw();
    }

    /// <summary>
    /// Habille la marque d'une image du graphiste (planche art/bosses/corvan/) dont l'animation est étirée sur la durée de la marque.
    /// Sans le fichier, la marque reste dessinée par le code.
    /// </summary>
    public void UseImage(string framesPath, StringName animation, Vector2 offset)
    {
        if (!ResourceLoader.Exists(framesPath)) return;
        var frames = GD.Load<SpriteFrames>(framesPath);
        if (frames == null || !frames.HasAnimation(animation)) return;
        _image = new AnimatedSprite2D { SpriteFrames = frames, Position = offset };
        AddChild(_image);
        float natural = frames.GetFrameCount(animation) / Mathf.Max(0.1f, (float)frames.GetAnimationSpeed(animation));
        _image.SpeedScale = natural / _duration;
        _image.Play(animation);
        QueueRedraw();
    }

    /// <summary>
    /// Cercle clair qui montre la portée de la lanterne de Brann (manche de l'eau) : il suit Brann, devant lui, comme la vraie lumière
    /// des salles sombres. Dure tant que le boss ne l'efface pas.
    /// </summary>
    public void BeginGuide(Player player)
    {
        _kind = Kind.LanternGuide;
        _radius = LanternRules.LightRadius * 0.9f;
        _duration = float.MaxValue;
        _follow = player;
        AddToGroup(GroupName);
        FollowPlayer();
        QueueRedraw();
    }

    private void FollowPlayer()
    {
        if (_follow == null || !IsInstanceValid(_follow)) return;
        GlobalPosition = _follow.GlobalPosition + new Vector2(0f, 6f) + _follow.FacingDirection * LanternRules.LightOffset;
    }

    public override void _Process(double delta)
    {
        if (_kind == Kind.LanternGuide)
        {
            FollowPlayer();
            QueueRedraw();
            return;
        }
        _age += (float)delta;
        if (_age >= _duration + (_kind == Kind.HammerWarn ? 0.05f : 0f))
        {
            QueueFree();
            return;
        }
        QueueRedraw();
    }

    public override void _Draw()
    {
        float t = Mathf.Clamp(_age / _duration, 0f, 1f);
        switch (_kind)
        {
            case Kind.LanternGuide:
                DrawCircle(Vector2.Zero, _radius, new Color(1f, 0.85f, 0.5f, 0.08f));
                DrawArc(Vector2.Zero, _radius, 0f, Mathf.Tau, 48, new Color(1f, 0.85f, 0.5f, 0.4f), 1.5f);
                break;
            case Kind.HammerWarn:
                if (_image == null)
                {
                    DrawCircle(Vector2.Zero, _radius, WarnFill);
                    DrawCircle(Vector2.Zero, _radius * t, WarnCore);
                }
                // Dans les derniers instants le contour clignote : le coup arrive.
                bool blink = t > 0.75f && ((int)(_age * 14f) % 2 == 0);
                DrawArc(Vector2.Zero, _radius, 0f, Mathf.Tau, 48, blink ? Colors.White : WarnRing, 2f);
                break;
            case Kind.HammerImpact:
                if (_image != null) break;
                {
                    float a = 1f - t;
                    DrawCircle(Vector2.Zero, _radius, new Color(ImpactColor.R, ImpactColor.G, ImpactColor.B, 0.35f * a));
                    DrawArc(Vector2.Zero, _radius * (0.7f + 0.3f * t), 0f, Mathf.Tau, 48, new Color(1f, 1f, 1f, a), 3f);
                    break;
                }
            case Kind.WaveRing:
                if (_image != null) break;
                for (int i = 0; i < 3; i++)
                {
                    float k = (t * 2.2f + i / 3f) % 1f; // trois anneaux qui se resserrent vers le centre
                    DrawArc(Vector2.Zero, _radius * (1f - k * 0.8f), 0f, Mathf.Tau, 40, new Color(_tint.R, _tint.G, _tint.B, 0.3f + 0.6f * k), 2f);
                }
                break;
            case Kind.Puddle:
                {
                    float a = t > 0.8f ? (1f - t) / 0.2f : 1f;
                    DrawCircle(Vector2.Zero, _radius, new Color(PuddleColor.R, PuddleColor.G, PuddleColor.B, PuddleColor.A * a));
                    DrawArc(Vector2.Zero, _radius, 0f, Mathf.Tau, 40, new Color(_tint.R, _tint.G, _tint.B, a), 2f);
                    break;
                }
        }
    }
}
