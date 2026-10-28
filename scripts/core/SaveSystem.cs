using System;
using System.IO;
using Godot;

/// <summary>
/// Autoload : lecture et écriture des sauvegardes (3 emplacements, user://save1.json à save3.json).
/// Le format est dans <see cref="SaveData"/> / <see cref="SaveSerializer"/> ; l'état vient de <see cref="GameState"/>.
/// </summary>
public partial class SaveSystem : Node
{
    public const int SlotCount = 3;

    [Signal]
    public delegate void GameSavedEventHandler(int slot);

    /// <summary>Une sauvegarde automatique vient de réussir (pas la statue ni F10) : le HUD affiche alors la petite icône de corbeau.</summary>
    [Signal]
    public delegate void AutoSavedEventHandler(int slot);

    private GameState _state;
    private SceneManager _sceneManager;

    /// <summary>Emplacement de la partie en cours (1 à 3). 0 = aucun : la sauvegarde automatique est alors désactivée.</summary>
    public int CurrentSlot { get; private set; }

    /// <summary>Temps de jeu cumulé de la partie en cours, en secondes.</summary>
    public double PlayTimeSeconds { get; private set; }

    public override void _Ready()
    {
        _state = GetNode<GameState>("/root/GameState");
        _sceneManager = GetNode<SceneManager>("/root/SceneManager");
        _state.ImportantChestOpened += OnImportantChestOpened;
        _state.BossDefeated += OnBossDefeated;
        _state.SealRestored += OnSealRestored;
        _sceneManager.TransitionFinished += OnTransitionFinished;
        // La salle de départ (lancée sans transition) donne la zone initiale ; on attend que l'arbre soit prêt.
        Callable.From(InitZone).CallDeferred();
    }

    // Zone de la dernière salle vue. null = inconnue (juste après un chargement ou une nouvelle partie).
    private string _lastZone;
    // Vrai quand la prochaine arrivée en salle ne doit pas sauvegarder (après un Load ou une nouvelle partie).
    private bool _skipNextZoneSave;
    private bool _warnedEmptyZone;
    // Nouvelle partie : une sauvegarde normale est faite à la fin de la transition vers la salle de départ.
    private bool _newGameSavePending;

    private void InitZone()
    {
        if (_lastZone == null && GetTree().CurrentScene is Room room)
            _lastZone = room.Zone ?? "";
    }

    public override void _ExitTree()
    {
        if (_state != null)
        {
            _state.ImportantChestOpened -= OnImportantChestOpened;
            _state.BossDefeated -= OnBossDefeated;
            _state.SealRestored -= OnSealRestored;
        }
        if (_sceneManager != null) _sceneManager.TransitionFinished -= OnTransitionFinished;
    }

    public override void _Process(double delta)
    {
        PlayTimeSeconds += delta; // un autoload ne tourne pas quand l'arbre est en pause : le temps de menu n'est pas compté
    }

    public static bool IsValidSlot(int slot) => slot >= 1 && slot <= SlotCount;

    private static string SlotFilePath(int slot) => $"user://save{slot}.json";

    // user:// est un chemin virtuel Godot ; GlobalizePath le convertit en vrai chemin disque pour System.IO.
    private static string RealPath(int slot) => ProjectSettings.GlobalizePath(SlotFilePath(slot));

    public bool HasSave(int slot) => IsValidSlot(slot) && File.Exists(RealPath(slot));

    public bool Delete(int slot)
    {
        if (!IsValidSlot(slot)) return false;
        try
        {
            if (File.Exists(RealPath(slot))) File.Delete(RealPath(slot));
            if (File.Exists(RealPath(slot) + ".tmp")) File.Delete(RealPath(slot) + ".tmp");
            if (CurrentSlot == slot) CurrentSlot = 0;
            return true;
        }
        catch (Exception e)
        {
            GD.PushError($"Suppression de la sauvegarde {slot} impossible : {e.Message}");
            return false;
        }
    }

    /// <summary>Remet l'état à zéro pour une nouvelle partie dans cet emplacement (sans lancer de scène : l'écran titre s'en chargera).</summary>
    public bool StartNewGame(int slot)
    {
        if (!IsValidSlot(slot)) return false;
        _state.ResetState();
        PlayTimeSeconds = 0;
        // Le point d'entrée (LastSpawnId) n'est PAS remis à zéro ici : l'appelant vient de le régler par GoToScene(scène, spawn, ...) avant ce rappel.
        _lastZone = null;
        _skipNextZoneSave = true;
        _newGameSavePending = true; // écrit l'emplacement dès l'arrivée dans la salle de départ
        CurrentSlot = slot;
        return true;
    }

