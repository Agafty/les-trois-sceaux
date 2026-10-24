#!/usr/bin/env python3
"""Vérification du Temple des Racines (donjon 1) - bibliothèque standard uniquement.

Usage :  python verif_donjon.py [chemin/vers/plan.md]

Lit les aperçus ASCII de plan.md (blocs "<!-- salle_XX -->" suivis d'un bloc ```text```) et :
  1. contrôle la forme des salles et la cohérence avec les tables ci-dessous (portes, coffres, cibles) ;
  2. fait un parcours sur l'ÉTAT du joueur (salle, petites clés, portes ouvertes, coffres ouverts,
     interrupteurs touchés, salles nettoyées, objets) et prouve que la salle du boss est atteignable
     depuis TOUS les états atteignables, donc quel que soit l'ordre d'ouverture des portes ;
  3. explore tous les états de chaque bloc poussable (Sokoban) et vérifie que Brann peut toujours
     ressortir par où il est entré (sinon : sortir/revenir remet le bloc en place, mais on le signale) ;
  4. lance un auto-test (retirer une clé doit rendre le boss inatteignable).

Hypothèses de jeu (voir plan.md) : Brann marche sur une grille de cases (4 voisins, estimation prudente) ;
un coffre s'ouvre depuis une case voisine ; une porte à clé s'ouvre depuis la case devant elle ;
la flèche vole en ligne droite sur au plus PORTEE_CASES cases et s'arrête sur un mur, un pilier, un bloc,
une porte fermée ; les flèches ne manquent pas (voir « Risques » dans plan.md) ; une porte `ennemis`
s'ouvre quand la salle est nettoyée (impossible tant qu'il reste un Lutin et qu'on n'a pas l'arc).
"""
import re
import sys
from collections import deque
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# --- Constantes de jeu (lues dans player.tscn, Arrow.cs, arc.tres) -----------------------------------------
BRANN_LARGEUR_PX, BRANN_HAUTEUR_PX = 16, 20      # capsule rayon 8, hauteur 20
PASSAGE_PORTE_VERTICALE_PX = 20                  # porte_haut / porte_bas (Brann : 16 de large)
PASSAGE_PORTE_HORIZONTALE_PX = 24                # porte_gauche / porte_droite (Brann : 20 de haut)
PORTEE_FLECHE_PX = 320                           # Arrow.MaxDistance (+ 20 px de décalage initial)
PORTEE_CASES = 9                                 # 9 cases = 288 px : marge de sécurité

# --- Tables (doivent correspondre aux aperçus de plan.md) ---------------------------------------------------
# id -> (type, côté A, côté B).  Un côté = (salle, "N|S|E|O") ou (salle, (col, ligne)) pour une porte intérieure.
PORTES = {
    "donjon1_porte_01": ("D", ("salle_02", "N"), ("salle_06", "S")),
    "donjon1_porte_02": ("N", ("salle_04", "E"), ("salle_05", "O")),
    "donjon1_porte_03": ("I", ("salle_06", "E"), ("salle_07", "O")),
    "donjon1_porte_04": ("D", ("salle_07", "E"), ("salle_08", "O")),
    "donjon1_porte_05": ("N", ("salle_08", "N"), ("salle_09", "S")),
    "donjon1_porte_06": ("I", ("salle_09", (15, 4)), None),
    "donjon1_porte_07": ("G", ("salle_09", "N"), ("salle_boss", "S")),
}
# Passages libres (caractère X) : ((salle, côté), (salle, côté)) ; "foret" = sortie vers l'overworld
LIENS_LIBRES = [
    (("salle_01", "S"), "foret"),
    (("salle_01", "N"), ("salle_02", "S")),
    (("salle_02", "O"), ("salle_03", "E")),
    (("salle_02", "E"), ("salle_04", "O")),
]
COFFRES = {  # id -> (salle, (col, ligne), contenu)
    "donjon1_coffre_01": ("salle_02", (15, 2), "carte_donjon"),
    "donjon1_coffre_02": ("salle_04", (15, 2), "boussole"),
    "donjon1_coffre_03": ("salle_05", (9, 2), "cle_petite"),
    "donjon1_coffre_04": ("salle_06", (6, 2), "objet_arc"),
    "donjon1_coffre_05": ("salle_07", (17, 2), "cle_petite"),
    "donjon1_coffre_06": ("salle_09", (16, 2), "grande_cle"),
}
INTERRUPTEURS = {  # id -> (salle, (col, ligne), id de la porte ouverte)
    "donjon1_interrupteur_01": ("salle_06", (18, 2), "donjon1_porte_03"),
    "donjon1_interrupteur_02": ("salle_09", (1, 2), "donjon1_porte_06"),
}
RAMASSABLES = {"donjon1_plume_01": ("salle_03", (4, 2))}
STATUE = ("salle_01", (13, 8))
DEPART = ("salle_01", "S")
SALLE_BOSS = "salle_boss"

