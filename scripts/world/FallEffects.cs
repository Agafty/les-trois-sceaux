using Godot;

/// <summary>Effets partagés par les trous (fosse mortelle et trou de passage).</summary>
public static class FallEffects
{
    /// <summary>
    /// Un ennemi tombe : il est figé, ne touche plus personne, rétrécit, puis est libéré SANS signal Died (pas de butin).
    /// La salle voit son nœud quitter l'arbre et le compte comme parti (porte « ennemis »).
    /// Le tween est rattaché à <paramref name="owner"/> (l'ennemi a son traitement désactivé).
    /// </summary>
    public static void DropEnemy(Node owner, Node2D enemy, float duration)
    {
        enemy.ProcessMode = Node.ProcessModeEnum.Disabled;
        if (enemy is CollisionObject2D body)
            body.CollisionLayer = 0;
        foreach (var child in enemy.GetChildren())
        {
            if (child is Area2D area)
            {
                area.SetDeferred(Area2D.PropertyName.Monitoring, false);
                area.SetDeferred(Area2D.PropertyName.Monitorable, false);
            }
        }

        var tween = owner.CreateTween();
        tween.SetParallel(true);
        tween.TweenProperty(enemy, "scale", new Vector2(0.1f, 0.1f), duration);
        tween.TweenProperty(enemy, "modulate:a", 0f, duration);
        tween.Chain().TweenCallback(Callable.From(() =>
        {
            if (GodotObject.IsInstanceValid(enemy)) enemy.QueueFree();
        }));
    }
}
