"""QA tính độc đáo hình glyph: so AnNam Serif với các font khác bằng IoU mực sau chuẩn hoá (cap / x-height, đường chân, tâm ngang).
    python3 tools/construct/qa_similarity.py fonts/ttf/AnNamSerif-Regular.ttf <font tham chiếu …>
Mốc 06/11: font độc lập khác designer TB 0.57–0.70; cùng gốc (Trirong ↔ Taviraj) 0.78 với 20 glyph ≥ 0.85.
import glob, os, sys, json
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from skimage.draw import polygon as skpoly

H = 220                # px cho chiều cao chuẩn hoá (cap hoặc x-height)
GW, GH = 700, 520      # khung raster
BASE = 380             # hàng đường chân

def flatten(rec):
    polys, cur, p = [], [], None
    for op, args in rec.value:
        if op == 'moveTo': cur = [args[0]]; p = args[0]
        elif op == 'lineTo': cur.append(args[0]); p = args[0]
        elif op == 'curveTo':
            a, b, c = args
            for k in range(1, 13):
                t = k/12; u = 1 - t
                cur.append((u**3*p[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t**3*c[0], u**3*p[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t**3*c[1]))
            p = c
        elif op == 'qCurveTo' and args[-1] is None:          # contour toàn điểm điều khiển (điểm neo ngầm ở giữa)
            offs = list(args[:-1]); n = len(offs)
            mids = [((offs[i][0] + offs[(i+1) % n][0])/2, (offs[i][1] + offs[(i+1) % n][1])/2) for i in range(n)]
            cur = [mids[-1]]
            for i in range(n):
                a, q, b = mids[i-1], offs[i], mids[i]
                for k in range(1, 9):
                    t = k/8; u = 1 - t
                    cur.append((u*u*a[0] + 2*u*t*q[0] + t*t*b[0], u*u*a[1] + 2*u*t*q[1] + t*t*b[1]))
            p = cur[-1]
        elif op == 'qCurveTo':
            pts = [p] + list(args); on = pts[0]; offs = pts[1:-1]; last = pts[-1]
            if not offs: cur.append(last)
            for i, q in enumerate(offs):
                nxt = last if i == len(offs) - 1 else ((q[0] + offs[i+1][0])/2, (q[1] + offs[i+1][1])/2)
                for k in range(1, 9):
                    t = k/8; u = 1 - t
                    cur.append((u*u*on[0] + 2*u*t*q[0] + t*t*nxt[0], u*u*on[1] + 2*u*t*q[1] + t*t*nxt[1]))
                on = nxt
            p = last
        elif op in ('closePath', 'endPath'):
            if cur: polys.append(cur)
            cur = []
    return polys

class F:
    def __init__(self, path):
        f = TTFont(path)
        if 'fvar' in f:
            from fontTools.varLib.instancer import instantiateVariableFont
            loc = {a.axisTag: (400 if a.axisTag == 'wght' and a.minValue <= 400 <= a.maxValue else a.defaultValue) for a in f['fvar'].axes}
            f = instantiateVariableFont(f, loc)
        self.f = f; self.gs = f.getGlyphSet(); self.cmap = f.getBestCmap()
        self.name = os.path.basename(path).split('[')[0].replace('.ttf', '').replace('.otf', '')
        self.cap = self.height('H'); self.xh = self.height('x')
    def polys(self, ch):
        g = self.cmap.get(ord(ch))
        if g is None: return None
        rp = DecomposingRecordingPen(self.gs); self.gs[g].draw(rp); return flatten(rp)
    def height(self, ch):
        P = self.polys(ch); return max(q[1] for c in P for q in c)
    def mask(self, ch):
        P = self.polys(ch)
        if not P: return None
        s = H/(self.xh if ch.islower() else self.cap)
        xs = [q[0] for c in P for q in c]; cx = (min(xs) + max(xs))/2
        m = np.zeros((GH, GW), bool)
        for c in P:
            rr = [BASE - y*s for _, y in c]; cc = [GW/2 + (x - cx)*s for x, _ in c]
            r, k = skpoly(rr, cc, (GH, GW)); t = np.zeros((GH, GW), bool); t[r, k] = True; m ^= t
        return m

CH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
me = F(sys.argv[1]); refs = []
for p_ in sys.argv[2:]:
    try: refs.append(F(p_))
    except Exception as e: print('bỏ qua', os.path.basename(p_), type(e).__name__)
print('so với', len(refs), 'font')
M = {c: me.mask(c) for c in CH}
res = {}
for r in refs:
    row = {}
    for c in CH:
        b = r.mask(c)
        if b is None or M[c] is None: continue
        row[c] = float((M[c] & b).sum()/max(1, (M[c] | b).sum()))
    res[r.name] = row
# baseline: IoU giữa các font tham chiếu với nhau (mức "giống nhau tự nhiên" của chữ serif)
print('== IoU trung bình AnNam Serif so với từng font (62 glyph) — cao → giống')
for n, row in sorted(res.items(), key=lambda kv: -np.mean(list(kv[1].values()))):
    v = list(row.values()); top = sorted(row.items(), key=lambda kv: -kv[1])[:4]
    print(f'  {n:24} TB {np.mean(v):.3f}  max {max(v):.3f}  ≥0.85: {sum(x >= 0.85 for x in v):2d}  ≥0.90: {sum(x >= 0.90 for x in v):2d}   glyph gần nhất: ' + ' '.join(f'{c}{s:.2f}' for c, s in top))
allv = [(n, c, s) for n, row in res.items() for c, s in row.items()]
print('== 15 cặp glyph giống nhất')
for n, c, s in sorted(allv, key=lambda t: -t[2])[:15]: print(f'  {c}  {n:24} {s:.3f}')
json.dump(res, open('out/construct/qa_similarity.json', 'w'))