    /// <summary>
    /// Écrit l'état dans l'emplacement. Refusé pendant une transition de salle et hors d'une salle (Room).
    /// Le slot devient l'emplacement courant.
    /// </summary>
    public bool Save(int slot)
    {
        if (!IsValidSlot(slot))
        {
            GD.PushError($"Emplacement de sauvegarde invalide : {slot}");
            return false;
        }
        if (_sceneManager.IsTransitioning) return false;

        var scene = GetTree().CurrentScene;
        if (scene is not Room || string.IsNullOrEmpty(scene.SceneFilePath))
            return false; // menu, écran titre... : pas de position de reprise valable

        try
        {
            var data = _state.CreateSaveData();
            data.Version = SaveData.CurrentVersion;
            data.SavedAtUtc = DateTime.UtcNow;
            data.PlayTimeSeconds = PlayTimeSeconds;
            data.ScenePath = scene.SceneFilePath;
            data.SpawnId = _sceneManager.LastSpawnId; // dernier Spawn d'entrée de la salle

            if (!WriteAtomic(RealPath(slot), SaveSerializer.Serialize(data)))
                return false;
        }
        catch (Exception e)
        {
            GD.PushError($"Sauvegarde {slot} échouée : {e.Message}");
            return false;
        }

        CurrentSlot = slot;
        EmitSignal(SignalName.GameSaved, slot);
        return true;
    }

    // Chemin de salle accepté : une scène .tscn/.scn sous scenes/ ou maps/, chargeable en PackedScene.
    private static bool IsValidScenePath(string path)
    {
        if (string.IsNullOrEmpty(path)) return false;
        if (!path.StartsWith("res://scenes/") && !path.StartsWith("res://maps/")) return false;
        if (path.Contains("..")) return false;
        if (!path.EndsWith(".tscn") && !path.EndsWith(".scn")) return false;
        return ResourceLoader.Exists(path) && ResourceLoader.Load(path) is PackedScene;
    }

    /// <summary>
    /// Lit l'emplacement, puis va à la salle et au Spawn sauvegardés. L'état n'est appliqué à GameState qu'une fois
    /// l'écran noir (juste avant le changement de scène), pour que l'ancienne salle ne puisse pas l'écraser.
    /// Tout est validé avant : en cas de problème, l'état courant n'est pas touché.
    /// </summary>
    public bool Load(int slot)
    {
        if (!IsValidSlot(slot) || _sceneManager.IsTransitioning) return false;
        _newGameSavePending = false; // un chargement annule toute sauvegarde de « nouvelle partie » en attente
        if (!TryRead(slot, out var data, true)) return false;

        if (!IsValidScenePath(data.ScenePath))
        {
            GD.PushError($"Sauvegarde {slot} : salle invalide « {data.ScenePath} ».");
            return false;
        }

        return _sceneManager.GoToScene(data.ScenePath, data.SpawnId, () =>
        {
            try
            {
                _state.ApplySaveData(data);
            }
            catch (Exception e)
            {
                GD.PushError($"Sauvegarde {slot} : application de l'état échouée : {e.Message}");
                throw; // SceneManager annule le changement de salle
            }
            PlayTimeSeconds = Math.Max(0, data.PlayTimeSeconds);
            CurrentSlot = slot;
            _lastZone = null; // la zone de la salle chargée sera apprise à son arrivée, sans sauvegarde
            _skipNextZoneSave = true;
        });
    }

    /// <summary>
    /// Lit le contenu d'un emplacement sans rien modifier (ni GameState, ni emplacement courant) : sert à l'écran titre
    /// pour afficher le résumé. Faux si l'emplacement est vide OU illisible (utiliser <see cref="HasSave"/> pour les distinguer).
    /// </summary>
    public bool TryPeek(int slot, out SaveData data)
    {
        data = null;
        return IsValidSlot(slot) && TryRead(slot, out data, false); // simple aperçu : un fichier illisible n'est qu'un avertissement
    }

    private bool TryRead(int slot, out SaveData data, bool logAsError)
    {
        data = null;
        string path = RealPath(slot);
        if (!File.Exists(path)) return false;
        try
        {
            string json = File.ReadAllText(path);
            if (SaveSerializer.TryDeserialize(json, out data, out string error))
                return true;
            LogReadProblem($"Sauvegarde {slot} illisible ({path}) : {error}", logAsError);
        }
        catch (Exception e)
        {
            LogReadProblem($"Lecture de la sauvegarde {slot} impossible : {e.Message}", logAsError);
        }
        return false;
    }

