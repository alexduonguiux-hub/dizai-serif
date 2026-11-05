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
            t = k/K; q = bez(segs[i], t); acc += math.dist(prev, q) if prev else 0; prev = q
            d = dbez(segs[i], t); dd = ddbez(segs[i], t); Ld = math.hypot(*d) or 1
            tab.append((acc, raw(i, t), (d[0]*dd[1] - d[1]*dd[0]) / Ld**3))
    sig = 22.0; sm = []; skap = []   # độ cong cũng làm mượt: mối nối Hermite có độ cong nhảy bậc
    for s0, _, _ in tab:
        ws = [(math.exp(-((s1 - s0)/sig)**2/2), w, kk) for s1, w, kk in tab if abs(s1 - s0) < 3*sig]
        sw = sum(a for a, _, _ in ws); sm.append(sum(a*w for a, w, _ in ws)/sw)
        wk = [(math.exp(-((s1 - s0)/8)**2/2), kk) for s1, _, kk in tab if abs(s1 - s0) < 24]   # độ cong: σ 8 (giữ đỉnh)
        skap.append(sum(a*kk for a, kk in wk)/sum(a for a, _ in wk))
    def interp(arr, i, t):
        x = min(max(i*K + t*K, 0), len(arr) - 1); j = min(int(x), len(arr) - 2); f = x - j
        return arr[j]*(1 - f) + arr[j + 1]*f
    def width(i, t): return interp(sm, i, t)
    def off(i, t, side):
        c = bez(segs[i], t); d = dbez(segs[i], t); L = math.hypot(*d) or 1; nv = (-d[1]/L*side, d[0]/L*side); w = width(i, t)/2
        k = interp(skap, i, t)          # độ cong (đã làm mượt); phía lòng không lùi quá 0.72 bán kính
        # không kẹp: chỗ mép trong gập (đuôi én) do pathops gộp lại thành góc trong, lỗ li ti bị clean() bỏ
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
    # viền liền một mạch: lấy mẫu dày cả hai mép trên toàn nét, khớp chuỗi Bézier (chia đôi khi sai số > 0.6 u),
    # khép bằng hai nắp. Không ghép mảnh nên không có gờ ở mối nối; chỗ nét tự cắt (&) do pathops gộp (winding khác 0).
    KS = 48; prm = [(i, k/KS) for i in range(n) for k in range(KS)] + [(n - 1, 1.0)]
    def chain(side):
        Q = [off(i, t, side) for i, t in prm]
        Q2 = [Q[0]]
        for q in Q[1:]:
            if math.dist(q, Q2[-1]) > 0.05: Q2.append(q)
        Q = Q2
        def tanq(j):
            a, b = Q[max(0, j - 1)], Q[min(len(Q) - 1, j + 1)]; L = math.dist(a, b) or 1; return ((b[0]-a[0])/L, (b[1]-a[1])/L)
        def fit(j0, j1, depth=0):
            pts = Q[j0:j1 + 1]; dl = [0]
            for a_, b_ in zip(pts, pts[1:]): dl.append(dl[-1] + math.dist(a_, b_))
            us = [x/dl[-1] for x in dl]
            c, err = _fit(pts, us, pts[0], pts[-1], tanq(j0), tanq(j1))
            if err > 0.6 and j1 - j0 > 3 and depth < 8:
                jm = (j0 + j1)//2; return fit(j0, jm, depth + 1) + fit(jm, j1, depth + 1)
            return [c]
        return fit(0, len(Q) - 1)
    L = chain(1); R = chain(-1)
    cmds = [('M', L[0][0])] + [('C', c[1], c[2], c[3]) for c in L] + [('L', R[-1][3])]
    cmds += [('C', c[2], c[1], c[0]) for c in reversed(R)] + [('Z',)]
    pieces = [pathops.simplify(P(cmds))]
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

FR, FF = 112, 23      # luật loe S5 / L1 (glyphs.js): compa r 112, chìa 23 u khỏi mép nét, trên đường cắt

