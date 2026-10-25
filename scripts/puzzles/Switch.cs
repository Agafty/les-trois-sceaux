using System.Collections.Generic;
using Godot;

/// <summary>
/// Interrupteur : une zone (Area2D) qui, activée, contribue à l'ouverture d'une porte.
/// - Mode Fleche : dans le groupe « cible_fleche », activé par une flèche (<see cref="IArrowTarget"/>) ; l'épée est sans effet.
/// - Mode Epee : activé par un coup d'épée (<see cref="IMeleeTarget"/>) ; les flèches l'ignorent. Sans symbole, c'est un levier.
/// Les interrupteurs de même <see cref="Target"/> forment un groupe (<see cref="SwitchGroup"/>) : la porte (groupe « portes »,
/// Id = Target) s'ouvre quand tous sont actifs ensemble. <see cref="Order"/> impose un ordre (hors ordre : tout le groupe revient
/// à zéro), <see cref="Duration"/> fait redevenir inactif un interrupteur touché au bout de N secondes (multipliées par
/// l'option d'aide <see cref="GameState.PuzzleTimeMultiplier"/>), <see cref="Symbol"/> choisit l'image de la cible.
/// Il a un corps solide (enfant « Corps », <see cref="SwitchBody"/>) : Brann et les blocs ne le traversent pas, l'épée et les flèches l'atteignent quand même.
/// Un interrupteur isolé, permanent et sans ordre garde le comportement d'origine : son Id est mémorisé dans GameState.
/// Sinon seul l'état de la porte est mémorisé : l'interrupteur repart de zéro quand la salle est rechargée
/// (et apparaît activé si sa porte est déjà ouverte).
/// </summary>
public partial class Switch : Area2D, IArrowTarget, IMeleeTarget
{
    /// <summary>L'interrupteur vient d'être activé (pas émis quand il est déjà activé au chargement de la salle).</summary>
    [Signal]
    public delegate void ActivatedEventHandler(string switchId);

    /// <summary>Identifiant unique, ex. "donjon1_interrupteur_01". Vide : l'état n'est pas mémorisé.</summary>
    [Export] public string Id { get; set; } = "";

    /// <summary>Id de la porte à ouvrir, ex. "donjon1_porte_03". Les interrupteurs de même cible forment un groupe.</summary>
    [Export] public string Target { get; set; } = "";

    [Export] public SwitchMode Mode { get; set; } = SwitchMode.Fleche;

    /// <summary>Rang dans la séquence à respecter (1, 2, 3...). 0 = pas d'ordre.</summary>
    [Export(PropertyHint.Range, "0,10,1")] public int Order { get; set; }

    /// <summary>Secondes pendant lesquelles l'interrupteur reste actif après un coup. 0 = permanent.</summary>
    [Export(PropertyHint.Range, "0,60,0.5")] public float Duration { get; set; }

    /// <summary>Symbole de la cible (gland, racine, feuille) : image art/puzzles/cible_&lt;symbole&gt;.png. Vide = image par défaut.</summary>
    [Export] public string Symbol { get; set; } = "";

    public bool IsActive => _active;

    /// <summary>Résolu pour de bon (porte ouverte) : plus de détection, les flèches passent ; le corps reste solide pour Brann.</summary>
    public bool IsFrozen => _frozen;

    /// <summary>Groupe Godot de tous les interrupteurs (sert à retrouver ses camarades de groupe).</summary>
    public static readonly StringName AllGroup = "interrupteurs";

    // Posés par le SwitchGroup.
    internal SwitchGroup Group { get; set; }
    internal int Index { get; set; }

    private const int FrameSize = 32;
    private const float ErrorDuration = 0.6f;
    private const float RingRadius = 19f;
    private const float BlinkBelowSeconds = 3f;
    private const int ChronoEmptyFrame = 4;
    private const int ChronoLastFullFrame = 3;
    private static readonly Color ErrorTint = new(1f, 0.35f, 0.3f);
    private static readonly Color RingColor = new(1f, 0.85f, 0.3f);
    private static readonly Color RingBlinkColor = new(1f, 1f, 1f);

