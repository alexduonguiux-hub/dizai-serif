#!/usr/bin/env python3
"""Chữ thường SUY RA từ module của designer (chưa có bản vẽ) — Regular + Bold. Nhãn TẠM, chờ designer duyệt / vẽ lại.
    python3 tools/construct/lower/derive.py   → lower/lower_derived.json (make_ref.py gộp vào ref_glyphs.json)

Module (đều là hình của designer, Figma 2115:421):
  VAI   = khối vai + thân + loe chân của a (Regular 2115:441; Bold = mẫu a Bold 2115:552) → n h m u r f t j
  LOE   = loe thân d (dài 69.6, chìa 22.6 u: cong từ mép nét, ngắt thẳng tới mũi trên mặt cắt) → mọi đầu thân / đầu chéo tự do
  VÒNG  = khối bụng d (o: lòng elip đứng đặt giữa) ; bụng e (c: hai nửa bụng e đối xứng)
  S     = S chữ hoa của designer thu về x-height, bù nét (s)
Nét (u):          Regular   Bold (theo mẫu a Bold)
  thân V          101.8     124.5
  chéo dày D      100       122      (= D chữ hoa × V thường Bold / V Regular)
  chéo mảnh t     44        56.7     (+12.7 như nét mảnh vòng Bold)
  ngang mảnh H    39.6      52.3     (thanh e)
"""
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'ref'))
import pathops
import lower as L
import vn_punct as V
from src_lower import SHAPES, S

XH, ASC, DESC = 495.0, 698.6, -200.8
W = {'Regular': dict(V=36*S, D=100.0, t=44.0, H=39.6, dot=118.0, wide=0.0),
     'Bold':    dict(V=44*S, D=122.0, t=56.7, H=52.3, dot=146.0, wide=22.0)}
# loe (px của thân d → u): tham số (v ra ngoài, u dọc mép về phía đầu nét)
FL = [(0, 0), (0, 6.961*S), (1.817*S, 13.802*S), (5.271*S, 19.846*S)]; FL_TIP = (8*S, 24.623*S)

def P(cmds): return V.P(cmds)
def N(p): return pathops.op(p, p, pathops.PathOp.UNION)      # chuẩn hoá chiều đường viền sau phép lật

# ---------- nét thẳng có loe ----------
def stroke(bc, tc, w, fl=''):
    """nét từ tâm đáy bc tới tâm đỉnh tc (đáy, đỉnh là mặt cắt NGANG), dày w đo vuông góc; fl ⊂ {tl,tr,bl,br}: góc có loe"""
    dx, dy = tc[0] - bc[0], tc[1] - bc[1]; Ln = math.hypot(dx, dy); d = (dx/Ln, dy/Ln)
    hw = w/2/abs(d[1])                                         # nửa bề ngang mặt cắt
    BL, BR, TL, TR = (bc[0] - hw, bc[1]), (bc[0] + hw, bc[1]), (tc[0] - hw, tc[1]), (tc[0] + hw, tc[1])
    def flare(corner, along, out, ycut):
        """đường loe đi TỚI góc: along = hướng dọc mép về phía đầu nét, out = hướng ra ngoài (vuông góc mép)"""
        lu = FL_TIP[1]; E0 = (corner[0] - along[0]*lu, corner[1] - along[1]*lu)
        pt = lambda v, u: (E0[0] + along[0]*u + out[0]*v, E0[1] + along[1]*u + out[1]*v)
        c1, c2, p3 = pt(*FL[1]), pt(*FL[2]), pt(*FL[3]); q = pt(*FL_TIP)
        k = (ycut - p3[1])/(q[1] - p3[1]) if abs(q[1] - p3[1]) > 1e-9 else 1     # mũi loe nằm đúng trên mặt cắt
        tip = (p3[0] + (q[0] - p3[0])*k, ycut)
        return E0, [('C', c1, c2, p3), ('L', tip)]
    nl = (-d[1], d[0])                                         # pháp tuyến bên trái (khi đi lên)
    up, dn = d, (-d[0], -d[1])
    cmds = []
    # đi: BL → (mép trái lên) → TL → TR → (mép phải xuống) → BR → BL
    if 'bl' in fl:
        E0, seg = flare(BL, dn, nl, bc[1]); tip = seg[-1][1]; c = seg[0]
        cmds += [('M', tip), ('L', c[3]), ('C', c[2], c[1], E0)]                 # đảo chiều đường loe
    else: cmds += [('M', BL)]
    if 'tl' in fl:
        E0, seg = flare(TL, up, nl, tc[1]); cmds += [('L', E0)] + seg
    else: cmds += [('L', TL)]
    if 'tr' in fl:
        E0, seg = flare(TR, up, (-nl[0], -nl[1]), tc[1]); tip = seg[-1][1]; c = seg[0]
        cmds += [('L', tip), ('L', c[3]), ('C', c[2], c[1], E0)]
    else: cmds += [('L', TR)]
    if 'br' in fl:
        E0, seg = flare(BR, dn, (-nl[0], -nl[1]), bc[1]); cmds += [('L', E0)] + seg
    else: cmds += [('L', BR)]
    cmds += [('Z',)]
    p = P(cmds); return pathops.op(p, p, pathops.PathOp.UNION)

def vstem(x0, x1, y0, y1, fl=''):
    # thu 0.001 u mỗi bên: mép trùng khít với thân của khối vai làm pathops gộp hỏng (mất cả thân)
    c = (x0 + x1)/2; return stroke((c, y0), (c, y1), x1 - x0 - 0.002, fl)
def side(p0, p1, left=True, big=4000):
    """nửa mặt phẳng bên trái (left) / phải của đường p0→p1"""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; Ln = math.hypot(dx, dy); d = (dx/Ln, dy/Ln); n = (-d[1], d[0]) if left else (d[1], -d[0])
    a = (p0[0] - d[0]*big, p0[1] - d[1]*big); b = (p0[0] + d[0]*big, p0[1] + d[1]*big)
    return V.poly([a, b, (b[0] + n[0]*big, b[1] + n[1]*big), (a[0] + n[0]*big, a[1] + n[1]*big)])
def dot(cx, w):
    r = W[w]['dot']/2; return V.ellipse((cx, XH + 70 + r), r, r)

# ---------- vai (khối a) ----------
def arch(w):
    """vai + thân + loe chân của a, đầu cắt trái ở x 0, chân ở y 0 (đỉnh vai 505.6 trước khi chốt vượt)"""
    k = 'a_stem' if w == 'Regular' else 'a_stem_B'; return L._path(SHAPES[k], (1, 0, 0, 0, 1, 188.25048828125))
def arch_stem(w):
    return (93*S, 129*S) if w == 'Regular' else (99*S, 143*S)

# vai n m h u (designer 05/11: "phần m, n, u, h không đẹp là do phần cong khuyết này bị phẳng"): vai a có mép ngoài bắt đầu
# cao (đầu cắt 12.75 → 57.25 px) nên chỗ vai mọc khỏi thân phẳng, không có khuyết. Dựng như tai r của designer (2127:982):
# đầu vai lùi vào trong thân N_OFF px, mép ngoài vai mọc từ đáy đầu vai theo đường cong của tai r (C 10.9 24.1 / 38.3 0,
# thu theo bề rộng vai) → khuyết cong rõ ở chỗ vai gặp đỉnh thân.
N_OFF = {'Regular': 12.0, 'Bold': 12.0}
# mép ngoài vai: bản a có tay nắm suy biến (cp2 trùng điểm cuối 129 59.75) → độ cong vọt ở chỗ vai chuyển sang thân phải, sau
# chốt đường vượt tay nắm còn lật ngược thành gợn (designer 05/11: "độ cong của các nét này không smooth"). Thay bằng tay nắm
# thật (κ 0.6, gần ellipse — song song lòng vai), tiếp tuyến ngang ở đỉnh, đứng ở thân.
D_N_ARCH = ("M60.5 0 C101.6 0 129 23.9 129 59.75 L129 154.127 C129 161.088 130.817 167.929 134.271 173.973 L137 178.75 "
            "L93 178.75 L93 58.25 C93 -19.7501 14.5005 24.2497 0 57.249 C9.35 36.5 33 0 60.5 0 Z")
D_N_ARCH_B = ("M63.5 0 C146.996 6.64214e-05 143 59.7435 143 59.75 L143 154.127 C143 161.088 144.817 167.929 148.271 173.973 L151 178.75 "
              "L99 178.75 L99 58.25 C98.9999 -9.75002 8.00126 38.2489 0 62.249 C9.8 39.5 34.6 0 63.5 0 Z")
