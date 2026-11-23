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
CAPS_AS_SERIF = False           # S72 (designer 22/11 "làm mỏng các nét mỏng của golden đồng loạt" — cả hoa lẫn thường): bỏ luật 20/11 "Golden hoa nên có độ dày y chang Serif"
FLARE_KX_CAP = 1.45            # designer 20/11: giữ size loe như cũ (thử ×2.9 bỏ)            # designer 20/11 "các chữ hoa Golden đuôi chân loe dài thêm ra thêm xíu" (chữ thường giữ 1.3)
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
                for p in fside + extra:                                 # phía chân: rộng × KX, cao × KY — theo hệ trục (dọc chân, dọc THÂN):
                    bb = (p[1] - C0[1])/td[1]; aa = (p[0] - C0[0]) - bb*td[0]  # thân chéo (K R X): cùng một phép phóng với phía thân
                    p[0] = C0[0] + FLK[0]*aa + FLARE_KY*bb*td[0]; p[1] = C0[1] + FLARE_KY*bb*td[1]   # (trước: trục x–y → cung loe gãy khúc)
                FLSEG.add((id(q[0]), id(q[3]))); n_fl += 1
    return n_fl

# ---------- G2b lòng vòm n m h / lòng đáy u: dịch nguyên khối (designer 20/11: "đường cong bụng trong chữ u, m, n không tự nhiên") ----------
ARCH = set()                   # (cũ: 'nmhuµ' dịch nguyên khối) — nay vòm / đáy u dùng G10 (dốc tuyến tính, vai cạnh thân gần đứng yên)
DIGIT_G8 = set('47')            # S72 (designer 22/11 "có, làm luôn số 4 7"): số theo bản vẽ riêng; chỉ 4 7 vào G8
SER_T = {'Regular': 34.0, 'Bold': 34.0}        # S78: Serif nay 34 mọi weight · S72: chuẩn nét mảnh AnNam Serif — chỉ dùng NHẬN DIỆN nét mảnh (ngưỡng), đích là RING_T / ARCH_T
ARCH_T = {'Regular': 34.0, 'Bold': 34.0}       # = RING_T (G8): bề dày đỉnh vòm sau khi dịch
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
                                    if hh and hh[0] < 2.2*max(ARCH_T[w], SER_T[w]): ds.append((hh[0] - ARCH_T[w])/abs(nv[1]))
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
            return (t - at_)/2*pin if 0.5*abs_t <= t <= 1.6*max(abs_t, SER_T[w]) else 0.0   # S72: nhận diện nét mảnh theo chuẩn Serif (chuẩn Golden 34 làm ngưỡng 1.6× bỏ sót bụng B D P R)
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
                    if own == 0.0 and abs_t is not None:                # S72 (designer 22/11 "đồng bộ hết … nét mỏng"): điểm giữa sát đỉnh
                        for tt in (0.7, 0.85, 0.3, 0.15):               # (V Bold: mép ngoài tách đôi ở y 344, tia giữa đoạn trúng nét kia)
                            p_ = (q[0][0] + (q[1][0] - q[0][0])*tt, q[0][1] + (q[1][1] - q[0][1])*tt)   # → thử dọc đoạn
                            own = shrink(p_, out, 20)
                            if own: break
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
    if unicodedata.normalize('NFD', ch)[0].isupper(): nf += g3b(cs)   # loe đầu tay chỉ cho chữ HOA (m n: đầu cờ x-height không phải tay)
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
RING_T = {'Regular': 34.0, 'Bold': 34.0}   # S78 designer 23/11 "mảnh hơn đồng loạt … bold không tăng" (trước 34 / 42) · S72 (designer 22/11 "làm mỏng các nét mỏng của golden đồng loạt … khi bold lên thì nét mỏng tăng ít thôi", chọn 34 → 42; trước 42 / 56.5 = Serif) · designer 20/11 "các nét mỏng của Golden đưa về bằng với nét mỏng của Serif" (trước 32 / 44)   # designer 20/11 "tại sao nó không bằng nhau": MỘT nét mảnh tuyệt đối cho mọi vòng (o O ơ Ơ …)
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
BAR_K = 0.88                   # designer 20/11 chọn k 0.88, giữ (quyết định cuối: "giữ nét ngang 0.88 như cũ") ("nét ngang F L T E Z dầy hơn nét còn lại") — chuẩn nét NGANG = BAR_K × chuẩn nét mảnh (hiệu chỉnh quang học)
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
    if len(L) != 8: return dl                                    # l đã mang chân t (AnNam Serif đã ghép) — giữ nguyên
    vert = lambda sg: sg[0] == 'L' and abs(sg[1][0] - sg[2][0]) < 0.5
    r = next(i for i, sg in enumerate(L) if vert(sg) and sg[1][1] < 250 and sg[2][1] > 500)      # mép phải thân l (đi lên)
    k = next(i for i, sg in enumerate(L) if vert(sg) and sg[1][1] > 500 and sg[2][1] < 250)      # mép trái thân l (đi xuống)
    i0 = next(i for i, sg in enumerate(T) if vert(sg) and sg[1][1] > 300 and sg[2][1] < 250)     # mép trái thân t xuống tới móc
    j = i0 + 1
    while T[j][-1][1] < 300: j += 1                                # móc chân + mép phải thân t lên tới mặt dưới thanh
    xl = L[k][1][0]; dx = xl - T[i0][1][0]; y0 = T[i0][2][1]
    sh = lambda p: [p[0] + dx, p[1]]
    out = [list(map(lambda v: v if isinstance(v, str) else list(v), sg)) for sg in L[r + 1:k]]
    out.append(['L', list(L[k][1]), [xl, y0]])
    for sg in T[i0 + 1:j + 1]: out.append([sg[0]] + [sh(p) for p in sg[1:]])
    out.append(['L', list(out[-1][-1]), list(L[r + 1][1])])
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

