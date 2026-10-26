using Godot;

/// <summary>
/// Brume d'un rectangle Tiled « Brume » : un voile semi-transparent dessiné par-dessus le décor (comme le calque « Dessus »).
/// Elle ne bloque rien (aucun corps). Sa densité (0 à 1) vient de la propriété « densite » de l'objet et de l'étape de l'histoire ;
/// elle respire doucement (opacité et dérive lentes) grâce à un Tween en boucle.
/// </summary>
public partial class BrumeZone : Node2D
{
    /// <summary>Taille du rectangle (px).</summary>
    public Vector2 AreaSize { get; set; } = new(32f, 32f);

    /// <summary>Densité de 0 (rien) à 1 (opaque).</summary>
    public float Density { get; set; } = 0.5f;

    /// <summary>Opacité maximale du voile quand la densité vaut 1.</summary>
    [Export(PropertyHint.Range, "0.1,1,0.05")] public float MaxOpacity { get; set; } = 0.75f;

    /// <summary>Durée (s) d'un cycle de respiration.</summary>
    [Export(PropertyHint.Range, "1,20,0.5")] public float BreathSeconds { get; set; } = 5f;

    private static readonly Color MistColor = new(0.82f, 0.86f, 0.93f);

    public override void _Ready()
    {
        // Deux nappes de la même couleur, décalées, qui respirent en contretemps : l'ensemble paraît mouvant sans texture.
        var baseOpacity = Density * MaxOpacity;
        for (int i = 0; i < 2; i++)
        {
            var veil = new ColorRect
            {
                Name = "Nappe" + i,
                Color = new Color(MistColor, baseOpacity * (i == 0 ? 0.65f : 0.5f)),
                Size = AreaSize,
                Position = -AreaSize * 0.5f,
                MouseFilter = Control.MouseFilterEnum.Ignore,
            };
            AddChild(veil);

            // La nappe 1 commence par monter quand la nappe 0 descend : elles respirent en contretemps.
            float low = i == 0 ? 0.7f : 0.35f;
            float first = i == 0 ? low : 1f;
            float second = i == 0 ? 1f : low;
            var breath = veil.CreateTween().SetLoops();
            breath.TweenProperty(veil, "modulate:a", first, BreathSeconds * 0.5f).SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.InOut);
            breath.TweenProperty(veil, "modulate:a", second, BreathSeconds * 0.5f).SetTrans(Tween.TransitionType.Sine).SetEase(Tween.EaseType.InOut);
        }
    }
}
