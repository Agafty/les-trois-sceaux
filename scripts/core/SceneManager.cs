using System;
using Godot;
using System.Threading.Tasks;

public partial class SceneManager : CanvasLayer
{
    private const float FadeDuration = 0.3f;

    /// <summary>Le changement de salle est terminé (fondu fini, _transitioning remis à false). Sert à la sauvegarde automatique.</summary>
    [Signal]
    public delegate void TransitionFinishedEventHandler(string scenePath, string spawnId);

    private ColorRect _fade;
    private string _previousSpawnId = "";
    private bool _changeFailed;
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

    /// <summary>
    /// Change de salle avec un fondu. <paramref name="beforeChange"/> (optionnel) est appelé une fois l'écran noir,
    /// juste avant le changement de scène : c'est là que le chargement d'une sauvegarde applique l'état,
    /// pour que l'ancienne salle ne puisse plus l'écraser.
    /// </summary>
    public bool GoToScene(string scenePath, string spawnId = "", Action beforeChange = null)
    {
        if (_transitioning) return false;
        _transitioning = true;
        _pendingSpawnId = spawnId;
        _previousSpawnId = LastSpawnId; // pour revenir en arrière si le changement échoue
        _changeFailed = false;
        LastSpawnId = spawnId;
        _ = FadeAndChangeScene(scenePath, beforeChange);
        return true;
    }

    /// <summary>Recharge la salle courante au point d'entrée mémorisé (PV et ennemis remis à neuf).</summary>
    public bool ReloadCurrentRoom()
    {
        return GoToScene(GetTree().CurrentScene.SceneFilePath, LastSpawnId);
    }

    /// <summary>Oublie le point d'entrée mémorisé (nouvelle partie).</summary>
    public void ResetSpawnId() => LastSpawnId = "";

    public string ConsumeSpawnId()
    {
        var id = _pendingSpawnId;
        _pendingSpawnId = "";
        return id;
    }

    private async Task FadeAndChangeScene(string scenePath, Action beforeChange)
    {
        bool completed = false;
        try
        {
            await FadeTo(1f);
            Callable.From(() => ChangeScene(scenePath, beforeChange)).CallDeferred();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await FadeTo(0f);
            completed = true;
        }
        catch (Exception e)
        {
            GD.PushError($"Changement de salle vers « {scenePath} » échoué : {e.Message}");
            _fade.Color = new Color(0, 0, 0, 0);
        }
        finally
        {
            _transitioning = false;
        }
        if (_changeFailed)
        {
            // On est resté dans l'ancienne salle : on retrouve son point d'entrée et on ne signale rien
            // (sinon la sauvegarde auto écrirait cette salle avec le spawn de la tentative ratée).
            LastSpawnId = _previousSpawnId;
            _pendingSpawnId = "";
        }
        else if (completed)
            EmitSignal(SignalName.TransitionFinished, scenePath, LastSpawnId);
    }

    private void ChangeScene(string scenePath, Action beforeChange)
    {
        try
        {
            beforeChange?.Invoke();
        }
        catch (Exception e)
        {
            GD.PushError($"Préparation du changement de salle échouée, changement annulé : {e.Message}");
            _changeFailed = true;
            return;
        }
        var error = GetTree().ChangeSceneToFile(scenePath);
        if (error != Error.Ok)
        {
            GD.PushError($"Impossible de charger la scène « {scenePath} » : {error}");
            _changeFailed = true;
        }
    }

    private async Task FadeTo(float alpha)
    {
        var tween = CreateTween();
        tween.TweenProperty(_fade, "color:a", alpha, FadeDuration);
        await ToSignal(tween, Tween.SignalName.Finished);
    }
}
