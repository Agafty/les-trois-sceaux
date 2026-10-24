using System.Collections.Generic;
using Godot;

/// <summary>
/// Boîte de texte unique d'une salle, partagée par toutes ses <see cref="HintZone"/> : la dernière zone entrée garde la main,
/// et la boîte ne se cache que lorsque Brann n'est plus dans aucune zone. Créée par la <see cref="Room"/>.
/// </summary>
public partial class HintBox : Node
{
    /// <summary>Texte actuellement affiché (vide si la boîte est cachée).</summary>
    public string Text => IsShown ? _label.Text : "";

    /// <summary>Vrai tant que la boîte est visible.</summary>
    public bool IsShown => _layer != null && _layer.Visible;

    private const string ThemePath = "res://resources/ui/theme_jeu.tres";
    private static bool _themeWarned;
    private static readonly Color BackColor = new(0.1f, 0.08f, 0.13f, 0.9f);
    private static readonly Rect2 BoxRect = new(16f, 272f, 608f, 64f);

    private readonly List<HintZone> _occupied = new(); // la dernière est celle qui s'affiche
    private CanvasLayer _layer;
    private Label _label;

    /// <summary>Brann entre dans la zone : son texte passe au premier plan.</summary>
    public void Enter(HintZone zone)
    {
        _occupied.Remove(zone);
        _occupied.Add(zone);
        Refresh();
    }

    /// <summary>Brann sort de la zone : le texte de la zone occupée précédente revient, ou la boîte se cache.</summary>
    public void Leave(HintZone zone)
    {
        _occupied.Remove(zone);
        Refresh();
    }

    private void Refresh()
    {
        if (_occupied.Count == 0)
        {
            if (_layer != null) _layer.Visible = false;
            return;
        }
        if (_layer == null) Build();
        var current = _occupied[^1];
        string text = Tr(current.TextKey);
        if (text == current.TextKey)
            GD.PushWarning($"Indice « {current.TextKey} » : pas de traduction dans textes.csv.");
        _label.Text = text;
        _layer.Visible = true;
    }

    // Fond sombre + texte qui passe à la ligne, dans un CanvasLayer au-dessus du HUD (5) et sous le fondu (10).
    private void Build()
    {
        _layer = new CanvasLayer { Layer = 6, Visible = false };
        var back = new ColorRect { Color = BackColor, Position = BoxRect.Position, Size = BoxRect.Size, MouseFilter = Control.MouseFilterEnum.Ignore };
        _label = new Label
        {
            Position = BoxRect.Position + new Vector2(8f, 6f),
            Size = BoxRect.Size - new Vector2(16f, 12f),
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            HorizontalAlignment = HorizontalAlignment.Left,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        var theme = GD.Load<Theme>(ThemePath);
        if (theme != null)
            _label.Theme = theme;
        else if (!_themeWarned)
        {
            _themeWarned = true;
            GD.PushWarning($"Thème introuvable : {ThemePath} (police par défaut utilisée pour les indices).");
        }
        _layer.AddChild(back);
        _layer.AddChild(_label);
        AddChild(_layer);
    }
}
