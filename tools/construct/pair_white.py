#!/usr/bin/env python3
"""Kiểm trắng cặp S1c (skill type-qa-qc §3.1) cho Đìzai Serif, so với dải font tham chiếu (ref_kern.py → ref_ratios.json).
    python3 tools/construct/pair_white.py [weight] [cặp,cặp,…]
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'ref'))
import spacing as SPc
from make_ref import outline
from ref_kern import white
OUT = os.path.join(HERE, '..', '..', 'out', 'construct')
XH, CAP = 495.0, 700.0; D = 0.12*XH

class Ours:
    def __init__(self, w, kern=True):
        self.w = w; self.O = json.load(open(os.path.join(OUT, 'outlines.json'))); self.SP = json.load(open(os.path.join(OUT, 'spacing.json')))
        self.K = json.load(open(os.path.join(OUT, 'kerning.json'))) if kern else None; self.cache = {}
    def prof(self, c):
        if c not in self.cache:
            L, R = SPc.profile(outline([self.O[f'{c}-{self.w}']])); d = self.SP[self.w][c]['dx']; self.cache[c] = (L + d, R + d)
        return self.cache[c]
    def kern(self, a, b):
        if self.K is None: return 0.0
        K = self.K[self.w]; v = K['exc'].get(f'{a}|{b}')
        return K['class'].get(f'{SPc.rclass(a)}|{SPc.lclass(b)}', 0.0) if v is None else v
    def W(self, a, b, kern=None):
        band = (0.0, XH) if (a.islower() or b.islower()) else (0.0, CAP)
        k = self.kern(a, b) if kern is None else kern
        return white(self.prof(a), self.prof(b), self.SP[self.w][a]['adv'], k, band, SPc.YS, D)
    def ratio(self, a, b):
        ref = self.W('n', 'n', 0.0) if (a.islower() or b.islower()) else self.W('H', 'H', 0.0)
        return self.W(a, b)/ref

if __name__ == '__main__':
    w = sys.argv[1] if len(sys.argv) > 1 else 'Regular'
    R = json.load(open(os.path.join(OUT, 'ref_ratios.json')))[w if w in ('Regular', 'Bold') else 'Regular']
    o = Ours(w)
    pairs = sys.argv[2].split(',') if len(sys.argv) > 2 else list(R)
    out = []
    for p in pairs:
        if p not in R: continue
        r = o.ratio(*p); med, lo, hi = R[p]
        out.append((p, round(r, 3), med, lo, hi, 'trong dải' if lo - 0.02 <= r <= hi + 0.02 else ('THƯA' if r > hi else 'CHẬT')))
    if len(pairs) < 60:
        for t in out: print(*t)
    else:
        import collections
        c = collections.Counter(t[5] for t in out); print(w, dict(c))
        for lab in ('THƯA', 'CHẬT'):
            L = sorted([t for t in out if t[5] == lab], key=lambda t: -abs(t[1] - t[2]))[:40]
            print(lab, [(t[0], t[1], t[2]) for t in L])
