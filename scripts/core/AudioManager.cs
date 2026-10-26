using System.Collections.Generic;
using Godot;

/// <summary>
/// Autoload : bruitages et musique, sur deux bus séparés « Musique » et « SFX » (default_bus_layout.tres).
/// - <see cref="PlaySfx"/> joue un bruitage de audio/sfx/ (noms dans <see cref="Sfx"/>) avec un petit pool de lecteurs :
///   aucune allocation par appel, au plus <see cref="MaxPerSound"/> exemplaires du même son en même temps, un délai minimum
///   entre deux déclenchements du même son, et le lecteur le plus ancien est réutilisé si tout est occupé.
/// - Un son manquant ou inconnu ne plante jamais : un seul avertissement par nom.
/// - Les sons continuent pendant la pause (ProcessMode Always réglé dans la scène) : menus, coffre qui s'ouvre...
/// - <see cref="PlayMusic"/> / <see cref="StopMusic"/> sont prêts (aucune musique pour l'instant).
/// - Volumes par bus en valeur linéaire 0..1 (<see cref="SetSfxVolume"/>, <see cref="SetMusicVolume"/>), réglés par le menu options (GameOptions).
/// Le reste du code appelle les méthodes statiques <see cref="Play"/> / <see cref="PlayAt"/> : sans AudioManager (scène lancée
/// hors du jeu, test), elles ne font rien.
/// </summary>
public partial class AudioManager : Node
{
    public const string MusicBus = "Musique";
    public const string SfxBus = "SFX";
    private const string SfxFolder = "res://audio/sfx/";

    /// <summary>Nombre de lecteurs de bruitages (sons simultanés au total).</summary>
    private const int PoolSize = 12;

    /// <summary>Exemplaires simultanés maximum d'un même son.</summary>
    private const int MaxPerSound = 2;

    /// <summary>Délai minimum (ms) entre deux déclenchements d'un même son.</summary>
    private const ulong DefaultCooldownMs = 40;

    /// <summary>Distance (px) jusqu'à laquelle un son positionné est entendu à plein volume, puis il s'atténue sur la même distance.</summary>
    private const float FullVolumeRadius = 320f;

    /// <summary>Instance de l'autoload (null avant son _Ready ou hors du jeu complet).</summary>
    public static AudioManager Instance { get; private set; }

    /// <summary>Joue un bruitage (sans effet s'il n'y a pas d'AudioManager).</summary>
    public static void Play(StringName name) => Instance?.PlaySfx(name);

    /// <summary>Joue un bruitage situé dans le monde : plus faible s'il est loin du centre de l'écran.</summary>
    public static void PlayAt(StringName name, Vector2 worldPosition) => Instance?.PlaySfx(name, worldPosition);

    private readonly Dictionary<StringName, AudioStream> _streams = new();
    private readonly Dictionary<StringName, ulong> _lastPlayed = new();
    private readonly HashSet<StringName> _warned = new();
    private readonly Dictionary<StringName, ulong> _cooldowns = new()
    {
        // Sons qui peuvent être redéclenchés en continu par le jeu : on les espace.
        { Sfx.PorteVerrouillee, 900 },
        { Sfx.BlocPousse, 300 },
        { Sfx.MenuDeplace, 25 },
        { Sfx.Rubis, 60 },
    };

    private AudioStreamPlayer[] _pool;
    private StringName[] _poolSound;
    private ulong[] _poolStart;
    private AudioStreamPlayer _music;
    private Tween _musicTween;
    private AudioStream _musicStream;

    private SceneManager _sceneManager;
    private SaveSystem _saveSystem;

