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
from vn_punct import T, TW, WEIGHTS, U, D, I, rect, poly, ellipse, move, xform, bounds, stroke, hermite, line, arc, wedge, dot, comma_shape
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

def xdilate(p, d):
    """cộng Minkowski với đoạn ngang [−d, d]: hợp hai bản dời ±d và dải quét của từng đoạn (giữ đường cong)"""
    parts = [move(p, -d, 0), move(p, d, 0)]
    for v, ps in p.segments:
        if v == 'moveTo': cur = ps[0]; start = cur
        elif v in ('lineTo', 'curveTo', 'closePath'):
            end = start if v == 'closePath' else ps[-1]
            q = pathops.Path(); q.moveTo(cur[0] - d, cur[1])
            if v == 'curveTo':
                a, b = ps[0], ps[1]
                q.cubicTo(a[0] - d, a[1], b[0] - d, b[1], end[0] - d, end[1]); q.lineTo(end[0] + d, end[1])
                q.cubicTo(b[0] + d, b[1], a[0] + d, a[1], cur[0] + d, cur[1])
            else:
                q.lineTo(end[0] - d, end[1]); q.lineTo(end[0] + d, end[1]); q.lineTo(cur[0] + d, cur[1])
            q.close(); q2 = pathops.Path(); q2.addPath(q)
            q2 = pathops.op(q, q, pathops.PathOp.UNION, fix_winding=True) if True else q
            parts.append(q2); cur = end
    return q2c(U(*parts))

def sharpen(p, w):
    """đỉnh nhọn (đáy chữ V trong M) bị cộng Minkowski ngang thành đoạn phẳng dài w → kéo dài hai mép kề tới giao điểm"""
    y0, y1 = bounds(p)[1], bounds(p)[3]; segs = []; tris = []
    for v, ps in p.segments:
        if v == 'moveTo': cur = ps[0]; start = cur; segs.append([])
        elif v in ('lineTo', 'curveTo'): segs[-1].append((v, cur, ps)); cur = ps[-1]
        elif v == 'closePath':
            if cur != start: segs[-1].append(('lineTo', cur, (start,)))
    for S_ in segs:
        n = len(S_)
        for i, (v, a, ps) in enumerate(S_):
            b = ps[-1]
            if v != 'lineTo' or abs(a[1] - b[1]) > 0.01 or abs(abs(b[0] - a[0]) - w) > 0.5 or min(a[1] - y0, y1 - a[1]) < 5: continue
            pv, pa, pps = S_[i - 1]; nv, na, nps = S_[(i + 1) % n]
            p_in = pps[-2] if pv == 'curveTo' else pa                  # hướng tới a
            p_out = nps[0] if nv == 'curveTo' else nps[-1]              # hướng rời b
            d1 = (a[0] - p_in[0], a[1] - p_in[1]); d2 = (p_out[0] - b[0], p_out[1] - b[1])
            den = d1[0]*d2[1] - d1[1]*d2[0]
            if abs(den) < 1e-9: continue
            t_ = ((b[0] - a[0])*d2[1] - (b[1] - a[1])*d2[0])/den
            if t_ <= 0 or t_ > 5*w: continue
            X = (a[0] + t_*d1[0], a[1] + t_*d1[1]); tris.append(poly([a, X, b]))
    return q2c(U(p, *tris)) if tris else p

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

def runs_y(p, y):
    """các đoạn mực (x0, x1) cắt ngang ở cao độ y"""
    s = I(p, rect(-3000, y - 0.05, 3000, y + 0.05)); out = []
    for v, ps in s.segments:
        if v == 'moveTo': cur = []
        if ps: cur += [q[0] for q in ps]
        if v == 'closePath' and cur: out.append((min(cur), max(cur)))
    return sorted(out)
def ering(c, ro, ri, rot=0):
    """vòng elip: elip ngoài ro = (rx, ry) trừ elip trong ri (cùng tâm)"""
    return D(ellipse(c, ro[0], ro[1], rot), ellipse(c, ri[0], ri[1], rot))
