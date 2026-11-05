using System.Collections.Generic;
using Godot;

/// <summary>
/// Générique de fin : texte qui défile vers le haut sur un fond étoilé, puis écran « Fin », puis retour à l'écran titre.
/// Atteint par l'étape « aller_a » de la cinématique <c>village_fete</c>. La partie a DÉJÀ été sauvegardée au village (drapeaux
/// <c>fete_vue</c> et <c>jeu_termine</c>) : ce n'est pas une <see cref="Room"/>, donc rien n'est sauvegardé ici, et « Continuer » reprend au village.
///
/// Commandes : maintenir valider / attaquer / interagir / bas = accélérer ; maintenir « pause » 1 s (Échap / Start) = passer.
/// Lecture à voix haute (option du joueur) : chaque section est lue une fois, quand elle franchit la ligne de lecture.
/// Textes : clés GENERIQUE_* de textes.csv, via Tr(). Images facultatives (ignorées si absentes) : art/ui/generique_logo.png, art/ui/generique_fin.png.
/// </summary>
public partial class CreditsScreen : Control
{
    /// <summary>Scène atteinte à la fin (écran titre).</summary>
    [Export(PropertyHint.File, "*.tscn")] public string ReturnScene { get; set; } = "res://scenes/ui/ecran_titre.tscn";

    private const string ThemePath = "res://resources/ui/theme_jeu.tres";
    private const string LogoPath = "res://art/ui/generique_logo.png";
    private const string EndImagePath = "res://art/ui/generique_fin.png";
    private const string EndFlag = "jeu_termine";
    private const float ScreenHeight = 360f;
    private const float ScreenWidth = 640f;
    private const float LineHeight = 18f;
    private const float SectionGap = 44f;
    private const float EndFadeSeconds = 1.5f;
    private const float EndInputDelay = 2f;

    private static readonly StringName ActionSkip = "pause";
    private static readonly StringName[] SpeedActions = { "ui_accept", "attack", "interact", "move_down" };

    // Clé du titre de section, clé des noms.
    private static readonly (string Heading, string Names)[] Sections =
    {
        ("GENERIQUE_UN_JEU_DE", "GENERIQUE_NOM_AUTEUR"),
        ("GENERIQUE_PROGRAMMATION", "GENERIQUE_NOM_PROGRAMMATION"),
        ("GENERIQUE_GRAPHISMES", "GENERIQUE_NOM_GRAPHISMES"),
        ("GENERIQUE_SONS", "GENERIQUE_NOM_SONS"),
        ("GENERIQUE_LEVEL_DESIGN", "GENERIQUE_NOM_LEVEL_DESIGN"),
        ("GENERIQUE_TEXTES", "GENERIQUE_NOM_TEXTES"),
        ("GENERIQUE_TESTS", "GENERIQUE_NOM_TESTS"),
        ("GENERIQUE_REMERCIEMENTS", "GENERIQUE_NOM_REMERCIEMENTS"),
    };

    private SceneManager _sceneManager;
    private GameState _state;
    private Control _content;
    private Control _endScreen;
    private readonly List<float> _tops = new();
    private readonly List<string> _spoken = new();
    private float _contentHeight;
    private float _offset;
    private float _maxOffset;
    private int _lastRead = -1;
    private float _skipHold;
    private ColorRect _skipBar;
    private ColorRect _skipBarBack;
    private bool _atEnd;
    private float _endAge;
    private bool _leaving;
    private bool _leaveStarted; // MarkCollected et TextReader.Stop une seule fois
    private bool _released; // toutes les touches ont été relâchées au moins une fois depuis l'ouverture

    public override void _Ready()
    {
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        _state = GetNode<GameState>("/root/GameState");
        var theme = GD.Load<Theme>(ThemePath);
        if (theme != null) Theme = theme;
        Engine.TimeScale = 1f;
        AudioManager.Instance?.PlayScreenTrack(MusicRules.Credits); // continue sans coupure si la fête jouait déjà ce thème

        var back = new ColorRect { Color = new Color(0.03f, 0.03f, 0.09f), MouseFilter = MouseFilterEnum.Ignore };
        back.SetAnchorsPreset(LayoutPreset.FullRect);
        AddChild(back);
        AddStars();

        BuildContent();
        BuildEndScreen();
        BuildHint();
        _maxOffset = CreditsRules.EndOffset(ScreenHeight, _contentHeight);
        _content.Position = new Vector2(0f, ScreenHeight);
    }