def n_arch(w):
    """Bold (designer 05/11: "m n h u bold bị mất nét góc", "bold thường tăng độ rộng hơn nhiều so với regular"): dựng từ vai
    Regular — thân dày chia đều hai phía (mỗi mép ½ B_STEM, cả loe chân), lòng vai dày xuống B_BAR; góc nách giữ dáng Regular"""
    d = D_N_ARCH
    if w != 'Regular':
        h, dH = L.B_STEM/2/S, L.B_BAR/S
        def f(x, y):
            if x >= 128.99: x += h
            elif 84.9 <= x <= 93.01: x -= h
            if (x, y) in ((14.5005, 24.2497), (0.0, 57.249)) or abs(y + 19.7501) < 1e-3: y += dH
            return x, y
        d = L._map_pts(d, f)
    return L._path(d, (1, 0, 0, 0, 1, 188.25048828125))

# Vai n m h u dựng bằng HAI ELLIPSE như các chữ tròn (designer 05/11: "nên thử áp dụng cách dựng bằng 2 ellipse như các chữ
# tròn khác"; trước đó: "độ cong của các nét này không smooth", "đường cong không tự nhiên"):
# - ellipse NGOÀI: tâm ở cao độ ARCH_CY (chỗ thân phải bắt đầu thẳng), mép phải = mép ngoài thân phải, đỉnh = đường vượt 503.4,
#   đi qua điểm khuyết trên mép phải thân trái (ARCH_NOTCH) → khuyết cong ở chỗ vai mọc khỏi thân;
# - ellipse TRONG (lòng): cùng cao độ tâm, mép phải = mép trong thân phải, đỉnh thấp hơn đường vượt đúng nét vai trên (ARCH_TOP:
#   Regular 40.4 = nét mảnh, Bold + B_BAR), đi qua nách (ARCH_CROTCH) trên mép phải thân trái.
# Mỗi nửa trên là một cung ellipse liền (độ cong biến thiên đều); trục nhấn nghiêng tự sinh vì tâm lòng lệch trái tâm ngoài.
ARCH_CY = 340.8
ARCH_NOTCH = {'Regular': 448.4, 'Bold': 458.9}
# Nách: chỗ nối vai–thân dày bằng chỗ nối bụng–thân của b d p q (đo đứng sát mép thân: Regular 67.1, Bold 77.4).
# Trước đó (nách 420.8 / 418.2) chỗ nối chỉ 27.5 / 40.6, ≈ 40 % các chữ khác (designer 05/11: "chỗ nối m, n, u có bị bất
# đồng bộ độ dày với các glyph khác không?").
ARCH_JOIN = {'Regular': 67.1, 'Bold': 81.8}
ARCH_CROTCH = {w: ARCH_NOTCH[w] - ARCH_JOIN[w] for w in ARCH_NOTCH}
ARCH_TOP = {'Regular': 40.4, 'Bold': 40.4 + 12.7}

def _ell_through(xr, top, cy, px, py):
    """ellipse trục đứng/ngang: mép phải xr, đỉnh top, tâm ở cao độ cy, qua (px, py) bên trái tâm → (cx, rx, ry)"""
    ry = top - cy; r = math.sqrt(1 - ((py - cy)/ry)**2); rx = (xr - px)/(1 + r); return xr - rx, rx, ry

# Lòng vai là ellipse NGHIÊNG (như bụng d nghiêng 15°) — designer 05/11: "nét nối của u, m, n, h vẫn cảm giác bị mỏng hơn
# so với các glyph khác": lòng trục đứng làm nét vai mỏng nhanh khi rời thân (cách thân 20 u chỉ 45 so với b d p q 55).
# Trục lớn nghiêng ARCH_TILT so với phương ngang (Regular 72.2°, Bold 67.8°), giải sao cho: đỉnh lòng = đường vượt − ARCH_TOP,
# mép phải lòng = mép trong thân phải ở đúng cao độ ARCH_CY (lòng gặp thân phải tiếp tuyến), qua nách ARCH_CROTCH.
# Kết quả (đo đứng cách thân 1 / 8 / 20 / 40 u): Regular 66 / 62 / 56 / 49 (b d p q 67 / 62 / 55 / 49),
# Bold 81.5 / 79 / 74 / 66 (b d p q 82 / 77 / 72 / 68).
ARCH_TILT = {'Regular': 72.2, 'Bold': 67.8}

def _tilted_inner(w, xl, xi):
    from scipy.optimize import least_squares
    th = math.radians(ARCH_TILT[w]); c, s = math.cos(th), math.sin(th); T = L.OV_T - ARCH_TOP[w]; yc = ARCH_CROTCH[w]
    def yup(cx, cy, a, b, x):
        X = x - cx; A = s*s/a/a + c*c/b/b; B = 2*X*c*s*(1/a/a - 1/b/b); C = X*X*(c*c/a/a + s*s/b/b) - 1
        return cy + (-B + math.sqrt(max(B*B - 4*A*C, 0)))/(2*A)
    def F(q):
        cx, cy, a, b = q; rx = math.sqrt(a*a*c*c + b*b*s*s)
        return [cy + math.sqrt(a*a*s*s + b*b*c*c) - T, cx + rx - xi, yup(cx, cy, a, b, xl) - yc, cy + s*c*(a*a - b*b)/rx - ARCH_CY]
    cx, cy, a, b = least_squares(F, [xl + 80, 300, 170, 105], bounds=([-200, 0, 30, 30], [600, 460, 500, 500])).x
    return V.ellipse((cx, cy), a, b, ARCH_TILT[w])

def shoulder(w, xl, xi, xo, ext=0.5):
    """vai giữa thân trái (mép phải xl) và thân phải (xi … xo), từ cao độ ARCH_CY lên đường vượt.
    m vai sau (ext 60): ellipse ngoài kéo sang trái đè lên vai trước → hai cung ngoài cắt nhau thành nách nhọn trên thân giữa"""
    cy = ARCH_CY; top = L.OV_T
    co, ao, bo = _ell_through(xo, top, cy, xl, ARCH_NOTCH[w])
    outer = V.I(V.ellipse((co, cy), ao, bo), V.rect(xl - ext, cy, xo, top + 5))
    inner = V.I(_tilted_inner(w, xl, xi), V.rect(xl if ext > 1 else xl - 5, cy - 0.5, xi, top))
    return V.U(V.D(outer, inner), V.rect(xi, 290, xo, cy + 0.5))

def n_like(w, asc=False, arches=1):
    v = W[w]['V']; vr = W['Regular']['V']; h = (v - vr)/2; s0, s1 = arch_stem('Regular'); o = N_OFF[w]*S
    parts = [vstem(-h, vr + h, 0, ASC if asc else XH, 'tlblbr' + ('tr' if asc else ''))]       # thân Bold dày đều hai phía
    xl = vr + h
    for i in range(arches):
        dx = o + i*(s0 + o) + ((i + 1)*h/arches if arches > 1 else 0.0)   # m: rộng thêm ½ nét tăng của thân giữa, chia đều hai lòng
        xi, xo = dx + s0 - h, dx + s1 + h
        parts += [shoulder(w, xl, xi, xo, ext=60 if i else 0.5), vstem(xi, xo, 0, 300, 'blbr')]
        xl = xo
    return V.U(*parts)

def ear(w, dy=0.0):
    """vai a lật ngang: thân trùng thân chữ (x 0..v), vai đi sang phải, đầu cắt bên phải; chỉ phần trên (từ 300)"""
    s0, s1 = arch_stem(w); A = N(V.xform(arch(w), lambda x, y: (s1 - x, y)))
    return V.move(V.I(A, V.halfplane(300)), 0, dy)

def hook(w, right=True, ybot=-11.3):
    """vai a xoay 180° (right: đầu cắt bên phải, thân bên trái — t) hoặc lật dọc (đầu cắt trái, thân phải — j); phần dưới 300"""
    s0, s1 = arch_stem(w); top = 505.6
    if right: f = lambda x, y: (s1 - x, top + ybot - y)
    else: f = lambda x, y: (x - s0, top + ybot - y)
    return V.I(N(V.xform(arch(w), f)), V.halfplane(ybot + 300, above=False))

