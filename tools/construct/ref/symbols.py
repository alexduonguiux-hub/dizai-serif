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

def chevron(apex, h, w, nib, left=True):
    """< (left) hoặc >: hai nét bút từ hai đầu về đỉnh; nét / mảnh, nét \\ dày (bút dẹt). apex = đỉnh nhọn, h = nửa chiều cao"""
    sx = 1 if left else -1
    top = (apex[0] + sx*w, apex[1] + h); bot = (apex[0] + sx*w, apex[1] - h)
    a = stroke([line(top, apex)], nib); b = stroke([line(apex, bot)], nib)
    c = U(a, b)
    # đỉnh: cắt phẳng vuông góc trục (tránh mũi nhọn dài), đầu: cắt đứng
    c = I(c, rect(min(apex[0], top[0]) - 400 if left else apex[0] - 400, -2000, max(apex[0], top[0]) + 400, 2000))
    c = I(c, rect(-4000, -2000, top[0], 4000) if left else rect(top[0], -2000, 4000, 4000))
    return c

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
        x0, xm, xt = 0.0, 95.0, 190.0
        top = [((xt, 860), (-1, 0)), ((xm, 780), (0, -1)), ((xm, 470), (0, -1)), ((x0, 355), (-1, -0.35))]
        bot = [((x0, 355), (1, -0.35)), ((xm, 240), (0, -1)), ((xm, -70), (0, -1)), ((xt, -150), (1, 0))]
        n = (t['N']*0.9, t['m']*1.2)
        return U(stroke(hermite(top), n, taper=lambda u: 0.75 + 0.25*math.sin(math.pi*min(1, u*1.2))),
                 stroke(hermite(bot), n, taper=lambda u: 0.75 + 0.25*math.sin(math.pi*min(1, (1 - u)*1.2))))
    br = brace(); br = I(br, rect(-500, -150, 2000, 860)); G['{'] = norm_x(br)
    b = bounds(G['{']); G['}'] = xform(G['{'], lambda x, y: (b[2] - x, y))
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
    # móc dưới (cedilla): nét bút từ đáy chữ xuống, cong sang phải rồi quặt về trái, đầu cắt ngang
    ce = hermite([((0, 10), (0, -1)), ((0, -60), (0, -1)), ((70, -120), (1, -0.2)), ((40, -200), (-1, -0.6)), ((-60, -215), (-1, 0))])
    ced = stroke(ce, (t['Nm']*0.75, t['mm']), taper=lambda u: 1.0 - 0.25*u); b = bounds(ced)
    G['̧'] = move(ced, -(b[0] + b[2])/2 + 10, 0)
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
