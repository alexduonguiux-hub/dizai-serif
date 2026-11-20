#!/usr/bin/env python3
"""S46 — cân nét chữ thường + số (designer: "các nét mỏng và dày nhất luôn bằng nhau"; chữ hoa giữ nguyên).
Chuẩn mỗi weight (đo trục giữa như qa_stroke, bỏ khớp + đầu nét):
  nét mảnh   h* = 42 / 48.7 / 55.3 / 62      (Regular / Medium / SemiBold / Bold — trung vị bụng b d o p q)
  nét tròn   T* = thân + 2 %  = 104 / 111 / 119 / 128   (o e a s c g)
  số         T* = 106 / 117.3 / 128.7 / 140,  nét mảnh = h*
Cách làm (luật, không vá tay): chỉ dời điểm neo TRƠN nằm giữa hai đoạn cong (nét thẳng, chân loe, góc giữ nguyên);
mỗi điểm dời theo pháp tuyến ra ngoài một nửa độ đổi bề dày Δ(w), w = bề dày tại điểm đó (tia vào trong mực),
Δ(w) = a (phía mảnh) → b (phía dày), nội suy tuyến tính theo w; tay nắm đi cùng điểm neo → giữ liền tiếp tuyến.
a, b giải lặp cho tới khi nét mảnh / nét dày đo được = chuẩn (±0.5 u).
"""
import math, os, sys, re
import numpy as np
from scipy import ndimage
from skimage.morphology import medial_axis
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'ref'))
from make_ref import parse, outline
import qa_stroke as Q
from weights import TW

HAIR = (42.0, 62.0); STEM = (102.0, 125.0)
def hair(w): return HAIR[0] + (HAIR[1] - HAIR[0])*TW[w]
def round_T(w): return (STEM[0] + (STEM[1] - STEM[0])*TW[w])*1.02
def fig_T(w): return 106.0 + (140.0 - 106.0)*TW[w]

# glyph → (nét mảnh, nét dày): 'h' = chuẩn nét mảnh, 'R' = chuẩn nét tròn, 'F' = chuẩn số, None = giữ của chính glyph
#   n h m u: chỗ mảnh nhất là vai (khớp vòm–thân) — giữ; a: bụng S46c riêng (dời lòng làm bậc ở góc lòng–thân); 2: không có nét mảnh (sống chéo); e: theo bản vẽ S47 (thanh + vòng — cân lên làm e nặng hơn o); 4 7: nét thẳng — giữ
SPEC = {'o': ('h', 'R'), 'c': ('h', 'R'), 's': ('h', 'R'), 'g': ('h', 'R'),
        'b': ('h', None), 'd': ('h', None), 'p': ('h', None), 'q': ('h', None),
        '0': ('h', 'F'), '3': ('h', 'F'), '5': (None, 'F'), '6': ('h', 'F'), '8': ('h', 'F'), '9': ('h', 'F')}
def targets(c, w):
    h, T = SPEC[c]
    return (hair(w) if h == 'h' else None), ({'R': round_T(w), 'F': fig_T(w)}[T] if T else None)

def mask_paths(paths):
    o = outline(paths); P = Q.polys(o)
    xs = [q[0] for c in P for q in c]; ys = [q[1] for c in P for q in c]
    x0, y0 = min(xs) - 6, min(ys) - 6; W = int((max(xs) - x0 + 6)*Q.SC) + 2; H = int((max(ys) - y0 + 6)*Q.SC) + 2
    from skimage.draw import polygon as skpoly
    m = np.zeros((H, W), bool)
    for c in P:
        rr, cc = skpoly([(y - y0)*Q.SC for _, y in c], [(x - x0)*Q.SC for x, _ in c], (H, W)); t = np.zeros((H, W), bool); t[rr, cc] = True; m ^= t
    return m, (x0, y0), P

JR = 2.2
def measure(paths, full=False):
    """t (phân vị 2) / T (phân vị 97) bề dày trục giữa, bỏ khớp (1.6 × nửa nét) và đầu nét (3 × nửa nét)"""
    m, org, _ = mask_paths(paths)
    sk, dist = medial_axis(m, return_distance=True); K3 = np.ones((3, 3), int)
    for _ in range(min(30, int(1.2*dist.max()))):
        dg = ndimage.convolve(sk.astype(int), K3, mode='constant') - 1; ends = sk & (dg <= 1)
        if not ends.any(): break
        sk = sk & ~ends
    deg = ndimage.convolve(sk.astype(int), K3, mode='constant') - 1
    Y, X = np.mgrid[0:m.shape[0], 0:m.shape[1]]; ex = np.zeros_like(sk)
    for y, x in zip(*np.nonzero(sk)):
        if deg[y, x] >= 3: r = JR*dist[y, x] + 2
        elif deg[y, x] <= 1: r = 3.0*dist[y, x] + 2
        else: continue
        ex |= (Y - y)**2 + (X - x)**2 <= r*r
    k = sk & ~ex
    w = 2*dist[k]/Q.SC
    return float(np.percentile(w, 2)), float(np.percentile(w, 97))

