import sys, os
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
names = sys.argv[3:]
cells = []
for n in names:
    im = Image.open(os.path.join(src, n + '.png')).convert('RGBA')
    for r in range(im.height // 32):
        for c in range(im.width // 32):
            cell = im.crop((c*32, r*32, c*32+32, r*32+32))
            if cell.getbbox(): cells.append(cell)
per = 8
rows = (len(cells) + per - 1) // per
img = Image.new('RGBA', (per*34, rows*34), (106,146,88,255))
for i, c in enumerate(cells):
    img.alpha_composite(c, ((i % per)*34+1, (i//per)*34+1))
img.resize((img.width*4, img.height*4), Image.NEAREST).save(out)
