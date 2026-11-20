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
FLARE_KX_CAP = 1.45             # designer 20/11 "các chữ hoa Golden đuôi chân loe dài thêm ra thêm xíu" (chữ thường giữ 1.3)
FLK = [1.3]                    # bề rộng loe đang dùng (g23 đặt theo chữ hoa / thường)
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
                    p[0] = C0[0] + (p[0] - C0[0])*FLK[0]; p[1] = Z + (p[1] - Z)*FLARE_KY
                FLSEG.add((id(q[0]), id(q[3]))); n_fl += 1
    return n_fl

# ---------- G2b lòng vòm n m h / lòng đáy u: dịch nguyên khối (designer 20/11: "đường cong bụng trong chữ u, m, n không tự nhiên") ----------
ARCH = set()                   # (cũ: 'nmhuµ' dịch nguyên khối) — nay vòm / đáy u dùng G10 (dốc tuyến tính, vai cạnh thân gần đứng yên)
ARCH_T = {'Regular': 42.0, 'Bold': 56.5}       # = RING_T (G8): bề dày đỉnh vòm sau khi dịch
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
                            # δ: dịch đứng cả chuỗi sao cho CHỖ MẢNH NHẤT dọc cung (đo theo pháp tuyến, gồm vai cạnh thân) = chuẩn:
                            # bề dày pháp tuyến giảm δ·|n_y| → δ = min (dày − chuẩn)/|n_y|
                            ds = []
                            for _, q in chain:
                                for t_ in range(1, 24):
                                    a_ = bz(*q, t_/24); b_ = bz(*q, t_/24 + 0.005); u_ = unit((b_[0] - a_[0], b_[1] - a_[1]))
                                    if not u_: continue
                                    nv = (-u_[1], u_[0])
                                    if not inside((a_[0] + 2*nv[0], a_[1] + 2*nv[1]), P): nv = (-nv[0], -nv[1])
                                    if not inside((a_[0] + 2*nv[0], a_[1] + 2*nv[1]), P) or abs(nv[1]) < 0.3: continue
                                    hh = ray(a_, nv, P)
                                    if hh and hh[0] < 2.2*ARCH_T[w]: ds.append((hh[0] - ARCH_T[w])/abs(nv[1]))
                            dlt = min(ds) if ds else h[0] - ARCH_T[w]
                            for p_ in pts: p_[1] += sg*dlt
                            done |= {id(p_) for p_ in pts}
                i = j
            else: i += 1
    return done

# ---------- G3b loe đứng đầu tay ngang dài hơn (designer 20/11: "các chân loe đứng dài hơn, ví dụ loe hai bên chữ T dài xuống hơn") ----------
# Mẫu: mép cắt đầu tay THẲNG ĐỨNG (30–220 u) → chuỗi cung tới điểm có tiếp tuyến NẰM NGANG (mép thanh, y = Y0). Chuỗi cung (gồm đầu
# mút loe) giãn đứng × ARM_K quanh Y0: đầu loe dài thêm 40 % theo chiều đứng, hướng tiếp tuyến ngang ở Y0 giữ (liền mạch với thanh).
ARM_K = 1.4
def g3b(cs):
    n_ = 0
    for c in cs:
        S_ = segs(c); n = len(S_)
        for i in range(n):
            k, q = S_[i]
            if k == 'C' or abs(q[0][0] - q[1][0]) > 0.5 or not (30 <= abs(q[0][1] - q[1][1]) <= 220): continue
            for fwd in (True, False):
                j = (i + 1) % n if fwd else (i - 1) % n; chain = []
                while S_[j][0] == 'C' and len(chain) < 4:
                    chain.append(S_[j])
                    t = tan_end(*S_[j], not fwd)                     # tiếp tuyến tại đầu xa của cung (theo chiều đi)
                    if t and abs(t[1]) < 0.06: break
                    j = (j + 1) % n if fwd else (j - 1) % n
                else: continue
                if not chain: continue
                endp = chain[-1][1][3] if fwd else chain[-1][1][0]
                t = tan_end(*chain[-1], not fwd)
                if not t or abs(t[1]) >= 0.06: continue
                tip = q[1] if fwd else q[0]; Y0 = endp[1]
                root = q[0] if fwd else q[1]                              # gốc mép cắt phải nằm trên đường kẻ (đầu tay chữ, không phải lòng)
                if not any(abs(root[1] - g) < 0.8 for g in GUIDES): continue
                if abs(tip[1] - Y0) < 20: continue
                mv = []
                for _, cq in chain:
                    for p_ in cq:
                        if p_ is endp or any(p_ is m for m in mv): continue
                        mv.append(p_)
                hfar = chain[-1][1][2] if fwd else chain[-1][1][1]          # tay nắm ở đầu ngang: giữ trên đường Y0
                for p_ in mv:
                    if p_ is hfar: continue
                    p_[1] = Y0 + (p_[1] - Y0)*ARM_K
                n_ += 1
    return n_