    private Sprite2D _sprite;
    private GameState _state;
    private bool _active;
    private bool _frozen;
    private Color _baseModulate = Colors.White;
    private Tween _errorTween;
    private float _timerFraction;
    private bool _timerBlink;
    private bool _chrono; // cible chronométrée sans symbole : art/puzzles/cible_chrono.png (0 plein ... 3 à 25 %, 4 vide = inactive)

    public override void _Ready()
    {
        _state = GetNode<GameState>("/root/GameState");
        _sprite = GetNode<Sprite2D>("Sprite2D");
        _sprite.ShowBehindParent = true; // l'anneau du temps (dessiné par ce nœud) passe devant l'image

        if (string.IsNullOrEmpty(Id))
            GD.PushWarning($"Interrupteur sans Id ({GetPath()}) : son état ne sera pas mémorisé.");
        if (string.IsNullOrEmpty(Target))
            GD.PushWarning($"Interrupteur {Id} : aucune cible (propriété « cible »).");

        SetupSprite();
        AddToGroup(AllGroup);

        // Déjà résolu : porte ouverte (groupe terminé lors d'une visite précédente) ou ancien état mémorisé par Id.
        if (_state.IsCollected(Target) || _state.IsCollected(Id))
        {
            Freeze();
            return;
        }

        if (Mode == SwitchMode.Fleche)
            AddToGroup(Arrow.TargetGroup);
        // Tous les interrupteurs de la salle sont créés dans la même image : on forme les groupes juste après.
        Callable.From(JoinGroup).CallDeferred();
    }

    public void OnArrowHit(Vector2 position, Vector2 direction)
    {
        if (Mode == SwitchMode.Fleche) Activate();
    }

    public void OnMeleeHit(Vector2 position)
    {
        if (Mode == SwitchMode.Epee) Activate();
    }

    /// <summary>Un coup sur l'interrupteur (flèche ou épée selon le mode). Sans effet s'il est déjà activé ou résolu.</summary>
    public void Activate()
    {
        if (_frozen) return;
        if (Group == null) JoinGroup();
        Group?.Hit(this);
    }

    internal void EmitActivated() => EmitSignal(SignalName.Activated, Id);

    // Cherche les autres interrupteurs de même cible qui n'ont pas encore de groupe et les rassemble.
    private void JoinGroup()
    {
        if (Group != null || _frozen || !IsInsideTree()) return;

        var members = new List<Switch>();
        if (string.IsNullOrEmpty(Target))
            members.Add(this);
        else
            foreach (var node in GetTree().GetNodesInGroup(AllGroup)) // une fois par salle
                if (node is Switch other && other.Group == null && !other._frozen && other.Target == Target)
                    members.Add(other);
        if (members.Count == 0) members.Add(this);

        var group = new SwitchGroup { Name = "GroupeInterrupteurs" };
        group.Setup(members);
        GetParent().AddChild(group);
    }

    // --- Affichage, piloté par le SwitchGroup ----------------------------------------------------

    /// <summary>Montre l'interrupteur actif ou inactif (image) ; l'anneau du temps est effacé.</summary>
    internal void ShowActive(bool active)
    {
        _active = active;
        if (!active) ShowTimer(0f, 0f);
        ApplyFrame();
    }

    /// <summary>Anneau qui se vide : fraction 0 = pas d'anneau. Il clignote quand il reste peu de temps.</summary>
    internal void ShowTimer(float fraction, float remainingSeconds)
    {
        bool blink = fraction > 0f && remainingSeconds < BlinkBelowSeconds && ((int)(remainingSeconds * 6f) & 1) == 0;
        if (Mathf.IsEqualApprox(fraction, _timerFraction) && blink == _timerBlink) return;
        _timerFraction = fraction;
        _timerBlink = blink;
        if (_chrono)
            ApplyFrame(); // la jauge est dans l'image
        else
            QueueRedraw();
    }

