using Godot;

/// <summary>
/// Zone d'interaction de la torche pour les flèches, plus grande que son corps physique (tir plus tolérant pour un jeune joueur).
/// Brann ne la sent pas (aucun corps physique) ; la flèche la détecte comme une Area2D et la transmet à la <see cref="Torch"/>.
/// </summary>
public partial class TorchArrowZone : Area2D, IArrowInteractor
{
    private Torch _torch;

    public override void _Ready() => _torch = GetParent<Torch>();

    public bool OnArrowTouch(Arrow arrow) => _torch.OnArrowTouch(arrow);
}