# ---------- G2 nét mảnh ----------
GUIDES = (0.0, 700.0, 535.0, 495.0)   # đường chân, cao chữ hoa, x-height Golden / AnNam Serif: mép thẳng nằm trên đó không dời
THIN_R = {'Regular': 1.0, 'Bold': 1.0}   # S59: nét mảnh Golden = AnNam Serif → không làm mảnh theo tỉ lệ (trước 0.8 / 0.65)   # designer 20/11: "giảm nét mảnh của các weight medium, semibold, bold" — Bold 0.65 (M / SB nội suy)
PAR = 50                       # mép đối diện lệch ≤ PAR° (vòng có lòng nghiêng: mép lòng đối diện lệch tới ~45°)
HAIR = {'Regular': 42.0, 'Bold': 62.0}; STEM = {'Regular': 104.0, 'Bold': 140.0}
def g2(cs, w, skip, ratio=None, fixed=frozenset(), thin=None, abs_t=None):
    """ratio: thu MỌI nét (không chỉ nét mảnh) về × ratio — dùng sau khi giãn ngang (G4)
    abs_t: mỗi đoạn thẳng nét mảnh (dày 0.5–1.6 × abs_t, đo riêng tại giữa đoạn) đưa về ĐÚNG abs_t (G8 tuyệt đối)"""
    P = polys(cs); wl, wh = 1.4*HAIR[w], 0.7*STEM[w]
    if ratio is not None: wl, wh = 1e9, 2e9
    R_ = (THIN_R[w] if thin is None else thin) if ratio is None else ratio
    def shrink(pt, nout, par=PAR):
        h = ray(pt, (-nout[0], -nout[1]), P)
        if not h: return 0.0
        t, nn = h
        if abs(nn[0]*nout[0] + nn[1]*nout[1]) < math.cos(math.radians(par)): return 0.0   # mép đối diện không song song
        hy = pt[1] - nout[1]*t
        pin = 2.0 if abs(nn[0]) < 0.05 and any(abs(hy - g) < 2.5 for g in GUIDES) else 1.0   # mép đối diện nằm trên đường kẻ: mép này nhận gấp đôi
        if ratio is not None and t > 2.2*STEM[w]: return 0.0       # tia đi xuyên lòng / khoảng trắng: không phải một nét
        if abs_t is not None:
            at_ = abs_t*BAR_K if abs(nout[1]) > 0.97 else abs_t      # nét NGANG: hiệu chỉnh quang học (trông dày hơn nét đứng / cong)
            if 0.26 < abs(nout[1]) < 0.97: at_ = abs_t*DIAG_K          # nét CHÉO (15–75°): trông mảnh hơn → dày thêm DIAG_K
            return (t - at_)/2*pin if 0.5*abs_t <= t <= 1.6*abs_t else 0.0
        f = 1.0 if t <= wl else max(0.0, (wh - t)/(wh - wl))
        return (1 - R_)/2*t*f*pin
    moves = []
    for ci, c in enumerate(cs):
        if ci in skip: continue
        S_ = segs(c); n = len(S_)
        for i in range(n):
            a, b = S_[i - 1], S_[i]                               # nút = điểm cuối a = điểm đầu b
            node = b[1][0]
            if id(node) in fixed: continue
            if ratio is None and a[0] == 'C' and b[0] == 'C': continue          # nét cong: không dời từng nút (làm mảnh bằng biến đổi lòng)
            ta, tb = tan_end(*a, False), tan_end(*b, True)
            if not ta or not tb: continue
            if any(abs(node[1] - g) < 0.8 for g in GUIDES) and (abs(ta[1]) < 0.05 or abs(tb[1]) < 0.05) and not (a[0] != 'C' and b[0] != 'C'): continue   # nút trên đường kẻ, tiếp tuyến ngang (góc thẳng–thẳng: được trượt dọc đường kẻ — chéo M W Y K dời song song)
            outs = []
            for tv, sg, seg_ in ((ta, -3, a), (tb, 3, b)):             # hướng ra ngoài: thử ở điểm lùi 3 u vào trong đoạn (góc chữ T);
                nv = (tv[1], -tv[0]); bp = (node[0] + sg*tv[0], node[1] + sg*tv[1])   # đoạn THẲNG: thử ở giữa đoạn (góc hẹp —
                if seg_[0] != 'C':                                             # đỉnh trong A của Æ — điểm sát góc lọt vào nét kề)
                    bp = ((seg_[1][0][0] + seg_[1][-1][0])/2, (seg_[1][0][1] + seg_[1][-1][1])/2)
                if inside((bp[0] + 1.5*nv[0], bp[1] + 1.5*nv[1]), P): nv = (-nv[0], -nv[1])
                outs.append(nv)
            # đoạn cong: đo tại nút (lệch vào 2 u); đoạn THẲNG: đo ở giữa đoạn, cả đoạn dời đều (thanh ngang không vát đầu)
            def at(sg, tv, out, end):
                if sg[0] != 'C':
                    q = sg[1]
                    ix_ = next((m for m in range(n) if S_[m][1] is q), None)          # đoạn gần thẳng hàng (≤ 6°) với đoạn kề DÀI HƠN:
                    u0_ = unit((q[1][0] - q[0][0], q[1][1] - q[0][1]))                 # cùng một mép nét (bị chia bởi mẩu nối / khớp)
                    for nb in ((S_[ix_ - 1], S_[(ix_ + 1) % n]) if ix_ is not None and u0_ else ()):
                        if nb[0] == 'C' or math.dist(*nb[1]) < max(60, math.dist(q[0], q[1])): continue
                        u1 = unit((nb[1][1][0] - nb[1][0][0], nb[1][1][1] - nb[1][0][1]))
                        if abs(u0_[0]*u1[0] + u0_[1]*u1[1]) < math.cos(math.radians(6)): continue
                        mid1 = ((nb[1][0][0] + nb[1][1][0])/2, (nb[1][0][1] + nb[1][1][1])/2); o1 = (u1[1], -u1[0])
                        if inside((mid1[0] + 1.5*o1[0], mid1[1] + 1.5*o1[1]), P): o1 = (-o1[0], -o1[1])
                        v1 = shrink(mid1, o1, 20)
                        if v1: return v1
                    if math.dist(q[0], q[1]) < 30:                     # đoạn ngắn nối tiếp một đoạn thẳng dài gần thẳng hàng (≤ 20°):
                        ix = next((m for m in range(n) if S_[m][1] is q), None)   # là phần của cùng nét — dời cùng nét đó, góc nối giữ nguyên
                        u0 = unit((q[1][0] - q[0][0], q[1][1] - q[0][1]))
                        for nb in ((S_[ix - 1], S_[(ix + 1) % n]) if ix is not None and u0 else ()):
                            if nb[0] == 'C' or math.dist(*nb[1]) < 60: continue
                            u1 = unit((nb[1][1][0] - nb[1][0][0], nb[1][1][1] - nb[1][0][1]))
                            if abs(u0[0]*u1[0] + u0[1]*u1[1]) < math.cos(math.radians(20)): continue
                            mid1 = ((nb[1][0][0] + nb[1][1][0])/2, (nb[1][0][1] + nb[1][1][1])/2); o1 = (u1[1], -u1[0])
                            if inside((mid1[0] + 1.5*o1[0], mid1[1] + 1.5*o1[1]), P): o1 = (-o1[0], -o1[1])
                            return shrink(mid1, o1, 20)
                    mid = ((q[0][0] + q[1][0])/2, (q[0][1] + q[1][1])/2)
                    if any(abs(q[0][1] - g) < 2.5 and abs(q[1][1] - g) < 2.5 for g in GUIDES): return 0.0   # mép trên đường kẻ (≤ 2.5 u — Œ: nối điểm vượt O): đứng yên
                    h = ray(mid, (-out[0], -out[1]), P)
                    if h and math.dist(q[0], q[1]) < 1.2*h[0]: return 0.0      # đoạn ngắn hơn bề dày = mặt cắt đầu nét: giữ
                    own = shrink(mid, out, 20)                          # đoạn thẳng: mép đối diện song song ±20° (thanh, thân, chéo)
                    if own == 0.0:                                      # không đo được (vd. đoạn hội tụ về đỉnh V của W) nhưng thẳng hàng
                        ix = next((m for m in range(n) if S_[m][1] is q), None)   # (≤ 6°) với đoạn kề dài: dời cùng nét đó (không xoay)
                        u0 = unit((q[1][0] - q[0][0], q[1][1] - q[0][1]))
                        for nb in ((S_[ix - 1], S_[(ix + 1) % n]) if ix is not None and u0 else ()):
                            if nb[0] == 'C' or math.dist(*nb[1]) < 60: continue
                            u1 = unit((nb[1][1][0] - nb[1][0][0], nb[1][1][1] - nb[1][0][1]))
                            if abs(u0[0]*u1[0] + u0[1]*u1[1]) < math.cos(math.radians(6)): continue
                            mid1 = ((nb[1][0][0] + nb[1][1][0])/2, (nb[1][0][1] + nb[1][1][1])/2); o1 = (u1[1], -u1[0])
                            if inside((mid1[0] + 1.5*o1[0], mid1[1] + 1.5*o1[1]), P): o1 = (-o1[0], -o1[1])
                            v1 = shrink(mid1, o1, 20)
                            if v1: return v1
                    return own
                sgn = -1 if end else 1
                return shrink((node[0] + sgn*2*tv[0], node[1] + sgn*2*tv[1]), out)
            da, db = at(a, ta, outs[0], True), at(b, tb, outs[1], False)
            if ratio is None and (a[0] == 'C') != (b[0] == 'C'):       # góc cung–thẳng: chỉ phía đoạn thẳng quyết định (cung không bị
                if a[0] == 'C': da = 0.0                                # kéo theo góc → đáy lòng G không gợn)
                else: db = 0.0
            if a[0] == 'C' and b[0] == 'C' and ratio is None:           # nút giữa hai cung: chỉ mép LÒNG (lõm) dời, gấp đôi; mép lồi
                q1, q2 = bz(*a[1], 0.5), bz(*b[1], 0.5)                  # (bóng ngoài, đường vượt) giữ nguyên
                mx, my = (q1[0] + q2[0])/2 - node[0], (q1[1] + q2[1])/2 - node[1]
                nv = outs[0]; cv = (mx*nv[0] + my*nv[1])/max(1e-6, math.dist(q1, q2))
                fct = 0.0 if cv < -0.01 else (2.0 if cv > 0.01 else 1.0)
                da, db = da*fct, db*fct
            if da == 0 and db == 0: continue
            n1, n2 = outs; cosang = n1[0]*n2[0] + n1[1]*n2[1]
            if cosang > 0.985:                                    # nút trơn
                m = unit((n1[0] + n2[0], n1[1] + n2[1]))
                d = (da + db) if (ratio is None and (a[0] == 'C') != (b[0] == 'C')) else (da + db)/2   # cung–thẳng liền tiếp tuyến: theo đoạn thẳng
                D = (-m[0]*d, -m[1]*d)
            else:                                                 # góc: D·n1 = −da, D·n2 = −db
                det = n1[0]*n2[1] - n1[1]*n2[0]
                if abs(det) < 0.15:                                # hai mép gần thẳng hàng (≤ 8.6°): dời vuông góc theo phía có độ dời
                    if cosang < 0.95: continue
                    m = unit((n1[0] + n2[0], n1[1] + n2[1])); d = max(da, db); D = (-m[0]*d, -m[1]*d)
                elif ratio is None and (a[0] == 'C') != (b[0] == 'C'):    # góc cung–thẳng: điểm nối dời theo pháp tuyến đoạn thẳng
                    nl, dl = (n2, db) if a[0] == 'C' else (n1, da)               # (cả đoạn dời song song — mép trong thanh Z không dốc)
                    D = (-nl[0]*dl, -nl[1]*dl)
                else: D = ((-da*n2[1] + db*n1[1])/det, (-db*n1[0] + da*n2[0])/det)
                if math.hypot(*D) > 3*max(abs(da), abs(db)): continue      # (giá trị tuyệt đối: làm DÀY có da / db âm)
            hs = []
            if a[0] == 'C': hs.append(a[1][2])
            if b[0] == 'C': hs.append(b[1][1])
            moves.append((node, hs, D))
            if os.environ.get('G2DBG') and float(os.environ.get('G2Y0', 600)) < node[1] < float(os.environ.get('G2Y1', 700)): print('g2', [round(v,1) for v in node], a[0], b[0], round(da,2), round(db,2), [round(v,2) for v in D])
    mv = {id(nd): D for nd, _, D in moves}
    if ratio is None:                                             # loe đi theo nét thẳng: đầu xa của cung kề nút đã dời (góc chân)
        extra = []                                                # trượt theo đường chân của nó cùng độ dời chiếu lên đường đó
        for c in cs:
            S_ = segs(c); n = len(S_)
            for i in range(n):
                k_, q = S_[i]
                if k_ != 'C': continue
                for near, far, farh, nxt in ((q[0], q[3], q[2], S_[(i + 1) % n]), (q[3], q[0], q[1], S_[i - 1])):
                    Dn = mv.get(id(near))
                    if not Dn or id(far) in mv or nxt[0] == 'C': continue
                    a_, b_ = nxt[1][0], nxt[1][-1]; u = unit((b_[0] - a_[0], b_[1] - a_[1]))
                    if not u: continue
                    pr = Dn[0]*u[0] + Dn[1]*u[1]; Df = (pr*u[0], pr*u[1])
                    if abs(pr) > 0.05: extra.append((far, [farh], Df)); mv[id(far)] = Df
        moves += extra
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
    # S58 (designer "sửa luôn gợn của W"): chuỗi cung nằm giữa hai góc (mọi nút trong chuỗi trơn cung–cung, vd. cung loe đầu chéo W):
    # độ dời mọi điểm (nút trong + tay nắm) nội suy TUYẾN TÍNH theo độ dài đa giác điều khiển giữa độ dời hai góc đầu → cung dời đều,
    # không gợn (lối cũ: chỉ lan một phần qua bước làm trơn + chiếu tay nắm → cung gần thẳng gợn ~1 u).
    FIX = {}
    if ratio is None:
        for c in cs:
            S_ = segs(c); n = len(S_)
            if n < 2: continue
            sm = []
            for i in range(n):
                a, b = S_[i - 1], S_[i]
                ta, tb = tan_end(*a, False), tan_end(*b, True)
                sm.append(bool(ta and tb and a[0] == 'C' and b[0] == 'C' and ta[0]*tb[0] + ta[1]*tb[1] > 0.995))
            if all(sm): continue
            st = next(i for i in range(n) if not sm[i])
            i = st
            for _ in range(n):
                if S_[i][0] == 'C' and not sm[i]:
                    j = i; run = []
                    while S_[j % n][0] == 'C' and len(run) < n:
                        run.append(S_[j % n]); j += 1
                        if not sm[j % n]: break
                    if run and not sm[j % n] and len(run) >= 2:
                        A_, B_ = run[0][1][0], run[-1][1][3]
                        DA, DB = DD.get(id(A_), (0.0, 0.0)), DD.get(id(B_), (0.0, 0.0))
                        prv, nxt_ = S_[(i - 1) % n], S_[j % n]
                        endsA = endsB = None
                        def proj(Dv, sg_):                                 # đầu còn lại trượt dọc đoạn thẳng của nó: chiếu độ dời
                            u_ = unit((sg_[1][1][0] - sg_[1][0][0], sg_[1][1][1] - sg_[1][0][1]))
                            if not u_: return (0.0, 0.0)
                            pr_ = Dv[0]*u_[0] + Dv[1]*u_[1]; return (pr_*u_[0], pr_*u_[1])
                        if DA == (0.0, 0.0) and DB != (0.0, 0.0) and prv[0] != 'C' and id(A_) not in fixed:
                            DA = proj(DB, prv); endsA = A_                     # (loe đi theo nét — cả chuỗi cung tịnh tiến gần như nguyên khối)
                        elif DB == (0.0, 0.0) and DA != (0.0, 0.0) and nxt_[0] != 'C' and id(B_) not in fixed:
                            DB = proj(DA, nxt_); endsB = B_
                        if endsA is not None and DA != (0.0, 0.0): FIX[id(endsA)] = (endsA, DA)
                        if endsB is not None and DB != (0.0, 0.0): FIX[id(endsB)] = (endsB, DB)
                        if DA != (0.0, 0.0) or DB != (0.0, 0.0):
                            pts = [run[0][1][0]]
                            for _k, q_ in run: pts += [q_[1], q_[2], q_[3]]
                            Ls = [0.0]
                            for u_, v_ in zip(pts, pts[1:]): Ls.append(Ls[-1] + math.dist(u_, v_))
                            tot = Ls[-1] or 1.0
                            for ix_, (pp, ll) in enumerate(zip(pts[1:-1], Ls[1:-1]), 1):
                                if ix_ == 1: FIX[id(pp)] = (pp, DA); continue          # tay nắm kề góc đầu: đi cùng góc (giữ tiếp tuyến)
                                if ix_ == len(pts) - 2: FIX[id(pp)] = (pp, DB); continue
                                f = ll/tot; FIX[id(pp)] = (pp, (DA[0] + (DB[0] - DA[0])*f, DA[1] + (DB[1] - DA[1])*f))
                i = (i + 1) % n
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
    for k, (pp, Df) in FIX.items():                                # chuỗi cung giữa hai góc: dời tuyến tính
        pp[0] += Df[0]; pp[1] += Df[1]; moved.add(k)
    for h, t_ in plan:
        if t_ is not None and id(h) not in moved: h[0], h[1] = t_; moved.add(id(h))
    for node, hs, D in moves:
        if id(node) in FIX: continue
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
    FLK[0] = FLARE_KX_CAP if unicodedata.normalize('NFD', ch)[0].isupper() else FLARE_KX
    nf = g3(cs) if unicodedata.category(ch)[0] == 'L' or ch in LIG else 0
    if unicodedata.category(ch)[0] == 'L': nf += g3b(cs)
    nt = 0
    if unicodedata.category(ch)[0] == 'L' or ch in LIG:
        NOSPLIT[0] = unicodedata.normalize('NFD', ch)[0] in 'aªnmhurµsS$eæœ'   # e: chia cung làm gợn đuôi e (designer 20/11)      # a; vòm n m h u r: chia cung làm lòng vòm nhọn, lệch (designer 20/11)
        NOSPLIT[0] = True                                         # luật mới: không chia cung (nét cong làm mảnh bằng biến đổi lòng)
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
RING_T = {'Regular': 42.0, 'Bold': 56.5}   # designer 20/11 "các nét mỏng của Golden đưa về bằng với nét mỏng của Serif" (trước 32 / 44)   # designer 20/11 "tại sao nó không bằng nhau": MỘT nét mảnh tuyệt đối cho mọi vòng (o O ơ Ơ …)
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
# G7 s S (luật mới): mép lòng trên / dưới là chuỗi điểm neo lõm nối từ đầu nét về sống. Mỗi lòng kéo dãn theo chiều đứng, tuyến tính
# theo độ cao tính từ điểm neo chân chuỗi (đứng yên): y' = y ± δ·(y − y_chân)/(y_đỉnh − y_chân) — phép affine nên mép lòng giữ trơn,
# không có điểm neo bị đẩy riêng (lối cũ dời từng điểm neo → lòng gãy góc). δ = bề dày đỉnh lòng − chuẩn, lặp 4 lượt.
def _s_chains(cs, pr):
    import stroke_balance as SB
    sm = {(gi, i) for gi, i, _ in SB.nodes(cs)}; side = {(p[1], p[2]): p for p in pr}; out = []
    for gi, g in enumerate(cs):
        n = len(g)
        for k in range(n):
            if (gi, k) in sm: continue                                            # góc đầu nét; chuỗi lõm đi lùi hoặc tiến
            for st in (-1, 1):
                ch = []; m = (k + st) % n
                while (gi, m) in sm and (gi, m) in side and side[(gi, m)][5] >= 0.5 and len(ch) < n:
                    ch.append(m); m = (m + st) % n
                if len(ch) >= 2 and (gi, m) in sm: out.append((gi, k, ch, m))   # (contour, góc đầu nét, chuỗi lõm, nút chân)
    return out