SOLIDES_FLECHE = set("#OrCRBS")                 # arrêtent une flèche (les portes fermées aussi, traitées à part)
SOLIDES = set("#OrCRS~")                        # bloquent Brann (B traité à part ; ~ = trou : on l'évite)
PORTES_CAR = {"X": None, "D": "cle", "G": "grande_cle", "N": "ennemis", "I": "interrupteur"}
COTES = ("N", "S", "E", "O")
OPP = {"N": "S", "S": "N", "E": "O", "O": "E"}
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
CAR_PORTE = set("XDGNI")


# --- Lecture du plan ------------------------------------------------------------------------------------
def lire_plan(chemin):
    texte = Path(chemin).read_text(encoding="utf-8")
    salles = {}
    for m in re.finditer(r"<!--\s*(salle_\w+)\s*-->\s*\n```text\n(.*?)\n```", texte, re.S):
        salles[m.group(1)] = [list(l) for l in m.group(2).split("\n")]
    return salles


def cellule_porte(cote, h):
    return {"N": (9, 0), "S": (9, h - 1), "O": (0, 5), "E": (19, 5)}[cote]


def cellule_arrivee(cote, h):
    return {"N": (9, 2), "S": (9, h - 3), "O": (2, 5), "E": (17, 5)}[cote]


erreurs = []


def err(msg):
    erreurs.append(msg)
    print("  ERREUR :", msg)


