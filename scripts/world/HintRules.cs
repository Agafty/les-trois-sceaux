/// <summary>Règles pures des rectangles d'indice (objets Tiled nommés « indice_... »), sans Godot.</summary>
public static class HintRules
{
    public const string Prefix = "indice_";

    /// <summary>Vrai si le nom d'un objet Tiled désigne un rectangle d'indice (« indice_ordre_cibles », éventuellement suivi d'un suffixe « 2 »).</summary>
    public static bool IsHintName(string name) => name != null && name.StartsWith(Prefix, System.StringComparison.Ordinal);

    /// <summary>
    /// Clé de traduction d'un indice : le nom en majuscules (« indice_ordre_cibles » donne « INDICE_ORDRE_CIBLES »).
    /// Un suffixe de doublon est ignoré : « nom 2 » (après un espace) ou chiffres collés à la fin (« indice_x2 », « indice_x_2 » donnent « INDICE_X »).
    /// Chaîne vide si le nom contient autre chose que lettres, chiffres et « _ » ou n'a plus de contenu après le préfixe.
    /// </summary>
    public static string KeyFor(string name)
    {
        if (!IsHintName(name)) return "";
        int space = name.IndexOf(' ');
        string baseName = space > 0 ? name[..space] : name;
        foreach (char c in baseName)
        {
            bool ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_';
            if (!ok) return "";
        }
        // Chiffres collés à la fin, puis les « _ » qui les précédaient.
        int end = baseName.Length;
        while (end > Prefix.Length && baseName[end - 1] >= '0' && baseName[end - 1] <= '9') end--;
        while (end > Prefix.Length && baseName[end - 1] == '_') end--;
        if (end <= Prefix.Length) return "";
        return baseName[..end].ToUpperInvariant();
    }
}