def s_thin(d, w):
    sys.path.insert(0, os.path.join(HERE, '..')); import stroke_balance as SB
    tgt = RING_T[w]
    for _ in range(4):
        cs = SB.contours(d); pr = SB.probe([d]); P = {(p[1], p[2]): p for p in pr}; done = True
        for gi, k, ch, m0 in _s_chains(cs, pr):
            g = cs[gi]; n = len(g); ys = g[m0][-1][1]
            ext = max(ch, key=lambda m: abs(g[m][-1][1] - ys)); yt = g[ext][-1][1]
            if abs(yt - ys) < 40: continue
            dlt = P[(gi, ext)][4] - tgt
            if abs(dlt) < 0.5: continue
            done = False; sg = 1 if yt > ys else -1
            f = lambda y: y + sg*dlt*max(0.0, (y - ys)*sg)/abs(yt - ys)
            pts = []
            for m in ch:                                     # nút + hai tay của nó
                A, B = g[m], g[(m + 1) % n]
                pts += ([A[3], A[4]] if A[0] == 'C' else [A[2]]) + ([B[1], B[2]] if B[0] == 'C' else [B[1]])
            for q in {id(q): q for q in pts}.values(): q[1] = f(q[1])
        d = SB.to_d(cs)
        if done: break
    return d

