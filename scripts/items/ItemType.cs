/// <summary>
/// Catégorie d'un objet d'inventaire. Volontairement courte :
/// <list type="bullet">
/// <item>Equipable : peut être assigné à la touche use_item (arc, bombes, lanterne).</item>
/// <item>KeyItem : objet de quête, possédé mais jamais équipé (clé du boss, médaillon...).</item>
/// <item>Consumable : s'utilise directement depuis le menu (potion) ; pas encore géré.</item>
/// </list>
/// </summary>
public enum ItemType
{
    Equipable,
    KeyItem,
    Consumable,
}
