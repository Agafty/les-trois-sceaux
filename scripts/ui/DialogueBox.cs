using System.Collections.Generic;
using Godot;

/// <summary>
/// Boîte de dialogue en bas de l'écran (cadre sombre, nom du personnage dans un onglet au-dessus).
/// - Le texte défile lettre par lettre (<see cref="CharsPerSecond"/>) avec un petit bruit de voix ; « interact » (seulement : comme
///   <see cref="InteractionZone"/>, « attack » ne fait rien ici, c'est le coup d'épée de Brann) affiche d'un coup la fin de la réplique,
///   puis passe à la suivante. Après la dernière : fermeture, ou choix Oui/Non s'il y en a.
/// - Deux usages :
///   * <see cref="OpenModal"/> (PNJ, boutique) : LE JEU EST MIS EN PAUSE (SceneTree.Paused) pendant la conversation. Brann, les ennemis
///     et les minuteries s'arrêtent, et le menu pause ne peut pas s'ouvrir par-dessus (il refuse quand le jeu est déjà en pause).
///     Si le jeu était déjà en pause (coffre qui s'ouvre), la boîte ne le relance pas à la fermeture.
///   * <see cref="Open"/> (réplique d'un boss) : pas de pause, une seule réplique qui se ferme seule après <see cref="AutoCloseSeconds"/>.
/// - Le signal <see cref="Finished"/> donne le choix fait (index) ou -1 s'il n'y a pas de choix.
/// - Les textes ne sont jamais en dur : <see cref="Open"/> prend des clés de traduction ; <see cref="OpenModal"/> prend des textes
///   DÉJÀ traduits par l'appelant (Tr(clé), éventuellement passé dans string.Format).
/// </summary>
public partial class DialogueBox : CanvasLayer
{
    private const string ScenePath = "res://scenes/ui/boite_dialogue.tscn";
    private const string ThemePath = "res://resources/ui/theme_jeu.tres";

    /// <summary>La conversation est terminée. choice = index du choix validé, -1 sans choix.</summary>
    [Signal]
    public delegate void FinishedEventHandler(int choice);

    /// <summary>Vitesse du défilement (lettres par seconde). Réglable dans la scène boite_dialogue.tscn.</summary>
    [Export(PropertyHint.Range, "5,200,1")] public float CharsPerSecond { get; set; } = 45f;

    /// <summary>Mode non modal : délai (s) après la fin du texte avant fermeture automatique (0 = jamais).</summary>
    [Export(PropertyHint.Range, "0,30,0.5")] public float AutoCloseSeconds { get; set; }

    /// <summary>Un lettre sur N fait « bip » (la voix du texte).</summary>
    [Export(PropertyHint.Range, "1,6,1")] public int BeepEvery { get; set; } = 2;

    /// <summary>Boîte non modale d'une réplique (clés de traduction), qui se ferme seule. Utilisée pour les boss.</summary>
    public static DialogueBox Open(Node owner, string speakerKey, string textKey, float maxSeconds = 8f)
    {
        var box = Create();
        box.AutoCloseSeconds = maxSeconds;
        owner.AddChild(box);
        box.Begin(string.IsNullOrEmpty(speakerKey) ? "" : box.Tr(speakerKey), new[] { box.Tr(textKey) }, null, false);
        return box;
    }

    /// <summary>
    /// Conversation modale (jeu en pause) : textes déjà traduits, choix facultatifs affichés après la dernière réplique.
    /// À attendre avec : var args = await ToSignal(box, DialogueBox.SignalName.Finished); int choice = (int)args[0];
    /// </summary>
    public static DialogueBox OpenModal(Node owner, string speakerName, IReadOnlyList<string> texts, IReadOnlyList<string> choices = null, int defaultChoice = 0)
    {
        var box = Create();
        box.DefaultChoice = defaultChoice;
        owner.AddChild(box);
        box.Begin(speakerName ?? "", texts, choices, true);
        return box;
    }

    private static DialogueBox Create()
    {
        var scene = GD.Load<PackedScene>(ScenePath);
        return scene != null ? scene.Instantiate<DialogueBox>() : new DialogueBox { Name = "BoiteDialogue", Layer = 6 };
    }

    /// <summary>Texte de la réplique en cours (en entier, même si le défilement n'est pas fini).</summary>
    public string Text => _label?.Text ?? "";

    public int LineIndex => _lineIndex;

    /// <summary>Vrai tant que la réplique en cours défile.</summary>
    public bool IsTyping => _typewriter != null && !_typewriter.IsComplete;

    public int VisibleCharacters => _typewriter?.Visible ?? 0;

