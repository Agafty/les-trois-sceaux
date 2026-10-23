using Godot;

/// <summary>
/// Pickup dont le sprite affiche l'icône de l'ItemData donné par son GiveItemEffect.
/// Hérite de Pickup (même détection, même sauvegarde par UniqueId).
/// </summary>
public partial class ItemPickup : Pickup
{
    public override void _Ready()
    {
        // Avant base._Ready() : le Pickup récupère le sprite et le fait rebondir.
        if (string.IsNullOrEmpty(UniqueId))
            GD.PushWarning($"{Name} ({SceneFilePath}) : UniqueId vide, l'objet réapparaîtra à chaque chargement de la salle.");
        var sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
        var icon = (Effect as GiveItemEffect)?.Item?.Icon;
        if (icon != null)
        {
            var frames = new SpriteFrames(); // contient déjà l'animation "default"
            frames.AddFrame("default", icon);
            sprite.SpriteFrames = frames;
            sprite.Animation = "default";
            sprite.Play();
        }
        base._Ready();
    }
}
