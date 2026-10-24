/// <summary>Règles pures des portes (sans Godot) : lecture du type Tiled.</summary>
public static class DoorRules
{
    /// <summary>Convertit la valeur Tiled « type » (cle, grande_cle, ennemis, interrupteur). Faux si inconnue.</summary>
    public static bool TryParseKind(string value, out DoorKind kind)
    {
        switch (value)
        {
            case "cle": kind = DoorKind.Cle; return true;
            case "grande_cle": kind = DoorKind.GrandeCle; return true;
            case "ennemis": kind = DoorKind.Ennemis; return true;
            case "interrupteur": kind = DoorKind.Interrupteur; return true;
            default: kind = DoorKind.Cle; return false;
        }
    }

    /// <summary>Nom de fichier de l'image de la porte (art/puzzles/porte_&lt;nom&gt;.png).</summary>
    public static string TextureName(DoorKind kind) => kind switch
    {
        DoorKind.GrandeCle => "grande_cle",
        DoorKind.Ennemis => "ennemis",
        DoorKind.Interrupteur => "interrupteur",
        _ => "cle",
    };

    /// <summary>Vrai pour les portes qui s'ouvrent quand Brann pousse dessus.</summary>
    public static bool OpensByPushing(DoorKind kind) => kind == DoorKind.Cle || kind == DoorKind.GrandeCle;
}
