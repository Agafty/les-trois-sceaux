/// <summary>
/// Réglages du joueur, écrits dans user://options.json (séparé des sauvegardes : ils valent pour toutes les parties).
/// Classe C# pure (sans Godot). Les valeurs sont toujours ramenées à des valeurs permises par <see cref="OptionsRules.Normalize"/>.
/// </summary>
public class OptionsData
{
    /// <summary>Version du format du fichier d'options. À incrémenter si le format change.</summary>
    public const int CurrentVersion = 1;

    public int Version { get; set; } = CurrentVersion;

    /// <summary>Volume de la musique, 0 à 100 par pas de 10.</summary>
    public int MusicVolume { get; set; } = 100;

    /// <summary>Volume des bruitages, 0 à 100 par pas de 10.</summary>
    public int SfxVolume { get; set; } = 100;

    public bool Fullscreen { get; set; }

    /// <summary>Échelle de la fenêtre : 0 = automatique (la plus grande qui tient dans l'écran), 1 à 4 = ×1 à ×4.</summary>
    public int WindowScale { get; set; }

    /// <summary>Aide au jeune joueur : durées des énigmes chronométrées. 1 = normal, 2 = doublées, 0 = sans limite.</summary>
    public int PuzzleTimeMultiplier { get; set; } = 1;

    /// <summary>Langue : « fr » ou « en ».</summary>
    public string Language { get; set; } = "fr";
}
