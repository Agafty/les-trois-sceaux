using System;
using System.Collections.Generic;

/// <summary>
/// Règles pures (sans Godot) du générique de fin : vitesse de défilement, progression et section à lire à voix haute.
/// Coordonnées : « haut d'une section » = sa position dans le contenu (0 = début du contenu) ; à l'écran, le contenu démarre juste sous le
/// bas de l'écran et monte de <c>offset</c> pixels : y écran = hauteurÉcran - offset + hautSection.
/// </summary>
public static class CreditsRules
{
    /// <summary>Vitesse normale (px/s) : environ une minute pour tout le texte.</summary>
    public const float NormalSpeed = 16f;

    /// <summary>Multiplicateur quand le joueur maintient une touche.</summary>
    public const float FastMultiplier = 8f;

    /// <summary>Maintien (s) de « pause » pour passer le générique.</summary>
    public const float SkipHoldSeconds = 1f;

    /// <summary>Durée (s) de l'écran « Fin » avant le retour automatique au titre.</summary>
    public const float EndHoldSeconds = 8f;

    /// <summary>Ligne de lecture (part de la hauteur d'écran, depuis le haut) que doit franchir le haut d'une section pour être lue.</summary>
    public const float ReadLine = 0.7f;

    public static float Speed(bool fast) => fast ? NormalSpeed * FastMultiplier : NormalSpeed;

    /// <summary>Nouveau décalage après <paramref name="delta"/> secondes, borné à <paramref name="maxOffset"/>.</summary>
    public static float Advance(float offset, float delta, bool fast, float maxOffset)
        => Math.Min(Math.Max(maxOffset, 0f), offset + Speed(fast) * Math.Max(delta, 0f));

    /// <summary>Décalage où tout le contenu est sorti par le haut de l'écran.</summary>
    public static float EndOffset(float screenHeight, float contentHeight) => screenHeight + contentHeight;

    /// <summary>Indice de la dernière section dont le haut a franchi la ligne de lecture ; -1 si aucune.</summary>
    public static int SectionToRead(IReadOnlyList<float> sectionTops, float offset, float screenHeight)
    {
        int result = -1;
        float line = screenHeight * ReadLine;
        for (int i = 0; i < sectionTops.Count; i++)
        {
            float screenY = screenHeight - offset + sectionTops[i];
            if (screenY <= line) result = i;
            else break;
        }
        return result;
    }
}
