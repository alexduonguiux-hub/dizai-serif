"""Outline TƯƠNG THÍCH Regular ↔ Bold cho variable font (cùng số contour, cùng chuỗi đoạn, cùng loại đoạn).
Dùng lại phép căn của ref/interp.py (ghép contour theo tâm + hộp, căn điểm neo bằng quy hoạch động vòng, tách đoạn dài nhất
khi một bên thừa neo). Phép tách giữ nguyên hình (de Casteljau) → master Regular / Bold trùng khít outline tĩnh.
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'ref'))
from interp import contours, area, reverse, align, tocubic

def _sarea(g, n=8):
    """diện tích có dấu theo đường cong LẤY MẪU (area() của interp chỉ dùng điểm neo: contour 2 đoạn cong — chấm i italic sau đơn
    giản hoá — có diện tích 0 → bị coi là ngược chiều, master Bold bị đảo, Medium / SemiBold chấm co lại)"""
    P = []
    for s in g:
        if s[0] == 'L': P.append(s[1])
        else:
            a, b, c, d = s[1:]
            for k in range(n):
                t = k/n; u = 1 - t
                P.append((u**3*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t**3*d[0], u**3*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t**3*d[1]))
    return sum(p[0]*q[1] - q[0]*p[1] for p, q in zip(P, P[1:] + P[:1]))/2

def _bbox(cs):
    xs = [q[0] for g in cs for s in g for q in s[1:]]; ys = [q[1] for g in cs for s in g for q in s[1:]]
    return min(xs), min(ys), max(xs), max(ys)

def compat(dR, dB):
    """dR, dB: chuỗi SVG path (y lên). Trả về [(segsR, segsB)] — mỗi cặp cùng độ dài, đoạn ['L', a, b] / ['C', a, c1, c2, b]."""
    cr, cb = contours([dR]), contours([dB])
    if not cr and not cb: return []
    assert len(cr) == len(cb), (len(cr), len(cb))
    br, bb = _bbox(cr), _bbox(cb)
    sx = lambda b: (b[2] - b[0]) or 1; sy = lambda b: (b[3] - b[1]) or 1
    nr = lambda p: ((p[0] - br[0])/sx(br), (p[1] - br[1])/sy(br))
    nb = lambda p: ((p[0] - bb[0])/sx(bb), (p[1] - bb[1])/sy(bb))
    def sig(g, n):
        P = [n(q) for s in g for q in s[1:]]; xs = [p[0] for p in P]; ys = [p[1] for p in P]
        return ((min(xs) + max(xs))/2, (min(ys) + max(ys))/2, max(xs) - min(xs), max(ys) - min(ys))
    used = set(); out = []
    for g in cr:
        c = sig(g, nr)
        k = min((k for k in range(len(cb)) if k not in used), key=lambda k: math.dist(c, sig(cb[k], nb)))
        used.add(k); h = cb[k]
        if (_sarea(g) > 0) != (_sarea(h) > 0): h = reverse(h)
        R, B = align(g, h, nr, nb)
        Ro, Bo = [], []
        for s, u in zip(R, B):
            if s[0] == 'L' and u[0] == 'L': Ro.append(s); Bo.append(u)
            else: Ro.append(tocubic(s)); Bo.append(tocubic(u))
        out.append((Ro, Bo))
    return out

def lerp_segs(a, b, t):
    return [[s[0]] + [(p[0] + (q[0] - p[0])*t, p[1] + (q[1] - p[1])*t) for p, q in zip(s[1:], u[1:])] for s, u in zip(a, b)]

def to_d(segs_list):
    out = []
    for segs in segs_list:
        c = ['M%.2f %.2f' % segs[0][1]]
        for s in segs: c.append('L%.2f %.2f' % s[2] if s[0] == 'L' else 'C%.2f %.2f %.2f %.2f %.2f %.2f' % (*s[2], *s[3], *s[4]))
        out.append(''.join(c) + 'Z')
    return ' '.join(out)
