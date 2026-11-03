"""Corvan vieux (epilogue) 32x32 : cheveux blancs, gilet bleu a la place du tablier, sans corruption - Les Trois Sceaux.
Usage : python tools/sprites/corvan_vieux.py   -> art/characters/corvan_vieux.png (160x128, comme corvan.png),
corvan_vieux.json, corvan_vieux_frames.tres (idle_* et walk_*). Meme gabarit que corvan.py (grilles reprises).
Sans Pillow : PIL est remplace par un module vide, seul le calcul des images d'engine.py sert."""
import json
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules.setdefault('PIL', types.ModuleType('PIL'))
sys.modules['PIL'].Image = types.ModuleType('PIL.Image')
sys.modules['PIL.Image'] = sys.modules['PIL'].Image
import engine  # noqa: E402
import corvan  # noqa: E402
from tsplan import save_png, ROOT  # noqa: E402

OUT = os.path.join(ROOT, 'art', 'characters')

REMAP = {
    '6': '#6a88a8', 'B': '#486684', 'D': '#2e4260',      # gilet bleu, ceinture
    '2': '#e8e0cc', '9': '#bcb29a',                       # chemise claire
    'g': '#f6f4f0', 'h': '#c4c0b8',                       # cheveux et barbe blancs
}


def whiten(rows, y0, y1, x0=0):
    out = []
    for y, r in enumerate(rows):
        if y0 <= y <= y1:
            r = r[:x0] + r[x0:].replace('3', 'g')
        out.append(r)
    return out


def views():
    d = whiten(corvan.DOWN, 2, 4)
    d = [r.replace('3', '3') for r in d]
    u = whiten(corvan.UP, 2, 8)
    l = whiten(corvan.LEFT, 1, 4)
    # une meche sur le front (face) : rangee 5 = ligne de cheveux
    d[5] = d[5].replace('3333333', 'gggg333', 1) if d[5].endswith('3333333') else d[5]
    return {'down': d, 'up': u, 'left': l}


def main():
    v = views()
    g = {'down': engine.grid(v['down'], half=True), 'up': engine.grid(v['up'], half=True), 'left': engine.grid(v['left'])}
    rows = engine.frames_for(g, corvan.HIP, corvan.LEGMID, corvan.HIP_SIDE)
    pal = dict(engine.PALETTE)
    pal.update(REMAP)
    px = [[None] * 160 for _ in range(128)]
    for r, frames in enumerate(rows):
        for c, gr in enumerate(frames):
            for y in range(32):
                for x in range(32):
                    col = pal[gr[y][x]]
                    if col:
                        px[r * 32 + y][c * 32 + x] = engine.rgba(col)
    save_png(os.path.join(OUT, 'corvan_vieux.png'), px)
    engine.write_tres('corvan_vieux', OUT)
    print('ok')


if __name__ == '__main__':
    main()
