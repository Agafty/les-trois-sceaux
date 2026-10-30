/// <summary>
/// Découpage des planches de Gorm (art/bosses/gorm/gorm.png et gorm_corruption.png : 17 colonnes x 3 lignes de 96x96 ;
/// ligne = état de l'armure, 0 plein, 1 brisé, 2 nu), recopié de gorm.json. Classe C# pure.
/// </summary>
public static class GormFrames
{
    public const int Columns = 17;
    public const int Rows = 3;
    public const int CellSize = 96;
    public const int OriginX = 48;
    public const int OriginY = 94;

    /// <summary>Une animation : première colonne, nombre de cases, images par seconde.</summary>
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

        /// <summary>Colonne à montrer après <paramref name="seconds"/> secondes (en boucle, ou figée sur la dernière).</summary>
        public int ColumnAt(float seconds, bool loop = true)
        {
            if (Count <= 1) return Start;
            int step = (int)(seconds * Fps);
            return Start + (loop ? step % Count : System.Math.Min(step, Count - 1));
        }
    }

    public static readonly Clip Idle = new(0, 2, 3f);
    public static readonly Clip Walk = new(2, 4, 6f);
    public static readonly Clip RaiseLow = new(6, 1, 1f);
    public static readonly Clip RaiseHigh = new(7, 1, 1f);
    public static readonly Clip Slam = new(8, 1, 1f);
    public static readonly Clip SlamEnd = new(9, 1, 1f);
    public static readonly Clip Hurt = new(10, 1, 1f);
    public static readonly Clip Stunned = new(11, 2, 3f);
    /// <summary>Seulement sur la ligne 2 (nu).</summary>
    public static readonly Clip Death = new(13, 4, 4f);
}