# ---------- cấu trúc đường: [[('M',p)], ...] → contour = list đoạn ----------
def contours(d):
    out = []; cur = None
    for c, pts in parse(d):
        if c == 'M': cur = []; s = pts[0]; last = s
        elif c == 'L': cur.append(['L', list(last), list(pts[0])]); last = pts[0]
        elif c == 'C': cur.append(['C', list(last), list(pts[0]), list(pts[1]), list(pts[2])]); last = pts[2]
        elif c == 'Z': out.append(cur)
    return out

def to_d(cs):
    f = lambda p: f"{p[0]:.1f} {p[1]:.1f}"
    s = ''
    for g in cs:
        s += 'M' + f(g[0][1])
        for seg in g: s += ('L' + f(seg[2])) if seg[0] == 'L' else ('C' + f(seg[2]) + ' ' + f(seg[3]) + ' ' + f(seg[4]))
        s += 'Z'
    return s

def nodes(cs):
    """điểm neo trơn giữa hai cubic: (contour, chỉ số đoạn đến, tiếp tuyến đơn vị)"""
    out = []
    for gi, g in enumerate(cs):
        n = len(g)
        for i in range(n):
            a, b = g[i], g[(i + 1) % n]
            if a[0] != 'C' or b[0] != 'C': continue
            P = a[4]; u = (P[0] - a[3][0], P[1] - a[3][1]); v = (b[2][0] - P[0], b[2][1] - P[1])
            lu, lv = math.hypot(*u), math.hypot(*v)
            if lu < 0.5 or lv < 0.5: continue
            if math.degrees(math.acos(max(-1, min(1, (u[0]*v[0] + u[1]*v[1])/(lu*lv))))) > 12: continue
            t = ((u[0]/lu + v[0]/lv)/2, (u[1]/lu + v[1]/lv)/2); lt = math.hypot(*t)
            out.append((gi, i, (t[0]/lt, t[1]/lt)))
    return out

def inside(P, polys):
    x, y = P; c = False
    for pl in polys:
        for i in range(len(pl)):
            (x1, y1), (x2, y2) = pl[i - 1], pl[i]
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1)*(x2 - x1)/(y2 - y1): c = not c
    return c

def ray(P, d, polys):
    best = None
    for pl in polys:
        for i in range(len(pl)):
            (x1, y1), (x2, y2) = pl[i - 1], pl[i]; ex, ey = x2 - x1, y2 - y1
            den = d[0]*ey - d[1]*ex
            if abs(den) < 1e-9: continue
            t = ((x1 - P[0])*ey - (y1 - P[1])*ex)/den; s = ((x1 - P[0])*d[1] - (y1 - P[1])*d[0])/den
            if t > 1.0 and 0 <= s <= 1 and (best is None or t < best): best = t
    return best

def probe(paths):
    """mỗi điểm neo trơn: (path, gi, i, pháp tuyến ra ngoài, bề dày w) — chỉ điểm nằm trên biên mực hợp nhất"""
    _, _, polys = mask_paths(paths); out = []
    for pi, d in enumerate(paths):
        cs = contours(d)
        for gi, i, t in nodes(cs):
            P = cs[gi][i][4]; n = (t[1], -t[0])
            a_in, b_in = inside((P[0] + 2.5*n[0], P[1] + 2.5*n[1]), polys), inside((P[0] - 2.5*n[0], P[1] - 2.5*n[1]), polys)
            if a_in == b_in: continue                     # điểm bị che trong phần khác (không nằm trên biên)
            if a_in: n = (-n[0], -n[1])                   # n = pháp tuyến ra ngoài mực
            w = ray(P, (-n[0], -n[1]), polys)
            if w is None or w > 400: continue
            A, B = cs[gi][i], cs[gi][(i + 1) % len(cs[gi])]
            bz = lambda g, t: tuple((1-t)**3*g[1][j] + 3*(1-t)**2*t*g[2][j] + 3*(1-t)*t*t*g[3][j] + t**3*g[4][j] for j in (0, 1))
            q1, q2 = bz(A, 0.5), bz(B, 0.5)
            mx, my = (q1[0] + q2[0])/2 - P[0], (q1[1] + q2[1])/2 - P[1]
            cv = (mx*n[0] + my*n[1])/max(1e-6, math.dist(q1, q2))      # < 0: mép lồi (cong về phía mực), > 0: mép lõm
            side = min(1.0, max(0.0, 0.5 + 8*cv))      # mép lõm (lòng chữ) = 1: nhận cả Δ; mép lồi (bóng ngoài) = 0: giữ nguyên
            out.append((pi, gi, i, n, w, side))
    return out

