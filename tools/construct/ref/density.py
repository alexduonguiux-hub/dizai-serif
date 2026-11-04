import json, sys
sys.path.insert(0, '.'); sys.path.insert(0, '..')
from make_ref import outline
import diff, pathops
YMIN = {'1': 0, '3': -11.3, '2': 0, '5': -11.3, '6': -11.3, '9': -11.3, '7': 0}
def shift(p, dy):
    q = pathops.Path()
    for v, ps in p.segments:
        P = [(x, y + dy) for x, y in ps]
        if v == 'moveTo': q.moveTo(*P[0])
        elif v == 'lineTo': q.lineTo(*P[0])
        elif v == 'curveTo': q.cubicTo(*P[0], *P[1], *P[2])
        elif v == 'closePath': q.close()
    return q
def dens(p):
    A = diff.raster(p); xs = A.any(0).nonzero()[0]; W = xs.max() - xs.min()
    return A.sum() / ((W + 80) * 700), W
if __name__ == "__main__":
    A = json.load(open('designer_A.json')); B = json.load(open('designer_B.json')); raw = json.load(open('designer_boldfig_raw.json'))
    L = lambda k: outline((A.get(k) or B.get(k)))
    lr = [dens(L(f'{c}-Regular'))[0] for c in 'ABCDEFGHIJKLMNOPQRST']; lb = [dens(L(f'{c}-Bold'))[0] for c in 'ABCDEFGHIJKLMNOPQRST']
    ratio = sum(lb) / sum(lr)
    print('letters A–T: Regular %.3f  Bold %.3f  ratio %.3f' % (sum(lr) / 20, sum(lb) / 20, ratio))
    for c in '0123456789':
        r = dens(L(f'{c}-Regular'))[0]
        if c in raw: b, W = dens(shift(outline(raw[c]), YMIN[c])); src = 'designer'
        else: b, W = dens(L(f'{c}-Bold')); src = 'derived'
        print(c, 'Reg %.3f  Bold %.3f  ratio %.3f  (%s)  target %.3f' % (r, b, b / r, src, r * ratio))
