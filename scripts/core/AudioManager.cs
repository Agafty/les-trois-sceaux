using System.Collections.Generic;
using Godot;

/// <summary>
/// Autoload : bruitages et musique, sur deux bus séparés « Musique » et « SFX » (default_bus_layout.tres).
/// - <see cref="PlaySfx"/> joue un bruitage de audio/sfx/ (noms dans <see cref="Sfx"/>) avec un petit pool de lecteurs :
///   aucune allocation par appel, au plus <see cref="MaxPerSound"/> exemplaires du même son en même temps, un délai minimum
///   entre deux déclenchements du même son, et le lecteur le plus ancien est réutilisé si tout est occupé.
/// - Un son manquant ou inconnu ne plante jamais : un seul avertissement par nom.
/// - Les sons continuent pendant la pause (ProcessMode Always réglé dans la scène) : menus, coffre qui s'ouvre...
/// - Musique : pistes de audio/musique/ (noms dans <see cref="MusicRules"/>), piste de salle (<see cref="EnterRoom"/>), de boss,
///   jingles, musique d'une cinématique ; fondus de 0,5 s, jamais de redémarrage si c'est déjà la piste en cours.
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

    // État de la musique (voir EnterRoom, BeginBossMusic, PlayJingle, PlayScriptedMusic).
    private const string MusicFolder = "res://audio/musique/";
    private static readonly string[] MusicExtensions = { ".ogg", ".mp3", ".wav" }; // une composition .ogg l'emporte sur la piste générée
    private readonly Dictionary<string, AudioStream> _tracks = new();
    private readonly HashSet<string> _preloading = new();
    private string _currentTrack;   // piste qui joue (ou vient d'être lancée)
    private string _zoneTrack;      // fond de la salle courante
    private string _bossTrack;      // piste de combat, prioritaire sur la salle
    private string _scriptedTrack;  // piste imposée par une cinématique (null = silence voulu)
    private bool _scripted;
    private bool _keepScripted;     // la cinématique part par « aller_a » : sa musique survit à la prochaine salle seulement
    private int _jingleId;          // numéro du jingle en cours (le minuteur de secours d'un jingle périmé est ignoré)
    private bool _jingle;           // un jingle joue : la suite reprend à sa fin

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
        _music.Finished += OnMusicFinished;
        PreloadTracks();

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
        if (_music != null && IsInstanceValid(_music)) _music.Finished -= OnMusicFinished;
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

    // --- Pistes du jeu -----------------------------------------------------------------------------

    /// <summary>Chemin du fichier d'une piste (.ogg, puis .mp3, puis .wav), ou null s'il n'existe pas.</summary>
    public static string ResolveMusicPath(string track)
    {
        if (!MusicRules.IsValidName(track)) return null;
        foreach (var ext in MusicExtensions)
        {
            var path = MusicFolder + track.Trim() + ext;
            if (ResourceLoader.Exists(path)) return path;
        }
        return null;
    }

    // Chargement en tâche de fond au démarrage : changer de salle ne fige jamais le jeu pour lire un fichier.
    private void PreloadTracks()
    {
        foreach (var track in MusicRules.All)
        {
            var path = ResolveMusicPath(track);
            if (path != null && ResourceLoader.LoadThreadedRequest(path) == Error.Ok) _preloading.Add(track);
        }
    }

    private AudioStream LoadTrack(string track)
    {
        if (_tracks.TryGetValue(track, out var cached)) return cached;
        AudioStream stream = null;
        var path = ResolveMusicPath(track);
        if (path == null)
            WarnOnce("musique:" + track, $"AudioManager : piste « {track} » introuvable dans {MusicFolder} (relancer tools/audio/musique.py ?).");
        else
        {
            stream = (_preloading.Remove(track) ? ResourceLoader.LoadThreadedGet(path) : ResourceLoader.Load(path)) as AudioStream;
            if (stream == null) WarnOnce("musique:" + track, $"AudioManager : {path} n'a pas pu être chargé.");
        }
        _tracks[track] = stream;
        return stream;
    }

    /// <summary>Joue une piste par son nom, avec fondu. Sans effet si c'est déjà elle qui joue.</summary>
    private void PlayTrack(string track, float fadeSeconds)
    {
        if (string.IsNullOrEmpty(track)) return;
        if (track == _currentTrack && _music.Playing) return;
        var stream = LoadTrack(track);
        if (stream == null)
        {
            SilenceTrack(fadeSeconds); // piste absente : silence plutôt que l'ancienne piste qui ne correspond plus (avertissement déjà émis)
            return;
        }
        _currentTrack = track;
        PlayMusic(stream, fadeSeconds);
    }

    private void SilenceTrack(float fadeSeconds)
    {
        _currentTrack = null;
        StopMusic(fadeSeconds);
    }

    // Ce qui doit jouer maintenant, par ordre de priorité : combat, musique de cinématique, fond de la salle.
    private void ResumeMusic(float fadeSeconds)
    {
        if (_jingle) return;
        string wanted = _bossTrack ?? (_scripted ? _scriptedTrack : _zoneTrack);
        if (wanted == null) SilenceTrack(fadeSeconds);
        else PlayTrack(wanted, fadeSeconds);
    }

    /// <summary>
    /// Appelé par chaque Room à son chargement avec la piste de sa zone (<see cref="MusicRules.ForRoom"/>, null = pas d'avis).
    /// Si c'est déjà la piste en cours (changement de salle dans la même zone), elle continue sans coupure.
    /// </summary>
    public void EnterRoom(string track)
    {
        _bossTrack = null; // une salle qui se charge n'est jamais au milieu d'un combat
        // Une musique de cinématique ne survit qu'au changement de salle voulu par la cinématique (« aller_a ») ;
        // toute autre arrivée (sortie à pied, rechargement après une mort) revient à la musique de la zone.
        if (_scripted)
        {
            if (!_keepScripted) _scripted = false;
            _keepScripted = false;
        }
        if (track != null) _zoneTrack = track;
        ResumeMusic(0.5f);
    }

    /// <summary>Le combat d'un boss commence : sa piste remplace celle de la salle.</summary>
    public void BeginBossMusic(string track)
    {
        _bossTrack = string.IsNullOrEmpty(track) ? null : track;
        _scripted = false;
        _jingle = false;
        ResumeMusic(0.4f);
    }

    /// <summary>Le combat est fini (victoire ou mort) : la piste de combat n'est plus prioritaire. Le son qui suit est choisi par l'appelant (jingle).</summary>
    public void EndBossMusic() => _bossTrack = null;

    /// <summary>
    /// Joue un jingle (non bouclé) tout de suite ; à sa fin, la musique de la salle reprend. Le flux est forcé sans boucle, et un minuteur
    /// de secours rend la main si le signal de fin n'arrive pas : la musique ne reste jamais muette.
    /// </summary>
    public void PlayJingle(string track)
    {
        if (!MusicRules.IsJingle(track))
        {
            WarnOnce("jingle:" + track, $"AudioManager : « {track} » n'est pas un jingle (MusicRules.IsJingle).");
            return;
        }
        var stream = LoadTrack(track);
        if (stream == null) return;
        switch (stream)
        {
            case AudioStreamWav wav: wav.LoopMode = AudioStreamWav.LoopModeEnum.Disabled; break;
            case AudioStreamOggVorbis ogg: ogg.Loop = false; break;
            case AudioStreamMP3 mp3: mp3.Loop = false; break;
        }
        _musicTween?.Kill();
        _jingle = true;
        int id = ++_jingleId;
        _currentTrack = track;
        _musicStream = stream;
        _music.Stream = stream;
        _music.VolumeDb = 0f;
        _music.Play();
        double length = stream.GetLength();
        GetTree().CreateTimer((length > 0 ? length : 8.0) + 0.5, true, false, true).Timeout += () => EndJingle(id);
    }

    private void EndJingle(int id)
    {
        if (!_jingle || id != _jingleId) return;
        _jingle = false;
        _currentTrack = null;
        ResumeMusic(0.5f);
    }

    /// <summary>Coupe la musique (fondu) jusqu'au prochain changement de salle ; utile quand une cinématique enchaîne.</summary>
    public void SilenceMusic(float fadeSeconds = 1f)
    {
        _jingle = false;
        SilenceTrack(fadeSeconds);
    }

    /// <summary>
    /// Écran qui impose sa piste (titre, générique) : tout le reste est oublié, la piste démarre (ou continue si c'est déjà elle).
    /// </summary>
    public void PlayScreenTrack(string track)
    {
        _bossTrack = null;
        _scripted = false;
        _jingle = false;
        _zoneTrack = track;
        PlayTrack(track, 0.5f);
    }

    /// <summary>
    /// À appeler juste avant qu'une cinématique parte par « aller_a » : la musique qu'elle a posée (piste ou silence) continue dans la salle
    /// d'arrivée, jusqu'à ce qu'une autre cinématique la remplace ou pose « zone ». Sans effet si la cinématique n'a posé aucune musique.
    /// </summary>
    public void KeepScriptedMusicForNextRoom(bool keep = true) => _keepScripted = keep && _scripted;

    /// <summary>
    /// Action « musique » des cinématiques : une piste, « stop » (silence) ou « zone » (retour à la musique de la salle).
    /// Elle ne dure que dans la salle courante, sauf départ par « aller_a » (<see cref="KeepScriptedMusicForNextRoom"/>).
    /// </summary>
    public void PlayScriptedMusic(string track, float fadeSeconds)
    {
        _jingle = false;
        if (track == "zone")
        {
            _scripted = false;
            ResumeMusic(fadeSeconds);
            return;
        }
        _scripted = true;
        _keepScripted = false;
        _scriptedTrack = track == "stop" ? null : track;
        ResumeMusic(fadeSeconds);
    }

    private void OnMusicFinished()
    {
        if (_jingle) EndJingle(_jingleId);
        else if (_currentTrack != null && _musicStream != null)
        {
            _music.Play(); // filet de sécurité : une piste importée sans boucle recommence au lieu de se taire
        }
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
