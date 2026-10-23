"""Animations spéciales : attaque/dégât/objet levé/mort de Brann, marteau et pose blessée de Corvan,
Pip accroupi, et l'effet de coup d'épée (sprite séparé, placé devant Brann par le code).

Usage : python3 actions.py <dossier art/characters>
"""
import sys, os, math, copy
from PIL import Image
import engine
from engine import PALETTE, rgba, grid, mirror, shift_up_body
import corvan, pip

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
REV = {rgba(v)[:3]: k for k, v in PALETTE.items() if v and k != 'e'}


def load_grid(png, col, row):
    im = Image.open(png).convert('RGBA')
    g = []
    for y in range(32):
        line = []
        for x in range(32):
            p = im.getpixel((col * 32 + x, row * 32 + y))
            line.append(REV[p[:3]] if p[3] else '.')
        g.append(line)
    return g


def paint(g, x, y, s):
    """Écrit la chaîne s à partir de (x, y). '.' = inchangé, '_' = transparent."""
    for i, c in enumerate(s):
        if 0 <= x + i < 32 and 0 <= y < 32 and c != '.':
            g[y][x + i] = '.' if c == '_' else c


def paint_rows(g, x, y, rows):
    for i, r in enumerate(rows):
        paint(g, x, y + i, r)


def cp(g):
    return copy.deepcopy(g)


def rotate_lying(side, bottom=31):
    """Couche un personnage vu de profil (tête à gauche) et le pose au sol."""
    h = [y for y in range(32) if any(c != '.' for c in side[y])]
    w = [x for x in range(32) if any(side[y][x] != '.' for y in range(32))]
    y0, y1, x0, x1 = h[0], h[-1], w[0], w[-1]
    # rotation de 90° : la tête (haut) va à gauche
    rot = [[side[y][x] for y in range(y0, y1 + 1)] for x in range(x1, x0 - 1, -1)]
    rh, rw = len(rot), len(rot[0])
    g = [['.'] * 32 for _ in range(32)]
    ox, oy = (32 - rw) // 2, bottom - rh + 1
    for y in range(rh):
        for x in range(rw):
            if rot[y][x] != '.':
                g[oy + y][ox + x] = rot[y][x]
    return g


def save_sheet(frames_rows, path, remap=None):
    pal = dict(PALETTE)
    if remap:
        pal.update(remap)
    w = max(len(r) for r in frames_rows) * 32
    img = Image.new('RGBA', (w, len(frames_rows) * 32), (0, 0, 0, 0))
    px = img.load()
    for r, frames in enumerate(frames_rows):
        for c, g in enumerate(frames):
            if g is None:
                continue
            for y in range(32):
                for x in range(32):
                    col = pal[g[y][x]]
                    if col:
                        px[c * 32 + x, r * 32 + y] = rgba(col)
    img.save(path)
    return img


# ---------------------------------------------------------------- Brann
B = os.path.join(OUT, 'brann.png')
b_down, b_up, b_left = (load_grid(B, 0, r) for r in (0, 1, 2))

SWORD_UP = [  # épée tenue pointe en haut (lame, garde, poignée)
    ".00.",
    "0gh0",
    "0gh0",
    "0gh0",
    "0gh0",
    "0gh0",
    "0gh0",
    "0gh0",
    "0gh0",
    "0KKK0",
    ".0D0",
    ".0D0",
]


def erase_front_arm(g, right=False):
    """Retire le bras gauche de l'écran (colonnes 4-8, lignes 17-25) en vue face/dos."""
    if right:
        g = mirror(g)
    for y in range(17, 26):
        for x in range(3, 8):
            g[y][x] = '.'
        if y <= 24:
            g[y][8] = '0'
    g[25][8] = '0'
    for y in (17, 18, 19):
        g[y][9] = '9'
    return mirror(g) if right else g


def raised_arm(g, right=False):
    """Bras levé au-dessus de l'épaule, épée pointe en haut."""
    if right:
        g = mirror(g)
    paint_rows(g, 0, 0, [r for r in SWORD_UP])
    paint_rows(g, 0, 12, [
        "0CCG0",
        "0CCG0",
        ".09220",
        "..09220",
        "...09220",
    ])
    return mirror(g) if right else g


def front_strike(g, x_glove, grip=True):
    """Main tenant la poignée devant le corps (vue face), lame dans l'effet séparé."""
    paint_rows(g, 4, 18, [
        "0922",
        "09220",
        ".09220",
    ])
    paint_rows(g, x_glove - 1, 21, [
        "000000",
        "0CCCG0",
        "0CCCG0",
        "000000",
    ])
    if grip:
        paint_rows(g, x_glove, 25, [".0D0", ".0K0", "0KKK0"[:4]])
    return g


