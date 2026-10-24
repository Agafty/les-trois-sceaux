#!/usr/bin/env python3
"""Vérification du Temple des Racines (donjon 1, deux étages) - bibliothèque standard uniquement.

Usage :  python -I verif_donjon.py [chemin/vers/plan.md]

Lit les aperçus ASCII de plan.md (blocs "<!-- salle_XX -->" suivis d'un bloc ```text```) et :
  1. contrôle la forme des salles et la cohérence avec les tables ci-dessous (portes, coffres, cibles,
     torches, plaques, escaliers, trous de passage) ;
  2. fait un parcours sur l'ÉTAT du joueur (salle, zone atteignable, portes ouvertes, coffres importants
     ouverts) et prouve que la salle du boss est atteignable depuis TOUS les états atteignables, donc quel
     que soit l'ordre d'ouverture des portes, de pose des clés, de chute ou de retour en arrière ;
  3. prouve que la grande clé n'est pas atteignable sans changer d'étage, que chaque porte à clé est
     obligatoire (économie des clés) et que les petites clés suffisent ;
  4. vérifie chaque énigme : blocs et plaques (solveur de Sokoban + test « Brann peut toujours ressortir »),
     cibles à flèche (dont cibles en temps limité et en séquence), torches (chaîne de flèches enflammées,
     temps limité), leviers ;
  5. vérifie les chutes de passage et les escaliers (étage d'arrivée, point d'apparition, retour possible) ;
  6. lance des auto-tests (retirer une clé ou l'arc doit rendre le boss inatteignable).

Hypothèses de jeu (voir plan.md) : Brann marche sur une grille de cases (4 voisins, estimation prudente,
3,125 cases/s) ; un coffre s'ouvre depuis une case voisine ; une porte à clé s'ouvre depuis la case devant ;
la flèche vole en ligne droite sur au plus PORTEE_CASES cases, passe au-dessus des trous et de l'eau, et
s'arrête sur un mur, un pilier, un bloc, un coffre, une cible, un levier, une torche éteinte, une porte
fermée ; elle prend feu en traversant une torche allumée ou un brasero et allume la première torche
éteinte qu'elle touche ; les flèches ne manquent pas (butin garanti, voir « Risques » dans plan.md) ;
une porte `ennemis` s'ouvre quand la salle est nettoyée (impossible tant qu'il reste un Lutin et qu'on
n'a pas l'arc) ; les blocs reviennent à leur place à chaque chargement de salle.

La lecture des vraies cartes .tmx sera ajoutée à l'étape 2 (les anciennes cartes ne correspondent plus au plan).
"""
import re
import sys
import time
from collections import deque
from itertools import permutations
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# --- Constantes de jeu (lues dans player.tscn, Player.cs, Arrow.cs, arc.tres) --------------------------------
BRANN_LARGEUR_PX, BRANN_HAUTEUR_PX = 16, 20      # capsule rayon 8, hauteur 20
PASSAGE_PORTE_VERTICALE_PX = 20                  # porte_haut / porte_bas (Brann : 16 de large)
PASSAGE_PORTE_HORIZONTALE_PX = 24                # porte_gauche / porte_droite (Brann : 20 de haut)
PORTEE_FLECHE_PX = 320                           # Arrow.MaxDistance (+ 20 px de décalage initial)
PORTEE_CASES = 9                                 # 9 cases = 288 px : marge de sécurité
VITESSE_CASES_S = 100 / 32                       # Player.Speed = 100 px/s (déplacement sur 4 voisins : prudent)
DELAI_TIR_S = 0.7                                # viser + tirer + vol de la flèche (estimation prudente)
PART_TEMPS_MAX = 0.7                             # une énigme chronométrée doit tenir dans 70 % du temps donné

# --- Tables (doivent correspondre aux aperçus de plan.md) ---------------------------------------------------
NUMEROS_B1 = range(11, 16)
SALLES = ["salle_%02d" % i for i in range(1, 16)] + ["salle_boss"]
ETAGE = {n: ("B1" if n.startswith("salle_") and n[6:].isdigit() and int(n[6:]) in NUMEROS_B1 else "RDC")
         for n in SALLES}