# ---------- móc / tai từ c (designer 05/11: "cập nhật lại các chữ thường còn lại theo c mới") ----------
# Vách trái c dày đúng bằng thân (36 px; Bold 44 px) nên nửa c ghép khít vào thân. Đầu cắt là đầu cắt c (nét mảnh cong,
# cắt đứng). Nửa c thu ngang C_KX phần BÊN PHẢI VÁCH (vách = thân giữ nguyên, không bậc ở chỗ thân gặp nửa c).
C_MID = (503.4 - 11.3)/2                                     # chia đôi c ở tâm lòng
C_KX = {'r': 0.60, 'f': 0.60, 't': 0.64, 'j': 0.64}   # móc trên (r f) 0.60, móc dưới (t j) 0.64 — designer 05/11: "móc trên chữ f và móc dưới chữ t hơi dài ra", "đồng bộ móc r và j theo f, t"
def c_half(w, top, kx):
    c = L.clean(L._q2c(L.raw('c', w)))
    wall = W[w]['V']                                         # vách c = thân: giữ nguyên, chỉ thu phần bên phải vách
    c = V.xform(c, lambda x, y: (x if x <= wall else wall + (x - wall)*kx, y))
    return V.I(c, V.halfplane(C_MID, above=top))

# ---------- chéo ----------
def vee(w, Wd, f=20.0, desc=False, fl_l='tltr', fl_r='tltr'):
    """v (desc: y): nét trái dày \\, nét phải mảnh /, đỉnh dưới cắt phẳng f; Wd = khoảng hai mép ngoài ở x-height"""
    D, t = W[w]['D'], W[w]['t']; cx = Wd/2
    Lo0, Lo1 = (cx - f/2, 0), (0, XH); Ro0, Ro1 = (cx + f/2, 0), (Wd, XH)
    def centre(o0, o1, wid, sgn):
        dx, dy = o1[0] - o0[0], o1[1] - o0[1]; Ln = math.hypot(dx, dy); hw = wid/2/(dy/Ln)
        return (o0[0] + sgn*hw, o0[1]), (o1[0] + sgn*hw, o1[1])
    lb, lt = centre(Lo0, Lo1, D, +1); rb, rt = centre(Ro0, Ro1, t, -1)
    if desc:                                                  # nét phải kéo tiếp xuống descender
        k = (DESC - rb[1])/(rt[1] - rb[1]); rb = (rb[0] + (rt[0] - rb[0])*k, DESC)
        Ro0 = (Ro0[0] + (Ro1[0] - Ro0[0])*k, DESC)
    Ls = stroke(lb, lt, D, fl_l); Rs = stroke(rb, rt, t, fl_r + ('blbr' if desc else ''))
    Ls = V.I(Ls, side(Ro0, Ro1, left=True))
    if desc:                                                  # nét dày dừng khi lọt hẳn vào nét mảnh
        # nét dày dừng ở cao độ mép ngoài của nó gặp mép trong nét mảnh (dưới đó nét dày lọt hẳn vào nét mảnh)
        sn = (Ro1[1] - Ro0[1])/math.hypot(Ro1[0] - Ro0[0], Ro1[1] - Ro0[1]); off = t/sn
        xl = lambda y: Lo0[0] + (Lo1[0] - Lo0[0])*(y - Lo0[1])/(Lo1[1] - Lo0[1])
        xr = lambda y: Ro0[0] - off + (Ro1[0] - Ro0[0])*(y - Ro0[1])/(Ro1[1] - Ro0[1])
        lo, hi = DESC, XH
        for _ in range(60):
            mid = (lo + hi)/2
            if xl(mid) > xr(mid): lo = mid
            else: hi = mid
        Ls = V.I(Ls, V.halfplane(hi))
    else:
        Rs = V.I(Rs, side(Lo0, Lo1, left=False))
    o = V.U(Ls, Rs)
    return V.I(o, V.halfplane(DESC if desc else 0))

def glyph(ch, w):
    v = W[w]['V']; D, t, H = W[w]['D'], W[w]['t'], W[w]['H']; wide = W[w]['wide']
    if ch == 'n': return n_like(w)
    if ch == 'h': return n_like(w, asc=True)
    if ch == 'm': return n_like(w, arches=2)
    if ch == 'u':
        n = n_like(w); return N(V.xform(n, lambda x, y: (-x, XH - y)))
    if ch == 'r': return V.U(vstem(0, v, 0, XH, 'tlblbr'), c_half(w, True, C_KX['r']))
    if ch == 'f': return L.raw('f', w)                       # khối r nâng lên ascender + thanh t (lower.py)
    if ch == 'j':                                            # móc t lật ngang + đỉnh thân t (lower.py) + chấm
        o = L.raw('j', w); return V.U(o, dot(o.bounds[2] - 8*S - v/2, w))
    h = (v - W['Regular']['V'])/2                           # thân Bold dày đều hai phía
    if ch == 'i': return V.U(vstem(-h, v - h, 0, XH, 'tltrblbr'), dot(v/2 - h, w))
    if ch == 'l': return vstem(-h, v - h, 0, ASC, 'tltrblbr')
    if ch == 'v': return shrink_caps('v', w)
    if ch == 'y': return y_from_V(w)
    if ch == 'w': return w_from_v(w)
    if ch == 'x': return shrink_caps('x', w)
    if ch == 'k': return k_from_K(w)
    if ch == 'z': return z_from_Z(w)
    if ch in 'oc': return L._q2c(oc(ch, w))
    if ch == 's': return s_from_S(w)
    raise KeyError(ch)

# ---------- o c (khối vòng) ----------
def oc(ch, w):
    if ch == 'o':
        m = (1, 0, 0, 0, 1, 189)
        outer = L._path(L._first_contour(SHAPES['bowl']), m); x0, y0, x1, y1 = outer.bounds
        cx, cy = (x0 + x1)/2, (y0 + y1)/2; rx, ry = 48*S, 74.5*S                 # lòng giữa: vách 34 px hai bên như d
        if w != 'Regular':
            c, k, st = L._stretch(outer.bounds); outer = V.xform(outer, st); rx, ry = rx*k*(1 - L.B_K), ry*(1 - L.B_K)
        return V.D(outer, V.ellipse((cx, cy), rx, ry))
    # c: bụng e (có đầu cắt) + bản lật dọc của nó làm nửa trên
    m = (1, 0, 0, 0, -1, 369)
    if w == 'Regular':
        bowl = L._path(SHAPES['e_bowl'], m)
    else:
        bo = L._path("M88.5 0 C114.943 0 138.677 11.6383 154.894 30.0879 L154.894 91 L0 91 L0 88.8076 C0 39.7607 39.6228 0 88.5 0 Z", m)
        c, k, st = L._stretch(bo.bounds)
        e2 = L._ell_from_pts([st(*q) for q in L._inner_pts(SHAPES['e_bowl'], m, lambda p: 32 < p[0] < 155 and 15 < p[1] < 91.5)])
        bowl = V.D(V.xform(bo, st), L._ell_path(*e2))
    seam = bowl.bounds[3]; ytop = 503.4; yb = bowl.bounds[1]
    top = V.xform(bowl, lambda x, y: (x, seam + (seam - y) - (2*seam - yb - ytop)))
    return V.U(bowl, top)

# ---------- s (từ S chữ hoa) ----------
# s (designer 05/11: "làm lại s theo c mới"): mỗi bụng là một c NHỎ dựng theo luật c — mép ngoài elip, lòng elip đứng,
# vách = thân, đỉnh mảnh = đỉnh c (16 px; Bold +12.7), đầu cắt đứng cách mép phải lòng 5 px như c (150 / 155 px).
# Bụng trên: nửa trên của c nhỏ (đầu cắt trên-phải); bụng dưới: bản xoay 180°. Sống: hai mép Hermite đi từ vách trái
# bụng trên (ở tâm bụng, tiếp tuyến đứng) xuống vách phải bụng dưới — nối G1, dày đúng bằng vách.
S_W, S_BH = 330.0, 300.0        # bề ngang s (Regular; Bold +11.3), chiều cao mỗi bụng (mép ngoài)
def s_from_c(w):
    wall = W[w]['V']; thin = 16*S + (0 if w == 'Regular' else L.B_BAR); Ws = S_W + (0 if w == 'Regular' else L.B_WIDE)
    top, bot = 503.4, -11.3; ry = S_BH/2; cy = top - ry
    # bụng là c tỉ lệ thật (rộng 2rx sao cho đầu cắt nằm ở Ws − 20), rồi thu phần BÊN PHẢI VÁCH về bề ngang Ws
    rx = (Ws - 20 + wall + 4.5*S)/2; cx = rx
    rxi, ryi = rx - wall + 0.5*S, ry - thin; cxi = cx + 0.5*S; cut = cxi + rxi - 5*S
    ring = V.D(V.ellipse((cx, cy), rx, ry), V.ellipse((cxi, cy), rxi, ryi))
    up = V.I(ring, V.rect(-50, cy - 0.5, cut, top + 50))                     # nửa trên, cắt đứng ở `cut`
    k = (Ws - 20 - wall)/(cut - wall)
    up = V.xform(up, lambda x, y: (x if x <= wall else wall + (x - wall)*k, y))
    ym = (top + bot)/2; rot = lambda p: (Ws - p[0], 2*ym - p[1])
    lo = N(V.xform(up, lambda x, y: rot((x, y))))
    O, I_ = (cx - rx, cy), (cxi - rxi, cy)                                   # mép ngoài / mép lòng vách trái ở tâm bụng
    Le = V.hermite([(O, (0, -1)), (rot(I_), (0, -1))])[0]; Re = V.hermite([(I_, (0, -1)), (rot(O), (0, -1))])[0]
    sp = V.P([('M', Le[0]), ('C', Le[1], Le[2], Le[3]), ('L', Re[3]), ('C', Re[2], Re[1], Re[0]), ('Z',)])
    return V.U(up, lo, N(sp))

