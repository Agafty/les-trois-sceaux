using Godot;

/// <summary>
/// Zone posée par <see cref="TileFeatures"/> sur la case d'un buisson (tuile du calque « Murs »). Quand l'épée de Brann la touche
/// (<see cref="IMeleeTarget"/>), la zone demande à <see cref="TileFeatures"/> de couper le buisson. Les flèches et les bombes l'ignorent.
/// Principe Godot : la HitBox de l'épée (Area2D, masque 1) prévient les Area2D de la couche 1 qui implémentent IMeleeTarget.
/// </summary>
public partial class BushCutter : Area2D, IMeleeTarget
{
    /// <summary>Le buisson a été touché : la case (coordonnées dans le calque) doit être coupée.</summary>
    [Signal]
    public delegate void CutRequestedEventHandler(Vector2I cell);

    /// <summary>Case du buisson dans le calque « Murs ».</summary>
    public Vector2I Cell { get; set; }

    private bool _requested;

    public void OnMeleeHit(Vector2 position)
    {
        if (_requested) return; // un seul coup compte, même si l'épée touche plusieurs images de suite
        _requested = true;
        EmitSignal(SignalName.CutRequested, Cell);
    }
}
