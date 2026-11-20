#!/usr/bin/env python3
"""An Nam Golden — họ chữ phát triển từ AnNam Serif (designer 19–20/11).
    python3 tools/construct/golden/golden.py      (sau build.py + compat_masters của AnNam Serif) → out/golden/outlines.json

Luật (đánh số G*), áp lên outline Regular + Bold đã ghép cấu trúc của AnNam Serif; Medium / SemiBold = nội suy ĐÚNG (1/3, 2/3)
như bản gốc (cùng cấu trúc điểm → master variable tương thích):
  G1  x-height 495 → 535 (designer 20/11: "nâng x-height lên, giữ nguyên bề ngang chữ"), chỉ chữ thường (+ chữ ghép, dấu tổ hợp):
      - vùng chữ x (0 … 503.4, gồm đường vượt) giãn đứng × 535/495; dưới 0 (phần xuống, vượt đáy) giữ; bề ngang giữ nguyên;
      - chữ có phần vươn (b d h k l þ): đầu thân giữ 699 — chỉ đoạn thân thẳng 503.4 → 628.9 co lại, loe đầu thân giữ hình;
        đ: thanh ngang giữ dày, dời theo tâm; f: móc giữ hình, cao thêm 20; ß: phần trên co đều;
      - chữ x (a c e … t, ơ ư, ð): phần trên x-height (đầu t, sừng, …) dời lên nguyên khối Δ = 40.7;
      - contour nằm trọn trên x-height (dấu thanh, dấu mũ, chấm i j) dời lên Δ — khoảng dấu – chữ giữ nguyên.
  G3  chân loe rộng hơn 30 %, thấp hơn (× 0.85) — vuốt nhọn: loe = đoạn cong nối thân (đoạn thẳng dài) với mặt chân / đỉnh
      (đoạn ngang). Gốc C = giao đường thân × đường chân: điểm nối thân + tay nắm của nó co × 0.85 về C (trượt trên đường thân,
      tiếp tuyến giữ — liền mạch); phía chân: rộng × 1.3 theo đường chân, cao × 0.85; áp cho mọi loe (chân, đỉnh thân, chéo).
  G4  v x y (+ ý ỳ ỷ ỹ ỵ ÿ) rộng thêm × 1.08 (= 535/495, góc chéo như AnNam Serif) quanh tâm; mọi nét thu lại × 1/1.08 theo
      luật G2 (dời mép theo pháp tuyến) → nét giữ bề dày; dấu giữ hình.
  G2  nét mảnh còn 80 % (thanh ngang, chéo mảnh, vòng mảnh, khớp mảnh — chữ hoa và thường): mỗi mép dời vào
      δ = 0.1·w (w = bề dày nét đo vuông góc tại đó, chỉ khi mép đối diện song song ngược chiều ±50° — là một NÉT, không phải mũi
      nhọn); w ≤ 1.4 × nét mảnh chuẩn: đủ 0.1·w, giảm tuyến tính về 0 ở 0.7 × thân; thân dày giữ nguyên. Điểm neo dời theo hai
      pháp tuyến của hai đoạn kề (góc: giải hai ràng buộc, trơn: theo pháp tuyến chung); tay nắm đi cùng điểm neo. Dấu, chấm giữ.
"""
import json, os, re, sys, unicodedata, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..', '..')
SRC = os.path.join(ROOT, 'out', 'construct'); OUT = os.environ.get('GOLDEN_OUT') or os.path.join(ROOT, 'out', 'golden')
TW = {'Medium': 1/3, 'SemiBold': 2/3}

XH0, XH1 = 495.0, 535.0
S = XH1/XH0; OVT = 503.4; D = OVT*(S - 1)          # đỉnh vùng x (gồm vượt) và độ dời phía trên
ASC_LET = set('bdhklþ'); TOP_FLARE = 628.9

# ---------- đường: chuỗi 'M x yL…C…Z' ↔ danh sách contour [[lệnh, [điểm…]]…] ----------
TOK = re.compile(r'[MLCZ]|-?\d+(?:\.\d+)?(?:e-?\d+)?')
def parse(d):
    t = TOK.findall(d); i = 0; out = []; cur = None
    while i < len(t):
        c = t[i]; i += 1
        n = {'M': 1, 'L': 1, 'C': 3, 'Z': 0}[c]
        pts = [[float(t[i + 2*k]), float(t[i + 2*k + 1])] for k in range(n)]; i += 2*n
        if c == 'M': cur = [['M', pts]]; out.append(cur)
        elif c == 'Z':
            last = cur[-1][1][-1] if len(cur) > 1 else None
            if last is not None and last == cur[0][1][0]: cur[-1][1][-1] = cur[0][1][0]   # điểm cuối trùng điểm đầu: CÙNG một
            cur.append(['Z', []])                                                          # đối tượng — mọi luật dời cả hai
        else: cur.append([c, pts])
    return out
def fmt(cs):
    s = ''
    for c in cs:
        for cmd, pts in c: s += cmd + ' '.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    return s
def pts_of(c):
    out, seen = [], set()
    for _, ps in c:
        for p in ps:
            if id(p) not in seen: seen.add(id(p)); out.append(p)
    return out

# ---------- G1 ----------
def pwl(knots):
    def f(y):
        if y <= OVT: return y*S if y > 0 else y
        for (a0, b0), (a1, b1) in zip(knots, knots[1:]):
            if y <= a1: return b0 + (y - a0)*(b1 - b0)/(a1 - a0)
        a, b = knots[-1]; return y + (b - a)
    return f
MAP_X = pwl([(OVT, OVT + D)])                                   # dời lên nguyên khối Δ
MAP_ASC = pwl([(OVT, OVT + D), (TOP_FLARE, TOP_FLARE)])
MAP = {'x': MAP_X, 'asc': MAP_ASC,
       'đ': pwl([(OVT, OVT + D), (580, 593.7), (620, 633.7), (649, 649)]),
       'f': pwl([(OVT, OVT + D), (543, 563)]),
       'ß': pwl([(OVT, OVT + D), (712, 712)])}
LIG = {'ﬀ': 'ff', '': 'ft', '': 'tf', '': 'tt'}
def kind(ch):
    b = unicodedata.normalize('NFD', ch)[0]
    if b in ASC_LET: return 'asc'
    if ch in MAP: return ch
    return 'x'
def lower_set(chars):
    return [c for c in chars if unicodedata.category(c) in ('Ll', 'Mn') or c in LIG]