# ---------- G10 nét mảnh cong của mọi lòng còn lại (B D P R b d p q a g C G c U J …): kéo dãn chuỗi cung lõm theo chiều đứng ----------
# Luật mới (designer 20/11 "đồng bộ tất cả"): nét cong chỉ làm mảnh bằng biến đổi lòng. Mỗi chuỗi điểm neo TRƠN liên tiếp trên mép lòng
# (nằm giữa hai góc, hoặc trọn một lòng kín toàn cung) có điểm cao nhất T / thấp nhất B. Nếu bề dày tại đó là nét mảnh (≤ 1.7 × chuẩn),
# nửa trên chuỗi kéo lên δT tuyến tính theo độ cao từ y_giữa (affine → mép trơn), nửa dưới kéo xuống δB. Góc đầu chuỗi nằm trên đoạn
# thẳng đứng thì trượt theo đoạn đó; góc khác (thanh ngang, đầu nét) đứng yên và làm mốc cho độ dốc. Lặp 3 lượt (đo lại).
G10_SKIP = set('oOQsSeæœijlfrtITı\u0237')
def _g10_chains(cs):
    import stroke_balance as SB
    sm = {(gi, i) for gi, i, _ in SB.nodes(cs)}; out = []
    for gi, g in enumerate(cs):
        n = len(g); cor = [m for m in range(n) if (gi, m) not in sm]
        if not cor:
            out.append((gi, list(range(n)), None, None)); continue
        for a_, b_ in zip(cor, cor[1:] + [cor[0] + n]):
            ch = [m % n for m in range(a_ + 1, b_)]
            if len(ch) >= 1: out.append((gi, ch, a_ % n, b_ % n))
    return out
