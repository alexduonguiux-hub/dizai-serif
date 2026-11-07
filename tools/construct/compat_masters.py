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

def _ln_isect(p, u, q, v):
    den = u[0]*v[1] - u[1]*v[0]
    if abs(den) < 1e-9: return None
    t = ((q[0] - p[0])*v[1] - (q[1] - p[1])*v[0])/den; return (p[0] + t*u[0], p[1] + t*u[1])

SYNC = set('gsšx')          # S20 chỉ áp cho chữ designer đã duyệt (07/11); N, 5, M sửa ở bản vẽ
def sync_struct(R, B):
    """S20 Đồng bộ cấu trúc theo đề xuất designer duyệt 07/11 (g, x, s):
    · GAI (g Bold): đoạn < 10 u có hai đầu quay > 120° (nét đi tới rồi quay ngược) → bỏ gai: nối hai đoạn kề ở trung điểm;
    · NÁCH (x): đoạn thẳng ngắn i+1 thẳng hàng với cạnh trước ở master này nhưng là MẶT NÁCH (hai góc) ở master kia → dựng mặt
      nách cùng hướng, cùng dài, đặt đúng trên hai cạnh (giao tuyến);
    · BẬC SAU GÓC (s Regular): đoạn ngắn sau một góc, nối trơn vào đoạn sau, mà master kia ở đó là cạnh thẳng hàng tới góc →
      đưa góc về cuối cạnh trước, đoạn ngắn thành phần nối dài cạnh, đoạn sau bắt đầu tại góc."""
    n = len(R); fixed = 0
    def K(X, i): return angle(tan_out(X[i]), tan_in(X[(i + 1) % n]))
    # gai
    for X, Y in ((R, B), (B, R)):
        for i in range(n):
            h, j = (i - 1) % n, (i + 1) % n
            if seglen(X[i]) < 10 and K(X, h) > 120 and K(X, i) > 120 and K(Y, h) < 30 and K(Y, i) < 30:
                a, b = X[i][1], X[i][-1]; m = ((a[0] + b[0])/2, (a[1] + b[1])/2)
                H_, J_ = list(X[h]), list(X[j]); dE = (m[0] - H_[-1][0], m[1] - H_[-1][1]); dS = (m[0] - J_[1][0], m[1] - J_[1][1])
                if H_[0] == 'C': H_[-2] = (H_[-2][0] + dE[0], H_[-2][1] + dE[1])
                if J_[0] == 'C': J_[2] = (J_[2][0] + dS[0], J_[2][1] + dS[1])
                H_[-1] = m; J_[1] = m
                # đoạn gai thành đoạn độ dài 0 nằm ở m (giữ số đoạn hai master bằng nhau); tay nắm hai bên thẳng hàng
                u = unit((J_[2][0] - H_[-2][0], J_[2][1] - H_[-2][1])) if H_[0] == J_[0] == 'C' else None
                if u:                                                      # tay nắm hai bên thẳng hàng → nút trơn
                    la, lb = math.dist(H_[-2], m), math.dist(J_[2], m)
                    H_[-2] = (m[0] - la*u[0], m[1] - la*u[1]); J_[2] = (m[0] + lb*u[0], m[1] + lb*u[1])
                # giữ số đoạn: đoạn trước chia đôi (de Casteljau) thay chỗ gai → master này có thêm một neo trơn trên đoạn trước
                if H_[0] == 'C':
                    a1, a2 = _split(H_, 0.5)
                    if h < i: X[h], X[i] = a1, a2
                    else: X[h], X[i] = a1, a2                             # (vòng: h = n−1, i = 0 — hiếm)
                else:
                    mm = ((H_[1][0] + m[0])/2, (H_[1][1] + m[1])/2); X[h], X[i] = ['L', H_[1], mm], ['L', mm, m]
                X[j] = J_
                fixed += 1
    # nách và bậc sau góc (ba đoạn thẳng / thẳng + cong)
    for X, Y in ((R, B), (B, R)):
        for i in range(n):
            h, j = (i - 1) % n, (i + 1) % n
            if X[i][0] != 'L' or Y[i][0] != 'L' or X[h][0] != 'L' or Y[h][0] != 'L': continue
            if seglen(Y[i]) <= 12 and K(X, h) < 3 and K(Y, h) > 30 and K(Y, i) > 30 and X[j][0] == 'L':      # nách: X thẳng hàng, Y có mặt nách
                fy = unit((Y[i][2][0] - Y[i][1][0], Y[i][2][1] - Y[i][1][1])); w = seglen(Y[i])
                u = unit((X[h][2][0] - X[h][1][0], X[h][2][1] - X[h][1][1])); v = unit((X[j][2][0] - X[j][1][0], X[j][2][1] - X[j][1][1]))
                V0 = X[i][2]                                               # đỉnh nách hiện tại
                # P trên cạnh trước, Q = P + w·fy trên cạnh sau
                Pp = _ln_isect((V0[0] - w*fy[0], V0[1] - w*fy[1]), v, X[h][1], u)
                if Pp is None: continue
                Q = (Pp[0] + w*fy[0], Pp[1] + w*fy[1])
                X[h] = ['L', X[h][1], Pp]; X[i] = ['L', Pp, Q]; X[j] = ['L', Q, X[j][2]]; fixed += 1
            elif seglen(X[i]) <= 12 and K(X, h) > 60 and K(X, i) < 30 and K(Y, h) < 3 and K(Y, i) > 30 and X[j][0] == 'C':   # bậc sau góc
                Vc = X[i][1]; u = unit((X[h][2][0] - X[h][1][0], X[h][2][1] - X[h][1][1])); w = seglen(X[i])
                Pp = (Vc[0] - w*u[0], Vc[1] - w*u[1])                      # điểm chia trên cạnh trước
                d_ = (Vc[0] - X[j][1][0], Vc[1] - X[j][1][1])
                X[h] = ['L', X[h][1], Pp]; X[i] = ['L', Pp, Vc]
                X[j] = ['C', Vc, (X[j][2][0] + d_[0], X[j][2][1] + d_[1])] + X[j][3:]; fixed += 1
    return R, B, fixed

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
    """hai contour trùng hình sau tịnh tiến (sai < 1.5 u) — so HAI CHIỀU (Hausdorff): so một chiều thì lòng Đ (lòng D + khuyết
    thanh ngang) bị coi là trùng lòng D và bị thay → mất phần thanh trong lòng (designer 06/11 "chữ Đ bị mất nét trong")"""
    def dense(S_, ox=0.0, oy=0.0):
        return [((bez(sg, k/40) if sg[0] == 'C' else (sg[1][0] + (sg[2][0] - sg[1][0])*k/40, sg[1][1] + (sg[2][1] - sg[1][1])*k/40))[0] + ox,
                 (bez(sg, k/40) if sg[0] == 'C' else (sg[1][0] + (sg[2][0] - sg[1][0])*k/40, sg[1][1] + (sg[2][1] - sg[1][1])*k/40))[1] + oy)
                for sg in S_ for k in range(41)]
    PA, PB = dense(A), dense(B, dx, dy)
    import numpy as np
    from scipy.spatial import cKDTree
    a, b = np.array(PA), np.array(PB)
    return max(cKDTree(a).query(b)[0].max(), cKDTree(b).query(a)[0].max()) < 3.0   # đơn giản hoá mỗi bên lệch ≤ 1.5 u

