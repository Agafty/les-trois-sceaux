#!/usr/bin/env python3
"""Recalcule les transitions de terrain (Wang par coins, comme le pinceau Terrains de Tiled) du calque Sol
des cartes d'overworld. Bibliotheque standard seulement.

Principe, pour chaque terrain (wangset) configure ci-dessous :
 - chaque case du calque Sol est classee : base (herbe/roche : couleur 1), terrain plein (couleur 2 aux 4 coins),
   transition du terrain (coins lus dans le wangset du .tsx) ou autre tuile (laissee intacte, jamais modifiee) ;
 - grille des sommets : un sommet vaut « terrain » si au moins une case voisine a ce coin en terrain
   (les coins existants sont donc conserves, rien ne se reduit) ;
 - chaque case de base ou de transition dont un coin est « terrain » recoit la tuile du wangset qui a exactement
   ces coins ; une case deja coherente (memes coins, ou tuile pleine) garde sa tuile : les variantes pleines
   ne sont jamais remplacees.
Ne touche ni Objets, ni Murs/Decor/Dessus, ni les cases dont le calque Murs porte un mur fissure, un eboulis
ou un buisson, ni une tuile a collision.
Usage : python maps/autotile_wang.py [--apply] [--show] [carte.tmx ...]   (sans --apply : simple rapport)"""
import re, sys, os, glob
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(ROOT, "tilesets")
FLAGS = 0xE0000000
APPLY = "--apply" in sys.argv
SHOW = "--show" in sys.argv

# tileset -> {wangset: tuiles pleines supplementaires (variantes, memes coins que la tuile pleine)}
TERRAINS = {
    "village": {"Paves": range(8, 15), "Terre": range(96, 102), "Rive": [64]},
    "foret": {"Eau": [40], "Chemin": []},
    "montagne": {"Sentier": [], "HerbeM": [], "Neige": [], "Ruisseau": [96]},
}
# tuiles de base (herbe / roche) par tileset : couleur 1 de tous les terrains ci-dessus
BASE = {"village": range(0, 8), "foret": list(range(0, 9)) + [24], "montagne": range(0, 14),
        "lac": [64, 65]}   # lac : herbe d'ilot
# variantes « eau peu profonde » d'autres tilesets, pleines pour les terrains Rive / Eau
WATER_EXTRA = {"lac": [7, 70]}

_ts = {}
def load_ts(src):
    name = os.path.splitext(os.path.basename(src))[0]
    if name in _ts: return _ts[name]
    r = ET.parse(os.path.join(TS, name + ".tsx")).getroot()
    solid = {int(t.get("id")) for t in r.findall("tile") if t.find("objectgroup") is not None}
    ws = {}
    for w in r.iter("wangset"):
        if w.get("type") != "corner": continue
        tiles = {}
        for t in w.findall("wangtile"):
            v = [int(x) for x in t.get("wangid").split(",")]
            tiles[int(t.get("tileid"))] = (v[7], v[1], v[5], v[3])   # HG, HD, BG, BD
        ws[w.get("name")] = tiles
    _ts[name] = (name, solid, ws)
    return _ts[name]

def breakable(ts, i):
    if ts == "village": return 136 <= i <= 139 or i == 142 or i == 300
    if ts == "montagne": return i in (156, 172, 203, 204) or 176 <= i <= 179
    if ts == "foret": return 96 <= i <= 99
    if ts in ("route_chateau", "chateau"): return 72 <= i <= 75
    return False

def read(txt, name):
    m = re.search(r'<layer [^>]*name="%s"[^>]*>\s*<data encoding="csv">\n(.*?)</data>' % name, txt, re.S)
    return m, [int(x) for x in m.group(1).replace("\n", "").split(",") if x.strip() != ""]

