#!/usr/bin/env python3
"""QA chiều contour (S82, designer 23/11 "preview vẫn hiện lỗi Ơ" — lòng bị tô kín): contour nằm trong một contour khác phải NGƯỢC chiều
contour chứa nó (SVG / canvas tô nonzero). Báo mọi glyph × weight sai.
    python3 tools/construct/qa_dirs.py <outlines.json>"""
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, 'golden')]
import golden as GD
O = json.load(open(sys.argv[1])); bad = []
def inside(q, P):
    k = 0
    for i in range(len(P)):
        (x1, y1), (x2, y2) = P[i - 1], P[i]
        if (y1 > q[1]) != (y2 > q[1]) and q[0] < x1 + (q[1] - y1)*(x2 - x1)/(y2 - y1): k += 1
    return k % 2 == 1
for k, d in O.items():
    PL = GD.polys(GD.parse(d)); A = [sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(P, P[1:] + P[:1])) for P in PL]
    for i, P in enumerate(PL):
        par = [j for j, Q in enumerate(PL) if j != i and abs(A[j]) > abs(A[i]) and inside(P[0], Q)]
        if par:
            j = min(par, key=lambda j: abs(A[j]))
            if (A[i] > 0) == (A[j] > 0): bad.append(k); break
print('contour lòng cùng chiều contour ngoài (lòng bị tô kín):', len(bad), sorted(bad)[:40])