def _shift(segs, dx, dy): return [[sg[0]] + [(p[0] + dx, p[1] + dy) for p in sg[1:]] for sg in segs]

STUB = 5.0
JOG = 6.0
def dejog(S):
    """BẬC THỪA (< JOG u giữa hai góc ~vuông, hướng vào / ra lệch < 50° — mép bị "bậc" chứ không phải góc thật): sinh ra khi nét
    ghép vào bụng bằng phép hợp (& : mép tay gặp mép bụng lệch 3 u) hoặc ở góc đầu nét (s Regular bậc ngang 5 u). Bỏ đoạn bậc,
    nối hai mép tại trung điểm (dời ≤ ½ bậc). Designer 06/11 duyệt đề xuất & — hai master cùng cấu trúc, khớp rõ, không bậc"""
    changed = True
    while changed and len(S) > 3:
        changed = False; n = len(S)
        for i in range(n):
            h, j = (i - 1) % n, (i + 1) % n
            if seglen(S[i]) >= JOG: continue
            a1, a2 = angle(tan_out(S[h]), tan_in(S[i])), angle(tan_out(S[i]), tan_in(S[j]))
            if a1 < 45 or a2 < 45 or angle(tan_out(S[h]), tan_in(S[j])) >= 50: continue
            p0, p1 = S[i][1], S[i][-1]; m = ((p0[0] + p1[0])/2, (p0[1] + p1[1])/2)
            d0 = (m[0] - p0[0], m[1] - p0[1]); d1 = (m[0] - p1[0], m[1] - p1[1])
            H_ = list(S[h]); H_[-1] = m
            if H_[0] == 'C': H_[-2] = (H_[-2][0] + d0[0], H_[-2][1] + d0[1])
            J_ = list(S[j]); J_[1] = m
            if J_[0] == 'C': J_[2] = (J_[2][0] + d1[0], J_[2][1] + d1[1])
            S[h], S[j] = H_, J_; del S[i]
            changed = True; break
    return S

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