    /// <summary>Choix surligné (0 = premier).</summary>
    public int SelectedChoice => _selected;

    public bool IsAskingChoice => _asking;

    private static readonly StringName ActionInteract = "interact";
    private static readonly StringName ActionLeft = "move_left";
    private static readonly StringName ActionRight = "move_right";
    private static readonly StringName ActionUp = "move_up";
    private static readonly StringName ActionDown = "move_down";
    private static readonly Color BackColor = new(0.1f, 0.08f, 0.13f, 0.92f);
    private static readonly Rect2 BoxRect = new(16f, 272f, 608f, 64f);
    private const float TabHeight = 16f;
    private const float InputDelay = 0.15f; // la touche qui a ouvert la boîte ne doit pas la fermer aussitôt
    private const float NonModalInputDelay = 1.2f; // réplique de boss : le joueur se bat, on évite qu'un appui réflexe la ferme

    private IReadOnlyList<string> _texts;
    private IReadOnlyList<string> _choices;
    private string _speaker = "";
    private bool _modal;

    /// <summary>Choix surligné au départ (index). Hors bornes : le premier. Pour un achat : « Non ».</summary>
    public int DefaultChoice { get; set; }
    private bool _pausedByBox;
    private bool _finished;
    private bool _asking;
    private int _lineIndex;
    private int _selected;
    private float _age;
    private float _completeAge;
    private bool _built;
    private TypewriterState _typewriter;
    private int _lastBeepVisible;

    private Label _label;
    private Label _choicesLabel;
    private ColorRect _choicesTab;
    private Polygon2D _arrow;

    private void Begin(string speaker, IReadOnlyList<string> texts, IReadOnlyList<string> choices, bool modal)
    {
        ProcessMode = ProcessModeEnum.Always; // continue de tourner quand le jeu est en pause
        _speaker = speaker;
        _texts = texts == null || texts.Count == 0 ? new[] { "" } : texts;
        _choices = choices != null && choices.Count > 0 ? choices : null;
        _modal = modal;
        BuildUi();
        if (modal && !GetTree().Paused)
        {
            GetTree().Paused = true;
            _pausedByBox = true;
        }
        ShowLine(0);
    }

    public override void _ExitTree()
    {
        // La salle est déchargée en pleine conversation : ne jamais laisser le jeu figé.
        if (_pausedByBox && GetTree() != null) GetTree().Paused = false;
        _pausedByBox = false;
    }