def g10(d, w, tgt=None):
    sys.path.insert(0, os.path.join(HERE, '..')); import stroke_balance as SB
    tgt = RING_T[w] if tgt is None else tgt
    for _ in range(3):
        cs = SB.contours(d); pr = SB.probe([d]); P = {(p[1], p[2]): p for p in pr}; moved = False
        polys_ = SB.mask_paths([d])[2]
        G_bz = lambda sg, t: bz(sg[1], sg[2], sg[3], sg[4], t)
        def _area(g):
            pl = [sg[-1] for sg in g]; return 0.5*sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(pl, pl[1:] + pl[:1]))
        ars = [_area(g) for g in cs]; big = max(range(len(cs)), key=lambda i: abs(ars[i])) if cs else 0
        hole = [ars[i]*ars[big] < 0 for i in range(len(cs))]     # contour lỗ = lòng kín
        for gi, ch, e0, e1 in _g10_chains(cs):
            g = cs[gi]; n = len(g); Y = lambda m: g[m][-1][1]
            def slide(e):                                         # góc trượt được khi đoạn thẳng kề nó gần đứng
                if e is None: return True
                for sg in (g[e], g[(e + 1) % n]):
                    if sg[0] == 'L':
                        dx, dy = sg[2][0] - sg[1][0], sg[2][1] - sg[1][1]
                        if abs(dy) > 1 and abs(dx/dy) < 0.2: return True
                return False
            sd = [P[(gi, m)][5] for m in ch if (gi, m) in P]
            if not sd or sum(sd)/len(sd) < 0.5: continue          # chỉ mép LÒNG (lõm); mép ngoài lồi giữ nguyên
            segs_ch = sorted({m for m in ch} | {(m + 1) % n for m in ch} | ({(e0 + 1) % n} if e0 is not None else set()))
            yall = [Y(m) for m in ch] + [Y(e) for e in (e0, e1) if e is not None]
            ym_ = (max(yall) + min(yall))/2
            top, bot = [], []                                     # lấy mẫu dày dọc các cung của chuỗi, chỗ tiếp tuyến gần ngang
            for j in segs_ch:
                sg = g[j]
                if sg[0] != 'C': continue
                for k in range(1, 20):
                    t_ = k/20; q = G_bz(sg, t_); q2 = G_bz(sg, t_ + 0.01)
                    L_ = math.hypot(q2[0] - q[0], q2[1] - q[1])
                    if L_ < 1e-9: continue
                    nv = (-(q2[1] - q[1])/L_, (q2[0] - q[0])/L_)          # pháp tuyến về phía mực
                    if not SB.inside((q[0] + 3*nv[0], q[1] + 3*nv[1]), polys_): nv = (-nv[0], -nv[1])
                    if not SB.inside((q[0] + 3*nv[0], q[1] + 3*nv[1]), polys_) or abs(nv[1]) < 0.3: continue
                    h = SB.ray(q, nv, polys_)
                    if not h or h > 400: continue
                    (top if q[1] > ym_ else bot).append((h/abs(nv[1]), 1 if nv[1] > 0 else -1, q[1], abs(nv[1]), q[0]))   # bề dày quy về độ dời đứng
            if not top and not bot: continue
            ym = ym_; yT = max([max(yall)] + [x[2] for x in top]); yB = min([min(yall)] + [x[2] for x in bot])
            fixed_e = [tuple(g[e][-1][:2]) for e in (e0, e1) if e is not None and not slide(e)]
            fixed_y = [Y(e) for e in (e0, e1) if e is not None and not slide(e)]
            lo_t = max([ym] + [y for y in fixed_y if ym <= y < yT]); hi_b = min([ym] + [y for y in fixed_y if yB < y <= ym])
            rT = lambda y: max(0.0, (y - lo_t)/max(1.0, yT - lo_t))      # không cắt ở 1: tay nắm vượt đỉnh / đáy cùng một phép affine
            rB = lambda y: max(0.0, (hi_b - y)/max(1.0, hi_b - yB))
            # δ lớn nhất sao cho mọi mẫu sau khi kéo (dày − δ·dốc) vẫn ≥ chuẩn; mẫu giới hạn chạm đúng chuẩn
            def delta(smp, r):
                amin = 0.3 if hole[gi] else 0.937                 # lòng hở: chỉ mẫu tiếp tuyến gần ngang (≤ 20°) — vai / đầu nét mảnh chủ ý không giới hạn
                ds = [(h - tgt/an)/r(y) for h, _, y, an, x in smp if r(y) > 0.15 and an >= amin and 0.5*tgt <= h*an <= 1.8*tgt
                      and all(math.dist((x, y), fe) > 90 for fe in fixed_e)]   # < ½ chuẩn: mũi; gần đầu nét cắt (90 u): độ thuôn chủ ý
                return max(-0.4*tgt, min(ds)) if ds else 0.0                     # âm: nét đang mảnh hơn chuẩn → lòng co lại (dày lên)
            dT, dB = delta(top, rT), delta(bot, rB)
            if not hole[gi]: dT, dB = max(0.0, dT), max(0.0, dB)  # lòng hở (C c n u J…): chỉ kéo mảnh — đầu nét / vai mảnh là chủ ý
            sT = top[0][1] if top else 1; sB = bot[0][1] if bot else -1
            if abs(dT) < 0.5 and abs(dB) < 0.5: continue
            def f(y):
                if y > lo_t: return y + sT*dT*rT(y)
                if y < hi_b: return y + sB*dB*rB(y)
                return y
            pts = []
            for m in ch:
                A, Bs = g[m], g[(m + 1) % n]
                pts += ([A[3], A[4]] if A[0] == 'C' else [A[2]]) + ([Bs[1], Bs[2]] if Bs[0] == 'C' else [Bs[1]])
            for e in (e0, e1):
                if e is not None and slide(e):                    # góc trượt: dời cả tay nắm kề nó (cung không bị uốn ngược)
                    A, Bs = g[e], g[(e + 1) % n]; pts += [A[-1], Bs[1]] + ([A[3]] if A[0] == 'C' else []) + ([Bs[2]] if Bs[0] == 'C' else [])
            for q in {id(q): q for q in pts}.values(): q[1] = f(q[1])
            moved = True
        d = SB.to_d(cs)
        if not moved: break
    return d