    public override void _Ready()
    {
        Instance = this;
        ProcessMode = ProcessModeEnum.Always; // déjà réglé dans la scène ; sécurité
        EnsureBuses();
        GameOptions.ApplyAudio(); // volumes choisis par le joueur (user://options.json), lus par GameState juste avant

        _pool = new AudioStreamPlayer[PoolSize];
        _poolSound = new StringName[PoolSize];
        _poolStart = new ulong[PoolSize];
        for (int i = 0; i < PoolSize; i++)
        {
            var player = new AudioStreamPlayer { Name = $"Sfx{i}", Bus = SfxBus };
            AddChild(player);
            _pool[i] = player;
        }
        _music = new AudioStreamPlayer { Name = "Musique", Bus = MusicBus };
        AddChild(_music);

        foreach (var name in Sfx.All)
        {
            var path = $"{SfxFolder}{name}.wav"; // au démarrage seulement
            if (!ResourceLoader.Exists(path))
            {
                WarnOnce(name, $"AudioManager : fichier {path} introuvable (relancer tools/audio/sfx.py ?).");
                continue;
            }
            var stream = GD.Load<AudioStream>(path);
            if (stream == null)
            {
                WarnOnce(name, $"AudioManager : {path} n'a pas pu être chargé.");
                continue;
            }
            _streams[name] = stream;
        }

        // Sons liés à des événements globaux (les autres sons sont déclenchés par les objets eux-mêmes).
        _sceneManager = GetNodeOrNull<SceneManager>("/root/SceneManager");
        if (_sceneManager != null) _sceneManager.TransitionStarted += OnTransitionStarted;
        _saveSystem = GetNodeOrNull<SaveSystem>("/root/SaveSystem");
        if (_saveSystem != null) _saveSystem.GameSaved += OnGameSaved;
    }

    public override void _ExitTree()
    {
        if (_sceneManager != null && IsInstanceValid(_sceneManager)) _sceneManager.TransitionStarted -= OnTransitionStarted;
        if (_saveSystem != null && IsInstanceValid(_saveSystem)) _saveSystem.GameSaved -= OnGameSaved;
        if (Instance == this) Instance = null;
    }

    // Le bruit de chute est joué par Brann lui-même au moment où il tombe (Player.BeginFall) : seul l'escalier passe ici.
    private void OnTransitionStarted(string kind)
    {
        if (kind == "escalier") PlaySfx(Sfx.Escalier);
    }

    private void OnGameSaved(int slot) => PlaySfx(Sfx.Sauvegarde);

    // --- Bruitages -------------------------------------------------------------------------------

    /// <summary>
    /// Joue un bruitage. <paramref name="position"/> (monde) l'atténue quand il est loin du centre de l'écran ; null = plein volume.
    /// </summary>
    public void PlaySfx(StringName name, Vector2? position = null)
    {
        if (_pool == null || name == null) return;
        if (!_streams.TryGetValue(name, out var stream))
        {
            WarnOnce(name, $"AudioManager : son inconnu ou non chargé « {name} ».");
            return;
        }

        ulong now = Time.GetTicksMsec();
        ulong cooldown = _cooldowns.TryGetValue(name, out var custom) ? custom : DefaultCooldownMs;
        if (_lastPlayed.TryGetValue(name, out var last) && now - last < cooldown) return;

        float gain = 1f;
        if (position.HasValue)
        {
            gain = DistanceGain(position.Value);
            if (gain <= 0.02f) return; // trop loin pour être entendu
        }

        // Limite de simultanéité par son + recherche d'un lecteur libre (ou du plus ancien).
        int sameCount = 0;
        int free = -1;
        int oldest = 0;
        for (int i = 0; i < PoolSize; i++)
        {
            if (!_pool[i].Playing)
            {
                if (free < 0) free = i;
                continue;
            }
            if (_poolSound[i] == name) sameCount++;
            if (_poolStart[i] < _poolStart[oldest]) oldest = i;
        }
        if (sameCount >= MaxPerSound) return;

        int slot = free >= 0 ? free : oldest;
        var player = _pool[slot];
        player.Stream = stream;
        player.VolumeDb = gain >= 0.999f ? 0f : Mathf.LinearToDb(gain);
        player.Play();
        _poolSound[slot] = name;
        _poolStart[slot] = now;
        _lastPlayed[name] = now;
    }

    /// <summary>Variante sans paramètre optionnel (appelable depuis un script GDScript ou un outil de test).</summary>
    public void PlaySfxAt(StringName name, Vector2 position) => PlaySfx(name, position);

    /// <summary>Joue un bruitage après <paramref name="seconds"/> secondes (même en pause). Pour enchaîner deux sons (coffre puis fanfare).</summary>
    public void PlaySfxDelayed(StringName name, float seconds, Vector2? position = null)
    {
        if (seconds <= 0f)
        {
            PlaySfx(name, position);
            return;
        }
        // Rare (quelques fois par partie) : l'allocation du minuteur et de la lambda est sans importance.
        GetTree().CreateTimer(seconds, true, false, true).Timeout += () => PlaySfx(name, position);
    }

    private float DistanceGain(Vector2 worldPosition)
    {
        var camera = GetViewport()?.GetCamera2D();
        if (camera == null) return 1f;
        float distance = camera.GetScreenCenterPosition().DistanceTo(worldPosition);
        return Mathf.Clamp(1f - (distance - FullVolumeRadius) / FullVolumeRadius, 0f, 1f);
    }

