import sys, os, importlib
import engine
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)
names = sys.argv[2:] or ['corvan']
for n in names:
    m = importlib.import_module(n)
    img = engine.build(n, m.VIEWS, m.HIP, m.LEGMID, OUT, hip_side=getattr(m, 'HIP_SIDE', None), overlays=getattr(m, 'OVERLAYS', None))
    engine.preview(img, os.path.join(OUT, f'_preview_{n}.png'))
    if hasattr(m, 'CORRUPT'):
        img = engine.build(n + '_corrupted', m.VIEWS, m.HIP, m.LEGMID, OUT, remap=m.CORRUPT, hip_side=getattr(m, 'HIP_SIDE', None))
        engine.preview(img, os.path.join(OUT, f'_preview_{n}_corrupted.png'))
