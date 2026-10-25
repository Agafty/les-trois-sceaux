using Godot;

/// <summary>
/// Bandeau « Vous obtenez : ... » montré quelques secondes quand Brann ramasse un objet au sol qui n'est pas courant
/// (voir <see cref="PickupEffect.ShowNameOnPickup"/>). Le jeu n'est pas mis en pause par le bandeau. C'est un CanvasLayer (couche 6, comme
/// les indices) enfant du joueur : un seul bandeau par joueur, réutilisé si on ramasse deux objets de suite.
/// </summary>
public partial class PickupBanner : CanvasLayer
{
    /// <summary>Texte affiché (nom, puis éventuellement une ligne d'explication).</summary>
    public string Text => _label?.Text ?? "";

    public bool IsShown => Visible;

    private const string NodeName = "PickupBanner";
    private const string ThemePath = "res://resources/ui/theme_jeu.tres";
    private const float BottomY = 268f;
    private const double ShowSeconds = 2.5;
    private static readonly Color BackColor = new(0.1f, 0.08f, 0.13f, 0.9f);

    private ColorRect _back;
    private Label _label;
    private Tween _tween;
    private Theme _theme;

    /// <summary>Annonce l'effet ramassé sous le joueur donné (crée le bandeau au besoin).</summary>
    public static void Announce(Node owner, PickupEffect effect)
    {
        string nameKey = effect.GetNameKey();
        if (string.IsNullOrEmpty(nameKey)) return;
        var banner = owner.GetNodeOrNull<PickupBanner>(NodeName);
        if (banner == null)
        {
            banner = new PickupBanner { Name = NodeName, Layer = 6, Visible = false };
            owner.AddChild(banner);
        }
        banner.ShowText(effect, nameKey);
    }

    private void ShowText(PickupEffect effect, string nameKey)
    {
        if (_label == null) Build();
        string text = string.Format(Tr("CHEST_OBTAIN"), Tr(nameKey));
        bool hasDescription = !string.IsNullOrEmpty(effect.DescriptionKey);
        if (hasDescription) text += "\n" + Tr(effect.DescriptionKey);
        _label.Text = text;
        float height = hasDescription ? 64f : 28f;
        _back.Position = new Vector2(16f, BottomY - height); // juste au-dessus de la boîte d'indice (16,272,608,64) : pas de chevauchement
        _back.Size = new Vector2(608f, height);
        _label.Position = _back.Position + new Vector2(8f, 4f);
        _label.Size = _back.Size - new Vector2(16f, 8f);
        Visible = true;
        _tween?.Kill();
        _tween = CreateTween(); // le Tween suit le temps du jeu : si le jeu est mis en pause, le bandeau attend aussi (pas de pause forcée)
        _tween.TweenInterval(ShowSeconds);
        _tween.TweenCallback(Callable.From(HideBanner));
    }

    /// <summary>Cache le bandeau tout de suite (mort de Brann).</summary>
    public void HideBanner()
    {
        _tween?.Kill();
        Visible = false;
    }

    private void Build()
    {
        _back = new ColorRect { Color = BackColor, MouseFilter = Control.MouseFilterEnum.Ignore };
        _label = new Label
        {
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            HorizontalAlignment = HorizontalAlignment.Left,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        _theme = GD.Load<Theme>(ThemePath);
        if (_theme != null) _label.Theme = _theme;
        AddChild(_back);
        AddChild(_label);
    }
}