def g1(d, ch):
    cs = parse(d)
    if ch in LIG:                                                # chữ ghép: tách hai phần theo khe lớn nhất của điểm phía trên 560
        xs = sorted(x for c in cs for x, y in pts_of(c) if y > 560)
        gap = max(range(len(xs) - 1), key=lambda i: xs[i + 1] - xs[i]); split = (xs[gap] + xs[gap + 1])/2
        fa, fb = (MAP[kind(LIG[ch][0])] if kind(LIG[ch][0]) in MAP else MAP_X), (MAP[kind(LIG[ch][1])] if kind(LIG[ch][1]) in MAP else MAP_X)
        m = lambda x, y: fa(y) if x < split else fb(y)
    else:
        f = MAP[kind(ch)]; m = lambda x, y: f(y)
    for c in cs:
        P = pts_of(c)
        if min(y for _, y in P) > OVT + 3:                      # dấu / chấm: dời nguyên khối
            for p in P: p[1] += D
        else:
            for p in P: p[1] = m(p[0], p[1])
    return fmt(cs)

# ---------- hình học chung ----------
import math
def bz(p0, p1, p2, p3, t):
    u = 1 - t; return [u**3*p0[i] + 3*u*u*t*p1[i] + 3*u*t*t*p2[i] + t**3*p3[i] for i in (0, 1)]
def segs(c):
    """contour → danh sách đoạn [(loại, [P0, …, Pn])] (điểm là list tham chiếu: sửa tại chỗ)"""
    out = []; cur = c[0][1][0]; start = cur
    for cmd, ps in c[1:]:
        if cmd == 'L': out.append(('L', [cur, ps[0]])); cur = ps[0]
        elif cmd == 'C': out.append(('C', [cur, ps[0], ps[1], ps[2]])); cur = ps[2]
        elif cmd == 'Z':
            if math.dist(cur, start) > 1e-6: out.append(('Z', [cur, start]))
    return out
def polys(cs):
    P = []
    for c in cs:
        pl = []
        for k, q in segs(c):
            if k == 'C': pl += [bz(*q, i/16) for i in range(16)]
            else: pl.append(q[0])
        P.append(pl)
    return P
def inside(pt, P):
    x, y = pt; r = False
    for pl in P:
        n = len(pl)
        for i in range(n):
            (x1, y1), (x2, y2) = pl[i - 1], pl[i]
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1)*(x2 - x1)/(y2 - y1): r = not r
    return r
def ray(pt, d, P, tmin=0.8):
    """khoảng cách tới mép đầu tiên theo hướng d + pháp tuyến (chưa định hướng) của mép đó"""
    best = None
    for pl in P:
        n = len(pl)
        for i in range(n):
            (x1, y1), (x2, y2) = pl[i - 1], pl[i]; ex, ey = x2 - x1, y2 - y1
            den = d[0]*ey - d[1]*ex
            if abs(den) < 1e-12: continue
            t = ((x1 - pt[0])*ey - (y1 - pt[1])*ex)/den; s_ = ((x1 - pt[0])*d[1] - (y1 - pt[1])*d[0])/den
            if t > tmin and 0 <= s_ <= 1 and (best is None or t < best[0]):
                L = math.hypot(ex, ey) or 1; best = (t, (ey/L, -ex/L))
    return best
def unit(v):
    L = math.hypot(*v); return (v[0]/L, v[1]/L) if L > 1e-9 else None
def tan_end(k, q, at_start):
    """tiếp tuyến đơn vị theo chiều đi của đoạn, tại đầu / cuối"""
    if k != 'C': return unit((q[1][0] - q[0][0], q[1][1] - q[0][1]))
    if at_start:
        for h in (q[1], q[2], q[3]):
            u = unit((h[0] - q[0][0], h[1] - q[0][1]))
            if u: return u
    else:
        for h in (q[2], q[1], q[0]):
            u = unit((q[3][0] - h[0], q[3][1] - h[1]))
            if u: return u
    return None

# ---------- G3 chân loe ----------
FLARE_KX, FLARE_KY = 1.3, 0.85   # designer 20/11: loe rộng hơn 30 %; "giảm chiều cao của loe để cảm giác vuốt nhọn hơn" → cao × 0.85
FLSEG = set()                   # (id điểm đầu, id điểm cuối) của các cung loe — luật nét mảnh không bẻ hình loe
def g3(cs):
    n_fl = 0
    for c in cs:
        S_ = segs(c); n = len(S_)
        for i in range(n):
            k, q = S_[i]
            if k != 'C': continue
            for rev in (False, True):                          # loe có thể đi thân → chân hoặc chân → thân
                stem = S_[(i - 1) % n] if not rev else S_[(i + 1) % n]
                nx1 = S_[(i + 1) % n] if not rev else S_[(i - 1) % n]
                nx2 = S_[(i + 2) % n] if not rev else S_[(i - 2) % n]
                if stem[0] == 'C' or nx1[0] == 'C': continue
                end = q[3] if not rev else q[0]                   # đầu loe phía chân
                hor = lambda sg: abs(sg[1][0][1] - sg[1][1][1]) < 0.5 and math.dist(*sg[1]) >= 40
                if hor(nx1): extra = []                           # loe chạm thẳng mặt chân
                elif nx2[0] != 'C' and math.dist(*nx1[1]) <= 30 and hor(nx2):
                    extra = [nx1[1][1] if not rev else nx1[1][0]] # đoạn ngắn rồi mới tới mặt chân
                else: continue
                sa, sb = stem[1]
                if math.dist(sa, sb) < 60: continue
                K = extra[0] if extra else end; Z = K[1]
                Sp = q[0] if not rev else q[3]
                if abs(Sp[1] - Z) > 140 or abs(Sp[1] - Z) < 20: continue
                td = unit((sb[0] - sa[0], sb[1] - sa[1]))
                tc = tan_end(k, q, not rev)
                if not td or not tc or abs(td[0]*tc[1] - td[1]*tc[0]) > 0.03: continue   # loe liền tiếp tuyến với thân
                if abs(td[1]) < 0.5: continue                       # thân phải đứng / chéo, không nằm ngang
                cx = Sp[0] + (Z - Sp[1])*td[0]/td[1]; C0 = (cx, Z)    # giao đường thân × đường chân
                sside = [q[0], q[1]] if not rev else [q[3], q[2]]      # điểm nối thân + tay nắm của nó: trượt trên đường thân
                fside = [q[2], q[3]] if not rev else [q[1], q[0]]
                for p in sside:
                    p[0] = C0[0] + (p[0] - C0[0])*FLARE_KY; p[1] = C0[1] + (p[1] - C0[1])*FLARE_KY
                for p in fside + extra:                                 # phía chân: rộng × KX, cao × KY
                    p[0] = C0[0] + (p[0] - C0[0])*FLARE_KX; p[1] = Z + (p[1] - Z)*FLARE_KY
                FLSEG.add((id(q[0]), id(q[3]))); n_fl += 1
    return n_fl

