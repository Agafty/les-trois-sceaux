using System.Collections.Generic;
using Godot;

/// <summary>
/// Base commune des boss. La <see cref="Room"/> instancie la scène du boss à l'emplacement du rectangle Tiled « boss_&lt;nom&gt; »,
/// lui donne le contexte de l'arène (piliers, portes, identifiant) puis écoute ses signaux pour la barre de vie du HUD,
/// la réplique de fin et les récompenses. Le boss ne connaît ni le HUD ni la salle : il signale vers le haut.
/// </summary>
public abstract partial class Boss : CharacterBody2D
{
    /// <summary>Le combat commence (la porte de l'arène se referme) : le HUD montre la barre de vie.</summary>
    [Signal]
    public delegate void EncounterStartedEventHandler();

    /// <summary>Progression du combat : 1 = boss en pleine forme, 0 = vaincu.</summary>
    [Signal]
    public delegate void ProgressChangedEventHandler(float fraction);

    /// <summary>Le combat est fini (victoire ou mort de Brann) : le HUD cache la barre. Émis une seule fois.</summary>
    [Signal]
    public delegate void EncounterEndedEventHandler();

    /// <summary>Le boss est purifié : la porte est rouverte, l'état est mémorisé ; la salle montre la réplique et les récompenses.</summary>
    [Signal]
    public delegate void DefeatedEventHandler();

    /// <summary>Le boss veut afficher un conseil bref au joueur (clé de traduction, durée en secondes), sans pause.</summary>
    [Signal]
    public delegate void HintRequestedEventHandler(string textKey, float seconds);

    /// <summary>Clé de traduction du nom affiché au-dessus de la barre de vie et devant la réplique.</summary>
    [Export] public string NameKey { get; set; } = "";

    /// <summary>Clé de traduction de la réplique prononcée à la libération.</summary>
    [Export] public string FarewellKey { get; set; } = "";

    /// <summary>Nom (sans extension) du ramassable de progression de resources/pickups/ : le sceau du donjon.</summary>
    [Export] public string SealPickupName { get; set; } = "";

    /// <summary>Un réceptacle de cœur apparaît à la victoire.</summary>
    [Export] public bool DropsHeartContainer { get; set; } = true;

    /// <summary>Identifiant mémorisé dans GameState à la victoire (réglé par la Room : « &lt;zone&gt;_boss_&lt;nom&gt; »).</summary>
    public string BossId { get; set; } = "";

    /// <summary>Piliers de l'arène (rectangles « pilier » de la carte, en coordonnées monde), réglés par la Room.</summary>
    public IReadOnlyList<Rect2> Pillars { get; set; } = System.Array.Empty<Rect2>();

    /// <summary>Portes de la salle, refermées pendant le combat (réglé par la Room).</summary>
    public IReadOnlyList<Door> ArenaDoors { get; set; } = System.Array.Empty<Door>();

    /// <summary>Point d'arrivée de Brann dans la salle (son Spawn d'entrée), réglé par la Room : le combat commence quand il s'en éloigne.</summary>
    public Vector2? EntryPoint { get; set; }

    /// <summary>Limites de l'arène (monde), réglées par la Room d'après la carte ; vide = valeur par défaut du boss.</summary>
    public Rect2 ArenaBounds { get; set; }
}
