/// <summary>
/// Découpage des planches de Sylve (art/bosses/sylve/sylve.png, 21 cases de 96x96) et position des trois bulbes sur ses bois,
/// recopiés de sylve.json (le graphiste les fournit par case ; centre du bulbe en px dans la case, origine en haut à gauche).
/// Classe C# pure. Si le graphiste réorganise la planche, c'est ici (et dans les [Export] de SylveBoss) qu'il faut ajuster.
/// </summary>
public static class SylveFrames
{
    /// <summary>Une animation : première case, nombre de cases, images par seconde.</summary>
    public readonly struct Clip
    {
        public readonly int Start;
        public readonly int Count;
        public readonly float Fps;

        public Clip(int start, int count, float fps)
        {
            Start = start;
            Count = count;
            Fps = fps;
        }

        /// <summary>Case à montrer après <paramref name="seconds"/> secondes (en boucle, ou figée sur la dernière si <paramref name="loop"/> est faux).</summary>
        public int FrameAt(float seconds, bool loop = true)
        {
            int step = (int)(seconds * Fps);
            if (Count <= 1) return Start;
            return Start + (loop ? step % Count : System.Math.Min(step, Count - 1));
        }
    }

    // Planche de face (sylve.png et sylve_ronces.png).
    public static readonly Clip Idle = new(0, 4, 4f);
    public static readonly Clip Walk = new(4, 4, 6f);
    public static readonly Clip Windup = new(8, 2, 6f);
    public static readonly Clip Charge = new(10, 4, 10f);
    public static readonly Clip Stunned = new(14, 2, 3f);
    public static readonly Clip Hurt = new(16, 1, 1f);
    public static readonly Clip Purified = new(17, 4, 5f);

    // Planche de côté (sylve_cote.png, tournée vers la gauche ; on la retourne pour la droite).
    public static readonly Clip SideWindup = new(0, 2, 6f);
    public static readonly Clip SideCharge = new(2, 4, 10f);

    /// <summary>Origine du cerf dans une case (bas-centre) : on pose ce point sur ses pieds.</summary>
    public const int OriginX = 48;
    public const int OriginY = 94;
    public const int CellSize = 96;

    // Centres des trois bulbes (gauche, milieu, droite) par case de face : idle 0-3, marche 4-7, préparation 8-9, touché 16.
    // Après la préparation et pendant la charge les bulbes ont disparu (phase 2) : les autres cases n'en ont pas besoin.
    private static readonly int[][] Bulbs =
    {
        new[] { 17, 10, 48, 10, 79, 10 }, // 0 idle0
        new[] { 17, 9, 48, 9, 79, 9 },    // 1
        new[] { 18, 8, 49, 8, 80, 8 },    // 2
        new[] { 18, 9, 49, 9, 80, 9 },    // 3
        new[] { 16, 9, 47, 9, 78, 9 },    // 4 marche0
        new[] { 17, 10, 48, 10, 79, 10 }, // 5
        new[] { 18, 9, 49, 9, 80, 9 },    // 6
        new[] { 17, 10, 48, 10, 79, 10 }, // 7
        new[] { 17, 33, 48, 33, 79, 33 }, // 8 prep0
        new[] { 18, 35, 49, 35, 80, 35 }, // 9 prep1
    };

    private static readonly int[] HurtBulbs = { 16, 8, 47, 8, 78, 8 };

    /// <summary>Position (x ou y) du centre du bulbe <paramref name="bulb"/> (0 à 2) dans la case <paramref name="frame"/>, ou -1 si la case n'en a pas.</summary>
    public static int BulbCoord(int frame, int bulb, bool y)
    {
        int[] data = frame >= 0 && frame < Bulbs.Length ? Bulbs[frame] : frame == Hurt.Start ? HurtBulbs : null;
        if (data == null || bulb < 0 || bulb > 2) return -1;
        return data[bulb * 2 + (y ? 1 : 0)];
    }
}
