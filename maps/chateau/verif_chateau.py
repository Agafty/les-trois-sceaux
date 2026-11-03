"""Verification des cartes de la fin : route, grotte, cour, salles du chateau.

Bibliotheque standard seulement. Usage : python maps/chateau/verif_chateau.py [--apercu]

Controle : tailles, calques, GID/tilesets, ids uniques, raccords Sortie <-> Spawn dans les deux sens,
ennemis a 3 cases ou plus d'un Spawn, accessibilite (parcours sur l'etat : murs a rune, murs fissures,
portes ennemis/interrupteur/grande cle, coffre), lignes de tir de l'arc, rectangles Porte/Sortie.
"""
import os
import sys
import math
import xml.etree.ElementTree as ET
from collections import deque

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAPS = {
    "route_falaise": ("maps/overworld/route_falaise.tmx", (40, 11)),
    "passage_falaise": ("maps/interieurs/passage_falaise.tmx", (20, 22)),
    "chateau": ("maps/overworld/chateau.tmx", (20, 22)),
    "chateau_salle_01": ("maps/chateau/salle_01.tmx", (20, 11)),
    "chateau_salle_02": ("maps/chateau/salle_02.tmx", (20, 11)),
    "chateau_salle_03": ("maps/chateau/salle_03.tmx", (20, 11)),
    "chateau_salle_04": ("maps/chateau/salle_04.tmx", (20, 11)),
    "chateau_salle_boss": ("maps/chateau/salle_boss.tmx", (20, 22)),
    # cartes existantes, controlees seulement pour les raccords
    "village": ("maps/overworld/village.tmx", None),
    "forge": ("maps/interieurs/forge.tmx", None),
}
SCENE_TO_MAP = {k: k for k in MAPS}
SCENE_TO_MAP["lac"] = None
LAYERS = ["Sol", "Decor", "Murs", "Objets", "Dessus"]
EMPTY_IDS = {"route_chateau": set(range(31, 40)) | set(range(58, 67)) | set(range(80, 96)),
             "chateau": set(range(31, 40)) | set(range(58, 67))}
RAVINE = {"chateau": set(range(81, 96))}   # fosse de ronces : infranchissable, les fleches passent
SOLID_AREA = 450
errors, warns = [], []


def err(m): errors.append(m); print("  ERREUR :", m)
def ok(m): print("  ok :", m)


def load_tsx(path):
    t = ET.parse(path).getroot()
    areas = {}
    for tile in t.findall("tile"):
        a = 0
        for o in tile.iter("object"):
            a += float(o.get("width", 0)) * float(o.get("height", 0))
        areas[int(tile.get("id"))] = a
    return t.get("name"), int(t.get("tilecount")), areas