def flare(Eg, u, n, cut=None, rad=FR, f=FF):
    """vùng loe ở một góc đầu nét: Eg = góc (mép nét ∩ đường cắt), u = hướng dọc mép nét đi vào thân nét,
    n = pháp tuyến ra ngoài. Mũi loe Pt = Eg + n·f trên đường cắt; một cung tròn r tiếp xúc mép nét, qua Pt (lõm)."""
    cut = cut or n                                   # hướng đường cắt (ra ngoài); mặc định vuông góc mép nét
    Pt = (Eg[0] + cut[0]*f, Eg[1] + cut[1]*f)
    w = (Pt[0] - Eg[0], Pt[1] - Eg[1]); uw = u[0]*w[0] + u[1]*w[1]; nw = n[0]*w[0] + n[1]*w[1]; ww = w[0]**2 + w[1]**2
    s_ = uw + math.sqrt(max(0, uw*uw - ww + 2*rad*nw))
    T = (Eg[0] + u[0]*s_, Eg[1] + u[1]*s_); C = (T[0] + n[0]*rad, T[1] + n[1]*rad)
    a0 = math.degrees(math.atan2(Pt[1] - C[1], Pt[0] - C[0])); a1 = math.degrees(math.atan2(T[1] - C[1], T[0] - C[0]))
    d = (a1 - a0 + 180) % 360 - 180
    segs = arc(C, rad, rad, a0, a0 + d)
    back = (Eg[0] - cut[0]*6, Eg[1] - cut[1]*6)                     # trên đúng đường cắt, lấn vào thân: không bậc
    return P([('M', back), ('L', Pt)] + [('C', c[1], c[2], c[3]) for c in segs] + [('L', (T[0] - n[0]*3, T[1] - n[1]*3)), ('Z',)])

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

# hỏi (designer 04/11: "dấu hỏi của bold lỗi", "sửa lại bụng của dấu hỏi regular lẫn bold"): vòng r 52 kết thúc ở −40° làm
# lòng thắt nhọn ở góc dưới-phải rồi phình (bụng gợn) khi chuyển sang đuôi; Bold r 60 với bút 0.8 bít lòng, đuôi gập mẩu mảnh.
# Nay: vòng r 58 (tâm y 106) dừng sớm ở −20°, đuôi dài hơn về (0, 4) → mép lòng chảy liền xuống cổ như dấu ?.
# Bold = tâm nét Regular phóng đều 1.2 (giữ tỉ lệ vòng/đuôi), bút 0.70 × bút dấu Bold.
HOOK_B = (1.2, 0.70); HOOK_END = -20; HOOK_TAIL = (0, 4); HOOK_R = 58; HOOK_C = 106
Q_NARROW = (20, 200, 45)   # ? hẹp ngang 45 u: Regular 420 → 375, Bold 436 → 391
HOOK_S = {'Regular': 0.38, 'Bold': 0.52}
def _q2c(p):
    """quadratic (sau boolean / stroke) → cubic; nhiều điểm điều khiển: điểm on-curve ngầm ở giữa"""
    out = pathops.Path(); cur = None
    for v, ps in p.segments:
        if v == 'moveTo': out.moveTo(*ps[0]); cur = ps[0]
        elif v == 'lineTo': out.lineTo(*ps[0]); cur = ps[0]
        elif v == 'curveTo': out.cubicTo(*ps[0], *ps[1], *ps[2]); cur = ps[2]
        elif v == 'qCurveTo':
            ctrl, end = list(ps[:-1]), ps[-1]
            for i, c in enumerate(ctrl):
                e = ((c[0] + ctrl[i + 1][0])/2, (c[1] + ctrl[i + 1][1])/2) if i + 1 < len(ctrl) else end
                out.cubicTo(cur[0] + 2/3*(c[0] - cur[0]), cur[1] + 2/3*(c[1] - cur[1]), e[0] + 2/3*(c[0] - e[0]), e[1] + 2/3*(c[1] - e[1]), *e); cur = e
        elif v == 'closePath': out.close()
    return out