S_SX = {'Regular': 0.85, 'Bold': 0.772}   # s = S hoa thu ngang, dọc về x-height (0.70). Bold thu hẹp hơn: S Bold vốn rộng
# hơn S Regular nhiều — s Bold chỉ rộng hơn s Regular ≈ 11 u như mọi vòng chữ thường (designer 05/11: "chữ s thường bold bề ngang hơi rộng")
S_D = {'Regular': 7.0, 'Bold': 7.0}   # Bold 7 (trước 4): sống s Bold = Regular + B_STEM (designer 05/11: "kiểm tra lại độ dày các chữ còn lại")
def s_from_S(w):
    """s là S hoa của designer thu nhỏ (designer 05/11: "chữ s thường phải giống chữ s hoa chứ?") — cùng dáng, cùng đầu
    nét; thu ngang S_SX, dọc về x-height, rồi bù nét S_D (nét viền góc vuông) để độ dày khớp chữ hoa."""
    from make_ref import outline
    src = {}
    for f in ('designer_A.json', 'designer_B.json', 'designer_M.json'): src.update(json.load(open(os.path.join(HERE, '..', 'ref', f))))
    Sp = outline(src[f'S-{w}'])
    x0, y0, x1, y1 = Sp.bounds; d = S_D[w]
    sy = (503.4 + 11.3 - 2*d)/(y1 - y0); sx = S_SX[w]
    p = V.xform(Sp, lambda x, y: ((x - x0)*sx, (y - y0)*sy - 11.3 + d))
    stp = pathops.Path(); stp.addPath(p); stp.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 8)   # miter 4 vát cụt mũi loe nhọn (designer 05/11: 'đỉnh loe không nhọn'); 40 kéo mũi thành kim
    stp.convertConicsToQuads()
    return L._q2c(V.U(p, L._q2c(stp)))

# v w x y k z: CHỮ HOA của designer thu nhỏ (designer 05/11: "chữ z cũng không đồng bộ style do thiếu module",
# "đồng bộ v w x y k theo chữ hoa") — giữ loe S5, đỉnh, mỏ của chữ hoa; thu ngang CAP_SX, dọc về x-height, bù nét
# CAP_D mỗi phía (nét viền góc vuông, góc giữ sắc) để nét mảnh ≈ 44 / chéo dày ≈ 100 (Bold theo mẫu a Bold).
CAP_SX = {'v': 0.55, 'w': 0.80, 'x': 0.565, 'z': 0.772, 'k': 0.785}
# V X hoa thu hẹp (ref/narrow_caps.py, designer 05/11): v x w thường GIỮ bề ngang Regular cũ (giải sx theo bề ngang đích)
W_TGT = {'v': 411.0, 'x': 423.0, 'w': 596.0}
# Làm dày nét \ (luật S10 — đồng bộ độ dày): V X hoa thu nhỏ chỉ còn nét \ ≈ 0.88 thân chữ thường → hai mép nét \ dời song
# song ra ngoài (mỗi bên ½ Δ, đo ngang), Δ giải để nét \ = thân (101.8 / Bold 124.5). Loe / vát ở đầu mép tịnh tiến theo mép
# nên cung module loe giữ nguyên bán kính như chữ hoa (designer 05/11: "chữ y, x, v lỗi module" — bản ngòi dẹt cộng Minkowski
# trước đó quét cả phần loe, cung module vỡ thành nhiều mảnh). Đỉnh nối mép với nét / tính lại bằng giao điểm. y dựng từ v.
# w giữ như cũ (designer 05/11: "giữ bề rộng chữ w như cũ").
THICK = ('v', 'w', 'x', 'z')   # w (QA độ dày 05/11: hai nét \\ của w mảnh hơn v 10 %)                                      # z: chéo / (designer 05/11: "kiểm tra lại module chữ k và z")
CAP_D = {'Regular': 6.0, 'Bold': 3.0}
def runs_at(p, y):
    """các đoạn mực (x0, x1) trên đường ngang y: mỗi mảnh giao với dải 0.1 u là một đoạn"""
    x0, _, x1, _ = p.bounds; r = V.I(p, V.rect(x0 - 10, y - 0.05, x1 + 10, y + 0.05))
    return sorted((c.bounds[0], c.bounds[2]) for c in r.contours)
def _caps(ch, w):
    ref = json.load(open(os.path.join(HERE, '..', 'ref_glyphs.json')))
    return N(V.P([(c[0], *[tuple(p) for p in c[1:]]) if c[0] != 'Z' else ('Z',) for c in ref[f'{ch.upper()}-{w}']['cmds']]))
def _embolden(p, d):
    stp = pathops.Path(); stp.addPath(p); stp.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 8)   # miter 4 vát cụt mũi loe nhọn (designer 05/11: 'đỉnh loe không nhọn'); 40 kéo mũi thành kim
    stp.convertConicsToQuads(); return L._q2c(V.U(p, L._q2c(stp)))
def _contours(p):
    out = []; cur = None
    for v, ps in p.segments:
        if v == 'moveTo': cur = {'start': tuple(ps[0]), 'segs': []}
        elif v == 'closePath':
            last = cur['segs'][-1][1][-1] if cur['segs'] else cur['start']
            if math.hypot(last[0] - cur['start'][0], last[1] - cur['start'][1]) > 1e-6: cur['segs'].append(('L', [cur['start']]))
            out.append(cur)
        else: cur['segs'].append(('L' if v == 'lineTo' else 'C', [tuple(q) for q in ps]))
    return out