# S25 (designer 07/11 "sửa luôn các cờ còn lại"): nút gãy NHỎ (< KINK°) giữa đoạn cong / cong–thẳng là lỗi (mọi góc cố ý của
# font sắc > 25°: mỏ, đầu nét, nách) — chân loe A (S21 dời mép), nút nối g Bold, & Bold, loe V Regular. Quyết định CHUNG cho
# cặp (R, B): gãy < KINK ở cả hai master → xoay tay nắm hai bên về một tiếp tuyến (cạnh thẳng giữ hướng; hai cong → phân giác),
# giữ độ dài tay nắm, không dời điểm neo. Hai đoạn thẳng thẳng hàng (< 0.5°) ở cả hai master → gộp. Contour diện tích ~0 → bỏ.
KINK = 12.0
MAXDEV = 3.5      # u: nút phải dời đường cong hơn mức này thì giữ bản vẽ (s S của designer — vector Figma đã duyệt)
LEFT = []
def _segdev(a, b):
    """độ dời HÌNH HỌC (Hausdorff) giữa hai đoạn — kéo tay nắm dọc đoạn thẳng không đổi hình"""
    A = [bez(a, t/24) for t in range(25)]; Bp = [bez(b, t/48) for t in range(49)]
    Ap = [bez(a, t/48) for t in range(49)]; Bq = [bez(b, t/24) for t in range(25)]
    return max(max(min(math.dist(p, q) for q in Bp) for p in A), max(min(math.dist(p, q) for q in Ap) for p in Bq))
KINK_CH = {'@': 0.0}    # @: lòng elip của a bên trong bị mép thân CẮT DỌC — góc cắt cố ý (designer 07/11 "bụng @ nên cắt ngang như này"), không làm liền
def _straight(sg):
    if sg[0] != 'C': return False
    a, d = sg[1], sg[4]; L = math.dist(a, d)
    if L < 20: return False
    u = unit((d[0] - a[0], d[1] - a[1]))
    for h, base in ((sg[2], a), (sg[3], d)):                     # tay nắm lệch dây cung < 3° (hoặc suy biến)
        v = unit((h[0] - base[0], h[1] - base[1]))
        if v and min(angle(v, u), angle(v, (-u[0], -u[1]))) > 3: return False
    return True
def _rot_handles(S, i, j, both_t, free=False):
    p = end(S[i]); u, v = tan_out(S[i]), tan_in(S[j])
    fi = S[i][0] == 'L' or (_straight(S[i]) and not free); fj = S[j][0] == 'L' or (_straight(S[j]) and not free)      # cạnh cố định (thẳng)
    if fi and fj:                                              # cả hai gần thẳng: giữ cạnh thật / cạnh dài, uốn đoạn cong ngắn
        if S[i][0] == 'L' and S[j][0] == 'L': return
        if S[j][0] == 'L' or (S[i][0] == 'C' and seglen(S[i]) < seglen(S[j])): fi = False
        else: fj = False
    if not fi and not fj:                                      # hai cong: hướng trung bình theo độ dài tay nắm (tay ngắn xoay theo tay dài)
        a_, b_ = math.dist(S[i][3], p), math.dist(S[j][2], p)
        t = unit((u[0]*a_ + v[0]*b_, u[1]*a_ + v[1]*b_)) or unit((u[0] + v[0], u[1] + v[1]))
    else: t = u if fi else v
    if t is None: return
    if S[i][0] == 'C' and not fi:
        a = list(S[i]); L = math.dist(a[3], p) or math.dist(a[1], p)/3; a[3] = (p[0] - t[0]*L, p[1] - t[1]*L); S[i] = a
    if S[j][0] == 'C' and not fj:
        b = list(S[j]); L = math.dist(b[2], p) or math.dist(b[4], p)/3; b[2] = (p[0] + t[0]*L, p[1] + t[1]*L); S[j] = b
def _hl(S, i, j):
    """(độ dài tay vào, độ dài tay ra) tại nút cuối S[i]; cạnh thẳng: độ dài cạnh"""
    p = end(S[i])
    a = math.dist(S[i][3], p) if S[i][0] == 'C' else math.dist(S[i][1], p)
    b = math.dist(S[j][2], p) if S[j][0] == 'C' else math.dist(S[j][2], p)
    return a, b