# ---------- G11 thanh T: mép dưới thanh là cung loe chạy vào thân (không có đoạn thẳng) — designer 20/11 "thanh ngang của T sao lại
# dày hơn của các chữ khác". Điểm nối cung–thân (tiếp tuyến ngang, thân đứng) dời đứng δ = bề dày thanh (tia đứng tới mép trên) − chuẩn
# nét mảnh; tay nắm kề nó dời cùng (giữ ngang → cung trơn); đầu nhọn loe đứng yên.
TBAR = set('T')
DIAG_K = 1.0                   # chuẩn nét CHÉO = DIAG_K × chuẩn nét mảnh (hiệu chỉnh quang học; designer "nét xéo của golden mỏng quá")
BAR_K = 0.88                   # designer 20/11 chọn k 0.88 ("nét ngang F L T E Z dầy hơn nét còn lại") — chuẩn nét NGANG = BAR_K × chuẩn nét mảnh (hiệu chỉnh quang học)
def bar_thin(d, w, tgt=None):
    tgt = (RING_T[w] if tgt is None else tgt)*BAR_K
    cs = parse(d); P = polys(cs); n_ = 0
    for c in cs:
        S_ = segs(c); n = len(S_)
        for i in range(n):
            a, b = S_[i - 1], S_[i]
            node = b[1][0]
            if node[1] < 500: continue
            for cv, ln, hd in ((a, b, a[1][2] if a[0] == 'C' else None), (b, a, b[1][1] if b[0] == 'C' else None)):
                if cv[0] != 'C' or ln[0] == 'C' or hd is None: continue
                q = ln[1]
                if abs(q[0][0] - q[1][0]) > 0.5 or abs(hd[1] - node[1]) > 0.5: continue      # thân đứng + tiếp tuyến ngang tại điểm nối
                h = ray((node[0] + (3 if hd[0] < node[0] else -3)*-1, node[1]), (0, 1), P)
                if not h or h[0] > 2*tgt + 40: continue
                dl = h[0] - tgt
                if abs(dl) < 0.5: continue
                node[1] += dl; hd[1] += dl; n_ += 1
    return fmt(cs), n_