HOOK_T = {'Regular': 54.0, 'Bold': 79.0}
HOOK_VEC = {'Regular': 1.54, 'Bold': 1.75}       # thành phải vector 35 px → Regular 54 u; Bold 61 u + bù nét tới 79
def hook_from_q(w):
    """dấu hỏi = VECTOR CỦA DESIGNER (Figma 2130:1183, hook_vec.json — designer 05/11 "Link vector dấu hỏi"): lật y, thu phóng
    HOOK_VEC; Bold bù nét (góc vuông) cho thành phải = HOOK_T Bold. Móc dưới (U+0327, Ç ç) = dấu này lật dọc."""
    J = json.load(open(os.path.join(HERE, 'hook_vec.json'))); k = HOOK_VEC[w]
    hk = xform(ref_outline([J['d']]), lambda x, y: (x*k, (J['h'] - y)*k))
    yb = bounds(hk); ym = yb[1] + 0.53*(yb[3] - yb[1]); runs = []
    for v, ps in I(hk, rect(-100, ym - 0.05, 2000, ym + 0.05)).segments:
        if v == 'moveTo': cur = [ps[0][0]]
        elif ps: cur += [p_[0] for p_ in ps]
        if v == 'closePath': runs.append((min(cur), max(cur)))
    r0 = max(runs, key=lambda r: r[1]); d = max(0.0, (HOOK_T[w] - (r0[1] - r0[0]))/2)
    if d > 0.5:
        st = pathops.Path(); st.addPath(hk); st.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
        st.convertConicsToQuads(); hk = _q2c(I(_q2c(U(hk, st)), rect(-500, yb[1], 3000, 3000)))
    return norm(hk)

