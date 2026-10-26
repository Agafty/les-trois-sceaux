/// <summary>
/// Règles pures (sans Godot) pour reconnaître certaines tuiles par leur numéro (id local Tiled = ligne x colonnes + colonne),
/// comme <see cref="HoleRules"/> : aucune modification des cartes .tmx n'est nécessaire.
/// Les tilesets sont désignés par le nom de leur PNG (« foret » pour art/tilesets/foret.png...).
/// </summary>
public static class TileRules
{
    public const string ForestTileset = "foret";
    public const string VillageTileset = "village";

    /// <summary>Nom d'un tileset d'après le chemin de son image (« res://art/tilesets/foret.png » donne « foret »). Vide si le chemin n'est pas un PNG.</summary>
    public static string TilesetNameFromTexturePath(string path)
    {
        if (string.IsNullOrEmpty(path) || !path.EndsWith(".png", System.StringComparison.OrdinalIgnoreCase)) return "";
        int slash = path.LastIndexOf('/'); // les chemins Godot (res://) n'utilisent que « / »
        return path.Substring(slash + 1, path.Length - slash - 5);
    }

    /// <summary>Numéro de tuile (id local Tiled) d'une case de l'atlas.</summary>
    public static int TileId(int atlasX, int atlasY, int columns) => atlasY * columns + atlasX;

    /// <summary>Buisson coupable à l'épée : foret 96 à 99 (buisson_a, buisson_b, fleuri, baies) et village 300 (buisson_fleuri).</summary>
    public static bool IsBush(string tileset, int tileId) => tileset switch
    {
        ForestTileset => tileId >= 96 && tileId <= 99,
        VillageTileset => tileId == 300,
        _ => false,
    };

    /// <summary>Ravin du tileset village (terrain « Ravin », 80 à 95) : solide pour Brann et les ennemis, mais les flèches passent au-dessus.</summary>
    public static bool IsRavine(string tileset, int tileId) => tileset == VillageTileset && tileId >= 80 && tileId <= 95;
}