# ---------- G19 thanh số 4: G8 làm mảnh phần thanh bên trái thân (đáy 167 → 183 Regular) nhưng phần bên phải thân (dưới cung loe)
# giữ / dời khác → đáy hai bên lệch nhau (Regular 10 u, Bold 14 u) và phần phải dày 36 / 54. Luật: đáy phần phải = đáy phần trái; mép trên
# phần phải (cung loe, cả điểm đầu cung ở thân) hạ xuống bằng mép trên phần trái (= đáy lòng tam giác) → thanh một khối, dày chuẩn hai bên.
def bar4(d):
    cs = parse(d)
    if len(cs) < 2: return d
    c0 = cs[0]; P = pts_of(c0)
    hs = []                                                       # đoạn ngang thấp (đáy thanh)
    prev = None
    for k, ps in c0:
        if k == 'L' and prev is not None and abs(ps[0][1] - prev[1]) < 0.01 and 100 < ps[0][1] < 320 and abs(ps[0][0] - prev[0]) > 40: hs.append((prev, ps[0]))
        if ps: prev = ps[-1]
    if len(hs) != 2: return d
    (a1, b1), (a2, b2) = sorted(hs, key=lambda h: -max(h[0][0], h[1][0]))   # phải, trái
    yl = a2[1]; ytop = min(p[1] for p in pts_of(cs[1]))
    xs = min(a1[0], b1[0])                                        # mép phải thân
    for p in (a1, b1): p[1] = yl
    top = [p for p in P if p[0] >= xs - 0.01 and p[1] > ytop + 0.5 and p[1] < 320 and p[0] <= max(a1[0], b1[0]) + 0.01 and p not in (a1, b1)]
    if not top: return fmt(cs)
    y0 = min(p[1] for p in top if abs(p[0] - xs) < 0.01) if any(abs(p[0] - xs) < 0.01 for p in top) else None
    if y0 is None: return fmt(cs)
    dl = y0 - ytop; done = set()
    for p in top:
        if id(p) in done: continue
        done.add(id(p)); p[1] -= dl
    return fmt(cs)

# ---------- G20 nét mảnh bụng D P B R (designer 23/11 "chữ D và P nét mỏng vẫn chưa đủ mỏng như O"): tại chỗ giao thân nét mảnh đúng
# chuẩn nhưng mép lòng rời tiếp tuyến ngang ngay → nét dày nhanh (Serif D: 42 → 46 ở 80 u, 57 ở 140 u). Luật: kéo dài tay nắm ngang của lòng
# tại mép trong thân (cùng hệ số s cho mọi tay trong chữ) tới khi nét mảnh đo trục giữa (stroke_balance, bỏ khớp) = chuẩn như O.
STEMBOWL = set('DPBR')
def _stem_handles(cs):
    hs = []
    for c in _holes(cs):
        P = pts_of(c); xm = min(p[0] for p in P)
        prev = None
        for k, ps in c:
            if k == 'C':
                a, b, e = ps
                if prev is not None and abs(prev[0] - xm) < 0.6 and abs(a[1] - prev[1]) < 0.6 + 0.05*abs(a[0] - prev[0]) and a[0] > prev[0] + 1: hs.append((prev, a, b))   # tay ra khỏi nút ở thân
                if abs(e[0] - xm) < 0.6 and abs(b[1] - e[1]) < 0.6 + 0.05*abs(b[0] - e[0]) and b[0] > e[0] + 1: hs.append((e, b, a))                              # tay vào nút ở thân
            if ps: prev = ps[-1]
    return hs
def _vthick(cs, x, ytop):
    ys = []
    for P in polys(cs):
        for i in range(len(P)):
            (x1, y1), (x2, y2) = P[i - 1], P[i]
            if (x1 <= x) != (x2 <= x): ys.append(y1 + (x - x1)*(y2 - y1)/(x2 - x1))
    ys = sorted(y for y in ys if y > ytop - 200)
    return ys[-1] - ys[-2] if len(ys) >= 2 else None
def stem_bowl(d, tgt, k=1.15):
    """nét mảnh trên của bụng, đo đứng tại cuối đoạn phẳng mép ngoài (nơi bụng bắt đầu cong) ≤ k × chuẩn (O tăng ~15 % ở cùng độ xa vùng mảnh)"""
    cs = parse(d); hs = _stem_handles(cs)
    if not hs: return d, 1.0
    outer = cs[0]; P0 = [ps[-1] for k_, ps in outer if ps]; ymax = max(p[1] for p in P0)      # nút trên đường (bỏ tay nắm)
    xf = max(p[0] for p in P0 if abs(p[1] - ymax) < 0.5)
    base = [(n, h, o, h[0] - n[0]) for n, h, o in hs]
    def at(s_):
        for n, h, o, L in base: h[0] = n[0] + L*s_
    smax = min(2.2, min((o[0] - n[0] - 2)/L for n, h, o, L in base if L > 0))
    f = lambda s_: (at(s_), _vthick(cs, xf, ymax))[1]
    if f(1.0) is None or f(1.0) <= k*tgt: at(1.0); return fmt(cs), 1.0
    lo, hi = 1.0, max(1.0, smax)
    if f(hi) > k*tgt: return fmt(cs), hi
    for _ in range(25):
        m = (lo + hi)/2
        if f(m) > k*tgt: lo = m
        else: hi = m
    at(hi); return fmt(cs), hi

JOINT_K = 0.65                 # G20 (designer 23/11): phần nối bụng–thân D P B R = 0.65 × nét mảnh Regular, MỌI weight bằng nhau ("khi bold lên không tăng độ dày nét mỏng")
def joint_thin(d, tgt):
    """G20: nút lòng chạm thân (tay nắm ngang) dời về phía mép ngoài / lòng kia (cùng tay nắm) → khe tại chỗ nối = tgt; cung lòng giữ nguyên
    phía xa → nét mảnh mỏng ở chỗ nối rồi cong lài ra."""
    cs = parse(d); hs = _stem_handles(cs); done = set()
    for n, h, o in hs:
        if id(n) in done: continue
        done.add(id(n))
        hole = [c for c in _holes(cs) if any(p is n for p in pts_of(c))]
        if not hole: continue
        hole = hole[0]; ys_h = [p[1] for p in polys([hole])[0]]; up = n[1] > (min(ys_h) + max(ys_h))/2
        x = n[0] + 1.0; ys = []
        for P in polys([c for c in cs if c is not hole]):
            for i in range(len(P)):
                (x1, y1), (x2, y2) = P[i - 1], P[i]
                if (x1 <= x) != (x2 <= x): ys.append(y1 + (x - x1)*(y2 - y1)/(x2 - x1))
        ys = [y for y in ys if (y > n[1] if up else y < n[1])]
        if not ys: continue
        yo = min(ys) if up else max(ys); dl = abs(yo - n[1]) - tgt
        if abs(dl) < 0.3: continue
        sg = 1 if up else -1; n[1] += sg*dl; h[1] += sg*dl
    return fmt(cs)