    private static void LogReadProblem(string message, bool asError)
    {
        if (asError) GD.PushError(message);
        else GD.PushWarning(message);
    }

    /// <summary>Annule la sauvegarde prévue à l'arrivée d'une nouvelle partie (le changement de salle a échoué).</summary>
    public void CancelNewGame() => _newGameSavePending = false;

    // Écriture atomique : on écrit dans « .tmp » puis on remplace le vrai fichier d'un seul coup.
    // Si le jeu plante pendant l'écriture, l'ancienne sauvegarde reste intacte.
    private static bool WriteAtomic(string path, string content)
    {
        string tmp = path + ".tmp";
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            using (var stream = new FileStream(tmp, FileMode.Create, System.IO.FileAccess.Write))
            using (var writer = new StreamWriter(stream))
            {
                writer.Write(content);
                writer.Flush();
                stream.Flush(true); // force l'écriture sur le disque avant le renommage
            }
            File.Move(tmp, path, true);
            return true;
        }
        catch (Exception e)
        {
            GD.PushError($"Écriture de la sauvegarde impossible ({path}) : {e.Message}");
            try { if (File.Exists(tmp)) File.Delete(tmp); } catch (Exception) { /* rien de plus à faire */ }
            return false;
        }
    }

    // --- Sauvegarde automatique -------------------------------------------------------------

    // Le signal peut arriver pendant le _ExitTree d'une salle : on attend la fin de l'image avant de toucher à l'arbre.
    // Les demandes d'une même image sont fusionnées par le drapeau ; une demande tombée pendant une transition
    // est abandonnée, car la fin de la transition en redemande une.
    private bool _autoSavePending;

    private void OnImportantChestOpened(string chestId) => RequestAutoSave();

    // Après un boss, et quand un sceau est restauré (ramassé) : sauvegarde automatique, comme pour un coffre important.
    private void OnBossDefeated(string bossId) => RequestAutoSave();

    private void OnSealRestored(string sealId) => RequestAutoSave();

    // Sauvegarde auto seulement quand la zone change (entrée dans un donjon, forêt -> village...).
    // Rien après un Load, une nouvelle partie ou une réapparition (la zone ne change pas).
    private void OnTransitionFinished(string scenePath, string spawnId)
    {
        if (_newGameSavePending)
        {
            _newGameSavePending = false;
            RequestAutoSave();
        }
        if (GetTree().CurrentScene is not Room room) return;
        string zone = room.Zone ?? "";
        if (zone.Length == 0)
        {
            if (!_warnedEmptyZone)
            {
                _warnedEmptyZone = true;
                GD.PushWarning($"Room sans Zone ({scenePath}) : pas de sauvegarde automatique pour cette salle.");
            }
            _lastZone = zone;
            return;
        }

        bool zoneChanged = _lastZone != null && _lastZone != zone;
        _lastZone = zone;
        if (_skipNextZoneSave)
        {
            _skipNextZoneSave = false;
            return;
        }
        if (zoneChanged)
            RequestAutoSave();
    }

    private void RequestAutoSave()
    {
        if (_autoSavePending) return;
        _autoSavePending = true;
        Callable.From(AutoSave).CallDeferred();
    }

    private void AutoSave()
    {
        _autoSavePending = false;
        if (_sceneManager.IsTransitioning)
            return; // TransitionFinished redemandera une sauvegarde à la fin de la transition
        if (CurrentSlot == 0) return;
        if (Save(CurrentSlot))
            EmitSignal(SignalName.AutoSaved, CurrentSlot);
    }

    // --- Raccourcis de test (build debug uniquement) -------------------------------------------

    public override void _UnhandledKeyInput(InputEvent @event)
    {
        if (!OS.IsDebugBuild()) return;
        if (@event is not InputEventKey { Pressed: true, Echo: false } key) return;

        if (key.Keycode == Key.F10)
            GD.Print(Save(1) ? "[DEBUG] Sauvegarde dans l'emplacement 1" : "[DEBUG] Sauvegarde refusée");
        else if (key.Keycode == Key.F11)
            GD.Print(Load(1) ? "[DEBUG] Chargement de l'emplacement 1" : "[DEBUG] Chargement impossible");
    }
}