# ---------- G2b lòng vòm n m h / lòng đáy u: dịch nguyên khối (designer 20/11: "đường cong bụng trong chữ u, m, n không tự nhiên") ----------
ARCH = set('nmhuµ')
ARCH_T = {'Regular': 32.0, 'Bold': 45.0}       # = RING_T (G8): bề dày đỉnh vòm sau khi dịch
def arch_thin(cs, w):
    """chuỗi đoạn cong giữa hai đoạn thân THẲNG ĐỨNG, phía mực nằm ngoài cung (lòng vòm / lòng đáy u): dời đứng cả chuỗi
    δ = (1 − THIN_R)·bề dày đỉnh — dáng cung giữ nguyên, điểm nối trượt trên thân. Trả về id các điểm đã dời (G2 bỏ qua)."""
    P = polys(cs); done = set()
    for c in cs:
        S_ = segs(c); n = len(S_)
        vert = lambda sg: sg[0] != 'C' and abs(sg[1][0][0] - sg[1][1][0]) < 0.5 and abs(sg[1][0][1] - sg[1][1][1]) > 30
        i = 0
        while i < n:
            if vert(S_[i]) and S_[(i + 1) % n][0] == 'C':
                j = i + 1; chain = []
                while S_[j % n][0] == 'C' and len(chain) < n: chain.append(S_[j % n]); j += 1
                if vert(S_[j % n]) and chain:
                    pts = []
                    for _, q in chain:
                        for p_ in q:
                            if all(p_ is not r for r in pts): pts.append(p_)
                    cv = [bz(*q, t_/24) for _, q in chain for t_ in range(25)]                # điểm TRÊN cung (không lấy tay nắm)
                    ys = [p_[1] for p_ in cv]; top, bot = max(ys), min(ys)
                    ends = (chain[0][1][0][1], chain[-1][1][3][1])
                    if top > max(ends) + 20:   pk = max(cv, key=lambda p_: p_[1]); sg = 1      # vòm: đỉnh cao hơn hai đầu
                    elif bot < min(ends) - 20: pk = min(cv, key=lambda p_: p_[1]); sg = -1    # đáy u
                    else: i = j; continue
                    if inside((pk[0], pk[1] + sg*2), P):                                       # mực ở phía ngoài cung → là lòng
                        h = ray(pk, (0, sg), P)
                        if h:
                            dlt = h[0] - ARCH_T[w]                                  # đỉnh vòm / đáy u = đúng chuẩn nét mảnh
                            for p_ in pts: p_[1] += sg*dlt
                            done |= {id(p_) for p_ in pts}
                i = j
            else: i += 1
    return done

