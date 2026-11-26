#!/usr/bin/env python3
"""Đánh giá kerning so với font serif tham chiếu (designer 26/11 "đánh giá lại toàn bộ kerning").
Cùng thước đo với ref_kern.py: W(a, b) = khe nhỏ nhất + độ sâu trắng trung bình (giới hạn 0.12 x-height), chia cho W(H, H) (vùng cap)
hoặc W(n, n) (vùng x). So tỉ số của font mình với [trung vị, min, max] của các font tham chiếu (out/construct/ref_ratios.json).
    python3 qa_kern_ref.py <font.otf> [nhãn]
In: số cặp lệch, cặp SÁT hơn mọi font tham chiếu, cặp XA hơn mọi font tham chiếu (xếp theo độ lệch so với trung vị)."""
import sys, os, json, itertools
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ref_kern import Ref, white, CHARS, STEP, is_lower
HERE = os.path.dirname(os.path.abspath(__file__))
RR = json.load(open(os.path.join(HERE, '../../out/construct/ref_ratios.json')))
def audit(path, wref='Regular', tol=0.08):
    r = Ref(path); ys = np.arange(-250.0, 951.0, STEP); D = 0.12*r.xh
    def W(a, b):
        band = (0.0, r.xh) if (is_lower(a) or is_lower(b)) else (0.0, 700.0)
        return white(r.prof(a, ys), r.prof(b, ys), r.adv(a), r.kern(a, b), band, ys, D)
    nn, HH = W('n', 'n'), W('H', 'H')
    tight, loose, n = [], [], 0
    for a, b in itertools.product(CHARS, CHARS):
        p = a + b
        if p not in RR[wref]: continue
        v = W(a, b)
        if v is None: continue
        ratio = v/(nn if (is_lower(a) or is_lower(b)) else HH)
        med, lo, hi = RR[wref][p]; n += 1
        if ratio < lo - tol: tight.append((round(ratio - med, 3), p, round(ratio, 3), med, lo, hi))
        elif ratio > hi + tol: loose.append((round(ratio - med, 3), p, round(ratio, 3), med, lo, hi))
    return n, sorted(tight), sorted(loose, reverse=True)
if __name__ == '__main__':
    f = sys.argv[1]; lab = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(f)
    wref = 'Bold' if 'Bold' in lab or 'Bold' in f else 'Regular'
    n, t, l = audit(f, wref)
    print(f'{lab}: {n} cặp · SÁT hơn mọi tham chiếu: {len(t)} · XA hơn mọi tham chiếu: {len(l)}')
    print('  sát nhất:', ' '.join(f'{p}({x:+.2f})' for x, p, *_ in t[:30]))
    print('  xa nhất :', ' '.join(f'{p}({x:+.2f})' for x, p, *_ in l[:30]))
