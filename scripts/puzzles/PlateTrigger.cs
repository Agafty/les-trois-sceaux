/// <summary>Ce qui enfonce une plaque de pression (propriété Tiled « declencheur »).</summary>
public enum PlateTrigger
{
    /// <summary>Un bloc poussable ou Brann (valeur par défaut).</summary>
    Tous,
    /// <summary>Seulement un bloc poussable.</summary>
    Bloc,
    /// <summary>Seulement Brann.</summary>
    Joueur,
}