# id -> (type, côté A, côté B).  Un côté = (salle, "N|S|E|O") ou (salle, (col, ligne)) pour une porte intérieure.
# Types : D petite clé, G grande clé, N ennemis, I interrupteur (levier, cibles, plaques, torches).
PORTES = {
    "donjon1_porte_01": ("D", ("salle_02", "N"), ("salle_06", "S")),
    "donjon1_porte_02": ("N", ("salle_04", "E"), ("salle_05", "O")),
    "donjon1_porte_03": ("I", ("salle_06", "E"), ("salle_07", "O")),
    "donjon1_porte_04": ("D", ("salle_07", "E"), ("salle_08", "O")),
    "donjon1_porte_05": ("N", ("salle_08", "N"), ("salle_09", "S")),
    "donjon1_porte_06": ("I", ("salle_09", "O"), ("salle_10", "E")),
    "donjon1_porte_07": ("G", ("salle_09", "N"), ("salle_boss", "S")),
    "donjon1_porte_08": ("I", ("salle_03", (3, 2)), None),
    "donjon1_porte_09": ("I", ("salle_05", (9, 2)), None),
    "donjon1_porte_10": ("I", ("salle_10", (9, 2)), None),
    "donjon1_porte_11": ("D", ("salle_13", "O"), ("salle_14", "E")),
    "donjon1_porte_12": ("I", ("salle_13", (4, 5)), None),
    "donjon1_porte_13": ("I", ("salle_14", (17, 2)), None),
    "donjon1_porte_14": ("I", ("salle_14", "N"), ("salle_12", "S")),
    "donjon1_porte_15": ("I", ("salle_12", (3, 2)), None),
}
# Passages libres (caractère X) : ((salle, côté), (salle, côté)) ; "foret" = sortie vers l'overworld
LIENS_LIBRES = [
    (("salle_01", "S"), "foret"),
    (("salle_01", "N"), ("salle_02", "S")),
    (("salle_02", "O"), ("salle_03", "E")),
    (("salle_02", "E"), ("salle_04", "O")),
    (("salle_07", "N"), ("salle_10", "S")),
    (("salle_11", "S"), ("salle_13", "N")),
]
# Escaliers : id -> (extrémité haute, extrémité basse), chacune = (salle, case de l'escalier, case du Spawn d'arrivée)
ESCALIERS = {
    "donjon1_escalier_01": (("salle_05", (1, 9), (2, 9)), ("salle_15", (1, 8), (2, 8))),
    "donjon1_escalier_02": (("salle_09", (18, 8), (17, 8)), ("salle_11", (18, 2), (17, 2))),
    "donjon1_escalier_03": (("salle_10", (1, 8), (2, 8)), ("salle_12", (18, 1), (17, 1))),
}
# Trous de passage : id -> (salle de départ, cases T, (salle d'arrivée, case du Spawn d'arrivée))
CHUTES = {
    "donjon1_chute_04": ("salle_04", [(1, 8), (2, 8), (1, 9), (2, 9)], ("salle_15", (9, 5))),
    "donjon1_chute_07": ("salle_07", [(17, 8), (18, 8), (17, 9), (18, 9)], ("salle_12", (9, 4))),
}
COFFRES = {  # id -> (salle, (col, ligne), contenu)
    "donjon1_coffre_01": ("salle_02", (15, 2), "carte_donjon"),
    "donjon1_coffre_02": ("salle_04", (15, 2), "boussole"),
    "donjon1_coffre_03": ("salle_05", (9, 1), "cle_petite"),
    "donjon1_coffre_04": ("salle_06", (6, 2), "objet_arc"),
    "donjon1_coffre_05": ("salle_10", (9, 1), "cle_petite"),
    "donjon1_coffre_06": ("salle_15", (11, 2), "cle_petite"),
    "donjon1_coffre_07": ("salle_14", (17, 1), "grande_cle"),
}
IMPORTANTS = {"cle_petite", "grande_cle", "objet_arc"}    # seuls ces contenus changent l'état du joueur
RAMASSABLES = {"donjon1_plume_01": ("salle_03", (1, 1)), "donjon1_plume_02": ("salle_12", (1, 1))}
STATUES = {"donjon1_statue_01": ("salle_01", (13, 8)), "donjon1_statue_02": ("salle_09", (6, 2))}
# Déclencheurs d'énigmes : id -> description.  `optionnel` : ne protège qu'une récompense facultative.
DECLENCHEURS = {
    "donjon1_plaques_01": dict(kind="plaques", salle="salle_03", plaques=[((15, 2), "bloc")],
                               porte="donjon1_porte_08", optionnel=True),
    "donjon1_plaques_02": dict(kind="plaques", salle="salle_05", plaques=[((14, 7), "bloc"), ((17, 7), "bloc")],
                               porte="donjon1_porte_09"),
    "donjon1_cibles_01": dict(kind="cibles", salle="salle_06", cibles=[(18, 2), (18, 8)], ordre=False, duree=6,
                              porte="donjon1_porte_03"),
    "donjon1_levier_01": dict(kind="levier", salle="salle_09", cell=(2, 3), porte="donjon1_porte_06"),
    "donjon1_torches_01": dict(kind="torches", salle="salle_10", torches=[(5, 2)], duree=0,
                               porte="donjon1_porte_10"),
    "donjon1_cibles_02": dict(kind="cibles", salle="salle_13", cibles=[(13, 4), (10, 8), (7, 4)], ordre=True,
                              duree=0, porte="donjon1_porte_12", indice="indice_ordre_cibles"),
    "donjon1_torches_02": dict(kind="torches", salle="salle_14", torches=[(7, 2), (7, 8), (14, 8)], duree=15,
                               porte="donjon1_porte_13"),
    "donjon1_levier_02": dict(kind="levier", salle="salle_14", cell=(10, 1), porte="donjon1_porte_14"),
    "donjon1_plaques_03": dict(kind="plaques", salle="salle_12", plaques=[((14, 2), "bloc"), ((16, 8), "joueur")],
                               porte="donjon1_porte_15", optionnel=True),
}
INDICES = {  # nom du rectangle -> (salle, cases)
    "indice_ronces_coupees": ("salle_05", [(8, 4), (9, 4), (10, 4)]),
    "indice_ordre_cibles": ("salle_11", [(8, 1), (9, 1), (10, 1)]),
}
DEPART = ("salle_01", "S")
SALLE_BOSS = "salle_boss"

SOLIDES_BRANN = set("#OrCRSBlfY~T")              # bloquent Brann (v et ^ : terminaux, traités à part)
SOLIDES_FLECHE = set("#OrCRSBl")                 # arrêtent une flèche (f éteinte et portes fermées : à part)
MARCHABLES = set(".PpFiX")
CAR_PORTE = set("XDGNI")
COTES = ("N", "S", "E", "O")
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

erreurs = []


def err(msg):
    erreurs.append(msg)
    print("  ERREUR :", msg)


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


# --- Modèle d'une salle -----------------------------------------------------------------------------------
class Salle:
    def __init__(self, nom, grille):
        self.nom, self.g = nom, grille
        self.h = len(grille)
        self.blocs = frozenset((c, r) for r in range(self.h) for c in range(20) if grille[r][c] == "B")
        self.lutins = any("L" in l for l in grille)
        self.ennemis = sum(l.count("E") + l.count("L") for l in grille)
        self.portes = {}          # cellule -> (id, type)
        for pid, (typ, a, b) in PORTES.items():
            for cote in (a, b):
                if cote and cote[0] == nom:
                    cel = cote[1] if isinstance(cote[1], tuple) else cellule_porte(cote[1], self.h)
                    self.portes[cel] = (pid, typ)
        self.ids = frozenset(pid for pid, _ in self.portes.values())
        self.liens = {}           # cellule libre -> (salle voisine ou 'foret', côté d'arrivée)
        for a, b in LIENS_LIBRES:
            for x, y in ((a, b), (b, a)):
                if x != "foret" and x[0] == nom:
                    self.liens[cellule_porte(x[1], self.h)] = y if y == "foret" else (y[0], y[1])
        self.escaliers = {}       # case d'escalier -> (salle d'arrivée, case du Spawn d'arrivée)
        self.spawns_escalier = {}  # case d'escalier -> case du Spawn de cette salle
        for haut, bas in ESCALIERS.values():
            for x, y in ((haut, bas), (bas, haut)):
                if x[0] == nom:
                    self.escaliers[x[1]] = (y[0], y[2])
                    self.spawns_escalier[x[1]] = x[2]
        self.chutes = []          # (ensemble de cases T, (salle d'arrivée, case du Spawn))
        for src, cases, dest in CHUTES.values():
            if src == nom:
                self.chutes.append((frozenset(cases), dest))
        self._reg, self._dist = {}, {}

    def car(self, cel):
        return self.g[cel[1]][cel[0]]

    def passable(self, cel, ouv):
        c, r = cel
        if not (0 <= c < 20 and 0 <= r < self.h):
            return False
        if cel in self.portes:
            return self.portes[cel][0] in ouv
        return self.g[r][c] in MARCHABLES

    def region(self, depart, ouv, blocs=None):
        """Cases atteignables à pied depuis `depart` (les blocs sont des obstacles, à leur place d'origine)."""
        cle = (depart, frozenset(ouv & self.ids)) if blocs is None else None
        if cle and cle in self._reg:
            return self._reg[cle]
        bl = self.blocs if blocs is None else blocs
        vus = {depart}
        file = deque([depart])
        while file:
            c, r = file.popleft()
            for dc, dr in DIRS:
                n = (c + dc, r + dr)
                if n not in vus and n not in bl and self.passable(n, ouv):
                    vus.add(n)
                    file.append(n)
        vus = frozenset(vus)
        if cle:
            self._reg[cle] = vus
        return vus

    @staticmethod
    def voisine(cel, reg):
        return any((cel[0] + dc, cel[1] + dr) in reg for dc, dr in DIRS)

    def distances(self, depart, ouv):
        cle = (depart, frozenset(ouv & self.ids))
        if cle in self._dist:
            return self._dist[cle]
        d = {depart: 0}
        file = deque([depart])
        while file:
            c, r = file.popleft()
            for dc, dr in DIRS:
                n = (c + dc, r + dr)
                if n not in d and n not in self.blocs and self.passable(n, ouv):
                    d[n] = d[(c, r)] + 1
                    file.append(n)
        self._dist[cle] = d
        return d

    def bloque_fleche(self, cel, ouv):
        if cel in self.portes and self.portes[cel][0] not in ouv:
            return True
        return self.car(cel) in SOLIDES_FLECHE or self.car(cel) == "f"

    # --- Flèches -----------------------------------------------------------------------------------------
    def tireurs_vers(self, cible, reg, ouv):
        """Cases d'où une flèche (non enflammée) touche `cible` en ligne droite."""
        cc, cr = cible
        res = []
        for (c, r) in reg:
            if (c == cc) == (r == cr):
                continue
            if abs(c - cc) + abs(r - cr) > PORTEE_CASES:
                continue
            dc, dr = (cc > c) - (cc < c), (cr > r) - (cr < r)
            x, y, ok = c + dc, r + dr, True
            while (x, y) != (cc, cr):
                if self.bloque_fleche((x, y), ouv):
                    ok = False
                    break
                x += dc
                y += dr
            if ok:
                res.append((c, r))
        return res

    def options_torches(self, reg, ouv, torches):
        """Pour chaque torche du groupe : liste de (case du tireur, torches à avoir allumées avant)."""
        opts = {t: [] for t in torches}
        for (c, r) in reg:
            for dc, dr in DIRS:
                brulant, via = False, set()
                for k in range(1, PORTEE_CASES + 1):
                    cel = (c + dc * k, r + dr * k)
                    if not (0 <= cel[0] < 20 and 0 <= cel[1] < self.h):
                        break
                    ch = self.car(cel)
                    if (cel in self.portes and self.portes[cel][0] not in ouv) or ch in SOLIDES_FLECHE:
                        break
                    if ch == "Y":
                        brulant = True
                    elif ch == "f":
                        if cel in opts and brulant:
                            opts[cel].append(((c, r), frozenset(via)))
                        if cel in opts:
                            via = via | {cel}      # si elle était allumée, la flèche continuerait
                            brulant = True
                        else:
                            break
        return opts


