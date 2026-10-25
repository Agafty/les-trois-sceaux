using System.Collections.Generic;
using Godot;

/// <summary>
/// Garde une référence C# forte vers des ressources dont la classe est écrite en C# (PickupEffect, LootTable, LootEntry...).
/// Sans cela, une telle ressource n'est tenue que par le cache de Godot et par des propriétés de nœuds qui disparaissent
/// à chaque changement de salle : le ramasse-miettes .NET peut alors libérer l'objet C# pendant que Godot le réutilise
/// (plantage « gchandle.is_released() » ou propriété [Export] qui revient vide). Ici, la ressource reste vivante tant que le jeu tourne.
/// Thread principal uniquement (les dictionnaires ne sont pas protégés). Classe statique : pas un autoload (limités à 4). Les ressources sont partagées et peu nombreuses, donc la mémoire reste bornée.
/// </summary>
public static class ResourceKeeper
{
    private static readonly Dictionary<string, Resource> ByPath = new();
    private static readonly HashSet<Resource> Pinned = new();

    /// <summary>Charge une ressource par chemin (une seule fois) et la garde. Renvoie null, avec une erreur claire, si le chargement échoue.</summary>
    public static T Load<T>(string path) where T : Resource
    {
        if (string.IsNullOrEmpty(path))
        {
            GD.PushError($"ResourceKeeper.Load<{typeof(T).Name}> : chemin vide.");
            return null;
        }
        if (ByPath.TryGetValue(path, out var cached))
        {
            if (cached is T typed && GodotObject.IsInstanceValid(typed))
                return typed;
            Pinned.Remove(cached); // ressource devenue invalide : on l'oublie avant de la recharger
            ByPath.Remove(path);
        }

        var resource = GD.Load<T>(path);
        if (resource == null)
        {
            GD.PushError($"Impossible de charger la ressource {typeof(T).Name} « {path} » (fichier absent, script cassé ou mauvais type).");
            return null;
        }
        ByPath[path] = resource;
        Pinned.Add(resource);
        return resource;
    }

    /// <summary>Garde une ressource déjà chargée (par exemple tenue par une scène d'ennemi). Sans effet pour null.</summary>
    public static void Pin(Resource resource)
    {
        if (resource != null) Pinned.Add(resource);
    }
}
