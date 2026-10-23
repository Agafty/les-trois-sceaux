import sys
from PIL import Image
src = sys.argv[1]; out = sys.argv[2]
names = ['brann','corvan','corvan_corrupted','hulda','pip','tobias','isolde','garrick']
bg = (106,146,88,255)
img = Image.new('RGBA',(len(names)*34, 4*34), bg)
for i,n in enumerate(names):
    s = Image.open(f'{src}/{n}.png').convert('RGBA')
    for r in range(4):
        img.alpha_composite(s.crop((0,r*32,32,r*32+32)), (i*34+1, r*34+1))
img.save(out.replace('.png','_x1.png'))
img.resize((img.width*4,img.height*4),Image.NEAREST).save(out)