# --- Énigmes -----------------------------------------------------------------------------------------------
def temps_enchainement(s, ouv, listes, duree_ok):
    """Plus court temps (s) entre le 1er et le dernier tir, en visitant une case de tir par liste (ordre libre)."""
    n = len(listes)
    meilleur = None
    for ordre in permutations(range(n)):
        # programmation dynamique sur les cases de tir
        cout = {c: 0.0 for c in listes[ordre[0]]}
        for i in range(1, n):
            nouveau = {}
            for c2 in listes[ordre[i]]:
                best = None
                for c1, v in cout.items():
                    d = s.distances(c1, ouv).get(c2)
                    if d is None:
                        continue
                    t = v + d / VITESSE_CASES_S
                    if best is None or t < best:
                        best = t
                if best is not None:
                    nouveau[c2] = best
            cout = nouveau
            if not cout:
                break
        if cout:
            t = min(cout.values()) + (n - 1) * DELAI_TIR_S
            if meilleur is None or t < meilleur:
                meilleur = t
    return meilleur


def resoudre_torches(s, reg, ouv, trig):
    """(faisable, temps minimal) pour allumer toutes les torches du groupe."""
    torches = trig["torches"]
    opts = s.options_torches(reg, ouv, torches)
    allumees, change = set(), True
    while change:
        change = False
        for t in torches:
            if t not in allumees and any(via <= allumees for _, via in opts[t]):
                allumees.add(t)
                change = True
    if len(allumees) < len(torches):
        return False, None
    # ordre d'allumage : programmation dynamique sur (ordre, case de tir), `via` doit être allumé avant
    meilleur = None
    for ordre in permutations(torches):
        cout, ok = None, True
        for i, t in enumerate(ordre):
            avant = set(ordre[:i])
            cands = [c for c, via in opts[t] if via <= avant]
            if not cands:
                ok = False
                break
            if cout is None:
                cout = {c: 0.0 for c in cands}
            else:
                nouveau = {}
                for c2 in cands:
                    best = None
                    for c1, v in cout.items():
                        d = s.distances(c1, ouv).get(c2)
                        if d is not None and (best is None or v + d / VITESSE_CASES_S < best):
                            best = v + d / VITESSE_CASES_S
                    if best is not None:
                        nouveau[c2] = best
                cout = nouveau
                if not cout:
                    ok = False
                    break
        if ok and cout:
            t = min(cout.values()) + (len(torches) - 1) * DELAI_TIR_S
            if meilleur is None or t < meilleur:
                meilleur = t
    return meilleur is not None, meilleur


def resoudre_cibles(s, reg, ouv, trig):
    """(faisable, temps minimal ou None) pour toucher toutes les cibles du déclencheur."""
    listes = [s.tireurs_vers(c, reg, ouv) for c in trig["cibles"]]
    if any(not l for l in listes):
        return False, None
    if trig["duree"] > 0:
        t = temps_enchainement(s, ouv, listes, trig["duree"])
        return t is not None, t
    return True, None


def cases_interdites_aux_blocs(s):
    """Cases où le jeu doit refuser de pousser un bloc : sur ou à côté (8 voisins) d'une ouverture, d'un
    Spawn, d'un escalier, d'une porte intérieure (convention demandée au développeur, voir plan.md)."""
    centres = [cellule_porte(c, s.h) for c in COTES
               if s.g[cellule_porte(c, s.h)[1]][cellule_porte(c, s.h)[0]] in CAR_PORTE]
    centres += [(c, r) for r in range(s.h) for c in range(20) if s.g[r][c] in "P^v"]
    centres += [cel for cel in s.portes if not (cel[0] in (0, 19) or cel[1] in (0, s.h - 1))]
    return {(c + dc, r + dr) for (c, r) in centres for dc in (-1, 0, 1) for dr in (-1, 0, 1)}


def sorties_de_salle(s):
    """Sorties réelles de la salle : ouvertures (la case d'ouverture) et escaliers (cases voisines de la tuile)."""
    res = [("ouverture " + c, [cellule_porte(c, s.h)]) for c in COTES
           if s.g[cellule_porte(c, s.h)[1]][cellule_porte(c, s.h)[0]] in CAR_PORTE]
    for tuile in s.escaliers:
        res.append(("escalier " + str(tuile), [(tuile[0] + dc, tuile[1] + dr) for dc, dr in DIRS]))
    return res