def marks(w):
    t = T[w]; nib = (t['Nm'], t['mm']); sx = t['sx']; S = lambda x, y: (x*sx, y)
    M = {}
    # sắc: đi lên-phải → nét mảnh; đầu trên đậm hơn theo vết bút
    # sắc / huyền (designer 04/11: "dấu sắc và huyền không đồng bộ"): một cặp đối xứng gương — cùng dài, cùng góc,
    # cùng hình nêm: đầu trên dày 0.80 N, chân 0.36 N; huyền = sắc lật ngang (không còn chênh mảnh/dày theo bút)
    a = line(S(-48, 0), S(48, 122)); wt, wb = 0.80*nib[0], 0.36*nib[0]
    M['acute'] = norm(stroke([a], nib, wabs=lambda u: wb + (wt - wb)*u))
    M['grave'] = norm(xform(M['acute'], lambda x, y: (-x, y)))
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
    # trăng (designer 04/11: "dấu ă cũng hơi lỗi"): lưỡi liềm ĐỐI XỨNG — nửa elip ngoài (ro, rv) trừ lòng elip có tâm nâng
    # lên 0.5 rv: đáy dày tb = 0.66 N, hai đầu thon te = 0.42 N, cắt ngang; lòng sâu nên không bẹt ở Bold.
    ro, rv = 112*sx, (90 if sx == 1 else 100); tb, te = 0.66*nib[0], 0.42*nib[0]
    ci = 0.5*rv; ryi = ci + rv - tb; rxi = (ro - te)/math.sqrt(1 - (ci/ryi)**2)
    br = D(ellipse((0, 0), ro, rv), ellipse((0, ci), rxi, ryi))
    M['breve'] = norm(I(br, halfplane(0, above=False)))
    # ngã: sóng; đoạn đi lên mảnh, đoạn đi xuống dày; hai đầu thon
    # tâm nét là một chu kỳ sin: y = 32 sin(2π(x+130)/260), đỉnh ở −65, đáy ở +65 (độ cong đỉnh R ≈ 53 > nửa nét)
    A_, kx = (32, 1.0) if sx == 1 else (28, 1.14)   # Bold: sóng giãn ngang 1.14, biên độ 28 → bán kính đỉnh ≈ 75 > nửa nét
    f = lambda x: (x*kx, A_*math.sin(2*math.pi*(x + 130)/260)); df = lambda x: (kx, A_*2*math.pi/260*math.cos(2*math.pi*(x + 130)/260))
    tl = hermite([(f(x), df(x)) for x in (-130, -65, 0, 65, 130)])
    M['tilde'] = norm(stroke(tl, nib, taper=lambda u: 0.8 + 0.2*math.sin(math.pi*u)))
    # hỏi: móc ? thu nhỏ; vòng là cung tròn HOOK_R (độ cong đều), rồi đuôi cong về giữa; bút 0.8 bút dấu (xem HOOK_*)
    hc, hr = (4, HOOK_C), HOOK_R; a_end = math.radians(HOOK_END)
    e = (hc[0] + hr*math.cos(a_end), hc[1] + hr*math.sin(a_end)); te = (math.sin(a_end), -math.cos(a_end))
    k = 1.0 if sx == 1 else HOOK_B[0]
    hk = arc(hc, hr, hr, 168, HOOK_END) + hermite([(e, te), (HOOK_TAIL, (-0.1, -1))])
    hk = [tuple((q[0]*k, q[1]*k) for q in sg) for sg in hk]
    M['hook'] = norm(xform(stroke(hk, (nib[0]*(0.8 if sx == 1 else HOOK_B[1]), nib[1]), taper=lambda u: 1.1 - 0.25*u),
                           lambda x, y: (x*sx, y)))
    # hỏi VẼ LẠI (designer 05/11: "Vẽ lại dấu hỏi và các móc"): luật S11 "hỏi = móc ? thu nhỏ" — lấy ĐÚNG phần móc của dấu ?
    # (đầu số 2 của designer + cổ, bỏ chấm), thu HOOK_S, bù nét để nét dày bằng nét dấu cũ (Regular 54, Bold 79) — cùng hình,
    # cùng độ cong với ? và 2, không còn nét bút tự dựng
    M['hook'] = hook_from_q(w)
    # nặng: cùng họ chấm với dấu chấm (tròn), nhỏ hơn
    M['dotbelow'] = norm(ellipse((0, 0), t['mdot']/2, t['mdot']/2))
    # sừng ơ ư (một tấm chung): gốc (0,0) bám vào mép phải chữ; nét đi ra phải rồi vút lên, dày dần.
    # Đầu sừng cắt phẳng ngang như đầu thân (designer 04/11: "dấu ư không nên tròn" — bỏ giọt tròn)
    # Tâm nét là MỘT cung Bézier (không nối đoạn) để đường cong liền mượt (designer 04/11: "điều chỉnh nét cong của dấu ư
    # lại cho smooth"); độ dày tăng theo smoothstep 0.34 V → 0.64 V.
    V = t['V']; hn = [(S(-50, -2), S(30, -2), S(82, 40), S(84, 132))]
    M['horn'] = stroke(hn, (1, 1), wabs=lambda u: V*(0.34 + 0.30*(u*u*(3 - 2*u))))
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
    """điểm bám của sừng (designer 04/11: "dấu ư lỗi và không đồng bộ"):
    Ơ — vai phải của vòng O (góc 38°); Ư — mép ngoài thân phải ở CÙNG cao độ với Ơ, nên đầu sừng hai chữ ngang nhau.
    Ở Ư sừng thay cho loe ngoài của thân phải (loe bị cắt trong compose), không còn khe giữa loe và sừng."""
    x0, y0, x1, y1 = bounds(p)
    if ch == 'U':
        y = CAP/2 + (CAP + 2*OV)/2*math.sin(math.radians(38))
        s = I(p, rect(x0, y - 0.05, x1, y + 0.05)); return (bounds(s)[2], y)
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
        ax, ay = horn_anchor(ch_base, base, w)
        if ch_base == 'U': parts[0] = D(base, rect(ax, ay, ax + 300, CAP + 50))   # bỏ loe ngoài thân phải: sừng thay chỗ loe
        parts.append(move(M['horn'], ax, ay))
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
    # đuôi rời chấm TIẾP TUYẾN ở điểm phải nhất của chấm: mép phải đuôi trùng mép chấm, không có mép thẳng thò ra
    # (designer 04/11: "vẫn lỗi nét thừa"); đuôi thon dần, cong xuống-trái.
    # đuôi ĐỀU NÉT (designer 04/11: "thay vì làm nhỏ dần nét thì làm nó đều đi"): một độ dày wt = 0.36 Ø từ chấm tới mặt cắt
    wt = 0.36*d; x_s = c[0] + r - wt/2                               # mép phải đuôi chạm đúng mép chấm
    # đuôi không vuốt nhọn (designer 04/11: "phần đuôi nhọn của các dấu , \" … nên cắt ngang phần nhọn 1 tí"): đuôi kéo quá
    # rồi CẮT NGANG ở −1.2 Ø, mặt cắt rộng ≈ 0.2 Ø.
    tail = hermite([((x_s, c[1]), (0, -1)), ((c[0] + 0.18*d, -0.55*d), (-0.45, -1)), ((c[0] - 0.40*d, -1.30*d), (-1, -0.9))])
    tl = stroke(tail, (1, 1), wabs=lambda u: wt)
    tl = I(tl, halfplane(-1.0*d))                                     # cắt thêm (designer 04/11: "cắt thêm xíu nữa cho đỡ nhọn")
    return U(dot(c, d), tl)