def ering4(x0, x1, y0, y1, wl, wr, wb, wt):
    """vòng elip dựng theo MÉP: elip ngoài nội tiếp hộp (x0, y0, x1, y1); elip trong lùi vào mỗi phía đúng độ dày thành
    (trái wl, phải wr, dưới wb, trên wt) → lòng lệch về phía thành mảnh, không phải vòng đồng tâm"""
    o = ellipse(((x0 + x1)/2, (y0 + y1)/2), (x1 - x0)/2, (y1 - y0)/2)
    ix0, ix1, iy0, iy1 = x0 + wl, x1 - wr, y0 + wb, y1 - wt
    return D(o, ellipse(((ix0 + ix1)/2, (iy0 + iy1)/2), (ix1 - ix0)/2, (iy1 - iy0)/2))
def contours_of(p):
    cs = []; cur = None
    for v, ps in p.segments:
        if v == 'moveTo': cur = pathops.Path(); cur.moveTo(*ps[0])
        elif v == 'lineTo': cur.lineTo(*ps[0])
        elif v == 'curveTo': cur.cubicTo(*ps[0], *ps[1], *ps[2])
        elif v == 'closePath': cur.close(); cs.append(cur)
    return cs
def norm_x(p): b = bounds(p); return move(p, -b[0], 0)
def scale(p, s, o=(0, 0)): return xform(p, lambda x, y: (o[0] + (x - o[0])*s, o[1] + (y - o[1])*s))