def seven_bar(d, tgt):
    """số 7: thanh trên dày = tgt, GIỮ mặt trên ở chiều cao hoa (G8 tự chọn mép có thể hạ mặt trên). Mép dưới thanh + vạt loe trái dời lên;
    góc trong thanh–chéo trượt dọc mép trong nét chéo."""
    cs = parse(d); c0 = cs[0]; P = pts_of(c0)
    top = max(p[1] for p in P)
    hz = [p for p in P if abs(p[1] - top) > 0.5 and p[1] > top - 160]
    ys = sorted({round(p[1], 1) for p in hz})
    if not ys: return d
    yb = max(ys, key=lambda y: sum(1 for p in hz if abs(p[1] - y) < 0.6))     # mép dưới thanh (nhiều nút nhất)
    dl = (top - yb) - tgt
    if abs(dl) < 0.3: return d
    corner = max((p for p in hz if abs(p[1] - yb) < 0.6), key=lambda p: p[0])   # góc trong thanh–chéo
    i = P.index(corner); prev = P[i - 1]                                       # nút trước = chân mép trong chéo
    done = set()
    for p in P:
        if id(p) in done or p is corner: continue
        if p[1] < top - 0.5 and p[1] > yb - 90 and p[0] < corner[0] - 1: done.add(id(p)); p[1] += dl
    y2 = corner[1] + dl
    if abs(corner[1] - prev[1]) > 1: corner[0] = prev[0] + (corner[0] - prev[0])*(y2 - prev[1])/(corner[1] - prev[1])
    corner[1] = y2
    return fmt(cs)

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
    A, B = parse(a), parse(b); done = set()                       # parse dùng chung đối tượng điểm (điểm khép = điểm M): nội suy MỖI điểm một lần
    for ca, cb in zip(A, B):
        for (_, pa), (_, pb) in zip(ca, cb):
            for p, q in zip(pa, pb):
                if id(p) in done: continue
                done.add(id(p)); p[0] += (q[0] - p[0])*t; p[1] += (q[1] - p[1])*t
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
        CAP_ = b_.isupper() and CAPS_AS_SERIF                         # chữ HOA: độ dày y như AnNam Serif (chỉ khác loe)
        if b_ in EFAM and not CAP_:                                   # G9 đỉnh e = chuẩn nét mảnh
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = e_top(G[f'{c}-{w}'], RING_T[w])
        if b_ in SFAM and not CAP_:                                   # G7 s S: nét mảnh = RING_T (cùng chuẩn vòng), mép lòng, lặp Newton
            for w in ('Regular', 'Bold'):
                G[f'{c}-{w}'] = s_thin(G[f'{c}-{w}'], w)
        if b_ in RING and not CAP_:
            for w in ('Regular', 'Bold'):
                base = RING[b_]
                if (base, w) not in RINGK: RINGK[(base, w)] = solve_ring(O[f'{base}-{w}'], G[f'{base}-{w}'], w, base == 'Q')
                G[f'{c}-{w}'] = ring_scale(G[f'{c}-{w}'], RINGK[(base, w)], base == 'Q')
        if c in TBAR and not CAP_:                                    # G11 thanh T = chuẩn nét mảnh
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = bar_thin(G[f'{c}-{w}'], w)[0]
        if c.isalpha() and len(c) == 1 and c.isascii() and c not in G10_SKIP and not CAP_:      # G10 nét mảnh cong (lòng kéo dãn đứng)
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = g10(G[f'{c}-{w}'], w)
        if ((c.isalpha() and len(c) == 1 and c.isascii()) or c in DIGIT_G8) and not CAP_:   # G8 tuyệt đối mọi chữ gốc (đoạn thẳng nét mảnh = chuẩn, gồm thanh e f t); S72: + số 4 7
            for w in ('Regular', 'Bold'):
                G[f'{c}-{w}'], G8R[(c, w)] = g8_solve(G[f'{c}-{w}'], c, w, low)
        if c == '4':                                                  # G19 thanh số 4 một đường thẳng xuyên thân (designer 23/11 "sửa luôn thanh số 4")
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = bar4(G[f'{c}-{w}'])
        if c in TCH:                                                  # G15 thanh t hai bên mảnh đều
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = tbar_eq(G[f'{c}-{w}'])
        if c in ARMD:                                                 # G13 tay loe đầu thanh dài bằng nhau (cả Æ Œ)
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = arm_depth(G[f'{c}-{w}'], w)[0]
        for w, t in TW.items(): G[f'{c}-{w}'] = lerp_d(G[f'{c}-Regular'], G[f'{c}-Bold'], t)
    for c in APEX_KEEP:                                            # G16 đỉnh A cắt như AnNam Serif
        if f'{c}-Regular' not in G: continue
        for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = apex_keep(G[f'{c}-{w}'], O[f'{c}-{w}'])
        for w, t in TW.items(): G[f'{c}-{w}'] = lerp_d(G[f'{c}-Regular'], G[f'{c}-Bold'], t)
    if 'B-Regular' in G:                                          # G18 eo B = chuẩn nét ngang Golden
        for w in ('Regular', 'Bold'): G[f'B-{w}'] = b_waist(G[f'B-{w}'], RING_T[w]*BAR_K)
        for w, t in TW.items(): G[f'B-{w}'] = lerp_d(G['B-Regular'], G['B-Bold'], t)
    for c in STEMBOWL:                                            # G20 phần nối bụng–thân D P B R mỏng (sau G18 eo B)
        if f'{c}-Regular' not in G: continue
        for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = joint_thin(G[f'{c}-{w}'], JOINT_K*RING_T['Regular'])
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
    nh = 0
    for c in chars:                                               # G17 chữ có sừng = chữ không sừng đã xử lý + sừng (từng weight)
        b2 = no_horn(c)
        if not b2 or f'{c}-Regular' not in G or f'{b2}-Regular' not in G: continue
        rr = {w: horn_splice(O[f'{c}-{w}'], O[f'{b2}-{w}'], G[f'{b2}-{w}']) for w in ('Regular', 'Bold')}   # ghép sừng không boolean → R / B cùng cấu trúc
        if all(rr.values()) and horn_compat(rr['Regular'], rr['Bold']):
            for w in ('Regular', 'Bold'): G[f'{c}-{w}'] = rr[w]
            for w, t in TW.items(): G[f'{c}-{w}'] = lerp_d(rr['Regular'], rr['Bold'], t)
            nh += 1
        else: print('G17 không ghép được (giữ cách cũ):', c)
    print('G17 chữ có sừng = chữ gốc + sừng:', nh)
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

