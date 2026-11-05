#!/usr/bin/env python3
"""Ký tự bổ sung nhóm 1 + 2 (designer 05/11: "làm nhóm 1 và 2 trước"), Regular + Bold — dựng theo luật, cùng hệ nét với
dấu câu đã có (vn_punct.py: bảng V / H, bút dẹt PHI 20°, họ chấm, nêm loe).
    python3 tools/construct/ref/symbols.py   → designer_D.json (y lên, baseline 0, cap 700)

Nhóm 1: * < > \\ ^ _ ` { } | ~ · gạch mềm (U+00AD = -) · ı ȷ · dấu tổ hợp rộng 0 U+0300 0301 0302 0303 0306 0308 0309 030A
        030C 031B 0323 0327 (space / nbsp: chỉ bề ngang, ghi trong spacing.json)
Nhóm 2: … • · « » ‹ › ‚ „ ¡ ¿ © ® ™ ° ± ÷ − ‰ § ¶ † ‡ £ ¥ ¢ µ

Luật chung (S15 ký hiệu):
- trục toán yc = 330 (như + = ×); nét toán đứng 0.62 V, ngang 0.55 V (như +).
- nét bút (chevron, ngoặc nhọn, £): bút dẹt của chữ (N, m) × 0.8 → nét / mảnh, nét \\ dày theo đúng logic bút.
- chấm: cùng họ chấm (Ø t['dot']); nêm (†, ‡, *): wedge() như ! và nháy.
- chữ dùng lại (C R T M Y, c u s i j): bản vẽ designer / chữ thường đã dựng, không vẽ lại.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pathops
import vn_punct as V
from vn_punct import T, U, D, I, rect, poly, ellipse, move, xform, bounds, stroke, hermite, line, arc, wedge, dot, comma_shape
from make_ref import outline as ref_outline

XH, DESC, YC = 495.0, -200.8, 330.0
COMB = '̧̛̣̀́̂̃̆̈̉̊̌'

def lower_src():
    S = {}
    for f in ('lower.json', 'lower_derived.json'): S.update(json.load(open(os.path.join(HERE, '..', 'lower', f))))
    return S

def embolden(p, d):
    s = pathops.Path(); s.addPath(p); s.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    s.convertConicsToQuads(); return q2c(U(p, q2c(s)))

def q2c(p):
    out = pathops.Path(); cur = None
    for v, ps in p.segments:
        if v == 'moveTo': out.moveTo(*ps[0]); cur = ps[0]
        elif v == 'lineTo': out.lineTo(*ps[0]); cur = ps[0]
        elif v == 'curveTo': out.cubicTo(*ps[0], *ps[1], *ps[2]); cur = ps[2]
        elif v == 'qCurveTo':
            pts = list(ps)
            ctrl, end = pts[:-1], pts[-1]
            # TrueType implied on-curve giữa các điểm điều khiển
            seq = []
            for i, c in enumerate(ctrl):
                nxt = ctrl[i + 1] if i + 1 < len(ctrl) else None
                seq.append((c, ((c[0] + nxt[0])/2, (c[1] + nxt[1])/2) if nxt else end))
            for c, e in seq:
                out.cubicTo(cur[0] + 2/3*(c[0] - cur[0]), cur[1] + 2/3*(c[1] - cur[1]), e[0] + 2/3*(c[0] - e[0]), e[1] + 2/3*(c[1] - e[1]), *e); cur = e
        elif v == 'closePath': out.close()
    return out

def norm_x(p): b = bounds(p); return move(p, -b[0], 0)
def scale(p, s, o=(0, 0)): return xform(p, lambda x, y: (o[0] + (x - o[0])*s, o[1] + (y - o[1])*s))

def pen_w(theta, nib):
    """độ dày bút dẹt theo hướng nét theta (như vn_punct.stroke): sqrt((N·sin(θ − PHI))² + m²)"""
    return math.hypot(nib[0]*math.sin(theta - V.PHI), nib[1])

def chevron(apex, h, w, nib, left=True):
    """< (left) hoặc > : ĐA GIÁC (như dấu mũ): mép ngoài hai nhánh gặp nhau thành đỉnh nhọn; mép trong lùi vào đúng độ dày bút
    của từng nhánh (nhánh trên / mảnh, nhánh dưới \\ dày theo bút dẹt), giao nhau ở đỉnh trong; hai đầu cắt đứng.
    (designer 05/11: "Lỗi" — bản nét bút cũ chồng hai mặt cắt ở đỉnh thành mỏm lởm chởm)"""
    ax, ay = apex; sx = 1 if left else -1; ex = ax + sx*w
    a = math.atan2(h, w)                                             # góc nhánh với phương ngang
    tu = pen_w(a if left else math.pi - a, nib); tl = pen_w(-a if left else math.pi + a, nib)
    du, dl = tu/math.cos(a), tl/math.cos(a)                          # độ lệch đứng của mép trong
    k = h/w                                                          # độ dốc nhánh
    # mép trong: y = ay + k|x−ax| − du (nhánh trên), y = ay − k|x−ax| + dl (nhánh dưới) → giao ở |x−ax| = (du + dl)/(2k)
    xi = (du + dl)/(2*k); yi = ay + k*xi - du
    pts = [(ax, ay), (ex, ay + h), (ex, ay + h - du), (ax + sx*xi, yi), (ex, ay - h + dl), (ex, ay - h)]
    return poly(pts if left else pts[::-1])

def build_w(S, L, w):
    t = T[w]; Vv, H = t['V'], t['H']; d = t['dot']; r = d/2; bold = w == 'Bold'
    nib = (t['N']*0.8, t['m']*0.85)
    P = V.punct(S, w); M = V.marks(w); G = {}
    # ---------- nhóm 1 ----------
    # * : 6 cánh nêm (đầu ngoài rộng, đầu trong hẹp) quanh tâm ở 0.80 cap, bán kính 150
    cx, cy, R = 170, 560, 150
    spoke = wedge(0, cy + R, cy + 10, 0.58*Vv, 0.20*Vv, 0.25)
    G['*'] = norm_x(U(*[xform(spoke, lambda x, y, a=math.radians(60*k): (cx + x*math.cos(a) - (y - cy)*math.sin(a),
                                                                       cy + x*math.sin(a) + (y - cy)*math.cos(a))) for k in range(6)]))
    # < > : nét bút trên trục toán, cao 420, rộng 400
    G['<'] = norm_x(chevron((0, YC), 200, 400, (t['N']*0.72, t['m']), True))
    G['>'] = norm_x(chevron((400, YC), 200, 400, (t['N']*0.72, t['m']), False))
    # \ : gương của /
    sl = P['/']; b = bounds(sl); G['\\'] = xform(sl, lambda x, y: (b[0] + b[2] - x, y))
    # ^ : mũ lớn (mũ dấu × 1.35), đỉnh ở cap
    ci = scale(M['circumflex'], 1.35); b = bounds(ci); G['^'] = norm_x(move(ci, 0, 700 - b[3]))
    # _ : gạch dưới dày như gạch nối, ở −120
    hy = 0.58*Vv; G['_'] = rect(0, -150, 500, -150 + hy)
    # ` : huyền đứng riêng, đáy ở 560 (vùng dấu chữ thường)
    gv = M['grave']; b = bounds(gv); G['`'] = norm_x(move(gv, 0, 560 - b[1]))
    # { } : nét bút: đầu trên cong ra phải, thân thẳng, mũi nhọn ở trục 355 (như ngoặc tròn / vuông: −150 … 860)
    def brace():
        """{ : nửa trên là MỘT nét bút từ đầu trên (đi ngang sang trái) → thân đứng → kéo quá mũi; cắt NGANG đúng ở trục mũi 355
        rồi lật gương xuống → hai nửa trùng khít ở mặt cắt, mũi nhọn sạch (designer 05/11: "Lỗi" — mũi răng cưa); đầu nét cắt
        đứng ở mép phải"""
        x0, xm, xt, ym = 0.0, 105.0, 215.0, 355.0
        n = (t['N']*0.95, t['m']*1.25)
        half = [((xt + 40, 815), (-1, 0)), ((xm, 715), (0, -1)), ((xm, 470), (0, -1)), ((x0 - 60, ym - 40), (-1, -0.55))]
        top = I(stroke(hermite(half), n, taper=lambda u: 0.80 + 0.20*math.sin(math.pi*min(1.0, u*1.15))), rect(-500, ym, xt, 1200))
        bot = xform(top, lambda x, y: (x, 2*ym - y))
        return q2c(U(top, bot))
    # | : thanh đứng 0.58 V, −150 … 860 (như ngoặc)
    G['|'] = rect(0, -150, 0.58*Vv, 860)
    # ~ : ngã lớn (ngã dấu × 1.7) trên trục toán
    tl = scale(M['tilde'], 1.7); b = bounds(tl); G['~'] = norm_x(move(tl, 0, YC - (b[1] + b[3])/2))
    # gạch mềm = gạch nối
    G['­'] = P['-']
    # ı ȷ : i j bỏ chấm (chấm i đáy ở XH + 70)
    for c0, c1 in (('i', 'ı'), ('j', 'ȷ')):
        g = ref_outline(L[f'{c0}-{w}']); G[c1] = I(g, rect(-500, -500, 2000, XH + 30))
    # dấu tổ hợp (rộng 0): CÙNG bộ dấu (vn_punct.marks) đặt ở vùng dấu chữ thường, tâm x = 0 (spacing đặt về trước)
    yl = 495 + 8.4 + V.GAP_ML + 3
    def above(m): b = bounds(m); return move(m, -(b[0] + b[2])/2, yl - b[1])
    G['̀'] = above(M['grave']); G['́'] = above(M['acute']); G['̂'] = above(M['circumflex'])
    G['̃'] = above(M['tilde']); G['̆'] = above(M['breve']); G['̉'] = above(M['hook'])
    md = t['mdot']; G['̈'] = above(U(dot((0, 0), md), dot((md + 0.75*md, 0), md)))
    ro = 0.62*md + 18; G['̊'] = above(D(ellipse((0, 0), ro, ro), ellipse((0, 0), ro - 0.34*Vv, ro - 0.34*Vv)))
    cf = M['circumflex']; b = bounds(cf); G['̌'] = above(xform(cf, lambda x, y: (x, b[1] + b[3] - y)))
    hn = M['horn']; b = bounds(hn); G['̛'] = move(hn, -b[0] - 30, XH - 70)          # bám mép phải chữ trước
    db = M['dotbelow']; b = bounds(db); G['̣'] = move(db, -(b[0] + b[2])/2, -11.3 - V.GAP_ML - (b[3] - b[1]))
    # móc dưới (cedilla) (designer 05/11: "Lỗi" — bản cũ dài, mảnh, thả tới −230): cổ ngắn từ đáy chữ, bụng móc phình sang phải
    # (nét bút dày như dấu), quặt về trái mảnh dần; đáy ≈ −165
    ce = hermite([((0, 25), (0, -1)), ((4, -45), (0.2, -1)), ((62, -95), (0.6, -1)), ((22, -158), (-1, -0.5)), ((-58, -162), (-1, 0.15))])
    ced = stroke(ce, (t['Nm']*1.05, t['mm']*1.15), taper=lambda u: 1.0 if u < 0.6 else 1.0 - 0.9*(u - 0.6))
    b = bounds(ced); G['\u0327'] = move(ced, -(b[0] + b[2])/2 + 8, 0)
    # ---------- nhóm 2 ----------
    sp = d + 0.8*d
    G['…'] = U(*[dot((r + k*sp, r - 3), d) for k in range(3)])
    G['•'] = dot((0.9*d, YC), 1.8*d)
    G['·'] = dot((r, 300), d)
    gw, gh = 200, 150; gn = (t['N']*0.62, t['m']*0.9); gy = 250
    ch1 = chevron((0, gy), gh, gw, gn, True); ch2 = chevron((gw, gy), gh, gw, gn, False)
    G['‹'] = norm_x(ch1); G['›'] = norm_x(ch2)
    gap_g = 0.62*gw
    G['«'] = norm_x(U(ch1, move(ch1, gap_g + 0.5*Vv, 0))); G['»'] = norm_x(U(ch2, move(ch2, gap_g + 0.5*Vv, 0)))
    G['‚'] = P[',']
    cm = P[','];  w1 = bounds(P['”'])[2] - bounds(P['’'])[2]; G['„'] = U(cm, move(cm, w1, 0))
    for src_, dst in (('!', '¡'), ('?', '¿')):
        g = P[src_]; b = bounds(g); g = xform(g, lambda x, y: (b[0] + b[2] - x, b[1] + b[3] - y)); b = bounds(g)
        G[dst] = norm_x(move(g, 0, (XH + 8.4) - b[3]))
    # © ®: vòng nét bút (nét tròn mảnh 0.45 V, dày 0.62 V, trục nghiêng như O) + C / R hoa thu về 0.44 cap
    Rr = 360; ring = D(ellipse((Rr, 350), Rr, Rr), ellipse((Rr + 4, 350), Rr - 0.62*Vv, Rr - 0.45*Vv, 30 + 90))
    def inner(ch):
        g = V.letter(S, ch, w); g = scale(g, 0.44); g = embolden(g, 0.10*Vv); b = bounds(g)
        return move(g, Rr - (b[0] + b[2])/2, 350 - (b[1] + b[3])/2)
    G['©'] = U(ring, inner('C')); G['®'] = U(ring, inner('R'))
    # ™: T M hoa thu 0.42, đỉnh ở cap, bù nét để thân ≈ 0.6 V
    def sup(ch, s=0.42):
        g = embolden(scale(V.letter(S, ch, w), s), 0.09*Vv); b = bounds(g); return move(g, -b[0], 700 - b[3])
    tT = sup('T'); tM = sup('M'); G['™'] = U(tT, move(tM, bounds(tT)[2] + 0.35*Vv, 0))
    # °: vòng nhỏ đỉnh ở cap
    ro = 105; G['°'] = D(ellipse((ro, 700 - ro), ro, ro), ellipse((ro, 700 - ro), ro - 0.42*Vv, ro - 0.42*Vv))
    # − ± ÷ (cùng nét +)
    mv, mh, ms = 0.62*Vv, 0.55*Vv, 500
    G['−'] = rect(0, YC - mh/2, ms, YC + mh/2)
    pl = U(rect(ms/2 - mv/2, YC + 60 - ms/2 + 50, ms/2 + mv/2, YC + 60 + ms/2 - 50), rect(0, YC + 60 - mh/2, ms, YC + 60 + mh/2))
    G['±'] = U(pl, rect(0, 0, ms, mh))
    G['÷'] = U(G['−'], dot((ms/2, YC + 150), 0.95*d), dot((ms/2, YC - 150), 0.95*d))
    # ‰: % + một vòng nữa bên phải vòng dưới
    pc = P['%']; b = bounds(pc)
    lo = I(pc, rect(b[2] - 2*(118 + (8 if bold else 0)) - 5, -50, b[2] + 5, 330))
    G['‰'] = U(pc, move(lo, 2*(118 + (8 if bold else 0)) + 0.35*Vv, 0))
    # § : hai s thường (× SEC) chồng nhau — s dưới = s trên xoay 180°; dời dọc để bụng dưới của s trên trùng bụng trên của
    # s dưới → vòng kín ở giữa (§ cổ điển); tổng cao từ −110 tới 700
    s0 = ref_outline(L[f's-{w}']); SEC = 0.82; s0 = scale(s0, SEC); b = bounds(s0); hs = b[3] - b[1]
    s0 = move(s0, -b[0], -b[1]); b = bounds(s0)
    rot = xform(s0, lambda x, y: (b[2] - x, b[3] - y))
    ov = 0.50*hs                                                  # phần chồng: đúng một bụng
    top_ = move(s0, 0, hs - ov); sec = q2c(U(top_, rot)); bb = bounds(sec)
    G['§'] = move(sec, 0, (700 - 110)/2 - (bb[1] + bb[3])/2 + 0)
    # ¶ : bụng đặc (nửa elip trái) + hai thân 0.5 V, −150 … 700
    st = 0.5*Vv; bx = 300
    bowl = I(ellipse((bx, 520), bx, 180), rect(0, 0, bx + 1, 800))
    G['¶'] = U(bowl, rect(bx - 1, -150, bx + st, 700), rect(bx + st + 70, -150, bx + 2*st + 70, 700), rect(bx, 700 - 0.55*H, bx + 2*st + 70, 700))
    # † ‡ : thân nêm (rộng ở hai đầu) + thanh ngang nêm
    def dag(ys):
        stem = U(wedge(0, 700, 300, 0.62*Vv, 0.36*Vv, 0.2), xform(wedge(0, 700, 300, 0.62*Vv, 0.36*Vv, 0.2), lambda x, y: (x, 300 - (y - 300) - 50 if y < 9999 else y)))
        stem = U(rect(-0.18*Vv, -150, 0.18*Vv, 700), wedge(0, 700, 420, 0.62*Vv, 0.36*Vv, 0.2),
                 xform(wedge(0, 700, 420, 0.62*Vv, 0.36*Vv, 0.2), lambda x, y: (x, 550 - y)))
        bars = []
        for yb in ys:
            hb = wedge(0, 180, 0, 0.55*Vv, 0.30*Vv, 0.2)
            arm = xform(hb, lambda x, y, yb=yb: (y, yb + x))
            bars += [arm, xform(arm, lambda x, y: (-x, y))]
        return norm_x(U(stem, *bars))
    G['†'] = dag([520]); G['‡'] = dag([540, 120])
    # £ : nét bút: móc trên (cong như f) → thân → chân cong vào thanh đáy; thanh giữa ngang ở 330
    pn = (t['N']*0.95, t['m']*1.1)
    spine = hermite([((440, 590), (-0.2, 1)), ((330, 700), (-1, 0)), ((200, 600), (0, -1)), ((200, 200), (0, -1)), ((80, 40), (-1, -0.8))])
    lb = U(stroke(spine, pn, taper=lambda u: 0.75 + 0.25*min(1, 2*u)), rect(40, 0, 480, 0.6*H + 14), rect(50, 300, 380, 300 + 0.6*H + 14))
    G['£'] = norm_x(I(lb, rect(-100, 0, 2000, 711)))
    # ¥ : Y hoa + hai thanh 0.70 H, khe 60 (luật ¥ €)
    yy = V.letter(S, 'Y', w); b = bounds(yy); bh = 0.70*H*1.4
    G['¥'] = U(yy, rect(b[0] + 0.12*(b[2] - b[0]), 300, b[2] - 0.12*(b[2] - b[0]), 300 + bh),
               rect(b[0] + 0.12*(b[2] - b[0]), 300 - 60 - bh, b[2] - 0.12*(b[2] - b[0]), 300 - 60))
    # ¢ : c thường + nét đứng mảnh 1.1 H xuyên qua, vươn ±100
    c0 = ref_outline(L[f'c-{w}']); b = bounds(c0); xcn = (b[0] + b[2])/2 + 10
    G['¢'] = U(c0, rect(xcn - 0.55*H, -100, xcn + 0.55*H, XH + 110))
    # µ : u thường, thân trái kéo xuống descender (cắt bằng)
    u0 = ref_outline(L[f'u-{w}']); runs = I(u0, rect(-100, 249.95, 2000, 250.05)); xs = sorted(set(round(q[0], 1) for _, ps in runs.segments for q in ps))
    G['µ'] = U(u0, rect(xs[0], DESC, xs[1], 60))
    G.update(group3(S, L, w, M, P, G))
    return G

# ---------------- nhóm 3 (designer 05/11: "làm tiếp nhóm 3") ----------------
MARK_YL = 495 + 8.4 + V.GAP_ML + 3          # đáy dấu chữ thường (như vn_lower)
def group3(S, L, w, M, P, G1):
    t = T[w]; Vv, H = t['V'], t['H']; md = t['mdot']; G = {}
    lw = lambda c: ref_outline(L[f'{c}-{w}'])
    def xcen(p, top):                                         # tâm ngang phần thân chữ (bỏ đuôi / dấu)
        b = bounds(I(p, rect(-500, -5, 3000, top))); return (b[0] + b[2])/2
    # dấu dùng chung (đáy y = 0, tâm x = 0)
    def c0(m): b = bounds(m); return move(m, -(b[0] + b[2])/2, -b[1])
    MK = {'diaer': c0(U(dot((0, 0), md), dot((md + 0.75*md, 0), md))),
          'ring': c0(D(ellipse((0, 0), 0.62*md + 18, 0.62*md + 18), ellipse((0, 0), 0.62*md + 18 - 0.34*Vv, 0.62*md + 18 - 0.34*Vv))),
          'caron': c0(xform(M['circumflex'], lambda x, y: (x, -y))), 'tilde': c0(M['tilde']), 'circ': c0(M['circumflex'])}
    ced = G1['\u0327']
    def cap_acc(base, mk):
        p = V.letter(S, base, w); cx = V.anchor_x(base, p)
        if mk == 'ring':                                       # Å: vòng sát đỉnh A hơn (khe 0.6 khe dấu)
            return U(p, move(MK[mk], cx, 700 + 11.3 + 0.6*V.GAP_ML))
        return U(p, move(MK[mk], cx, V.MARK_Y))
    def low_acc(base, mk, src=None):
        p = src if src is not None else lw(base); cx = xcen(p, 495 + 25)
        return U(p, move(MK[mk], cx, MARK_YL))
    for ch, (b, mk) in {'Ä': ('A', 'diaer'), 'Å': ('A', 'ring'), 'Ë': ('E', 'diaer'), 'Î': ('I', 'circ'), 'Ï': ('I', 'diaer'),
                        'Ñ': ('N', 'tilde'), 'Ö': ('O', 'diaer'), 'Û': ('U', 'circ'), 'Ü': ('U', 'diaer'), 'Ÿ': ('Y', 'diaer'),
                        'Š': ('S', 'caron'), 'Ž': ('Z', 'caron')}.items():
        G[ch] = cap_acc(b, mk)
    dl = G1['ı']
    for ch, (b, mk) in {'ä': ('a', 'diaer'), 'å': ('a', 'ring'), 'ë': ('e', 'diaer'), 'ñ': ('n', 'tilde'), 'ö': ('o', 'diaer'),
                        'û': ('u', 'circ'), 'ü': ('u', 'diaer'), 'ÿ': ('y', 'diaer'), 'š': ('s', 'caron'), 'ž': ('z', 'caron')}.items():
        G[ch] = low_acc(b, mk)
    G['î'] = low_acc('i', 'circ', dl); G['ï'] = low_acc('i', 'diaer', dl)
    # Ç ç: móc dưới (cùng nét U+0327) bám đáy giữa chữ
    for ch, p in (('Ç', V.letter(S, 'C', w)), ('ç', lw('c'))):
        b = bounds(p); G[ch] = U(p, move(ced, (b[0] + b[2])/2 + 15, b[1] + 25))
    # Ð = Đ (cùng hình) · Ø ø: O / o + nét chéo / mảnh (bút dẹt) vượt vòng
    G['Ð'] = V.dstroke(S, w)
    for ch, p in (('Ø', V.letter(S, 'O', w)), ('ø', lw('o'))):
        b = bounds(p); wd = b[2] - b[0]; sw = 0.42*Vv           # nét / mảnh, dốc ~60°, chìa ra ngoài vòng 30
        a0, a1 = (b[0] + 0.14*wd, b[1] - 30), (b[2] - 0.14*wd, b[3] + 30)
        ang = math.atan2(a1[1] - a0[1], a1[0] - a0[0]); nx, ny = -math.sin(ang)*sw/2, math.cos(ang)*sw/2
        G[ch] = U(p, poly([(a0[0] - nx, a0[1] - ny), (a1[0] - nx, a1[1] - ny), (a1[0] + nx, a1[1] + ny), (a0[0] + nx, a0[1] + ny)]))
    # Æ: A bỏ chân phải (cắt dọc qua đỉnh) + E có thân đứng tại đỉnh A
    A_ = V.letter(S, 'A', w); E_ = V.letter(S, 'E', w); ab = bounds(A_)
    top = I(A_, rect(-100, 690, 2000, 800)); tb = bounds(top); apx = (tb[0] + tb[2])/2
    left = I(A_, rect(-100, -100, apx + 0.5*Vv, 800))
    eb = bounds(E_); es = I(E_, rect(-100, 300, 2000, 300.1)); ex0 = bounds(es)[0]
    G['Æ'] = U(left, move(E_, apx - 0.15*Vv - ex0, 0))
    # Œ: O cắt ở 0.62 bề ngang + E có thân trùng chỗ cắt
    O_ = V.letter(S, 'O', w); ob = bounds(O_); xcut = ob[0] + 0.60*(ob[2] - ob[0])
    G['Œ'] = U(I(O_, rect(-100, -100, xcut, 800)), move(E_, xcut - Vv - ex0, 0))
    # æ: a + e chồng — vách trái e trùng thân a; œ: o + e chồng một vách
    a_ = lw('a'); e_ = lw('e'); o_ = lw('o'); abx = bounds(a_); ebx = bounds(e_); obx = bounds(o_)
    G['æ'] = U(a_, move(e_, abx[2] - 0.62*Vv - ebx[0] - 25, 0))
    G['œ'] = U(o_, move(e_, obx[2] - 0.80*Vv - ebx[0], 0))
    # Þ: thân P cao trọn cap, bụng P hạ xuống 140 (giữa thân); þ: p có thân vươn lên ascender (đỉnh thân b)
    P_ = V.letter(S, 'P', w); pb = bounds(P_); st = I(P_, rect(-100, 299.9, 2000, 300.1)); sr = sorted(set(round(q[0], 1) for _, ps in st.segments for q in ps))
    s1 = sr[1]; stem = I(P_, rect(-100, -100, s1 + 0.5, 800)); bowl = I(P_, rect(s1 - 2, 300, 2000, 800))
    G['Þ'] = U(stem, move(bowl, 0, -150))
    p_ = lw('p'); b_ = lw('b'); bb = bounds(b_); pbx = bounds(p_)
    G['þ'] = U(p_, move(I(b_, rect(-100, 300, bb[0] + 0.5*(bb[2] - bb[0]), 800)), pbx[0] - bb[0], 0))
    # ð: o + cổ cong (nét bút) từ vai phải lên ascender, cắt chéo bằng thanh nhỏ
    nb = (t['N']*0.9, t['m']*1.1)
    ow = obx[2] - obx[0]
    neck = hermite([((obx[2] - 0.32*Vv, 360), (0.05, 1)), ((obx[2] - 0.30*ow, 640), (-0.8, 1)), ((obx[0] + 0.28*ow, 712), (-1, 0.05))])
    eth = U(o_, stroke(neck, nb, taper=lambda u: 1.0 - 0.55*u))
    nx_ = obx[2] - 0.22*ow                                      # thanh gạch thẳng, hơi chếch lên phải, cắt ngang cổ ở 585
    G['ð'] = U(eth, poly([(nx_ - 120, 560), (nx_ + 95, 610), (nx_ + 95, 610 + 0.85*H), (nx_ - 120, 560 + 0.85*H)]))
    # ß: thân l thường (đỉnh vòm sang phải) + nét bút: vòm trên → eo → bụng dưới về chân
    l_ = lw('l'); lb = bounds(l_); lsr = I(l_, rect(-100, 299.9, 2000, 300.1)); lx = sorted(set(round(q[0], 1) for _, ps in lsr.segments for q in ps))
    # thân + vòm + bụng là MỘT nét bút liền (độ rộng bút đứng = thân chữ thường) — designer 05/11: "Lỗi" (đỉnh thân bậc ở
    # chỗ nối vòm); chân loe lấy từ l
    sw_ = lx[1] - lx[0]; mm = t['m']*1.15; NN = math.sqrt(max(sw_**2 - mm**2, 1))/math.sin(math.radians(90) - V.PHI)
    foot = I(l_, rect(-100, -100, 2000, 160)); xr0 = lx[0] + sw_/2
    sp = hermite([((xr0, 120), (0, 1)), ((xr0, 520), (0, 1)), ((xr0 + 135, 705), (1, 0)), ((xr0 + 265, 590), (0, -1)), ((xr0 + 150, 430), (-1, -0.3)),
                  ((xr0 + 325, 230), (0.1, -1)), ((xr0 + 190, -8), (-1, -0.02)), ((lx[1] + 75, 8), (-1, 0.3))])
    G['ß'] = q2c(U(foot, stroke(sp, (NN, mm))))
    # toán / phút giây
    YC_ = 330.0; mh = 0.55*Vv; ms = 500
    eq = P['=']; eb_ = bounds(eq); cxq = (eb_[0] + eb_[2])/2; sw = 0.45*Vv
    def slash(xc, yc, hh, lean=0.38):
        dx = hh*lean; return poly([(xc - dx - sw/2, yc - hh), (xc - dx + sw/2, yc - hh), (xc + dx + sw/2, yc + hh), (xc + dx - sw/2, yc + hh)])
    G['≠'] = U(eq, slash(cxq, YC_, 230))
    lt, gt = G1['<'], G1['>']
    def le(ch_):
        b = bounds(ch_); sc_ = 0.84; c_ = scale(ch_, sc_, ((b[0] + b[2])/2, YC_)); c_ = move(c_, 0, 85)
        cb = bounds(c_); return U(c_, rect(cb[0], YC_ - 230, cb[2], YC_ - 230 + mh))
    G['≤'] = le(lt); G['≥'] = le(gt)
    tl = scale(G1['~'], 0.78); tb_ = bounds(tl); tl = move(tl, 0, YC_ - (tb_[1] + tb_[3])/2)
    G['≈'] = U(move(tl, 0, 92), move(tl, 0, -92))
    G['¬'] = U(rect(0, YC_ - mh/2, ms, YC_ + mh/2), rect(ms - 0.62*Vv, YC_ - 200, ms, YC_ + mh/2))
    G['¦'] = U(rect(0, -150, 0.58*Vv, 300), rect(0, 410, 0.58*Vv, 860))
    q1 = P["'"]; qb = bounds(q1); sh = math.tan(math.radians(14))
    pr = xform(q1, lambda x, y: (x + (y - qb[1])*sh, y)); G['′'] = pr
    G['″'] = U(pr, move(pr, (bounds(pr)[2] - bounds(pr)[0]) + 0.35*Vv, 0))
    return G

def build():
    S = V.load(); L = lower_src(); out = {}
    for w in ('Regular', 'Bold'):
        for ch, p in build_w(S, L, w).items():
            p = q2c(p)
            if ch not in COMB: p = norm_x(p)
            out[f'{ch}-{w}'] = [V.to_d(p)]
    json.dump(out, open(os.path.join(HERE, 'designer_D.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('ok', len(out))

if __name__ == '__main__':
    build()