# ---------- G2 nét mảnh ----------
THIN_R = {'Regular': 0.8, 'Bold': 0.65}   # designer 20/11: "giảm nét mảnh của các weight medium, semibold, bold" — Bold 0.65 (M / SB nội suy)
PAR = 50                       # mép đối diện lệch ≤ PAR° (vòng có lòng nghiêng: mép lòng đối diện lệch tới ~45°)
HAIR = {'Regular': 42.0, 'Bold': 62.0}; STEM = {'Regular': 104.0, 'Bold': 140.0}
def g2(cs, w, skip, ratio=None, fixed=frozenset(), thin=None):
    """ratio: thu MỌI nét (không chỉ nét mảnh) về × ratio — dùng sau khi giãn ngang (G4)"""
    P = polys(cs); wl, wh = 1.4*HAIR[w], 0.7*STEM[w]
    if ratio is not None: wl, wh = 1e9, 2e9
    R_ = (THIN_R[w] if thin is None else thin) if ratio is None else ratio
    def shrink(pt, nout, par=PAR):
        h = ray(pt, (-nout[0], -nout[1]), P)
        if not h: return 0.0
        t, nn = h
        if abs(nn[0]*nout[0] + nn[1]*nout[1]) < math.cos(math.radians(par)): return 0.0   # mép đối diện không song song
        if ratio is not None and t > 2.2*STEM[w]: return 0.0       # tia đi xuyên lòng / khoảng trắng: không phải một nét
        f = 1.0 if t <= wl else max(0.0, (wh - t)/(wh - wl))
        return (1 - R_)/2*t*f
    moves = []
    for ci, c in enumerate(cs):
        if ci in skip: continue
        S_ = segs(c); n = len(S_)
        for i in range(n):
            a, b = S_[i - 1], S_[i]                               # nút = điểm cuối a = điểm đầu b
            node = b[1][0]
            if id(node) in fixed: continue
            ta, tb = tan_end(*a, False), tan_end(*b, True)
            if not ta or not tb: continue
            outs = []
            for tv, sg in ((ta, -3), (tb, 3)):                         # hướng ra ngoài: thử ở điểm lùi 3 u vào trong đoạn (góc chữ T)
                nv = (tv[1], -tv[0]); bp = (node[0] + sg*tv[0], node[1] + sg*tv[1])
                if inside((bp[0] + 1.5*nv[0], bp[1] + 1.5*nv[1]), P): nv = (-nv[0], -nv[1])
                outs.append(nv)
            # đoạn cong: đo tại nút (lệch vào 2 u); đoạn THẲNG: đo ở giữa đoạn, cả đoạn dời đều (thanh ngang không vát đầu)
            def at(sg, tv, out, end):
                if sg[0] != 'C':
                    q = sg[1]; mid = ((q[0][0] + q[1][0])/2, (q[0][1] + q[1][1])/2)
                    h = ray(mid, (-out[0], -out[1]), P)
                    if h and math.dist(q[0], q[1]) < 1.2*h[0]: return 0.0      # đoạn ngắn hơn bề dày = mặt cắt đầu nét: giữ
                    return shrink(mid, out, 20)                         # đoạn thẳng: mép đối diện song song ±20° (thanh, thân, chéo)
                sgn = -1 if end else 1
                return shrink((node[0] + sgn*2*tv[0], node[1] + sgn*2*tv[1]), out)
            da, db = at(a, ta, outs[0], True), at(b, tb, outs[1], False)
            if a[0] == 'C' and b[0] == 'C' and ratio is None:           # nút giữa hai cung: chỉ mép LÒNG (lõm) dời, gấp đôi; mép lồi
                q1, q2 = bz(*a[1], 0.5), bz(*b[1], 0.5)                  # (bóng ngoài, đường vượt) giữ nguyên
                mx, my = (q1[0] + q2[0])/2 - node[0], (q1[1] + q2[1])/2 - node[1]
                nv = outs[0]; cv = (mx*nv[0] + my*nv[1])/max(1e-6, math.dist(q1, q2))
                fct = 0.0 if cv < -0.01 else (2.0 if cv > 0.01 else 1.0)
                da, db = da*fct, db*fct
            if da == 0 and db == 0: continue
            n1, n2 = outs; cosang = n1[0]*n2[0] + n1[1]*n2[1]
            if cosang > 0.985:                                    # nút trơn
                m = unit((n1[0] + n2[0], n1[1] + n2[1])); d = (da + db)/2; D = (-m[0]*d, -m[1]*d)
            else:                                                 # góc: D·n1 = −da, D·n2 = −db
                det = n1[0]*n2[1] - n1[1]*n2[0]
                if abs(det) < 0.15: continue
                D = ((-da*n2[1] + db*n1[1])/det, (-db*n1[0] + da*n2[0])/det)
                if math.hypot(*D) > 3*max(da, db): continue
            hs = []
            if a[0] == 'C': hs.append(a[1][2])
            if b[0] == 'C': hs.append(b[1][1])
            moves.append((node, hs, D))
    mv = {id(nd): D for nd, _, D in moves}
    moves = [m for m in moves if id(m[0]) not in FLMID]
    for c in cs:                                                  # điểm giữa cung loe: dời theo trung bình hai đầu (giữ hình loe)
        for cmd, ps in c:
            for p in ps:
                if id(p) in FLMID:
                    a_, b_, h1, h2 = FLMID[id(p)]; Da, Db = mv.get(id(a_), (0.0, 0.0)), mv.get(id(b_), (0.0, 0.0))
                    D = ((Da[0] + Db[0])/2, (Da[1] + Db[1])/2)
                    if D != (0.0, 0.0): moves.append((p, [h1, h2], D))
    # dời: điểm neo theo D; tay nắm theo pha trộn D hai đầu cung (1/3, 2/3) rồi chiếu về hướng tiếp tuyến CŨ tại điểm neo
    # (giữ liền tiếp tuyến, cung đổi đều như một đường offset — không xoắn cạnh nút)
    DD = {id(nd): D for nd, _, D in moves}
    # làm mượt độ dời dọc contour qua các nút trơn (2 lượt, ½ – ¼ – ¼): bề dày đổi dần, không khấc / gợn giữa hai nút kề
    HS = {id(nd): hs for nd, hs, _ in moves}
    for c in cs:
        S_ = segs(c); n = len(S_)
        nodes = [sg[1][0] for sg in S_]
        smooth = []
        for i in range(n):
            a, b = S_[i - 1], S_[i]
            ta, tb = tan_end(*a, False), tan_end(*b, True)
            smooth.append(bool(ta and tb and a[0] == 'C' and b[0] == 'C' and ta[0]*tb[0] + ta[1]*tb[1] > 0.995))
        for _ in range(2):
            cur = [DD.get(id(p_), (0.0, 0.0)) for p_ in nodes]; new = list(cur)
            for i in range(n):
                if not smooth[i] or id(nodes[i]) in fixed: continue
                l, r = cur[i - 1], cur[(i + 1) % n]
                new[i] = (0.5*cur[i][0] + 0.25*(l[0] + r[0]), 0.5*cur[i][1] + 0.25*(l[1] + r[1]))
            for i in range(n):
                if new[i] != (0.0, 0.0) or id(nodes[i]) in DD:
                    if id(nodes[i]) not in HS:
                        a, b = S_[i - 1], S_[i]
                        HS[id(nodes[i])] = ([a[1][2]] if a[0] == 'C' else []) + ([b[1][1]] if b[0] == 'C' else [])
                    DD[id(nodes[i])] = new[i]
    allnodes = {id(p_): p_ for c in cs for sg in segs(c) for p_ in sg[1][:1]}
    moves = [(allnodes[k], HS.get(k, []), D) for k, D in DD.items() if k in allnodes and D != (0.0, 0.0)]
    plan = []
    for c in cs:
        for k_, q in segs(c):
            if k_ != 'C': continue
            p0, h1, h2, p3 = q; D0, D3 = DD.get(id(p0), (0.0, 0.0)), DD.get(id(p3), (0.0, 0.0))
            if D0 == (0.0, 0.0) and D3 == (0.0, 0.0): continue
            def tgt(h, p, Dh, Dp):
                u = unit((h[0] - p[0], h[1] - p[1]))
                if not u: return None
                hx, hy = h[0] + Dh[0], h[1] + Dh[1]; px, py = p[0] + Dp[0], p[1] + Dp[1]
                L = max(0.25*math.dist(h, p), (hx - px)*u[0] + (hy - py)*u[1])
                return (px + u[0]*L, py + u[1]*L)
            D1 = ((2*D0[0] + D3[0])/3, (2*D0[1] + D3[1])/3); D2 = ((D0[0] + 2*D3[0])/3, (D0[1] + 2*D3[1])/3)
            plan.append((h1, tgt(h1, p0, D1, D0))); plan.append((h2, tgt(h2, p3, D2, D3)))
    moved = set()
    for h, t_ in plan:
        if t_ is not None and id(h) not in moved: h[0], h[1] = t_; moved.add(id(h))
    for node, hs, D in moves:
        node[0] += D[0]; node[1] += D[1]
        for h in hs:
            if id(h) not in moved: h[0] += D[0]; h[1] += D[1]; moved.add(id(h))
    return len(moves)

