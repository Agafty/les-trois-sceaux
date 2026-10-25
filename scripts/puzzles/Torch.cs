using System.Collections.Generic;
using Godot;

/// <summary>
/// Torche ou brasero (objet Tiled « Torche »). Obstacle d'une demi-case pour Brann.
/// - Allumée : la flèche la traverse et prend feu (<see cref="Arrow.Ignite"/>).
/// - Éteinte : arrête la flèche ; une flèche enflammée l'allume (<see cref="Light"/>) et disparaît, une normale disparaît.
/// - Permanente (brasero) : toujours allumée, ne s'éteint jamais, n'ouvre rien.
/// - <see cref="Duration"/> > 0 : une torche allumée s'éteint après ce nombre de secondes (multiplié par
///   <see cref="GameState.PuzzleTimeMultiplier"/>) ; sa flamme rétrécit pendant les 3 dernières secondes.
/// Toutes les torches de même <see cref="Target"/> allumées en même temps ouvrent la porte (<see cref="Door.OpenById"/>,
/// mémorisée) ; elles restent alors allumées. L'état des torches n'est pas sauvegardé.
/// Image : art/puzzles/torche.png (7 images : éteinte, 4 de flamme, 2 de flamme qui rétrécit) ou brasero.png (4 images).
/// </summary>
public partial class Torch : StaticBody2D, IArrowInteractor
{
    /// <summary>La torche vient de s'allumer ou de s'éteindre.</summary>
    [Signal]
    public delegate void LitChangedEventHandler(bool lit);

    [Export] public string Id { get; set; } = "";

    /// <summary>Id de la porte (type « interrupteur ») à ouvrir quand toutes les torches de même cible brûlent. Vide pour un brasero.</summary>
    [Export] public string Target { get; set; } = "";

    /// <summary>Allumée au chargement de la salle.</summary>
    [Export] public bool StartLit { get; set; }

    /// <summary>Brasero : toujours allumé.</summary>
    [Export] public bool Permanent { get; set; }

    /// <summary>Secondes d'allumage avant extinction. 0 = reste allumée.</summary>
    [Export(PropertyHint.Range, "0,120,0.5")] public float Duration { get; set; }

    public bool IsLit => _lit;

    public static readonly StringName GroupName = "torches";

    private const int FrameSize = 32;

    private Sprite2D _sprite;
    private GameState _state;
    private bool _lit;
    private bool _frozen; // résolue : reste allumée
    private float _remaining; // > 0 : compte à rebours en cours
    private float _animTime;
    private bool _hasFlame;
    private ulong _lastArrowId;
    private bool _lastArrowResult;

    public override void _Ready()
    {
        _state = GetNode<GameState>("/root/GameState");
        _sprite = GetNode<Sprite2D>("Sprite2D");
        AddToGroup(GroupName);
        SetupSprite();
        SetProcess(false);

        if (string.IsNullOrEmpty(Target) && !Permanent)
            GD.PushWarning($"Torche {Id} : aucune cible (propriété « cible ») et pas permanente.");

        bool solved = !Permanent && !string.IsNullOrEmpty(Target) && _state.IsCollected(Target);
        if (solved)
        {
            _frozen = true;
            SetLit(true, startTimer: false);
        }
        else if (Permanent)
        {
            SetLit(true, startTimer: false); // brasero : jamais de compte à rebours
        }
        else if (StartLit)
        {
            SetLit(true, startTimer: true);
            // Tout un groupe qui démarre allumé ouvrirait la porte tout de suite : on vérifie une fois la salle en place.
            if (!string.IsNullOrEmpty(Target))
                Callable.From(CheckGroupAtLoad).CallDeferred();
        }
        else
        {
            ApplyFrame();
        }
    }

    // Le corps et la zone élargie (TorchArrowZone) peuvent tous deux toucher la même flèche : on ne traite qu'une fois par flèche.
    public bool OnArrowTouch(Arrow arrow)
    {
        ulong id = arrow.GetInstanceId();
        if (id == _lastArrowId) return _lastArrowResult;
        _lastArrowId = id;
        _lastArrowResult = ComputeArrowTouch(arrow);
        return _lastArrowResult;
    }

    private bool ComputeArrowTouch(Arrow arrow)
    {
        if (_lit)
        {
            // Une flèche déjà enflammée « recharge » une torche chronométrée : sa minuterie repart de zéro (choix pour le jeune joueur).
            if (arrow.IsBurning && !_frozen && !Permanent && _remaining > 0f)
                _remaining = TorchRules.EffectiveDuration(Duration, _state.PuzzleTimeMultiplier);
            arrow.Ignite();
            return false; // la flèche traverse la flamme
        }
        if (arrow.IsBurning)
            Light();
        return true; // éteinte : la flèche disparaît (normale ou enflammée)
    }