# ---------- G13 tay loe đầu thanh dài bằng nhau (designer 20/11 "phần loe của T và E đang không bằng nhau. Lẽ ra nó phải bằng nhau") ----------
# Mép cắt đứng ở đầu tay (gốc trên đường kẻ 0 / 700, dài 20–250) — độ sâu loe — đặt đúng ARM_D[w] cho MỌI tay (E F L T Z, phần E của Æ Œ):
# đầu mũi dời tới đường kẻ ∓ ARM_D; chuỗi cung loe (từ mũi tới tiếp tuyến ngang ở mép thanh, y = Y0) giãn đứng affine quanh Y0.
ARMD = set('EFLTZÆŒ')
ARM_D = {'Regular': 114.0, 'Bold': 148.0}          # Golden: theo T (tay thuần, nhận đủ G3b ×1.4); AnNam Serif đặt lại 94 / 122 (bản vẽ gốc)
def arm_depth(d, w):
    cs = parse(d); Dd = ARM_D[w]; n_ = 0
    for c in cs:
        S_ = segs(c); n = len(S_)
        for i in range(n):
            k, q = S_[i]
            if k == 'C' or abs(q[0][0] - q[1][0]) > 0.5: continue
            for g_ in (700.0, 0.0):
                ends = [p for p in q if abs(p[1] - g_) < 2.5]
                if len(ends) != 1: continue
                root = ends[0]; tip = q[1] if root is q[0] else q[0]
                old = abs(tip[1] - g_)
                if not (20 <= old <= 250) or abs(old - Dd) < 0.5: continue
                fwd = tip is q[1]                                   # chuỗi cung nối tiếp từ mũi
                j = (i + 1) % n if fwd else (i - 1) % n; chain = []
                while S_[j][0] == 'C' and len(chain) < 4:
                    chain.append(S_[j]); t = tan_end(*S_[j], not fwd)
                    if t and abs(t[1]) < 0.06: break
                    j = (j + 1) % n if fwd else (j - 1) % n
                else: continue
                if not chain: continue
                endp = chain[-1][1][3] if fwd else chain[-1][1][0]; Y0 = endp[1]
                sgn = -1 if g_ > 300 else 1                          # mũi nằm dưới đường 700 / trên đường 0
                dold = abs(tip[1] - Y0); dnew = abs((g_ + sgn*Dd) - Y0)
                if dold < 5: continue
                kf = dnew/dold; mv = []
                for _, cq in chain:
                    for p_ in cq:
                        if p_ is endp or any(p_ is m for m in mv): continue
                        mv.append(p_)
                hfar = chain[-1][1][2] if fwd else chain[-1][1][1]
                for p_ in mv:
                    if p_ is hfar: continue
                    p_[1] = Y0 + (p_[1] - Y0)*kf
                tip[1] = g_ + sgn*Dd; n_ += 1
    return fmt(cs), n_

# ---------- G14 chân l = chân t (designer 20/11 "dùng chân chữ t cho chân chữ l" — chỉ Golden) ----------
# Hai thân cùng bề dày → ghép: phần trên l (loe đỉnh + mép trái tới y = đầu cung móc t) + thân dưới & móc chân của t dời ngang cho trùng
# mép trái thân l + mép phải đi thẳng lên loe đỉnh l. Cấu trúc như nhau ở Regular / Bold → nội suy được.
def l_from_t(dl, dt):
    L = SB_contours(dl)[0]; T = SB_contours(dt)[0]
    # l: [0]L đáy [1]C loe phải dưới [2]L thân phải [3]C loe phải trên [4]L đỉnh [5]C loe trái trên [6]L thân trái [7]C loe trái dưới
    # t: [5]L thân trái xuống tới y0 · [6..10] móc chân · [11]C mép phải lên tới thanh
    xl = L[6][1][0]; dx = xl - T[5][1][0]; y0 = T[5][2][1]
    sh = lambda p: [p[0] + dx, p[1]]
    out = [L[3], L[4], L[5], ['L', list(L[6][1]), [xl, y0]]]
    for sg in T[6:12]: out.append([sg[0]] + [sh(p) for p in sg[1:]])
    top_r = L[3][1]
    out.append(['L', list(out[-1][-1]), list(top_r)])
    return SB_to_d([out])
def SB_contours(d):
    sys.path.insert(0, os.path.join(HERE, '..')); import stroke_balance as SB; return SB.contours(d)
def SB_to_d(cs):
    sys.path.insert(0, os.path.join(HERE, '..')); import stroke_balance as SB; return SB.to_d(cs)

# ---------- G15 thanh t hai bên thân mảnh đều (designer 20/11 "t thường gạch ngang 2 bên không mỏng đều nhau" — Golden) ----------
# Đầu t Golden: mép trên phần thanh bên trái là nét chéo của đầu t (không có mép song song) → G8 không làm mảnh được. Mép dưới mọi đoạn
# thanh (đoạn ngang 430–530, dài > 20) đặt về CÙNG độ cao = mép dưới cao nhất (phần thanh bên phải, đã đúng chuẩn); góc trượt trên mép đứng.
def tbar_eq(d):
    cs = parse(d); ls = []
    for c in cs:
        for k_, q in segs(c):
            if k_ == 'L' and abs(q[0][1] - q[1][1]) < 0.5 and 430 < q[0][1] < 530 and abs(q[0][0] - q[1][0]) > 20: ls.append(q)
    if len(ls) < 2: return d
    y = max(q[0][1] for q in ls)
    for q in ls:
        for p_ in q: p_[1] = y
    return fmt(cs)