def apply(paths, pr, a, b, wl, wh):
    cs = [contours(d) for d in paths]
    for pi, gi, i, n, w, side in pr:
        k = 0 if wh <= wl else min(1, max(0, (w - wl)/(wh - wl)))
        s = (a + (b - a)*k)*side
        g = cs[pi][gi]; A, B = g[i], g[(i + 1) % len(g)]
        for p in (A[3], A[4], B[1], B[2]): p[0] += n[0]*s; p[1] += n[1]*s
    return [to_d(c) for c in cs]

def balance(paths, h_t=None, T_t=None, it=10, log=None):
    """h_t / T_t = None: giữ nguyên nét mảnh / nét dày của chính glyph"""
    pr = probe(paths)
    t0, T0 = measure(paths)
    if not pr: return paths, dict(t0=round(t0, 1), T0=round(T0, 1), t=round(t0, 1), T=round(T0, 1), a=0, b=0)
    ws = sorted(p[4] for p in pr if p[4] < 1.6*T0); wl, wh = ws[0], ws[-1]
    h_t = t0 if h_t is None else h_t; T_t = T0 if T_t is None else T_t
    def f(a, b):
        o = apply(paths, pr, a, b, wl, wh); t, T = measure(o); return o, t, T
    tgt = lambda t, T: (h_t - t, T_t - T)
    a = b = 0.0; out, t, T = paths, t0, T0
    _, ta, Ta = f(4.0, 0.0)                                    # Jacobian ∂(t,T)/∂(a,b) bằng sai phân
    J = np.array([[(ta - t0)/4, 0.0], [(Ta - T0)/4, 1.0]])
    _, tb, Tb = f(0.0, 4.0); J[0, 1] = (tb - t0)/4; J[1, 1] = (Tb - T0)/4
    CAP = 0.45*h_t
    if J[0, 0] < 0.3: J[0, 0] = 1e9                              # nét mảnh nằm ngoài các điểm neo trơn (khớp): không chỉnh
    if J[1, 1] < 0.3: J[1, 1] = 1e9
    best = (abs(t0 - h_t) + abs(T0 - T_t), paths, t0, T0, 0.0, 0.0)
    for _ in range(it):
        e = np.array(tgt(t, T))
        if abs(e[0]) < 0.5 and abs(e[1]) < 0.5: break
        dx = np.linalg.lstsq(J, e, rcond=None)[0]
        a1 = max(-CAP, min(CAP, a + float(dx[0]))); b1 = max(-CAP, min(CAP, b + float(dx[1])))
        o1, t1, T1 = f(a1, b1)
        s_ = np.array([a1 - a, b1 - b]); y_ = np.array([t1 - t, T1 - T])
        if s_ @ s_ > 1e-6: J = J + np.outer(y_ - J @ s_, s_)/(s_ @ s_)        # cập nhật Broyden
        a, b, out, t, T = a1, b1, o1, t1, T1
        sc = abs(t - h_t) + abs(T - T_t)
        if sc < best[0]: best = (sc, out, t, T, a, b)
    _, out, t, T, a, b = best
    # chấp nhận chỉ khi không chiều nào xấu đi quá 1 u
    if abs(t - h_t) > abs(t0 - h_t) + 1.0 or abs(T - T_t) > abs(T0 - T_t) + 1.0: out, t, T, a, b = paths, t0, T0, 0.0, 0.0
    return out, dict(t0=round(t0, 1), T0=round(T0, 1), t=round(t, 1), T=round(T, 1), a=round(a, 1), b=round(b, 1))

def run_file(path, chars, weights=('Regular', 'Medium', 'SemiBold', 'Bold'), src=None, log=True):
    import json
    D = json.load(open(src or path)); rep = {}
    for c in chars:
        for w in weights:
            k = f'{c}-{w}'
            if k not in D: continue
            D[k], r = balance(D[k], *targets(c, w)); rep[k] = r
            if log: print(k, r, flush=True)
    json.dump(D, open(path, 'w'), separators=(',', ':')) if src else json.dump(D, open(path, 'w'))
    return rep

if __name__ == '__main__':
    # lower   : sau lower.py  → lower/lower.json (a b c d e g o p q)        [pipeline]
    # derived : sau derive.py → lower/lower_derived.json (s)                [pipeline]
    # fig     : một lần, từ ảnh chụp ref/designer_B_preS46.json → ref/designer_B.json (số Regular + Bold; interp.py sinh M / SB)
    import shutil
    mode = sys.argv[1] if len(sys.argv) > 1 else 'lower'
    LC = [c for c in SPEC if c.isalpha()]
    if mode == 'lower': run_file(os.path.join(HERE, 'lower', 'lower.json'), LC)
    elif mode == 'derived': run_file(os.path.join(HERE, 'lower', 'lower_derived.json'), LC)
    elif mode == 'fig':
        dst = os.path.join(HERE, 'ref', 'designer_B.json'); snap = os.path.join(HERE, 'ref', 'designer_B_preS46.json')
        if not os.path.exists(snap): shutil.copy(dst, snap)
        run_file(dst, [c for c in SPEC if c.isdigit()], ('Regular', 'Bold'), src=snap)
