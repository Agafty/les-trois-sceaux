using Godot;

/// <summary>
/// Objet d'histoire sans inventaire : pose un drapeau dans GameState (ex. « epee_bois », « epee_corvan ») ou ne fait rien de plus que
/// montrer son nom (le charbon : c'est l'id unique du ramassable qui est mémorisé). Sert aux objets de l'ouverture.
/// Tant que le graphiste n'a pas livré d'icône (<see cref="PickupEffect.Icon"/>), une petite vignette de couleur la remplace.
/// </summary>
[GlobalClass]
public partial class FlagEffect : PickupEffect
{
    /// <summary>Drapeau posé à l'obtention (vide : aucun).</summary>
    [Export] public string Flag { get; set; } = "";

    /// <summary>Couleur de la vignette de remplacement (16x16) quand il n'y a pas d'icône.</summary>
    [Export] public Color PlaceholderColor { get; set; } = new Color(0.25f, 0.25f, 0.28f);

    private Texture2D _placeholder;

    public override bool CanApply(Player player, GameState state) => true;

    public override void Apply(Player player, GameState state)
    {
        if (!string.IsNullOrEmpty(Flag)) state.MarkCollected(Flag);
    }

    public override Texture2D GetIcon() => Icon ?? (_placeholder ??= MakePlaceholder());

    private Texture2D MakePlaceholder()
    {
        var image = Image.CreateEmpty(16, 16, false, Image.Format.Rgba8);
        var dark = PlaceholderColor.Darkened(0.4f);
        var light = PlaceholderColor.Lightened(0.3f);
        for (int y = 3; y < 13; y++)
            for (int x = 3; x < 13; x++)
            {
                bool edge = x == 3 || x == 12 || y == 3 || y == 12;
                image.SetPixel(x, y, edge ? dark : (x + y < 14 ? light : PlaceholderColor));
            }
        return ImageTexture.CreateFromImage(image);
    }
}
