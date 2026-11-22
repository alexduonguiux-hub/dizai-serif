#!/usr/bin/env python3
"""QA họ chữ có dấu (S77, designer 23/11 "Kiểm tra lại hết"): nét mảnh nhỏ nhất (stroke_balance.measure phân vị 2) của mỗi chữ có dấu
so với chữ gốc (Ờ ↔ O, Ữ ↔ U, ằ ↔ a …) — lệch > 2.5 u báo; + đỉnh A (mặt cắt) và eo B mọi weight.
    python3 tools/construct/qa_family.py <outlines.json>"""
import json, sys, os, unicodedata, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, 'golden')]
import stroke_balance as SB
O = json.load(open(sys.argv[1])); W = ('Regular', 'Medium', 'SemiBold', 'Bold')
HORN = '̛'
def base(c):
    n = unicodedata.normalize('NFD', c); b = n[0]
    return b if b != c and b.isalpha() else None
bad = []; cache = {}
import golden as GD
def body(d, ref):
    """chỉ contour THÂN: bỏ contour dấu nằm hẳn trên đỉnh / dưới chân chữ gốc (sừng dính thân → giữ)"""
    yr = [p[1] for c in GD.parse(ref) for p in GD.pts_of(c)]; y0, y1 = min(yr), max(yr)
    keep = []
    for c in GD.parse(d):
        ys = [p[1] for p in GD.pts_of(c)]
        if ys and not (min(ys) > y1 + 5 or max(ys) < y0 - 5): keep.append(c)
    return GD.fmt(keep)
def m(k, ref=None):
    key = (k, ref)
    if key not in cache: cache[key] = SB.measure([body(O[k], O[ref]) if ref else O[k]])[0]
    return cache[key]
chars = sorted({k.rsplit('-', 1)[0] for k in O})
for c in chars:
    b = base(c)
    if not b or b in 'iIjJ': continue
    for w in W:
        if f'{c}-{w}' not in O or f'{b}-{w}' not in O: continue
        t, tb = m(f'{c}-{w}', f'{b}-{w}'), m(f'{b}-{w}')
        if t < tb - 2.5 or t > tb + 2.5: bad.append((c, w, round(t, 1), b, round(tb, 1)))
print('chữ có dấu lệch nét mảnh chữ gốc > 2.5 u:', len(bad))
for x in bad[:60]: print('   ', *x)
def apex(d):
    ys = [float(v) for v in re.findall(r'-?\d+\.\d+|-?\d+', d)[1::2]]
    pts = re.findall(r'(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)', d); ymax = max(float(y) for x, y in pts)
    xs = sorted({round(float(x), 2) for x, y in pts if abs(float(y) - ymax) < 0.6})
    return round(xs[-1] - xs[0], 1) if len(xs) >= 2 else 0.0
print('mặt cắt đỉnh A:', {w: apex(O[f'A-{w}']) for w in W if f'A-{w}' in O})