def wedge(xc, ytop, ybot, wt, wb, conc=0.18):
    """nét thon (chấm than, nháy): đỉnh cắt ngang rộng wt, chân rộng wb, hai cạnh lõm nhẹ như loe"""
    a, b = (xc - wt/2, ytop), (xc - wb/2, ybot); c, d = (xc + wb/2, ybot), (xc + wt/2, ytop)
    k = conc*(wt - wb)/2
    return P([('M', a), ('C', (a[0] + k, a[1] - (a[1]-b[1])*0.35), (b[0], b[1] + (a[1]-b[1])*0.3), b),
              ('C', (b[0], b[1] - wb*0.5), (c[0], c[1] - wb*0.5), c),          # chân tròn tiếp tuyến hai cạnh (G1, không gãy)
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
    # ? (designer 04/11: "điều chỉnh nét của dấu ? cho smooth hơn"): lấy PHẦN ĐẦU SỐ 2 của designer (vòng móc + đầu nét trái,
    # đồng bộ với bộ số), cắt ở y_cut nơi sống 2 bắt đầu đi chéo; nối thân cong liền xuống thẳng đứng; chấm cùng họ dấu chấm.
    two = letter(S, '2', w); y_cut = 400
    def span(y):
        sp = I(two, rect(-50, y - 0.05, 1000, y + 0.05)); xs = sorted(set(round(p_[0], 1) for _, ps in sp.segments for p_ in ps))
        return xs[0], xs[-1]
    a0_, a1_ = span(y_cut)
    c0 = ((a0_ + a1_)/2, y_cut)
    sx = c0[0] - (95 if not bold else 100); y_end = 250 + 0.1*d; we = 0.78*V
    # thân: hai mép là hai cung Hermite đi tiếp từ đúng hai mép sống 2 tại chỗ cắt (cùng điểm, cùng tiếp tuyến) xuống thẳng
    # đứng, rộng 0.78 V, cắt ngang. Mép nối G1 với sống 2 nên không còn bậc ở mép phải (bản trước lệch 4 u).
    e0, e1 = span(y_cut + 3); top2 = I(two, rect(-50, y_cut - 0.5, 1000, 800))
    lt, rt = (a0_ - e0, -3), (a1_ - e1, -3)
    Le = hermite([((a0_, y_cut), lt), ((sx - we/2, y_end), (0, -1))])[0]
    Re = hermite([((a1_, y_cut), rt), ((sx + we/2, y_end), (0, -1))])[0]
    qs = pathops.Path(); qs.moveTo(*Le[0]); qs.cubicTo(*Le[1], *Le[2], *Le[3]); qs.lineTo(*Re[3])
    qs.cubicTo(*Re[2], *Re[1], *Re[0]); qs.close()
    # hẹp ngang (designer 04/11: "dấu ? nên làm hẹp ngang lại bớt"): uốn mềm theo x trong dải tay trái Q_NARROW = (x0, x1, Δ):
    # x' = x + Δ·smoothstep((x1 − x)/(x1 − x0)) — đầu nét trái dời sang phải Δ, vòng phải, thân, chấm giữ nguyên.
    # Dải nằm ở tay trái đi lên (nét gần ngang, độ dày đo dọc) nên nét không mỏng đi.
    qx0, qx1, qd = Q_NARROW
    def qw(x, y):
        u = min(1, max(0, (qx1 - x)/(qx1 - qx0))); return (x + qd*u*u*(3 - 2*u), y)
    G['?'] = U(xform(U(top2, qs), qw), dot((sx, r - 3), d))
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
    # ngoặc tròn (designer 04/11: "( ) nên có glyph phổ biến của dòng serif"): lưỡi liềm từ hai elip đồng tâm —
    # dày nhất ở giữa tm = 0.85 V, thon dần về hai đầu mảnh te ≈ 0.55 H, cắt ngang ở −150 và 860 (tâm 355).
    tm, te = 0.85*V, 0.55*H; cy_, half = 355, 505
    Ao, Bo = 230 + (20 if bold else 0), 545          # Bo chỉ hơn nửa chiều cao 8 %: hai đầu cong vào rõ như ngoặc serif
    ko = Ao*math.sqrt(1 - (half/Bo)**2); ki = ko - te                      # bề lệch ngang của mép ngoài / trong ở hai đầu
    Ai = Ao - tm; Bi = half/math.sqrt(1 - (ki/Ai)**2)
    Co = Ao
    cres = D(ellipse((Co, cy_), Ao, Bo), ellipse((Co, cy_), Ai, Bi))
    par = I(cres, rect(-10, cy_ - half, Co, cy_ + half))
    par = move(par, -bounds(par)[0], 0); G['('] = par
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
    # ×: hai thanh 0.6 V xoay ±45° quanh tâm (200, 330), dài 430; đầu thanh cắt VUÔNG GÓC với nét
    # (designer 04/11: "glyph này các góc cắt hơi kỳ" — bản cũ bị cắt bởi khung vuông nên đầu nét lệch góc).
    def bar(a_deg, L=430, wb=0.6*V, c_=(200, yc)):
        a_ = math.radians(a_deg); ux, uy = math.cos(a_)*L/2, math.sin(a_)*L/2; px_, py_ = -math.sin(a_)*wb/2, math.cos(a_)*wb/2
        return poly([(c_[0] - ux - px_, c_[1] - uy - py_), (c_[0] + ux - px_, c_[1] + uy - py_), (c_[0] + ux + px_, c_[1] + uy + py_), (c_[0] - ux + px_, c_[1] - uy + py_)])
    G['×'] = U(bar(45), bar(-45))
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
    # & (designer 04/11: "ký tự & cũng lỗi"): dựng từ SỐ 8 của designer để đồng bộ nét và vòng:
    #   cắt bỏ góc trên-phải của bụng dưới (từ tâm bụng dưới lên tới eo) → vòng trên mở ở chân phải và chảy thành chân;
    #   chân là nét chéo dày D (như chân K, X), từ eo xuống chân phải, cắt ngang ở baseline, cắt trên ở eo.
    e8 = letter(S, '8', w); eb = bounds(e8)
    lc = (261, 210) if not bold else (275, 210)                 # tâm lòng dưới (đo từ bản vẽ 8)
    waist = 413 if not bold else 405
    # & serif cổ điển: chân dày (\\) cắt chéo qua TAY mảnh (/) — bụng dưới bị cắt ở góc −40° (dưới-phải), từ đó một nét
    # mảnh t đi lên-phải (đúng logic bút: nét / mảnh, nét \\ dày) tới đầu tay ở 0.52 cap bên phải; phần trên-phải còn lại
    # của bụng dưới cắt bỏ để vòng trên chảy thành chân.
    ang = math.radians(-40); far = 600
    cut = poly([(lc[0], lc[1]), (lc[0] + far*math.cos(ang), lc[1] + far*math.sin(ang)), (eb[2] + 300, -100), (eb[2] + 300, waist - 8), (lc[0] + 40, waist - 8)])
    amp = D(e8, cut)
    # điểm giữa nét bụng ở một góc: trung điểm hai giao điểm của tia với mép trong / mép ngoài
    def mid_at(a_):
        ray = poly([(lc[0], lc[1] - 0.5), (lc[0] + far*math.cos(a_), lc[1] + far*math.sin(a_) - 0.5), (lc[0] + far*math.cos(a_), lc[1] + far*math.sin(a_) + 0.5), (lc[0], lc[1] + 0.5)])
        hb = bounds(I(e8, ray)); pa = (hb[0], hb[3]) if math.sin(a_) < 0 else (hb[0], hb[1]); pb = (hb[2], hb[1]) if math.sin(a_) < 0 else (hb[2], hb[3])
        return ((pa[0] + pb[0])/2, (pa[1] + pb[1])/2), math.dist(pa, pb)
    a0 = ang - math.radians(22)
    m0, _ = mid_at(a0); mid, t0 = mid_at(ang)
    tg0 = (m0[0] - lc[0], m0[1] - lc[1]); tg0 = (-tg0[1], tg0[0])        # tiếp tuyến bụng (ngược chiều kim đồng hồ)
    tg = (mid[0] - lc[0], mid[1] - lc[1]); tg = (-tg[1], tg[0])
    tt = t['t']; tip = (eb[2] + (115 if not bold else 135), 0.52*CAP)
    # tay đi trùng nét bụng từ góc −62° tới góc cắt −40° (che mặt cắt, mối nối liền), rồi thon dần về t
    va = (1/math.hypot(1, 1.15), 1.15/math.hypot(1, 1.15)); pre = (tip[0] - 90*va[0], tip[1] - 90*va[1])
    over = (tip[0] + 80*va[0], tip[1] + 80*va[1])
    arm_c = hermite([(m0, tg0), (mid, tg), (pre, va)]) + [line(pre, over)]  # đoạn cuối thẳng, vượt quá đỉnh rồi cắt ngang
    arm = stroke(arm_c, (1, 1), wabs=lambda u: t0*(0.8 + 0.2*u/0.5) if u < 0.5 else tt + (t0 - tt)*max(0, 1 - (u - 0.5)/0.3)**2)   # gốc hẹp hơn nét bụng: nắp đầu nằm trọn trong bụng
    arm = I(arm, rect(-100, -300, 3000, tip[1]))                     # đầu tay cắt NGANG ở 0.52 cap, như đầu tay K ở cap
    amp = U(amp, arm)
    Dd = 100 if not bold else 146
    top, foot = ((lc[0] + 55, waist), (eb[2] + 70, 0)) if not bold else ((lc[0] + 60, waist), (eb[2] + 85, 0))
    L = math.dist(top, foot); nx, ny = (foot[1] - top[1])/L, -(foot[0] - top[0])/L
    ext = lambda p, k: (p[0] + (foot[0] - top[0])/L*k, p[1] + (foot[1] - top[1])/L*k)
    a, b = ext(top, -120), ext(foot, 160)
    leg = poly([(a[0] - nx*Dd/2, a[1] - ny*Dd/2), (b[0] - nx*Dd/2, b[1] - ny*Dd/2), (b[0] + nx*Dd/2, b[1] + ny*Dd/2), (a[0] + nx*Dd/2, a[1] + ny*Dd/2)])
    # đỉnh chân: kéo lên quá eo rồi cắt theo mép ngoài số 8 (không để góc chân thò ra ngoài vòng)
    filled = pathops.Path(); first = True
    for v, ps in e8.segments:
        if v == 'moveTo' and not first: break
        first = False
        if v == 'moveTo': filled.moveTo(*ps[0])
        elif v == 'lineTo': filled.lineTo(*ps[0])
        elif v == 'curveTo': filled.cubicTo(*ps[0], *ps[1], *ps[2])
        elif v == 'closePath': filled.close()
    leg = I(leg, U(filled, rect(-100, 0, 3000, waist - 90)))
    leg = I(leg, rect(-100, 0, 3000, waist + 40))
    cs = []; cur = None                                           # lòng trên của số 8 (contour có tâm cao nhất)
    for v, ps in e8.segments:
        if v == 'moveTo': cur = pathops.Path(); cur.moveTo(*ps[0])
        elif v == 'lineTo': cur.lineTo(*ps[0])
        elif v == 'curveTo': cur.cubicTo(*ps[0], *ps[1], *ps[2])
        elif v == 'closePath': cur.close(); cs.append(cur)
    upc = max(cs[1:], key=lambda c: bounds(c)[1])
    leg = D(leg, pathops.op(upc, upc, pathops.PathOp.UNION))     # chân không lấn vào lòng trên
    # loe (luật S5, như chân K/X và đầu chéo của chữ; designer 04/11: "& thiếu module loe như glyph chữ"):
    #   chân: hai góc ở baseline; đầu tay: hai góc trên mặt cắt vuông góc
    ud = ((top[0] - foot[0])/L, (top[1] - foot[1])/L)
    xl = min(foot[0] - nx*Dd/2 - ud[0]/ud[1]*(foot[1] - ny*Dd/2), foot[0] + nx*Dd/2 - ud[0]/ud[1]*(foot[1] + ny*Dd/2))
    xr = max(foot[0] - nx*Dd/2 - ud[0]/ud[1]*(foot[1] - ny*Dd/2), foot[0] + nx*Dd/2 - ud[0]/ud[1]*(foot[1] + ny*Dd/2))
    nl = (-ud[1], ud[0]) if -ud[1] < 0 else (ud[1], -ud[0])          # pháp tuyến mép trái, hướng ra ngoài (sang trái)
    fl = [flare((xl, 0), ud, nl, (-1, 0)), flare((xr, 0), ud, (-nl[0], -nl[1]), (1, 0))]
    v = va; pv = (-v[1], v[0])
    for sg in (1, -1):                                               # góc mép tay ∩ đường cắt ngang; loe chìa theo phương ngang
        e0 = (tip[0] + pv[0]*sg*tt/2, tip[1] + pv[1]*sg*tt/2); k_ = (tip[1] - e0[1])/v[1]
        Eg = (e0[0] + v[0]*k_, tip[1]); nout = (pv[0]*sg, pv[1]*sg)
        fl.append(flare(Eg, (-v[0], -v[1]), nout, (1 if nout[0] > 0 else -1, 0)))
    G['&'] = U(amp, leg, *fl)
    # @: vòng ngoài là nét bút gần trọn vòng; bên trong là "a" một tầng (lòng elip + thân)
    R0, cy = 335, 300; cx0 = R0 + 50
    # thân "a" đi xuống, vòng chữ U (bán kính ≈ 118) sang phải, nhập vào vòng ngoài ở góc 0° rồi chạy ngược chiều kim đồng hồ tới 300°
    ring_o = arc((cx0, cy), R0, R0, 0, 300)
    stem_c = hermite([((cx0 + 100, 470), (0, -1)), ((cx0 + 100, 300), (0, -1)), ((cx0 + 217, 166), (1, 0)), ((cx0 + R0, cy), (0, 1))])
    at = U(stroke(stem_c + ring_o, (t['N']*0.8, t['m']*0.85)), D(ellipse((cx0 - 12, cy + 10), 128, 160), ellipse((cx0 - 12 + 6, cy + 10), 128 - 0.62*V, 160 - 0.32*V, 25)))
    G['@'] = at
    return G

def to_d(p):
    out = []; p = _q2c(p)
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
