using System.Collections.Generic;
using Godot;

/// <summary>
/// Surveille les déclencheurs de cinématique d'une salle (classe Tiled « Scenario » ou scenarios.json) et lance la première dont
/// les conditions sont vraies : drapeaux requis posés, drapeaux interdits absents, drapeau de fin de la cinématique absent, et
/// (si le déclencheur a une zone) le centre de Brann dedans. Les conditions sont revérifiées 10 fois par seconde tant que la salle vit,
/// donc une cinématique peut partir « quand le deuxième charbon est ramassé ». Une cinématique part au plus une fois par chargement de salle
/// (même sans drapeau de fin) et seulement quand Brann est libre : ni en pause, ni en transition, ni en train d'attaquer ou d'être touché.
/// </summary>
public partial class ScenarioWatcher : Node
{
    private const float CheckInterval = 0.1f;
    private const float StartDelay = 0.3f;

    private CinematicPlayer _player;
    private Player _brann;
    private GameState _state;
    private System.Func<string, bool> _isSet; // GameState.IsCollected, mémorisé (pas de délégué créé à chaque vérification)
    private SceneManager _sceneManager;
    private List<ScenarioDef> _defs;
    private readonly HashSet<string> _fired = new();
    private float _timer = StartDelay;

    public void Setup(CinematicPlayer cinematics, Player brann, List<ScenarioDef> defs)
    {
        _player = cinematics;
        _brann = brann;
        _defs = defs;
        _state = GetNode<GameState>("/root/GameState");
        _isSet = _state.IsCollected;
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
    }

    public override void _PhysicsProcess(double delta)
    {
        _timer -= (float)delta;
        if (_timer > 0f) return;
        _timer = CheckInterval;
        if (_defs == null || _player == null || _player.IsPlaying) return;
        if (_sceneManager.IsTransitioning || GetTree().Paused) return;
        if (!IsInstanceValid(_brann) || !_brann.CanInteract) return;

        for (int i = 0; i < _defs.Count; i++)
        {
            var def = _defs[i];
            if (_fired.Contains(def.Cinematic)) continue;
            var data = CinematicLibrary.Get(def.Cinematic);
            if (data == null)
            {
                _fired.Add(def.Cinematic); // déjà signalé : on n'insiste pas
                continue;
            }
            if (!ScenarioRules.Matches(def, data.EndFlag, _isSet)) continue;
            if (def.HasZone && !def.ZoneContains(_brann.GlobalPosition.X, _brann.GlobalPosition.Y)) continue;

            _fired.Add(def.Cinematic);
            _ = _player.Play(data);
            return; // une seule à la fois ; la suivante est examinée quand celle-ci est finie
        }
    }
}