def verifier_structure(salles):
    print("== 1. Structure et cohérence des aperçus ==")
    attendues = ["salle_%02d" % i for i in range(1, 10)] + [SALLE_BOSS]
    for n in attendues:
        if n not in salles:
            err("aperçu manquant : " + n)
    comptes = {"C": 0, "S": 0}
    for n, g in salles.items():
        h = 22 if n == SALLE_BOSS else 11
        if len(g) != h or any(len(l) != 20 for l in g):
            err("%s : dimensions %dx%d au lieu de 20x%d" % (n, len(g[0]) if g else 0, len(g), h))
            continue
        for c in range(20):
            if g[0][c] not in "#X" and not (c == 9 and g[0][c] in CAR_PORTE):
                err("%s : mur du haut abîmé en (%d,0)" % (n, c))
        # ouvertures uniquement aux positions fixes
        for r in range(h):
            for c in range(20):
                ch = g[r][c]
                if ch in CAR_PORTE and (c, r) not in [cellule_porte(s, h) for s in COTES] and ch != "I":
                    err("%s : porte '%s' hors position fixe en (%d,%d)" % (n, ch, c, r))
        # bordure
        for r in range(h):
            for c in range(20):
                if (r in (0, h - 1) or c in (0, 19)) and g[r][c] not in "#" and g[r][c] not in CAR_PORTE:
                    err("%s : bordure ouverte en (%d,%d) = %r" % (n, c, r, g[r][c]))
    # portes : caractère attendu des deux côtés, spawn d'arrivée présent
    def verifier_cote(salle, cote, car, ident):
        if salle not in salles:
            return
        g = salles[salle]; h = len(g)
        if isinstance(cote, tuple):
            if g[cote[1]][cote[0]] != car:
                err("%s : porte intérieure %s attendue en %s" % (salle, ident, cote))
            return
        c, r = cellule_porte(cote, h)
        if g[r][c] != car:
            err("%s : côté %s doit porter '%s' (%s), trouvé %r" % (salle, cote, car, ident, g[r][c]))
        pc, pr = cellule_arrivee(cote, h)
        if g[pr][pc] != "P":
            err("%s : pas de Spawn P en (%d,%d) pour le côté %s" % (salle, pc, pr, cote))
    for pid, (typ, a, b) in PORTES.items():
        verifier_cote(*a, typ, pid)
        if b:
            verifier_cote(*b, typ, pid)
    for a, b in LIENS_LIBRES:
        verifier_cote(*a, "X", "libre")
        if b != "foret":
            verifier_cote(*b, "X", "libre")
    # aucun passage non déclaré
    declares = set()
    for pid, (typ, a, b) in PORTES.items():
        for cote in (a, b):
            if cote and not isinstance(cote[1], tuple):
                declares.add(cote)
    for a, b in LIENS_LIBRES:
        declares.add(a)
        if b != "foret":
            declares.add(b)
    for n, g in salles.items():
        h = len(g)
        for s in COTES:
            c, r = cellule_porte(s, h)
            if g[r][c] in CAR_PORTE and (n, s) not in declares:
                err("%s : passage non déclaré côté %s" % (n, s))
    # objets déclarés <-> aperçus
    for cid, (salle, (c, r), contenu) in COFFRES.items():
        if salles[salle][r][c] != "C":
            err("%s : coffre %s absent de l'aperçu en (%d,%d)" % (salle, cid, c, r))
    for iid, (salle, (c, r), _) in INTERRUPTEURS.items():
        if salles[salle][r][c] != "S":
            err("%s : interrupteur %s absent en (%d,%d)" % (salle, iid, c, r))
    for rid, (salle, (c, r)) in RAMASSABLES.items():
        if salles[salle][r][c] != "F":
            err("%s : ramassable %s absent" % (salle, rid))
    sc, (c, r) = STATUE
    if salles[sc][r][c] != "R":
        err("statue absente")
    nC = sum(l.count("C") for g in salles.values() for l in g)
    nS = sum(l.count("S") for g in salles.values() for l in g)
    if nC != len(COFFRES):
        err("%d 'C' dans les aperçus pour %d coffres déclarés" % (nC, len(COFFRES)))
    if nS != len(INTERRUPTEURS):
        err("%d 'S' dans les aperçus pour %d interrupteurs déclarés" % (nS, len(INTERRUPTEURS)))
    # ennemis jamais collés à une arrivée (>= 3 cases)
    for n, g in salles.items():
        sp = [(c, r) for r, l in enumerate(g) for c, ch in enumerate(l) if ch == "P"]
        for r, l in enumerate(g):
            for c, ch in enumerate(l):
                if ch in "EL":
                    d = min(((c - a) ** 2 + (r - b) ** 2) ** 0.5 for a, b in sp)
                    if d < 3:
                        err("%s : ennemi en (%d,%d) à %.1f cases d'une arrivée" % (n, c, r, d))
    # dimensions de Brann
    print("  Brann %dx%d px ; passage porte haut/bas %d px, gauche/droite %d px ; couloirs d'une case = 32 px : OK"
          % (BRANN_LARGEUR_PX, BRANN_HAUTEUR_PX, PASSAGE_PORTE_VERTICALE_PX, PASSAGE_PORTE_HORIZONTALE_PX))
    assert BRANN_LARGEUR_PX < PASSAGE_PORTE_VERTICALE_PX and BRANN_HAUTEUR_PX < PASSAGE_PORTE_HORIZONTALE_PX
    print("  portée de la flèche : %d px (+ ~20 px de décalage), utilisée : %d cases = %d px"
          % (PORTEE_FLECHE_PX, PORTEE_CASES, PORTEE_CASES * 32))
    print("  %d salles lues, %d coffres, %d interrupteurs" % (len(salles), len(COFFRES), len(INTERRUPTEURS)))