# ---------- G16 đỉnh A giữ mặt cắt (designer 23/11 "đầu A golden bị nhọn chứ không phải cắt như Serif") ----------
# Làm mảnh nét trái A (42 → 34) dời mép ngoài song song → đầu mép trượt trên đường cap, mặt cắt đỉnh hẹp lại (Regular 23 → 19 u,
# Bold 5.4 u → chéo nhau thành nhọn). Đặt lại: điểm trái mặt cắt = điểm phải − bề rộng mặt cắt AnNam Serif (mép mảnh xoay < 1°).
APEX_KEEP = set('AÆ')
APEX_W = 23.3                    # S76 (designer 23/11 "kích thước cắt các weight của A không đều"): mặt cắt đỉnh A mọi weight = Regular

def _isect(p, u, q, v):
    """giao đường (p, hướng u) × (q, hướng v)"""
    den = u[0]*v[1] - u[1]*v[0]
    if abs(den) < 1e-12: return None
    t = ((q[0] - p[0])*v[1] - (q[1] - p[1])*v[0])/den
    return (p[0] + u[0]*t, p[1] + u[1]*t)

def apex_set(d, W):
    """đỉnh A: mặt cắt rộng đúng W. Mép ngoài nét mảnh XOAY quanh điểm chân B (đầu trên = điểm phải − W); mép trong dựng lại song song,
    cách đúng bề dày hiện tại (góc thanh ngang, đỉnh lòng, đoạn chân dưới thanh = giao điểm) → chân loe giữ, nét mảnh đều"""
    cs = parse(d)
    ys = max((pts[-1][1] for c in cs for cmd, pts in c if pts), default=0)
    for c in cs:                                                    # mép ngoài: đoạn L tới điểm đỉnh từ dưới-trái
        for k, (cmd, pts) in enumerate(c):
            if cmd == 'L' and abs(pts[-1][1] - ys) < 0.6 and k > 0 and c[k - 1][1] and c[k - 1][1][-1][1] < ys - 300 and c[k - 1][1][-1][0] < pts[-1][0] + 1:
                L_ = pts[-1]; B = c[k - 1][1][-1]; outer = c; break
        else: continue
        break
    else: return d
    R_ = next((pts[-1] for cmd, pts in outer if pts and abs(pts[-1][1] - ys) < 0.6 and pts[-1] is not L_), None)
    if R_ is None: return d
    u0 = (L_[0] - B[0], L_[1] - B[1]); n0 = math.hypot(*u0); u0 = (u0[0]/n0, u0[1]/n0)
    # lòng: contour không chứa điểm đỉnh; mép trong = đoạn song song u0
    inner = None
    for c in cs:
        if c is outer: continue
        P = [pts[-1] for cmd, pts in c if pts]; n = len(P)
        for i in range(n):
            p1, p2 = P[i], P[(i + 1) % n]; v = (p2[0] - p1[0], p2[1] - p1[1]); vn = math.hypot(*v)
            if vn > 50 and abs(v[0]/vn*u0[1] - v[1]/vn*u0[0]) < 0.03:
                lo, hi = (p1, p2) if p1[1] < p2[1] else (p2, p1)
                other = next(P[j] for j in range(n) if P[j] is not lo and P[j] is not hi)
                inner = (lo, hi, other); break
        if inner: break
    if not inner: return d
    lo, hi, other = inner
    t = abs((lo[0] - B[0])*u0[1] - (lo[1] - B[1])*u0[0])                 # bề dày nét mảnh hiện tại
    Lnew = (R_[0] - W, ys); u = (Lnew[0] - B[0], Lnew[1] - B[1]); nu = math.hypot(*u); u = (u[0]/nu, u[1]/nu)
    nrm = (u[1], -u[0])
    if (lo[0] - B[0])*nrm[0] + (lo[1] - B[1])*nrm[1] < 0: nrm = (-nrm[0], -nrm[1])
    Q = (B[0] + nrm[0]*t, B[1] + nrm[1]*t)                              # một điểm trên mép trong mới
    L_[0], L_[1] = Lnew
    hx = (hi[0] - other[0], hi[1] - other[1])
    lo_n = _isect(Q, u, lo, (1, 0)); hi_n = _isect(Q, u, other, hx)
    if lo_n is None or hi_n is None: return d
    lo[0], lo[1] = lo_n; hi[0], hi[1] = hi_n
    for k, (cmd, pts) in enumerate(outer):                          # đoạn chân dưới thanh (song song cũ, không phải mép ngoài)
        if cmd != 'L' or pts[-1] is L_ or k == 0 or not outer[k - 1][1]: continue
        a_ = outer[k - 1][1][-1]; b_ = pts[-1]; v = (b_[0] - a_[0], b_[1] - a_[1]); vn = math.hypot(*v)
        if vn < 30 or abs(v[0]/vn*u0[1] - v[1]/vn*u0[0]) > 0.03 or max(a_[1], b_[1]) > ys - 100: continue
        for q_ in (a_, b_):
            r = _isect(Q, u, q_, (1, 0)); dxq = r[0] - q_[0]; q_[0] = r[0]
            if q_ is b_ and k + 1 < len(outer) and outer[k + 1][0] == 'C': outer[k + 1][1][0][0] += dxq
            if q_ is a_ and outer[k - 1][0] == 'C': outer[k - 1][1][1][0] += dxq
    return fmt(cs)

def apex_keep(d, d_serif):
    """Golden: mặt cắt đỉnh = AnNam Serif (= APEX_W)"""
    return apex_set(d, APEX_W)