def thicken(p, delta, ylo=90.0, yhi=400.0, fs=False):
    """nét \\ dày thêm delta (đo ngang): hai mép dời song song ra ngoài mỗi bên delta/2; điểm loe / vát ở đầu mép (y < ylo hoặc
    > yhi, gần mép hơn mọi nét khác) tịnh tiến theo mép; đỉnh nối mép với nét khác = giao điểm mép mới với nét đó"""
    CS = _contours(p); lines = []
    for c in CS:
        a = c['start']
        for t, ps in c['segs']:
            b = ps[-1]
            if t == 'L' and math.hypot(b[0] - a[0], b[1] - a[1]) > 60: lines.append((a, b, ((b[0] - a[0])*(b[1] - a[1]) > 0) if fs else ((b[0] - a[0])*(b[1] - a[1]) < 0)))
            a = b
    xat = lambda l, y: l[0][0] + (y - l[0][1])*(l[1][0] - l[0][0])/(l[1][1] - l[0][1])
    oth = [l for l in lines if not l[2] and abs(l[1][1] - l[0][1]) > 1]; E = []
    for l in sorted([l for l in lines if l[2]], key=lambda l: xat(l, 250)):
        if E and abs(xat(l, 250) - xat(E[-1][0], 250)) < 3: E[-1].append(l)
        else: E.append([l])
    assert len(E) in (2, 4), len(E)                          # v x z k: một nét \ (2 mép); w: hai nét \ (4 mép)
    SH = tuple(-delta/2 if k % 2 == 0 else delta/2 for k in range(len(E)))
    def dist(pt, l):
        (a, b, _) = l; dx, dy = b[0] - a[0], b[1] - a[1]; return abs((pt[0] - a[0])*dy - (pt[1] - a[1])*dx)/math.hypot(dx, dy)
    def onseg(pt, l): return dist(pt, l) < 0.6 and min(l[0][1], l[1][1]) - 0.6 <= pt[1] <= max(l[0][1], l[1][1]) + 0.6
    def tag(pt):
        for k, e in enumerate(E):
            if any(onseg(pt, l) for l in e): return k, 'edge'
        if pt[1] < ylo or pt[1] > yhi:
            dmin, k = min([(min(dist(pt, l) for l in e), k) for k, e in enumerate(E)] + [(dist(pt, l), -1) for l in oth])
            if k >= 0 and dmin < 45: return k, 'flare'
        return None, None
    def inter(k, a, b):
        l = E[k][0]; q = (l[0][0] + SH[k], l[0][1]); d = (l[1][0] - l[0][0], l[1][1] - l[0][1]); ex, ey = b[0] - a[0], b[1] - a[1]
        t = ((a[0] - q[0])*ey - (a[1] - q[1])*ex)/(d[0]*ey - d[1]*ex); return (q[0] + t*d[0], q[1] + t*d[1])
    out = []
    for c in CS:
        segs = c['segs']; n = len(segs); A = [c['start']] + [ps[-1] for t, ps in segs]
        def newA(i):
            pt = A[i]; k, kind = tag(pt)
            if k is None: return pt
            if kind == 'edge' and ylo <= pt[1] <= yhi:
                for j, other in ((i - 1, A[i - 1] if i > 0 else A[n - 1]), (i, A[i + 1] if i < n else A[1])):
                    if segs[j % n][0] == 'L' and tag(other)[0] != k and math.hypot(other[0] - pt[0], other[1] - pt[1]) > 40:
                        l = E[k][0]; ang = abs(math.degrees(math.atan2(other[1] - pt[1], other[0] - pt[0])
                                                      - math.atan2(l[1][1] - l[0][1], l[1][0] - l[0][0]))) % 180
                        if min(ang, 180 - ang) < 8: continue        # S24: mảnh mép gần thẳng hàng (lệch ~1 u, X Medium sau S21)
                        return inter(k, other, pt)
            return (pt[0] + SH[k], pt[1])
        NA = [newA(i) for i in range(n + 1)]; NA[n] = NA[0]; cmds = [('M', NA[0])]
        for i, (t, ps) in enumerate(segs):
            if t == 'L': cmds.append(('L', NA[i + 1]))
            else:
                d1, d2 = NA[i][0] - A[i][0], NA[i + 1][0] - A[i + 1][0]
                cmds.append(('C', (ps[0][0] + d1, ps[0][1]), (ps[1][0] + d2, ps[1][1]), NA[i + 1]))
        out.append(V.P(cmds + [('Z',)]))
    return V.U(*out)

def _thick_of(p, y1=XH*0.78, y2=XH*0.70, i=0):
    """độ dày nét chéo đậm (vuông góc), run thứ i ở hai cao độ (mặc định 0.78 / 0.70 x-height: trên chỗ hai nét x giao)"""
    (a1, b1), (a2, b2) = runs_at(p, y1)[i], runs_at(p, y2)[i]
    th = math.atan2(y1 - y2, ((a1 + b1) - (a2 + b2))/2); return (b1 - a1)*abs(math.sin(th))

THIN_ON = [True]
def _off(f):
    """chạy f với S10b tắt (bản trước khi làm dày nét mảnh) — làm chuẩn khoảng trắng lòng"""
    THIN_ON[0] = False
    try: return f()
    finally: THIN_ON[0] = True
def counter(p, y=XH*0.75, i=0):
    """khoảng trắng lòng: khe giữa run i và run i+1 ở cao độ y"""
    r = runs_at(p, y); return r[i + 1][0] - r[i][1]
def _cnt(p):
    """counter, lòng bít (một run) → 0"""
    r = runs_at(p, XH*0.75); return r[1][0] - r[0][1] if len(r) > 1 else 0.0
def _solve(f, g0, a, b):
    """secant: tìm sx để counter(f(sx)) = g0. S24: secant đi lệch (counter không đơn điệu quanh a vì S10b làm dày nét mảnh
    theo bước — x Bold sau S21 nhảy về 0.46, lòng bít) → chia đôi trong khoảng kẹp tìm bằng bước × 1.04 từ a"""
    a0 = a; ea, eb = _cnt(f(a)), _cnt(f(b))
    for _ in range(5):
        if abs(eb - ea) < 1e-6 or abs(eb - g0) < 0.05: break
        c = b + (g0 - eb)*(b - a)/(eb - ea)
        if not 0.8*a0 < c < 2*a0: break
        a, ea, b, eb = b, eb, c, _cnt(f(c))
    if abs(eb - g0) < 0.5 and 0.8*a0 < b < 2*a0: return b
    lo = a0; hi = a0
    while _cnt(f(hi)) < g0 and hi < 2*a0: lo, hi = hi, hi*1.04
    for _ in range(18):
        m = (lo + hi)/2
        if _cnt(f(m)) < g0: lo = m
        else: hi = m
    return hi

# S10c (designer 06/11 "bản regular đã hẹp sẵn rồi"): bề ngang mực v x w so với n theo TRUNG VỊ font serif tham chiếu
# (ref_kern.REFS: Liberation, DejaVu, Caladea, FreeSerif — cùng bộ dùng cho kerning). Dizai Regular trước: v/n 0.94, x 0.96,
# w 1.38 (tham chiếu 0.985 / 0.971 / 1.46). Bề ngang = max(tham chiếu × n, bản giữ khoảng trắng lòng) → Bold không hẹp lại.
WIDEN = 1.10
VN_REF = {'Regular': {'v': 0.9855, 'x': 0.971, 'w': 1.4605}, 'Bold': {'v': 0.944, 'x': 0.9125, 'w': 1.358}}
def _n_ink(w):
    ref = json.load(open(os.path.join(HERE, '..', 'ref_glyphs.json')))
    xs = [p[0] for c in ref[f'n-{w}']['cmds'] if c[0] != 'Z' for p in c[1:]]
    return max(xs) - min(xs)
def _widen(f, ch, w, sx):
    from weights import TW as _TW
    ink = lambda k: (lambda q: q.bounds[2] - q.bounds[0])(f(k))
    # designer 06/11 "hẹp ý tôi là hẹp kích thước", "tăng thêm cỡ 10% bề ngang": bề ngang mực = WIDEN × bản trước hôm nay
    # (Regular v 411 · x 423 · w 596; Bold theo luật cũ R + ½ B_STEM) — tham chiếu VN_REF giữ để đối chiếu (Regular +7 / +2 / +9 %)
    old_ = _off(lambda: shrink_caps(ch, w) if ch != 'w' else w_from_v(w))
    tgt = WIDEN*(old_.bounds[2] - old_.bounds[0])
    if w != 'Regular':                                       # đơn điệu: đậm hơn ≥ Regular + ½ phần thân tăng × số nét dày
        R = shrink_caps(ch, 'Regular') if ch != 'w' else w_from_v('Regular')
        tgt = max(tgt, R.bounds[2] - R.bounds[0] + (W[w]['V'] - W['Regular']['V'])/2*(2 if ch == 'w' else 1))
    if ink(sx) >= tgt - 0.5: return sx
    a0 = sx; a, b = sx, sx*1.06; ea, eb = ink(a), ink(b)
    for _ in range(5):
        if abs(eb - ea) < 1e-6 or abs(eb - tgt) < 0.3: break
        c = b + (tgt - eb)*(b - a)/(eb - ea)
        if not a0 <= c < 1.6*a0: break
        a, ea, b, eb = b, eb, c, ink(c)
    ok = lambda k: f(k).bounds[1] > -5                       # S24: outline hỏng (thicken lật) → bỏ
    if abs(eb - tgt) < 0.5 and a0 <= b < 1.6*a0 and ok(b): return b
    lo, hi = a0, a0                                          # S24: secant đi lệch (x Medium sau S21) → chia đôi
    while (ink(hi) < tgt or not ok(hi)) and hi < 1.6*a0: lo, hi = hi, hi*1.03
    for _ in range(16):
        m = (lo + hi)/2
        if ink(m) < tgt or not ok(m): lo = m
        else: hi = m
    return hi