# ---------- G8 đồng bộ nét mảnh mọi chữ (designer 20/11: "kiểm tra đồng bộ hết độ dày các nét mỏng") ----------
# Sau các luật trên, nét mảnh từng chữ gốc (Regular, Bold) đo lại; nét mảnh (≤ 1.4 × chuẩn) nhân thêm hệ số r = chuẩn / đo (lặp 3
# lượt, giới hạn 0.7–1.4) theo đúng luật G2 (mép lòng của cung, hai mép của đoạn thẳng). Chuẩn = RING_T (32 / 45). Chữ có dấu dùng r
# của chữ gốc. Bỏ qua chữ không có nét mảnh (i j l f r t I) — đo của chúng là thân.
NOHAIR = set('ijlfrtITı\u0237')
G8R = {}
def g8_apply(d, ch, w, r, low, xtop=None, abs_t=None):
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
    g2(cs, w, skip, fixed=fixed, thin=r, abs_t=abs_t)
    NOSPLIT[0] = old
    return fmt(cs)
def g8_solve(d, ch, w, low, xtop=None):
    """G8 tuyệt đối (S52, designer "thanh ngang của T sao lại dày hơn"): mỗi đoạn thẳng nét mảnh tự về đúng chuẩn RING_T — không còn
    một hệ số chung cho cả chữ (hệ số chung làm thanh P mảnh quá khi cung của nó mảnh hơn). 2 lượt (đo lại sau khi dời)."""
    cur = d
    for _ in range(2): cur = g8_apply(cur, ch, w, 1.0, low, xtop, abs_t=RING_T[w])
    return cur, 1.0

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

def drop_tiny(dR, dB, lim=2.0):
    """đoạn dài < lim u (ở một trong hai master) — mẩu nối của bản vẽ bị luật làm mảnh co lại: bỏ ở CẢ HAI master (giữ tương thích)"""
    R, B = parse(dR), parse(dB); n = 0
    if len(R) != len(B): return dR, dB, 0
    for cr, cb in zip(R, B):
        if len(cr) != len(cb): continue
        j = 1
        while j < len(cr) - 2:                                    # không đụng đoạn cuối (điểm khép contour)
            if cr[j][0] == cb[j][0] and cr[j][0] in 'LC':
                L = [math.dist(c[j - 1][1][-1], c[j][1][-1]) for c in (cr, cb)]
                if min(L) < lim:
                    del cr[j]; del cb[j]; n += 1; continue
            j += 1
    return (fmt(R), fmt(B), n) if n else (dR, dB, 0)
def lerp_d(a, b, t):
    A, B = parse(a), parse(b)
    for ca, cb in zip(A, B):
        for (_, pa), (_, pb) in zip(ca, cb):
            for p, q in zip(pa, pb): p[0] += (q[0] - p[0])*t; p[1] += (q[1] - p[1])*t
    return fmt(A)

def main():
    O = json.load(open(os.path.join(SRC, 'outlines.json'))); SP = json.load(open(os.path.join(SRC, 'spacing.json')))
    chars = list(SP['Regular']); low = set(lower_set(chars)); G = {}; NF = {'Regular': 0, 'Bold': 0}; NT = dict(NF)
    for c in chars:                                               # mẩu nối < 3 u của bản vẽ (nách K): bỏ TRƯỚC mọi luật (không có tiếp tuyến)
        if f'{c}-Regular' in O:
            O[f'{c}-Regular'], O[f'{c}-Bold'], _ = drop_tiny(O[f'{c}-Regular'], O[f'{c}-Bold'], 3.0)
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
        if c in TBAR:                                             # G11 thanh T = chuẩn nét mảnh
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = bar_thin(G[f'{c}-{w}'], w)[0]
        if c.isalpha() and len(c) == 1 and c.isascii() and c not in G10_SKIP:      # G10 nét mảnh cong (lòng kéo dãn đứng)
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = g10(G[f'{c}-{w}'], w)
        if c.isalpha() and len(c) == 1 and c.isascii():                          # G8 tuyệt đối mọi chữ gốc (đoạn thẳng nét mảnh = chuẩn, gồm thanh e f t)
            for w in ('Regular', 'Bold'):
                G[f'{c}-{w}'], G8R[(c, w)] = g8_solve(G[f'{c}-{w}'], c, w, low)
        if c in TCH:                                                  # G15 thanh t hai bên mảnh đều
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = tbar_eq(G[f'{c}-{w}'])
        if c in ARMD:                                                 # G13 tay loe đầu thanh dài bằng nhau (cả Æ Œ)
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = arm_depth(G[f'{c}-{w}'], w)[0]
        for w, t in TW.items(): G[f'{c}-{w}'] = lerp_d(G[f'{c}-Regular'], G[f'{c}-Bold'], t)
    if 'l-Regular' in G and 't-Regular' in G:                     # G14 chân l = chân t
        for w in ('Regular', 'Bold'): G[f'l-{w}'] = l_from_t(G[f'l-{w}'], G[f't-{w}'])
        for w, t in TW.items(): G[f'l-{w}'] = lerp_d(G['l-Regular'], G['l-Bold'], t)
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
    ntiny = []
    for c in chars:
        if f'{c}-Regular' not in G: continue
        G[f'{c}-Regular'], G[f'{c}-Bold'], k = drop_tiny(G[f'{c}-Regular'], G[f'{c}-Bold'])
        if k:
            ntiny.append(c)
            for w, t in TW.items(): G[f'{c}-{w}'] = lerp_d(G[f'{c}-Regular'], G[f'{c}-Bold'], t)
    print('bỏ đoạn siêu ngắn (< 2 u):', ''.join(ntiny))
    print('chữ có dấu ghép = chữ gốc + dấu:', nrb)
    print('G8 hệ số nét mảnh:', ' '.join(f'{c}{w[0]}{r:.2f}' for (c, w), r in sorted(G8R.items()) if abs(r - 1) > 0.02))
    os.makedirs(OUT, exist_ok=True)
    json.dump(G, open(os.path.join(OUT, 'outlines.json'), 'w'))
    print('G6 lòng giãn:', {f'{b}-{w}': round(k, 3) for (b, w), k in RINGK.items()})
    print('golden:', len(G), 'glyph ·', len(low), 'ký tự chữ thường nâng x-height', XH0, '→', XH1, '· loe phóng', NF, '· nút nét mảnh dời', NT)

if __name__ == '__main__':
    main()