    // Quelques étoiles fixes (graine fixe : toujours le même ciel).
    private void AddStars()
    {
        var rng = new RandomNumberGenerator { Seed = 1051 };
        for (int i = 0; i < 48; i++)
        {
            float size = rng.Randf() < 0.2f ? 2f : 1f;
            AddChild(new ColorRect
            {
                Color = new Color(1f, 0.96f, 0.8f, 0.25f + rng.Randf() * 0.5f),
                Position = new Vector2(rng.RandfRange(0f, ScreenWidth), rng.RandfRange(0f, ScreenHeight)),
                Size = new Vector2(size, size),
                MouseFilter = MouseFilterEnum.Ignore,
            });
        }
    }

    private void BuildContent()
    {
        _content = new Control { Name = "Contenu", MouseFilter = MouseFilterEnum.Ignore };
        AddChild(_content);
        float y = 0f;

        if (ResourceLoader.Exists(LogoPath))
        {
            var logo = GD.Load<Texture2D>(LogoPath);
            _content.AddChild(new TextureRect { Texture = logo, Position = new Vector2((ScreenWidth - logo.GetWidth()) / 2f, y), MouseFilter = MouseFilterEnum.Ignore });
            y += logo.GetHeight() + 16f;
        }
        string title = Tr("GENERIQUE_TITRE");
        _tops.Add(y);
        _spoken.Add(title);
        AddLine(title, y, new Color(1f, 0.85f, 0.45f), 2f);
        y += LineHeight * 2f + SectionGap;

        string previousNames = "";
        foreach (var (headingKey, namesKey) in Sections)
        {
            string heading = Tr(headingKey);
            string names = Tr(namesKey);
            _tops.Add(y);
            _spoken.Add(names == previousNames ? heading : heading + ". " + names);
            previousNames = names;
            AddLine(heading, y, new Color(0.95f, 0.8f, 0.45f), 1f);
            y += LineHeight + 4f;
            AddLine(names, y, Colors.White, 1f);
            y += LineHeight + SectionGap;
        }
        _contentHeight = y;
    }

    private void AddLine(string text, float y, Color color, float scale)
    {
        _content.AddChild(new Label
        {
            Text = text,
            Position = new Vector2(0f, y),
            Size = new Vector2(ScreenWidth, LineHeight),
            HorizontalAlignment = HorizontalAlignment.Center,
            Modulate = color,
            MouseFilter = MouseFilterEnum.Ignore,
            PivotOffset = new Vector2(ScreenWidth / 2f, 0f),
            Scale = new Vector2(scale, scale),
        });
    }

    private void BuildEndScreen()
    {
        _endScreen = new Control { Name = "EcranFin", Visible = false, MouseFilter = MouseFilterEnum.Ignore };
        _endScreen.SetAnchorsPreset(LayoutPreset.FullRect);
        AddChild(_endScreen);
        float y = 150f;
        if (ResourceLoader.Exists(EndImagePath))
        {
            var tex = GD.Load<Texture2D>(EndImagePath);
            _endScreen.AddChild(new TextureRect { Texture = tex, Position = new Vector2((ScreenWidth - tex.GetWidth()) / 2f, 100f), MouseFilter = MouseFilterEnum.Ignore });
            y = 100f + tex.GetHeight() + 12f;
        }
        _endScreen.AddChild(new Label
        {
            Text = Tr("GENERIQUE_FIN"),
            Position = new Vector2(0f, y),
            Size = new Vector2(ScreenWidth, LineHeight),
            HorizontalAlignment = HorizontalAlignment.Center,
            Modulate = new Color(1f, 0.85f, 0.45f),
            MouseFilter = MouseFilterEnum.Ignore,
        });
    }