# ---------- G17 chữ có sừng = chữ không sừng đã đồng bộ + mảnh sừng (designer 23/11 "nét mỏng chữ Ở bị mảnh hơn các chữ O còn lại",
# "các nét mảnh của golden vẫn không đều nhau"): sừng dính liền thân → rebase không khớp contour → Ơ Ư xử lý riêng, vòng / thân lệch O U
# (Serif Ơ Bold 68 / O 57; Golden ư 41 / u 34). Thân + dấu = Ó Ò … đã đồng bộ (tịnh tiến như ở nguồn); sừng = phần nguồn ngoài thân
# (thành phần chạm thân), kèm dải chồng 6 u vào thân.
import pathops
HORN = '\u031b'
G17_SKIP = set()           # (S77: horn_splice thay boolean — không còn chữ phải bỏ qua)
def _pp(d):
    p = pathops.Path()
    for c in parse(d):
        for cmd, pts in c:
            if cmd == 'M': p.moveTo(*pts[0])
            elif cmd == 'L': p.lineTo(*pts[0])
            elif cmd == 'C': p.cubicTo(*pts[0], *pts[1], *pts[2])
            elif cmd == 'Z': p.close()
    return p
def _pd(p):
    s_ = ''; last_ = None; first_ = None
    for v, pts in p.segments:
        if pts: last_n = tuple(pts[-1])
        if v == 'moveTo': s_ += 'M%.2f %.2f' % tuple(pts[0]); first_ = tuple(pts[0])
        elif v == 'lineTo': s_ += 'L%.2f %.2f' % tuple(pts[0])
        elif v == 'curveTo': s_ += 'C' + ' '.join('%.2f %.2f' % tuple(q) for q in pts)
        elif v == 'qCurveTo':
            q0 = last_
            for k in range(len(pts) - 1):
                c_ = pts[k]; e_ = pts[k + 1] if k == len(pts) - 2 else ((pts[k][0] + pts[k + 1][0])/2, (pts[k][1] + pts[k + 1][1])/2)
                c1 = (q0[0] + 2/3*(c_[0] - q0[0]), q0[1] + 2/3*(c_[1] - q0[1])); c2 = (e_[0] + 2/3*(c_[0] - e_[0]), e_[1] + 2/3*(c_[1] - e_[1]))
                s_ += 'C%.2f %.2f %.2f %.2f %.2f %.2f' % (*c1, *c2, *e_); q0 = e_
        elif v in ('closePath', 'endPath'): s_ += 'Z'
        if v in ('closePath', 'endPath'): last_ = first_
        elif pts: last_ = tuple(pts[-1])
    return s_
def _op(a, b, op): return pathops.op(a, b, op)
def no_horn(c):
    n = unicodedata.normalize('NFD', c)
    return unicodedata.normalize('NFC', n.replace(HORN, '')) if HORN in n else None
def horn_compat(a, b):
    sig = lambda d: [[k for k, _ in c] for c in parse(d)]
    return sig(a) == sig(b)
def horn_compose(src_c, src_b, new_b):
    SC, SB_ = parse(src_c), parse(src_b)
    dx, dy = horn_align(SC, SB_)
    mv = lambda d: fmt([[[k, [[x + dx, y + dy] for x, y in ps]] for k, ps in c] for c in parse(d)])
    srcC = _pp(src_c); srcB = _pp(mv(src_b)); newB = _pp(mv(new_b))
    return _horn_bool(srcC, srcB, newB)
def horn_align(SC, SB_):
    dx = dy = None                                                 # tịnh tiến thân: contour lòng khớp hình (nguồn)
    for sb in SB_:
        for sc in SC:
            P, Q = pts_of(sc), pts_of(sb)
            if [k for k, _ in sc] != [k for k, _ in sb] or len(P) != len(Q): continue
            ddx, ddy = P[0][0] - Q[0][0], P[0][1] - Q[0][1]
            if max(abs(p[0] - q[0] - ddx) + abs(p[1] - q[1] - ddy) for p, q in zip(P, Q)) < 0.5: dx, dy = ddx, ddy; break
        if dx is not None: break
    if dx is None:                                                 # dự phòng: căn trọng tâm lòng (contour ngược chiều lớn nhất)
        def cen(cs_):
            best = None
            for c in cs_:
                P = pts_of(c)
                if len(P) < 3: continue
                a = 0.5*sum(P[i-1][0]*P[i][1] - P[i][0]*P[i-1][1] for i in range(len(P)))
                if best is None or abs(a) > abs(best[0]): best = (a, c)
            outer_sign = best[0] > 0 if best else True
            hs = [c for c in cs_ if len(pts_of(c)) >= 3 and (0.5*sum(pts_of(c)[i-1][0]*pts_of(c)[i][1] - pts_of(c)[i][0]*pts_of(c)[i-1][1] for i in range(len(pts_of(c)))) > 0) != outer_sign]
            if not hs: return None
            h = max(hs, key=lambda c: (max(p[0] for p in pts_of(c)) - min(p[0] for p in pts_of(c)))*(max(p[1] for p in pts_of(c)) - min(p[1] for p in pts_of(c))))
            P = pts_of(h); return ((min(p[0] for p in P) + max(p[0] for p in P))/2, (min(p[1] for p in P) + max(p[1] for p in P))/2)
        a_, b_ = cen(SC), cen(SB_)
        if a_ is not None and b_ is not None: dx, dy = a_[0] - b_[0], a_[1] - b_[1]
        else:                                                      # không có lòng kín (U): căn mép trái + mép dưới thân (sừng ở trên-phải)
            allc = [p for c in SC for p in pts_of(c)]; allb = [p for c in SB_ for p in pts_of(c)]
            dx = min(p[0] for p in allc) - min(p[0] for p in allb); dy = min(p[1] for p in allc) - min(p[1] for p in allb)
    return dx, dy
def _horn_bool(srcC, srcB, newB):
    diff = _op(srcC, srcB, pathops.PathOp.DIFFERENCE)
    band = pathops.Path(); band.addPath(srcB); band.stroke(12, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4); band.convertConicsToQuads()
    horn = pathops.Path()
    for cont in diff.contours:                                     # thành phần chạm thân = sừng (dấu là thành phần rời)
        q = pathops.Path(); q.addPath(cont)
        if list(_op(q, band, pathops.PathOp.INTERSECTION).segments): horn = _op(horn, q, pathops.PathOp.UNION)
    if not list(horn.segments): return None
    hb = pathops.Path(); hb.addPath(horn); hb.stroke(12, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4); hb.convertConicsToQuads()
    hb = _op(_op(hb, horn, pathops.PathOp.UNION), srcC, pathops.PathOp.INTERSECTION)   # sừng + dải 6 u (trong nét nguồn)
    out = _op(newB, hb, pathops.PathOp.UNION); out.convertConicsToQuads()
    return _pd(out)