def shrink_caps(ch, w, top=XH, sx=None, delta=None):
    """chữ hoa thu về x-height; v x: nét \\ dày bằng thân (thicken); Bold: giải sx để bề ngang = Regular + ½ B_STEM"""
    if sx is None and ch in ('v', 'x') and THIN_ON[0]:
        # S10b làm dày nét mảnh: GIỮ KHOẢNG TRẮNG LÒNG của bản trước S10b (designer 05/11 "các chữ y, x, w, v thường giờ thì lại
        # hẹp quá" — giữ bề ngang mực làm cả chữ co lại) → chữ rộng thêm đúng phần nét mảnh dày lên
        g0 = counter(_off(lambda: shrink_caps(ch, w, top)))
        sx = _solve(lambda k: shrink_caps(ch, w, top, k), g0, CAP_SX[ch], CAP_SX[ch]*1.05)
        sx = _widen(lambda k: shrink_caps(ch, w, top, k), ch, w, sx)
        return shrink_caps(ch, w, top, sx, delta)
    if w == 'Regular' and sx is None and ch in W_TGT and ch != 'w':
        def wd(k): p = shrink_caps(ch, w, top, k); return p.bounds[2] - p.bounds[0]
        a, b = CAP_SX[ch], CAP_SX[ch]*1.05; ea, eb = wd(a), wd(b)
        for _ in range(4):
            if abs(eb - ea) < 1e-6 or abs(eb - W_TGT[ch]) < 0.05: break
            c = b + (W_TGT[ch] - eb)*(b - a)/(eb - ea); a, ea, b, eb = b, eb, c, wd(c)
        return shrink_caps(ch, w, top, b, delta)
    if w != 'Regular' and sx is None and ch in THICK:
        R = shrink_caps(ch, 'Regular', top); tgt = R.bounds[2] - R.bounds[0] + L.B_STEM/2
        def wd(k): p = shrink_caps(ch, w, top, k); return p.bounds[2] - p.bounds[0]
        a, b = CAP_SX[ch], CAP_SX[ch]*1.05; ea, eb = wd(a), wd(b)
        for _ in range(3): c = b + (tgt - eb)*(b - a)/(eb - ea); a, ea, b, eb = b, eb, c, wd(c)
        sx = b
    P_ = _caps(ch, w); x0, y0, x1, y1 = P_.bounds; d = CAP_D[w]; sx = sx or CAP_SX[ch]; sy = (top - 2*d)/(y1 - y0)
    p = V.xform(P_, lambda x, y: ((x - x0)*sx, (y - y0)*sy + d))
    if ch in THICK:
        if delta is None:                                    # nét \\ tăng tuyến tính theo Δ → hai lần đo
            fs = ch == 'z'; m = (lambda q: _thick_of(q, XH*0.6, XH*0.4)) if fs else _thick_of
            t0 = m(_embolden(p, d)); t1 = m(_embolden(thicken(p, 40.0, fs=fs), d))
            delta = 40.0*(W[w]['V'] - t0)/(t1 - t0)
        p = thicken(p, delta, fs=(ch == 'z'))
        if ch in ('v', 'x') and THIN_ON[0]:                  # S10b: nét mảnh / theo tỉ lệ mảnh / thân của V hoa
            mt = lambda q: _thick_of(q, XH*0.80, XH*0.70, -1)
            u0 = mt(_embolden(p, d)); u1 = mt(_embolden(thicken(p, 30.0, fs=True), d))
            dl = 30.0*(thin_target(w) - u0)/(u1 - u0) if abs(u1 - u0) > 1e-3 else (thin_target(w) - u0)*1.25
            if dl > 0.2: p = thicken(p, dl, fs=True)
    p = _embolden(p, d)
    return V.move(p, -p.bounds[0], 0)

_TR = {}
def thin_target(w):
    """S10b (designer 05/11 "độ dày các đường xéo x y v w k thường có bị mỏng so với cân bằng chung không"): nét chéo mảnh
    của chữ thường = thân chữ thường × (nét mảnh / thân) của V hoa cùng weight — V thu nhỏ bằng nén ngang 0.55 làm nét / còn
    0.35–0.40 thân (V hoa 0.43 Regular, 0.50 Bold); Bold mỏng hơn hệ chung tới 20 %"""
    if w not in _TR:
        Vc = _caps('v', w); Hc = _caps('h', w)
        r = _thick_of(Vc, 700*0.72, 700*0.60, -1)/(lambda a: a[1] - a[0])(runs_at(Hc, 560)[0])   # thân H trên thanh
        _TR[w] = r*W[w]['V']
    return _TR[w]

W_SX = 0.47   # v dùng cho w: hẹp hơn v (0.55) → hai chữ v ghép lại rộng ≈ 1.45 v
def w_from_v(w, sx=None):
    if sx is None and THIN_ON[0]:                            # S10b: giữ khoảng trắng lòng trái của w như bản trước S10b
        g0 = counter(_off(lambda: w_from_v(w)))
        sx = _solve(lambda k: w_from_v(w, k), g0, W_SX, W_SX*1.05)
        return w_from_v(w, _widen(lambda k: w_from_v(w, k), 'w', w, sx))
    return _w_from_v(w, sx)

def _w_from_v(w, sx=None):
    """w (designer 05/11: "cân nhắc làm lại chữ w thường khác" — bản W hoa thu nhỏ có nét giữa bắt chéo, cụm mực đặc ở giữa):
    hai MODULE v ghép lại. v dựng như v (shrink_caps, nét \\ dày = thân) nhưng hẹp hơn (W_SX). Hai nét ngoài giữ loe của v;
    hai nét trong bỏ loe, kéo thẳng theo mép nét lên quá x-height; đỉnh giữa cắt phẳng ở x-height, rộng đúng đáy nhọn v.
    Bold: sx giải để w Bold rộng hơn Regular ½ B_STEM × 2 (hai nét dày)"""
    if w == 'Regular' and sx is None:
        a, b = W_SX, W_SX*1.05; ea, eb = w_from_v(w, a).bounds[2], w_from_v(w, b).bounds[2]
        for _ in range(4):
            if abs(eb - ea) < 1e-6 or abs(eb - W_TGT['w']) < 0.05: break
            c = b + (W_TGT['w'] - eb)*(b - a)/(eb - ea); a, ea, b, eb = b, eb, c, w_from_v(w, c).bounds[2]
        sx = b
    if w != 'Regular' and sx is None:
        tgt = w_from_v('Regular').bounds[2] + L.B_STEM
        a, b = W_SX, W_SX*1.05; ea, eb = w_from_v(w, a).bounds[2], w_from_v(w, b).bounds[2]
        for _ in range(3): c = b + (tgt - eb)*(b - a)/(eb - ea); a, ea, b, eb = b, eb, c, w_from_v(w, c).bounds[2]
        sx = b
    sx = sx or W_SX
    p = shrink_caps('v', w, sx=sx)
    # v không có lòng: bỏ lỗ mảnh (v hẹp ở Regular để lại một khe hình tam giác trong nét / sau thicken + embolden)
    cs = list(p.contours); p = max(cs, key=lambda c: c.bounds[2] - c.bounds[0]); p = pathops.op(p, p, pathops.PathOp.UNION)
    lines = []
    for c in _contours(p):
        a = c['start']
        for t, ps in c['segs']:
            b = ps[-1]
            if t == 'L' and math.hypot(b[0] - a[0], b[1] - a[1]) > 100: lines.append((a, b))
            a = b
    xat = lambda l, y: l[0][0] + (y - l[0][1])*(l[1][0] - l[0][0])/(l[1][1] - l[0][1])
    bs = sorted([l for l in lines if (l[1][0] - l[0][0])*(l[1][1] - l[0][1]) < 0], key=lambda l: xat(l, 300))   # \\ : mép ngoài, mép trong
    fs = sorted([l for l in lines if (l[1][0] - l[0][0])*(l[1][1] - l[0][1]) > 0], key=lambda l: xat(l, 300))   # / : mép trong, mép ngoài
    eL, eR = bs[0], bs[-1]; tL, tR = fs[0], fs[-1]
    f = runs_at(p, 1)[0]; f = f[1] - f[0]                                  # đáy nhọn (cắt phẳng) của v
    top = [l for l in (eR, tL)]; xs = (xat(eR, XH) + xat(tL, XH))/2           # chỗ tách hai nửa ở đỉnh (giữa khe hai nét)
    def band(l0, l1, y0, y1): return V.poly([(xat(l0, y0), y0), (xat(l1, y0), y0), (xat(l1, y1), y1), (xat(l0, y1), y1)])
    lowp = V.I(p, V.rect(-1000, -1000, 3000, XH - 60))
    v1 = V.U(V.I(p, V.rect(-1000, -1000, xs, 2000)), lowp, band(tL, tR, XH - 80, XH + 60))      # nét / phải: bỏ loe
    v2 = V.U(V.I(p, V.rect(xs, -1000, 3000, 2000)), lowp, band(eL, eR, XH - 80, XH + 60))      # nét \\ trái: bỏ loe
    dx = f + xat(tL, XH) - xat(eR, XH)
    o = V.I(V.U(L._q2c(v1), V.move(L._q2c(v2), dx, 0)), V.rect(-1000, -1000, 3000, XH))
    return V.move(L._q2c(o), -o.bounds[0], 0)