NOSPLIT = [False]               # a: lòng dựng theo elip của bản vẽ — chia cung làm lòng gợn ở weight đậm → chỉ dời điểm neo gốc
FLMID = {}                      # id điểm giữa cung loe (sau khi chia đôi) → hai điểm đầu cung
def split_curves(cs, mask=None, minlen=60):
    """chia đôi (t = ½, đúng hình) mọi cubic dài ≥ minlen — thêm điểm neo ở giữa cung để luật nét mảnh đặt được tại chỗ
    mảnh nhất nằm giữa hai điểm neo (vòng có lòng nghiêng). Cùng một phép chia cho Regular và Bold (độ dài lấy theo Regular
    — truyền danh sách vào) để hai master giữ cùng cấu trúc."""
    out = []; mk = []; j = 0
    for c in cs:
        nc = [c[0]]; cur = c[0][1][0]
        for cmd, ps in c[1:]:
            def straight(p0, p1, p2, p3):                         # "cong" mà thẳng (tay nắm nằm trên dây cung): không chia
                L = math.dist(p0, p3) or 1; ux, uy = (p3[0] - p0[0])/L, (p3[1] - p0[1])/L
                return max(abs((q[0] - p0[0])*uy - (q[1] - p0[1])*ux) for q in (p1, p2)) < 1.5
            sp = (mask[j] if mask is not None else (cmd == 'C' and math.dist(cur, ps[2]) >= minlen and NOSPLIT[0] is False
                                                    and not straight(cur, *ps))); mk.append(sp); j += 1
            if sp:
                p0, p1, p2, p3 = cur, ps[0], ps[1], ps[2]
                m = lambda a, b: [(a[0] + b[0])/2, (a[1] + b[1])/2]
                a1, b1, c1 = m(p0, p1), m(p1, p2), m(p2, p3); a2, b2 = m(a1, b1), m(b1, c1); mid = m(a2, b2)
                nc.append(['C', [a1, a2, mid]]); nc.append(['C', [b2, c1, p3]])
                if (id(cur), id(p3)) in FLSEG: FLMID[id(mid)] = (cur, p3, a2, b2)
            else: nc.append([cmd, ps])
            if cmd in 'LC': cur = ps[-1]
        out.append(nc)
    return out, mk

def g23(d, ch, w, low, mask=None):
    cs = parse(d)
    nf = g3(cs) if unicodedata.category(ch)[0] == 'L' or ch in LIG else 0
    nt = 0
    if unicodedata.category(ch)[0] == 'L' or ch in LIG:
        NOSPLIT[0] = unicodedata.normalize('NFD', ch)[0] in 'aªnmhurµsS$eæœ'   # e: chia cung làm gợn đuôi e (designer 20/11)      # a; vòm n m h u r: chia cung làm lòng vòm nhọn, lệch (designer 20/11)
        cs, mask = split_curves(cs, mask)
        top = (OVT + D if ch in low else 712.0) + 3
        skip = {i for i, c in enumerate(cs) if min(y for _, y in pts_of(c)) > top or max(y for _, y in pts_of(c)) < -150}
        fixed = arch_thin(cs, w) if unicodedata.normalize('NFD', ch)[0] in ARCH else frozenset()
        if unicodedata.normalize('NFD', ch)[0] == 'Q':                  # Q: lòng góc dưới-phải (đuôi ăn vào) giữ nguyên — không khấc
            c_ = _counter(cs)
            if c_ is not None:
                P_ = polys([c_])[0]; cx_ = sum(p[0] for p in P_)/len(P_); cy_ = sum(p[1] for p in P_)/len(P_)
                fixed = set(fixed) | {id(p) for p in pts_of(c_) if p[0] > cx_ and p[1] < cy_ + 40}
        nt = g2(cs, w, skip, fixed=fixed)
    return fmt(cs), nf, nt, mask

# ---------- G5 đầu t vát (designer 20/11, hình phác: "đầu chữ t đổi thành kiểu này cho golden") ----------
# Đầu t = tam giác vuông: mép phải thân đi thẳng lên đỉnh; cạnh vát từ đỉnh xuống mặt trên thanh ngang, chạm thanh tại điểm cách
# mép trái thân 0.625 × phần thanh thò trái (hình phác: 45 / 120 px tính từ đầu thanh); đỉnh cao hơn mặt thanh 1.03 × bề ngang
# thân (185 / 180 px). Áp cho t và chữ ghép có t (ft tf tt) — sửa trực tiếp contour (giữ cấu trúc chung Regular / Bold).
T_TOP_K, T_FOOT_K = 1.03, 0.625
def t_head(cs, overhang):
    n_ = 0
    for ci, c in enumerate(cs):
        S_ = segs(c); n = len(S_)
        if n < 6: continue
        bt = None
        for i in range(n):
            k, q = S_[i]
            if k == 'C' or abs(q[0][1] - q[1][1]) > 0.5 or math.dist(q[0], q[1]) < 50 or q[0][1] < OVT + D + 40: continue
            if q[0][0] < q[1][0]: continue                                  # mặt đỉnh đi ngược chiều (phải → trái) như contour gốc
            # lùi tới đoạn bắt đầu ở mặt thanh (phía thân phải), tiến tới đoạn kết thúc ở mặt thanh (phía thân trái)
            ir = i
            while S_[ir % n][1][0][1] > OVT + D + 2: ir -= 1
            il = i
            while S_[il % n][1][-1][1] > OVT + D + 2: il += 1
            Pr, Pl = S_[ir % n][1][0], S_[il % n][1][-1]
            bt = (Pr[1] + Pl[1])/2; sr, sl = Pr[0], Pl[0]
            top = bt + T_TOP_K*(sr - sl); xs = sl - T_FOOT_K*overhang
            nxt = S_[(il + 1) % n]
            new = [('L', [[sr, bt], [sr, top]]), ('L', [[sr, top], [xs, bt]])]
            rest = [S_[(il + 1 + j) % n] for j in range(n - (il - ir) - 1)]
            rest[0] = (rest[0][0], [[xs, bt]] + rest[0][1][1:])
            seq = new + rest                                                # bắt đầu ở (sr, bt)
            seq[-1] = (seq[-1][0], seq[-1][1][:-1] + [[sr, bt]])
            nc = [['M', [[sr, bt]]]] + [[('C' if k_ == 'C' else 'L'), q_[1:]] for k_, q_ in seq if not (k_ == 'Z')] + [['Z', []]]
            cs[ci] = nc; n_ += 1
            break
    return n_
OVH = {'Regular': 67.9, 'Bold': 67.9}     # phần thanh t thò trái thân (AnNam Serif, cả hai weight) — chữ ghép dùng chung
TCH = {'t', '\ue000', '\ue001', '\ue002'}