def _bz(seg, t):
    """điểm trên đoạn (p0, cmd, pts) tại t"""
    p0, k, ps = seg
    if k == 'L': return (p0[0] + (ps[0][0] - p0[0])*t, p0[1] + (ps[0][1] - p0[1])*t)
    a, b, c_, d_ = p0, ps[0], ps[1], ps[2]; u = 1 - t
    return tuple(u**3*a[i] + 3*u*u*t*b[i] + 3*u*t*t*c_[i] + t**3*d_[i] for i in (0, 1))
def _cut(seg, t0, t1):
    """phần [t0, t1] của đoạn → (cmd, pts)"""
    p0, k, ps = seg
    if k == 'L': return ('L', [list(_bz(seg, t1))])
    P = [p0, ps[0], ps[1], ps[2]]
    def sub(P, t):                                                  # de Casteljau: (trái, phải)
        a = [[P[i][j] + (P[i+1][j] - P[i][j])*t for j in (0, 1)] for i in range(3)]
        b = [[a[i][j] + (a[i+1][j] - a[i][j])*t for j in (0, 1)] for i in range(2)]
        c_ = [b[0][j] + (b[1][j] - b[0][j])*t for j in (0, 1)]
        return [P[0], a[0], b[0], c_], [c_, b[1], a[2], P[3]]
    R = sub(P, t0)[1] if t0 > 0 else P
    tt = (t1 - t0)/(1 - t0) if t0 < 1 else 1
    L = sub(R, tt)[0] if tt < 1 else R
    return ('C', [list(L[1]), list(L[2]), list(L[3])])
def _segs(c):
    out, cur = [], None
    for k, ps in c:
        if k == 'M': cur = ps[0]
        elif k in 'LC': out.append((tuple(cur), k, ps)); cur = ps[-1]
    if out and (abs(out[-1][2][-1][0] - out[0][0][0]) > 1e-6 or abs(out[-1][2][-1][1] - out[0][0][1]) > 1e-6):
        out.append((tuple(cur), 'L', [list(out[0][0])]))
    return out
def _near(segs, q):
    best = None
    for i, sg in enumerate(segs):
        for n in range(0, 201):
            t = n/200; p = _bz(sg, t); dd = (p[0] - q[0])**2 + (p[1] - q[1])**2
            if best is None or dd < best[0]: best = (dd, i, t)
    dd, i, t = best; h = 1/200                                     # tinh chỉnh quanh t
    for _ in range(40):
        for t_ in (max(0.0, t - h), min(1.0, t + h)):
            p = _bz(segs[i], t_); d2 = (p[0] - q[0])**2 + (p[1] - q[1])**2
            if d2 < dd: dd, t = d2, t_
        h *= 0.6
    return (dd, i, t)
HORN_CUT = [None]
def horn_splice(src_c, src_b, new_b, tol=2.5):
    """G17 (bản tương thích R / B): sừng = chuỗi đoạn của contour nguồn chữ có sừng nằm NGOÀI chữ gốc nguồn (J1 → J2);
    cắt contour chữ gốc mới tại điểm gần J1 / J2 nhất và chèn chuỗi sừng vào (nối bằng đoạn thẳng ngắn). Không dùng boolean →
    cấu trúc điểm của Regular / Bold giống nhau (nội suy / variable đúng)."""
    SC, SB_ = parse(src_c), parse(src_b)
    dx, dy = horn_align(SC, SB_)
    NB = [[[k, [[x + dx, y + dy] for x, y in ps]] for k, ps in c] for c in parse(new_b)]
    SBm = [[[k, [[x + dx, y + dy] for x, y in ps]] for k, ps in c] for c in SB_]
    sb_segs = [_segs(c) for c in SBm]
    def on_b(q):
        return min(_near(ss, q)[0] for ss in sb_segs if ss) <= tol*tol
    run = None
    for c in SC:
        sg = _segs(c); n = len(sg)
        off = [not on_b(sg[i][2][-1]) for i in range(n)]            # điểm cuối đoạn i nằm ngoài chữ gốc
        if not any(off) or all(off): continue
        i0 = next(i for i in range(n) if off[i] and not off[i - 1])   # đoạn đầu tiên đi ra khỏi chữ gốc
        j = i0
        while off[j % n]: j += 1
        if sum(1 for i in range(n) if off[i] and not off[i - 1]) != 1: return None   # một sừng / contour
        run = [sg[k % n] for k in range(i0, j + 1)]; src_cont = c; break
    if not run: return None
    PL = polys(NB)                                                  # cắt chuỗi sừng tại chỗ ra / vào thân MỚI (thân Golden cao hơn nguồn)
    def inside(q):
        k = 0
        for P in PL:
            for i in range(len(P)):
                (x1, y1), (x2, y2) = P[i - 1], P[i]
                if (y1 > q[1]) != (y2 > q[1]) and q[0] < x1 + (q[1] - y1)*(x2 - x1)/(y2 - y1): k += 1
        return k % 2 == 1
    def bis(sg, a, b):                                              # inside(a) != inside(b) → t biên
        ia = inside(_bz(sg, a))
        for _ in range(30):
            m = (a + b)/2
            if inside(_bz(sg, m)) == ia: a = m
            else: b = m
        return (a + b)/2
    samp = [(i, n/40) for i in range(len(run)) for n in range(0, 41)]
    ins = [inside(_bz(run[i], t)) for i, t in samp]
    if all(ins): return None
    if not any(ins): ins = [True] + [False]*(len(samp) - 2) + [True]   # hai đầu nằm đúng trên biên thân mới
    e = next(k for k in range(1, len(samp)) if ins[k - 1] and not ins[k]) if ins[0] else 0
    f = next(k for k in range(len(samp) - 1, 0, -1) if ins[k] and not ins[k - 1]) if ins[-1] else len(samp) - 1
    (ia, ta), (ib, tb) = samp[e], samp[f]
    if e == 1 and not inside(_bz(run[0], 0.0)): ta = 0.0
    elif ins[0]: ta = bis(run[ia], samp[e - 1][1] if samp[e - 1][0] == ia else 0.0, ta)
    if f == len(samp) - 1 and not inside(_bz(run[-1], 1.0)): tb = 1.0
    elif ins[-1]: tb = bis(run[ib], samp[f - 1][1] if samp[f - 1][0] == ib else 0.0, tb)
    new_run = []
    for i in range(ia, ib + 1):
        t0 = ta if i == ia else 0.0; t1 = tb if i == ib else 1.0
        if t1 - t0 < 1e-4: continue
        st = _bz(run[i], t0); k_, ps_ = _cut(run[i], t0, t1); new_run.append((st, k_, ps_))
    if not new_run: return None
    run = new_run
    J1, J2 = run[0][0], run[-1][2][-1]
    area = lambda sg: sum(a_[0]*b_[1] - b_[0]*a_[1] for a_, b_ in zip([x[0] for x in sg], [x[0] for x in sg[1:] + sg[:1]]))
    s_src = area(_segs(src_cont))
    for ci, c in enumerate(NB):
        sg = _segs(c)
        if not sg: continue
        if (area(sg) > 0) != (s_src > 0):                               # thân mới ngược chiều contour nguồn → đảo
            sg = [(tuple(ps[-1]), k, ([[p0[0], p0[1]]] if k == 'L' else [ps[1], ps[0], [p0[0], p0[1]]])) for p0, k, ps in reversed(sg)]
        a, b = _near(sg, J1), _near(sg, J2)
        if a[0] > 40**2 or b[0] > 40**2: continue
        (_, i1, t1), (_, i2, t2) = a, b
        snap = lambda i, t: (i, 0.0) if t < 0.03 else (((i + 1) % len(sg), 0.0) if t > 0.97 else (i, t))   # bám điểm neo: R / B cắt cùng đoạn
        (i1, t1), (i2, t2) = snap(i1, t1), snap(i2, t2)
        HORN_CUT[0] = (ci, i1, i2)
        if (i1, t1) == (i2, t2): return None
        n = len(sg); out = []
        p1 = _bz(sg[i1], t1); p2 = _bz(sg[i2], t2)
        # J2' → … → J1' (phần thân giữ lại), rồi J1' → J1 → sừng → J2 → J2'
        segs_keep = []
        if i2 == i1 and t2 < t1: return None
        k = i2; tstart = t2
        while True:
            if k % n == i1 and (k != i2 or t1 > tstart):
                if t1 > tstart: segs_keep.append(_cut(sg[i1], tstart, t1))
                break
            if tstart < 1: segs_keep.append(_cut(sg[k % n], tstart, 1.0))
            k += 1; tstart = 0.0
            if k - i2 > n + 1: return None
        cont = [['M', [list(p2)]]] + [[kk, ps] for kk, ps in segs_keep]
        hr = [[kk, [list(p) for p in ps]] for _, kk, ps in run]
        d1 = (p1[0] - J1[0])**2 + (p1[1] - J1[1])**2; d2 = (p2[0] - J2[0])**2 + (p2[1] - J2[1])**2
        if d1 > 15**2 or d2 > 15**2: return None
        if d1 > 1.0: hr = [['L', [list(J1)]]] + hr                       # đầu sừng nguồn nằm ngoài thân mới (thân Golden hẹp hơn): nối thẳng vào thân
        if d2 > 1.0: hr = hr + [['L', [list(p2)]]]
        else: hr[-1][1][-1] = list(p2)                                 # J ≈ p: trùng điểm, không đoạn suy biến
        cont += hr + [['Z', []]]
        NB[ci] = cont
        return fmt(NB)
    return None

