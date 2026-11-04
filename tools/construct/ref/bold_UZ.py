#!/usr/bin/env python3
"""U V W X Y Z Bold theo nguyên tắc rút ra từ Bold A–T của designer (xem docs/08-nguyen-tac-bold.md):
  thân 102→139 dày vào phía lòng (mép ngoài giữ), thanh/tay 40→68, vòng: lòng co ~38, nét chéo dày 100→146 / mảnh 44→74
  với chân ngoài cố định và đỉnh dịch theo nửa phần tăng bề rộng, mặt cắt đỉnh 20; loe/mỏ giữ nguyên hình, trượt theo mép.
    python3 tools/construct/ref/bold_UZ.py   → designer_B.json: U-Bold … Z-Bold
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pathops
from make_ref import parse
OP = pathops.PathOp
K = 0.5523
XT, Xt, ZD = 132, 72, 134   # X: dày, mảnh; Z: chéo — chỉnh cho tỉ lệ mật độ Bold/Regular ≈ 1.34 như A, M, N của designer

def poly(pts):
    p = pathops.Path(); p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close(); return p
def U(*ps):
    a = ps[0]
    for b in ps[1:]: a = pathops.op(a, b, OP.UNION)
    return a
def I(a, b): return pathops.op(a, b, OP.INTERSECTION)
def xat(p, q, y): return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])
def inter(p1, p2, p3, p4):
    d1 = (p2[0] - p1[0], p2[1] - p1[1]); d2 = (p4[0] - p3[0], p4[1] - p3[1]); den = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den
    return (p1[0] + d1[0] * t, p1[1] + d1[1] * t)
def offset_line(p, q, w, side):
    """đường song song với pq, cách w, về phía side (+1 = bên trái hướng p→q)"""
    L = math.dist(p, q); n = (-(q[1] - p[1]) / L * side, (q[0] - p[0]) / L * side)
    return (p[0] + n[0] * w, p[1] + n[1] * w), (q[0] + n[0] * w, q[1] + n[1] * w)
def band(p, q, w, side, y0=-60, y1=760):
    a, b = offset_line(p, q, w, side)
    return poly([(xat(p, q, y0), y0), (xat(p, q, y1), y1), (xat(a, b, y1), y1), (xat(a, b, y0), y0)])
def band2(P1, P2, w, sgn):
    """hai đường song song qua P1 và P2, cách nhau w (như luật dựng): trả hướng"""
    v = (P2[0] - P1[0], P2[1] - P1[1]); L = math.hypot(*v); ang = math.atan2(v[1], v[0]) + sgn * math.asin(min(1, w / L))
    return (math.cos(ang), math.sin(ang))
def wedge(cmds, dx, dy, close_pts):
    """vùng loe: đường cong của designer (dời dx, dy) + các điểm khép"""
    p = pathops.Path(); first = True; cur = None
    for c, pts in cmds:
        P = [(x + dx, y + dy) for x, y in pts]
        if first: p.moveTo(*P[0]); first = False; cur = P[0]
        if c == 'C': p.cubicTo(*P[0], *P[1], *P[2])
        elif c == 'L' and not first: p.lineTo(*P[0])
    for q in close_pts: p.lineTo(*q)
    p.close(); return p
def C(*pts): return ('C', list(pts))
def to_d(p):
    out = []
    for v, ps in p.segments:
        k = {'moveTo': 'M', 'lineTo': 'L', 'curveTo': 'C', 'closePath': 'Z'}[v]
        out.append(k + ' '.join('%.1f %.1f' % q for q in ps))
    return ''.join(out)
def arc(c, r_x, r_y, a0, a1):
    """cung elip (nhiều đoạn 90°) từ góc a0 tới a1 (độ)"""
    segs = []; n = max(1, round(abs(a1 - a0) / 90)); da = (a1 - a0) / n
    for i in range(n):
        s, e = math.radians(a0 + i * da), math.radians(a0 + (i + 1) * da); k = 4 / 3 * math.tan((e - s) / 4)
        p0 = (c[0] + r_x * math.cos(s), c[1] + r_y * math.sin(s)); p3 = (c[0] + r_x * math.cos(e), c[1] + r_y * math.sin(e))
        segs.append(((p0[0] - k * r_x * math.sin(s), p0[1] + k * r_y * math.cos(s)), (p3[0] + k * r_x * math.sin(e), p3[1] - k * r_y * math.cos(e)), p3))
    return segs

def make_V(B):
    # V Regular = A Regular xoay 180°  →  V Bold = A Bold của designer xoay 180°, bỏ thanh, hai mép trong gặp ở chạc
    d = B['A-Bold'][0].split('Z')[0] + 'Z'
    d = d.replace('L448 158.7L173.6 158.7', 'L448 158.7L316.7 464.7L173.6 158.7')
    W = 694.6; p = pathops.Path()
    for c, pts in parse(d):
        P = [(W - x, 700 - y) for x, y in pts]
        if c == 'M': p.moveTo(*P[0])
        elif c == 'L': p.lineTo(*P[0])
        elif c == 'C': p.cubicTo(*P[0], *P[1], *P[2])
        else: p.close()
    return p

def make_U(B):
    # thân y hệt H Bold (22.7–161.5 và 379.8–518.6, loe đỉnh của H Bold); bụng: mép ngoài là nửa vòng nối hai mép ngoài thân,
    # lòng co: đáy dày 39.7 + 38 (luật vòng); lòng là nửa vòng nối hai mép trong thân
    xl0, xl1, xr0, xr1, W = 22.7, 161.5, 379.8, 518.6, 541.3
    Ro = (xr1 - xl0) / 2; cxo = (xl0 + xr1) / 2; cyo = -14.2 + Ro
    Ri = (xr0 - xl1) / 2; cxi = (xl1 + xr0) / 2; bot_in = -14.2 + 39.7 + 38; cyi = bot_in + Ri
    p = pathops.Path()
    p.moveTo(0, 700); p.lineTo(7.7, 686.5); p.cubicTo(17.5, 669.3, 22.7, 649.9, xl0, 630.2); p.lineTo(xl0, cyo)
    for c1, c2, e in arc((cxo, cyo), Ro, Ro, 180, 360): p.cubicTo(*c1, *c2, *e)
    p.lineTo(xr1, 630.2); p.cubicTo(xr1, 649.9, 523.8, 669.3, 533.6, 686.5); p.lineTo(W, 700); p.lineTo(357.1, 700); p.lineTo(364.8, 686.5)
    p.cubicTo(374.6, 669.3, xr0, 649.9, xr0, 630.2); p.lineTo(xr0, cyi)
    for c1, c2, e in arc((cxi, cyi), Ri, Ri, 0, -180): p.cubicTo(*c1, *c2, *e)
    p.lineTo(xl1, 630.2); p.cubicTo(xl1, 649.9, 166.7, 669.3, 176.5, 686.5); p.lineTo(184.2, 700); p.close()
    return p

def make_Z():
    # thanh 68 (trên dày xuống, dưới dày lên), mỏ trượt theo thanh (như E: x theo bề rộng +48, y ±28);
    # chéo dày 146 đi qua góc trên-phải (W, 683) và dưới-trái (0, 17) như Regular
    W = 464.8 + 48; dw = 48
    top = poly([(11.3, 632), (W, 632), (W, 700), (11.3, 700)]); bot = poly([(0, 0), (W - 11.3, 0), (W - 11.3, 68), (0, 68)])
    bk1 = pathops.Path(); bk1.moveTo(104.9, 632); bk1.cubicTo(75.6, 632, 47.4, 620.7, 26.4, 600.8); bk1.cubicTo(19.8, 594.5, 15.1, 586.5, 11.3, 578.2); bk1.lineTo(11.3, 634); bk1.lineTo(106, 634); bk1.close()
    bk2 = pathops.Path(); bk2.moveTo(359.9 + dw, 68); bk2.cubicTo(389.2 + dw, 68, 417.4 + dw, 79.3, 438.4 + dw, 99.2); bk2.cubicTo(445 + dw, 105.5, 449.7 + dw, 113.5, 453.4 + dw, 121.8); bk2.lineTo(453.4 + dw, 66); bk2.lineTo(358 + dw, 66); bk2.close()
    A1, B1 = (W, 683), (0, 17); d = band2(A1, B1, ZD, 1)
    if d[1] > 0: d = band2(A1, B1, ZD, -1)
    q1 = (A1[0] + d[0] * 1000, A1[1] + d[1] * 1000); q2 = (B1[0] - d[0] * 1000, B1[1] - d[1] * 1000)
    diag = I(poly([(xat(A1, q1, 760), 760), (xat(A1, q1, -60), -60), (xat(B1, q2, -60), -60), (xat(B1, q2, 760), 760)]), poly([(0, 0), (W, 0), (W, 700), (0, 700)]))
    return U(top, bot, bk1, bk2, diag)

def make_X():
    # Regular: nét dày \ (mép E1 qua góc (0,700), mép E2 qua góc (642.2,0)), nét mảnh / (T2 qua (3.3,0), T1 qua (638.9,700))
    # Bold: rộng +23, góc ngoài giữ (bên phải dời +23), dày 95→141, mảnh 47→77; loe trong lấy nguyên hình designer, trượt theo mép
    dw = 23; W = 642.2 + dw
    E1p, E2p = (0, 700), (642.2 + dw, 0)
    dE = min((band2(E1p, E2p, XT, sg) for sg in (1, -1)), key=lambda d: abs(d[0] / d[1]))   # nghiệm dốc hơn (như Regular)
    E1q = (E1p[0] + dE[0] * 2000, E1p[1] + dE[1] * 2000); E2q = (E2p[0] - dE[0] * 2000, E2p[1] - dE[1] * 2000)
    T2p, T1p = (3.3, 0), (638.9 + dw, 700)
    dT = min((band2(T2p, T1p, Xt, sg) for sg in (1, -1)), key=lambda d: abs(d[0] / d[1]))
    T2q = (T2p[0] + dT[0] * 2000, T2p[1] + dT[1] * 2000); T1q = (T1p[0] - dT[0] * 2000, T1p[1] - dT[1] * 2000)
    thick = poly([(xat(E1p, E1q, 760), 760), (xat(E1p, E1q, -60), -60), (xat(E2p, E2q, -60), -60), (xat(E2p, E2q, 760), 760)])
    thin = poly([(xat(T2p, T2q, 760), 760), (xat(T2p, T2q, -60), -60), (xat(T1p, T1q, -60), -60), (xat(T1p, T1q, 760), 760)])
    box = poly([(0, 0), (W, 0), (W, 700), (0, 700)])
    # loe (designer Regular X), mỗi loe trượt sao cho điểm gắn nằm trên mép mới
    def fl(curve, attach, P, Q, tip_y):
        y = attach[1]; dx = xat(P, Q, y) - attach[0]
        return wedge(curve, dx, 0, [(xat(P, Q, tip_y), tip_y)])
    f1 = fl([('M', [(162.8, 700)]), ('C', [(153, 685.8), (150.1, 668.8), (153.5, 653.1)])], (153.5, 653.1), E2p, E2q, 700)
    f2 = fl([('M', [(479.3, 0)]), ('C', [(489.2, 14.2), (492.1, 31.2), (488.7, 46.9)])], (488.7, 46.9), E1p, E1q, 0)
    f3 = fl([('M', [(529.1, 640.3)]), ('C', [(537.8, 659.1), (536.6, 681.8), (524, 700)])], (529.1, 640.3), T2p, T2q, 700)
    f4 = fl([('M', [(113.1, 59.7)]), ('C', [(104.4, 40.9), (105.6, 18.2), (118.2, 0)])], (113.1, 59.7), T1p, T1q, 0)
    for f, dx in ((f3, dw), (f4, 0)): pass
    return I(U(thick, thin, f1, f2, f3, f4), box)

def make_Y():
    # Regular: tay trái dày (mép ngoài qua (0,700) tới mép trái thân), tay phải mảnh (mép ngoài qua (W,700) tới mép phải thân), thân 102
    # Bold: rộng +23; thân 139, tâm thân dịch +11.5 (như T: nửa phần tăng bề rộng); mép ngoài tay giữ độ dốc của designer;
    # tay trái dày 100→146, tay phải mảnh 47→77, dày vào phía trong; loe trong + loe chân thân trượt theo mép
    dw = 23; W = 631.6 + dw; xs0, xs1 = 321.65 + dw / 2 - 69.5, 321.65 + dw / 2 + 69.5
    sL, sR = 270.6 / 375.2, (631.6 - 372.7) / (700 - 371)
    yL = 700 - xs0 / sL; yR = 700 - (W - xs1) / sR
    L0, L1 = (0, 700), (xs0, yL); R0, R1 = (W, 700), (xs1, yR)
    Li = offset_line(L0, L1, 146, 1); Ri = offset_line(R0, R1, 77, -1)
    crotch = inter(*Li, *Ri)
    def side(a, b, pt): return (b[0] - a[0]) * (pt[1] - a[1]) - (b[1] - a[1]) * (pt[0] - a[0])
    # thân
    stem = poly([(xs0, -1), (xs1, -1), (xs1, max(yL, yR) + 5), (xs0, max(yL, yR) + 5)])
    feet = pathops.Path(); feet.moveTo(xs1, 69.8); feet.cubicTo(xs1, 50.1, xs1 + 5.1, 30.7, xs1 + 14.9, 13.5); feet.lineTo(xs1 + 22.6, 0); feet.lineTo(xs0 - 22.6, 0)
    feet.lineTo(xs0 - 14.9, 13.5); feet.cubicTo(xs0 - 5.1, 30.7, xs0, 50.1, xs0, 69.8); feet.close()
    armL = poly([L0, L1, (xat(*Li, yL), yL) if False else inter(*Li, L1, (L1[0], L1[1] - 500)), Li[0]])
    arms = poly([L0, L1, (xs0, crotch[1] - 400), (xs1, crotch[1] - 400), R1, R0, (xat(*Ri, 700), 700), crotch, (xat(*Li, 700), 700)])
    # loe trong của designer (Regular Y), trượt theo mép trong mới
    a1 = (182.6, 617.8); dx1 = xat(*Li, a1[1]) - a1[0]
    f1 = wedge([('M', [(169.4, 700)]), ('C', [(156.6, 681.6), (154, 657.5), (182.6, 617.8)])], dx1, 0, [(xat(*Li, 700), 700)])
    a2 = (507.8, 618.7); dx2 = xat(*Ri, a2[1]) - a2[0]
    f2 = wedge([('M', [(507.8, 618.7)]), ('C', [(529.9, 657.8), (533.1, 681.7), (520.4, 700)])], dx2, 0, [(xat(*Ri, 700), 700)])
    box = poly([(0, 0), (W, 0), (W, 700), (0, 700)])
    return I(U(arms, stem, feet, f1, f2), box)

def make_W():
    # 4 nét: S1 dày \, S2 mảnh /, S3 dày \, S4 mảnh / ; hai V lồng nhau, hai nét giữa cắt nhau, đỉnh giữa cắt phẳng không loe
    # Bold: rộng +25; mép ngoài mỗi nét giữ (tỉ lệ theo x), đáy nhọn phẳng 20; dày 146 / mảnh 74 dày vào trong
    W0, dw = 779.6, 25; W = W0 + dw; sx = lambda x: x + dw * x / W0
    a1 = sx(272.6); a2 = sx(482.35)
    S1o = ((sx(25.5), 700), (a1 - 10, -11.3)); S2o = ((a1 + 10, -11.3), (sx(547), 700))
    S3o = ((sx(235.2), 700), (a2 - 10, -11.3)); S4o = ((a2 + 10, -11.3), (sx(756.6), 700))
    def B(o, w, side): return band(*o, w, side)
    s1 = B(S1o, 146, 1); s2 = B(S2o, 74, 1); s3 = B(S3o, 146, 1); s4 = B(S4o, 74, 1)
    def hull(o1, o2): return poly([(xat(*o1, 700), 700), (xat(*o1, -11.3), -11.3), (xat(*o2, -11.3), -11.3), (xat(*o2, 700), 700)])
    v1 = I(U(s1, s2), hull(S1o, S2o)); v2 = I(U(s3, s4), hull(S3o, S4o))
    # loe: S1 trái (ngoài), S1 phải (trong), S4 trái (trong), S4 phải (ngoài) — hình của designer, trượt theo mép
    S1i = offset_line(*S1o, 146, 1); S4i = offset_line(*S4o, 74, 1)
    def mv(attach, P, Q): return xat(P, Q, attach[1]) - attach[0]
    f1 = wedge([('M', [(52.9, 617.8)]), ('L', [(47, 635.3)]), ('C', [(44.9, 641.4), (42.4, 647.4), (39.2, 653)]), ('C', [(34.5, 661.4), (30.4, 667.8), (23.9, 675.5)]), ('L', [(0, 700)])],
               mv((52.9, 617.8), *S1o), 0, [(xat(*S1o, 700), 700)])
    f2 = wedge([('M', [(158.4, 624.4)]), ('L', [(157.4, 628.3)]), ('C', [(150.1, 652.3), (153.1, 678.3), (165.8, 700)])], mv((158.4, 624.4), *S1i), 0, [(xat(*S1i, 700), 700)])
    f3 = wedge([('M', [(678, 617.8)]), ('L', [(681.8, 628.3)]), ('C', [(689, 652.3), (688.8, 678.3), (676.2, 700)])], mv((678, 617.8), *S4i), 0, [(xat(*S4i, 700), 700)])
    f4 = wedge([('M', [(728.2, 623.4)]), ('L', [(735.7, 640.5)]), ('C', [(741.1, 653.2), (750, 665.5), (758.6, 675.5)]), ('L', [(779.6, 700)])], mv((728.2, 623.4), *S4o), 0, [(xat(*S4o, 700), 700)])
    box = poly([(0, -11.3), (W + 5, -11.3), (W + 5, 700), (0, 700)])
    return I(U(v1, v2, f1, f2, f3, f4), box)

if __name__ == '__main__':
    B = json.load(open(os.path.join(HERE, 'designer_B.json')))
    out = {'V': make_V(B), 'U': make_U(B), 'Z': make_Z(), 'X': make_X(), 'Y': make_Y(), 'W': make_W()}
    for ch, p in out.items():
        p = pathops.simplify(p, fix_winding=True)
        xs = [q[0] for v, ps in p.segments for q in ps]; x0 = min(xs)
        q = pathops.Path()
        for v, ps in p.segments:
            P = [(x - x0, y) for x, y in ps]
            if v == 'moveTo': q.moveTo(*P[0])
            elif v == 'lineTo': q.lineTo(*P[0])
            elif v == 'curveTo': q.cubicTo(*P[0], *P[1], *P[2])
            elif v == 'closePath': q.close()
        B[f'{ch}-Bold'] = [to_d(q)]
        print(ch, 'W', round(max(xs) - x0))
    json.dump(B, open(os.path.join(HERE, 'designer_B.json'), 'w'), separators=(',', ':'))