def closed_eyes_front(g):
    for x in (12, 19):
        g[10][x] = '3'
    for x in (11, 12, 13, 18, 19, 20):
        g[11][x] = '0'
    return g


def closed_eyes_side(g):
    g[10][8] = '3'
    g[11][7], g[11][8], g[11][9] = '0', '0', '0'
    return g


# attaque vue de face
a_down1 = raised_arm(erase_front_arm(cp(b_down)))
a_down2 = front_strike(erase_front_arm(shift_up_body(cp(b_down), 27)), 12)
a_down3 = front_strike(erase_front_arm(cp(b_down)), 16)

# attaque vue de dos (main droite = côté droit de l'écran)
a_up1 = raised_arm(erase_front_arm(cp(b_up), right=True), right=True)
a_up2 = erase_front_arm(shift_up_body(cp(b_up), 27), right=True)
paint_rows(a_up2, 19, 8, [  # bras tendu vers le haut, devant la tête
    "..0000",
    ".0CCG0",
    ".0CCG0",
    ".09220",
    ".09220",
    "092220",
    "09220.",
    "0920..",
])
a_up3 = erase_front_arm(cp(b_up), right=True)
paint_rows(a_up3, 17, 12, [
    "000000",
    "0CCCG0",
    "0CCCG0",
    "000920",
    "..09220",
    "...0920",
])


def erase_side_arm(g):
    for y in range(18, 25):
        for x in range(12, 17):
            g[y][x] = g[y][17]
    for x in range(13, 17):
        g[25][x] = '9'
    return g


# attaque de profil (tourné à gauche)
a_left1 = erase_side_arm(cp(b_left))
paint_rows(a_left1, 18, 2, [r for r in SWORD_UP])
paint_rows(a_left1, 17, 14, [
    "0CCG0",
    "0CCG0",
    "09220",
    ".0920",
])
a_left2 = erase_side_arm(shift_up_body(cp(b_left), 28))
paint_rows(a_left2, 1, 17, [
    "0000000000000",
    "0CCG022222220",
    "0CCG099999990",
    "00000000000..",
])
a_left3 = erase_side_arm(cp(b_left))
paint_rows(a_left3, 3, 20, [
    "...00000000",
    "..0222222220",
    "0000999990..",
    "0CCG0000....",
    "0CCG0.......",
    "00000.......",
])

# dégât : rebond, yeux fermés
hurt_down = closed_eyes_front(shift_up_body(cp(b_down), 27))
hurt_up = shift_up_body(cp(b_up), 27)
hurt_left = closed_eyes_side(shift_up_body(cp(b_left), 28))

# objet levé au-dessus de la tête (vue de face)
lift = erase_front_arm(erase_front_arm(cp(b_down)), right=True)
for side in (False, True):
    lift = mirror(lift) if side else lift
    paint_rows(lift, 1, 4, [
        "0000",
        "0CCG0",
        "0CCG0",
        "00920",
        ".09220",
        ".092220",
        "..09220",
        "..092220",
        "...09220",
        "...092220",
        "....09220",
        "....092220",
        ".....09220",
    ])
    lift = mirror(lift) if side else lift

# mort : à genoux, puis couché
death1 = [['.'] * 32 for _ in range(32)]
for y in range(0, 27):
    death1[y + 3] = cp(b_down)[y]
closed_eyes_front(death1)
paint_rows(death1, 7, 29, ["0AAAAA00000AAAAA0"[:18], "000000000000000000"])
death2 = closed_eyes_side(cp(b_left))
death2 = rotate_lying(death2)

brann_actions = [
    [a_down1, a_down2, a_down3, hurt_down, lift],
    [a_up1, a_up2, a_up3, hurt_up, death1],
    [a_left1, a_left2, a_left3, hurt_left, death2],
    [mirror(a_left1), mirror(a_left2), mirror(a_left3), mirror(hurt_left), None],
]
save_sheet(brann_actions, os.path.join(OUT, 'brann_actions.png'))


