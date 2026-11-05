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
    if w == 'Bold':
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
ARCH_JOIN = {'Regular': 67.1, 'Bold': 77.4}
ARCH_CROTCH = {w: ARCH_NOTCH[w] - ARCH_JOIN[w] for w in ARCH_NOTCH}
ARCH_TOP = {'Regular': 40.4, 'Bold': 40.4 + 12.7}

def _ell_through(xr, top, cy, px, py):
    """ellipse trục đứng/ngang: mép phải xr, đỉnh top, tâm ở cao độ cy, qua (px, py) bên trái tâm → (cx, rx, ry)"""
    ry = top - cy; r = math.sqrt(1 - ((py - cy)/ry)**2); rx = (xr - px)/(1 + r); return xr - rx, rx, ry

def shoulder(w, xl, xi, xo, ext=0.5):
    """vai giữa thân trái (mép phải xl) và thân phải (xi … xo), từ cao độ ARCH_CY lên đường vượt.
    m vai sau (ext 60): ellipse ngoài kéo sang trái đè lên vai trước → hai cung ngoài cắt nhau thành nách nhọn trên thân giữa"""
    cy = ARCH_CY; top = L.OV_T if hasattr(L, 'OV_T') else 503.4
    co, ao, bo = _ell_through(xo, top, cy, xl, ARCH_NOTCH[w])
    ci, ai, bi = _ell_through(xi, top - ARCH_TOP[w], cy, xl, ARCH_CROTCH[w])
    outer = V.I(V.ellipse((co, cy), ao, bo), V.rect(xl - ext, cy, xo, top + 5))
    inner = V.I(V.ellipse((ci, cy), ai, bi), V.rect(xl if ext > 1 else xl - 5, cy - 1, xi, top))
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
    if ch == 'w': return shrink_caps('w', w)
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
        if w == 'Bold':
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

S_SX = {'Regular': 0.85, 'Bold': 0.786}   # s = S hoa thu ngang, dọc về x-height (0.70). Bold thu hẹp hơn: S Bold vốn rộng
# hơn S Regular nhiều — s Bold chỉ rộng hơn s Regular ≈ 11 u như mọi vòng chữ thường (designer 05/11: "chữ s thường bold bề ngang hơi rộng")
S_D = {'Regular': 7.0, 'Bold': 4.0}   # bù nét mỗi phía (góc vuông giữ sắc): mảnh ≈ H, vách/sống ≈ S hoa (Bold theo mẫu a Bold)
def s_from_S(w):
    """s là S hoa của designer thu nhỏ (designer 05/11: "chữ s thường phải giống chữ s hoa chứ?") — cùng dáng, cùng đầu
    nét; thu ngang S_SX, dọc về x-height, rồi bù nét S_D (nét viền góc vuông) để độ dày khớp chữ hoa."""
    from make_ref import outline
    src = {}
    for f in ('designer_A.json', 'designer_B.json'): src.update(json.load(open(os.path.join(HERE, '..', 'ref', f))))
    Sp = outline(src[f'S-{w}'])
    x0, y0, x1, y1 = Sp.bounds; d = S_D[w]
    sy = (503.4 + 11.3 - 2*d)/(y1 - y0); sx = S_SX[w]
    p = V.xform(Sp, lambda x, y: ((x - x0)*sx, (y - y0)*sy - 11.3 + d))
    stp = pathops.Path(); stp.addPath(p); stp.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    stp.convertConicsToQuads()
    return L._q2c(V.U(p, L._q2c(stp)))

# v w x y k z: CHỮ HOA của designer thu nhỏ (designer 05/11: "chữ z cũng không đồng bộ style do thiếu module",
# "đồng bộ v w x y k theo chữ hoa") — giữ loe S5, đỉnh, mỏ của chữ hoa; thu ngang CAP_SX, dọc về x-height, bù nét
# CAP_D mỗi phía (nét viền góc vuông, góc giữ sắc) để nét mảnh ≈ 44 / chéo dày ≈ 100 (Bold theo mẫu a Bold).
CAP_SX = {'v': 0.565, 'w': 0.80, 'x': 0.60, 'z': 0.80, 'k': 0.85}
# Ngòi dẹt (luật S10 — đồng bộ độ dày): V hoa thu nhỏ chỉ còn nét \ ≈ 0.88 thân thường, nét / ≈ 0.45 → cộng Minkowski với một
# đoạn thẳng dài NIB theo hướng nét / (nét / gần như không dày thêm, nét \ dày thêm ≈ NIB·sin góc giữa hai nét):
# v x: nét \ = thân (102 / 124.5), nét / ≈ 40–45 / 56; w: hai chữ V chồng ở giữa nên ngòi ngắn (giữ lòng giữa mở).
NIB = {'v': {'Regular': (47, 68), 'Bold': (41, 62)},
       'x': {'Regular': (32, 55), 'Bold': (36, 55)}}