# --- Modèle d'une salle -----------------------------------------------------------------------------------
class Salle:
    def __init__(self, nom, grille):
        self.nom, self.g = nom, grille
        self.h = len(grille)
        self.blocs = frozenset((c, r) for r in range(self.h) for c in range(20) if grille[r][c] == "B")
        self.lutins = any("L" in l for l in grille)
        # portes de cette salle : cellule -> (id, type)
        self.portes = {}
        for pid, (typ, a, b) in PORTES.items():
            for cote in (a, b):
                if cote and cote[0] == nom:
                    cel = cote[1] if isinstance(cote[1], tuple) else cellule_porte(cote[1], self.h)
                    self.portes[cel] = (pid, typ)
        self.liens = {}  # cellule libre -> (salle voisine ou 'foret', côté d'arrivée)
        for a, b in LIENS_LIBRES:
            for x, y in ((a, b), (b, a)):
                if x != "foret" and x[0] == nom:
                    cel = cellule_porte(x[1], self.h)
                    self.liens[cel] = y if y == "foret" else (y[0], y[1])

    def passable(self, cel, ouvertes, blocs):
        c, r = cel
        if not (0 <= c < 20 and 0 <= r < self.h):
            return False
        ch = self.g[r][c]
        if cel in blocs:
            return False
        if ch in SOLIDES:
            return False
        if cel in self.portes:
            return self.portes[cel][0] in ouvertes
        return True

    def region(self, depart, ouvertes, blocs):
        vus = {depart}
        file = deque([depart])
        while file:
            c, r = file.popleft()
            for dc, dr in DIRS:
                n = (c + dc, r + dr)
                if n not in vus and self.passable(n, ouvertes, blocs):
                    vus.add(n); file.append(n)
        return vus

    def voisines_libres(self, cel, region):
        return any((cel[0] + dc, cel[1] + dr) in region for dc, dr in DIRS)

    def tir_possible(self, cible, region, ouvertes):
        cc, cr = cible
        for (c, r) in region:
            if not ((c == cc) != (r == cr)):
                continue
            d = abs(c - cc) + abs(r - cr)
            if d > PORTEE_CASES:
                continue
            sc = (cc > c) - (cc < c); sr = (cr > r) - (cr < r)
            x, y, ok = c + sc, r + sr, True
            while (x, y) != (cc, cr):
                ch = self.g[y][x]
                if ch in SOLIDES_FLECHE or ((x, y) in self.portes and self.portes[(x, y)][0] not in ouvertes):
                    ok = False; break
                x += sc; y += sr
            if ok:
                return True
        return False


# --- Parcours du donjon sur l'état du joueur ---------------------------------------------------------------
def explorer(salles_ascii, coffres, verbose=False):
    salles = {n: Salle(n, g) for n, g in salles_ascii.items()}
    # état : (salle, côté d'arrivée, portes ouvertes, coffres ouverts, interrupteurs touchés, salles nettoyées)
    init = (DEPART[0], DEPART[1], frozenset(), frozenset(), frozenset(), frozenset())
    aretes, vus, file = {}, {init}, deque([init])
    max_portes_cle = 0
    resume_max = None

    def successeurs(etat):
        nonlocal max_portes_cle, resume_max
        nom, cote, ouv, cof, sw, net = etat
        s = salles[nom]
        objets = {coffres[i][2] for i in cof}
        cles = sum(1 for i in cof if coffres[i][2] == "cle_petite") - sum(1 for p in ouv if PORTES[p][0] == "D")
        arc = "objet_arc" in objets
        depart = cellule_arrivee(cote, s.h)
        reg = s.region(depart, ouv, s.blocs)
        out = []
        # coffres
        for cid, (sn, cel, _) in coffres.items():
            if sn == nom and cid not in cof and s.voisines_libres(cel, reg):
                out.append(("coffre " + cid, (nom, cote, ouv, cof | {cid}, sw, net)))
        # portes à clé / grande clé (depuis la case devant la porte, côté de cette salle)
        accessibles = 0
        for cel, (pid, typ) in s.portes.items():
            if pid in ouv or typ not in ("D", "G") or not s.voisines_libres(cel, reg):
                continue
            if typ == "D":
                accessibles += 1
            if (typ == "D" and cles > 0) or (typ == "G" and "grande_cle" in objets):
                out.append(("porte " + pid, (nom, cote, ouv | {pid}, cof, sw, net)))
        if accessibles > max_portes_cle:
            max_portes_cle, resume_max = accessibles, (nom, cles)
        # interrupteurs à distance
        for iid, (sn, cel, pid) in INTERRUPTEURS.items():
            if sn == nom and iid not in sw and arc and s.tir_possible(cel, reg, ouv):
                out.append(("tir " + iid, (nom, cote, ouv | {pid}, cof, sw | {iid}, net)))
        # portes « ennemis » : salle nettoyée (un Lutin exige l'arc)
        if nom not in net and (arc or not s.lutins):
            ids = {pid for cel, (pid, typ) in s.portes.items() if typ == "N"}
            out.append(("nettoyer " + nom, (nom, cote, ouv | ids, cof, sw, net | {nom})))
        # traversée des ouvertures
        for cote2 in COTES:
            cel = cellule_porte(cote2, s.h)
            if cel not in reg:
                continue
            if cel in s.portes:
                dest = None
                pid, typ = s.portes[cel]
                t, a, b = PORTES[pid]
                autre = b if a == (nom, cote2) else a
                if autre:
                    dest = (autre[0], autre[1])
            else:
                dest = s.liens.get(cel)
            if dest and dest != "foret":
                out.append(("aller " + dest[0], (dest[0], dest[1], ouv, cof, sw, net)))
        return out

    while file:
        e = file.popleft()
        succ = successeurs(e)
        aretes[e] = succ
        for _, n in succ:
            if n not in vus:
                vus.add(n); file.append(n)
    # états depuis lesquels le boss est atteignable (parcours inverse)
    gagnants = {e for e in vus if e[0] == SALLE_BOSS}
    inverse = {}
    for e, succ in aretes.items():
        for _, n in succ:
            inverse.setdefault(n, set()).add(e)
    file = deque(gagnants); bons = set(gagnants)
    while file:
        e = file.popleft()
        for p in inverse.get(e, ()):
            if p not in bons:
                bons.add(p); file.append(p)
    return vus, aretes, bons, gagnants, max_portes_cle, resume_max