    /// <summary>Retour visuel d'un mauvais ordre : image « erreur » (ou teinte rouge) un court instant.</summary>
    internal void FlashError()
    {
        _errorTween?.Kill();
        if (_sprite.Hframes == 3 && !_chrono)
            _sprite.Frame = 2;
        else
            _sprite.Modulate = ErrorTint;
        _errorTween = CreateTween();
        _errorTween.TweenInterval(ErrorDuration);
        _errorTween.TweenCallback(Callable.From(EndErrorFlash));
    }

    private void EndErrorFlash()
    {
        _sprite.Modulate = _baseModulate;
        ApplyFrame();
    }

    /// <summary>Résolu : actif pour de bon, plus de compte à rebours, plus de détection ; les flèches passent au travers (y compris du corps), mais le corps reste solide pour Brann.</summary>
    internal void Freeze()
    {
        _frozen = true;
        _active = true;
        ShowTimer(0f, 0f);
        ApplyFrame();
        RemoveFromGroup(Arrow.TargetGroup);
        SetDeferred(Area2D.PropertyName.Monitorable, false); // plus de détection
    }

    public override void _Draw()
    {
        if (_timerFraction <= 0f || _chrono) return;
        float start = -Mathf.Pi * 0.5f;
        DrawArc(Vector2.Zero, RingRadius, start, start + Mathf.Tau * _timerFraction, 32,
            _timerBlink ? RingBlinkColor : RingColor, 2f);
    }

    private void ApplyFrame()
    {
        if (_chrono)
        {
            if (!_active) _sprite.Frame = ChronoEmptyFrame;
            else if (_frozen || _timerFraction <= 0f) _sprite.Frame = 0;
            else _sprite.Frame = Mathf.Min(ChronoLastFullFrame, (int)((1f - _timerFraction) * 4f));
            return;
        }
        int activeFrame = _sprite.Hframes > 1 ? 1 : 0;
        _sprite.Frame = _active ? activeFrame : 0;
    }

    // Image : levier (épée sans symbole), cible_<symbole>, sinon interrupteur_<mode> ; à défaut celle de la flèche.
    // Une image de cible absente est remplacée par l'image de la flèche teintée selon le symbole (placeholder).
    private void SetupSprite()
    {
        string path;
        bool placeholder = false;
        bool hasSymbol = !string.IsNullOrEmpty(Symbol);
        if (hasSymbol && !RoomObjectCatalog.IsSafeName(Symbol))
        {
            GD.PushWarning($"Interrupteur {Id} : symbole invalide « {Symbol} », ignoré.");
            hasSymbol = false;
        }

        if (SwitchRules.IsLever(Mode, hasSymbol ? Symbol : ""))
            path = "res://art/puzzles/levier.png";
        else if (hasSymbol)
            path = $"res://art/puzzles/cible_{Symbol}.png";
        else if (Duration > 0f && ResourceLoader.Exists("res://art/puzzles/cible_chrono.png"))
        {
            path = "res://art/puzzles/cible_chrono.png";
            _chrono = true;
        }
        else
            path = $"res://art/puzzles/interrupteur_{SwitchRules.TextureName(Mode)}.png";

        if (!ResourceLoader.Exists(path))
        {
            placeholder = hasSymbol;
            path = "res://art/puzzles/interrupteur_fleche.png";
        }
        var texture = GD.Load<Texture2D>(path);
        if (texture == null)
        {
            GD.PushError($"Interrupteur {Id} : image introuvable ({path}).");
            return;
        }
        _sprite.Texture = texture;
        _sprite.Hframes = Mathf.Clamp(texture.GetWidth() / FrameSize, 1, 5);
        _sprite.Frame = _chrono ? ChronoEmptyFrame : 0;
        if (placeholder)
            _baseModulate = SymbolTint(Symbol);
        _sprite.Modulate = _baseModulate;
    }

    private static Color SymbolTint(string symbol) => symbol switch
    {
        "gland" => new Color(1f, 0.75f, 0.45f),
        "racine" => new Color(0.85f, 0.6f, 1f),
        "feuille" => new Color(0.55f, 1f, 0.55f),
        _ => Colors.White,
    };
}