def process(path):
    txt = open(path, encoding="utf-8").read()
    root = ET.fromstring(txt)
    W, H = int(root.get("width")), int(root.get("height"))
    sets = sorted((int(t.get("firstgid")), load_ts(t.get("source"))) for t in root.findall("tileset"))

    def resolve(g):
        g &= ~FLAGS
        for fg, info in reversed(sets):
            if g >= fg: return info[0], g - fg
        return None, 0

    msol, sol = read(txt, "Sol")
    _, murs = read(txt, "Murs")
    orig = list(sol)
    base = set()
    for fg, info in sets:
        base |= {fg + i for i in BASE.get(info[0], [])}
    frozen = set()
    for k, g in enumerate(murs):
        if g and breakable(*resolve(g)): frozen.add(k)
    log = []
    for fg, (name, solid, ws) in sets:
        for wname, extra in TERRAINS.get(name, {}).items():
            if wname not in ws: continue
            tiles = ws[wname]
            full_tile = next(i for i, c in tiles.items() if c == (2, 2, 2, 2))
            bygrid = {}
            for i, c in tiles.items():
                if c != (1, 1, 1, 1): bygrid.setdefault(c, i)
            fullgids = {fg + full_tile} | {fg + i for i in extra}
            if wname in ("Rive", "Eau"):
                for fg2, info2 in sets:
                    fullgids |= {fg2 + i for i in WATER_EXTRA.get(info2[0], [])}

            def corners(k):
                g = sol[k] & ~FLAGS
                if g in fullgids: return (2, 2, 2, 2), "full"
                if g:
                    n, i = resolve(g)
                    if n == name and i in tiles and i != full_tile:
                        c = tiles[i]
                        return c, ("base" if c == (1, 1, 1, 1) else "trans")
                if g in base: return (1, 1, 1, 1), "base"
                return None, "other"

            V = [[1] * (W + 1) for _ in range(H + 1)]
            cls = {}
            anyt = False
            for k in range(W * H):
                c, kind = corners(k)
                cls[k] = (c, kind)
                if c is None: continue
                x, y = k % W, k // W
                for (dx, dy), v in zip(((0, 0), (1, 0), (0, 1), (1, 1)), c):
                    if v == 2: V[y + dy][x + dx] = 2; anyt = True
            if not anyt: continue
            for k in range(W * H):
                c, kind = cls[k]
                if c is None or kind == "full": continue
                x, y = k % W, k // W
                want = (V[y][x], V[y][x + 1], V[y + 1][x], V[y + 1][x + 1])
                if want == c: continue
                if k in frozen:
                    log.append((x, y, wname, "gele (mur fissure/buisson)")); continue
                new_local = full_tile if want == (2, 2, 2, 2) else bygrid[want]
                if new_local in solid:
                    log.append((x, y, wname, "collision, ignore")); continue
                sol[k] = fg + new_local
            # signale les tuiles non classees (autre terrain, decor de sol) touchees par un sommet terrain
            for k in range(W * H):
                if cls[k][1] != "other" or not orig[k] or sol[k] != orig[k]: continue
                x, y = k % W, k // W
                if any(V[y + dy][x + dx] == 2 for dx in (0, 1) for dy in (0, 1)):
                    n, i = resolve(orig[k])
                    log.append((x, y, wname, "voisine non classee %s %d" % (n, i)))
    changed = [(k % W, k // W, orig[k] & ~FLAGS, sol[k]) for k in range(W * H) if sol[k] != orig[k]]
    if APPLY and changed:
        rows = [",".join(str(v) for v in sol[r * W:(r + 1) * W]) for r in range(H)]
        txt = txt[:msol.start(1)] + ",\n".join(rows) + "\n" + txt[msol.end(1):]
        open(path, "w", encoding="utf-8", newline="").write(txt)
    return W, H, orig, sol, changed, log, resolve


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = args or sorted(glob.glob(os.path.join(ROOT, "overworld", "*.tmx")))
    tot = 0
    for p in files:
        W, H, orig, sol, changed, log, resolve = process(p)
        tot += len(changed)
        c = Counter(resolve(b)[0] for _x, _y, _a, b in changed)
        print(f"{os.path.relpath(p, ROOT)} : {len(changed)} cases changees", dict(c))
        for l in sorted(set(log)): print("   ", l)
        if SHOW:
            for y in range(H):
                print("   " + " ".join(("%3d" % resolve(sol[y * W + x])[1] if sol[y * W + x] else "  .")
                                       + ("*" if sol[y * W + x] != orig[y * W + x] else " ") for x in range(W)))
    print("total", tot, "(applique)" if APPLY else "(simulation)")