    private void BuildHint()
    {
        AddChild(new Label
        {
            Text = Tr("GENERIQUE_SKIP"),
            Position = new Vector2(8f, 340f),
            Size = new Vector2(624f, 16f),
            HorizontalAlignment = HorizontalAlignment.Right,
            Modulate = new Color(1f, 1f, 1f, 0.4f),
            MouseFilter = MouseFilterEnum.Ignore,
        });
        _skipBarBack = new ColorRect { Color = new Color(0f, 0f, 0f, 0.5f), Position = new Vector2(512f, 330f), Size = new Vector2(120f, 4f), Visible = false, MouseFilter = MouseFilterEnum.Ignore };
        _skipBar = new ColorRect { Color = new Color(0.95f, 0.9f, 0.7f), Position = new Vector2(512f, 330f), Size = new Vector2(0f, 4f), Visible = false, MouseFilter = MouseFilterEnum.Ignore };
        AddChild(_skipBarBack);
        AddChild(_skipBar);
    }

    public override void _Process(double delta)
    {
        float dt = (float)delta;
        if (_leaving)
        {
            Leave(); // un fondu précédent était peut-être encore en cours : on réessaie
            return;
        }
        if (!_released) _released = !IsAnyHeld();
        UpdateSkip(dt);
        if (_leaving) return;

        if (!_atEnd)
        {
            bool fast = _released && IsAccelerating();
            _offset = CreditsRules.Advance(_offset, dt, fast, _maxOffset);
            _content.Position = new Vector2(0f, Mathf.Round(ScreenHeight - _offset));
            ReadNewSection();
            if (_offset >= _maxOffset) ShowEnd();
        }
        else
        {
            _endAge += dt;
            _endScreen.Modulate = new Color(1f, 1f, 1f, Mathf.Clamp(_endAge / EndFadeSeconds, 0f, 1f));
            if (_endAge >= CreditsRules.EndHoldSeconds) Leave();
        }
    }

    // Maintenir « pause » une seconde passe tout le générique (un appui bref ne fait rien : pas de sortie par accident).
    private void UpdateSkip(float dt)
    {
        if (_released && Input.IsActionPressed(ActionSkip)) _skipHold += dt;
        else _skipHold = Mathf.Max(0f, _skipHold - dt * 2f);
        bool holding = _skipHold > 0.02f;
        _skipBar.Visible = _skipBarBack.Visible = holding;
        if (holding) _skipBar.Size = new Vector2(120f * Mathf.Clamp(_skipHold / CreditsRules.SkipHoldSeconds, 0f, 1f), 4f);
        if (_skipHold >= CreditsRules.SkipHoldSeconds) Leave();
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        // Sur l'écran « Fin », une touche (après un court délai) revient au titre.
        if (!_atEnd || _leaving || _endAge < EndInputDelay) return;
        if (!@event.IsPressed() || @event.IsEcho()) return;
        if (@event is InputEventKey or InputEventJoypadButton or InputEventMouseButton)
        {
            Leave();
            GetViewport().SetInputAsHandled();
        }
    }

    private bool IsAccelerating()
    {
        for (int i = 0; i < SpeedActions.Length; i++)
            if (Input.IsActionPressed(SpeedActions[i])) return true;
        return false;
    }

    private bool IsAnyHeld() => IsAccelerating() || Input.IsActionPressed(ActionSkip);

    private void ReadNewSection()
    {
        int index = CreditsRules.SectionToRead(_tops, _offset, ScreenHeight);
        if (index <= _lastRead) return;
        _lastRead = index;
        TextReader.Speak(_spoken[index], TextSource.Dialogue);
    }

    private void ShowEnd()
    {
        _atEnd = true;
        _endAge = 0f;
        _content.Visible = false;
        _endScreen.Visible = true;
        _endScreen.Modulate = new Color(1f, 1f, 1f, 0f);
        TextReader.Speak(Tr("GENERIQUE_FIN"), TextSource.Dialogue);
    }

    private void Leave()
    {
        _leaving = true;
        if (!_leaveStarted)
        {
            _leaveStarted = true;
            _state.MarkCollected(EndFlag); // déjà posé par la cinématique ; sans effet s'il l'est
            TextReader.Stop();
        }
        if (!ResourceLoader.Exists(ReturnScene))
        {
            GD.PushError($"Générique : scène de retour introuvable « {ReturnScene} ».");
            SetProcess(false);
            return;
        }
        _sceneManager.ResetSpawnId();
        if (_sceneManager.GoToScene(ReturnScene)) SetProcess(false);
    }
}
