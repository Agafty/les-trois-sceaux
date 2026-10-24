/// <summary>Façon d'ouvrir une porte (propriété Tiled « type » de l'objet Porte).</summary>
public enum DoorKind
{
    /// <summary>Consomme une petite clé au contact (« cle »).</summary>
    Cle,
    /// <summary>Demande la grande clé du donjon, qui n'est pas consommée (« grande_cle »).</summary>
    GrandeCle,
    /// <summary>Fermée tant que les ennemis de la salle ne sont pas tous morts (« ennemis »).</summary>
    Ennemis,
    /// <summary>Ouverte de l'extérieur par un interrupteur, via <c>Door.Open()</c> (« interrupteur »).</summary>
    Interrupteur,
}