class Sokoban:
    """Explore tous les états d'une salle à blocs : (blocs, zone du joueur)."""

    def __init__(self, s, ouv):
        self.s, self.ouv = s, frozenset(ouv)
        self.interdites = cases_interdites_aux_blocs(s)

    def zone(self, depart, blocs):
        return self.s.region(depart, self.ouv, blocs)

    def peut_pousser_vers(self, cel, blocs):
        s = self.s
        c, r = cel
        if not (0 < c < 19 and 0 < r < s.h - 1) or cel in self.interdites:
            return False
        return s.car(cel) in ".pPiF" and cel not in blocs and cel not in s.portes

    def explorer(self, depart):
        s = self.s
        b0 = s.blocs
        z0 = self.zone(depart, b0)
        start = (b0, min(z0))
        vus = {start: 0}
        file = deque([start])
        while file:
            blocs, rep = file.popleft()
            reg = self.zone(rep, blocs)
            for b in blocs:
                for dc, dr in DIRS:
                    avant, apres = (b[0] - dc, b[1] - dr), (b[0] + dc, b[1] + dr)
                    if avant in reg and self.peut_pousser_vers(apres, blocs):
                        nb = (blocs - {b}) | {apres}
                        nxt = (nb, min(self.zone(b, nb)))
                        if nxt not in vus:
                            vus[nxt] = vus[(blocs, rep)] + 1
                            file.append(nxt)
        return vus

    def but(self, vus, plaques):
        """Pousses minimales pour atteindre le but, ou None."""
        best = None
        pb = [c for c, t in plaques if t == "bloc"]
        pj = [c for c, t in plaques if t == "joueur"]
        for (blocs, rep), n in vus.items():
            if all(p in blocs for p in pb):
                reg = self.zone(rep, blocs)
                if all(p in reg for p in pj):
                    if best is None or n < best:
                        best = n
        return best

    def etats_but(self, vus, plaques):
        pb = [c for c, t in plaques if t == "bloc"]
        pj = [c for c, t in plaques if t == "joueur"]
        return {e for e in vus if all(p in e[0] for p in pb) and all(p in self.zone(e[1], e[0]) for p in pj)}


_cache_sokoban = {}


def sokoban_resolu(s, depart, ouv, trig):
    cle = (s.nom, depart, frozenset(ouv & s.ids))
    if cle not in _cache_sokoban:
        sk = Sokoban(s, ouv)
        vus = sk.explorer(depart)
        _cache_sokoban[cle] = (sk, vus)
    sk, vus = _cache_sokoban[cle]
    return sk.but(vus, trig["plaques"]) is not None


def peut_declencher(tid, trig, s, reg, ouv, arc, rep):
    k = trig["kind"]
    if k == "levier":
        return s.voisine(trig["cell"], reg)
    if k == "plaques":
        return sokoban_resolu(s, rep, ouv, trig)
    if not arc:
        return False
    if k == "cibles":
        ok, t = resoudre_cibles(s, reg, ouv, trig)
        return ok and (t is None or t <= PART_TEMPS_MAX * trig["duree"])
    if k == "torches":
        ok, t = resoudre_torches(s, reg, ouv, trig)
        return ok and (t is None or trig["duree"] == 0 or t <= PART_TEMPS_MAX * trig["duree"])
    return False


# --- Parcours du donjon sur l'état du joueur ---------------------------------------------------------------
def explorer(salles_ascii, coffres, *, sans_etage=False, bloquees=frozenset(), verbose=False):
    salles = {n: Salle(n, g) for n, g in salles_ascii.items()}
    decl_par_salle = {}
    for tid, t in DECLENCHEURS.items():
        if not t.get("optionnel"):
            decl_par_salle.setdefault(t["salle"], []).append((tid, t))
    memo = {}
    stats = {"max_portes_cle": 0, "resume": None}

    def canon(nom, cel, ouv):
        return (nom, min(salles[nom].region(cel, ouv)))

    def successeurs(etat):
        nom, rep, ouv, cof = etat
        s = salles[nom]
        reg = s.region(rep, ouv)
        objets = {coffres[i][2] for i in cof}
        arc = "objet_arc" in objets
        cles = sum(1 for i in cof if coffres[i][2] == "cle_petite") - \
            sum(1 for p in ouv if PORTES[p][0] == "D")
        out = []

        def interne(ouv2, cof2, lab):
            r2 = s.region(rep, ouv2)
            out.append((lab, (nom, min(r2), ouv2, cof2)))

        for cid, (sn, cel, contenu) in coffres.items():
            if sn == nom and contenu in IMPORTANTS and cid not in cof and s.voisine(cel, reg):
                out.append(("coffre " + cid, (nom, rep, ouv, cof | {cid})))
        accessibles = 0
        for cel, (pid, typ) in s.portes.items():
            if pid in ouv or pid in bloquees or typ not in ("D", "G") or not s.voisine(cel, reg):
                continue
            if typ == "D":
                accessibles += 1
            if (typ == "D" and cles > 0) or (typ == "G" and "grande_cle" in objets):
                interne(ouv | {pid}, cof, "porte " + pid)
        if accessibles > stats["max_portes_cle"]:
            stats["max_portes_cle"], stats["resume"] = accessibles, (nom, cles)
        for tid, t in decl_par_salle.get(nom, ()):
            if t["porte"] in ouv or t["porte"] in bloquees:
                continue
            cle = (tid, rep, frozenset(ouv & s.ids), arc)
            if cle not in memo:
                memo[cle] = peut_declencher(tid, t, s, reg, ouv, arc, rep)
            if memo[cle]:
                interne(ouv | {t["porte"]}, cof, "énigme " + tid)
        if (arc or not s.lutins):
            ids = {pid for cel, (pid, typ) in s.portes.items() if typ == "N" and pid not in bloquees}
            if ids - ouv:
                interne(ouv | ids, cof, "nettoyer " + nom)
        for cote in COTES:
            cel = cellule_porte(cote, s.h)
            if cel not in reg:
                continue
            if cel in s.portes:
                pid, typ = s.portes[cel]
                t_, a, b = PORTES[pid]
                autre = b if a == (nom, cote) else a
                dest = (autre[0], autre[1]) if autre else None
            else:
                dest = s.liens.get(cel)
            if dest and dest != "foret":
                arr = cellule_arrivee(dest[1], salles[dest[0]].h)
                out.append(("aller " + dest[0], (dest[0], canon(dest[0], arr, ouv)[1], ouv, cof)))
        if not sans_etage:
            for tuile, (sd, spawn) in s.escaliers.items():
                if s.voisine(tuile, reg):
                    out.append(("escalier vers " + sd, (sd, canon(sd, spawn, ouv)[1], ouv, cof)))
            for cases, (sd, spawn) in s.chutes:
                if any(s.voisine(c, reg) for c in cases):
                    out.append(("chute vers " + sd, (sd, canon(sd, spawn, ouv)[1], ouv, cof)))
        return out

    nom0, cote0 = DEPART
    arr0 = cellule_arrivee(cote0, salles[nom0].h)
    init = (nom0, canon(nom0, arr0, frozenset())[1], frozenset(), frozenset())
    parent, file = {init: None}, deque([init])
    aretes = {}
    while file:
        e = file.popleft()
        succ = successeurs(e)
        aretes[e] = [n for _, n in succ]
        for lab, n in succ:
            if n not in parent:
                parent[n] = (e, lab)
                file.append(n)
    vus = set(parent)
    gagnants = {e for e in vus if e[0] == SALLE_BOSS}
    inverse = {}
    for e, succ in aretes.items():
        for n in succ:
            inverse.setdefault(n, []).append(e)
    bons, file = set(gagnants), deque(gagnants)
    while file:
        e = file.popleft()
        for p in inverse.get(e, ()):
            if p not in bons:
                bons.add(p)
                file.append(p)
    return dict(vus=vus, parent=parent, bons=bons, gagnants=gagnants, salles=salles, stats=stats, init=init)


def chemin(res, but):
    out, e = [], but
    while res["parent"][e]:
        e, lab = res["parent"][e]
        out.append(lab)
    out.reverse()
    return out


