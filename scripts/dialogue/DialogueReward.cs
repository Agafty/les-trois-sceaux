/// <summary>
/// Récompense donnée à la fin d'une conversation (champ « reward » d'un bloc de dialogue JSON) : un ramassable de resources/pickups/ et l'id
/// unique qui mémorise qu'elle a été donnée (classe C# pure).
/// </summary>
public sealed class DialogueReward
{
    /// <summary>Nom du .tres de resources/pickups/ (sans extension), ex. « quart_coeur ».</summary>
    public string Content { get; init; } = "";

    /// <summary>Id mémorisé dans GameState (MarkCollected) une fois la récompense donnée ; elle ne l'est jamais deux fois.</summary>
    public string Id { get; init; } = "";
}
