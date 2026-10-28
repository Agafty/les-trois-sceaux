/// <summary>
/// Règles pures (sans Godot) pour reconnaître certaines tuiles par leur numéro (id local Tiled = ligne x colonnes + colonne),
/// comme <see cref="HoleRules"/> : aucune modification des cartes .tmx n'est nécessaire.
/// Les tilesets sont désignés par le nom de leur PNG (« foret » pour art/tilesets/foret.png...).
/// </summary>
public static class TileRules
{
    public const string ForestTileset = "foret";
    public const string VillageTileset = "village";
    public const string MountainTileset = "montagne";

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
        MountainTileset => tileId == 203 || tileId == 204,
        _ => false,
    };

    /// <summary>Ravin du tileset village (terrain « Ravin », 80 à 95) : solide pour Brann et les ennemis, mais les flèches passent au-dessus.</summary>
    public static bool IsRavine(string tileset, int tileId) => (tileset == VillageTileset || tileset == MountainTileset) && tileId >= 80 && tileId <= 95;

    public const string InteriorTileset = "interieurs";

    /// <summary>
    /// Tuile « fermée » d'un mur fissuré ou d'un éboulis (village 136 à 139 et 142, intérieurs 67), que la bombe fait disparaître du calque « Murs ».
    /// </summary>
    public static bool IsBreakable(string tileset, int tileId) => tileset switch
    {
        VillageTileset => (tileId >= 136 && tileId <= 139) || tileId == 142,
        MountainTileset => tileId == 156 || tileId == 172 || (tileId >= 176 && tileId <= 179),
        InteriorTileset => tileId == 67,
        _ => false,
    };

    /// <summary>
    /// Version ouverte d'une tuile cassable et calque où la poser : éboulis 136/138 vers 140 et 137/139 vers 141 (« Sol »), mur fissuré 142 vers 143 (« Decor »).
    /// Faux s'il n'y a pas de version ouverte (la case est alors seulement vidée).
    /// </summary>
    public static bool TryGetOpenedTile(string tileset, int closedId, out int openId, out string layer)
    {
        openId = -1;
        layer = "";
        if (tileset == MountainTileset)
        {
            switch (closedId)
            {
                case 176: case 178: openId = 180; layer = "Sol"; return true;
                case 177: case 179: openId = 181; layer = "Sol"; return true;
                case 156: openId = 157; layer = "Decor"; return true;
                case 172: openId = 173; layer = "Decor"; return true;
                default: return false;
            }
        }
        if (tileset != VillageTileset) return false;
        switch (closedId)
        {
            case 136: case 138: openId = 140; layer = "Sol"; return true;
            case 137: case 139: openId = 141; layer = "Sol"; return true;
            case 142: openId = 143; layer = "Decor"; return true;
            default: return false;
        }
    }

    /// <summary>Tuile fermée dessinée par un mur fissuré quand la carte a déjà posé dessous la version ouverte (140 donne 136, 141 donne 137, 143 donne 142).</summary>
    public static bool TryGetClosedTile(string tileset, int openId, out int closedId)
    {
        closedId = -1;
        if (tileset == MountainTileset)
        {
            switch (openId)
            {
                case 180: closedId = 176; return true;
                case 181: closedId = 177; return true;
                case 157: closedId = 156; return true;
                case 173: closedId = 172; return true;
                default: return false;
            }
        }
        if (tileset != VillageTileset) return false;
        switch (openId)
        {
            case 140: closedId = 136; return true;
            case 141: closedId = 137; return true;
            case 143: closedId = 142; return true;
            default: return false;
        }
    }
}