def verifier_donjon(salles_ascii):
    print("\n== 2. Parcours du donjon sur l'état du joueur ==")
    t0 = time.time()
    res = explorer(salles_ascii, COFFRES)
    vus, bons, gagnants, salles = res["vus"], res["bons"], res["gagnants"], res["salles"]
    print("  %d états atteignables depuis l'arrivée (salle_01, côté sud) [%.1f s]" % (len(vus), time.time() - t0))
    print("  salle du boss atteignable : %s (%d états gagnants)" % ("OUI" if gagnants else "NON", len(gagnants)))
    if not gagnants:
        err("la salle du boss est inatteignable")
        return res
    pieges = vus - bons
    print("  états d'où le boss est HORS de portée (soft-lock) : %d" % len(pieges))
    for e in list(pieges)[:5]:
        err("soft-lock possible : salle %s, portes %s, coffres %s" % (e[0], sorted(e[2]), sorted(e[3])))
    # salles atteignables, étages
    atteintes = {e[0] for e in vus}
    for n in SALLES:
        if n not in atteintes:
            err("salle jamais atteignable : " + n)
    print("  salles atteintes : %d/%d (RDC : %d, sous-sol : %d)" % (
        len(atteintes), len(SALLES), sum(1 for n in atteintes if ETAGE[n] == "RDC"),
        sum(1 for n in atteintes if ETAGE[n] == "B1")))
    # coffres et ramassables atteignables (dans au moins un état)
    for cid, (sn, cel, contenu) in COFFRES.items():
        ok = any(e[0] == sn and Salle.voisine(cel, salles[sn].region(e[1], e[2])) for e in vus)
        if not ok:
            err("coffre jamais atteignable : " + cid)
    for rid, (sn, cel) in RAMASSABLES.items():
        ok = any(e[0] == sn and (cel in salles[sn].region(e[1], e[2] | frozenset(
            t["porte"] for t in DECLENCHEURS.values() if t["salle"] == sn and t.get("optionnel")))) for e in vus)
        print("  %s atteignable (avec sa grille ouverte) : %s" % (rid, "OUI" if ok else "NON"))
        if not ok:
            err("ramassable inatteignable : " + rid)
    # énigmes facultatives : faisables depuis au moins un état atteint
    for tid, t in DECLENCHEURS.items():
        if not t.get("optionnel"):
            continue
        s = salles[t["salle"]]
        ok = False
        for e in vus:
            if e[0] != t["salle"]:
                continue
            reg = s.region(e[1], e[2])
            arc = any(COFFRES[i][2] == "objet_arc" for i in e[3])
            if peut_declencher(tid, t, s, reg, e[2], arc, e[1]):
                ok = True
                break
        print("  énigme facultative %s faisable : %s" % (tid, "OUI" if ok else "NON"))
        if not ok:
            err("énigme facultative infaisable : " + tid)
    # clés
    n_cles = max(sum(1 for i in e[3] if COFFRES[i][2] == "cle_petite") for e in vus)
    portes_cle = [p for p, v in PORTES.items() if v[0] == "D"]
    print("  petites clés trouvables : %d ; portes à clé : %d" % (n_cles, len(portes_cle)))
    if n_cles < len(portes_cle):
        err("moins de clés que de portes à clé")
    mx = res["stats"]["max_portes_cle"]
    print("  portes à clé utilisables au même moment : au plus %d (dans %s avec %d clé(s) en poche)"
          % (mx, res["stats"]["resume"][0], res["stats"]["resume"][1]))
    # chemin le plus court
    but = min(gagnants, key=lambda e: len(chemin(res, e)))
    print("  chemin le plus court vers le boss (%d actions) :" % len(chemin(res, but)))
    print("    " + " > ".join(chemin(res, but)))
    return res


def verifier_etages(salles_ascii, res_complet):
    print("\n== 3. Deux étages : grande clé, portes à clé, chutes et escaliers ==")
    # 3a. grande clé atteignable sans escalier ni chute ?
    res = explorer(salles_ascii, COFFRES, sans_etage=True)
    ouverts = set().union(*(e[3] for e in res["vus"]))
    gc = [cid for cid, v in COFFRES.items() if v[2] == "grande_cle"][0]
    print("  sans escalier ni chute : %d états, grande clé atteignable : %s (attendu : NON), boss atteignable : %s"
          % (len(res["vus"]), "OUI" if gc in ouverts else "NON", "OUI" if res["gagnants"] else "NON"))
    if gc in ouverts or res["gagnants"]:
        err("la grande clé (ou le boss) est atteignable sans changer d'étage")
    if ETAGE[COFFRES[gc][0]] != "B1":
        err("la grande clé n'est pas au sous-sol")
    sal = res_complet["salles"]
    porte_boss = [p for p, v in PORTES.items() if v[0] == "G"][0]
    salle_porte = PORTES[porte_boss][1][0]
    print("  grande clé : %s (%s) ; porte du boss : %s (%s) ; salles RDC reliées au sous-sol par escalier : %s"
          % (COFFRES[gc][0], COFFRES[gc][1], porte_boss, salle_porte,
             sorted({x[0] for e in ESCALIERS.values() for x in e if ETAGE[x[0]] == "RDC"})))
    # 3b. chaque porte à clé et chaque clé sont obligatoires ; économie
    obligatoires = []
    for pid in [p for p, v in PORTES.items() if v[0] == "D"]:
        r = explorer(salles_ascii, COFFRES, bloquees=frozenset({pid}))
        print("  porte %s condamnée -> boss atteignable : %s" % (pid, "OUI" if r["gagnants"] else "NON"))
        if not r["gagnants"]:
            obligatoires.append(pid)
    for cid in [c for c, v in COFFRES.items() if v[2] == "cle_petite"]:
        c2 = {k: v for k, v in COFFRES.items() if k != cid}
        r = explorer(salles_ascii, c2)
        print("  sans la clé du coffre %s -> boss atteignable : %s (attendu : NON si toutes les portes sont "
              "obligatoires)" % (cid, "OUI" if r["gagnants"] else "NON"))
        if r["gagnants"] and len(obligatoires) == len([c for c, v in COFFRES.items() if v[2] == "cle_petite"]):
            err("une petite clé est inutile alors que toutes les portes sont obligatoires")
    nc = len([c for c, v in COFFRES.items() if v[2] == "cle_petite"])
    print("  portes à clé obligatoires : %d ; petites clés disponibles : %d" % (len(obligatoires), nc))
    if nc < len(obligatoires):
        err("clés insuffisantes")
    # 3c. chutes et escaliers
    for cid, (src, cases, (dst, spawn)) in CHUTES.items():
        gs = salles_ascii[src]
        bon_etage = ETAGE[src] == "RDC" and ETAGE[dst] == "B1"
        spawn_ok = salles_ascii[dst][spawn[1]][spawn[0]] == "P"
        autour = [(spawn[0] + dc, spawn[1] + dr) for dc in (-1, 0, 1) for dr in (-1, 0, 1) if (dc, dr) != (0, 0)]
        pres_trou = any(salles_ascii[dst][y][x] in "~T" for x, y in autour)
        cases_ok = all(gs[y][x] == "T" for x, y in cases)
        # rectangle plein
        xs, ys = {x for x, _ in cases}, {y for _, y in cases}
        rect = len(cases) == len(xs) * len(ys)
        # depuis l'arrivée de chute, un escalier vers le haut est-il joignable dans tous les états atteints ?
        sal_d = Salle(dst, salles_ascii[dst])
        etats = [e for e in res_complet["vus"] if e[0] == dst and spawn in sal_d.region(e[1], e[2])]
        ok_retour = all(any(sal_d.voisine(t, sal_d.region(e[1], e[2])) for t in sal_d.escaliers) or
                        e in res_complet["bons"] for e in etats)
        print("  %s : %s (%s) -> %s%s : étage %s, Spawn P %s, cases T %s, rectangle %s, pas de trou près du "
              "Spawn %s, retour/boss possible depuis tous les états d'arrivée %s"
              % (cid, src, ETAGE[src], dst, spawn, "OK" if bon_etage else "KO", "OK" if spawn_ok else "KO",
                 "OK" if cases_ok else "KO", "OK" if rect else "KO", "OK" if not pres_trou else "KO",
                 "OK" if ok_retour else "KO"))
        for ok, msg in ((bon_etage, "la chute ne descend pas d'un étage"), (spawn_ok, "pas de Spawn d'arrivée"),
                        (cases_ok, "cases T absentes de l'aperçu"), (rect, "trou de passage non rectangulaire"),
                        (not pres_trou, "trou près du Spawn d'arrivée"), (ok_retour, "retour impossible")):
            if not ok:
                err("%s : %s" % (cid, msg))
        if any(b for b in Salle(src, gs).blocs):
            err("%s : bloc dans une salle à trous de passage" % cid)
    for eid, (haut, bas) in ESCALIERS.items():
        ok = ETAGE[haut[0]] == "RDC" and ETAGE[bas[0]] == "B1" and \
            salles_ascii[haut[0]][haut[1][1]][haut[1][0]] == "v" and salles_ascii[bas[0]][bas[1][1]][bas[1][0]] == "^" \
            and salles_ascii[haut[0]][haut[2][1]][haut[2][0]] == "P" and salles_ascii[bas[0]][bas[2][1]][bas[2][0]] == "P"
        voisins = abs(haut[1][0] - haut[2][0]) + abs(haut[1][1] - haut[2][1]) == 1 and \
            abs(bas[1][0] - bas[2][0]) + abs(bas[1][1] - bas[2][1]) == 1
        print("  %s : %s %s <-> %s %s : v en haut, ^ en bas, Spawn voisin de l'escalier : %s"
              % (eid, haut[0], haut[1], bas[0], bas[1], "OK" if ok and voisins else "KO"))
        if not (ok and voisins):
            err("%s : escalier mal formé" % eid)
    return res