CAP_D = {'Regular': 6.0, 'Bold': 3.0}
def runs_at(p, y):
    """các đoạn mực (x0, x1) trên đường ngang y: mỗi mảnh giao với dải 0.1 u là một đoạn"""
    x0, _, x1, _ = p.bounds; r = V.I(p, V.rect(x0 - 10, y - 0.05, x1 + 10, y + 0.05))
    return sorted((c.bounds[0], c.bounds[2]) for c in r.contours)
def _caps(ch, w):
    ref = json.load(open(os.path.join(HERE, '..', 'ref_glyphs.json')))
    return N(V.P([(c[0], *[tuple(p) for p in c[1:]]) if c[0] != 'Z' else ('Z',) for c in ref[f'{ch.upper()}-{w}']['cmds']]))
def _embolden(p, d):
    stp = pathops.Path(); stp.addPath(p); stp.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    stp.convertConicsToQuads(); return L._q2c(V.U(p, L._q2c(stp)))
def nib(p, Ln, ang):
    """cộng Minkowski với đoạn thẳng dài Ln theo góc ang (ngòi dẹt, tâm ở giữa): hợp hai bản dời ±½ đoạn + dải quét từng cạnh"""
    vx, vy = Ln*math.cos(math.radians(ang)), Ln*math.sin(math.radians(ang))
    a = V.move(p, -vx/2, -vy/2); parts = [a, V.move(p, vx/2, vy/2)]; cur = start = None
    for verb, pts in a.segments:
        if verb == 'moveTo': cur = start = pts[0]; continue
        if verb == 'closePath':
            if cur == start: continue
            verb, pts = 'lineTo', (start,)
        end = pts[-1]; q = pathops.Path(); q.moveTo(*cur)
        if verb == 'lineTo': q.lineTo(*end)
        else: q.cubicTo(*pts[0], *pts[1], *pts[2])
        q.lineTo(end[0] + vx, end[1] + vy)
        if verb == 'lineTo': q.lineTo(cur[0] + vx, cur[1] + vy)
        else: q.cubicTo(pts[1][0] + vx, pts[1][1] + vy, pts[0][0] + vx, pts[0][1] + vy, cur[0] + vx, cur[1] + vy)
        q.close(); q.simplify(fix_winding=True); parts.append(q); cur = end
    return L._q2c(V.I(L._q2c(V.U(*parts)), V.rect(-100, 0, 2000, XH)))

def shrink_caps(ch, w, top=XH, sx=None):
    """chữ hoa thu về x-height; v w x: + ngòi dẹt; Bold: giải sx để bề ngang = Regular + ½ B_STEM"""
    if w == 'Bold' and sx is None and ch in NIB:
        R = shrink_caps(ch, 'Regular', top); tgt = R.bounds[2] - R.bounds[0] + L.B_STEM/2
        def wd(k): p = shrink_caps(ch, w, top, k); return p.bounds[2] - p.bounds[0]
        a, b = CAP_SX[ch], CAP_SX[ch]*1.05; ea, eb = wd(a), wd(b)
        for _ in range(3): c = b + (tgt - eb)*(b - a)/(eb - ea); a, ea, b, eb = b, eb, c, wd(c)
        sx = b
    P_ = _caps(ch, w); x0, y0, x1, y1 = P_.bounds; d = CAP_D[w]; sy = (top - 2*d)/(y1 - y0); sx = sx or CAP_SX[ch]
    p = _embolden(V.xform(P_, lambda x, y: ((x - x0)*sx, (y - y0)*sy + d)), d)
    if ch in NIB: p = nib(p, *NIB[ch][w]); p = V.move(p, -p.bounds[0], 0)
    return p
