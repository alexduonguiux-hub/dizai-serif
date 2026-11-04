#!/usr/bin/env python3
"""Số Bold suy ra từ số Regular của designer, theo đúng cách designer làm chữ Bold (đo từ O, H, E, A):
mép ngoài, loe, mỏ giữ nguyên; nét dày lên vào phía lòng: thân +37, ngang +28 (≈ V 102→139, Hb 40→68).
Cách làm: Bold = H ∩ (R ⊕ chữ nhật ±37 × ±28)
  R = số Regular; H = vùng được phép có mực = R đã lấp lòng + lòng hở được khép bằng dây cung
      + các dải cho phép nét dày ra ở phía không có lòng (thân 1, 4; chéo 3, 5, 7; thanh 2, 4, 7).
    python3 tools/construct/ref/make_bold_fig.py   → thêm '0-Bold'… '9-Bold' vào designer_B.json (khoá *-Bold)
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pathops
from make_ref import outline
DX, DY = 37, 28
OP = pathops.PathOp

def P(pts):
    p = pathops.Path(); p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close(); return p
def ell(c, rx, ry, n=96):
    return P([(c[0] + rx * math.cos(2 * math.pi * i / n), c[1] + ry * math.sin(2 * math.pi * i / n)) for i in range(n)])
def tr(p, dx, dy):
    q = pathops.Path()
    for v, ps in p.segments:
        P_ = [(x + dx, y + dy) for x, y in ps]
        if v == "moveTo": q.moveTo(*P_[0])
        elif v == "lineTo": q.lineTo(*P_[0])
        elif v == "curveTo": q.cubicTo(*P_[0], *P_[1], *P_[2])
        elif v == "closePath": q.close()
    return q
def U(*ps):
    a = ps[0]
    for b in ps[1:]: a = pathops.op(a, b, OP.UNION)
    return a
def I(a, b): return pathops.op(a, b, OP.INTERSECTION)
def Dif(a, b): return pathops.op(a, b, OP.DIFFERENCE)
def sweep(p, xs, ys, n=12):
    acc = p
    for i in range(n + 1): acc = U(acc, tr(p, xs[0] + (xs[1] - xs[0]) * i / n, 0))
    h = acc
    for j in range(n + 1): acc = U(acc, tr(h, 0, ys[0] + (ys[1] - ys[0]) * j / n))
    return acc
def filled(p):
    """chỉ giữ các contour ngoài (lấp lòng kín)"""
    out = None; cur = []; contours = []
    for v, ps in p.segments:
        cur.append((v, ps))
        if v == "closePath": contours.append(cur); cur = []
    for c in contours:
        q = pathops.Path()
        for v, ps in c:
            if v == "moveTo": q.moveTo(*ps[0])
            elif v == "lineTo": q.lineTo(*ps[0])
            elif v == "curveTo": q.cubicTo(*ps[0], *ps[1], *ps[2])
            else: q.close()
        area = 0; pts = [pt for v, ps in c for pt in ps]
        for i in range(len(pts)): area += pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
        out = (q, area) if out is None or abs(area) > abs(out[1]) else out
    return out[0]

def contours(p):
    out, cur, c0 = [], [], None
    for v, ps in p.segments:
        if v == "moveTo": cur = [ps[0]]; c0 = ps[0]
        elif v == "lineTo": cur.append(ps[0])
        elif v == "curveTo":
            a = cur[-1]
            for i in range(1, 9):
                t = i / 8; u = 1 - t
                cur.append(tuple(u**3*a[k] + 3*u*u*t*ps[0][k] + 3*u*t*t*ps[1][k] + t**3*ps[2][k] for k in (0, 1)))
        elif v == "closePath": out.append(cur)
    return out
def inside(pt, poly):
    x, y = pt; c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def hull(p):
    pts = sorted(set((round(x, 2), round(y, 2)) for c in contours(p) for x, y in c))
    cr = lambda o, a, b: (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for q in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0: lo.pop()
        lo.append(q)
    for q in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0: up.pop()
        up.append(q)
    return P(lo[:-1] + up[:-1])
def white(R, seeds, extra_cut=None, extra_keep=None):
    """các vùng trắng (trong bao lồi) chứa điểm hạt: lòng kín hoặc lòng hở"""
    Wt = Dif(hull(R), R)
    if extra_cut is not None: Wt = Dif(Wt, extra_cut)
    acc = None; flat = contours(Wt); i = 0; cur = None
    for v, ps in Wt.segments:   # giữ đường cong chính xác của từng contour, chỉ dùng bản gấp khúc để thử điểm hạt
        if v == "moveTo": cur = pathops.Path(); cur.moveTo(*ps[0])
        elif v == "lineTo": cur.lineTo(*ps[0])
        elif v == "curveTo": cur.cubicTo(*ps[0], *ps[1], *ps[2])
        elif v == "closePath":
            cur.close()
            if any(inside(s, flat[i]) for s in seeds): acc = cur if acc is None else U(acc, cur)
            i += 1
    if acc is not None and extra_keep is not None: acc = I(acc, extra_keep)
    return acc
def esweep(p, rx, ry, n=64):
    acc = p
    for i in range(n):
        t = 2 * math.pi * i / n
        for f in (1.0, 0.6):
            acc = U(acc, tr(p, f * rx * math.cos(t), f * ry * math.sin(t)))
    return acc

EXT = {
    "3": [[(0, 241.3), (-16, 302), (-80, 302), (-80, 40), (0, 66.4)]],
    "5": [[(0, 241.3), (-16, 302), (-80, 302), (-80, 40), (0, 66.4)]],
    "2": [[(28.8, 508.4), (-20, 440.4), (-80, 440), (-80, 656.2), (28.5, 656.2)]],
    "6": [[(410.9, 530.1), (441, 480.7), (560, 520), (560, 720), (469.8, 630.8)]],
}
EXT["9"] = [[(527.1 - x, 703.7 - y) for x, y in EXT["6"][0]]]

def bold(ch, R):
    F = filled(R)
    Rx = U(R, *[P(q) for q in EXT.get(ch, [])]) if ch in EXT else R
    K = ((-DX, DX), (-DY, DY))
    if ch in "08":
        H = F; B = I(H, esweep(R, DX, DY))
    elif ch in "69":
        seeds = [(300, 560), (200, 600)] if ch == "6" else [(227, 140), (327, 100)]
        t0, t1 = ((469.8, 630.8), (410.9, 530.1)) if ch == "6" else ((57.4, 72.8), (116.3, 173.5))
        d = (t1[0] - t0[0], t1[1] - t0[1]); L = math.hypot(*d); d = (d[0] / L, d[1] / L)
        nn = (d[1], -d[0])  # phía lòng hở (trái đường cắt đầu nét)
        keep = P([(t0[0] - d[0] * 2000, t0[1] - d[1] * 2000), (t0[0] + d[0] * 2000, t0[1] + d[1] * 2000),
                  (t0[0] + d[0] * 2000 + nn[0] * 3000, t0[1] + d[1] * 2000 + nn[1] * 3000), (t0[0] - d[0] * 2000 + nn[0] * 3000, t0[1] - d[1] * 2000 + nn[1] * 3000)])
        Wap = white(R, seeds, extra_keep=keep)
        # mép trên của bụng là mép ngoài của bụng → giữ nguyên (như O Bold); chỉ đuôi dày vào lòng hở
        bowl = ell((280.5, 233.9), 246.6, 245.1) if ch == "6" else ell((246.6, 469.8), 246.6, 245.2)
        B = U(I(F, esweep(Rx, DX, DY)), I(Wap, esweep(Dif(Rx, bowl), DX, DY)))
    elif ch == "1":
        H = U(F, I(tr(R, DX, 0), P([(150, -5), (400, -5), (400, 720), (150, 720)])), P([(178.5, 0), (178.5 + DX, 0), (178.5 + DX, 711.3), (178.5, 711.3)]))
        B = I(H, sweep(R, (0, DX), (0, 0)))
    elif ch == "4":
        stem_below = P([(328.7 - DX, 0), (330, 0), (330, 167.2), (328.7 - DX, 167.2)])
        H = U(F, I(tr(R, -DX, 0), P([(260, -5), (330, -5), (330, 167.2), (260, 167.2)])), stem_below,
              P([(0, 167.2 - DY), (530, 167.2 - DY), (530, 167.2), (0, 167.2)]))
        B = I(H, sweep(R, (-DX, 0), (-DY, 0)))
    elif ch in "35":
        ycut = 439.2 if ch == "3" else 413.8   # chỉ phần lòng hở dưới chỗ chéo/thân nối bụng; không lấn dưới thanh trên
        Wo = white(R, [(60, 330)] if ch == "3" else [(30, 330)], extra_keep=P([(-10, -100), (600, -100), (600, ycut), (-10, ycut)]))
        if ch == "3":
            n = (0.7238, -0.69); w = 30; a, b = (405.3, 686.6), (206.8, 478.4)
        else:
            a, b = (83.2, 609.3), (57.5, 444.9); L = math.dist(a, b); n = ((a[1] - b[1]) / L, -(a[0] - b[0]) / L); w = 30
        band = P([a, b, (b[0] + n[0] * w, b[1] + n[1] * w), (a[0] + n[0] * w, a[1] + n[1] * w)])
        x1 = 405.3 if ch == "3" else 394.9
        barband = I(P([(0, 609.3 - DY), (x1, 609.3 - DY), (x1, 609.3), (0, 609.3)]), U(hull(R), F))
        if ch == "3": barband = Dif(barband, Dif(hull(R), F))  # không lấn vào khoảng trắng dưới thanh bên phải chéo
        band = I(band, P([(0, 0), (x1, 0), (x1, 700), (0, 700)]))
        parts = [F, band, barband] + ([Wo] if Wo is not None else [])
        H = U(*parts); B = I(H, esweep(Rx, DX, DY))
    elif ch == "2":
        # lòng dưới cung: chỉ phần trên (y ≥ 330), không vượt mặt cắt đầu nét trái; vùng phải-dưới (giữa sống và thanh đáy): sống và thanh dày vào đó
        # lòng dưới cung (cả phần trái sống): cung và sống dày vào đó; không vượt mặt cắt đầu nét trái (x = 28.5)
        Wo = white(R, [(150, 500), (300, 520)], extra_keep=P([(28.5, -100), (600, -100), (600, 800), (28.5, 800)]))
        barband = I(Dif(P([(92.5, 90.7), (447.8, 90.7), (447.8, 90.7 + DY), (92.5, 90.7 + DY)]), R), hull(R))
        H = U(F, barband, *[w for w in (Wo,) if w is not None])
        B = I(H, esweep(Rx, DX, DY))
    elif ch == "7":
        barband = P([(0, 668.8 - DY), (330, 668.8 - DY), (330, 668.8), (0, 668.8)])
        a, b = (322.1, 668.8), (79.4, 0); L = math.dist(a, b); n = (-(a[1] - b[1]) / L, (a[0] - b[0]) / L); w = 40
        band = P([a, b, (b[0] + n[0] * w, b[1] + n[1] * w), (a[0] + n[0] * w, a[1] + n[1] * w)])
        H = U(F, barband, I(band, P([(0, 0), (445, 0), (445, 668.8), (0, 668.8)])))
        B = I(H, sweep(R, (-DX, 0), (-DY, 0)))
    if ch in "1235 7": B = filled(B)   # các số không có lòng kín: lấp mọi khe trắng nhỏ phát sinh
    xs = [q[0] for v, ps in B.segments for q in ps]; x0 = min(xs)
    return tr(B, -x0, 0)

if __name__ == "__main__":
    A = json.load(open(os.path.join(HERE, "designer_B.json")))
    for ch in "0123456789":
        R = outline(A[f"{ch}-Regular"]); B = bold(ch, R)
        d = []
        for v, ps in B.segments:
            k = {"moveTo": "M", "lineTo": "L", "curveTo": "C", "closePath": "Z"}[v]
            d.append(k + " ".join("%.1f %.1f" % q for q in ps))
        A[f"{ch}-Bold"] = ["".join(d)]
        print(ch, len(d))
    json.dump(A, open(os.path.join(HERE, "designer_B.json"), "w"), separators=(",", ":"))
