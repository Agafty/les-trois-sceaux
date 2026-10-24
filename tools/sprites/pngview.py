"""Outil de controle (hors jeu) : lit un PNG RGBA 8 bits produit par nos scripts (filtre 0 ou filtres standards),
et l'exporte agrandi (plus proche voisin) sur un fond uni, eventuellement recadre.
Usage : python pngview.py entree.png sortie.png facteur [x y w h] [fond_hex]"""
import struct
import sys
import zlib


def read_png(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n'
    i, idat = 8, b''
    while i < len(d):
        n, t = struct.unpack('>I4s', d[i:i + 8])
        body = d[i + 8:i + 8 + n]
        if t == b'IHDR':
            w, h, bd, ct = struct.unpack('>IIBB', body[:10])
            assert bd == 8 and ct == 6
        elif t == b'IDAT':
            idat += body
        i += 12 + n
    raw = zlib.decompress(idat)
    bpp, stride, rows, prev = 4, w * 4, [], bytearray(w * 4)
    for y in range(h):
        f = raw[y * (stride + 1)]
        cur = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for x in range(stride):
            a = cur[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                cur[x] = (cur[x] + a) & 255
            elif f == 2:
                cur[x] = (cur[x] + b) & 255
            elif f == 3:
                cur[x] = (cur[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                cur[x] = (cur[x] + pr) & 255
        rows.append([tuple(cur[x * 4:x * 4 + 4]) for x in range(w)])
        prev = cur
    return rows


def main():
    src, dst, k = sys.argv[1], sys.argv[2], int(sys.argv[3])
    rows = read_png(src)
    rest = sys.argv[4:]
    bg = (56, 46, 66, 255)
    if len(rest) in (1, 5):
        h = rest[-1].lstrip('#')
        bg = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    if len(rest) >= 4:
        x, y, w, h = map(int, rest[:4])
        rows = [r[x:x + w] for r in rows[y:y + h]]
    sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
    from coffres import save_png
    px = [[p if p[3] == 255 else bg for p in r] for r in rows]
    save_png(dst, px, k)


if __name__ == '__main__':
    main()