def z_from_Z(w):
    """z: Z hoa thu nhỏ; chéo / dày bằng thân (thicken); Bold rộng hơn Regular ½ B_STEM (shrink_caps tự giải)"""
    return shrink_caps('z', w)

def k_from_K(w, sxk=None, kd=None):
    """k: thân K giữ nguyên chiều cao (= ascender 698.6 ≈ cap), tay + chân thu về x-height; Bold: thân về 124.5 (thân Bold thường),
    dày ra đều hai phía (mép trái lùi ½ B_STEM), phần chéo giữ đúng vươn ngang của Regular tính từ mép phải thân → k Bold rộng
    hơn Regular đúng B_STEM (như n)"""
    P_ = _caps('k', w); x0, y0, x1, y1 = P_.bounds
    s0, s1 = runs_at(P_, 600)[0]                             # mép thân ở 600 (trên chỗ tay nhập thân)
    v = W[w]['V']; kx = v/(s1 - s0)
    if w != 'Regular' and sxk is None:                          # giải sxk để vươn chéo (từ mép phải thân) = Regular
        R = k_from_K('Regular'); tgt = R.bounds[2] - runs_at(R, 600)[0][1]
        def ext(k): p = k_from_K(w, k); return p.bounds[2] - runs_at(p, 600)[0][1]
        a, b = 0.6, 0.9; ea, eb = ext(a), ext(b)
        for _ in range(4):                                   # secant
            c = b + (tgt - eb)*(b - a)/(eb - ea); a, ea, b, eb = b, eb, c, ext(c)
        sxk = b
    elif sxk is None: sxk = CAP_SX['k']
    h = (v - W['Regular']['V'])/2 if w != 'Regular' else 0.0
    FLR = 90                                                 # vùng loe phải của thân (đỉnh, chân) đi theo thân, không theo nét chéo
    stem = V.U(V.I(P_, V.rect(x0 - 50, -50, s1 + 0.5, 800)), V.I(P_, V.rect(s1 - 1, 700 - FLR, s1 + 40, 800)),
               V.I(P_, V.rect(s1 - 1, -50, s1 + 40, FLR)))
    stem = V.xform(stem, lambda x, y: (s0 - h + (x - s0)*kx, y*ASC/700))
    d = CAP_D[w]; sx = sxk; sy = (XH - 2*d)/(y1 - y0)
    diag = V.D(V.I(P_, V.rect(s1 + 0.5, -50, x1 + 50, 800)), V.U(V.rect(s1 - 1, 700 - FLR, s1 + 40, 800), V.rect(s1 - 1, -50, s1 + 40, FLR)))
    diag = V.xform(diag, lambda x, y: (s0 - h + v - 0.5 + (x - s1)*sx, y*sy + d))
    if kd is None:                                           # chân k (nét \\) dày bằng thân: dời song song hai mép (như v x)
        leg = lambda q: _thick_of(_embolden(q, d), 140, 100, -1)
        t0, t1 = leg(diag), leg(thicken(diag, 40.0)); kd = 40.0*(v - t0)/(t1 - t0)
    diag = thicken(diag, kd)
    # S10b: tay k (nét /) theo tỉ lệ mảnh / thân của V hoa
    arm = lambda q: _thick_of(_embolden(q, d), XH*0.86, XH*0.76, -1)
    u0, u1 = arm(diag), arm(thicken(diag, 30.0, fs=True))
    dl = 30.0*(thin_target(w) - u0)/(u1 - u0) if abs(u1 - u0) > 1e-3 else (thin_target(w) - u0)*1.25
    if dl > 0.2: diag = thicken(diag, dl, fs=True)
    diag = _embolden(diag, d)
    xr = s0 - h + v - 0.5                                    # tay / chân sau khi bù nét không lấn qua mép phải thân (bậc 6 u)
    k = V.U(stem, V.I(V.I(diag, V.halfplane(0)), V.rect(xr, -100, 2000, 2000)))
    # đầu tay k = đầu nét / của v (cùng module loe nét xiên Figma 2138:1189): mũi K gốc rất nhọn (~27°), thu về k thành nêm dài
    return graft_top(k, shrink_caps('v', w), XH, xr + 40, xr - 5)

# MODULE LOE ĐẦU NÉT (designer 05/11: "đỉnh loe không nhọn như các module khác", "lỗi" ở đầu nét chéo V v): loe thân H của
# designer (giống nhau Regular / Bold): (u chìa ngang ra ngoài, t cách đường cap/chân) — cubic (0, 69.8) (0, 50.1) (5.2, 30.7)
# (15.0, 13.5) rồi thẳng tới mũi (22.7, 0). Đầu nét chéo: HAI bên đều là loe này. Mép nét ngả 29 u trên 70 u cao (hơn độ chìa 22.7)
# → dời ngang theo mép vẫn ra "mũi tù" phía nét ngả vào (chính là mũi lồi của bản vẽ). Nên đặt theo MŨI: mũi chìa 22.7 ra ngoài
# điểm ngoài cùng của mép trong vùng loe, đoạn cuối gặp đường cap 60° như thân H, đường cong rời mép tiếp tuyến.
FLARE_LOG = []
FLARE = [(0.0, 69.8), (0.0, 50.1), (5.2, 30.7), (15.0, 13.5), (22.7, 0.0)]
def flare_ends(p, yend, top, xmin=-1e9, xmax=1e9, slope=None):
    """dựng lại loe hai bên mọi đầu nét chéo chạm đường yend (top: đầu trên; không: chân). slope: chỉ nét '/' (True) / '\\' (False)"""
    H = FLARE[0][1]; sgn = -1 if top else 1; ycut = yend + sgn*H
    segs = []
    for c in _contours(p):
        a = c['start']
        for t, ps in c['segs']:
            b = ps[-1]
            if t == 'L' and math.hypot(b[0] - a[0], b[1] - a[1]) > 40 and abs(b[0] - a[0]) > 5 and abs(b[1] - a[1]) > 5: segs.append((a, b))
            a = b
    xat = lambda l, y: l[0][0] + (y - l[0][1])*(l[1][0] - l[0][0])/(l[1][1] - l[0][1])
    yr = yend + sgn*110                                           # cao độ đo / ghép cặp mép: dưới vùng loe
    near = [l for l in segs if min(l[0][1], l[1][1]) - 1 <= yr <= max(l[0][1], l[1][1]) + 1 and xmin <= xat(l, yr) <= xmax]
    out = p
    for fs in (True, False):
        if slope is not None and fs != slope: continue
        ls = sorted([l for l in near if ((l[1][0] - l[0][0])*(l[1][1] - l[0][1]) > 0) == fs], key=lambda l: xat(l, yr))
        i = 0
        while i + 1 < len(ls):
            eL, eR = ls[i], ls[i + 1]
            sl = lambda l: (l[1][0] - l[0][0])/(l[1][1] - l[0][1])
            if abs(sl(eL) - sl(eR)) > 0.03 or not (20 < xat(eR, yr) - xat(eL, yr) < 260): i += 1; continue
            def pt(l, u, t, side): return (xat(l, yend + sgn*t) + side*u, yend + sgn*t)
            # cắt từ chỗ MÉP THẲNG của bản vẽ dừng (loe cũ bắt đầu từ đó), không từ đỉnh loe module: không sót bướu / gãy của loe cũ
            tend = lambda l: abs(yend - (max(l[0][1], l[1][1]) if top else min(l[0][1], l[1][1])))
            tc = max(H, tend(eL), tend(eR)) + 2; ycut_ = yend + sgn*tc
            def side_pts(l, side):
                # MODULE CỦA DESIGNER (Figma 2138:1189, 05/11 "tham khảo nét dựng module ở đây"): một cubic từ mép tới mũi,
                # đo theo MÉP NÉT kéo dài (u chìa ra ngoài, t cách đường cap / chân; đơn vị module cao 29):
                #   thân đứng   : mũi u 8;  điểm đ.khiển gần mũi (1.5, t 8);  gần mép (0, t 13.5)
                #   nét xiên 15°: phía góc tù  mũi 10.2, đ.khiển (1.45, t 6)
                #                 phía góc nhọn mũi 5.8,  đ.khiển (−2.9 — LẤN VÀO mép, t 8) → đoạn lồi nhỏ rồi mũi nhọn
                # → nội suy theo độ ngả λ = ngả / 0.268. Quy ra font: t × 69.8/29 (= cao loe thân H), u × 22.7/8 (= chìa loe H)
                kt, ku = 69.8/29, 22.7/8
                e = lambda t: xat(l, yend + sgn*t)
                lean = (e(1.0) - e(0.0))*(-1)                            # dời ngang của mép khi tiến tới đầu nét (mỗi 1 u)
                lam = abs(lean)/0.268
                acute = side*lean < 0                                   # mép chạy ra xa phía này khi tới đầu nét
                if acute: tip_u, p2_u, p2_t, p1_t = 8 - 2.23*lam, 1.5 - 4.37*lam, 8.0, 13.5 + 0.5*min(lam, 1.0)
                else:     tip_u, p2_u, p2_t, p1_t = 8 + 2.23*lam, 1.5 - 0.05*lam, 8.0 - 2.0*min(lam, 1.5), 13.5
                q = lambda u, t: (e(t*kt) + side*u*ku, yend + sgn*t*kt)
                return [q(0, 29), q(0, p1_t), q(p2_u, p2_t), q(tip_u, 0)]
            L0 = side_pts(eL, -1); R0 = side_pts(eR, +1)
            cmds = [('M', pt(eL, 0, tc + 3, -1)), ('L', L0[0]), ('C', L0[1], L0[2], L0[3]), ('L', R0[3]),
                    ('C', R0[2], R0[1], R0[0]), ('L', pt(eR, 0, tc + 3, 1)), ('Z',)]
            piece = V.P(cmds); piece = pathops.op(piece, piece, pathops.PathOp.UNION)
            ys = sorted((ycut_, yend - sgn*3))
            cut = V.poly([(xat(eL, ys[0]) - 120, ys[0]), (xat(eR, ys[0]) + 120, ys[0]), (xat(eR, ys[1]) + 120, ys[1]), (xat(eL, ys[1]) - 120, ys[1])])
            out = V.U(V.D(out, cut), piece); FLARE_LOG.append((round(xat(eL, yend)), round(xat(eR, yend)), yend))
            i += 2
    return L._q2c(out)

