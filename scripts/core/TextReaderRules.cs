using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;

/// <summary>Règles pures (sans Godot) de la lecture à voix haute : nettoyage du texte, vitesse, langue de la voix.</summary>
public static class TextReaderRules
{
    public const float SlowRate = 0.85f;
    public const float NormalRate = 1.0f;

    private static readonly Regex TimesPattern = new(@"(?<![\p{L}\d])x(\d+)", RegexOptions.Compiled);

    private static readonly char[] LocaleSeparators = { '_', '-' };

    /// <summary>Vitesse de la voix pour un réglage <see cref="OptionsData.ReadSpeed"/> (0 = lente, 1 = normale).</summary>
    public static float RateFor(int readSpeed) => readSpeed == 1 ? NormalRate : SlowRate;

    /// <summary>« fr_FR » ou « fr-FR » donne « fr » ; vide donne « fr ».</summary>
    public static string LanguageOf(string locale)
    {
        if (string.IsNullOrEmpty(locale)) return "fr";
        int cut = locale.IndexOfAny(LocaleSeparators);
        return (cut > 0 ? locale.Substring(0, cut) : locale).ToLowerInvariant();
    }

    /// <summary>
    /// Prépare un texte pour la synthèse vocale : retire les balises [BBCode], les guillemets français, les symboles qui se
    /// lisent mal (flèches, cœurs, chevrons...), remplace les retours à la ligne par une pause et réduit les espaces.
    /// </summary>
    public static string Clean(string text, string language = "fr")
    {
        if (string.IsNullOrWhiteSpace(text)) return "";
        // « x2 » (multiplicateur du jeu) se lit « fois 2 » / « times 2 ».
        text = TimesPattern.Replace(text, language == "en" ? "times $1" : "fois $1");
        var sb = new StringBuilder(text.Length);
        bool inTag = false;
        for (int i = 0; i < text.Length; i++)
        {
            char c = text[i];
            if (inTag)
            {
                if (c == ']') inTag = false;
                continue;
            }
            switch (c)
            {
                case '[':
                    if (text.IndexOf(']', i) > i) { inTag = true; continue; } // « [ » jamais fermé : texte normal
                    break;
                case '\r': continue;
                case '\n': AppendPause(sb); continue;
                case '…': sb.Append("..."); continue;
                case '—':
                case '–': sb.Append(", "); continue;
                case '«':
                case '»':
                case '"':
                case '_':
                case '*':
                case '#':
                case '~':
                case '^':
                case '|': continue;
                case '’': sb.Append('\''); continue;
            }
            var category = char.GetUnicodeCategory(c);
            if (category is UnicodeCategory.MathSymbol or UnicodeCategory.OtherSymbol or UnicodeCategory.ModifierSymbol
                or UnicodeCategory.Control or UnicodeCategory.Surrogate or UnicodeCategory.PrivateUse)
            {
                sb.Append(' ');
                continue;
            }
            sb.Append(c);
        }
        return CollapseSpaces(sb.ToString());
    }

    private static void AppendPause(StringBuilder sb)
    {
        int end = sb.Length;
        while (end > 0 && sb[end - 1] == ' ') end--;
        sb.Length = end;
        if (end > 0 && ".!?:;,".IndexOf(sb[end - 1]) < 0) sb.Append('.');
        sb.Append(' ');
    }

    private static string CollapseSpaces(string s)
    {
        var sb = new StringBuilder(s.Length);
        bool lastSpace = true;
        foreach (char c in s)
        {
            if (char.IsWhiteSpace(c))
            {
                if (!lastSpace) sb.Append(' ');
                lastSpace = true;
            }
            else
            {
                sb.Append(c);
                lastSpace = false;
            }
        }
        return sb.ToString().TrimEnd();
    }
}
