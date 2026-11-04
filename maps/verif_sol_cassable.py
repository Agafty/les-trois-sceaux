#!/usr/bin/env python3
"""Verifie (et avec --apply corrige) le calque Sol sous les tuiles de Murs que le jeu peut retirer :
murs fissures/eboulis (TileRules.IsBreakable) et buissons (TileRules.IsBush).
Sol vide, solide, trou, ravin ou escalier -> remplace par la tuile de sol la plus frequente alentour (meme tileset).
Usage : python maps/verif_sol_cassable.py [--apply]   (stdlib seulement)"""
import re, sys, glob, os
import xml.etree.ElementTree as ET
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(ROOT, "tilesets")
APPLY = "--apply" in sys.argv
FLAGS = 0xE0000000

def breakable(ts, i):
    if ts == "village": return 136 <= i <= 139 or i == 142 or i == 300
    if ts in ("mine", "mine_sous_sol"): return 144 <= i <= 147 or i in (152, 164, 165) or 72 <= i <= 75
    if ts in ("sanctuaire", "sanctuaire_crypte", "route_chateau", "chateau"): return 72 <= i <= 75
    if ts == "montagne": return i in (156, 172, 203, 204) or 176 <= i <= 179
    if ts == "interieurs": return i == 67
    if ts == "foret": return 96 <= i <= 99
    return False

_cache = {}
def tsinfo(src):
    if src in _cache: return _cache[src]
    t = ET.parse(os.path.join(TS, os.path.basename(src))).getroot()
    solid = {int(x.get("id")) for x in t.findall("tile") if x.find("objectgroup") is not None}
    _cache[src] = (os.path.splitext(os.path.basename(src))[0], solid, int(t.get("tilecount")))
    return _cache[src]

def bad_floor(name, i, solid):
    if i in solid: return True
    if 58 <= i <= 66 and name.startswith("temple_racines"): return True
    if name in ("village", "montagne", "chateau") and 80 <= i <= 95: return True
    if i in (56, 57): return True
    if 31 <= i <= 39 and name.startswith("temple"): return True
    return False

def process(path):
    txt = open(path, encoding="utf-8").read()
    root = ET.fromstring(txt)
    W, H = int(root.get("width")), int(root.get("height"))
    sets = sorted((int(t.get("firstgid")), t.get("source")) for t in root.findall("tileset"))
    def resolve(g):
        g &= ~FLAGS
        for fg, src in reversed(sets):
            if g >= fg: return tsinfo(src), g - fg, fg
        return None, 0, 0
    layers = {l.get("name"): l for l in root.findall("layer")}
    if "Murs" not in layers or "Sol" not in layers: return []
    def grid(l):
        v = [int(x) for x in l.find("data").text.replace("\n", "").split(",") if x.strip() != ""]
        return v
    murs, sol = grid(layers["Murs"]), grid(layers["Sol"])
    out = []
    changes = {}
    for k, g in enumerate(murs):
        if not g: continue
        info, i, _ = resolve(g)
        if not info or not breakable(info[0], i): continue
        name, solid, _n = info
        s = sol[k]
        si, sid, sfg = resolve(s) if s else (None, 0, 0)
        ok = s != 0 and not bad_floor(si[0], sid, si[1])
        if ok: continue
        x, y = k % W, k // W
        best = None
        for r in range(1, 6):
            c = Counter()
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r: continue
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < W and 0 <= yy < H): continue
                    gg = sol[yy * W + xx]
                    if not gg or (yy * W + xx) in changes: continue
                    ni, nid, _ = resolve(gg)
                    if bad_floor(ni[0], nid, ni[1]): continue
                    c[gg & ~FLAGS] += 1 + (2 if abs(dx) + abs(dy) == 1 else 0) if r == 1 else 1
            if c:
                best = c.most_common(1)[0][0]; break
        out.append((x, y, name, i, s, best))
        if best is not None:
            changes[k] = best
    if APPLY and changes:
        for k, v in changes.items(): sol[k] = v
        rows = [",".join(str(v) for v in sol[r * W:(r + 1) * W]) for r in range(H)]
        body = ",\n".join(rows) + "\n"
        node = layers["Sol"]
        m = re.search(r'(<layer [^>]*name="Sol"[^>]*>\s*<data encoding="csv">\n)(.*?)(</data>)', txt, re.S)
        txt = txt[:m.start(2)] + body + txt[m.end(2):]
        open(path, "w", encoding="utf-8", newline="").write(txt)
    return out

total = 0
for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.tmx"), recursive=True)):
    res = process(p)
    for x, y, name, i, s, best in res:
        total += 1
        print(f"{os.path.relpath(p, ROOT)} ({x},{y}) {name} murs={i} sol_avant={s} -> {best}")
print(("corrigees" if APPLY else "a corriger"), total)
