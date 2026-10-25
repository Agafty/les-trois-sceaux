using Godot;

/// <summary>
/// Ronces qui sortent du sol (attaque de la phase 1 de Sylve). D'abord un cercle d'avertissement qui se remplit
/// (<see cref="WarnDuration"/>), puis les épines surgissent et blessent (<see cref="ActiveDuration"/>), puis elles s'effacent.
/// Dessinée par le code (pas d'image). Le nœud est posé <see cref="SortOffset"/> px au-dessus de son centre visible, pour que
/// le tri en profondeur la place sous Brann quand il est dessus ; <see cref="HitBox"/> est un enfant qui s'active au bon moment.
/// </summary>
public partial class ThornEruption : Node2D
{
    /// <summary>Groupe Godot de toutes les ronces en cours (le boss les efface quand il change de phase).</summary>
    public static readonly StringName GroupName = "ronces_boss";

    [Export(PropertyHint.Range, "0.2,3,0.05")] public float WarnDuration { get; set; } = 1.0f;
    [Export(PropertyHint.Range, "0.1,2,0.05")] public float ActiveDuration { get; set; } = 0.5f;
    [Export(PropertyHint.Range, "0.05,1,0.05")] public float FadeDuration { get; set; } = 0.25f;
    [Export(PropertyHint.Range, "8,48,1")] public float Radius { get; set; } = 22f;

    /// <summary>Décalage (px) entre l'origine du nœud et le centre dessiné.</summary>
    public const float SortOffset = 24f;

    private const int Spikes = 8;
    private static readonly Color WarnFill = new(0.35f, 0.05f, 0.45f, 0.35f);
    private static readonly Color WarnRing = new(0.9f, 0.3f, 0.9f, 0.9f);
    private static readonly Color SpikeColor = new(0.14f, 0.05f, 0.2f);
    private static readonly Color SpikeTip = new(0.6f, 0.2f, 0.65f);
    private static readonly Vector2[][] SpikeShapes = BuildSpikes();

    private HitBox _hitBox;
    private float _time;
    private bool _active;

    public override void _Ready()
    {
        AddToGroup(GroupName);
        _hitBox = GetNode<HitBox>("HitBox");
        var shapeNode = _hitBox.GetNode<CollisionShape2D>("CollisionShape2D");
        shapeNode.Shape = new CircleShape2D { Radius = Radius - 3f }; // un peu plus petit que le cercle : indulgent
        shapeNode.Position = new Vector2(0f, SortOffset);
        _hitBox.Monitoring = false;
        ZIndex = 0;
    }

    public override void _PhysicsProcess(double delta)
    {
        _time += (float)delta;
        if (!_active && _time >= WarnDuration)
        {
            _active = true;
            _hitBox.Monitoring = true;
        }
        float end = WarnDuration + ActiveDuration;
        if (_active && _time >= end)
        {
            _hitBox.Monitoring = false;
            if (_time >= end + FadeDuration)
            {
                QueueFree();
                return;
            }
        }
        QueueRedraw();
    }

    public override void _Draw()
    {
        var center = new Vector2(0f, SortOffset);
        if (_time < WarnDuration)
        {
            float t = _time / WarnDuration; // le disque se remplit : le coup arrive quand il est plein
            DrawCircle(center, Radius, WarnFill);
            DrawCircle(center, Radius * t, new Color(WarnRing.R, WarnRing.G, WarnRing.B, 0.45f));
            DrawArc(center, Radius, 0f, Mathf.Tau, 24, WarnRing, 2f);
            return;
        }
        float end = WarnDuration + ActiveDuration;
        float alpha = _time < end ? 1f : 1f - (_time - end) / FadeDuration;
        float rise = _time < WarnDuration + 0.08f ? (_time - WarnDuration) / 0.08f : 1f; // les épines jaillissent vite
        DrawSetTransform(center, 0f, new Vector2(Radius * rise, Radius * rise));
        for (int i = 0; i < SpikeShapes.Length; i++)
            DrawColoredPolygon(SpikeShapes[i], new Color(SpikeColor.R, SpikeColor.G, SpikeColor.B, alpha));
        DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
        DrawCircle(center, 4f, new Color(SpikeTip.R, SpikeTip.G, SpikeTip.B, alpha));
    }

    // Huit triangles pointant vers l'extérieur, pour un rayon de 1 (mis à l'échelle au dessin).
    private static Vector2[][] BuildSpikes()
    {
        var shapes = new Vector2[Spikes][];
        for (int i = 0; i < Spikes; i++)
        {
            float a = Mathf.Tau * i / Spikes;
            var dir = new Vector2(Mathf.Cos(a), Mathf.Sin(a));
            var side = new Vector2(-dir.Y, dir.X) * 0.16f;
            shapes[i] = new[] { dir * 1.0f, dir * 0.2f + side, dir * 0.2f - side };
        }
        return shapes;
    }
}