def wave(w, k):
    """sóng ~ ≈ (QA độ dày 05/11): đường sin của dấu ngã × k, bút nhóm toán — nét dày nhất 0.60 V"""
    t = T[w]; A_, kx = V._B(w, 32, 28)*k, V._B(w, 1.0, 1.14)*k
    f = lambda x: (x*kx, A_*math.sin(2*math.pi*(x + 130)/260)); df = lambda x: (kx, A_*2*math.pi/260*math.cos(2*math.pi*(x + 130)/260))
    tl_ = V.hermite([(f(x), df(x)) for x in (-130, -65, 0, 65, 130)]); kn = 0.60*t['V']/(0.87*t['Nm'])
    return V.norm(V.stroke(tl_, (t['Nm']*kn, t['mm']*kn), taper=lambda u: 0.8 + 0.2*math.sin(math.pi*u)))

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
    t = T[w]; Vv, H = t['V'], t['H']; d = t['dot']; r = d/2; tw = TW[w]
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
        """{ — dựng bằng MODULE (designer 05/11: "simplify các điểm"; bản nét bút cũ có hàng chục điểm, đầu nét gãy nhẹ):
        thân đứng 0.70 V (470 … 715); đầu trên = ¼ vòng elip (ering4: thành đứng = thân, đỉnh 0.55 thân) từ đỉnh thân cong sang
        phải tới đầu cắt đứng ở xt, đỉnh 860; mũi = ¼ vòng elip từ chân thân cong vào trục 355, đầu mũi cắt đứng mảnh;
        nửa dưới = gương quanh 355"""
        w_ = 0.85*Vv; xm, xt, x0, ym = 120.0, 240.0, 0.0, 355.0     # thân 0.85 V = giữa ngoặc tròn, ngoặc vuông 0.86 V (QA độ dày 05/11)
        sl, sr = xm - w_/2, xm + w_/2
        stem = rect(sl, 470 - 1, sr, 715 + 1)
        cyh = 715.0; ryh = 860 - cyh
        hook = I(ering4(sl, 2*xt - sl, 2*cyh - 860, 860, w_, w_, 0.55*w_, 0.55*w_), rect(sl - 1, cyh, xt, 900))
        cyt = 470.0; ryt = cyt - ym
        tip = I(ering4(2*x0 - sr, sr, ym, 2*cyt - ym, w_, w_, 0.16*w_, 0.16*w_), rect(x0, ym, sr + 1, cyt))
        top = q2c(U(stem, hook, tip))
        bot = xform(top, lambda x, y: (x, 2*ym - y))
        return q2c(U(top, bot))
    br = brace(); G['{'] = norm_x(br)
    b = bounds(G['{']); G['}'] = xform(G['{'], lambda x, y: (b[2] - x, y))
    # | : thanh đứng 0.58 V, −150 … 860 (như ngoặc)
    G['|'] = rect(0, -150, 0.58*Vv, 860)
    # ~ : ngã lớn (ngã dấu × 1.7) trên trục toán
    # ~ (QA độ dày 05/11: ngã dấu × 1.7 làm nét 116 = gấp đôi nhóm toán + − = < 60): cùng đường sin của dấu ngã × 1.7 nhưng
    # vẽ lại bằng bút nhóm toán — nét dày nhất 0.60 V
    tl = wave(w, 1.7); b = bounds(tl); G['~'] = norm_x(move(tl, 0, YC - (b[1] + b[3])/2))
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
    ro = 0.62*md + 18; rw_ = 0.66*t['Nm']   # nét vòng = đáy trăng 0.66 N dấu (QA độ dày 05/11: 0.34 V mảnh hơn mọi dấu khác ~30 %)
    G['̊'] = above(D(ellipse((0, 0), ro, ro), ellipse((0, 0), ro - rw_, ro - rw_)))
    cf = M['circumflex']; b = bounds(cf); G['̌'] = above(xform(cf, lambda x, y: (x, b[1] + b[3] - y)))
    hn = M['horn']; b = bounds(hn); G['̛'] = move(hn, -b[0] - 30, XH - 70)          # bám mép phải chữ trước
    db = M['dotbelow']; b = bounds(db); G['̣'] = move(db, -(b[0] + b[2])/2, -11.3 - V.GAP_ML - (b[3] - b[1]))
    # móc dưới (cedilla) = DẤU HỎI LẬT DỌC × 0.80 (designer 05/11: "Móc vẫn lỗi" ×3 — bản cổ chữ nhật + vòng không cùng hệ dấu):
    # đuôi dấu hỏi thành cổ đi lên chạm đáy chữ, cung tròn cuộn xuống thành móc, đầu cắt bên trái — cùng nét bút, cùng cách dựng
    # với dấu tiếng Việt (vn_punct.marks: hook)
    # × 0.80: dấu hỏi mới đuôi ngắn hơn (× 0.62 làm móc chỉ thò 57 dưới đường chân, lòng Bold bít)
    # VẼ LẠI 05/11 (designer: "đuôi móc không giống các font cùng dòng" — bản dấu hỏi lật cuộn ngược lên ở đầu trái): móc dưới
    # kiểu serif = CỔ ĐỨNG mảnh + ¾ VÒNG ELIP (ering4) cong sang phải rồi về trái, đuôi thon cắt đứng ở dưới-trái.
    # Thành phải dày 0.62 thân thường, trên / trái = nét mảnh thường hl, đáy 0.85 hl; khe & cỡ theo Regular, nở theo weight.
    # Gốc: tâm cổ x = 0, đỉnh cổ y = 15 (đáy chữ ở −25 sau khi đặt: Ç ç đặt ở b[1] + 25)
    hl_ = 40.4 + 12.7*tw; vl_ = 101.8 + 22.6*tw; nw = 1.1*hl_
    Wc, Hc = 165 + 40*tw, 130 + 10*tw; y1c = -65.0
    # mép trái lòng = mép trái cổ: cổ đi thẳng xuống thành mép lòng, vòng mở hẳn về trái (bỏ cả thành trái);
    # đuôi = thành đáy (mép trên phẳng ở đáy lòng), cắt đứng dưới mép trái cổ
    x0c = -nw/2 - hl_; cxc = x0c + Wc/2; cyc = y1c - Hc/2
    ringc = ering4(x0c, x0c + Wc, y1c - Hc, y1c, hl_, 0.62*vl_, 0.85*hl_, hl_)
    ringc = I(ringc, rect(-nw/2, -2000, 2000, 2000))          # đuôi cắt đứng thẳng hàng mép trái cổ
    # mở hẳn: bỏ mọi mực bên trái tâm lòng trong khoảng cao của lòng (sót mép thành trái cong làm vòng khép kín)
    iy0, iy1 = y1c - Hc + 0.85*hl_, y1c - hl_; cxi_ = (x0c + hl_ + x0c + Wc - 0.62*vl_)/2
    ringc = D(ringc, rect(-2000, iy0, cxi_, iy1))
    G['\u0327'] = q2c(U(ringc, rect(-nw/2, y1c - 0.5*hl_, nw/2, 15)))
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
    # ™ (designer 05/11 "kiểm tra lỗi của glyph này"): làm đậm ĐỀU mọi phía (0.09 V) làm nét mảnh dày gấp đôi → chéo mảnh của M
    # nặng gần bằng thân, mép chéo hết song song. Dựng lại: T M của master BOLD thu 0.42 (thân 0.42 × V_B ≈ 0.57 V Regular, giữ
    # nguyên tương phản bút dẹt của Bold), weight đậm hơn thì chỉ làm dày THEO PHƯƠNG NGANG (cộng Minkowski với đoạn ngang):
    # thân dày theo tỉ lệ V_w / V_R, nét ngang giữ nguyên, mép chéo song song, loe giữ đầu nhọn trên đường cap / chân
    def sup(ch, s=0.42):
        g = scale(V.letter(S, ch, 'Bold'), s)
        dx = 0.5*s*T['Bold']['V']*(Vv/T['Regular']['V'] - 1)
        if dx > 0.05: g = sharpen(xdilate(g, dx), 2*dx)
        b = bounds(g); return move(g, -b[0], 700 - b[3])
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
    lo = I(pc, rect(b[2] - 2*(118 + 8*tw) - 5, -50, b[2] + 5, 330))
    G['‰'] = U(pc, move(lo, 2*(118 + 8*tw) + 0.35*Vv, 0))
    # § (designer 05/11: "Check lỗi" ×2): S HOA của designer thu nhỏ (ngang 0.62, dọc 0.52), bù nét tới sống ≈ 0.85 V; S dưới =
    # S trên xoay 180°, chồng ĐÚNG MỘT BỤNG → bụng dưới S trên + bụng trên S dưới ghép thành vòng kín; cao ≈ −40 … 700
    S0 = V.letter(S, 'S', w); b = bounds(S0); S0 = move(S0, -b[0], -b[1])
    S0 = xform(S0, lambda x, y: (x*0.64, y*0.58)); b = bounds(S0)
    sp_ = runs_y(S0, (b[1] + b[3])/2); spine = max(r_[1] - r_[0] for r_ in sp_)
    # QA độ dày 05/11: S thu 0.64 × 0.58 còn nét ~0.62 V (đo trục giữa: § 66 so với ( ) [ ] { } ! € 88) — embolden mỗi phía
    # 0.115 V → nét chính 0.85 V, cùng nhóm ngoặc (đo "spine" theo run ngang cũ ăn cả độ nghiêng sống nên không nở)
    S0 = embolden(S0, 0.115*Vv); b = bounds(S0); hs = b[3] - b[1]
    S0 = move(S0, -b[0], -b[1]); b = bounds(S0)
    # bỏ ĐẦU NÉT DƯỚI của S (góc dưới-trái) trước khi chồng: đầu này nằm trong vòng giữa và lòi ra hai bên (designer 05/11:
    # "vẫn lỗi dư nét"); chỗ đó do sống của S kia khép lại
    S0 = q2c(D(S0, rect(-100, -100, b[0] + 0.46*(b[2] - b[0]), b[1] + 0.43*hs)))
    rot = xform(S0, lambda x, y: (b[2] - x, b[3] - y)); ov = 0.47*hs
    sec = q2c(U(move(S0, 0, hs - ov), rot)); bb = bounds(sec)
    # lòng vòng giữa = MỘT ELIP nội tiếp hộp của lòng (designer 05/11: "lỗi vòng khuyết trong" — góc nhát cắt ló vào lòng):
    # lấp kín lòng rồi khoét lại bằng elip
    cs = []; cur = None
    for v, ps in sec.segments:
        if v == 'moveTo': cur = pathops.Path(); cur.moveTo(*ps[0])
        elif v == 'lineTo': cur.lineTo(*ps[0])
        elif v == 'curveTo': cur.cubicTo(*ps[0], *ps[1], *ps[2])
        elif v == 'closePath': cur.close(); cs.append(cur)
    mid = (bb[1] + bb[3])/2
    holes = [c for c in cs if bounds(c)[1] < mid < bounds(c)[3] and (bounds(c)[2] - bounds(c)[0]) < 0.8*(bb[2] - bb[0])]
    if holes:
        hb = bounds(min(holes, key=lambda c: (bounds(c)[2] - bounds(c)[0])*(bounds(c)[3] - bounds(c)[1])))
        fill = pathops.Path(); fill.addPath(min(holes, key=lambda c: (bounds(c)[2] - bounds(c)[0])*(bounds(c)[3] - bounds(c)[1])))
        fill = pathops.op(fill, fill, pathops.PathOp.UNION)
        sec = q2c(D(U(sec, fill), ellipse(((hb[0] + hb[2])/2, (hb[1] + hb[3])/2), (hb[2] - hb[0])/2, (hb[3] - hb[1])/2)))
    G['§'] = move(sec, 0, 330 - (bb[1] + bb[3])/2)
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
    # £ — VẼ LẠI lần 2 (designer 05/11: "vẽ lại ký hiệu Bảng anh cho giống các font khác nhưng đồng bộ concept"): cấu trúc £ của
    # font serif (móc trên cong phải · thân cong về trái ở chân vào thanh đáy · thanh giữa · thanh đáy vểnh đầu phải) dựng bằng
    # MODULE của Đìzai:
    #   móc trên  = nửa trên vòng elip (ering4: thành trái = thân, đỉnh 0.55 V, phải 0.5 thân), cắt đứng như đầu nét trên C;
    #   thân      = 0.9 V; chân thân = ¼ vòng elip (thành phải = thân, đáy = nét mảnh) cong sang trái, liền tiếp tuyến vào đáy;
    #   thanh đáy = nét mảnh H, đầu phải = module đầu tay dưới E (mép đứng 93 rồi cong lõm vào, tay nắm 0.69);
    #   thanh giữa= nét mảnh H ở 300, đầu phải cắt xiên như thanh giữa E (dài thêm 0.17 H ở mép dưới)
    sw = 0.9*Vv; hb = H; sx0 = 196.0; sx1 = sx0 + sw
    ytop = 712.0; xcut = sx0 + 0.86*(1.0*560 - sx0)*0.62 + 60
    hook = I(ering4(sx0, 560.0, 380.0, ytop, sw, 0.5*sw, 0.4*sw, 0.55*Vv), U(rect(sx0 - 1, 546.0, xcut, 900), rect(sx0 - 1, 380, sx1, 547)))
    yb = 170.0                                                     # chân thân bắt đầu cong ở cao này
    rxq = 150.0; cxq = sx1 - rxq
    foot = I(D(ellipse((cxq, yb), rxq, yb), ellipse((cxq, yb), rxq - sw, yb - hb)), rect(cxq, -1, sx1 + 1, yb + 1))   # ¼ vòng: phải = thân, đáy = mảnh
    stem = rect(sx0, yb, sx1, 547.0)
    xe = sx1 + 300.0; eh = 93.0
    # đầu phải = đúng hai cubic của đầu tay dưới E (Figma 6:924: …L99 233 C109.3 233 119.3 229 126.7 222 C129 219.8 130.7 216.9 132 214
    # L132 247), quy về đơn vị font (k = 700/247), đáy tay dày = nét mảnh của weight
    kE = 700/247.0; ey = lambda yf: hb + (14 - (247 - yf))*0 + ((247 - yf) - 14)*kE
    base = U(rect(cxq - 70, 0, xe - 33*kE + 1, hb),
             V.P([('M', (xe - 33*kE, 0)), ('L', (xe, 0)), ('L', (xe, ey(214))),
                  ('C', (xe - 1.33*kE, ey(216.94)), (xe - 2.97*kE, ey(219.76)), (xe - 5.31*kE, ey(221.98))),
                  ('C', (xe - 12.73*kE, ey(229.01)), (xe - 22.68*kE, hb), (xe - 33*kE, hb)), ('Z',)]))
    ym = 300.0; xl = sx0 - 105; xr = sx1 + 120
    bar = poly([(xl, ym), (xr, ym), (xr + 0.17*hb*2.0, ym + hb), (xl, ym + hb)])
    G['£'] = norm_x(q2c(U(hook, stem, foot, base, bar)))
    # ¥ : Y hoa + hai thanh 0.70 H, khe 60 (luật ¥ €)
    yy = V.letter(S, 'Y', w); b = bounds(yy); bh = 0.70*H*1.4
    G['¥'] = U(yy, rect(b[0] + 0.12*(b[2] - b[0]), 300, b[2] - 0.12*(b[2] - b[0]), 300 + bh),
               rect(b[0] + 0.12*(b[2] - b[0]), 300 - 60 - bh, b[2] - 0.12*(b[2] - b[0]), 300 - 60))
    # ¢ : c thường + nét đứng mảnh 1.1 H xuyên qua, vươn ±100
    c0 = ref_outline(L[f'c-{w}']); b = bounds(c0); xcn = (b[0] + b[2])/2 + 10
    G['¢'] = U(c0, rect(xcn - 0.55*H, -100, xcn + 0.55*H, XH + 110))
    # µ : u thường, thân trái kéo xuống descender (cắt bằng)
    u0 = ref_outline(L[f'u-{w}']); s0_, s1_ = runs_y(u0, 300)[0]            # mép thân trái đo đúng (lỗi bậc: "Check lỗi")
    # thân trái µ THẲNG từ descender lên 300 (designer 05/11: "Lỗi glyph" — thân u phình ra ở chân, đoạn kéo xuống lệch bậc):
    # bỏ phần u bên trái mép thân dưới 300, thêm thân thẳng s0 … s1
    G['µ'] = q2c(U(D(u0, rect(-500, -500, s0_, 300)), rect(s0_, DESC, s1_, 300)))
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
          'ring': c0(D(ellipse((0, 0), 0.62*md + 18, 0.62*md + 18), ellipse((0, 0), 0.62*md + 18 - 0.66*t['Nm'], 0.62*md + 18 - 0.66*t['Nm']))),
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
        # cổ móc đặt đúng điểm THẤP NHẤT của đáy chữ (đáy nằm ngang, cổ đứng → góc rõ; đặt lệch thì mép cổ gặp đường cong ở góc
        # nông, thành chỗ gãy — QA 05/11)
        b = bounds(p); xs_ = [b[0] + k*(b[2] - b[0])/200 for k in range(201)]
        xlow = min(xs_, key=lambda x: min([y0 for y0, _ in [(r_[0], 0) for r_ in [(bounds(I(p, rect(x - 0.3, -500, x + 0.3, 2000)))[1],)] if r_]] or [9e9]))
        G[ch] = U(p, move(ced, xlow, b[1] + 25))
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
    # góc trên-trái (designer 05/11: "lỗi glyph góc trái"): đỉnh A (vượt 712) nhô trên thanh E và loe trái đầu thân E chìa ra
    # ngoài nét chéo → cắt cả khối ở mặt trên thanh E (cap 700) và theo đúng mép ngoài nét chéo trái của A kéo dài (phần trên 400)
    ae = U(left, move(E_, apx - 0.15*Vv - ex0, 0))
    (xa, _), (xb, _) = runs_y(A_, 300)[0], runs_y(A_, 600)[0]
    dx_ = (xb - xa)/300; cut_l = poly([(xa + dx_*(400 - 300), 400), (xa + dx_*(1200 - 300), 1200), (3000, 1200), (3000, 400)])
    # lòng (designer 05/11: "lỗi vòng khuyết"): đỉnh lòng A nằm trái thân E → còn đoạn xiên ngắn (mép trong chéo phải A) từ đỉnh
    # lòng xuống thân. Lòng dựng lại = tam giác: mép trong chéo trái A × mép trái thân E × mặt trên thanh A — một đỉnh nhọn ở thân
    cA = min(contours_of(A_), key=lambda c: abs(c.area)); cb_ = bounds(cA); ybar = cb_[1]
    (_, xi0), (_, xi1) = runs_y(A_, ybar + 20)[0], runs_y(A_, ybar + 220)[0]
    sl = (xi1 - xi0)/200; exl = apx - 0.15*Vv; xil = lambda y: xi0 + sl*(y - ybar - 20)
    ytop = ybar + 20 + (exl - xi0)/sl
    ae = D(ae, poly([(xil(ybar), ybar), (exl + 1, ybar), (exl + 1, ytop), (xil(ytop) , ytop)]))
    G['Æ'] = I(I(ae, U(rect(-100, -100, 3000, 400.5), cut_l)), rect(-100, -100, 3000, bounds(I(E_, rect(-100, 600, 2000, 900)))[3]))
    # Œ: O cắt ở 0.62 bề ngang + E có thân trùng chỗ cắt
    O_ = V.letter(S, 'O', w); ob = bounds(O_); xcut = ob[0] + 0.60*(ob[2] - ob[0])
    G['Œ'] = U(I(O_, rect(-100, -100, xcut, 800)), move(E_, xcut - Vv - ex0, 0))
    # æ: a + e chồng — vách trái e trùng thân a; œ: o + e chồng một vách
    a_ = lw('a'); e_ = lw('e'); o_ = lw('o'); abx = bounds(a_); ebx = bounds(e_); obx = bounds(o_)
    vl = 101.8 + 22.6*TW[w]                                        # thân chữ thường của weight (phần chồng theo chữ thường, không theo V hoa)
    G['æ'] = U(a_, move(e_, abx[2] - 0.62*vl - ebx[0] - 25, 0))
    G['œ'] = U(o_, move(e_, obx[2] - 0.80*vl - ebx[0], 0))
    # Þ: thân P cao trọn cap, bụng P hạ xuống 140 (giữa thân); þ: p có thân vươn lên ascender (đỉnh thân b)
    P_ = V.letter(S, 'P', w); pb = bounds(P_); st = I(P_, rect(-100, 299.9, 2000, 300.1)); sr = sorted(set(round(q[0], 1) for _, ps in st.segments for q in ps))
    s1 = sr[1]; stem = I(P_, rect(-100, -100, s1 + 0.5, 800)); bowl = I(P_, rect(s1 - 2, 300, 2000, 800))
    G['Þ'] = U(stem, move(bowl, 0, -150))
    p_ = lw('p'); b_ = lw('b'); bb = bounds(b_); pbx = bounds(p_)
    bs0, bs1 = runs_y(b_, 600)[0]; ps0, ps1 = runs_y(p_, -100)[0]      # chỉ thân b phía trên x-height, canh theo mép thân p
    # bỏ loe đỉnh-trái của thân p (ở x-height) — thân b nối tiếp lên nên loe này thành mấu thừa (designer 05/11: ảnh þ)
    G['þ'] = q2c(U(D(p_, rect(-500, 300, ps0, 2000)), move(I(b_, rect(-100, 300, bs1 + 0.3, 800)), ps0 - bs0, 0)))
    # ð: o + cổ cong (nét bút) từ vai phải lên ascender, cắt chéo bằng thanh nhỏ
    nb = (t['N']*0.9, t['m']*1.1)
    ow = obx[2] - obx[0]
    # ð — VẼ LẠI bằng module: cổ = một đoạn VÒNG ELIP đi tiếp thành phải của o — elip ngoài có điểm cực phải trùng điểm cực
    # phải của o (cùng cao độ, tiếp tuyến đứng → mép trơn liền), đỉnh ở 712; elip trong lùi đúng thành o ở bên phải, đỉnh mảnh
    # 0.5 H; giữ phần trên cao độ cực phải, đầu trên-trái cắt đứng
    ys_ = [obx[1] + k*(obx[3] - obx[1])/80 for k in range(1, 80)]
    yr = max(ys_, key=lambda y: runs_y(o_, y)[-1][1]); xr = runs_y(o_, yr)[-1][1]; wl = runs_y(o_, yr)[-1][1] - runs_y(o_, yr)[-1][0]
    cxn = obx[0] + 0.50*ow; Rx, Ry = xr - cxn, 712 - yr
    # đồng bộ độ dày (designer 05/11: "kiểm tra đồng bộ độ dày"): ngọn cổ = nét mảnh H; lòng o giữ nguyên (trừ lòng o khỏi cổ)
    # → chỗ cổ nhập vòng dày đúng thành o (trước: 137 / Bold 165 so với thành o 101 / 124; ngọn 22 / 36 so với H 40 / 53)
    hl = 40.4 + 12.7*TW[w]                           # nét mảnh chữ thường (ARCH_TOP)
    neck = I(ering((cxn, yr), (Rx, Ry), (Rx - 0.75*wl, Ry - hl)), rect(cxn - 35, yr, 2000, 2000))
    oc = [c for c in contours_of(o_)]; outer_o = max(oc, key=lambda c: (bounds(c)[2] - bounds(c)[0])*(bounds(c)[3] - bounds(c)[1]))
    counter_o = D(pathops.op(outer_o, outer_o, pathops.PathOp.UNION), o_)
    eth = U(o_, D(neck, counter_o)); nx_ = cxn + 0.62*Rx
    G['ð'] = U(eth, poly([(nx_ - 110, 575), (nx_ + 85, 615), (nx_ + 85, 615 + hl), (nx_ - 110, 575 + hl)]))
    # ß: thân l thường (đỉnh vòm sang phải) + nét bút: vòm trên → eo → bụng dưới về chân
    l_ = lw('l'); lb = bounds(l_); lsr = I(l_, rect(-100, 299.9, 2000, 300.1)); lx = sorted(set(round(q[0], 1) for _, ps in lsr.segments for q in ps))
    # ß — VẼ LẠI bằng module (như B): thân l (cả chân loe) tới 560 + VÒNG TRÊN kín + VÒNG DƯỚI mở dưới-trái; vòng dựng theo
    # MÉP (ering4): thành phải dày như thân, thành trái chìm trong thân (mảnh), trên / dưới mảnh 0.5 H
    s0l, s1l = runs_y(l_, 300)[0]; vth = s1l - s0l
    # vòng trên: mép trái trùng mép trái thân, thành trái = thân → thân đi thẳng lên rồi uốn liền vào vòng (không vai vuông)
    cyu = (425 + 712)/2
    stem = I(l_, rect(-100, -100, 2000, cyu))
    up = I(ering4(s0l, s1l + 255, 425, 712, vth, 0.84*vth, 0.42*H, 0.5*H), rect(s0l - 1, 400, 2000, 2000))
    # vòng dưới: đỉnh trùng thành đáy của vòng trên (chung chỗ thắt), chỉ giữ nửa phải phía trên tâm → đầu cắt nằm gọn trong thành
    # đáy vòng trên (designer 05/11: "Regular lỗi" — đầu cắt lộ ra trong lòng); đầu dưới-trái cắt ở chỗ vòng đủ dày
    # tâm ngang vòng dưới = tâm vòng trên: đỉnh vòng dưới (ngoài / trong) trùng đúng thành đáy vòng trên, cùng tiếp tuyến ngang
    # → chỗ thắt liền, không bậc
    cxu = (s0l + s1l + 255)/2; xr_ = s1l + 280; y1l = 425 + 0.42*H; cyl = (y1l - 11)/2
    # lòng vòng dưới lệch trái (thành trái 0.35, phải 0.92 thân) → đỉnh lòng ở cxi, không phải cxu. Cắt / nối eo tại cxi để
    # mép đáy eo chạy ngang rồi vào đúng tiếp tuyến ngang ở đỉnh lòng (designer 05/11: "vẫn dư nét dưới bụng" — cắt ở cxu để lại bậc)
    cxi = cxu - 0.285*vth
    # đầu cắt dưới-trái cách mép loe chân thân một khe cố định theo Regular (designer 05/11: "glyph dưới bị dính" — Bold chỉ còn 8)
    xcut = runs_y(l_, 1)[0][1] + 50
    lo = I(ering4(2*cxu - xr_, xr_, -11, y1l, 0.35*vth, 0.92*vth, 0.5*H, 0.42*H),
           U(rect(cxi, cyl, 2000, 2000), rect(xcut, -400, 2000, cyl + 1)))
    # chỗ thắt (designer 05/11: "còn dư lỗi glyph" — cung đáy vòng trên mỏng dần chạm thân thành mũi nhọn): đoạn từ thân tới đáy
    # vòng là thanh ngang đúng bề dày thành đáy (0.42 H), tiếp tuyến ngang ở đáy vòng → liền; góc gặp thân vuông
    waist = rect(s1l - 1, 425, cxi + 1, 425 + 0.42*H)
    G['ß'] = q2c(U(stem, up, lo, waist))
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
    tl = wave(w, 1.7*0.78); tb_ = bounds(tl); tl = move(tl, 0, YC_ - (tb_[1] + tb_[3])/2)   # ≈: sóng nhỏ hơn, cùng nét ~
    G['≈'] = U(move(tl, 0, 92), move(tl, 0, -92))
    G['¬'] = U(rect(0, YC_ - mh/2, ms, YC_ + mh/2), rect(ms - 0.62*Vv, YC_ - 200, ms, YC_ + mh/2))
    G['¦'] = U(rect(0, -150, 0.58*Vv, 300), rect(0, 410, 0.58*Vv, 860))
    q1 = P["'"]; qb = bounds(q1); sh = math.tan(math.radians(14))
    pr = xform(q1, lambda x, y: (x + (y - qb[1])*sh, y)); G['′'] = pr
    G['″'] = U(pr, move(pr, (bounds(pr)[2] - bounds(pr)[0]) + 0.35*Vv, 0))
    return G

def build():
    S = V.load(); L = lower_src(); out = {}
    for w in WEIGHTS:
        for ch, p in build_w(S, L, w).items():
            p = q2c(p)
            if ch not in COMB: p = norm_x(p)
            out[f'{ch}-{w}'] = [V.to_d(p)]
    json.dump(out, open(os.path.join(HERE, 'designer_D.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('ok', len(out))

if __name__ == '__main__':
    build()