# ---------------------------------------------------------------- Effet de coup d'épée
def slash_frame(facing, a_deg, trail):
    fx, fy = facing
    px_, py_ = fy, -fx                      # perpendiculaire
    cx, cy = 16 - fx * 12, 16 - fy * 12     # pivot : bord de la case côté Brann
    g = [['.'] * 32 for _ in range(32)]

    def at(r, a):
        a = math.radians(a)
        dx = math.cos(a) * fx + math.sin(a) * px_
        dy = math.cos(a) * fy + math.sin(a) * py_
        return round(cx + r * dx), round(cy + r * dy)

    if trail:  # traînée de l'arc
        lo, hi = trail
        a = lo
        while a <= hi:
            for r in (12, 13):
                x, y = at(r, a)
                if 0 <= x < 32 and 0 <= y < 32:
                    g[y][x] = 'g' if r == 13 else 'h'
            a += 2
    blade = set()
    for r10 in range(30, 130):
        x, y = at(r10 / 10, a_deg)
        blade.add((x, y))
    hilt = set()
    for r10 in range(0, 30):
        hilt.add(at(r10 / 10, a_deg))
    for (x, y) in blade | hilt:  # contour
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= x + dx < 32 and 0 <= y + dy < 32 and g[y + dy][x + dx] in '.hg':
                    g[y + dy][x + dx] = '0'
    for (x, y) in blade:
        if 0 <= x < 32 and 0 <= y < 32:
            g[y][x] = 'g'
    for (x, y) in hilt:
        if 0 <= x < 32 and 0 <= y < 32:
            g[y][x] = 'D'
    gx, gy = at(3, a_deg)
    if 0 <= gx < 32 and 0 <= gy < 32:
        g[gy][gx] = 'K'
    return g


slash = []
for facing in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
    slash.append([slash_frame(facing, -60, None),
                  slash_frame(facing, 0, (-80, -4)),
                  slash_frame(facing, 60, (-40, 56))])
save_sheet(slash, os.path.join(OUT, 'sword_slash.png'))

# ---------------------------------------------------------------- Corvan
C = os.path.join(OUT, 'corvan.png')
c_down, c_left = load_grid(C, 0, 0), load_grid(C, 0, 2)
HAMMER_UP = [
    "0000000",
    "0hhghh0",
    "0hkkkh0",
    "0000000",
    "..060..",
    "..060..",
]


def corvan_erase_arm(g):
    for y in range(13, 26):
        for x in range(2, 7):
            g[y][x] = '.'
        if 14 <= y <= 24:
            g[y][7] = '0'
    for y in range(14, 25):
        if g[y][8] == '0':
            g[y][8] = '2'
    return g


h1 = corvan_erase_arm(cp(c_down))
paint_rows(h1, 0, 4, HAMMER_UP)
paint_rows(h1, 1, 10, [
    "0CCG0",
    "0CCG0",
    "09220",
    ".09220",
    "..09220",
])
h2 = corvan_erase_arm(cp(c_down))
paint_rows(h2, 4, 16, [
    "0922",
    "09220",
    ".09220",
    "..0922000",
    "...0CCCG0",
    "...0CCCG0",
    "...000600",
    ".....060.",
])
paint_rows(h2, 9, 24, [
    "00000000",
    "0hhghhh0",
    "0hkkkkh0",
    "00000000",
])
h3 = cp(h2)
paint_rows(h3, 6, 22, ["____"])  # léger rebond : marteau remonté d'un pixel
h3 = [row[:] for row in h3]
for y in range(22, 28):
    for x in range(9, 17):
        h3[y - 1][x] = h3[y][x]
for x in range(9, 17):
    h3[27][x] = h2[28][x] if h2[28][x] != '.' else c_down[27][x]
wounded = rotate_lying(c_left)
for y in range(32):
    for x in range(32):
        if wounded[y][x] == 'e':
            wounded[y][x] = '0'

corvan_actions = [[h1, h2, h3, wounded]]
save_sheet(corvan_actions, os.path.join(OUT, 'corvan_actions.png'))
save_sheet(corvan_actions, os.path.join(OUT, 'corvan_corrupted_actions.png'), remap=corvan.CORRUPT)

# ---------------------------------------------------------------- Pip accroupi
p_down = load_grid(os.path.join(OUT, 'pip.png'), 0, 0)
crouch = [['.'] * 32 for _ in range(32)]
for y in range(9, 27):          # tête + tunique descendent de 3 px
    crouch[y + 3] = p_down[y][:]
for y in (29, 30, 31):
    crouch[y] = p_down[y][:]
paint_rows(crouch, 9, 18, [    # mains sur le bonnet
    "000",
    "0330",
])
paint_rows(crouch, 20, 18, [
    ".000",
    "0330",
])
save_sheet([[crouch]], os.path.join(OUT, 'pip_actions.png'))
print('ok')
