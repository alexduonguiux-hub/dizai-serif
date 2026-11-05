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

def n_like(w, asc=False, arches=1):
    v = W[w]['V']; s0, s1 = arch_stem(w); A = arch(w)
    parts = [vstem(0, v, 0, ASC if asc else XH, 'tlblbr' + ('tr' if asc else ''))]
    for i in range(arches):
        dx = i*s0
        parts += [V.move(A, dx, 0), vstem(dx + s0, dx + s1, 0, 300, 'bl')]
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
C_KX = {'r': 0.70, 'f': 0.72, 't': 0.78, 'j': 0.78}
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
    if ch == 'f':
        dy = ASC + 8.4 - 503.4
        bar = V.rect(-95, XH - H, v + 165, XH)
        return V.U(vstem(0, v, 0, C_MID + dy + 20, 'blbr'), V.move(c_half(w, True, C_KX['f']), 0, dy), bar)
    if ch == 't':
        top = 640.0; bar = V.rect(-110, XH - H, v + 150, XH)
        return V.U(vstem(0, v, C_MID - 20, top, 'tltr'), c_half(w, False, C_KX['t']), bar)
    if ch == 'j':
        dy = DESC - 8.4 + 11.3
        hk = V.move(N(V.xform(c_half(w, False, C_KX['j']), lambda x, y: (-x, y))), 0, dy)
        hk = V.move(hk, -hk.bounds[0], 0); x1 = hk.bounds[2]
        st = vstem(x1 - v, x1, C_MID + dy - 20, XH, 'tltr')
        return V.U(hk, st, dot(x1 - v/2, w))
    if ch == 'i': return V.U(vstem(0, v, 0, XH, 'tltrblbr'), dot(v/2, w))
    if ch == 'l': return vstem(0, v, 0, ASC, 'tltrblbr')
    if ch == 'v': return vee(w, 455 + wide)
    if ch == 'y': return vee(w, 455 + wide, desc=True)
    if ch == 'w':
        Ww = 690 + 2*wide; a = 0.5*Ww
        v1 = vee(w, a + 30, fl_r=''); v2 = V.move(vee(w, Ww - a + 30, fl_l=''), a - 30, 0)
        return V.U(v1, v2)
    if ch == 'x':
        Wx = 440 + wide; hD = D/2/(XH/math.hypot(Wx, XH)); ht = t/2/(XH/math.hypot(Wx, XH))
        a = stroke((Wx - hD, 0), (hD, XH), D, 'tltrblbr'); b = stroke((ht, 0), (Wx - ht, XH), t, 'tltrblbr')
        return V.U(a, b)
    if ch == 'k':
        st = vstem(0, v, 0, ASC, 'tltrblbr'); ax = v + 265 + wide; lx = v + 300 + wide
        ab, at = (v - 15, 130), (ax - t/2, XH)
        arm = V.I(stroke(ab, at, t, 'tltr'), V.halfplane(0))
        j = (ab[0] + (at[0] - ab[0])*0.42, ab[1] + (at[1] - ab[1])*0.42)
        leg = stroke((lx - D/2, 0), j, D, 'blbr')
        dx, dy = at[0] - ab[0], at[1] - ab[1]; Ln = math.hypot(dx, dy); nrm = (-dy/Ln, dx/Ln)
        up0 = (ab[0] + nrm[0]*t/2, ab[1] + nrm[1]*t/2); up1 = (at[0] + nrm[0]*t/2, at[1] + nrm[1]*t/2)
        leg = V.I(leg, side(up0, up1, left=False))            # chân không thò lên trên mép tay
        return V.U(st, arm, leg)
    if ch == 'z':
        Wz = 400 + wide; hD = D/2/((XH - 2*H)/math.hypot(Wz, XH - 2*H))
        top = V.rect(0, XH - H, Wz, XH); bot = V.rect(0, 0, Wz, H)
        dg = V.poly([(0, H), (2*hD, H), (Wz, XH - H), (Wz - 2*hD, XH - H)])
        return V.U(top, bot, dg)
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

S_SX = 0.85                       # s = S hoa thu: ngang 0.85, dọc về x-height (0.70)
S_D = {'Regular': 7.0, 'Bold': 3.0}   # bù nét mỗi phía (góc vuông giữ sắc): mảnh ≈ H, vách/sống ≈ S hoa (Bold theo mẫu a Bold)
def s_from_S(w):
    """s là S hoa của designer thu nhỏ (designer 05/11: "chữ s thường phải giống chữ s hoa chứ?") — cùng dáng, cùng đầu
    nét; thu ngang S_SX, dọc về x-height, rồi bù nét S_D (nét viền góc vuông) để độ dày khớp chữ hoa."""
    from make_ref import outline
    src = {}
    for f in ('designer_A.json', 'designer_B.json'): src.update(json.load(open(os.path.join(HERE, '..', 'ref', f))))
    Sp = outline(src[f'S-{w}'])
    x0, y0, x1, y1 = Sp.bounds; d = S_D[w]
    sy = (503.4 + 11.3 - 2*d)/(y1 - y0); sx = S_SX
    p = V.xform(Sp, lambda x, y: ((x - x0)*sx, (y - y0)*sy - 11.3 + d))
    stp = pathops.Path(); stp.addPath(p); stp.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    stp.convertConicsToQuads()
    return L._q2c(V.U(p, L._q2c(stp)))

CHARS = 'fhijklmnrstuvwxyz'      # o, c: đã có bản vẽ designer (lower.py)
if __name__ == '__main__':
    out = {}
    for c in CHARS:
        for w in ('Regular', 'Bold'):
            o = L._q2c(glyph(c, w)); o = V.move(o, -o.bounds[0], 0)
            out[f'{c}-{w}'] = [V.to_d(L.clean(o))]
    json.dump(out, open(os.path.join(HERE, 'lower_derived.json'), 'w'))
    from make_ref import outline
    for k, v in out.items(): print(k, [round(x, 1) for x in outline(v).bounds])
