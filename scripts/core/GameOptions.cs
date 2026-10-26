using System;
using System.IO;
using Godot;

/// <summary>
/// Réglages du joueur (volumes, plein écran, échelle de fenêtre, aide, langue) : lecture, application et écriture de
/// user://options.json. Classe statique (et non un cinquième autoload) : elle n'a ni nœud ni signal, juste l'état
/// <see cref="Current"/> et les méthodes ci-dessous. Le format est dans <see cref="OptionsData"/> / <see cref="OptionsSerializer"/>.
/// <see cref="LoadAndApply"/> est appelée par GameState (le premier autoload) ; AudioManager lit ensuite <see cref="Current"/>
/// pour régler ses bus quand il est prêt. Fichier absent ou corrompu : valeurs par défaut, jamais d'exception.
/// </summary>
public static class GameOptions
{
    public const string FilePath = "user://options.json";

    /// <summary>Réglages en cours (jamais null).</summary>
    public static OptionsData Current { get; private set; } = new();

    private static string RealPath => ProjectSettings.GlobalizePath(FilePath);

    /// <summary>Lit le fichier d'options puis applique tout (langue, aide, affichage ; l'audio par AudioManager).</summary>
    public static void LoadAndApply()
    {
        Current = Load();
        ApplyLanguage();
        ApplyHelp();
        ApplyDisplay();
        ApplyAudio();
    }

    private static OptionsData Load()
    {
        try
        {
            string path = RealPath;
            if (!File.Exists(path)) return new OptionsData();
            if (OptionsSerializer.TryDeserialize(File.ReadAllText(path), out var data)) return data;
            GD.PushWarning("options.json illisible : valeurs par défaut.");
        }
        catch (Exception e)
        {
            GD.PushWarning($"options.json non lu ({e.Message}) : valeurs par défaut.");
        }
        return new OptionsData();
    }

    /// <summary>Écrit les options (fichier .tmp puis renommage, comme les sauvegardes). Faux en cas d'échec.</summary>
    public static bool Save()
    {
        string path = RealPath;
        string tmp = path + ".tmp";
        try
        {
            OptionsRules.Normalize(Current);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            using (var stream = new FileStream(tmp, FileMode.Create, System.IO.FileAccess.Write))
            using (var writer = new StreamWriter(stream))
            {
                writer.Write(OptionsSerializer.Serialize(Current));
                writer.Flush();
                stream.Flush(true);
            }
            File.Move(tmp, path, true);
            return true;
        }
        catch (Exception e)
        {
            GD.PushError($"Écriture de options.json impossible : {e.Message}");
            try { if (File.Exists(tmp)) File.Delete(tmp); } catch (Exception) { /* rien de plus à faire */ }
            return false;
        }
    }

    // --- Application (chaque méthode applique un réglage immédiatement) -----------------------------

    /// <summary>Règle les bus Musique et SFX. Sans AudioManager (pas encore prêt), il lira <see cref="Current"/> lui-même.</summary>
    public static void ApplyAudio()
    {
        var audio = AudioManager.Instance;
        if (audio == null) return;
        audio.SetMusicVolume(Current.MusicVolume / 100f);
        audio.SetSfxVolume(Current.SfxVolume / 100f);
    }

    public static void ApplyLanguage() => TranslationServer.SetLocale(Current.Language);

    public static void ApplyHelp()
    {
        if (Engine.GetMainLoop() is SceneTree tree && tree.Root.GetNodeOrNull<GameState>("GameState") is { } state)
            state.PuzzleTimeMultiplier = Current.PuzzleTimeMultiplier;
    }

    /// <summary>Plein écran, ou fenêtre à l'échelle choisie (centrée), sans jamais dépasser l'écran. Sans effet en headless.</summary>
    public static void ApplyDisplay()
    {
        if (DisplayServer.GetName() == "headless") return;
        if (Current.Fullscreen)
        {
            DisplayServer.WindowSetMode(DisplayServer.WindowMode.Fullscreen);
            return;
        }
        DisplayServer.WindowSetMode(DisplayServer.WindowMode.Windowed);
        var usable = DisplayServer.ScreenGetUsableRect(DisplayServer.WindowGetCurrentScreen());
        int scale = OptionsRules.EffectiveScale(Current.WindowScale, usable.Size.X, usable.Size.Y);
        var size = new Vector2I(OptionsRules.BaseWidth * scale, OptionsRules.BaseHeight * scale);
        DisplayServer.WindowSetSize(size);
        DisplayServer.WindowSetPosition(usable.Position + (usable.Size - size) / 2);
    }
}
