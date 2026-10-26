using System;

/// <summary>
/// Étapes de l'histoire, vues du village (classe C# pure, sans Godot). L'étape est DÉRIVÉE de la sauvegarde, jamais stockée :
///   0 = début (aucun sceau)            1 = après la forêt (1 sceau)
///   2 = après la montagne (2 sceaux)   3 = après le lac (3 sceaux, éclipse, avant le final)
///   4 = épilogue (flag <see cref="EpilogueFlag"/> posé quand Morvath est vaincu)
/// Elle correspond aux 5 étapes de « Évolution du village » de la roadmap.
/// </summary>
public static class StoryRules
{
    public const int MaxStage = 4;

    /// <summary>Id mémorisé dans GameState (MarkCollected) à la fin du jeu : fait passer le village à l'épilogue.</summary>
    public const string EpilogueFlag = "morvath_vaincu";

    public static int Compute(int sealCount, bool epilogue)
    {
        if (epilogue) return MaxStage;
        return Math.Clamp(sealCount, 0, MaxStage - 1);
    }

    /// <summary>Valeur par défaut de <c>etape_max</c> sur un objet Tiled (« jamais retiré »).</summary>
    public const int NoMaxStage = 99;

    /// <summary>
    /// Vrai si un objet Tiled doit exister à l'étape donnée (propriétés <c>etape_min</c> / <c>etape_max</c>, bornes incluses).
    /// Un intervalle à l'envers (min &gt; max) ne contient jamais rien.
    /// </summary>
    public static bool IsInStageRange(int minStage, int maxStage, int stage) => stage >= minStage && stage <= maxStage;
}
