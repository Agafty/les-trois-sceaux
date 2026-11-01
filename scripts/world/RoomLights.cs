using Godot;

/// <summary>Fabrique de lumières 2D sans image : texture radiale générée par code, créée une seule fois.</summary>
public static class RoomLights
{
    private const int TextureSize = 256;
    private static GradientTexture2D _radial;

    /// <summary>Texture radiale (blanc au centre, transparent au bord) ; sa moitié (128 px) vaut un rayon de 128 px à l'échelle 1.</summary>
    public static Texture2D Radial
    {
        get
        {
            if (_radial != null && GodotObject.IsInstanceValid(_radial)) return _radial;
            var gradient = new Gradient();
            gradient.Offsets = new float[] { 0f, 0.35f, 1f };
            gradient.Colors = new[] { new Color(1, 1, 1, 1), new Color(1, 1, 1, 0.65f), new Color(1, 1, 1, 0) };
            _radial = new GradientTexture2D
            {
                Gradient = gradient,
                Fill = GradientTexture2D.FillEnum.Radial,
                FillFrom = new Vector2(0.5f, 0.5f),
                FillTo = new Vector2(1f, 0.5f),
                Width = TextureSize,
                Height = TextureSize,
            };
            return _radial;
        }
    }

    /// <summary>Crée une lumière ronde de ce rayon (px). Elle n'est visible que dans une salle assombrie (teinte).</summary>
    public static PointLight2D Create(float radius, Color color, float energy)
    {
        return new PointLight2D
        {
            Texture = Radial,
            TextureScale = radius / (TextureSize * 0.5f),
            Color = color,
            Energy = energy,
        };
    }
}