def z_from_Z(w):
    if w == 'Bold':                                          # z Bold chỉ rộng hơn z Regular ½ B_STEM (Z Bold rộng hơn Z Regular 48)
        zr = _caps('z', 'Regular').bounds; zb = _caps('z', 'Bold').bounds
        wr = (zr[2] - zr[0])*CAP_SX['z'] + 2*CAP_D['Regular']
        old = CAP_SX['z']; CAP_SX['z'] = (wr + L.B_STEM/2 - 2*CAP_D['Bold'])/(zb[2] - zb[0])
        try: return shrink_caps('z', w)
        finally: CAP_SX['z'] = old
    return shrink_caps('z', w)

def k_from_K(w, sxk=None):
    """k: thân K giữ nguyên chiều cao (= ascender 698.6 ≈ cap), tay + chân thu về x-height; Bold: thân về 124.5 (thân Bold thường),
    dày ra đều hai phía (mép trái lùi ½ B_STEM), phần chéo giữ đúng vươn ngang của Regular tính từ mép phải thân → k Bold rộng
    hơn Regular đúng B_STEM (như n)"""
    P_ = _caps('k', w); x0, y0, x1, y1 = P_.bounds
    s0, s1 = runs_at(P_, 600)[0]                             # mép thân ở 600 (trên chỗ tay nhập thân)
    v = W[w]['V']; kx = v/(s1 - s0)
    if w == 'Bold' and sxk is None:                          # giải sxk để vươn chéo (từ mép phải thân) = Regular
        R = k_from_K('Regular'); tgt = R.bounds[2] - runs_at(R, 600)[0][1]
        def ext(k): p = k_from_K(w, k); return p.bounds[2] - runs_at(p, 600)[0][1]
        a, b = 0.6, 0.9; ea, eb = ext(a), ext(b)
        for _ in range(4):                                   # secant
            c = b + (tgt - eb)*(b - a)/(eb - ea); a, ea, b, eb = b, eb, c, ext(c)
        sxk = b
    elif sxk is None: sxk = CAP_SX['k']
    h = (v - W['Regular']['V'])/2 if w == 'Bold' else 0.0
    FLR = 90                                                 # vùng loe phải của thân (đỉnh, chân) đi theo thân, không theo nét chéo
    stem = V.U(V.I(P_, V.rect(x0 - 50, -50, s1 + 0.5, 800)), V.I(P_, V.rect(s1 - 1, 700 - FLR, s1 + 40, 800)),
               V.I(P_, V.rect(s1 - 1, -50, s1 + 40, FLR)))
    stem = V.xform(stem, lambda x, y: (s0 - h + (x - s0)*kx, y*ASC/700))
    d = CAP_D[w]; sx = sxk; sy = (XH - 2*d)/(y1 - y0)
    diag = V.D(V.I(P_, V.rect(s1 + 0.5, -50, x1 + 50, 800)), V.U(V.rect(s1 - 1, 700 - FLR, s1 + 40, 800), V.rect(s1 - 1, -50, s1 + 40, FLR)))
    diag = _embolden(V.xform(diag, lambda x, y: (s0 - h + v - 0.5 + (x - s1)*sx, y*sy + d)), d)
    xr = s0 - h + v - 0.5                                    # tay / chân sau khi bù nét không lấn qua mép phải thân (bậc 6 u)
    return V.U(stem, V.I(V.I(diag, V.halfplane(0)), V.rect(xr, -100, 2000, 2000)))

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

CHARS = 'fhijklmnsuvwxyz'      # o, c, r, t: đã có bản vẽ designer (lower.py)
if __name__ == '__main__':
    out = {}
    for c in CHARS:
        for w in ('Regular', 'Bold'):
            o = L._q2c(glyph(c, w)); o = V.move(o, -o.bounds[0], 0)
            out[f'{c}-{w}'] = [V.to_d(L.clean(o))]
    json.dump(out, open(os.path.join(HERE, 'lower_derived.json'), 'w'))
    from make_ref import outline
    for k, v in out.items(): print(k, [round(x, 1) for x in outline(v).bounds])
