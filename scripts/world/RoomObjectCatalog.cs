/// <summary>
/// Correspondance entre les valeurs écrites dans Tiled (type d'ennemi, contenu d'un coffre...) et les
/// fichiers du projet. Classe C# pure (sans Godot).
/// </summary>
public static class RoomObjectCatalog
{
    public const string VariantRed = "rouge";

    /// <summary>Accepte seulement un nom simple (lettres minuscules, chiffres, « _ ») : jamais de chemin venu d'une carte.</summary>
    public static bool IsSafeName(string name)
    {
        if (string.IsNullOrEmpty(name)) return false;
        foreach (char c in name)
        {
            bool ok = (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_';
            if (!ok) return false;
        }
        return true;
    }

    public static string EnemyScenePath(string type) => $"res://scenes/enemies/{type}.tscn";

    /// <summary>SpriteFrames de la variante rouge d'un ennemi (art/enemies/&lt;type&gt;_red_frames.tres).</summary>
    public static string EnemyRedFramesPath(string type) => $"res://art/enemies/{type}_red_frames.tres";

    public static bool IsRedVariant(string variant) => variant == VariantRed;

    /// <summary>Effet de ramassage correspondant à la propriété « contenu » (resources/pickups/&lt;contenu&gt;.tres).</summary>
    public static string PickupEffectPath(string content) => $"res://resources/pickups/{content}.tres";
}