def verifier_donjon(salles_ascii):
    print("\n== 2. Parcours du donjon sur l'état du joueur ==")
    vus, aretes, bons, gagnants, mx, resume = explorer(salles_ascii, COFFRES)
    print("  %d états atteignables depuis l'arrivée (salle_01, côté sud)" % len(vus))
    print("  salle du boss atteignable : %s (%d états gagnants)" % ("OUI" if gagnants else "NON", len(gagnants)))
    if not gagnants:
        err("la salle du boss est inatteignable")
    pieges = vus - bons
    print("  états d'où le boss est HORS de portée (soft-lock) : %d" % len(pieges))
    if pieges:
        for e in list(pieges)[:5]:
            err("soft-lock possible : salle %s, portes %s, coffres %s" % (e[0], sorted(e[2]), sorted(e[3])))
    print("  nombre maximal de portes à clé utilisables au même moment : %d (dans %s avec %d clé(s) en poche)"
          % (mx, resume[0] if resume else "-", resume[1] if resume else 0))
    # coffres jamais ouverts / jamais atteints
    ouverts = set().union(*(e[3] for e in vus))
    for cid in COFFRES:
        if cid not in ouverts:
            err("coffre jamais atteignable : " + cid)
    toutes_cles = max(sum(1 for i in e[3] if COFFRES[i][2] == "cle_petite") for e in vus)
    portes_cle = [p for p, v in PORTES.items() if v[0] == "D"]
    print("  petites clés trouvables : %d ; portes à clé : %d" % (toutes_cles, len(portes_cle)))
    if toutes_cles < len(portes_cle):
        err("moins de clés que de portes à clé")
    # ordre : pour chaque état, aucune porte obligatoire sans clé -> équivalent à « pas de soft-lock »
    final = max(vus, key=lambda e: (len(e[2]) + len(e[3]) + len(e[4])))
    print("  progression maximale : portes %s ; coffres %s" % (sorted(final[2]), sorted(final[3])))
    # chemin le plus court vers le boss
    pere = {}
    init = next(e for e in vus if e[0] == DEPART[0] and not e[2] and not e[3] and e[1] == DEPART[1])
    file = deque([init]); pere[init] = None
    but = None
    while file:
        e = file.popleft()
        if e[0] == SALLE_BOSS:
            but = e; break
        for lab, n in aretes[e]:
            if n not in pere:
                pere[n] = (e, lab); file.append(n)
    if but:
        chemin = []
        e = but
        while pere[e]:
            e, lab = pere[e]; chemin.append(lab)
        chemin.reverse()
        print("  chemin le plus court : " + " > ".join(chemin))
    return vus


