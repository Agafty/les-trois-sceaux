using Godot;
using System.Threading.Tasks;

public partial class SceneManager : CanvasLayer
{
    private const float FadeDuration = 0.3f;

    private ColorRect _fade;
    private string _pendingSpawnId = "";

    private bool _transitioning;

    // Point d'entrée utilisé pour la salle courante, pour y revenir après une mort.
    // Vide tant qu'aucun GoToScene n'a eu lieu (salle lancée directement avec F5/F6).
    public string LastSpawnId { get; private set; } = "";

    public override void _Ready()
    {
        Layer = 10;
        _fade = GetNode<ColorRect>("Fade");
        _fade.Color = new Color(0, 0, 0, 0);
        _fade.MouseFilter = Control.MouseFilterEnum.Ignore;
    }

    /// <summary>Vrai pendant un fondu / changement de salle.</summary>
    public bool IsTransitioning => _transitioning;

    public bool GoToScene(string scenePath, string spawnId = "")
    {
        if (_transitioning) return false;
        _transitioning = true;
        _pendingSpawnId = spawnId;
        LastSpawnId = spawnId;
        _ = FadeAndChangeScene(scenePath);
        return true;
    }

    /// <summary>Recharge la salle courante au point d'entrée mémorisé (PV et ennemis remis à neuf).</summary>
    public bool ReloadCurrentRoom()
    {
        return GoToScene(GetTree().CurrentScene.SceneFilePath, LastSpawnId);
    }

    public string ConsumeSpawnId()
    {
        var id = _pendingSpawnId;
        _pendingSpawnId = "";
        return id;
    }

    private async Task FadeAndChangeScene(string scenePath)
    {
        try
        {
            await FadeTo(1f);
            GetTree().CallDeferred(SceneTree.MethodName.ChangeSceneToFile, scenePath);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await FadeTo(0f);
        }
        finally
        {
            _transitioning = false;
        }
    }

    private async Task FadeTo(float alpha)
    {
        var tween = CreateTween();
        tween.TweenProperty(_fade, "color:a", alpha, FadeDuration);
        await ToSignal(tween, Tween.SignalName.Finished);
    }
}
