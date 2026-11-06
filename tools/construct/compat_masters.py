#!/usr/bin/env python3
"""Đơn giản hoá outline + đưa Regular / Bold về CÙNG CẤU TRÚC (designer 05/11: "Simplify lại để dễ làm variables").
    python3 tools/construct/compat_masters.py   (sau build.py) → ghi lại out/construct/outlines.json

1. Ghép cặp R ↔ B từng glyph (font/compat.py: ghép contour theo tâm + hộp, căn điểm neo bằng quy hoạch động, tách đoạn dài nhất
   khi một bên thừa neo) → hai master cùng số contour, cùng chuỗi đoạn, cùng loại đoạn.
2. Đơn giản hoá ĐỒNG THỜI hai master: chỉ bỏ một điểm neo khi bỏ được ở CẢ HAI —
   · hai đoạn thẳng thẳng hàng (lệch < 0.35 u),
   · đoạn siêu ngắn (< 1.2 u ở cả hai),
   · hai đoạn cong nối trơn (lệch tiếp tuyến < 6°) mà một cubic (giữ hai đầu + hướng tiếp tuyến hai đầu) khớp, sai số < 0.8 u.
   Góc có chủ ý (gãy ≥ 6° ở một trong hai master) giữ nguyên.
3. S18 neo tương ứng (reanchor): nút cực trị ở master này ↔ nút xiên ở master kia → dời nút về cực trị trên chính đường cong.
   S17 (font/fair.py, đang tắt): S s Š š $ § làm độ cong liền G2 ở mọi nút trơn, giữ điểm neo, cấu trúc.
4. Medium / SemiBold = nội suy đúng hai master (TW 1/3, 2/3) → bản tĩnh trùng khít bản variable.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'font'))
sys.path.insert(0, os.path.join(HERE, 'ref'))
from compat import compat, lerp_segs, to_d, _sarea
from interp import reverse
from interp import contours, tocubic
from weights import WEIGHTS, TW
from fair import fair
# S17 độ cong liền G2 (font/fair.py) — designer 06/11 "Các đường cong của chữ s và S. Cảm giác không smooth lắm"
FAIR = set()   # S17 TẮT (designer 06/11 "bụng không cong tròn tự nhiên" → designer tự vẽ lại S Regular + Bold, ref/figma_S.py); bật lại: set('SsŠš$§')
OUT = os.environ.get('DIZAI_OUT') or os.path.join(HERE, '..', '..', 'out', 'construct')   # DIZAI_OUT: nhánh Italic (out/construct_italic)

def bez(s, t):
    if s[0] == 'L': a, b = s[1], s[2]; return (a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t)
    a, b, c, d = s[1:]; u = 1 - t
    return (u**3*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t**3*d[0], u**3*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t**3*d[1])
def start(s): return s[1]
def end(s): return s[2] if s[0] == 'L' else s[4]
def seglen(s, n=12):
    P = [bez(s, k/n) for k in range(n + 1)]; return sum(math.dist(a, b) for a, b in zip(P, P[1:]))
def unit(v):
    L = math.hypot(*v); return (v[0]/L, v[1]/L) if L > 1e-9 else None
def tan_out(s):              # hướng tiếp tuyến ở cuối đoạn
    if s[0] == 'L': return unit((s[2][0] - s[1][0], s[2][1] - s[1][1]))
    for q in (s[3], s[2], s[1]):
        v = unit((s[4][0] - q[0], s[4][1] - q[1]))
        if v: return v
def tan_in(s):
    if s[0] == 'L': return unit((s[2][0] - s[1][0], s[2][1] - s[1][1]))
    for q in (s[2], s[3], s[4]):
        v = unit((q[0] - s[1][0], q[1] - s[1][1]))
        if v: return v
def angle(a, b):
    if a is None or b is None: return 180.0
    return math.degrees(math.acos(max(-1.0, min(1.0, a[0]*b[0] + a[1]*b[1]))))

def fit(s1, s2):
    """một cubic thay cho s1 + s2: giữ hai đầu, hướng tiếp tuyến đầu (của s1) và cuối (của s2); độ dài tay nắm bình phương tối thiểu"""
    p0, p3 = start(s1), end(s2); t0, t1 = tan_in(s1), tan_out(s2)
    if t0 is None or t1 is None: return None, 1e9
    pts = [bez(s1, k/16) for k in range(17)] + [bez(s2, k/16) for k in range(1, 17)]
    d = [0.0]
    for a, b in zip(pts, pts[1:]): d.append(d[-1] + math.dist(a, b))
    if d[-1] < 1e-9: return None, 1e9
    us = [x/d[-1] for x in d]
    # P(u) = B0 p0 + B1 (p0 + a t0) + B2 (p3 − b t1) + B3 p3 → tuyến tính theo a, b
    A11 = A12 = A22 = X1 = X2 = 0.0
    for u, q in zip(us, pts):
        v = 1 - u; B0, B1, B2, B3 = v**3, 3*v*v*u, 3*v*u*u, u**3
        c1 = (B1*t0[0], B1*t0[1]); c2 = (-B2*t1[0], -B2*t1[1])
        r = (q[0] - (B0 + B1)*p0[0] - (B2 + B3)*p3[0], q[1] - (B0 + B1)*p0[1] - (B2 + B3)*p3[1])
        A11 += c1[0]*c1[0] + c1[1]*c1[1]; A12 += c1[0]*c2[0] + c1[1]*c2[1]; A22 += c2[0]*c2[0] + c2[1]*c2[1]
        X1 += c1[0]*r[0] + c1[1]*r[1]; X2 += c2[0]*r[0] + c2[1]*r[1]
    det = A11*A22 - A12*A12
    if abs(det) < 1e-12: return None, 1e9
    a = (X1*A22 - X2*A12)/det; b = (A11*X2 - A12*X1)/det
    chord = math.dist(p0, p3)
    if a <= 0 or b <= 0 or a > 1.5*chord or b > 1.5*chord: return None, 1e9
    c = ['C', p0, (p0[0] + a*t0[0], p0[1] + a*t0[1]), (p3[0] - b*t1[0], p3[1] - b*t1[1]), p3]
    # sai số: khoảng cách lớn nhất từ điểm mẫu của đường cũ tới đường mới (lấy mẫu dày đường mới)
    Q = [bez(c, k/120) for k in range(121)]
    err = max(min(math.dist(p, q) for q in Q) for p in pts)
    return c, err

KINK, TOL = 10.0, 1.5     # góc thật: gãy ≥ 10°; sai số cho phép 1.5 u (< 0.2 % cao chữ)
def simplify_pair(R, B, tol=TOL):
    """R, B: chuỗi đoạn vòng cùng độ dài, cùng loại. Bỏ điểm neo chung khi bỏ được ở cả hai"""
    changed = True
    while changed and len(R) > 2:
        changed = False
        n = len(R)
        for i in range(n):
            j = (i + 1) % n
            if j == 0 and n <= 2: break
            ok = True; newR = newB = None
            for S, out in ((R, 'R'), (B, 'B')):
                s1, s2 = S[i], S[j]
                tiny = seglen(s1) < 1.2 or seglen(s2) < 1.2
                kink = angle(tan_out(s1), tan_in(s2))
                if s1[0] == 'L' and s2[0] == 'L':
                    a, b, c = start(s1), end(s1), end(s2); L = math.dist(a, c)
                    dev = abs((b[0] - a[0])*(c[1] - a[1]) - (b[1] - a[1])*(c[0] - a[0]))/L if L > 1e-9 else 0
                    m = ['L', a, c] if (dev < 0.35 or tiny) else None
                elif (s1[0] == 'C' or s2[0] == 'C') and (kink < KINK or tiny):
                    m, err = fit(tocubic(s1), tocubic(s2)); m = m if err < tol else None
                else: m = None
                if m is None: ok = False; break
                if out == 'R': newR = m
                else: newB = m
            if not ok: continue
            for S, m in ((R, newR), (B, newB)):
                if j == 0: S[0] = m; del S[i]
                else: S[i] = m; del S[j]
            changed = True; break
    return R, B

ITP = float(os.environ.get("DIZAI_ITP", "2.0"))      # độ: gãy cho phép ở bản nội suy (S 1.3° giữ nguyên vector designer)
AXT = math.sin(math.radians(2.0))                    # tiếp tuyến lệch trục < 2° → nút ở cực trị
RTOL = 3.6                                           # u: sai số khớp lại khi dời nút (≈ 0.5 % cao chữ; s Regular cần 3.58)

def _split(s, t):
    a, b, c, d = s[1:]
    l = lambda p, q: (p[0] + (q[0] - p[0])*t, p[1] + (q[1] - p[1])*t)
    ab, bc, cd = l(a, b), l(b, c), l(c, d); abc, bcd = l(ab, bc), l(bc, cd); m = l(abc, bcd)
    return ['C', a, ab, abc, m], ['C', m, bcd, cd, d]

def _roots(s, ax):
    """t ∈ (0, 1) nơi đạo hàm theo trục ax (0 = x, 1 = y) bằng 0"""
    p = [q[ax] for q in s[1:]]
    a = -p[0] + 3*p[1] - 3*p[2] + p[3]; b = 2*(p[0] - 2*p[1] + p[2]); c = p[1] - p[0]
    if abs(a) < 1e-9: r = [-c/b] if abs(b) > 1e-9 else []
    else:
        D = b*b - 4*a*c
        r = [] if D < 0 else [(-b + sg*math.sqrt(D))/(2*a) for sg in (1, -1)]
    return [t for t in r if 0.02 < t < 0.98]

def _ext_axis(X, i):
    v = tan_out(X[i])
    if v is None: return None
    return 0 if abs(v[0]) < AXT else 1 if abs(v[1]) < AXT else None   # tiếp tuyến dọc → cực x; ngang → cực y

def _mid_kink(R, B, i, j):
    M = lerp_segs([R[i], R[j]], [B[i], B[j]], 0.5); return angle(tan_out(M[0]), tan_in(M[1]))

def _ratio(R, B, i, j):
    """nút xiên ở cả hai master: đặt tỉ lệ tay nắm vào / ra của hai master bằng nhau (trung bình nhân), giữ tổng độ dài và hướng
    → lerp hai cặp vectơ cùng tỉ lệ luôn thẳng hàng. Chỉ nhận khi đường cong mỗi master lệch < RTOL."""
    L = []
    for X in (R, B):
        p = X[i][4]; la, lb = math.dist(X[i][3], p), math.dist(X[j][2], p)
        if la < 1 or lb < 1: return False
        L.append((la, lb))
    r = math.sqrt((L[0][0]/L[0][1])*(L[1][0]/L[1][1])); new = []
    for X, (la, lb) in zip((R, B), L):
        p = X[i][4]; tot = la + lb; lb2 = tot/(1 + r); la2 = tot - lb2
        u = tan_out(X[i]); v = tan_in(X[j]); d = unit((u[0] + v[0], u[1] + v[1]))
        ni = X[i][:3] + [(p[0] - la2*d[0], p[1] - la2*d[1]), p]; nj = [X[j][0], p, (p[0] + lb2*d[0], p[1] + lb2*d[1])] + X[j][3:]
        Q = [bez(ni, k/60) for k in range(61)] + [bez(nj, k/60) for k in range(61)]
        err = max(min(math.dist(bez(sg, k/20), q) for q in Q) for sg in (X[i], X[j]) for k in range(21))
        if err > RTOL: return False
        new.append((ni, nj))
    (R[i], R[j]), (B[i], B[j]) = new
    return True

def _ext_at(X, i, j, ax):
    return any(_roots(X[k], ax) for k in (i, j))

def _to_ext(X, i, j, ax):
    """dời nút giữa đoạn i và j của master X về cực trị trục ax gần nhất trên chính đường cong (sai số khớp ≤ RTOL)"""
    best = None
    for k, seg in ((i, X[i]), (j, X[j])):
        for t in _roots(seg, ax):
            L = seglen(_split(seg, t)[1]) if k == i else seglen(_split(seg, t)[0])
            if best is None or L < best[0]: best = (L, k, t)
    if best is None: return False
    _, k, t = best
    if k == j:
        a_, b_ = _split(X[j], t); ni, err = fit(X[i], a_); nj = b_
    else:
        a_, b_ = _split(X[i], t); nj, err = fit(b_, X[j]); ni = a_
    if ni is None or err > RTOL: return False
    X[i], X[j] = ni, nj
    return True

def reanchor(R, B):
    """S18 Neo tương ứng cho nội suy (designer 06/11 "bụng s medium và semi bold lỗi"). Hai master ghép cặp điểm neo theo thứ tự;
    khi một master neo ở CỰC TRỊ (tiếp tuyến ngang / dọc) mà master kia neo ở chỗ xiên (s: Regular neo cực phải bụng dưới,
    Bold — S Bold mới của designer — neo xiên), bản nội suy nội suy giữa hai hướng tiếp tuyến khác nhau → gãy (s SemiBold 13°).
    Sửa: dời nút của master kia về cực trị cùng trục trên CHÍNH đường cong của nó (cắt de Casteljau phần chứa cực trị, khớp lại
    phần còn lại bằng fit(), sai số < TOL) → hình hai master không đổi, chỉ đổi vị trí điểm; mọi bản nội suy liền tiếp tuyến."""
    n = len(R); fixed = []
    for i in range(n):
        j = (i + 1) % n
        if R[i][0] == B[i][0] == R[j][0] == B[j][0] == 'L':
            # hai đoạn thẳng: một master thẳng hàng (điểm giữa chỉ là điểm chia), master kia có góc (vd. góc đầu nét dưới s Regular
            # có bậc ngang 5 u) → đặt điểm chia theo đúng tỉ lệ độ dài của master có góc, tránh mép thẳng bị bẻ ở Medium / SemiBold
            def col(X): a, b, c = X[i][1], X[i][2], X[j][2]; return angle(unit((b[0]-a[0], b[1]-a[1])), unit((c[0]-b[0], c[1]-b[1])))
            cr, cb = col(R), col(B)
            if cr < 0.5 and cb < 0.5:
                # cả hai thẳng hàng (nét thẳng chia hai đoạn) nhưng tỉ lệ chia khác nhau → điểm chia nội suy lệch khỏi đường thẳng,
                # nét chéo A V W K v w y gãy 2–4° ở Medium / SemiBold. Đặt cùng tỉ lệ (trung bình) — điểm trượt trên chính đường
                fr = [math.dist(X[i][1], X[i][2])/max(1e-9, math.dist(X[i][1], X[j][2])) for X in (R, B)]
                if abs(fr[0] - fr[1]) > 0.01:
                    f = sum(fr)/2
                    for X in (R, B):
                        a, c = X[i][1], X[j][2]; m = (a[0] + (c[0] - a[0])*f, a[1] + (c[1] - a[1])*f)
                        X[i] = ['L', a, m]; X[j] = ['L', m, c]
                    fixed.append(i)
                continue
            if min(cr, cb) < 0.5 and max(cr, cb) > 30:
                X, Y = (R, B) if cr < 0.5 else (B, R)
                l1, l2 = math.dist(Y[i][1], Y[i][2]), math.dist(Y[j][1], Y[j][2]); f = l1/(l1 + l2)
                a, c = X[i][1], X[j][2]; m = (a[0] + (c[0] - a[0])*f, a[1] + (c[1] - a[1])*f)
                X[i] = ['L', a, m]; X[j] = ['L', m, c]; fixed.append(i)
            continue
        if not (R[i][0] == B[i][0] == R[j][0] == B[j][0] == 'C'): continue
        if angle(tan_out(R[i]), tan_in(R[j])) >= 6 or angle(tan_out(B[i]), tan_in(B[j])) >= 6: continue
        if _mid_kink(R, B, i, j) <= ITP: continue
        ar, ab = _ext_axis(R, i), _ext_axis(B, i)
        if ar is not None and ab is not None: continue
        if ar is None and ab is None:
            # cả hai xiên: nếu cung (đoạn i ∪ j) của CẢ HAI master cùng chứa một cực trị (cùng trục) → dời cả hai nút về cực trị đó;
            # không thì cân tỉ lệ tay nắm (nếu master lệch < RTOL)
            done = False
            for ax in (0, 1):
                if _ext_at(R, i, j, ax) and _ext_at(B, i, j, ax):
                    keep = [list(R[i]), list(R[j]), list(B[i]), list(B[j])]
                    if _to_ext(R, i, j, ax) and _to_ext(B, i, j, ax) and _mid_kink(R, B, i, j) <= ITP + 0.5:
                        done = True; break
                    R[i], R[j], B[i], B[j] = keep
            if done or _ratio(R, B, i, j): fixed.append(i)
            continue
        X, ax = (B, ar) if ar is not None else (R, ab)
        oi, oj = X[i], X[j]
        if not _to_ext(X, i, j, ax): continue
        if _mid_kink(R, B, i, j) > ITP + 0.5: X[i], X[j] = oi, oj; continue
        fixed.append(i)
    return R, B, len(fixed)

def _bbox(segs):
    P = [bez(sg, k/8) if sg[0] == 'C' else sg[1] for sg in segs for k in range(9)]
    xs = [p[0] for p in P]; ys = [p[1] for p in P]; return min(xs), min(ys), max(xs), max(ys), P

def _same(A, B, dx, dy):
    """hai contour trùng hình sau tịnh tiến (sai < 1.5 u)"""
    PA = _bbox(A)[4]; PB = [(p[0] + dx, p[1] + dy) for p in _bbox(B)[4]]
    Q = [bez(sg, k/40) if sg[0] == 'C' else (sg[1][0] + (sg[2][0] - sg[1][0])*k/40, sg[1][1] + (sg[2][1] - sg[1][1])*k/40)
         for sg in A for k in range(41)]
    return max(min(math.dist(p, q) for q in Q) for p in PB) < 1.5

def _shift(segs, dx, dy): return [[sg[0]] + [(p[0] + dx, p[1] + dy) for p in sg[1:]] for sg in segs]

STUB = 5.0
def drop_stub(S):
    """đoạn cong tí hon (< STUB u) ngay sau một GÓC, nối trơn với đoạn sau → gộp vào đoạn sau (fit, sai số < TOL). Vd ß Regular có
    đoạn 4 u ở mũi đuôi mà Bold không có → ghép cặp lệch một bậc, SemiBold gãy 37° (06/11)"""
    changed = True
    while changed and len(S) > 3:
        changed = False; n = len(S)
        for i in range(n):
            h, j = (i - 1) % n, (i + 1) % n
            if S[i][0] != 'C' or S[j][0] != 'C' or seglen(S[i]) >= STUB: continue
            if angle(tan_out(S[h]), tan_in(S[i])) < 15 or angle(tan_out(S[i]), tan_in(S[j])) >= 6: continue
            m, err = fit(S[i], S[j])
            if m is None or err > TOL:
                # đoạn tí hon gần thẳng, cùng hướng với tay nắm đầu của đoạn sau → kéo điểm đầu đoạn sau về đầu đoạn tí hon
                a, b = S[i][1], S[i][4]; q = S[j][2]
                u = unit((b[0] - a[0], b[1] - a[1])); v = unit((q[0] - b[0], q[1] - b[1]))
                if not u or not v or angle(u, v) > 3: continue
                m = ['C', a] + S[j][2:]
            S[i] = m; del S[j]
            changed = True; break
    return S

def main():
    O = json.load(open(os.path.join(OUT, 'outlines.json')))
    REG = []           # S18b: cặp contour (R, B) đã ghép của chữ gốc — chữ có dấu dùng lại đúng cặp đó (Š ← S, …)
    chars = sorted({k.rsplit('-', 1)[0] for k in O})
    stat = {'glyph': 0, 'ghép được': 0, 'không ghép': [], 'đoạn trước': 0, 'đoạn sau': 0}
    pre = dict(O)
    for c in chars:
        kr, kb = f'{c}-Regular', f'{c}-Bold'
        if kr not in O or kb not in O: continue
        stat['glyph'] += 1
        # đơn giản hoá TỪNG master trước (bỏ điểm thừa của boolean / làm đậm), rồi mới ghép cặp
        for k_ in (kr, kb):
            cs = [drop_stub(simplify_pair([list(x) for x in g], [list(x) for x in g])[0]) for g in contours([O[k_]])]
            O[k_] = to_d(cs)
        try: C = compat(O[kr], O[kb])
        except Exception as e: stat['không ghép'].append(c); continue
        if not C: continue
        before = sum(len(g) for g in contours([pre[kr]]))
        out = []
        for Rr, Bb in C:
            Rr, Bb = simplify_pair([list(s) for s in Rr], [list(s) for s in Bb])
            if c in FAIR: Rr, Bb = fair(Rr), fair(Bb)          # cùng cấu trúc → Medium / SemiBold vẫn nội suy được
            # S18b: contour trùng hình (sau tịnh tiến) với contour của chữ gốc đã ghép → dùng lại cặp của chữ gốc; phép hợp
            # chữ + dấu (Š = S ∪ móc) chia lại điểm neo khác nhau ở hai master → nội suy gãy dù chữ gốc liền (Š SemiBold 8°)
            br, bb_ = _bbox(Rr), _bbox(Bb); hit = None
            for (R0, B0, r0, b0) in REG:
                if abs((br[2] - br[0]) - (r0[2] - r0[0])) < 1.5 and abs((br[3] - br[1]) - (r0[3] - r0[1])) < 1.5 and \
                   abs((bb_[2] - bb_[0]) - (b0[2] - b0[0])) < 1.5 and abs((bb_[3] - bb_[1]) - (b0[3] - b0[1])) < 1.5:
                    dR = (br[0] - r0[0], br[1] - r0[1]); dB = (bb_[0] - b0[0], bb_[1] - b0[1])
                    if _same(Rr, R0, *dR) and _same(Bb, B0, *dB):
                        hit = (_shift(R0, *dR), _shift(B0, *dB))
                        if (_sarea(hit[0]) > 0) != (_sarea(Rr) > 0): hit = (reverse(hit[0]), reverse(hit[1]))   # giữ chiều contour của chữ
                        break
            if hit and (len(hit[0]) != len(Rr) or hit[0] != Rr):
                Rr, Bb = hit; stat.setdefault('S18b', []).append(c)
            else:
                k_ = 0
                for _ in range(4):                             # dời một nút có thể làm nút kề gãy thêm → lặp tới khi ổn định
                    Rr, Bb, kk = reanchor(Rr, Bb); k_ += kk
                    if not kk: break
                if k_: stat.setdefault('S18', []).append(f'{c}×{k_}')
                if c.isalpha() and len(c) == 1 and ord(c) < 0x80: REG.append((Rr, Bb, br, bb_))
            out.append((Rr, Bb))
        after = sum(len(a) for a, _ in out)
        stat['đoạn trước'] += before; stat['đoạn sau'] += after; stat['ghép được'] += 1
        for w in WEIGHTS:
            O[f'{c}-{w}'] = to_d([lerp_segs(a, b, TW[w]) for a, b in out])
    json.dump(O, open(os.path.join(OUT, 'outlines.json'), 'w'))
    print('compat:', {k: (v if not isinstance(v, list) else len(v)) for k, v in stat.items()}, 'không ghép:', stat['không ghép'][:30])
    print('S18 nội suy liền tiếp tuyến:', ' '.join(stat.get('S18', [])))
    print('S18b ghép theo chữ gốc:', ''.join(sorted(set(stat.get('S18b', [])))))

if __name__ == '__main__':
    main()