def verifier_enigmes(salles_ascii, res):
    print("\n== 4. Énigmes ==")
    salles, vus = res["salles"], res["vus"]
    for tid, t in DECLENCHEURS.items():
        s = salles[t["salle"]]
        meilleur, n_ok, n_tot = None, 0, 0
        for e in vus:
            if e[0] != t["salle"] or t["porte"] in e[2]:
                continue
            n_tot += 1
            reg = s.region(e[1], e[2])
            arc = any(COFFRES[i][2] == "objet_arc" for i in e[3])
            if peut_declencher(tid, t, s, reg, e[2], arc, e[1]):
                n_ok += 1
        # description
        detail = ""
        e0 = next((e for e in vus if e[0] == t["salle"] and t["porte"] not in e[2]), None)
        if t["kind"] == "torches" and e0:
            reg = s.region(e0[1], e0[2])
            ok, tmin = resoudre_torches(s, reg, e0[2], t)
            detail = "chaîne de %d torche(s)%s" % (len(t["torches"]), (", temps min %.1f s sur %d s" % (tmin, t["duree"]))
                                                  if tmin is not None and t["duree"] else "")
        elif t["kind"] == "cibles" and e0:
            reg = s.region(e0[1], e0[2])
            ok, tmin = resoudre_cibles(s, reg, e0[2], t)
            detail = "%d cible(s)%s%s" % (len(t["cibles"]), ", en séquence" if t["ordre"] else "",
                                         (", temps min %.1f s sur %d s" % (tmin, t["duree"])) if tmin else "")
        elif t["kind"] == "plaques":
            ouv = frozenset(s.ids)
            dep = [cellule_arrivee(c, s.h) for c in COTES
                   if s.g[cellule_porte(c, s.h)[1]][cellule_porte(c, s.h)[0]] in CAR_PORTE]
            dep += list(s.spawns_escalier.values())
            sk = Sokoban(s, ouv)
            vus_b = sk.explorer(dep[0])
            detail = "%d bloc(s), %d plaque(s), %d état(s), solution en %s pousse(s)" % (
                len(s.blocs), len(t["plaques"]), len(vus_b), sk.but(vus_b, t["plaques"]))
        print("  %-20s %-8s %-22s faisable dans %d/%d états où elle reste à faire  %s"
              % (tid, t["kind"], t["salle"], n_ok, n_tot, detail))
        if n_tot and n_ok == 0:
            err("énigme jamais faisable : " + tid)
        if t.get("indice") and INDICES[t["indice"]][0] not in {e[0] for e in vus}:
            err("indice de %s inatteignable" % tid)
        if t["kind"] in ("cibles", "torches") and s.ennemis == 0:
            err("%s : salle à flèches sans ennemi (pas de butin de flèches)" % tid)
    # flèches
    print("  salles où l'on tire (cibles, torches) et qui contiennent au moins un ennemi (butin de flèches) : "
          "%s" % sorted({t["salle"] for t in DECLENCHEURS.values() if t["kind"] in ("cibles", "torches")}))