class Level:
    def __init__(s, key):
        path, size = MAPS[key]
        s.key, s.path, s.size = key, os.path.join(ROOT, path), size
        r = ET.parse(s.path).getroot()
        s.root = r
        s.w, s.h = int(r.get("width")), int(r.get("height"))
        s.props = {p.get("name"): p.get("value") for p in r.findall("properties/property")}
        s.tilesets = [(int(ts.get("firstgid")), ts.get("source")) for ts in r.findall("tileset")]
        s.layers = {}
        for l in r.findall("layer"):
            data = [int(v) for v in l.find("data").text.replace("\n", "").split(",") if v.strip() != ""]
            s.layers[l.get("name")] = data
        s.layer_order = [e.get("name") for e in r if e.tag in ("layer", "objectgroup")]
        s.objs = []
        for o in r.find("objectgroup").findall("object"):
            d = dict(id=int(o.get("id")), cls=o.get("type"), name=o.get("name"), x=float(o.get("x")), y=float(o.get("y")),
                     w=float(o.get("width", 0)), h=float(o.get("height", 0)), point=o.find("point") is not None,
                     p={p.get("name"): p.get("value") for p in o.findall("properties/property")})
            s.objs.append(d)
        s.nextobj = int(r.get("nextobjectid"))
        tn, tc, areas = load_tsx(os.path.join(os.path.dirname(s.path), s.tilesets[0][1])) if s.tilesets else (None, 0, {})
        s.tsname, s.tcount, s.areas = tn, tc, areas

    def tid(s, layer, x, y):
        g = s.layers[layer][y * s.w + x]
        return (g & 0x0FFFFFFF) - 1

    def cells(s, o):
        if o["point"]:
            return [(int(o["x"] // 32), int(o["y"] // 32))]
        return [(cx, cy) for cy in range(int(o["y"] // 32), int((o["y"] + o["h"] - 1) // 32) + 1)
                for cx in range(int(o["x"] // 32), int((o["x"] + o["w"] - 1) // 32) + 1)]

    def tile_solid(s, x, y):
        t = s.tid("Murs", x, y)
        if t < 0:
            return False
        return s.areas.get(t, 0) >= SOLID_AREA or t in RAVINE.get(s.tsname, ())

    def tile_arrow_solid(s, x, y):
        t = s.tid("Murs", x, y)
        return t >= 0 and s.areas.get(t, 0) >= SOLID_AREA and t not in RAVINE.get(s.tsname, ())


def check_file(L):
    print("[%s] %dx%d" % (L.key, L.w, L.h))
    if L.size and (L.w, L.h) != L.size:
        err("%s : taille %dx%d au lieu de %s" % (L.key, L.w, L.h, L.size))
    else:
        ok("taille")
    if L.layer_order != LAYERS:
        err("ordre des calques %s" % L.layer_order)
    for n, d in L.layers.items():
        if len(d) != L.w * L.h:
            err("calque %s : %d valeurs" % (n, len(d)))
    ids = [o["id"] for o in L.objs]
    if len(ids) != len(set(ids)):
        err("ids d'objets dupliques")
    if L.nextobj <= max(ids):
        err("nextobjectid trop petit")
    # GID / tuiles
    bad = set()
    for n, d in L.layers.items():
        for i, v in enumerate(d):
            g = v & 0x0FFFFFFF
            if g == 0:
                continue
            t = g - 1
            if t >= L.tcount:
                bad.add((n, t, "hors tileset"))
            elif t in EMPTY_IDS.get(L.tsname, ()) and not (t in RAVINE.get(L.tsname, ()) or t == 80):
                bad.add((n, t, "id reserve vide"))
            else:
                a = L.areas.get(t, 0)
                if n in ("Sol", "Decor", "Dessus") and a > 0:
                    bad.add((n, t, "collision sur un calque sans collision"))
                if n == "Murs" and a == 0:
                    bad.add((n, t, "pas de collision sur Murs"))
    if L.tsname in RAVINE:
        pass
    for b in sorted(bad):
        err("%s tuile %d : %s" % b)
    if not bad:
        ok("GID : toutes les tuiles existent dans %s (%d tuiles), calques coherents" % (L.tsname, L.tcount))
    # props
    names = {o["p"].get("id") for o in L.objs if o["p"].get("id")}
    for o in L.objs:
        if o["cls"] in ("Sortie", "Indice") or (o["name"] or "").startswith("indice"):
            if o["p"].get("godot_node_type") != "area":
                err("objet %d sans godot_node_type=area" % o["id"])
    pid = [o["p"]["id"] for o in L.objs if o["p"].get("id") and o["cls"] not in ("Porte",)]
    dup = {i for i in pid if pid.count(i) > 1}
    if dup:
        err("ids de gameplay dupliques dans la carte : %s" % dup)


def build_grid(L, state):
    """Cases franchissables selon l'etat (portes / murs ouverts)."""
    solid = [[L.tile_solid(x, y) for x in range(L.w)] for y in range(L.h)]
    arrow = [[L.tile_arrow_solid(x, y) for x in range(L.w)] for y in range(L.h)]
    for o in L.objs:
        c = L.cells(o)
        if o["cls"] == "MurFissure":
            for (x, y) in c:
                if o["p"]["id"] in state:
                    solid[y][x] = arrow[y][x] = False
                else:
                    solid[y][x] = arrow[y][x] = True
        elif o["cls"] == "Porte":
            for (x, y) in c:
                if o["p"]["id"] in state:
                    continue
                solid[y][x] = arrow[y][x] = True
        elif o["cls"] in ("Coffre", "StatueCorbeau", "Interrupteur", "Torche"):
            for (x, y) in c:
                solid[y][x] = True
                if o["cls"] != "Torche":
                    arrow[y][x] = True
    return solid, arrow


def reach(L, solid, seeds):
    seen = set()
    q = deque()
    for s in seeds:
        if not solid[s[1]][s[0]]:
            seen.add(s); q.append(s)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < L.w and 0 <= ny < L.h and (nx, ny) not in seen and not solid[ny][nx]:
                seen.add((nx, ny)); q.append((nx, ny))
    return seen


def adjacent(reachset, cell):
    x, y = cell
    return any((x + dx, y + dy) in reachset for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def arrow_line(L, arrow, reachset, cell, maxd=10):
    x, y = cell
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for d in range(1, maxd + 1):
            nx, ny = x + dx * d, y + dy * d
            if not (0 <= nx < L.w and 0 <= ny < L.h) or arrow[ny][nx]:
                break
            if (nx, ny) in reachset:
                return True
    return False


def spawn_cell(o):
    return (int(o["x"] // 32), int(o["y"] // 32))


def main():
    apercu = "--apercu" in sys.argv
    levels = {k: Level(k) for k in MAPS}
    for k, L in levels.items():
        if k in ("village", "forge"):
            continue
        check_file(L)

    print("[raccords]")
    spawns = {k: {o["p"]["id"]: o for o in L.objs if o["cls"] == "Spawn"} for k, L in levels.items()}
    sorties = {k: [o for o in L.objs if o["cls"] == "Sortie"] for k, L in levels.items()}
    for k, L in levels.items():
        for so in sorties[k]:
            sc = so["p"]["cible_carte"]
            name = os.path.basename(sc).replace("_room.tscn", "")
            if name not in levels:
                continue
            sp = so["p"]["cible_spawn"]
            if sp not in spawns[name]:
                err("%s -> %s : Spawn %s introuvable" % (k, name, sp))
                continue
            back = [b for b in sorties[name] if os.path.basename(b["p"]["cible_carte"]).replace("_room.tscn", "") == k]
            if k in ("village", "forge") or name in ("village", "forge"):
                ok("%s -> %s / %s (Spawn existe)" % (k, name, sp))
                continue
            if not back:
                err("%s -> %s : aucune Sortie retour" % (k, name))
            else:
                bsp = back[0]["p"]["cible_spawn"]
                if bsp not in spawns[k]:
                    err("%s : Spawn retour %s manquant" % (k, bsp))
                else:
                    ok("%s <-> %s : %s / %s" % (k, name, sp, bsp))
    # Sortie village -> route et Spawn depuis_route
    if "depuis_route" in spawns["village"] and any("route_falaise" in s["p"]["cible_carte"] for s in sorties["village"]):
        ok("village : Sortie vers route_falaise et Spawn depuis_route presents")
    else:
        err("village : raccord vers route_falaise incomplet")
    if "depuis_chateau" in spawns["forge"]:
        ok("forge : Spawn depuis_chateau present")
    else:
        err("forge : Spawn depuis_chateau absent")

    print("[portes et sorties]")
    allportes = {}
    for k, L in levels.items():
        for o in L.objs:
            if o["cls"] == "Porte":
                allportes.setdefault(o["p"]["id"], []).append((k, o))
    for pid, lst in allportes.items():
        if not pid.startswith(("chateau_", "route_")):
            continue
        typ = {o["p"].get("type") for _, o in lst}
        if len(typ) != 1:
            err("porte %s : types differents %s" % (pid, typ))
        if "lanterne" in typ or "interrupteur" in typ:
            if len(lst) != 1:
                err("porte %s : %d faces" % (pid, len(lst)))
            continue
        if len(lst) != 2:
            err("porte %s : %d faces au lieu de 2" % (pid, len(lst)))
        for k, o in lst:
            L = levels[k]
            if not any((s["x"], s["y"], s["w"], s["h"]) == (o["x"], o["y"], o["w"], o["h"]) for s in sorties[k]):
                err("porte %s (%s) sans Sortie de meme rectangle" % (pid, k))
    ok("portes verifiees : %s" % ", ".join(sorted(p for p in allportes if p.startswith(("chateau_", "route_")))))

    print("[ennemis / spawns]")
    for k, L in levels.items():
        if k in ("village", "forge"):
            continue
        for e in [o for o in L.objs if o["cls"] == "Ennemi"]:
            for s in [o for o in L.objs if o["cls"] == "Spawn"]:
                d = math.hypot(e["x"] - s["x"], e["y"] - s["y"]) / 32.0
                if d < 3:
                    err("%s : ennemi %s a %.1f cases du Spawn %s" % (k, e["p"]["type"], d, s["p"]["id"]))
        for s in [o for o in L.objs if o["cls"] == "Spawn"]:
            c = spawn_cell(s)
            for o in L.objs:
                if o["cls"] in ("Sortie", "Porte") and c in L.cells(o):
                    err("%s : Spawn %s sur une %s" % (k, s["p"]["id"], o["cls"]))
            if L.tile_solid(*c):
                err("%s : Spawn %s dans un mur" % (k, s["p"]["id"]))
    ok("controle termine")

    # --- parcours global sur l'etat ---
    print("[parcours sur l'etat : objets Brann = epee, arc, bombes, lanterne ; 0 petite clef, 1 grande clef]")
    lvl = [k for k in MAPS if k not in ("village", "forge")]
    state = set()
    reachsets = {k: set() for k in lvl}
    seeds = {k: set() for k in lvl}
    seeds["route_falaise"].add(spawn_cell(spawns["route_falaise"]["depuis_village"]))
    got_key = False
    killed_doors = set()
    changed = True
    log = []
    while changed:
        changed = False
        grids = {}
        for k in lvl:
            solid, arrow = build_grid(levels[k], state)
            grids[k] = (solid, arrow)
            rs = reach(levels[k], solid, seeds[k])
            if rs != reachsets[k]:
                reachsets[k] = rs; changed = True
        # sorties -> spawns
        for k in lvl:
            L = levels[k]
            for so in sorties[k]:
                name = os.path.basename(so["p"]["cible_carte"]).replace("_room.tscn", "")
                if name not in seeds:
                    continue
                if any(c in reachsets[k] for c in L.cells(so)):
                    c = spawn_cell(spawns[name][so["p"]["cible_spawn"]])
                    if c not in seeds[name]:
                        seeds[name].add(c); changed = True
        # ouvertures
        for k in lvl:
            L = levels[k]
            rs = reachsets[k]
            solid, arrow = grids[k]
            for o in L.objs:
                cl = o["cls"]
                if cl == "MurFissure" and o["p"]["id"] not in state:
                    if any(adjacent(rs, c) for c in L.cells(o)):
                        state.add(o["p"]["id"]); changed = True; log.append("bombe : %s" % o["p"]["id"])
                if cl == "Porte" and o["p"]["id"] not in state:
                    typ = o["p"].get("type")
                    if typ == "lanterne":
                        cx, cy = o["x"] + o["w"] / 2, o["y"] + o["h"] / 2
                        if any(math.hypot(x * 32 + 16 - cx, y * 32 + 16 - cy) <= 64 for (x, y) in rs):
                            state.add(o["p"]["id"]); changed = True; log.append("lanterne : %s" % o["p"]["id"])
                    elif typ == "grande_cle" and got_key:
                        if any(adjacent(rs, c) for c in L.cells(o)):
                            state.add(o["p"]["id"]); changed = True; log.append("grande clef : %s" % o["p"]["id"])
                    elif typ == "ennemis":
                        allk = True
                        for e in [q for q in L.objs if q["cls"] == "Ennemi"]:
                            c = spawn_cell(e)
                            if L.tile_solid(*c) or L.tile_arrow_solid(*c):   # dans un mur : seulement a l'arc
                                okk = arrow_line(L, arrow, rs, c)
                            else:
                                okk = c in rs
                            if not okk:
                                allk = False
                        if allk and any(adjacent(rs, c) for c in L.cells(o)):
                            state.add(o["p"]["id"]); changed = True; log.append("ennemis vaincus : %s" % o["p"]["id"])
                    elif typ == "interrupteur":
                        sw = [(kk, q) for kk, LL in levels.items() if kk in lvl for q in LL.objs if q["cls"] == "Interrupteur" and q["p"]["cible"] == o["p"]["id"]]
                        allsw = True
                        for kk, q in sw:
                            c = spawn_cell(q)
                            rr = reachsets[kk]
                            if q["p"]["mode"] == "fleche":
                                okk = arrow_line(levels[kk], grids[kk][1], rr, c)
                            else:
                                okk = adjacent(rr, c)
                            if not okk:
                                allsw = False
                        if allsw and sw:
                            state.add(o["p"]["id"]); changed = True; log.append("interrupteurs (%d) : %s" % (len(sw), o["p"]["id"]))
                if cl == "Coffre" and o["p"]["contenu"] == "grande_cle" and not got_key:
                    if adjacent(rs, spawn_cell(o)):
                        got_key = True; changed = True; log.append("grande clef obtenue (%s)" % o["p"]["id"])
    for l in log:
        print("  -", l)
    needed_doors = {p for p in allportes if p.startswith(("chateau_", "route_")) and p not in ("route_porte_03",)}
    missing = needed_doors - state
    if missing:
        err("portes jamais ouvertes : %s" % sorted(missing))
    else:
        ok("toutes les portes/murs obligatoires s'ouvrent dans la chaine (route_porte_03 : plume, facultatif, ouverte : %s)" % ("route_porte_03" in state))
    bossL = levels["chateau_salle_boss"]
    bm = [o for o in bossL.objs if o["name"] == "boss_corvan"][0]
    if spawn_cell(bm) in reachsets["chateau_salle_boss"]:
        ok("salle du boss atteignable ; Corvan atteignable")
    else:
        err("boss inatteignable")
    for pm in [o for o in bossL.objs if o["cls"] == "Marqueur"]:
        if spawn_cell(pm) not in reachsets["chateau_salle_boss"]:
            err("Marqueur %s inatteignable" % pm["p"]["id"])
    # tous les objets interessants atteignables (cases libres) ou approchables (objets solides)
    for k in lvl:
        L = levels[k]
        rs = reachsets[k]
        solid, arrow = build_grid(L, state)
        for o in L.objs:
            if o["cls"] in ("Ennemi",):
                c = spawn_cell(o)
                if (L.tile_solid(*c)):
                    if not arrow_line(L, arrow, rs, c) and not adjacent(rs, c):
                        err("%s : ennemi en mur %s hors de portee" % (k, c))
                elif c not in rs:
                    err("%s : ennemi %s en %s inatteignable" % (k, o["p"]["type"], c))
            if o["cls"] in ("Coffre", "StatueCorbeau", "Interrupteur", "Ramassable", "Torche"):
                c = spawn_cell(o)
                if not (c in rs or adjacent(rs, c)):
                    err("%s : %s %s inatteignable" % (k, o["cls"], o["p"].get("id")))
            if o["cls"] == "Sortie":
                if not any(c in rs for c in L.cells(o)):
                    err("%s : Sortie vers %s inatteignable" % (k, o["p"]["cible_carte"]))
            if o["cls"] == "Spawn" and spawn_cell(o) not in rs:
                err("%s : Spawn %s hors zone atteignable" % (k, o["p"]["id"]))
    ok("objets, ennemis et Sorties atteignables apres ouverture dans l'ordre de la chaine")

    # --- fermeture : rien n'est atteignable trop tot ---
    print("[blocages : ce qui doit rester ferme]")
    s0 = set()
    sg, ag = build_grid(levels["passage_falaise"], s0)
    rs = reach(levels["passage_falaise"], sg, {spawn_cell(spawns["passage_falaise"]["depuis_route"])})
    north = [o for o in sorties["passage_falaise"] if "chateau_room" in o["p"]["cible_carte"]][0]
    if any(c in rs for c in levels["passage_falaise"].cells(north)):
        err("passage : le nord est atteignable sans lanterne")
    else:
        ok("passage : nord ferme tant que route_porte_02 est fermee")
    plume = [o for o in levels["passage_falaise"].objs if o["cls"] == "Ramassable"][0]
    sg2, ag2 = build_grid(levels["passage_falaise"], {"route_porte_02"})
    rs2 = reach(levels["passage_falaise"], sg2, {spawn_cell(spawns["passage_falaise"]["depuis_route"])})
    if spawn_cell(plume) in rs2 or adjacent(rs2, spawn_cell(plume)) and spawn_cell(plume) in rs2:
        err("plume atteignable sans route_porte_03")
    else:
        ok("plume fermee tant que route_porte_03 est fermee")
    L3 = levels["chateau_salle_03"]
    sg, ag = build_grid(L3, set())
    rs = reach(L3, sg, {spawn_cell(spawns["chateau_salle_03"]["depuis_sud"])})
    for o in L3.objs:
        if o["cls"] == "Coffre" or (o["cls"] == "Interrupteur" and o["p"]["mode"] == "epee"):
            if adjacent(rs, spawn_cell(o)):
                err("salle_03 : %s approchable avant ouverture" % o["p"]["id"])
    ok("salle_03 : coffre et leviers fermes avant la grille / le mur / la rune")
    cible = [o for o in L3.objs if o["cls"] == "Interrupteur" and o["p"]["mode"] == "fleche"][0]
    c = spawn_cell(cible)
    line = [d for d in range(1, 11) if (c[0] + d, c[1]) in rs and all(not ag[c[1]][c[0] + e] for e in range(1, d + 1))]
    if line:
        ok("salle_03 : cible tirable depuis %d cases (1 a %d)" % (len(line), max(line)))
    else:
        err("salle_03 : cible sans ligne de tir")
    L1 = levels["chateau_salle_01"]
    sg, ag = build_grid(L1, set())
    rs = reach(L1, sg, {spawn_cell(spawns["chateau_salle_01"]["depuis_cour"])})
    for e in [o for o in L1.objs if o["cls"] == "Ennemi"]:
        c = spawn_cell(e)
        dmin = min(math.hypot(x - c[0], y - c[1]) for (x, y) in rs)
        shots = arrow_line(L1, ag, rs, c)
        far = [d for d in range(1, 11) if (c[0], c[1] + d) in rs and all(not ag[c[1] + k][c[0]] for k in range(1, d + 1))]
        if dmin < 3.0 or not shots:
            err("salle_01 : Oeil %s : case atteignable la plus proche %.1f, tir possible %s" % (c, dmin, shots))
        else:
            ok("salle_01 : Oeil %s : plus proche case a %.1f cases (hors epee), tir de %d a %d cases" % (c, dmin, min(far), max(far)))

    if apercu:
        for k in lvl:
            L = levels[k]
            print("--- %s ---" % k)
            solid, arrow = build_grid(L, set())
            mark = {}
            for o in L.objs:
                ch = {"Spawn": "P", "Sortie": "X", "Ennemi": "E", "Coffre": "C", "Porte": "D", "Interrupteur": "S", "StatueCorbeau": "R",
                      "Torche": "Y", "MurFissure": "F", "Ramassable": "f", "Marqueur": "m", "Scenario": "s"}.get(o["cls"])
                if o["name"] == "boss_corvan":
                    ch = "g"
                if o["name"] == "pilier" or (o["name"] or "").startswith("indice"):
                    continue
                if ch is None:
                    continue
                for c in L.cells(o):
                    if o["cls"] == "Sortie" and c in mark:
                        continue
                    mark[c] = ch
            for y in range(L.h):
                row = ""
                for x in range(L.w):
                    if (x, y) in mark:
                        row += mark[(x, y)]
                    elif L.tid("Murs", x, y) in RAVINE.get(L.tsname, ()) and L.tid("Murs", x, y) >= 0:
                        row += "~"
                    elif solid[y][x]:
                        row += "#"
                    else:
                        row += "."
                print(row)
    print()
    if errors:
        print("%d ERREUR(S)" % len(errors))
        sys.exit(1)
    print("TOUT EST OK")


if __name__ == "__main__":
    main()
