#!/usr/bin/env python3
"""Tỉ số TRẮNG CẶP của font tham chiếu (skill type-qa-qc §3.1 S1c — phương pháp đo của DINHTUONG60s; designer 05/11: "hãy dùng
skill kerning của Dinh Tuong đã đo sẵn").
    python3 tools/construct/ref_kern.py   → out/construct/ref_ratios.json

Trắng cặp W(a, b): trung bình theo cao độ (vùng x-height với cặp có chữ thường, vùng cap với cặp hoa / số) của
    (khe giữa hai mép mực ngoài cùng) + trắng phía phải của a + trắng phía trái của b,
mỗi phía đo từ MÉP MỰC NGOÀI CÙNG của chính chữ đó, chặn ở độ sâu D = 0.12 × x-height (cao độ không có mực tính đủ D).
Kerning GPOS của font tham chiếu được tính vào. Tỉ số = W(a, b) / W(n, n) (vùng x) hoặc / W(H, H) (vùng cap).
Font tham chiếu: serif có sẵn trong máy, Regular + Bold. Lưu trung vị (và min / max) cho mọi cặp A–Z a–z 0–9.
"""
import json, os, sys, itertools
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'out', 'construct')
REFS = {
    'Regular': ['/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
                '/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf', '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'],
    'Bold': ['/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
             '/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf', '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf'],
}
CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
STEP = 4.0