def verifier_blocs(salles_ascii, res):
    print("\n== 5. Blocs poussables (parcours de tous les états) ==")
    tout_ok = True
    for nom, g in salles_ascii.items():
        s = Salle(nom, g)
        if not s.blocs:
            continue
        ouv = frozenset(s.ids)                       # cas le plus favorable : toutes les portes ouvertes
        sorties = sorties_de_salle(s)
        entrees = {}                                 # case d'arrivée -> sorties de la salle
        for c in COTES:
            cp = cellule_porte(c, s.h)
            if g[cp[1]][cp[0]] in CAR_PORTE:
                entrees[cellule_arrivee(c, s.h)] = ["ouverture " + c]
        for tuile, sp in s.spawns_escalier.items():
            entrees[sp] = ["escalier " + str(tuile)]
        for d in CHUTES.values():
            if d[2][0] == nom:
                entrees[d[2][1]] = [lab for lab, _ in sorties]
        trig = [t for t in DECLENCHEURS.values() if t["salle"] == nom and t["kind"] == "plaques"]
        for ent in entrees:
            sk = Sokoban(s, ouv)
            vus = sk.explorer(ent)
            # graphe des poussées (arêtes inverses)
            inverse = {}
            for (blocs, rep) in vus:
                zone = sk.zone(rep, blocs)
                for b in blocs:
                    for dc, dr in DIRS:
                        avant, apres = (b[0] - dc, b[1] - dr), (b[0] + dc, b[1] + dr)
                        if avant in zone and sk.peut_pousser_vers(apres, blocs):
                            nb = (blocs - {b}) | {apres}
                            inverse.setdefault((nb, min(sk.zone(b, nb))), []).append((blocs, rep))

            def remonte(buts):
                ok, file = set(buts), deque(buts)
                while file:
                    e = file.popleft()
                    for q in inverse.get(e, ()):
                        if q not in ok:
                            ok.add(q)
                            file.append(q)
                return ok

            avec_sortie, dont_arrivee = set(), set()
            for (blocs, rep) in vus:
                zone = sk.zone(rep, blocs)
                atteintes = {lab for lab, cases in sorties if any(c in zone for c in cases)}
                if atteintes:
                    avec_sortie.add((blocs, rep))
                if set(entrees[ent]) & atteintes:
                    dont_arrivee.add((blocs, rep))
            enfermes = len(vus) - len(remonte(avec_sortie))          # aucune suite de poussées ne les libère
            gene = len(vus) - len(dont_arrivee)                      # sortie d'arrivée momentanément coupée
            positions = len({b for b, _ in vus})
            msg = ("  %s depuis %s : %d bloc(s), %d positions de blocs, %d états ; états où Brann est enfermé pour "
                   "toujours : %d ; états où la sortie d'arrivée est momentanément coupée : %d"
                   % (nom, ent, len(s.blocs), positions, len(vus), enfermes, gene))
            for t in trig:
                p = sk.but(vus, t["plaques"])
                bons = remonte(sk.etats_but(vus, t["plaques"]))
                msg += " ; solution en %s pousses ; états sans issue (réinitialisation par sortie/retour) : %d" % (
                    p, len(vus) - len(bons))
                if p is None:
                    err("%s : énigme de plaques sans solution" % nom)
            print(msg)
            if enfermes:
                tout_ok = False
                err("%s : un bloc peut enfermer Brann (arrivée en %s)" % (nom, ent))
    if tout_ok:
        print("  Brann peut toujours ressortir (avec la règle « pas de bloc près d'une sortie ») ; "
              "sortir et revenir remet de toute façon les blocs en place.")


def autotest(salles_ascii):
    print("\n== 6. Auto-tests du vérificateur (il doit détecter les défauts qu'on lui injecte) ==")
    for retire in [c for c, v in COFFRES.items() if v[2] in ("cle_petite", "objet_arc")]:
        c2 = {k: v for k, v in COFFRES.items() if k != retire}
        r = explorer(salles_ascii, c2)
        print("  sans %s : boss atteignable = %s (attendu : False)" % (retire, bool(r["gagnants"])))
        if r["gagnants"]:
            err("l'auto-test échoue : %s retiré mais le boss reste atteignable" % retire)
    # 1. trou de passage sans escalier de retour : la salle d'arrivée devient un piège
    sauve = dict(ESCALIERS)
    del ESCALIERS["donjon1_escalier_01"]
    try:
        r = explorer(salles_ascii, COFFRES)
        pieges = len(r["vus"] - r["bons"])
    finally:
        ESCALIERS.update(sauve)
    print("  escalier 05-15 supprimé (la chute vers 15 n'a plus de retour) : %d états piégés (attendu : > 0)" % pieges)
    if pieges == 0:
        err("l'auto-test échoue : un soft-lock injecté n'est pas détecté")
    # 2. torches trop chronométrées
    t = DECLENCHEURS["donjon1_torches_02"]
    ancien = t["duree"]
    t["duree"] = 6
    try:
        r = explorer(salles_ascii, COFFRES)
    finally:
        t["duree"] = ancien
    print("  torches de la salle 14 limitées à 6 s : boss atteignable = %s (attendu : False)" % bool(r["gagnants"]))
    if r["gagnants"]:
        err("l'auto-test échoue : la limite de temps n'est pas prise en compte")