    /// <summary>Allume la torche et démarre son compte à rebours ; si c'est la dernière de sa cible, la porte s'ouvre.</summary>
    public void Light()
    {
        if (_lit || _frozen) return;
        SetLit(true, startTimer: true);
        TryOpenTarget();
    }

    public override void _Process(double delta)
    {
        if (!_lit) return;
        _animTime += (float)delta;
        if (_remaining > 0f)
        {
            _remaining -= (float)delta;
            if (_remaining <= 0f)
            {
                _remaining = 0f;
                SetLit(false, startTimer: false);
                return;
            }
        }
        ApplyFrame();
    }

    private void SetLit(bool lit, bool startTimer)
    {
        bool changed = lit != _lit;
        _lit = lit;
        _remaining = 0f;
        if (lit && startTimer && !_frozen && !Permanent)
            _remaining = TorchRules.EffectiveDuration(Duration, _state.PuzzleTimeMultiplier);
        SetProcess(lit); // pas d'animation ni de compte à rebours sur une torche éteinte
        _animTime = 0f;
        ApplyFrame();
        if (changed) EmitSignal(SignalName.LitChanged, lit);
    }

    // Toutes les torches de même cible allumées ensemble : la porte s'ouvre, les torches restent allumées.
    private void CheckGroupAtLoad()
    {
        if (!IsInsideTree() || _frozen) return;
        if (TryOpenTarget())
            GD.PushWarning($"Torche {Id} : toutes les torches de « {Target} » démarrent allumées, la porte s'ouvre dès le chargement (revoir etat dans Tiled).");
    }

    /// <summary>Ouvre la porte si toutes les torches de même cible sont allumées. Renvoie vrai si c'est le cas.</summary>
    private bool TryOpenTarget()
    {
        if (string.IsNullOrEmpty(Target) || Permanent) return false;
        var group = new List<Torch>();
        foreach (var node in GetTree().GetNodesInGroup(GroupName)) // rare : à chaque allumage
        {
            if (node is not Torch other || other.Target != Target || other.Permanent) continue;
            if (!other.IsLit) return false;
            group.Add(other);
        }
        foreach (var torch in group) torch.Freeze();
        if (!Door.OpenById(GetTree(), _state, Target))
            GD.PushWarning($"Torche {Id} : aucune porte « {Target} » dans cette salle (groupe « portes »), ouverture mémorisée.");
        return true;
    }

    private void Freeze()
    {
        _frozen = true;
        _remaining = 0f;
        ApplyFrame();
    }

    private void ApplyFrame()
    {
        if (_sprite == null) return;
        if (!_hasFlame)
        {
            // Brasero : boucle de toutes les images.
            _sprite.Frame = _lit && _sprite.Hframes > 1 ? (int)(_animTime * 8f) % _sprite.Hframes : 0;
            return;
        }
        if (!_lit)
            _sprite.Frame = TorchRules.UnlitFrame;
        else if (TorchRules.IsShrinking(_remaining) && _sprite.Hframes > TorchRules.FirstShrinkFrame)
            _sprite.Frame = TorchRules.ShrinkFrame(_animTime);
        else
            _sprite.Frame = Mathf.Min(TorchRules.FlameFrame(_animTime), _sprite.Hframes - 1);
    }

    // brasero.png pour une torche permanente, torche.png sinon ; à défaut un carré de couleur (placeholder).
    private void SetupSprite()
    {
        string path = Permanent ? "res://art/puzzles/brasero.png" : "res://art/puzzles/torche.png";
        Texture2D texture = ResourceLoader.Exists(path) ? GD.Load<Texture2D>(path) : null;
        if (texture == null)
        {
            GD.PushWarning($"Torche {Id} : image {path} introuvable, placeholder utilisé.");
            var image = Image.CreateEmpty(FrameSize * 7, FrameSize, false, Image.Format.Rgba8);
            for (int f = 0; f < 7; f++)
                image.FillRect(new Rect2I(f * FrameSize + 8, 8, 16, 16), f == 0 ? new Color(0.3f, 0.25f, 0.3f) : new Color(1f, 0.6f, 0.15f));
            texture = ImageTexture.CreateFromImage(image);
        }
        _sprite.Texture = texture;
        _sprite.Hframes = Mathf.Max(1, texture.GetWidth() / FrameSize);
        _hasFlame = !Permanent;
        _sprite.Frame = 0;
    }
}