def _set_hl(S, i, j, a, b):
    p = end(S[i])
    if S[i][0] == 'C':
        h = S[i][3]; L = math.dist(h, p)
        if L > 1e-6: x = list(S[i]); x[3] = (p[0] + (h[0] - p[0])*a/L, p[1] + (h[1] - p[1])*a/L); S[i] = x
    if S[j][0] == 'C':
        h = S[j][2]; L = math.dist(h, p)
        if L > 1e-6: x = list(S[j]); x[2] = (p[0] + (h[0] - p[0])*b/L, p[1] + (h[1] - p[1])*b/L); S[j] = x
def _sync_ratio(R, B, i, j):
    """nút liền ở cả hai master: nội suy liền khi tỉ lệ (tay vào : tay ra) bằng nhau ở hai master. Chọn cách dời ít nhất trong:
    chỉnh MỘT tay nắm (vào / ra của R hoặc B) cho đúng tỉ lệ của master kia, hoặc đưa cả hai về trung bình nhân"""
    aR, bR = _hl(R, i, j); aB, bB = _hl(B, i, j)
    if min(aR, bR, aB, bB) < 1e-3: return
    rR, rB = aR/bR, aB/bB
    if abs(math.log(rR/rB)) < 0.02: return
    k0 = [list(R[i]), list(R[j]), list(B[i]), list(B[j])]; cands = []
    def tryit(f):
        R[i], R[j], B[i], B[j] = [list(x) for x in k0]; f()
        a2, b2 = _hl(R, i, j); a3, b3 = _hl(B, i, j)
        if abs(math.log((a2/b2)/(a3/b3))) > 0.03: return
        dv = max(_segdev(k0[0], R[i]), _segdev(k0[1], R[j]), _segdev(k0[2], B[i]), _segdev(k0[3], B[j]))
        cands.append((dv, [list(R[i]), list(R[j]), list(B[i]), list(B[j])]))
    if B[i][0] == 'C': tryit(lambda: _set_hl(B, i, j, rR*bB, bB))
    if B[j][0] == 'C': tryit(lambda: _set_hl(B, i, j, aB, aB/rR))
    if R[i][0] == 'C': tryit(lambda: _set_hl(R, i, j, rB*bR, bR))
    if R[j][0] == 'C': tryit(lambda: _set_hl(R, i, j, aR, aR/rB))
    r = math.sqrt(rR*rB)
    def gm():
        for S, a, b in ((R, aR, bR), (B, aB, bB)):
            if S[i][0] == 'C' and S[j][0] == 'C': ab = a*b; _set_hl(S, i, j, math.sqrt(ab*r), math.sqrt(ab/r))
            elif S[i][0] == 'C': _set_hl(S, i, j, r*b, b)
            elif S[j][0] == 'C': _set_hl(S, i, j, a, a/r)
    tryit(gm)
    if cands: R[i], R[j], B[i], B[j] = min(cands, key=lambda c: c[0])[1]
    else: R[i], R[j], B[i], B[j] = k0
