#!/usr/bin/env python3
"""Dấu tiếng Việt (bộ .case cho chữ hoa), 67 chữ hoa tiếng Việt, dấu câu và ký hiệu — Regular & Bold.
Luật: docs/09-dau-tieng-viet-va-dau-cau.md (S11, S15).

Mọi nét cong / nét xiên của dấu là MỘT NÉT BÚT DẸT (S3): bút nghiêng PHI, độ dày vuông góc
    w(θ) = sqrt((N·sin(θ − PHI))² + m²) × taper
θ = hướng nét. Bảng N, m lấy từ bảng nét chữ (V, H của S2): nét đứng ≈ V, nét ngang ≈ H.
Viền là hai đường song song biến thiên, khớp lại bằng Bézier (least-squares, chia đôi tới khi sai số < 0.6 u).

    python3 tools/construct/ref/vn_punct.py   → designer_C.json (y lên, baseline 0, cap 700)
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pathops
from make_ref import parse, outline as ref_outline
OP = pathops.PathOp
PHI = math.radians(20)

# ---------- bảng nét ----------
# chữ:  Regular V 102 / H 40, Bold V 139 / H 68  →  bút chữ N, m  (đứng 0.94N⊕m ≈ V, ngang 0.34N⊕m ≈ H)
# dấu:  bút dấu = 0.74 N chữ, cùng m  (dấu nhẹ hơn thân chữ, đậm hơn nét mảnh)
T = {
    'Regular': dict(N=105, m=26, Nm=78, mm=26, V=102, H=40, t=44, dot=120, mdot=100, sx=1.0),
    'Bold':    dict(N=146, m=46, Nm=108, mm=44, V=139, H=68, t=74, dot=164, mdot=138, sx=1.08),
}
CAP, OV = 700, 11.3
GAP_ML, GAP_MM = 36, 30          # khe dấu–chữ, dấu–dấu (S11)
MARK_Y = CAP + OV + GAP_ML + 3   # 750: đáy dấu thấp nhất trên chữ hoa

# ---------- hình học cơ bản ----------
def bez(c, t):
    a, b, cc, d = c; s = 1 - t
    return (s**3*a[0] + 3*s*s*t*b[0] + 3*s*t*t*cc[0] + t**3*d[0], s**3*a[1] + 3*s*s*t*b[1] + 3*s*t*t*cc[1] + t**3*d[1])
def dbez(c, t):
    a, b, cc, d = c; s = 1 - t
    return (3*s*s*(b[0]-a[0]) + 6*s*t*(cc[0]-b[0]) + 3*t*t*(d[0]-cc[0]), 3*s*s*(b[1]-a[1]) + 6*s*t*(cc[1]-b[1]) + 3*t*t*(d[1]-cc[1]))
def ddbez(c, t):
    a, b, cc, d = c; s = 1 - t
    return (6*s*(cc[0] - 2*b[0] + a[0]) + 6*t*(d[0] - 2*cc[0] + b[0]), 6*s*(cc[1] - 2*b[1] + a[1]) + 6*t*(d[1] - 2*cc[1] + b[1]))
def split(c, t):
    a, b, cc, d = c
    L = lambda p, q: (p[0] + (q[0]-p[0])*t, p[1] + (q[1]-p[1])*t)
    ab, bc, cd = L(a, b), L(b, cc), L(cc, d); abc, bcd = L(ab, bc), L(bc, cd); m = L(abc, bcd)
    return (a, ab, abc, m), (m, bcd, cd, d)
def line(p, q): return (p, (p[0] + (q[0]-p[0])/3, p[1] + (q[1]-p[1])/3), (p[0] + 2*(q[0]-p[0])/3, p[1] + 2*(q[1]-p[1])/3), q)
def hermite(pts):
    """[(điểm, hướng tiếp tuyến)] → chuỗi cubic, tay nắm = dây cung/3 theo tiếp tuyến"""
    out = []
    for (p, tp), (q, tq) in zip(pts, pts[1:]):
        L = math.dist(p, q) / 3; a = math.hypot(*tp); b = math.hypot(*tq)
        out.append((p, (p[0] + tp[0]/a*L, p[1] + tp[1]/a*L), (q[0] - tq[0]/b*L, q[1] - tq[1]/b*L), q))
    return out
def arc(c, rx, ry, a0, a1, rot=0):
    segs = []; n = max(1, math.ceil(abs(a1 - a0) / 90 - 1e-9)); da = (a1 - a0) / n; cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = lambda x, y: (c[0] + x*cr - y*sr, c[1] + x*sr + y*cr)
    for i in range(n):
        s, e = math.radians(a0 + i*da), math.radians(a0 + (i+1)*da); k = 4/3*math.tan((e - s)/4)
        segs.append((R(rx*math.cos(s), ry*math.sin(s)), R(rx*math.cos(s) - k*rx*math.sin(s), ry*math.sin(s) + k*ry*math.cos(s)),
                     R(rx*math.cos(e) + k*rx*math.sin(e), ry*math.sin(e) - k*ry*math.cos(e)), R(rx*math.cos(e), ry*math.sin(e))))
    return segs

def P(cmds):
    """cmds: [('M',p),('L',p),('C',p1,p2,p3),('Z',)] → pathops.Path"""
    p = pathops.Path()
    for c in cmds:
        if c[0] == 'M': p.moveTo(*c[1])
        elif c[0] == 'L': p.lineTo(*c[1])
        elif c[0] == 'C': p.cubicTo(*c[1], *c[2], *c[3])
        else: p.close()
    return p
def U(*ps):
    ps = [p for p in ps if p is not None]; a = ps[0]
    for b in ps[1:]: a = pathops.op(a, b, OP.UNION)
    return a
def D(a, b): return pathops.op(a, b, OP.DIFFERENCE)
def I(a, b): return pathops.op(a, b, OP.INTERSECTION)
def rect(x0, y0, x1, y1): return P([('M', (x0, y0)), ('L', (x1, y0)), ('L', (x1, y1)), ('L', (x0, y1)), ('Z',)])
def poly(pts): return P([('M', pts[0])] + [('L', q) for q in pts[1:]] + [('Z',)])
def ellipse(c, rx, ry, rot=0):
    s = arc(c, rx, ry, 0, 360, rot); return P([('M', s[0][0])] + [('C', a[1], a[2], a[3]) for a in s] + [('Z',)])
def xform(p, f):
    out = pathops.Path()
    for v, pts in p.segments:
        q = [f(*x) for x in pts]
        if v == 'moveTo': out.moveTo(*q[0])
        elif v == 'lineTo': out.lineTo(*q[0])
        elif v == 'curveTo': out.cubicTo(*q[0], *q[1], *q[2])
        elif v == 'qCurveTo': out.qCurveTo(*q)
        elif v == 'closePath': out.close()
    return out
def move(p, dx, dy): return xform(p, lambda x, y: (x + dx, y + dy))
def scale(p, sx, sy=None, o=(0, 0)):
    sy = sx if sy is None else sy; return xform(p, lambda x, y: (o[0] + (x - o[0])*sx, o[1] + (y - o[1])*sy))
def bounds(p): return p.bounds   # (xmin, ymin, xmax, ymax)

# ---------- nét bút dẹt ----------
def _fit(Q, ts, p0, p3, t0, t3):
    """cubic qua p0,p3, tiếp tuyến t0,t3 (đơn vị), tay nắm a,b tối ưu least-squares cho các điểm Q tại tham số ts"""
    A11 = A12 = A22 = B1 = B2 = 0
    for q, t in zip(Q, ts):
        s = 1 - t; b1 = 3*s*s*t; b2 = 3*s*t*t; b0 = s**3 + b1; b3 = t**3 + b2
        base = (b0*p0[0] + b3*p3[0], b0*p0[1] + b3*p3[1]); u = (b1*t0[0], b1*t0[1]); v = (-b2*t3[0], -b2*t3[1]); r = (q[0]-base[0], q[1]-base[1])
        A11 += u[0]*u[0] + u[1]*u[1]; A12 += u[0]*v[0] + u[1]*v[1]; A22 += v[0]*v[0] + v[1]*v[1]
        B1 += u[0]*r[0] + u[1]*r[1]; B2 += v[0]*r[0] + v[1]*r[1]
    det = A11*A22 - A12*A12; L = math.dist(p0, p3)
    if abs(det) < 1e-9: a = b = L/3
    else: a = (B1*A22 - B2*A12)/det; b = (A11*B2 - A12*B1)/det
    if not (0.05*L < a < 2*L) or not (0.05*L < b < 2*L): a = b = L/3
    c = (p0, (p0[0] + a*t0[0], p0[1] + a*t0[1]), (p3[0] - b*t3[0], p3[1] - b*t3[1]), p3)
    err = max(math.dist(bez(c, t), q) for q, t in zip(Q, ts))
    return c, err

def stroke(segs, nib, taper=None, wabs=None):
    """segs: chuỗi cubic (tâm nét). nib=(N, m). taper(u)/wabs(u) theo tham số toàn cục u∈[0,1]. Trả Path."""
    n = len(segs); N, m = nib
    def raw(i, t):
        d = dbez(segs[i], t); th = math.atan2(d[1], d[0]); u = (i + t)/n
        if wabs: return wabs(u)
        return math.hypot(N*math.sin(th - PHI), m) * (taper(u) if taper else 1)
    # độ dày làm mượt theo chiều dài nét (cửa sổ Gauss σ = 14 u): độ cong nhảy ở mối nối Hermite không thành gờ trên viền
    K = 40; tab = []; acc = 0; prev = None
    for i in range(n):
        for k in range(K + (1 if i == n - 1 else 0)):
            t = k/K; q = bez(segs[i], t); acc += math.dist(prev, q) if prev else 0; prev = q; tab.append((acc, raw(i, t)))
    sig = 14.0; sm = []
    for s0, _ in tab:
        ws = [(math.exp(-((s1 - s0)/sig)**2/2), w) for s1, w in tab if abs(s1 - s0) < 3*sig]
        sm.append(sum(a*w for a, w in ws)/sum(a for a, _ in ws))
    def width(i, t):
        x = (i*K + t*K); j = min(int(x), len(sm) - 2); f = x - j
        return sm[j]*(1 - f) + sm[j + 1]*f
    def off(i, t, side):
        c = bez(segs[i], t); d = dbez(segs[i], t); L = math.hypot(*d) or 1; nv = (-d[1]/L*side, d[0]/L*side); w = width(i, t)/2
        dd = ddbez(segs[i], t); k = (d[0]*dd[1] - d[1]*dd[0]) / L**3          # độ cong; phía lòng không lùi quá 0.8 bán kính
        if side*k > 1e-9: Rm = 0.8/(side*k); w = (w**-4 + Rm**-4)**-0.25          # min mềm: không gờ khi chạm ngưỡng
        return (c[0] + nv[0]*w, c[1] + nv[1]*w)
    def side_curves(i, t0, t1, side, depth=0):
        K = 16; ts = [t0 + (t1 - t0)*k/K for k in range(K + 1)]; Q = [off(i, t, side) for t in ts]
        h = 1e-4*(t1 - t0)
        def tan(t, sgn):
            a, b = off(i, max(t0, t - h), side), off(i, min(t1, t + h), side); L = math.dist(a, b) or 1; return ((b[0]-a[0])/L, (b[1]-a[1])/L)
        # tham số theo chiều dài dây
        dl = [0]
        for a, b in zip(Q, Q[1:]): dl.append(dl[-1] + math.dist(a, b))
        us = [x/dl[-1] for x in dl] if dl[-1] > 0 else [k/K for k in range(K + 1)]
        c, err = _fit(Q, us, Q[0], Q[-1], tan(t0, 1), tan(t1, -1))
        if err > 0.6 and depth < 4:
            tm = (t0 + t1)/2; return side_curves(i, t0, tm, side, depth + 1) + side_curves(i, tm, t1, side, depth + 1)
        return [c]
    pieces = []
    for i in range(n):
        L = side_curves(i, 0, 1, 1); R = side_curves(i, 0, 1, -1)
        cmds = [('M', L[0][0])] + [('C', c[1], c[2], c[3]) for c in L] + [('L', R[-1][3])]
        cmds += [('C', c[2], c[1], c[0]) for c in reversed(R)] + [('Z',)]
        pieces.append(P(cmds))
    return clean(U(*pieces))

def clean(p, amin=400):
    """bỏ các vòng kín rất nhỏ (lỗ li ti do hợp các mảnh nét)"""
    out = pathops.Path(); cont = []; cur = []
    for v, ps in p.segments:
        cur.append((v, ps))
        if v == 'closePath': cont.append(cur); cur = []
    for c in cont:
        q = pathops.Path()
        for v, ps in c:
            getattr(q, {'moveTo': 'moveTo', 'lineTo': 'lineTo', 'curveTo': 'cubicTo', 'closePath': 'close'}[v])(*[x for pt in ps for x in pt])
        if abs(q.area) >= amin:
            for v, ps in c: getattr(out, {'moveTo': 'moveTo', 'lineTo': 'lineTo', 'curveTo': 'cubicTo', 'closePath': 'close'}[v])(*[x for pt in ps for x in pt])
    return out

def halfplane(y, above=True, x0=-2000, x1=4000):
    return rect(x0, y, x1, y + 4000) if above else rect(x0, y - 4000, x1, y)
def flat_top(p, flat):
    """cắt ngang đỉnh nhọn ở cao độ mà dây cung ngang dài đúng `flat` (như mặt cắt đỉnh A)"""
    x0, y0, x1, y1 = bounds(p); lo, hi = y0, y1
    for _ in range(40):
        mid = (lo + hi)/2; s = I(p, rect(x0 - 5, mid - 0.05, x1 + 5, mid + 0.05))
        w = (bounds(s)[2] - bounds(s)[0]) if list(s.segments) else 0
        if w > flat: lo = mid
        else: hi = mid
    return I(p, halfplane(lo, above=False))

def samples(p, step=2.0):
    pts = []; cur = None; st = None
    for v, ps in p.segments:
        if v == 'moveTo': cur = st = ps[0]; pts.append(cur)
        elif v in ('lineTo', 'closePath'):
            q = ps[0] if v == 'lineTo' else st; k = max(1, int(math.dist(cur, q)/step))
            pts += [(cur[0] + (q[0]-cur[0])*j/k, cur[1] + (q[1]-cur[1])*j/k) for j in range(1, k + 1)]; cur = q
        elif v == 'curveTo':
            c = (cur, *ps); k = max(2, int(sum(math.dist(a, b) for a, b in zip(c, c[1:]))/step))
            pts += [bez(c, j/k) for j in range(1, k + 1)]; cur = ps[2]
    return pts
def gap(a, b):
    A, B = samples(a, 3), samples(b, 3)
    return min(math.dist(p, q) for p in A for q in B)

# ---------- dấu (.case), gốc toạ độ: tâm ngang x=0, đáy y=0 ----------
def norm(p, cx=None):
    x0, y0, x1, y1 = bounds(p); cx = (x0 + x1)/2 if cx is None else cx
    return move(p, -cx, -y0)

def marks(w):
    t = T[w]; nib = (t['Nm'], t['mm']); sx = t['sx']; S = lambda x, y: (x*sx, y)
    M = {}
    # sắc: đi lên-phải → nét mảnh; đầu trên đậm hơn theo vết bút
    a = line(S(-48, 0), S(48, 122)); M['acute'] = norm(stroke([a], nib, taper=lambda u: 0.72 + 0.55*u))
    # huyền: đi xuống-phải → nét dày (D thu nhỏ), mảnh dần về chân
    g = line(S(-48, 122), S(48, 0)); M['grave'] = norm(stroke([g], nib, taper=lambda u: 1.08 - 0.42*u))
    # mũ: đỉnh A thu nhỏ — chân trái mảnh (/), chân phải dày (\), chân cắt ngang, đỉnh cắt phẳng 0.2 × nét dày; lòng mở.
    # Dựng như A: hai cạnh ngoài, hai cạnh trong (song song, cách đúng độ dày bút), giao nhau ở đỉnh trong.
    hw, hh = 150*sx, 150; ang = math.atan2(hh, hw)
    wl = 0.85*math.hypot(nib[0]*math.sin(ang - PHI), nib[1]); wr = 0.85*math.hypot(nib[0]*math.sin(-ang - PHI), nib[1])   # dấu nhỏ: 0.85 để lòng mũ mở ở Bold
    n_l = (-math.sin(ang), math.cos(ang)); n_r = (math.sin(ang), math.cos(ang))      # pháp tuyến hướng ra ngoài (lên)
    Lo0, Lo1 = (-hw, 0), (0, hh); Ro0, Ro1 = (hw, 0), (0, hh)                          # cạnh ngoài đi qua chân ngoài và đỉnh
    Li0 = (-hw + wl/math.sin(ang), 0); Ri0 = (hw - wr/math.sin(ang), 0)                # cạnh trong: dời theo phương ngang wl/sinα
    xi = lambda p, q, y: p[0] + (q[0] - p[0])*(y - p[1])/(q[1] - p[1])
    dirL = (Lo1[0] - Lo0[0], Lo1[1] - Lo0[1]); dirR = (Ro1[0] - Ro0[0], Ro1[1] - Ro0[1])
    # đỉnh trong = giao hai cạnh trong
    den = dirL[0]*dirR[1] - dirL[1]*dirR[0]; tt = ((Ri0[0] - Li0[0])*dirR[1] - (Ri0[1] - Li0[1])*dirR[0])/den
    inn = (Li0[0] + dirL[0]*tt, Li0[1] + dirL[1]*tt)
    flat = 0.2*nib[0]; ytop = hh*(1 - flat/(2*hw))
    M['circumflex'] = norm(poly([Lo0, (xi(Lo0, Lo1, ytop), ytop), (xi(Ro0, Ro1, ytop), ytop), Ro0, Ri0, inn, Li0]))
    # trăng: nửa elip trục nghiêng (như lòng O): ngoài là nửa elip, lòng là elip xoay 18° → dày dưới-trái, mảnh dưới-phải; đầu mảnh
    ro, rv = 118*sx, 96
    ri, ci = ro - 0.33*nib[0], 22; rvi = ci + rv - 0.72*nib[0]        # đáy dày 0.72 N, hai đầu ≈ 0.4 N
    br = D(ellipse((0, 0), ro, rv), ellipse((0, ci), ri, rvi, 12))
    M['breve'] = norm(I(br, halfplane(0, above=False)))
    # ngã: sóng; đoạn đi lên mảnh, đoạn đi xuống dày; hai đầu thon
    # tâm nét là một chu kỳ sin: y = 32 sin(2π(x+130)/260), đỉnh ở −65, đáy ở +65 (độ cong đỉnh R ≈ 53 > nửa nét)
    A_, kx = (32, 1.0) if sx == 1 else (28, 1.14)   # Bold: sóng giãn ngang 1.14, biên độ 28 → bán kính đỉnh ≈ 75 > nửa nét
    f = lambda x: (x*kx, A_*math.sin(2*math.pi*(x + 130)/260)); df = lambda x: (kx, A_*2*math.pi/260*math.cos(2*math.pi*(x + 130)/260))
    tl = hermite([(f(x), df(x)) for x in (-130, -65, 0, 65, 130)])
    M['tilde'] = norm(stroke(tl, nib, taper=lambda u: 0.8 + 0.2*math.sin(math.pi*u)))
    # hỏi: móc ? thu nhỏ, chân đứng ngắn; bút 0.85 bút dấu (nét cong nhỏ)
    # vòng móc là cung tròn r 52 (độ cong đều: không nút thắt ở phía lòng), rồi đuôi cong về giữa
    hc, hr = (4*sx, 100), 52*sx; a_end = math.radians(-40)
    e = (hc[0] + hr*math.cos(a_end), hc[1] + hr*math.sin(a_end)); te = (math.sin(a_end), -math.cos(a_end))
    hk = arc(hc, hr, hr, 168, -40) + hermite([(e, te), (S(2, 4), (-0.1, -1))])
    M['hook'] = norm(stroke(hk, (nib[0]*0.8, nib[1]), taper=lambda u: 1.1 - 0.25*u))
    # nặng: cùng họ chấm với dấu chấm (tròn), nhỏ hơn
    M['dotbelow'] = norm(ellipse((0, 0), t['mdot']/2, t['mdot']/2))
    # sừng ơ ư (một tấm chung): gốc (0,0) bám vào mép phải chữ; nét đi ra phải rồi vút lên, dày dần, kết bằng giọt (họ chấm)
    V = t['V']; hn = hermite([(S(-50, -4), (1, 0.06)), (S(58, 40), (0.5, 1)), (S(78, 118), (0, 1))])
    hs = stroke(hn, (1, 1), wabs=lambda u: V*(0.34 + 0.28*u))
    M['horn'] = U(hs, ellipse(S(78, 118), 0.31*V, 0.31*V))
    return M

# ---------- chữ gốc ----------
def load():
    S = {}
    for f in ('designer_A.json', 'designer_B.json'): S.update(json.load(open(os.path.join(HERE, f))))
    return S
def letter(S, ch, w): return ref_outline(S[f'{ch}-{w}'])

def anchor_x(ch, p):
    x0, y0, x1, y1 = bounds(p)
    if ch == 'E': return x0 + 0.44*(x1 - x0)          # tâm thị giác của E nằm lệch về thân
    return (x0 + x1)/2

def horn_anchor(ch, p, w):
    """điểm bám của sừng: Ư — mép ngoài thân phải ở 0.91 cap; Ơ — vai phải của vòng O (góc 38°)"""
    x0, y0, x1, y1 = bounds(p)
    if ch == 'U':
        y = 0.9*CAP; s = I(p, rect(x0, y - 0.05, x1, y + 0.05)); return (bounds(s)[2], y)
    a = math.radians(38); cx, cy = (x0 + x1)/2, (y0 + y1)/2; rx, ry = (x1 - x0)/2, (y1 - y0)/2
    return (cx + rx*math.cos(a), cy + ry*math.sin(a))

TONES = {'': None, '́': 'acute', '̀': 'grave', '̉': 'hook', '̃': 'tilde', '̣': 'dotbelow'}
BASES = {'A': ('A', None), 'Ă': ('A', 'breve'), 'Â': ('A', 'circumflex'), 'E': ('E', None), 'Ê': ('E', 'circumflex'),
         'I': ('I', None), 'O': ('O', None), 'Ô': ('O', 'circumflex'), 'Ơ': ('O', 'horn'), 'U': ('U', None), 'Ư': ('U', 'horn'), 'Y': ('Y', None)}

def place_above(lower, m, cx, min_gap=GAP_MM):
    """đặt dấu m (đáy y=0, tâm x=0) chồng lên trên `lower`, tâm cx, khe đúng min_gap"""
    top = bounds(lower)[3]; q = move(m, cx, top + 4)
    while gap(lower, q) < min_gap + 2: q = move(q, 0, 2)
    return q
def place_right(circ, m, w):
    """dấu thanh đi kèm mũ (Ấ Ầ Ẩ): bên phải mũ, đáy ngang 0.45 chiều cao mũ, đẩy sang phải tới khi khe = 30"""
    x0, y0, x1, y1 = bounds(circ); mx = bounds(m)
    q = move(m, (x0 + x1)/2 + 40 - mx[0], y0 + 0.45*(y1 - y0))
    while gap(circ, q) < GAP_MM + 2: q = move(q, 2, 0)
    return q

def compose(S, M, ch_base, mod, tone, w):
    base = letter(S, ch_base, w); cx = anchor_x(ch_base, base); parts = [base]; above = []
    if mod == 'horn':
        ax, ay = horn_anchor(ch_base, base, w); parts.append(move(M['horn'], ax, ay))
    elif mod:
        m0 = move(M[mod], cx, MARK_Y); above.append(m0)
    if tone and tone != 'dotbelow':
        m = M[tone]
        if mod == 'circumflex' and tone in ('acute', 'grave', 'hook'): above.append(place_right(above[0], m, w))
        elif above: above.append(place_above(above[-1], m, cx))
        else: above.append(move(m, cx, MARK_Y))
    if tone == 'dotbelow':
        d = M['dotbelow']; db = bounds(d); parts.append(move(d, cx, min(-OV, bounds(base)[1]) - GAP_ML - (db[3] - db[1]) - 2))   # dưới đáy thật (U −14.2)
    return U(*parts, *above)

def dstroke(S, w):
    """Đ: thanh ngang H cắt qua thân trái của D ở 0.5 cap (tâm thị giác ngang thanh H)"""
    t = T[w]; base = letter(S, 'D', w)
    s = I(base, rect(-10, 349.95, 400, 350.05)); x_out = bounds(s)[0]
    # mép ngoài thân (bỏ phần loe): đo ở giữa thân; mép trong = mép ngoài + V
    x_in = x_out + t['V']; bar = rect(x_out - 0.62*t['V'], 350 - t['H']/2 - 4, x_in + 0.9*t['V'], 350 + t['H']/2 + 4)
    return U(base, bar)

# ---------- dấu câu và ký hiệu (y lên, baseline 0) ----------
def dot(c, d): return ellipse(c, d/2, d/2)
def comma_shape(t, w):
    d = t['dot']; r = d/2; c = (r, r - 3)
    tail = hermite([((c[0] + 0.22*d, c[1] + 0.05*d), (0.15, -1)), ((c[0] + 0.12*d, -0.62*d), (-0.6, -1)), ((c[0] - 0.42*d, -1.25*d), (-1, -0.75))])
    tl = stroke(tail, (1, 1), wabs=lambda u: d*(0.62*(1 - u)**1.1 + 0.07))
    return U(dot(c, d), tl)
def wedge(xc, ytop, ybot, wt, wb, conc=0.18):
    """nét thon (chấm than, nháy): đỉnh cắt ngang rộng wt, chân rộng wb, hai cạnh lõm nhẹ như loe"""
    a, b = (xc - wt/2, ytop), (xc - wb/2, ybot); c, d = (xc + wb/2, ybot), (xc + wt/2, ytop)
    k = conc*(wt - wb)/2
    return P([('M', a), ('C', (a[0] + k, a[1] - (a[1]-b[1])*0.35), (b[0], b[1] + (a[1]-b[1])*0.3), b),
              ('C', (b[0] + wb*0.1, b[1] - wb*0.45), (c[0] - wb*0.1, c[1] - wb*0.45), c),
              ('C', (c[0], c[1] + (d[1]-c[1])*0.3), (d[0] - k, d[1] - (d[1]-c[1])*0.35), d), ('Z',)])

def punct(S, w):
    t = T[w]; d = t['dot']; r = d/2; V, H = t['V'], t['H']; nib = (t['N'], t['m']); G = {}
    bold = w == 'Bold'
    G['.'] = dot((r, r - 3), d)
    G[','] = comma_shape(t, w)
    up = 480 - d                                          # chấm trên của : ; — đỉnh ở 480 (x-height tạm, S10)
    G[':'] = U(dot((r, r - 3), d), dot((r, up + r), d))
    G[';'] = U(comma_shape(t, w), dot((r, up + r), d))
    ex_w = 0.98*V; G['!'] = U(wedge(ex_w/2, 700, 220 + 0.15*d, ex_w, 0.42*V), dot((ex_w/2, r - 3), d))
    # ?: một nét bút (luật bút chữ): đầu trái có giọt, vòng phải, thân đứng xuống
    qx = 1.0 if not bold else 1.08
    q = hermite([((26*qx, 548), (0.15, 1)), ((168*qx, 711 - 0.5*H), (1, 0)), ((312*qx, 548), (0, -1)), ((178*qx, 360), (-0.55, -1)),
                 ((166*qx, 250 + 0.1*d), (0, -1))])
    qs = stroke(q, nib, taper=lambda u: 1.0 if u > 0.15 else 1.0 + (0.15 - u)*2.2)
    qb = bounds(qs); G['?'] = U(qs, dot((166*qx, r - 3), d))
    # nháy thẳng ' "
    qt = lambda xc: wedge(xc, 711, 455, 0.86*V, 0.34*V, 0.25)
    G["'"] = qt(0.43*V); G['"'] = U(qt(0.43*V), qt(0.43*V + 0.86*V + 0.75*V))
    # nháy cong ’ ‘ ” “ = dấu phẩy nâng lên (đỉnh chấm ở 711)
    cm = comma_shape(t, w); cb = bounds(cm); rq = move(cm, -cb[0], 711 - cb[3] + 0.0)
    rb = bounds(rq); lq = xform(rq, lambda x, y: (rb[0] + rb[2] - x, rb[1] + rb[3] - y))   # ‘ = ’ xoay 180°
    G['’'] = rq; G['‘'] = lq
    sp = (bounds(rq)[2] - bounds(rq)[0]) + 0.6*V
    G['”'] = U(rq, move(rq, sp, 0)); G['“'] = U(lq, move(lq, sp, 0))
    # gạch nối và gạch ngang: dày 0.58 V (nằm giữa H và V), tâm ở 330 (giữa cap, hạ quang học)
    hy = 0.58*V; yc = 330
    G['-'] = rect(0, yc - hy/2, 250 + (20 if bold else 0), yc + hy/2)
    G['–'] = rect(0, yc - hy/2*0.9, 420, yc + hy/2*0.9)
    G['—'] = rect(0, yc - hy/2*0.9, 920, yc + hy/2*0.9)
    # ngoặc tròn: một nét bút cong, dày ở giữa (đứng) mảnh ở hai đầu
    pr = hermite([((250, 860), (-0.78, -1)), ((62, 355), (0, -1)), ((250, -150), (0.78, -1))])
    par = stroke(pr, (t['N']*0.86, t['m']*0.8)); par = move(par, -bounds(par)[0], 0); G['('] = par
    pb = bounds(par); G[')'] = xform(par, lambda x, y: (pb[2] - x, y))
    # ngoặc vuông: thân 0.86 V, tay H×1.15 dài 0.5 cap/ 2.3
    bv, bh, bl = 0.86*V, 1.15*H, 150 + (10 if bold else 0)
    br = U(rect(0, -150, bv, 860), rect(0, -150, bl, -150 + bh), rect(0, 860 - bh, bl, 860)); G['['] = br
    G[']'] = xform(br, lambda x, y: (bl - x, y))
    # gạch chéo: nét / (mảnh theo bút) nhưng đủ đậm để đứng một mình: 0.58 V
    sw = 0.58*V; G['/'] = poly([(0, -130), (sw*1.08, -130), (330 + sw*1.08, 830), (330, 830)])
    # toán: + = × — đứng 0.62 V, ngang 0.55 V (ngang dày như số, Hf), cùng tâm 330
    mv, mh, ms = 0.62*V, 0.55*V, 500
    G['+'] = U(rect(ms/2 - mv/2, yc - ms/2 + 10, ms/2 + mv/2, yc + ms/2 - 10), rect(0, yc - mh/2, ms, yc + mh/2))
    G['='] = U(rect(0, yc + 95 - mh/2, ms, yc + 95 + mh/2), rect(0, yc - 95 - mh/2, ms, yc - 95 + mh/2))
    xb = I(U(stroke([line((0, yc - 200), (400, yc + 200))], (1, 1), wabs=lambda u: 0.6*V),
             stroke([line((0, yc + 200), (400, yc - 200))], (1, 1), wabs=lambda u: 0.6*V)), rect(0, -1000, 400, 2000))
    G['×'] = I(xb, rect(-10, yc - 200, 410, yc + 200))
    # #: hai nét đứng nghiêng 10°, 0.66 V; hai ngang 0.5 V
    hw, gv, gh = 560, 0.66*V, 0.5*V; sl = math.tan(math.radians(10))
    def slant(xc): return poly([(xc - gv/2 - 350*sl, 0), (xc + gv/2 - 350*sl, 0), (xc + gv/2 + 350*sl, 700), (xc - gv/2 + 350*sl, 700)])
    G['#'] = U(slant(0.37*hw), slant(0.69*hw), rect(10, 235 - gh/2, hw, 235 + gh/2), rect(0, 470 - gh/2, hw - 10, 470 + gh/2))
    # %: hai vòng nhỏ kiểu O (lòng nghiêng 30°) + nét chéo
    def ring(c, rx, ry):
        o = ellipse(c, rx, ry); i = ellipse((c[0], c[1]), rx - 0.6*V, ry - 0.36*V - 4, 30); return D(o, i)
    pw = 640 + (30 if bold else 0); rx, ry = 118 + (8 if bold else 0), 150
    G['%'] = U(ring((rx, 700 - ry), rx, ry), ring((pw - rx, ry), rx, ry),
              poly([(pw*0.2, -11), (pw*0.2 + 0.6*V, -11), (pw*0.8 + 0.6*V, 711), (pw*0.8, 711)]))
    # $: S của designer + nét đứng H xuyên qua, vươn ±90
    s = letter(S, 'S', w); sb = bounds(s); xc = (sb[0] + sb[2])/2; bw = 1.1*H
    G['$'] = U(s, rect(xc - bw/2, -100, xc + bw/2, 800))
    # €: C của designer + hai thanh H vươn ra trái
    c = letter(S, 'C', w); cb = bounds(c); ew = cb[2] - cb[0]; eh = H*1.05
    e = U(c, rect(-0.12*ew, 300 - eh/2, 0.6*ew, 300 + eh/2), rect(-0.12*ew, 430 - eh/2, 0.66*ew, 430 + eh/2))
    G['€'] = e
    # &: một nét bút liền (luật bút chữ) — chân phải đi lên-trái (dày), vòng trên, bụng dưới, tay phải vút lên
    k = 1.0 if not bold else 1.12; Hh = 0.5*H
    # vòng trên là oval đứng (phải 350, trái 160), nét trong vòng nhẹ hơn 0.78 (lòng mở như lòng B trên)
    amp = hermite([((585*k, 8), (-0.72, 1)), ((330*k, 380), (-0.3, 1)), ((352*k, 572), (0, 1)), ((256*k, 711 - Hh - 6), (-1, 0)),
                   ((160*k, 592), (0, -1)), ((206*k, 470), (0.12, -1)), ((120*k, 300), (-0.62, -1)), ((62*k, 170), (0, -1)),
                   ((225*k, -11 + Hh + 4), (1, 0)), ((432*k, 118), (0.9, 1)), ((540*k, 318), (0.35, 1))])
    lt = lambda u: 1 - (0.22 if not bold else 0.3)*max(0, 1 - abs(u - 0.32)/0.2)
    G['&'] = stroke(amp, (t['N']*0.9, t['m']), taper=lt)
    # @: vòng ngoài là nét bút gần trọn vòng; bên trong là "a" một tầng (lòng elip + thân)
    R0, cy = 335, 300; cx0 = R0 + 50
    # thân "a" đi xuống, vòng chữ U (bán kính ≈ 118) sang phải, nhập vào vòng ngoài ở góc 0° rồi chạy ngược chiều kim đồng hồ tới 300°
    ring_o = arc((cx0, cy), R0, R0, 0, 300)
    stem_c = hermite([((cx0 + 100, 470), (0, -1)), ((cx0 + 100, 300), (0, -1)), ((cx0 + 217, 166), (1, 0)), ((cx0 + R0, cy), (0, 1))])
    at = U(stroke(stem_c + ring_o, (t['N']*0.8, t['m']*0.85)), D(ellipse((cx0 - 12, cy + 10), 128, 160), ellipse((cx0 - 12 + 6, cy + 10), 128 - 0.62*V, 160 - 0.32*V, 25)))
    G['@'] = at
    return G

def to_d(p):
    out = []
    for v, ps in p.segments:
        k = {'moveTo': 'M', 'lineTo': 'L', 'curveTo': 'C', 'closePath': 'Z'}.get(v)
        if k is None: raise ValueError(v)
        out.append(k + ' '.join('%.1f %.1f' % q for q in ps))
    return ''.join(out)

def build():
    S = load(); out = {}; Wover = {}; meta = {}
    for w in ('Regular', 'Bold'):
        M = marks(w)
        for bch, (base, mod) in BASES.items():
            for mk, tone in TONES.items():
                if not mod and not tone: continue
                ch = __import__('unicodedata').normalize('NFC', bch + mk)
                p = compose(S, M, base, mod, tone, w); key = f'{ch}-{w}'
                out[key] = [to_d(p)]; Wover[key] = round(bounds(letter(S, base, w))[2])
        dd = dstroke(S, w); b = bounds(dd); dd = move(dd, -b[0], 0); out[f'Đ-{w}'] = [to_d(dd)]
        for ch, p in punct(S, w).items():
            b = bounds(p); p = move(p, -b[0], 0); out[f'{ch}-{w}'] = [to_d(p)]
        meta[w] = {k: round(bounds(v)[3] - bounds(v)[1], 1) for k, v in M.items()}
    out['_W'] = Wover
    json.dump(out, open(os.path.join(HERE, 'designer_C.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('ok', len(out) - 1, meta)

if __name__ == '__main__':
    build()