def verifier_blocs(salles_ascii):
    print("\n== 3. Blocs poussables (parcours de tous les états) ==")
    tout_ok = True
    for nom, g in salles_ascii.items():
        s = Salle(nom, g)
        if not s.blocs:
            continue
        # entrées : les cases d'arrivée de toutes les ouvertures de la salle
        ouvertes_toutes = {pid for (pid, _t) in s.portes.values()}   # portes ouvertes : cas le plus favorable
        entrees = [cellule_arrivee(c, s.h) for c in COTES if s.g[cellule_porte(c, s.h)[1]][cellule_porte(c, s.h)[0]] in CAR_PORTE]
        etats_vus, mauvais = set(), 0
        for entree in entrees:
            reg0 = s.region(entree, ouvertes_toutes, s.blocs)
            start = (s.blocs, min(reg0))
            file = deque([start]); etats_vus.add(start)
            while file:
                blocs, rep = file.popleft()
                reg = s.region(rep, ouvertes_toutes, blocs)
                if entree not in reg:
                    mauvais += 1
                for b in blocs:
                    for dc, dr in DIRS:
                        avant = (b[0] - dc, b[1] - dr)       # case du joueur
                        apres = (b[0] + dc, b[1] + dr)       # case où va le bloc
                        if avant in reg and s.passable(apres, ouvertes_toutes, blocs - {b} | set()) \
                                and apres not in blocs and s.g[apres[1]][apres[0]] not in "~" \
                                and apres not in s.portes and apres not in s.liens \
                                and 0 < apres[0] < 19 and 0 < apres[1] < s.h - 1:
                            nb = (blocs - {b}) | {apres}
                            reg2 = s.region(b, ouvertes_toutes, nb)
                            nxt = (nb, min(reg2))
                            if nxt not in etats_vus:
                                etats_vus.add(nxt); file.append(nxt)
        nb_pos = len({e[0] for e in etats_vus})
        print("  %s : %d bloc(s), %d positions de bloc possibles, %d états explorés, états sans retour vers l'entrée : %d"
              % (nom, len(s.blocs), nb_pos, len(etats_vus), mauvais))
        if mauvais:
            tout_ok = False
            err("%s : un bloc peut empêcher de ressortir" % nom)
        # le ramassable derrière le bloc est-il atteignable quelque part dans les états ?
        for rid, (sn, cel) in RAMASSABLES.items():
            if sn == nom:
                ok = False
                for blocs, rep in etats_vus:
                    if cel in s.region(rep, ouvertes_toutes, blocs) or \
                            any((cel[0] + dc, cel[1] + dr) in s.region(rep, ouvertes_toutes, blocs) for dc, dr in DIRS):
                        ok = True; break
                print("     %s atteignable dans au moins un état : %s" % (rid, "OUI" if ok else "NON"))
                if not ok:
                    err("%s inatteignable" % rid)
    if tout_ok:
        print("  Aucun bloc ne peut enfermer Brann ; sortir et revenir remet de toute façon le bloc en place.")


def autotest(salles_ascii):
    print("\n== 4. Auto-test du vérificateur ==")
    for retire in ("donjon1_coffre_03", "donjon1_coffre_05"):
        c2 = {k: v for k, v in COFFRES.items() if k != retire}
        _, _, _, gagnants, _, _ = explorer(salles_ascii, c2)
        print("  sans %s : boss atteignable = %s (attendu : False)" % (retire, bool(gagnants)))
        if gagnants:
            err("l'auto-test échoue : le vérificateur ne détecte pas le manque de clé")
    # un seul coffre de clé reconverti en carte : la clé 1 manque -> même résultat
    c3 = dict(COFFRES); c3["donjon1_coffre_05"] = ("salle_07", COFFRES["donjon1_coffre_05"][1], "carte_donjon")
    _, _, _, g3, _, _ = explorer(salles_ascii, c3)
    print("  clé n°2 remplacée par une carte : boss atteignable = %s (attendu : False)" % bool(g3))
    if g3:
        err("auto-test 3 échoué")


def apercu(salles_ascii):
    print("\n== Plan des salles ==")
    print("""
 y=3                 [salle_09]--G--[salle_boss]   (le boss est au nord de salle_09, 20x22)
                        |N(ennemis)
 y=2  [salle_06]-I-[salle_07]-D-[salle_08]
          |D
 y=1  [salle_03]-[salle_02]-[salle_04]-N-[salle_05]
                    |
 y=0            [salle_01]--(sortie vers la forêt)
 (D clé, G grande clé, N ennemis, I interrupteur ; sans lettre = ouvert)""")


def main():
    chemin = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("plan.md")
    salles = lire_plan(chemin)
    verifier_structure(salles)
    if not erreurs:
        verifier_donjon(salles)
        verifier_blocs(salles)
        autotest(salles)
    print()
    if erreurs:
        print("RÉSULTAT : %d erreur(s)" % len(erreurs))
        sys.exit(1)
    print("RÉSULTAT : toutes les vérifications passent.")


if __name__ == "__main__":
    main()