# ---------- G18 eo B = chuẩn nét mảnh (designer 23/11 "sửa luôn Ơ Ư, D, B các cho đều nét mảnh"): eo giữa hai bụng là hai CUNG
# (đáy lòng trên, đỉnh lòng dưới) → G8 (đoạn thẳng) bỏ sót: Serif Bold 44 / 56.5, Golden Regular 27 / 30. Đo khe hẹp nhất giữa hai lòng
# (dọc), dời đáy lòng trên lên và đỉnh lòng dưới xuống mỗi bên ½ phần thiếu / thừa (điểm cực + tay nắm kề).
def _holes(cs):
    out = []
    for c in cs:
        P = pts_of(c)
        if len(P) < 3: continue
        a = 0.5*sum(P[i-1][0]*P[i][1] - P[i][0]*P[i-1][1] for i in range(len(P)))
        out.append((a, c))
    big = max(out, key=lambda t: abs(t[0]))[0]
    return [c for a, c in out if (a > 0) != (big > 0)]
def b_waist(d, tgt):
    cs = parse(d); H = _holes(cs)
    if len(H) != 2: return d
    sm = lambda c, k: sum(p[1] for p in pts_of(c))/len(pts_of(c))
    up, lo = sorted(H, key=lambda c: -sm(c, 0))
    def sample(c, n=60):
        out = []
        for cmd, pts in c:
            pass
        P = polys([c])[0]; return P
    PU, PL = polys([up])[0], polys([lo])[0]
    allx = [p[0] for c in cs for p in pts_of(c)]; gx0, gx1 = min(allx), max(allx)
    xs0 = max(min(p[0] for p in PU), min(p[0] for p in PL), gx0 + 0.35*(gx1 - gx0))      # đo ở 35–80 % bề ngang (giữa eo, xa thân)
    xs1 = min(max(p[0] for p in PU), max(p[0] for p in PL), gx0 + 0.80*(gx1 - gx0))
    if xs1 - xs0 < 20: return d
    def yat(P, x, low):
        ys = []
        for i in range(len(P)):
            (x1, y1), (x2, y2) = P[i - 1], P[i]
            if (x1 - x) * (x2 - x) <= 0 and x1 != x2: ys.append(y1 + (y2 - y1)*(x - x1)/(x2 - x1))
        return (min(ys) if low else max(ys)) if ys else None
    gaps = []
    for k in range(0, 41):
        x = xs0 + (xs1 - xs0)*k/40; a = yat(PU, x, True); b = yat(PL, x, False)
        if a is not None and b is not None: gaps.append(a - b)
    if not gaps: return d
    g = min(gaps); dl = (tgt - g)/2
    if abs(dl) < 0.3: return d
    ymin_u = min(p[1] for p in pts_of(up)); ymax_l = max(p[1] for p in pts_of(lo))
    def shift(c, yref, dy):
        for cmd, pts in c:
            for q in pts:
                if abs(q[1] - yref) < 1.5: q[1] += dy
    shift(up, ymin_u, dl); shift(lo, ymax_l, -dl)
    return fmt(cs)

if __name__ == '__main__':
    main()

