using Godot;
using System.Threading.Tasks;

public partial class SceneManager : CanvasLayer
{
    private const float FadeDuration = 0.3f;

    private ColorRect _fade;
    private string _pendingSpawnId = "";

    public override void _Ready()
    {
        Layer = 10;
        _fade = GetNode<ColorRect>("Fade");
        _fade.Color = new Color(0, 0, 0, 0);
        _fade.MouseFilter = Control.MouseFilterEnum.Ignore;
    }

    public void GoToScene(string scenePath, string spawnId = "")
    {
        _pendingSpawnId = spawnId;
        _ = FadeAndChangeScene(scenePath);
    }

    public string ConsumeSpawnId()
    {
        var id = _pendingSpawnId;
        _pendingSpawnId = "";
        return id;
    }

    private async Task FadeAndChangeScene(string scenePath)
    {
        await FadeTo(1f);
        GetTree().CallDeferred(SceneTree.MethodName.ChangeSceneToFile, scenePath);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await FadeTo(0f);
    }

    private async Task FadeTo(float alpha)
    {
        var tween = CreateTween();
        tween.TweenProperty(_fade, "color:a", alpha, FadeDuration);
        await ToSignal(tween, Tween.SignalName.Finished);
    }
}