def flatten(rec):
    polys = []; cur = []; p = None
    for op, args in rec.value:
        if op == 'moveTo': cur = [args[0]]; p = args[0]
        elif op == 'lineTo': cur.append(args[0]); p = args[0]
        elif op == 'curveTo':
            a, b, c = args; d0 = p
            for k in range(1, 13):
                t = k/12; u = 1 - t
                cur.append((u**3*d0[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t**3*c[0], u**3*d0[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t**3*c[1]))
            p = c
        elif op == 'qCurveTo':
            pts = [p] + list(args)
            # tách chuỗi quadratic có điểm ngầm
            on = pts[0]
            offs = pts[1:-1]; last = pts[-1]
            segs = []
            for i, q in enumerate(offs):
                nxt = last if i == len(offs) - 1 else ((q[0] + offs[i + 1][0])/2, (q[1] + offs[i + 1][1])/2)
                segs.append((on, q, nxt)); on = nxt
            if not offs: cur.append(last)
            for a, b, c in segs:
                for k in range(1, 9):
                    t = k/8; u = 1 - t
                    cur.append((u*u*a[0] + 2*u*t*b[0] + t*t*c[0], u*u*a[1] + 2*u*t*b[1] + t*t*c[1]))
            p = last
        elif op in ('closePath', 'endPath'):
            if cur: polys.append(cur)
            cur = []
    return polys

def profile(polys, ys):
    L = np.full(len(ys), np.nan); R = np.full(len(ys), np.nan)
    for poly in polys:
        P = np.array(poly + [poly[0]])
        for (x0, y0), (x1, y1) in zip(P[:-1], P[1:]):
            if y0 == y1: continue
            lo, hi = min(y0, y1), max(y0, y1)
            m = (ys >= lo) & (ys < hi)
            if not m.any(): continue
            x = x0 + (ys[m] - y0)*(x1 - x0)/(y1 - y0)
            L[m] = np.fmin(L[m], x); R[m] = np.fmax(R[m], x)
    return L, R

class Ref:
    def __init__(self, path):
        f = TTFont(path); self.f = f; self.gs = f.getGlyphSet(); self.cmap = f.getBestCmap()
        self.hmtx = f['hmtx'].metrics
        self.cache = {}
        hb = self.bounds('H'); xb = self.bounds('x')
        self.s = 700.0/hb[3]                         # chuẩn hoá: cap = 700
        self.xh = xb[3]*self.s
        self.kern = self._gpos()
    def gname(self, ch): return self.cmap.get(ord(ch))
    def bounds(self, ch):
        from fontTools.pens.boundsPen import BoundsPen
        bp = BoundsPen(self.gs); self.gs[self.gname(ch)].draw(bp); return bp.bounds
    def prof(self, ch, ys):
        key = (ch, len(ys), ys[0])
        if key not in self.cache:
            rp = DecomposingRecordingPen(self.gs); self.gs[self.gname(ch)].draw(rp)
            polys = [[(x*self.s, y*self.s) for x, y in p] for p in flatten(rp)]
            self.cache[key] = profile(polys, ys)
        return self.cache[key]
    def adv(self, ch): return self.hmtx[self.gname(ch)][0]*self.s
    def _gpos(self):
        K = {}
        if 'GPOS' not in self.f: return lambda a, b: 0.0
        g = self.f['GPOS'].table
        idx = set()
        for fr in g.FeatureList.FeatureRecord:
            if fr.FeatureTag == 'kern': idx.update(fr.Feature.LookupListIndex)
        subs = []
        for i in sorted(idx):
            lk = g.LookupList.Lookup[i]
            for st in lk.SubTable:
                if lk.LookupType == 9: st = st.ExtSubTable
                if getattr(st, 'LookupType', 2) == 2 or st.__class__.__name__ == 'PairPos': subs.append(st)
        def kern(a, b):
            ga, gb = self.gname(a), self.gname(b)
            for st in subs:
                cov = st.Coverage.glyphs
                if ga not in cov: continue
                if st.Format == 1:
                    ps = st.PairSet[cov.index(ga)]
                    for pv in ps.PairValueRecord:
                        if pv.SecondGlyph == gb:
                            v = getattr(pv.Value1, 'XAdvance', 0) if pv.Value1 else 0; return (v or 0)*self.s
                elif st.Format == 2:
                    c1 = st.ClassDef1.classDefs.get(ga, 0); c2 = st.ClassDef2.classDefs.get(gb, 0)
                    rec = st.Class1Record[c1].Class2Record[c2]
                    v = getattr(rec.Value1, 'XAdvance', 0) if rec.Value1 else 0
                    if v: return v*self.s
            return 0.0
        return kern

def white(prof_a, prof_b, adv_a, kern, band, ys, D):
    (La, Ra), (Lb, Rb) = prof_a, prof_b
    m = (ys >= band[0]) & (ys <= band[1])
    Ra_, Lb_ = Ra[m], Lb[m]
    if np.all(np.isnan(Ra_)) or np.all(np.isnan(Lb_)): return None
    ra = np.nanmax(Ra_); lb = np.nanmin(Lb_)
    da = np.where(np.isnan(Ra_), D, np.minimum(ra - Ra_, D)); db = np.where(np.isnan(Lb_), D, np.minimum(Lb_ - lb, D))
    return float((lb + adv_a + kern - ra) + (da + db).mean())

def is_lower(c): return c.islower()

def main():
    res = {}
    for w, paths in REFS.items():
        refs = [Ref(p) for p in paths if os.path.exists(p)]
        per = {}
        for r in refs:
            ys = np.arange(-250.0, 951.0, STEP); D = 0.12*r.xh
            def W(a, b):
                band = (0.0, r.xh) if (is_lower(a) or is_lower(b)) else (0.0, 700.0)
                return white(r.prof(a, ys), r.prof(b, ys), r.adv(a), r.kern(a, b), band, ys, D)
            nn, HH = W('n', 'n'), W('H', 'H')
            for a, b in itertools.product(CHARS, CHARS):
                if r.gname(a) is None or r.gname(b) is None: continue
                v = W(a, b)
                if v is None: continue
                ref = nn if (is_lower(a) or is_lower(b)) else HH
                per.setdefault(a + b, []).append(v/ref)
        res[w] = {p: [round(float(np.median(v)), 4), round(min(v), 4), round(max(v), 4)] for p, v in per.items()}
        print(w, 'font tham chiếu', len(refs), '· cặp', len(res[w]), '· ví dụ', {p: res[w][p] for p in ('HA', 'RA', 'KA', 'XA', 'UA', 'AU', 'DA', 'AT', 'TA', 'AV', 'nn', 'oo', 'ox', 'va')})
    json.dump(res, open(os.path.join(OUT, 'ref_ratios.json'), 'w'))

if __name__ == '__main__':
    main()
