using Godot;

/// <summary>
/// Un objet de la salle qui réagit à la lanterne quand Brann (qui la possède) reste à portée : torche à allumer, mur à rune.
/// Il s'inscrit dans <see cref="LanternRegistry"/> tant qu'il attend la lanterne et s'en retire dès qu'il a réagi ou quitte l'arbre.
/// </summary>
public interface ILanternReactive
{
    /// <summary>Position monde mesurée contre Brann.</summary>
    Vector2 LanternPosition { get; }

    /// <summary>Distance (px) à laquelle la lanterne agit.</summary>
    float LanternReach { get; }

    /// <summary>Secondes de présence nécessaires.</summary>
    float LanternDwell { get; }

    /// <summary>Présence cumulée (tenue par <c>LanternLight</c>).</summary>
    float LanternTimer { get; set; }

    /// <summary>La lanterne est restée assez longtemps à portée : réagir (puis se désinscrire).</summary>
    void OnLanternReached();
}