# ---------- G4 v x y rộng hơn ----------
WIDE = {'v': 1.08, 'x': 1.08, 'y': 1.08}     # designer 20/11: "tăng bề ngang các chữ v, y, x" — × 535/495 (giữ góc chéo như AnNam Serif)
def g4(d, ch, w):
    b = unicodedata.normalize('NFD', ch)[0]
    if b not in WIDE: return d
    k = WIDE[b]; cs = parse(d)
    body = [c for c in cs if min(y for _, y in pts_of(c)) <= OVT + D + 3]      # dấu giữ nguyên hình, chỉ dời theo tâm
    xs = [x for c in body for x, _ in pts_of(c)]; cx = (min(xs) + max(xs))/2
    for c in cs:
        if c in body:
            for p in pts_of(c): p[0] = cx + (p[0] - cx)*k
    g2(cs, w, {i for i, c in enumerate(cs) if c not in body}, ratio=1/k)     # nét giữ bề dày như trước khi giãn
    return fmt(cs)

# ---------- G6 vòng o O mảnh hơn (designer 20/11: "làm vòng o O mảnh hơn nữa") ----------
# Lòng (contour trong lớn nhất) giãn theo TRỤC DÀI của chính nó quanh tâm: chỗ mảnh của vòng nằm ở hai đầu trục dài lòng nghiêng
# → mảnh đúng chỗ; góc nghiêng, nét nhấn, bóng ngoài giữ. Hệ số giải theo o / O (nét mảnh = THIN_R × AnNam Serif), áp cùng hệ số
# cho chữ cùng gốc (ó ò ỏ õ ọ ô … ơ Ơ).
RING = {'o': 'o', 'O': 'O', 'ơ': 'o', 'Ơ': 'O', 'Q': 'Q'}   # Q: lòng có đuôi ăn vào — vùng đuôi giữ nguyên (ring_scale tail)
RINGK = {}
RING_T = {'Regular': 32.0, 'Bold': 44.0}   # designer 20/11 "tại sao nó không bằng nhau": MỘT nét mảnh tuyệt đối cho mọi vòng (o O ơ Ơ …)
                                           # — không theo tỉ lệ AnNam Serif (o 42 / O 34 ở bản gốc vốn lệch). M / SB nội suy.
def _counter(cs):
    ar = lambda c: 0.5*sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(polys([c])[0], polys([c])[0][1:] + polys([c])[0][:1]))
    A0 = ar(cs[0]); inn = [c for c in cs[1:] if ar(c)*A0 < 0 and sum(1 for k, _ in c if k == 'C') >= 4]
    return max(inn, key=lambda c: abs(ar(c))) if inn else None
def ring_scale(d, k, tail=False):
    """tail (Q): điểm lòng ở góc dưới-phải (đuôi ăn vào) giữ nguyên, độ giãn tăng dần theo khoảng cách tới vùng đó (120 u)"""
    cs = parse(d); c = _counter(cs)
    if c is None or abs(k - 1) < 1e-6: return d
    P = polys([c])[0]; n = len(P); cx = sum(p[0] for p in P)/n; cy = sum(p[1] for p in P)/n
    sxx = sum((p[0] - cx)**2 for p in P); syy = sum((p[1] - cy)**2 for p in P); sxy = sum((p[0] - cx)*(p[1] - cy) for p in P)
    th = 0.5*math.atan2(2*sxy, sxx - syy); u = (math.cos(th), math.sin(th))          # trục dài
    pts = pts_of(c)
    prot = [p for p in pts if p[0] > cx and p[1] < cy + 40] if tail is True else []
    if tail == 'stem':                                          # b d p q: mép thân thẳng của lòng giữ nguyên
        S_ = segs(c); prot = [q_ for k_, sg in S_ if k_ != 'C' for q_ in sg]
    for p in pts:
        wgt = 1.0
        if prot: wgt = 0.0 if any(p is q for q in prot) else min(1.0, min(math.dist(p, q) for q in prot)/120)
        t = (p[0] - cx)*u[0] + (p[1] - cy)*u[1]; p[0] += wgt*(k - 1)*t*u[0]; p[1] += wgt*(k - 1)*t*u[1]
    return fmt(cs)
BOWL = set('bdpq')                 # lòng có mép thân thẳng: ring_scale(tail='stem')
def solve_ring(d0, d, w, tail=False):
    k = 1.0
    for _ in range(3):                                         # lặp: đo lại sau khi giãn (chỗ mảnh dịch theo trục)
        k *= _solve_ring1(d0, ring_scale(d, k, tail), w)
    return k
def _solve_ring1(d0, d, w):
    """k = 1 + Δ / a: Δ = nét mảnh hiện tại − RING_T (âm → lòng ngắn lại, nét dày lên), a = bán trục dài lòng"""
    sys.path.insert(0, os.path.join(HERE, '..')); import stroke_balance as SB
    tgt = RING_T[w]; cur = SB.measure([d])[0]
    c = _counter(parse(d)); P = polys([c])[0]; n = len(P); cx = sum(p[0] for p in P)/n; cy = sum(p[1] for p in P)/n
    sxx = sum((p[0] - cx)**2 for p in P); syy = sum((p[1] - cy)**2 for p in P); sxy = sum((p[0] - cx)*(p[1] - cy) for p in P)
    th = 0.5*math.atan2(2*sxy, sxx - syy); u = (math.cos(th), math.sin(th))
    a_ = max(abs((p[0] - cx)*u[0] + (p[1] - cy)*u[1]) for p in P)
    return 1 + (cur - tgt)/a_

# ---------- G7 s S nét mảnh theo chuẩn vòng (designer 20/11: "kiểm tra lại nét mỏng nhất của s") ----------
SFAM = set('sS')
def s_thin(d, w):
    sys.path.insert(0, os.path.join(HERE, '..')); import stroke_balance as SB
    out, r = SB.balance([d], RING_T[w], None)
    return out[0] if isinstance(out, list) else out