# ---------- G21 dấu sắc / huyền cắt ngang (designer 23/11 "dấu sắc và huyền nên cắt như này", "nâng chiều dài lên sau khi cắt để dễ đọc") ----------
# Dấu sắc / huyền là một nét xiên: hai cạnh dài (cung) + hai nhát cắt (đoạn thẳng xiên). Luật: nhát cắt nằm NGANG như chân dấu mũ;
# đầu dưới cắt ở điểm cao hơn của nhát cũ (không lấn xuống chữ), đầu trên cắt ở điểm cao hơn rồi kéo dài thêm MARK_EXT × chiều cao dấu
# (cạnh dài kéo theo tiếp tuyến cuối, một đoạn thẳng).
MARK_EXT = 0.18
ACUTE_GRAVE = {'̀', '́'}
def _ag_contour(c):
    ks = [k for k, _ in c if k in 'LC']
    if len(ks) != 4 or ks.count('L') != 2 or ks.count('C') != 2: return False
    return ks in (['C', 'L', 'C', 'L'], ['L', 'C', 'L', 'C'])
def _ycut_curve(p0, c1, c2, p3, y, from_end):
    """cắt cung (p0..p3) tại mép ngang y: trả về (cmd, pts) phần giữ lại (from_end: giữ phần cuối) + điểm cắt"""
    f = lambda t: (1-t)**3*p0[1] + 3*(1-t)**2*t*c1[1] + 3*(1-t)*t*t*c2[1] + t**3*p3[1]
    lo, hi = 0.0, 1.0; up = f(1.0) > f(0.0)
    for _ in range(50):
        m = (lo + hi)/2
        if (f(m) < y) == up: lo = m
        else: hi = m
    t = (lo + hi)/2
    P = [p0, c1, c2, p3]
    a = [[P[i][j] + (P[i+1][j] - P[i][j])*t for j in (0, 1)] for i in range(3)]
    b = [[a[i][j] + (a[i+1][j] - a[i][j])*t for j in (0, 1)] for i in range(2)]
    m_ = [b[0][j] + (b[1][j] - b[0][j])*t for j in (0, 1)]
    return ([list(P[0]), a[0], b[0], m_], [m_, b[1], a[2], list(P[3])])
def mark_cut(c, ext=MARK_EXT):
    """contour dấu sắc / huyền → cắt ngang hai đầu + kéo dài đầu trên. c: contour (parse)."""
    sg = []
    cur = None
    for k, ps in c:
        if k == 'M': cur = ps[0]
        elif k in 'LC': sg.append([k, list(cur)] + [list(p) for p in ps]); cur = ps[-1]
    while sg[0][0] != 'C': sg = sg[1:] + sg[:1]                    # C L C L
    e1, cut1, e2, cut2 = sg
    ys = [p[1] for s in sg for p in s[1:]]; H = max(ys) - min(ys)
    # nhát cắt nào ở trên
    top_is_1 = (cut1[1][1] + cut1[2][1]) > (cut2[1][1] + cut2[2][1])
    def recut(ea, cut, eb, y):
        """ea kết thúc ở cut[1], eb bắt đầu ở cut[2]: đưa hai đầu về đúng y (cắt cung nếu vượt, kéo dài thẳng theo tiếp tuyến nếu thiếu)"""
        out_a, out_b = ea, eb
        pa, pb = ea[-1], eb[1]
        def ext_pt(p, d):
            if abs(d[1]) < 1e-6: return list(p)
            s = (y - p[1])/d[1]; return [p[0] + d[0]*s, p[1] + d[1]*s]
        add_a = add_b = None
        if (pa[1] > y) == (ea[1][1] < pa[1]) and abs(pa[1] - y) > 0.01 and ((pa[1] - y)*(pa[1] - ea[1][1]) > 0):   # cung ea vượt qua y → cắt
            L, R = _ycut_curve(ea[1], ea[2], ea[3], ea[4], y, False); out_a = ['C', L[0], L[1], L[2], L[3]]
        else:
            add_a = ext_pt(pa, (pa[0] - ea[3][0], pa[1] - ea[3][1]))
        if abs(pb[1] - y) > 0.01 and ((pb[1] - y)*(pb[1] - eb[4][1]) > 0):
            L, R = _ycut_curve(eb[1], eb[2], eb[3], eb[4], y, True); out_b = ['C', R[0], R[1], R[2], R[3]]
        else:
            add_b = ext_pt(pb, (pb[0] - eb[2][0], pb[1] - eb[2][1]))
        return out_a, add_a, out_b, add_b
    yc1 = max(cut1[1][1], cut1[2][1]); yc2 = max(cut2[1][1], cut2[2][1])
    if top_is_1: yc1 += ext*H
    else: yc2 += ext*H
    a1, x1, b1, x2_ = recut(e1, cut1, e2, yc1)
    b1b, y1, a2, y2 = recut(b1, cut2, a1, yc2)
    # ghép: a2 (e1 đã chỉnh 2 đầu) → [x1 nối] → ngang → [x2_] → b1b (e2) → [y1] → ngang → [y2] → về đầu a2
    pts = []
    def segs_of(e): return [['C', [e[2], e[3], e[4]]]] if e[0] == 'C' else [['L', [e[-1]]]]
    seq = []
    start = a2[1]
    seq += segs_of(a2)
    if x1: seq.append(['L', [x1]])
    seq.append(['L', [x2_ if x2_ else b1b[1]]])
    if x2_: seq.append(['L', [b1b[1]]])
    seq += segs_of(b1b)
    if y1: seq.append(['L', [y1]])
    seq.append(['L', [y2 if y2 else a2[1]]])
    out_, last = [], start
    for k_, ps_ in seq:                                            # bỏ đoạn suy biến (đầu cung đã nằm đúng mép cắt)
        if k_ == 'L' and abs(ps_[0][0] - last[0]) < 0.05 and abs(ps_[0][1] - last[1]) < 0.05: continue
        out_.append([k_, ps_]); last = ps_[-1]
    if out_ and out_[-1][0] == 'L' and abs(out_[-1][1][0][0] - start[0]) < 0.05 and abs(out_[-1][1][0][1] - start[1]) < 0.05: out_.pop()
    return [['M', [start]]] + out_ + [['Z', []]]
def mark_fix(d, ch):
    import unicodedata as _u
    if not (set(_u.normalize('NFD', ch)) & ACUTE_GRAVE) and ch not in '´`ˊˋ̀́`´': return d
    cs = parse(d); out = []
    for c in cs:
        out.append(mark_cut(c) if _ag_contour(c) else c)
    return fmt(out)
