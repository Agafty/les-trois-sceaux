using Godot;

/// <summary>
/// Comportement d'un objet utilisé avec use_item (bombe posée, flèche tirée...).
/// La scène référencée par ItemData.UseScene a un script qui hérite de cette classe :
/// le Player l'instancie, la place, puis appelle Begin(). Chaque objet = une scène + un script, sans toucher au Player.
/// </summary>
public abstract partial class ItemUse : Node2D
{
    /// <summary>Appelé juste après l'ajout à la salle. direction = direction du regard (vecteur unité).</summary>
    public abstract void Begin(Player user, Vector2 direction);
}