def smooth_pair(R, B, kink=KINK):
    R, B = [list(x) for x in R], [list(x) for x in B]; nk = 0
    i = 0
    while i < len(R) and len(R) > 2:
        n = len(R); j = (i + 1) % n
        tR, tB = angle(tan_out(R[i]), tan_in(R[j])), angle(tan_out(B[i]), tan_in(B[j]))
        if R[i][0] == R[j][0] == 'L' == B[i][0] == B[j][0] and tR < 0.5 and tB < 0.5 and j != 0:
            R[i] = ['L', R[i][1], R[j][2]]; B[i] = ['L', B[i][1], B[j][2]]; del R[j]; del B[j]; nk += 1; continue
        if not (R[i][0] == R[j][0] == 'L') and max(tR, tB) < kink:
            keep = [list(R[i]), list(R[j]), list(B[i]), list(B[j])]
            best = None
            for free in (False, True):                                 # phương án 2: uốn nhẹ đầu đoạn cong "thẳng" thay vì xoay đoạn kia
                R[i], R[j], B[i], B[j] = [list(x) for x in keep]
                if max(tR, tB) > 0.3: _rot_handles(R, i, j, None, free); _rot_handles(B, i, j, None, free)
                if _mid_kink(R, B, i, j) > 1.0: _sync_ratio(R, B, i, j)      # chỉ khi bản nội suy gãy
                dv = max(_segdev(keep[0], R[i]), _segdev(keep[1], R[j]), _segdev(keep[2], B[i]), _segdev(keep[3], B[j]))
                if best is None or dv < best[0] - 0.05: best = (dv, [list(R[i]), list(R[j]), list(B[i]), list(B[j])])
            dev = best[0]; R[i], R[j], B[i], B[j] = best[1]
            if dev > MAXDEV:                                           # dời đường cong > MAXDEV u: giữ bản vẽ, báo lại
                R[i], R[j], B[i], B[j] = keep; LEFT.append((round(max(tR, tB), 1), round(dev, 1)))
            elif keep != [R[i], R[j], B[i], B[j]]: nk += 1
        i += 1
    return R, B, nk

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
            cs = [dejog(drop_stub(simplify_pair([list(x) for x in g], [list(x) for x in g])[0])) for g in contours([O[k_]])]
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
            for (R0, B0, r0, b0, R1, B1) in (REG if ord(c[0]) >= 0x80 else []):        # chỉ chữ có dấu / ngoài ASCII
                if abs((br[2] - br[0]) - (r0[2] - r0[0])) < 1.5 and abs((br[3] - br[1]) - (r0[3] - r0[1])) < 1.5 and \
                   abs((bb_[2] - bb_[0]) - (b0[2] - b0[0])) < 1.5 and abs((bb_[3] - bb_[1]) - (b0[3] - b0[1])) < 1.5:
                    dR = (br[0] - r0[0], br[1] - r0[1]); dB = (bb_[0] - b0[0], bb_[1] - b0[1])
                    if _same(Rr, R0, *dR) and _same(Bb, B0, *dB):           # so với cặp GỐC của chữ gốc (trước khi dời neo)
                        hit = (_shift(R1, *dR), _shift(B1, *dB))                # dùng lại cặp ĐÃ dời neo
                        if (_sarea(hit[0]) > 0) != (_sarea(Rr) > 0): hit = (reverse(hit[0]), reverse(hit[1]))   # giữ chiều contour của chữ
                        break
            if hit and (len(hit[0]) != len(Rr) or hit[0] != Rr):
                Rr, Bb = hit; stat.setdefault('S18b', []).append(c)
            else:
                R_pre, B_pre = [list(x) for x in Rr], [list(x) for x in Bb]
                k_ = 0
                if c in SYNC: Rr, Bb, k_ = sync_struct(Rr, Bb)
                if k_: stat.setdefault('S20', []).append(f'{c}×{k_}')
                k_ = 0
                for _ in range(4):                             # dời một nút có thể làm nút kề gãy thêm → lặp tới khi ổn định
                    Rr, Bb, kk = reanchor(Rr, Bb); k_ += kk
                    if not kk: break
                if k_: stat.setdefault('S18', []).append(f'{c}×{k_}')
                if c.isalpha() and len(c) == 1 and ord(c) < 0x80: REG.append((R_pre, B_pre, br, bb_, Rr, Bb))
            n0 = len(LEFT); Rr, Bb, k_ = smooth_pair(Rr, Bb, KINK_CH.get(c, KINK))
            if len(LEFT) > n0: stat.setdefault('S25 giữ', []).append(f'{c}{LEFT[n0:]}')
            if k_: stat.setdefault('S25', []).append(f'{c}×{k_}')
            if abs(_sarea(Rr)) < 5 and abs(_sarea(Bb)) < 5: stat.setdefault('S25 bỏ contour rỗng', []).append(c); continue
            out.append((Rr, Bb))
        after = sum(len(a) for a, _ in out)
        stat['đoạn trước'] += before; stat['đoạn sau'] += after; stat['ghép được'] += 1
        for w in WEIGHTS:
            O[f'{c}-{w}'] = to_d([lerp_segs(a, b, TW[w]) for a, b in out])
    json.dump(O, open(os.path.join(OUT, 'outlines.json'), 'w'))
    print('compat:', {k: (v if not isinstance(v, list) else len(v)) for k, v in stat.items()}, 'không ghép:', stat['không ghép'][:30])
    print('S18 nội suy liền tiếp tuyến:', ' '.join(stat.get('S18', [])))
    print('S20 đồng bộ cấu trúc:', ' '.join(stat.get('S20', [])))
    print('S25 nút gãy nhỏ → liền:', ' '.join(stat.get('S25', [])), '· giữ (dời > %.1f u):' % MAXDEV, ' '.join(stat.get('S25 giữ', [])), '· bỏ contour rỗng:', ''.join(stat.get('S25 bỏ contour rỗng', [])))
    print('S18b ghép theo chữ gốc:', ''.join(sorted(set(stat.get('S18b', [])))))

if __name__ == '__main__':
    main()