    private void WarnOnce(StringName name, string message)
    {
        if (_warned.Add(name)) GD.PushWarning(message);
    }

    // --- Musique ---------------------------------------------------------------------------------

    /// <summary>Lance une musique (en boucle si le flux est réglé en boucle à l'import), avec un fondu. Sans effet si c'est déjà elle.</summary>
    public void PlayMusic(AudioStream stream, float fadeSeconds = 0.5f)
    {
        if (stream == null)
        {
            StopMusic(fadeSeconds);
            return;
        }
        if (stream == _musicStream && _music.Playing) return;

        _musicTween?.Kill();
        _musicStream = stream;
        if (_music.Playing && fadeSeconds > 0f)
        {
            _musicTween = CreateTween();
            _musicTween.TweenProperty(_music, "volume_db", -60f, fadeSeconds * 0.5f);
            _musicTween.TweenCallback(Callable.From(() => StartMusicNow(fadeSeconds * 0.5f)));
        }
        else
        {
            StartMusicNow(fadeSeconds);
        }
    }

    /// <summary>Charge puis lance une musique par chemin (« res://audio/musique/titre.ogg »). Un fichier absent donne un avertissement, pas une erreur.</summary>
    public void PlayMusicFile(string path, float fadeSeconds = 0.5f)
    {
        if (!ResourceLoader.Exists(path))
        {
            WarnOnce(path, $"AudioManager : musique introuvable « {path} ».");
            return;
        }
        PlayMusic(GD.Load<AudioStream>(path), fadeSeconds);
    }

    private void StartMusicNow(float fadeSeconds)
    {
        _music.Stream = _musicStream;
        _music.VolumeDb = fadeSeconds > 0f ? -60f : 0f;
        _music.Play();
        if (fadeSeconds <= 0f) return;
        _musicTween = CreateTween();
        _musicTween.TweenProperty(_music, "volume_db", 0f, fadeSeconds);
    }

    /// <summary>Arrête la musique avec un fondu (0 = tout de suite).</summary>
    public void StopMusic(float fadeSeconds = 0.5f)
    {
        _musicTween?.Kill();
        _musicStream = null;
        if (!_music.Playing) return;
        if (fadeSeconds <= 0f)
        {
            _music.Stop();
            return;
        }
        _musicTween = CreateTween();
        _musicTween.TweenProperty(_music, "volume_db", -60f, fadeSeconds);
        _musicTween.TweenCallback(Callable.From(_music.Stop));
    }

    // --- Volumes (menu options) ------------------------------------------------------------------

    /// <summary>Volume des bruitages, de 0 (muet) à 1 (plein).</summary>
    public void SetSfxVolume(float linear) => SetBusVolume(SfxBus, linear);

    /// <summary>Volume de la musique, de 0 (muet) à 1 (plein).</summary>
    public void SetMusicVolume(float linear) => SetBusVolume(MusicBus, linear);

    public float GetSfxVolume() => GetBusVolume(SfxBus);

    public float GetMusicVolume() => GetBusVolume(MusicBus);

    public void SetBusVolume(string bus, float linear)
    {
        int index = AudioServer.GetBusIndex(bus);
        if (index < 0) return;
        linear = Mathf.Clamp(linear, 0f, 1f);
        AudioServer.SetBusMute(index, linear <= 0.0001f);
        AudioServer.SetBusVolumeDb(index, linear <= 0.0001f ? -80f : Mathf.LinearToDb(linear));
    }

    public float GetBusVolume(string bus)
    {
        int index = AudioServer.GetBusIndex(bus);
        if (index < 0 || AudioServer.IsBusMute(index)) return 0f;
        return Mathf.DbToLinear(AudioServer.GetBusVolumeDb(index));
    }

    // Filet de sécurité : si default_bus_layout.tres n'est pas chargé, on crée les deux bus.
    private static void EnsureBuses()
    {
        foreach (var bus in new[] { MusicBus, SfxBus })
        {
            if (AudioServer.GetBusIndex(bus) >= 0) continue;
            GD.PushWarning($"AudioManager : le bus « {bus} » n'existe pas (default_bus_layout.tres ?), création à la volée.");
            AudioServer.AddBus();
            int index = AudioServer.BusCount - 1;
            AudioServer.SetBusName(index, bus);
            AudioServer.SetBusSend(index, "Master");
        }
    }
}