# ---------- G8 đồng bộ nét mảnh mọi chữ (designer 20/11: "kiểm tra đồng bộ hết độ dày các nét mỏng") ----------
# Sau các luật trên, nét mảnh từng chữ gốc (Regular, Bold) đo lại; nét mảnh (≤ 1.4 × chuẩn) nhân thêm hệ số r = chuẩn / đo (lặp 3
# lượt, giới hạn 0.7–1.4) theo đúng luật G2 (mép lòng của cung, hai mép của đoạn thẳng). Chuẩn = RING_T (32 / 45). Chữ có dấu dùng r
# của chữ gốc. Bỏ qua chữ không có nét mảnh (i j l f r t I) — đo của chúng là thân.
NOHAIR = set('ijlfrtITı\u0237')
G8R = {}
def g8_apply(d, ch, w, r, low, xtop=None):
    cs = parse(d)
    top = ((OVT + D if xtop is None else xtop) if ch in low else 712.0) + 3
    skip = {i for i, c in enumerate(cs) if min(y for _, y in pts_of(c)) > top or max(y for _, y in pts_of(c)) < -150}
    fixed = frozenset()
    if unicodedata.normalize('NFD', ch)[0] == 'Q':
        c_ = _counter(cs)
        if c_ is not None:
            P_ = polys([c_])[0]; cx_ = sum(p[0] for p in P_)/len(P_); cy_ = sum(p[1] for p in P_)/len(P_)
            fixed = {id(p) for p in pts_of(c_) if p[0] > cx_ and p[1] < cy_ + 40}
    old = NOSPLIT[0]; NOSPLIT[0] = True
    g2(cs, w, skip, fixed=fixed, thin=r)
    NOSPLIT[0] = old
    return fmt(cs)
def g8_solve(d, ch, w, low, xtop=None):
    sys.path.insert(0, os.path.join(HERE, '..')); import stroke_balance as SB
    rt = 1.0; cur = d
    for _ in range(3):
        t = SB.measure([cur])[0]
        if abs(t - RING_T[w]) < 1.0: break
        r = max(0.7/rt, min(1.3/rt, RING_T[w]/t))               # tổng hệ số trong 0.7–1.3 (0.6–1.45 làm méo S, tai g, B) (đo trúng khớp / tay dày: không đẩy quá)
        if abs(r - 1) < 0.01: break
        rt *= r
        cur = g8_apply(cur, ch, w, r, low, xtop)
    return cur, rt

# ---------- G9 đỉnh cung trên e = nét mảnh (designer 20/11: "phần trên này của e là nét mỏng") ----------
# Lòng mắt e (contour trong cao nhất, đáy là mép trên thanh) kéo lên theo chiều đứng, độ kéo tăng tuyến tính theo độ cao:
# y' = y + δ·(y − y_thanh)/(y_đỉnh − y_thanh) → mép thanh đứng yên, đỉnh lòng lên đúng δ = bề dày đỉnh − chuẩn.
EFAM = set('eæœ')
def _top_thick(cs, c_eye):
    Pe = polys([c_eye])[0]; pk = max(Pe, key=lambda p: p[1]); best = None
    P = polys([c for c in cs if min(q[1] for q in polys([c])[0]) < pk[1]])   # chỉ thân chữ — bỏ contour dấu phía trên
    for dx in range(-60, 61, 6):
        x = pk[0] + dx; hits = []
        for pl in P:
            for i in range(len(pl)):
                (x1, y1), (x2, y2) = pl[i - 1], pl[i]
                if (x1 <= x) != (x2 <= x): hits.append(y1 + (x - x1)*(y2 - y1)/(x2 - x1))
        up = sorted(h for h in hits if h >= pk[1] - 40)
        ins = [h for h in up]
        if len(ins) >= 2:
            ins.sort(); t = ins[-1] - ins[-2]
            if best is None or t < best: best = t
    return best
def e_top(d, tgt):
    cs = parse(d)
    ar = lambda c: 0.5*sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(polys([c])[0], polys([c])[0][1:] + polys([c])[0][:1]))
    A0 = ar(cs[0]); inn = [c for c in cs[1:] if ar(c)*A0 < 0]
    if not inn: return d
    eye = max(inn, key=lambda c: sum(p[1] for p in polys([c])[0])/len(polys([c])[0]))
    t = _top_thick(cs, eye)
    if t is None or abs(t - tgt) < 0.5: return d
    ys = [p[1] for p in polys([eye])[0]]; yb, yt = min(ys), max(ys); dl = t - tgt
    for p in pts_of(eye): p[1] += dl*max(0.0, (p[1] - yb)/(yt - yb))
    return fmt(cs)

# ---------- đồng nhất chữ có dấu với chữ gốc ----------
def rebase(src_c, src_b, new_b, new_c):
    """contour thân của chữ có dấu (khớp hình với contour chữ gốc ở bản NGUỒN, sai khác chỉ là tịnh tiến) → lấy đúng contour chữ gốc
    đã xử lý (+ cùng tịnh tiến); dấu giữ của chính nó. Chữ có dấu luôn trùng hình thân với chữ gốc."""
    SC, SB_, NB, NC = parse(src_c), parse(src_b), parse(new_b), parse(new_c)
    if len(SC) != len(NC): return new_c
    sig = lambda c: [k for k, _ in c]
    out = []
    for ci, (sc, nc) in enumerate(zip(SC, NC)):
        rep = nc
        for bi, sb in enumerate(SB_):
            if sig(sb) != sig(sc) or bi >= len(NB) or sig(NB[bi]) != sig(nc): continue
            P, Q = pts_of(sc), pts_of(sb)
            if len(P) != len(Q): continue
            dx, dy = P[0][0] - Q[0][0], P[0][1] - Q[0][1]
            if max(abs(p[0] - q[0] - dx) + abs(p[1] - q[1] - dy) for p, q in zip(P, Q)) < 0.5:
                rep = [[k, [[x + dx, y + dy] for x, y in ps]] for k, ps in NB[bi]]; break
        out.append(rep)
    return fmt(out)

