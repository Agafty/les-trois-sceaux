using System.Collections.Generic;
using Godot;

/// <summary>
/// Groupe d'interrupteurs de même cible dans une salle (créé par le premier <see cref="Switch"/> prêt). Il applique les
/// règles de <see cref="SwitchGroupLogic"/> (tous actifs ensemble, ordre, durée) et commande l'affichage des membres.
/// Quand le dernier membre est activé, il ouvre la porte cible. Son traitement n'est actif que pendant qu'un compte
/// à rebours tourne.
/// </summary>
public partial class SwitchGroup : Node
{
    private readonly List<Switch> _members = new();
    private SwitchGroupLogic _logic;
    private GameState _state;
    private string _target = "";

    /// <summary>Configure le groupe avant son ajout à l'arbre. L'ordre de la liste donne l'indice de chaque membre.</summary>
    public void Setup(List<Switch> members)
    {
        _members.Clear();
        _members.AddRange(members);
        _logic = new SwitchGroupLogic(_members.Count);
        for (int i = 0; i < _members.Count; i++)
        {
            _members[i].Group = this;
            _members[i].Index = i;
            _logic.Configure(i, _members[i].Order, _members[i].Duration);
        }
        _target = _members[0].Target;
    }

    public override void _Ready()
    {
        _state = GetNode<GameState>("/root/GameState");
        SetPhysicsProcess(false);
    }

    /// <summary>Un coup sur un membre.</summary>
    internal void Hit(Switch member)
    {
        int index = member.Index;
        switch (_logic.Hit(index, _state.PuzzleTimeMultiplier))
        {
            case SwitchHitResult.Activated:
                member.ShowActive(true);
                if (_logic.Total(index) > 0f)
                {
                    member.ShowTimer(1f, _logic.Total(index));
                    SetPhysicsProcess(true);
                }
                member.EmitActivated();
                break;

            case SwitchHitResult.Solved:
                Solve(member);
                break;

            case SwitchHitResult.WrongOrder:
                for (int i = 0; i < _members.Count; i++)
                {
                    _members[i].ShowActive(false);
                    _members[i].FlashError();
                }
                SetPhysicsProcess(false);
                break;
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        _logic.Tick((float)delta);
        for (int i = 0; i < _members.Count; i++)
        {
            var member = _members[i];
            if (_logic.JustExpired(i))
                member.ShowActive(false);
            else if (_logic.IsActive(i) && _logic.Total(i) > 0f)
                member.ShowTimer(_logic.Fraction(i), _logic.Remaining(i));
        }
        if (!_logic.HasRunningTimer)
            SetPhysicsProcess(false);
    }

    private void Solve(Switch last)
    {
        for (int i = 0; i < _members.Count; i++)
            _members[i].Freeze();
        SetPhysicsProcess(false);

        // Interrupteur isolé, permanent, sans ordre : comme avant, son Id est mémorisé.
        if (_members.Count == 1 && SwitchRules.IsPersistent(1, last.Order, last.Duration) && !string.IsNullOrEmpty(last.Id))
            _state.MarkCollected(last.Id);

        if (!Door.OpenById(GetTree(), _state, _target))
            GD.PushWarning($"Interrupteur {last.Id} : aucune porte « {_target} » dans cette salle (groupe « portes »), ouverture mémorisée.");
        last.EmitActivated();
    }
}
