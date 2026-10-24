/// <summary>Résultat d'un coup porté à un membre d'un groupe d'interrupteurs.</summary>
public enum SwitchHitResult
{
    /// <summary>Rien ne change (déjà actif, ou groupe déjà résolu).</summary>
    Ignored,
    /// <summary>Le membre devient actif ; le groupe n'est pas encore complet.</summary>
    Activated,
    /// <summary>Le membre touché était le dernier : tous sont actifs, la porte doit s'ouvrir.</summary>
    Solved,
    /// <summary>Touché hors de l'ordre demandé : tout le groupe est revenu à zéro.</summary>
    WrongOrder,
}

/// <summary>
/// Règles pures d'un groupe d'interrupteurs (sans Godot). Les interrupteurs de même « cible » forment un groupe :
/// la porte s'ouvre quand tous sont actifs ensemble. Chaque membre a un <c>ordre</c> (0 = libre) et une <c>durée</c>
/// (0 = reste actif). Un membre avec ordre doit être touché quand il est le plus petit ordre encore inactif ; sinon
/// le groupe entier revient à zéro. Un membre avec durée se désactive tout seul (<see cref="Tick"/>).
/// </summary>
public sealed class SwitchGroupLogic
{
    private readonly int[] _order;
    private readonly float[] _duration;
    private readonly bool[] _active;
    private readonly bool[] _timed;
    private readonly float[] _remaining;
    private readonly float[] _total;
    private readonly bool[] _justExpired;
    private int _timedCount;

    public SwitchGroupLogic(int count)
    {
        _order = new int[count];
        _duration = new float[count];
        _active = new bool[count];
        _timed = new bool[count];
        _remaining = new float[count];
        _total = new float[count];
        _justExpired = new bool[count];
    }

    public int Count => _order.Length;

    /// <summary>Vrai quand tous les membres ont été activés ensemble : le groupe ne bouge plus ensuite.</summary>
    public bool IsSolved { get; private set; }

    /// <summary>Au moins un membre est actif avec un compte à rebours en cours.</summary>
    public bool HasRunningTimer => _timedCount > 0;

    public void Configure(int index, int order, float duration)
    {
        _order[index] = order < 0 ? 0 : order;
        _duration[index] = duration < 0f ? 0f : duration;
    }

    public bool IsActive(int index) => _active[index];

    /// <summary>Le membre vient de se désactiver au dernier <see cref="Tick"/>.</summary>
    public bool JustExpired(int index) => _justExpired[index];

    /// <summary>Temps restant (s) d'un membre actif chronométré, 0 sinon.</summary>
    public float Remaining(int index) => _timed[index] ? _remaining[index] : 0f;

    /// <summary>Durée totale (s) accordée au membre à son activation, 0 s'il n'est pas chronométré.</summary>
    public float Total(int index) => _timed[index] ? _total[index] : 0f;

    /// <summary>Fraction (0 à 1) du temps qui reste, 1 si le membre n'est pas chronométré.</summary>
    public float Fraction(int index) => _timed[index] && _total[index] > 0f ? _remaining[index] / _total[index] : 1f;

    /// <summary>
    /// Un coup sur le membre. <paramref name="timeMultiplier"/> multiplie sa durée (option d'aide) ;
    /// 0 ou moins = durée illimitée (le membre reste actif).
    /// </summary>
    public SwitchHitResult Hit(int index, float timeMultiplier)
    {
        if (IsSolved || _active[index]) return SwitchHitResult.Ignored;

        if (_order[index] > 0 && _order[index] != NextOrder())
        {
            ResetAll();
            return SwitchHitResult.WrongOrder;
        }

        _active[index] = true;
        if (_duration[index] > 0f && timeMultiplier > 0f)
        {
            _timed[index] = true;
            _total[index] = _duration[index] * timeMultiplier;
            _remaining[index] = _total[index];
            _timedCount++;
        }

        for (int i = 0; i < _active.Length; i++)
            if (!_active[i]) return SwitchHitResult.Activated;

        IsSolved = true;
        // Plus aucun compte à rebours : tout reste actif définitivement.
        for (int i = 0; i < _timed.Length; i++) _timed[i] = false;
        _timedCount = 0;
        return SwitchHitResult.Solved;
    }

    /// <summary>Avance les comptes à rebours. Renvoie le nombre de membres qui viennent de se désactiver (voir <see cref="JustExpired"/>).</summary>
    public int Tick(float delta)
    {
        for (int i = 0; i < _justExpired.Length; i++) _justExpired[i] = false;
        if (IsSolved || _timedCount == 0) return 0;

        int expired = 0;
        for (int i = 0; i < _timed.Length; i++)
        {
            if (!_timed[i]) continue;
            _remaining[i] -= delta;
            if (_remaining[i] > 0f) continue;
            _remaining[i] = 0f;
            _timed[i] = false;
            _active[i] = false;
            _justExpired[i] = true;
            _timedCount--;
            expired++;
        }
        return expired;
    }

    /// <summary>Remet tout le groupe à zéro (mauvais ordre).</summary>
    public void ResetAll()
    {
        for (int i = 0; i < _active.Length; i++)
        {
            _active[i] = false;
            _timed[i] = false;
            _remaining[i] = 0f;
            _justExpired[i] = false;
        }
        _timedCount = 0;
    }

    // Plus petit ordre (> 0) parmi les membres encore inactifs ; 0 s'il n'y en a plus.
    private int NextOrder()
    {
        int next = 0;
        for (int i = 0; i < _order.Length; i++)
        {
            if (_active[i] || _order[i] <= 0) continue;
            if (next == 0 || _order[i] < next) next = _order[i];
        }
        return next;
    }
}