# ---------- ghép chữ có dấu = chữ gốc + dấu (designer 20/11: "nên dùng e rồi gắn dấu vào thôi") ----------
NOCOMP = {'\u031b', '\u0327'}           # sừng ơ ư, móc ç: dính liền thân — giữ glyph riêng
def compose(base_d, acc_d):
    """thân = đúng contour chữ gốc (canh theo tâm ngang phần thân của chữ có dấu); dấu = contour của chữ có dấu nằm ngoài thân"""
    B, A = parse(base_d), parse(acc_d)
    PB = [polys([c])[0] for c in B]
    sa = lambda pl: 0.5*sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(pl, pl[1:] + pl[:1]))
    outer = [pl for pl in PB if sa(pl)*sa(PB[0]) > 0]
    ylo = min(p[1] for pl in PB for p in pl); yhi = max(p[1] for pl in PB for p in pl)
    bx0 = min(p[0] for pl in PB for p in pl); bx1 = max(p[0] for pl in PB for p in pl)
    PA = [polys([c])[0] for c in A]
    bod = [pl for pl in PA if min(p[1] for p in pl) < yhi - 5 and max(p[1] for p in pl) > ylo + 5]
    if not bod: return acc_d
    ax0 = min(p[0] for pl in bod for p in pl); ax1 = max(p[0] for pl in bod for p in pl)
    dx = (ax0 + ax1)/2 - (bx0 + bx1)/2
    sh = [[(x + dx, y) for x, y in pl] for pl in outer]
    def ink(pt): return inside(pt, sh)
    marks = []
    for c, pl in zip(A, PA):
        cxm = sum(p[0] for p in pl)/len(pl); cym = sum(p[1] for p in pl)/len(pl)
        if not ink((cxm, cym)) and not (min(p[1] for p in pl) < yhi - 5 and max(p[1] for p in pl) > ylo + 5 and
                                          min(p[0] for p in pl) < ax1 and max(p[0] for p in pl) > ax0 and abs(sa(pl)) > 0.25*abs(sa(PB[0]))):
            marks.append(c)
    body = [[[k, [[x + dx, y] for x, y in ps]] for k, ps in c] for c in B]
    return fmt(body + marks)
def composable(c):
    nfd = unicodedata.normalize('NFD', c); b = nfd[0]
    return c != b and b.isalpha() and b not in 'iIjJ' and not (set(nfd) & NOCOMP)

def lerp_d(a, b, t):
    A, B = parse(a), parse(b)
    for ca, cb in zip(A, B):
        for (_, pa), (_, pb) in zip(ca, cb):
            for p, q in zip(pa, pb): p[0] += (q[0] - p[0])*t; p[1] += (q[1] - p[1])*t
    return fmt(A)

def main():
    O = json.load(open(os.path.join(SRC, 'outlines.json'))); SP = json.load(open(os.path.join(SRC, 'spacing.json')))
    chars = list(SP['Regular']); low = set(lower_set(chars)); G = {}; NF = {'Regular': 0, 'Bold': 0}; NT = dict(NF)
    for c in chars:
        if f'{c}-Regular' not in O: continue
        for w in ('Regular', 'Bold'):
            d = O[f'{c}-{w}']
            if c in low: d = g1(d, c)
            if c in TCH:
                for _ in range(2):                                          # tt: hai đầu t
                    cs_ = parse(d)
                    if not t_head(cs_, OVH[w]): break
                    d = fmt(cs_)
            d = g4(d, c, w)
            d, nf, nt, mask = g23(d, c, w, low, mask if w == 'Bold' else None); NF[w] += nf; NT[w] += nt
            G[f'{c}-{w}'] = d
        b_ = unicodedata.normalize('NFD', c)[0]
        if b_ in EFAM:                                            # G9 đỉnh e = chuẩn nét mảnh
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = e_top(G[f'{c}-{w}'], RING_T[w])
        if b_ in SFAM:                                            # G7 s S: nét mảnh = RING_T (cùng chuẩn vòng), mép lòng, lặp Newton
            for w in ('Regular', 'Bold'):
                G[f'{c}-{w}'] = s_thin(G[f'{c}-{w}'], w)
        if b_ in RING:
            for w in ('Regular', 'Bold'):
                base = RING[b_]
                if (base, w) not in RINGK: RINGK[(base, w)] = solve_ring(O[f'{base}-{w}'], G[f'{base}-{w}'], w, base == 'Q')
                G[f'{c}-{w}'] = ring_scale(G[f'{c}-{w}'], RINGK[(base, w)], base == 'Q')
        if c.isalpha() and len(c) == 1 and c.isascii() and c not in NOHAIR and c not in EFAM:   # G8 chữ gốc (e: chỉ G9 đỉnh cung)
            for w in ('Regular', 'Bold'):
                G[f'{c}-{w}'], G8R[(c, w)] = g8_solve(G[f'{c}-{w}'], c, w, low)
        for w, t in TW.items(): G[f'{c}-{w}'] = lerp_d(G[f'{c}-Regular'], G[f'{c}-Bold'], t)
    for c in chars:                                               # G8 chữ có dấu / chữ ghép: r của chữ gốc
        b_ = unicodedata.normalize('NFD', c)[0]
        if c == b_ or f'{c}-Regular' not in G or b_ in NOHAIR or not ((b_, 'Regular') in G8R): continue
        for w in ('Regular', 'Bold'):
            r = G8R[(b_, w)]
            if abs(r - 1) > 0.01: G[f'{c}-{w}'] = g8_apply(G[f'{c}-{w}'], c, w, r, low)
        for w, t in TW.items(): G[f'{c}-{w}'] = lerp_d(G[f'{c}-Regular'], G[f'{c}-Bold'], t)
    nrb = 0
    for c in chars:                                               # chữ có dấu = chữ gốc + dấu (sau mọi luật)
        b_ = unicodedata.normalize('NFD', c)[0]
        if f'{c}-Regular' not in G or f'{b_}-Regular' not in G: continue
        if composable(c):
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = compose(G[f'{b_}-{w}'], G[f'{c}-{w}'])
            nrb += 1
        elif c != b_:
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = rebase(O[f'{c}-{w}'], O[f'{b_}-{w}'], G[f'{b_}-{w}'], G[f'{c}-{w}'])
        else: continue
        for w, t in TW.items(): G[f'{c}-{w}'] = lerp_d(G[f'{c}-Regular'], G[f'{c}-Bold'], t)
    print('chữ có dấu ghép = chữ gốc + dấu:', nrb)
    print('G8 hệ số nét mảnh:', ' '.join(f'{c}{w[0]}{r:.2f}' for (c, w), r in sorted(G8R.items()) if abs(r - 1) > 0.02))
    os.makedirs(OUT, exist_ok=True)
    json.dump(G, open(os.path.join(OUT, 'outlines.json'), 'w'))
    print('G6 lòng giãn:', {f'{b}-{w}': round(k, 3) for (b, w), k in RINGK.items()})
    print('golden:', len(G), 'glyph ·', len(low), 'ký tự chữ thường nâng x-height', XH0, '→', XH1, '· loe phóng', NF, '· nút nét mảnh dời', NT)

if __name__ == '__main__':
    main()