# --- Structure des aperçus ----------------------------------------------------------------------------------
def verifier_structure(salles):
    print("== 1. Structure et cohérence des aperçus ==")
    for n in SALLES:
        if n not in salles:
            err("aperçu manquant : " + n)
    for n in salles:
        if n not in SALLES:
            err("salle inconnue : " + n)
    comptes = {}
    for n, g in salles.items():
        h = 22 if n == SALLE_BOSS else 11
        if len(g) != h or any(len(l) != 20 for l in g):
            err("%s : dimensions %dx%d au lieu de 20x%d" % (n, len(g[0]) if g else 0, len(g), h))
            return
        for l in g:
            for ch in l:
                comptes[ch] = comptes.get(ch, 0) + 1
                if ch not in "#.~TOrEiLCSBpFRXDGNIPvYf^l":
                    err("%s : caractère inconnu %r" % (n, ch))
        for r in range(h):
            for c in range(20):
                ch = g[r][c]
                bord = r in (0, h - 1) or c in (0, 19)
                fixes = [cellule_porte(s_, h) for s_ in COTES]
                if bord and ch not in "#" and not (ch in CAR_PORTE and (c, r) in fixes):
                    err("%s : bordure ouverte en (%d,%d) = %r" % (n, c, r, ch))
                if ch in "XDGN" and (c, r) not in fixes:
                    err("%s : porte '%s' hors position fixe en (%d,%d)" % (n, ch, c, r))
                if ch in "vTpfYlS^B" and bord:
                    err("%s : élément %r sur la bordure en (%d,%d)" % (n, ch, c, r))
    # portes : caractère attendu des deux côtés, Spawn d'arrivée présent
    arrivees = {n: set() for n in salles}

    def verifier_cote(salle, cote, car, ident):
        if salle not in salles:
            return
        g = salles[salle]
        h = len(g)
        if isinstance(cote, tuple):
            if g[cote[1]][cote[0]] != car:
                err("%s : porte intérieure %s attendue en %s (%r)" % (salle, ident, cote, car))
            return
        c, r = cellule_porte(cote, h)
        if g[r][c] != car:
            err("%s : côté %s doit porter '%s' (%s), trouvé %r" % (salle, cote, car, ident, g[r][c]))
        pc, pr = cellule_arrivee(cote, h)
        arrivees[salle].add((pc, pr))
        if g[pr][pc] != "P":
            err("%s : pas de Spawn P en (%d,%d) pour le côté %s" % (salle, pc, pr, cote))

    for pid, (typ, a, b) in PORTES.items():
        verifier_cote(*a, typ, pid)
        if b:
            verifier_cote(*b, typ, pid)
    declares = set()
    for a, b in LIENS_LIBRES:
        verifier_cote(*a, "X", "libre")
        declares.add(a)
        if b != "foret":
            verifier_cote(*b, "X", "libre")
            declares.add(b)
    for pid, (typ, a, b) in PORTES.items():
        for cote in (a, b):
            if cote and not isinstance(cote[1], tuple):
                declares.add(cote)
    for n, g in salles.items():
        h = len(g)
        for s_ in COTES:
            c, r = cellule_porte(s_, h)
            if g[r][c] in CAR_PORTE and (n, s_) not in declares:
                err("%s : passage non déclaré côté %s" % (n, s_))
    # Spawns des escaliers et des chutes
    for eid, (haut, bas) in ESCALIERS.items():
        for (sn, tuile, spawn) in (haut, bas):
            arrivees[sn].add(spawn)
    for cid, (src, cases, (dst, spawn)) in CHUTES.items():
        arrivees[dst].add(spawn)
    for n, g in salles.items():
        ps = {(c, r) for r, l in enumerate(g) for c, ch in enumerate(l) if ch == "P"}
        if ps != arrivees[n]:
            err("%s : Spawns P %s différents des arrivées déclarées %s" % (n, sorted(ps), sorted(arrivees[n])))
    # objets déclarés <-> aperçus
    def verifier_cases(table, car, nom_table):
        for k, v in table.items():
            salle, cases = v[0], v[1]
            cases = cases if isinstance(cases, list) else [cases]
            for (c, r) in cases:
                if salles[salle][r][c] != car:
                    err("%s : %s %s absent de l'aperçu en (%d,%d) (trouvé %r)" % (salle, nom_table, k, c, r,
                                                                                 salles[salle][r][c]))
    verifier_cases(COFFRES, "C", "coffre")
    verifier_cases(RAMASSABLES, "F", "ramassable")
    verifier_cases(CHUTES_AS_ZONES(), "T", "trou de passage")
    for tid, t in DECLENCHEURS.items():
        s_ = t["salle"]
        if t["kind"] == "levier":
            verifier_cases({tid: (s_, t["cell"])}, "l", "levier")
        elif t["kind"] == "cibles":
            verifier_cases({tid: (s_, t["cibles"])}, "S", "cible")
        elif t["kind"] == "torches":
            verifier_cases({tid: (s_, t["torches"])}, "f", "torche")
        elif t["kind"] == "plaques":
            verifier_cases({tid: (s_, [c for c, _ in t["plaques"]])}, "p", "plaque")
        if t["porte"] not in PORTES or PORTES[t["porte"]][0] != "I":
            err("%s : la porte cible doit être de type I" % tid)
    # chaque porte I a un déclencheur, et un seul
    for pid, (typ, a, b) in PORTES.items():
        if typ == "I":
            n = sum(1 for t in DECLENCHEURS.values() if t["porte"] == pid)
            if n != 1:
                err("%s : %d déclencheur(s) au lieu de 1" % (pid, n))
    for iid, (salle, cases) in INDICES.items():
        for (c, r) in cases:
            if salles[salle][r][c] != "i":
                err("%s : indice %s absent en (%d,%d)" % (salle, iid, c, r))
    verifier_cases(STATUES, "R", "statue du corbeau")
    nb = lambda ch: sum(l.count(ch) for g in salles.values() for l in g)
    attendu = {
        "C": len(COFFRES), "F": len(RAMASSABLES), "T": sum(len(v[1]) for v in CHUTES.values()),
        "l": sum(1 for t in DECLENCHEURS.values() if t["kind"] == "levier"),
        "S": sum(len(t["cibles"]) for t in DECLENCHEURS.values() if t["kind"] == "cibles"),
        "p": sum(len(t["plaques"]) for t in DECLENCHEURS.values() if t["kind"] == "plaques"),
        "v": len(ESCALIERS), "^": len(ESCALIERS), "R": len(STATUES),
        "f": sum(len(t["torches"]) for t in DECLENCHEURS.values() if t["kind"] == "torches"),
    }
    for ch, n in attendu.items():
        if nb(ch) != n:
            err("%d %r dans les aperçus pour %d déclarés" % (nb(ch), ch, n))
    # braseros (Y) : au moins un par salle à torches
    for tid, t in DECLENCHEURS.items():
        if t["kind"] == "torches" and not any("Y" in l for l in salles[t["salle"]]):
            err("%s : pas de brasero allumé dans la salle" % tid)
    # ennemis jamais collés à une arrivée (>= 3 cases)
    for n, g in salles.items():
        sp = [(c, r) for r, l in enumerate(g) for c, ch in enumerate(l) if ch == "P"]
        for r, l in enumerate(g):
            for c, ch in enumerate(l):
                if ch in "EL" and min(((c - a) ** 2 + (r - b) ** 2) ** 0.5 for a, b in sp) < 3:
                    err("%s : ennemi en (%d,%d) trop près d'une arrivée" % (n, c, r))
        # Spawn pas contre un trou
        for (a, b) in sp:
            for dc in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    if g[b + dr][a + dc] in "~T":
                        err("%s : Spawn (%d,%d) contre un trou" % (n, a, b))
    # règles blocs : pas de bloc dans une salle à trous, ni de cible/torche (ligne de tir)
    for n, g in salles.items():
        txt = "".join("".join(l) for l in g)
        if "B" in txt and any(ch in txt for ch in "~TSfY"):
            err("%s : bloc dans une salle à trous, cibles ou torches" % n)
    print("  Brann %dx%d px ; passage porte haut/bas %d px, gauche/droite %d px ; couloirs d'une case = 32 px : OK"
          % (BRANN_LARGEUR_PX, BRANN_HAUTEUR_PX, PASSAGE_PORTE_VERTICALE_PX, PASSAGE_PORTE_HORIZONTALE_PX))
    print("  portée de la flèche : %d px (+ ~20 px), utilisée : %d cases ; vitesse de Brann : %.3f cases/s"
          % (PORTEE_FLECHE_PX, PORTEE_CASES, VITESSE_CASES_S))
    print("  %d salles lues (%d au sol, %d au sous-sol, dont 1 salle de boss), %d coffres, %d portes, "
          "%d escaliers, %d trous de passage, %d énigmes à déclencheur"
          % (len(salles), sum(1 for n in salles if ETAGE.get(n) == "RDC"),
             sum(1 for n in salles if ETAGE.get(n) == "B1"), len(COFFRES), len(PORTES), len(ESCALIERS),
             len(CHUTES), len(DECLENCHEURS)))


def CHUTES_AS_ZONES():
    return {k: (v[0], v[1]) for k, v in CHUTES.items()}


SCHEMA = """ ÉTAGE (rez-de-chaussée)
                                            [boss]
                                              G
                                              |
                              [10]=====I====[09]
                               |             N
                               |             |
                [06]=====I====[07]=====D====[08]
                 D
                 |
  [03]----------[02]----------[04]=====N====[05]
                 |
                 |
                [01] --> forêt

 SOUS-SOL
                              [12]          [11]
                               I             |
                              [14]=====D====[13]

                              [15]

 Liens d'étage : escaliers 05-15, 09-11, 10-12 ; trous de passage 04 -> 15 et 07 -> 12 (sens unique).
 Légende : - passage libre, D petite clé, G grande clé, N tous les ennemis morts, I interrupteur (levier, cibles,
 plaques ou torches), = porte entre deux salles."""


def apercu():
    print("\n== Plan des salles ==")
    print(SCHEMA)


def main():
    dossier = Path(__file__).parent
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chemin_plan = args[0] if args else dossier / "plan.md"
    plan = lire_plan(chemin_plan)
    verifier_structure(plan)
    if not erreurs:
        res = verifier_donjon(plan)
        if not erreurs:
            verifier_etages(plan, res)
            verifier_enigmes(plan, res)
            verifier_blocs(plan, res)
            autotest(plan)
    apercu()
    print()
    if erreurs:
        print("RÉSULTAT : %d erreur(s)" % len(erreurs))
        sys.exit(1)
    print("RÉSULTAT : toutes les vérifications passent.")


if __name__ == "__main__":
    main()