def graft_end(p, donor, yend, xmin, xline, top=True, slash=True):
    """thay ĐẦU / CHÂN một nét chéo của p bằng đầu / chân nét chéo cùng hướng của donor (nét cuối cùng bên phải ở đầu đó):
    loe nhọn như mọi module (designer 05/11: "đỉnh loe không nhọn như các module khác"; chân K Medium/SemiBold vát).
    Ánh xạ theo mép nét: ở mỗi cao độ, đoạn [mép trái, mép phải] của nét donor → đoạn tương ứng của nét đích (loe chìa ngoài
    hai mép co giãn theo bề dày nét). slash: nét / (tay k K); không: nét \\ (chân K)"""
    sg = (lambda a, b: (b[0] - a[0])*(b[1] - a[1]) > 0) if slash else (lambda a, b: (b[0] - a[0])*(b[1] - a[1]) < 0)
    def lines(q, x_lo):
        out = []
        for c in _contours(q):
            a = c['start']
            for t, ps in c['segs']:
                b = ps[-1]
                if t == 'L' and math.hypot(b[0] - a[0], b[1] - a[1]) > 60 and sg(a, b) and min(a[0], b[0]) > x_lo: out.append((a, b))
                a = b
        return out
    xat = lambda l, y: l[0][0] + (y - l[0][1])*(l[1][0] - l[0][0])/(l[1][1] - l[0][1])
    yr = yend - 1 if top else yend + 1
    rd = runs_at(donor, yr); dsplit = (rd[-2][1] + rd[-1][0])/2 if len(rd) > 1 else donor.bounds[0]
    near = (lambda l: max(l[0][1], l[1][1]) > yend - 150) if top else (lambda l: min(l[0][1], l[1][1]) < yend + 150)   # chỉ mép chạy tới vùng đầu / chân (A: bỏ mép trong trên thanh ngang)
    DL = [l for l in lines(donor, dsplit - 300) if near(l)]
    TL = [l for l in lines(p, xline) if near(l)]
    if top: ycut = min(max(l[0][1], l[1][1]) for l in DL + TL) - 4
    else: ycut = max(min(l[0][1], l[1][1]) for l in DL + TL) + 4
    span = lambda l: min(l[0][1], l[1][1]) - 6 <= ycut <= max(l[0][1], l[1][1]) + 6
    DL = [l for l in DL if span(l)]; TL = [l for l in TL if span(l)]
    DL.sort(key=lambda l: xat(l, ycut)); TL.sort(key=lambda l: xat(l, ycut))
    vL, vR, kL, kR = DL[-2], DL[-1], TL[-2], TL[-1]
    reg = (lambda x0: V.rect(x0, ycut, 5000, yend + 5)) if top else (lambda x0: V.rect(x0, yend - 5, 5000, ycut))
    seam = V.rect(dsplit, ycut - 2, 5000, yend + 5) if top else V.rect(dsplit, yend - 5, 5000, ycut + 2)
    piece = V.I(donor, seam)
    def f(x, y):
        a, b = xat(vL, y), xat(vR, y); u = (x - a)/(b - a); c, d = xat(kL, y), xat(kR, y); return (c + u*(d - c), y)
    return L._q2c(V.U(V.D(p, reg(xmin)), V.xform(L._q2c(piece), f)))

def graft_top(p, donor, ytop, xmin, xline=None):
    return graft_end(p, donor, ytop, xmin, xmin - 60 if xline is None else xline, top=True, slash=True)

def y_from_V(w):
    """y: v (V hoa thu nhỏ) + nét mảnh kéo xuống descender có loe chân; nét dày dừng khi lọt hẳn vào nét mảnh"""
    v = shrink_caps('v', w); x0, _, x1, _ = v.bounds
    def right_run(y): return runs_at(v, y)[-1]
    ya, yb = XH*0.80, XH*0.50; (la, ra), (lb, rb) = right_run(ya), right_run(yb)   # đo nơi hai nét còn tách (Bold nhập sớm)
    lx = lambda y: lb + (la - lb)*(y - yb)/(ya - yb); rx = lambda y: rb + (ra - rb)*(y - yb)/(ya - yb)
    # cao độ nét dày lọt hẳn vào nét mảnh: mép trái v (nét dày) gặp mép trái nét mảnh
    def left_edge(y): return runs_at(v, y)[0][0]
    lo, hi = 0.0, XH*0.5
    for _ in range(40):
        m = (lo + hi)/2
        if left_edge(m) < lx(m) - 0.5: hi = m                 # mép trái còn nằm ngoài nét mảnh: điểm dừng ở thấp hơn
        else: lo = m
    thick = V.I(v, V.halfplane(lo))
    thin = V.I(v, side((lx(0), 0), (lx(XH), XH), left=False))
    t = (rx(0) - lx(0))*abs(math.sin(math.atan2(XH, lx(XH) - lx(0))))
    cb = ((lx(DESC) + rx(DESC))/2, DESC); ct = ((lx(40) + rx(40))/2, 40)
    tail = stroke(cb, ct, t, 'blbr')
    return V.U(thick, thin, tail)

# ---------- 4 weight: bảng tham số nội suy (weights.lerp_w); "w != 'Regular'" = nhánh đậm, phần thêm vào nhân TW[w] qua L.set_weight
sys.path.insert(0, os.path.join(HERE, '..'))
from weights import WEIGHTS, lerp_w
for _d in (W, N_OFF, ARCH_NOTCH, ARCH_JOIN, ARCH_TOP, ARCH_TILT, S_SX, S_D, CAP_D): lerp_w(_d)
ARCH_CROTCH = {w: ARCH_NOTCH[w] - ARCH_JOIN[w] for w in ARCH_NOTCH}

CHARS = 'fhijklmnsuvwxyz'      # o, c, r, t: đã có bản vẽ designer (lower.py)
if __name__ == '__main__':
    out = {}
    for c in CHARS:
        for w in WEIGHTS:
            L.set_weight(w); o = L._q2c(glyph(c, w)); o = V.move(o, -o.bounds[0], 0)
            out[f'{c}-{w}'] = [V.to_d(L.clean(o))]
    json.dump(out, open(os.path.join(HERE, 'lower_derived.json'), 'w'))
    from make_ref import outline
    for k, v in out.items(): print(k, [round(x, 1) for x in outline(v).bounds])
