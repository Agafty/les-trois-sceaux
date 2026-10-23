using Godot;
using System.Collections.Generic;

public partial class Room : Node2D
{
    public override void _Ready()
    {
        var player = FindPlayer(this);
        var sceneManager = GetNode<SceneManager>("/root/SceneManager");
        var spawn = FindSpawnById(this, sceneManager.ConsumeSpawnId());
        if (player != null && spawn != null)
            player.GlobalPosition = spawn.GlobalPosition;

        foreach (var sortie in FindAllByClass(this, "Sortie"))
        {
            if (sortie is Area2D area)
                area.BodyEntered += body => OnSortieEntered(area, body);
        }

        if (player != null)
            ConfigureCamera(player);
    }

    private void ConfigureCamera(Player player)
    {
        var camera = player.GetNodeOrNull<Camera2D>("Camera2D");
        var tileMapLayer = FindNodeByName(this, "Sol") as TileMapLayer;
        if (camera == null || tileMapLayer?.TileSet == null)
            return;

        var usedRect = tileMapLayer.GetUsedRect();
        var tileSize = tileMapLayer.TileSet.TileSize;

        camera.LimitLeft = usedRect.Position.X * tileSize.X;
        camera.LimitTop = usedRect.Position.Y * tileSize.Y;
        camera.LimitRight = (usedRect.Position.X + usedRect.Size.X) * tileSize.X;
        camera.LimitBottom = (usedRect.Position.Y + usedRect.Size.Y) * tileSize.Y;
        camera.PositionSmoothingEnabled = true;
    }

    private static Player FindPlayer(Node root)
    {
        foreach (var child in root.GetChildren())
        {
            if (child is Player player)
                return player;
            var found = FindPlayer(child);
            if (found != null)
                return found;
        }
        return null;
    }

    private static Node FindNodeByName(Node root, string name)
    {
        foreach (var child in root.GetChildren())
        {
            if (child.Name == name)
                return child;
            var found = FindNodeByName(child, name);
            if (found != null)
                return found;
        }
        return null;
    }

    private void OnSortieEntered(Node sortie, Node body)
    {
        if (body is not Player { IsDead: false }) return;
        if (!sortie.HasMeta("cible_carte")) return;

        var cibleCarte = (string)sortie.GetMeta("cible_carte");
        var cibleSpawn = sortie.HasMeta("cible_spawn") ? (string)sortie.GetMeta("cible_spawn") : "";
        GetNode<SceneManager>("/root/SceneManager").GoToScene(cibleCarte, cibleSpawn);
    }

    private static Node2D FindSpawnById(Node root, string spawnId)
    {
        Node2D firstSpawn = null;
        foreach (var node in FindAllByClass(root, "Spawn"))
        {
            if (node is not Node2D node2D) continue;
            firstSpawn ??= node2D;
            if (!string.IsNullOrEmpty(spawnId) && node.HasMeta("id") && (string)node.GetMeta("id") == spawnId)
                return node2D;
        }
        return firstSpawn;
    }

    private static List<Node> FindAllByClass(Node root, string className)
    {
        var results = new List<Node>();
        CollectByClass(root, className, results);
        return results;
    }

    private static void CollectByClass(Node root, string className, List<Node> results)
    {
        foreach (var child in root.GetChildren())
        {
            if (HasClass(child, className))
                results.Add(child);
            CollectByClass(child, className, results);
        }
    }

    private static bool HasClass(Node node, string className)
    {
        return node.HasMeta("class") && (string)node.GetMeta("class") == className;
    }
}