    private void BuildUi()
    {
        if (_built) return;
        _built = true;
        var theme = GD.Load<Theme>(ThemePath);

        AddChild(new ColorRect { Color = BackColor, Position = BoxRect.Position, Size = BoxRect.Size, MouseFilter = Control.MouseFilterEnum.Ignore });
        _label = new Label
        {
            Position = BoxRect.Position + new Vector2(8f, 6f),
            Size = BoxRect.Size - new Vector2(16f, 12f),
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            HorizontalAlignment = HorizontalAlignment.Left,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        if (theme != null) _label.Theme = theme;
        AddChild(_label);

        if (!string.IsNullOrEmpty(_speaker))
        {
            var nameLabel = new Label { Text = _speaker, MouseFilter = Control.MouseFilterEnum.Ignore };
            if (theme != null) nameLabel.Theme = theme;
            float width = nameLabel.GetCombinedMinimumSize().X + 16f;
            AddChild(new ColorRect
            {
                Color = BackColor,
                Position = new Vector2(BoxRect.Position.X, BoxRect.Position.Y - TabHeight),
                Size = new Vector2(width, TabHeight),
                MouseFilter = Control.MouseFilterEnum.Ignore,
            });
            nameLabel.Position = new Vector2(BoxRect.Position.X + 8f, BoxRect.Position.Y - TabHeight + 2f);
            AddChild(nameLabel);
        }

        if (_choices != null)
        {
            _choicesTab = new ColorRect
            {
                Color = BackColor,
                Position = new Vector2(BoxRect.End.X - 170f, BoxRect.Position.Y - TabHeight),
                Size = new Vector2(170f, TabHeight),
                MouseFilter = Control.MouseFilterEnum.Ignore,
                Visible = false,
            };
            _choicesLabel = new Label
            {
                Position = new Vector2(8f, 2f),
                Size = new Vector2(154f, 12f),
                HorizontalAlignment = HorizontalAlignment.Right,
                MouseFilter = Control.MouseFilterEnum.Ignore,
            };
            if (theme != null) _choicesLabel.Theme = theme;
            _choicesTab.AddChild(_choicesLabel);
            AddChild(_choicesTab);
        }

        // Petite flèche clignotante en bas à droite : « appuie pour continuer ».
        _arrow = new Polygon2D
        {
            Polygon = new[] { new Vector2(0, 0), new Vector2(8, 0), new Vector2(4, 5) },
            Color = new Color(0.95f, 0.9f, 0.7f),
            Position = new Vector2(BoxRect.End.X - 16f, BoxRect.End.Y - 10f),
            Visible = false,
        };
        AddChild(_arrow);
    }

    private void ShowLine(int index)
    {
        _lineIndex = index;
        _label.Text = _texts[index];
        _label.VisibleCharacters = 0;
        _typewriter = new TypewriterState(_label.Text.Length, CharsPerSecond);
        _lastBeepVisible = 0;
        _completeAge = 0f;
        _arrow.Visible = false;
        if (_choicesTab != null) _choicesTab.Visible = false;
        _asking = false;
        if (_typewriter.IsComplete) OnLineComplete(); // texte vide
    }

    public override void _Process(double delta)
    {
        if (_finished || _typewriter == null) return;
        float dt = (float)delta;
        _age += dt;

        if (IsTyping)
        {
            int revealed = _typewriter.Update(dt);
            if (revealed > 0)
            {
                _label.VisibleCharacters = _typewriter.Visible;
                PlayVoice();
            }
            if (_typewriter.IsComplete) OnLineComplete();
        }
        else
        {
            _completeAge += dt;
            // Clignotement de la flèche (sans allocation).
            _arrow.Visible = !_asking && ((int)(_completeAge * 3f) & 1) == 0;
            if (!_modal && AutoCloseSeconds > 0f && _completeAge >= AutoCloseSeconds)
            {
                Finish(-1);
                return;
            }
        }

        if (_age < (_modal ? InputDelay : NonModalInputDelay)) return;
        if (_asking)
        {
            if (Input.IsActionJustPressed(ActionLeft) || Input.IsActionJustPressed(ActionUp)) MoveSelection(-1);
            else if (Input.IsActionJustPressed(ActionRight) || Input.IsActionJustPressed(ActionDown)) MoveSelection(1);
        }
        if (Input.IsActionJustPressed(ActionInteract))
            Confirm();
    }

    // Une lettre sur BeepEvery fait « bip » ; les espaces et la ponctuation restent muets.
    private void PlayVoice()
    {
        int visible = _typewriter.Visible;
        if (visible - _lastBeepVisible < BeepEvery) return;
        _lastBeepVisible = visible;
        if (visible > 0 && visible <= _label.Text.Length && char.IsLetterOrDigit(_label.Text[visible - 1]))
            AudioManager.Play(Sfx.Texte);
    }

    private void OnLineComplete()
    {
        _label.VisibleCharacters = -1;
        bool last = _lineIndex >= _texts.Count - 1;
        if (last && _choices != null)
        {
            _asking = true;
            _selected = DefaultChoice >= 0 && DefaultChoice < _choices.Count ? DefaultChoice : 0;
            _choicesTab.Visible = true;
            RefreshChoices();
        }
    }

    /// <summary>Touche de validation : affiche la fin de la réplique, passe à la suivante, valide le choix ou ferme.</summary>
    public void Confirm()
    {
        if (_finished || _typewriter == null) return;
        if (IsTyping)
        {
            _typewriter.Skip();
            OnLineComplete();
            return;
        }
        if (_asking)
        {
            AudioManager.Play(Sfx.MenuValide);
            Finish(_selected);
            return;
        }
        if (_lineIndex < _texts.Count - 1)
            ShowLine(_lineIndex + 1);
        else
            Finish(-1);
    }

    /// <summary>Déplace le choix surligné (-1 / +1, sans boucler).</summary>
    public void MoveSelection(int step)
    {
        if (!_asking) return;
        int next = Mathf.Clamp(_selected + step, 0, _choices.Count - 1);
        if (next == _selected) return;
        _selected = next;
        AudioManager.Play(Sfx.MenuDeplace);
        RefreshChoices();
    }

    private void RefreshChoices()
    {
        var sb = new System.Text.StringBuilder(); // appelé seulement quand le choix change
        for (int i = 0; i < _choices.Count; i++)
        {
            if (i > 0) sb.Append("   ");
            sb.Append(i == _selected ? "> " : "  ").Append(_choices[i]);
        }
        _choicesLabel.Text = sb.ToString();
    }

    private void Finish(int choice)
    {
        if (_finished) return;
        _finished = true;
        if (_pausedByBox)
        {
            GetTree().Paused = false;
            _pausedByBox = false;
        }
        EmitSignal(SignalName.Finished, choice);
        QueueFree();
    }
}
