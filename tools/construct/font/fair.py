"""S17 Độ cong liền (G2) tại nút trơn — designer 06/11: "Các đường cong của chữ s và S. Cảm giác không smooth lắm".

Đo: ở cực trái bụng trên S Regular bán kính cong phía trên 129, phía dưới 467 — đường liền tiếp tuyến (G1) nhưng độ cong
nhảy ×3.6 → mắt thấy "cong gắt rồi bỗng thẳng". Luật:
  · GIỮ mọi điểm neo (cực trị, điểm uốn, đầu nét) và số điểm (master tương thích cho variable).
  · Nút trơn gãy nhẹ (< 6°, sót lại sau boolean / đơn giản hoá) → hai tay nắm về chung một hướng (trung bình).
  · Chỉ đổi ĐỘ DÀI tay nắm (giữ hướng) sao cho độ cong hai bên mỗi nút trơn bằng nhau, hình lệch ít nhất (bình phương tối thiểu).
Độ cong đầu / cuối một cubic: κ0 = ⅔·(P1−P0)×(P2−P1)/|P1−P0|³ ; κ1 = ⅔·(P3−P2)×(P1−P2)/|P3−P2|³.
"""
import math
import numpy as np
from scipy.optimize import least_squares

SMOOTH = 6.0          # nút có gãy < 6° coi là nút trơn
TOL = 3.0             # u: thang phần dư lệch hình (lấy mẫu theo tham số)
W2 = 20000.0          # trọng số G2 (Δκ 0.001 ↔ 20 phần dư): tỉ lệ bán kính hai bên nút ≤ 1.15
SLIDE, MAXSLIDE = 12.0, 8.0    # u: thang / giới hạn trượt nút dọc tiếp tuyến


def _cross(a, b): return a[0]*b[1] - a[1]*b[0]
def _sub(a, b): return (a[0] - b[0], a[1] - b[1])
def _unit(v):
    L = math.hypot(*v); return (v[0]/L, v[1]/L) if L > 1e-9 else None
def _bez(s, t):
    a, b, c, d = s[1:]; u = 1 - t
    return (u**3*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t**3*d[0], u**3*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t**3*d[1])
def k0(s):
    a = _sub(s[2], s[1]); L = math.hypot(*a); return 2/3*_cross(a, _sub(s[3], s[2]))/L**3
def k1(s):
    a = _sub(s[4], s[3]); L = math.hypot(*a); return 2/3*_cross(a, _sub(s[2], s[3]))/L**3
def kink(s1, s2):
    a, b = _unit(_sub(s1[4], s1[3])), _unit(_sub(s2[2], s2[1]))
    if a is None or b is None: return 180.0
    return math.degrees(math.acos(max(-1.0, min(1.0, a[0]*b[0] + a[1]*b[1]))))


def joins(segs):
    n = len(segs)
    return [i for i in range(n) if segs[i][0] == 'C' and segs[(i + 1) % n][0] == 'C' and kink(segs[i], segs[(i + 1) % n]) < SMOOTH]


def fair(segs):
    """segs: chuỗi đoạn vòng ['L', a, b] / ['C', p0, p1, p2, p3]. Trả về chuỗi mới cùng cấu trúc."""
    S = [list(s) for s in segs]; n = len(S); J = joins(S)
    if not J: return S
    for i in J:                                            # 1. nút trơn: hai tay nắm chung hướng
        a, b = S[i], S[(i + 1) % n]
        la, lb = math.dist(a[3], a[4]), math.dist(b[1], b[2])
        u = _unit(_sub(a[4], a[3])); v = _unit(_sub(b[2], b[1])); d = _unit((u[0] + v[0], u[1] + v[1]))
        a[3] = (a[4][0] - la*d[0], a[4][1] - la*d[1]); b[2] = (b[1][0] + lb*d[0], b[1][1] + lb*d[1])
    # tay nắm độ dài 0 (góc đầu nét: cubic suy biến) giữ nguyên
    C = [i for i in range(n) if S[i][0] == 'C' and math.dist(S[i][1], S[i][2]) > 1e-6 and math.dist(S[i][3], S[i][4]) > 1e-6]
    dirs = {i: (_unit(_sub(S[i][2], S[i][1])), _unit(_sub(S[i][3], S[i][4]))) for i in C}
    L0 = np.array([[math.dist(S[i][1], S[i][2]), math.dist(S[i][4], S[i][3])] for i in C])
    old = {i: [_bez(S[i], t/8) for t in range(1, 8)] for i in range(n) if S[i][0] == 'C'}
    ix = {i: k for k, i in enumerate(C)}
    # nút trơn được TRƯỢT dọc tiếp tuyến của nó (giữ cực trị: nút ở cực trái / đỉnh trượt dọc / ngang, toạ độ cực không đổi)
    tang = {i: _unit(_sub(S[(i + 1) % n][2], S[(i + 1) % n][1])) for i in J}
    nC = 2*len(C)

    def build(x):
        L = np.exp(x[:nC]).reshape(-1, 2); T = [list(s) for s in S]
        for k, i in enumerate(J):                            # trượt nút: dời cả hai tay nắm kề theo
            t = tang[i]; dx, dy = x[nC + k]*t[0], x[nC + k]*t[1]; j = (i + 1) % n
            for q, idx in ((T[i], 4), (T[i], 3), (T[j], 1), (T[j], 2)):
                q[idx] = (q[idx][0] + dx, q[idx][1] + dy)
        for i in C:
            (u0, u1), (a, b) = dirs[i], L[ix[i]]
            T[i][2] = (T[i][1][0] + a*u0[0], T[i][1][1] + a*u0[1]); T[i][3] = (T[i][4][0] + b*u1[0], T[i][4][1] + b*u1[1])
        return T

    def res(x):
        T = build(x); r = []
        for i in J:
            r.append(W2*(k1(T[i]) - k0(T[(i + 1) % n])))       # G2: độ cong hai bên bằng nhau
        for i in old:
            for t, q in zip(range(1, 8), old[i]):
                p = _bez(T[i], t/8); r += [(p[0] - q[0])/TOL, (p[1] - q[1])/TOL]
        r += list(x[nC:]/SLIDE)
        return np.array(r)

    x0 = np.concatenate([np.log(L0.ravel()), np.zeros(len(J))])
    lo = np.concatenate([np.log(0.3*L0.ravel()), -MAXSLIDE*np.ones(len(J))])
    hi = np.concatenate([np.log(2.2*L0.ravel()), MAXSLIDE*np.ones(len(J))])
    sol = least_squares(res, x0, bounds=(lo, hi), method='trf', xtol=1e-12, ftol=1e-12, max_nfev=6000)
    return build(sol.x)


def report(segs):
    """[(nút, bán kính vào, bán kính ra, gãy°)] cho mọi nút trơn"""
    n = len(segs); out = []
    for i in joins(segs):
        a, b = segs[i], segs[(i + 1) % n]; ki, ko = k1(a), k0(b)
        out.append((a[4], 1/ki if ki else math.inf, 1/ko if ko else math.inf, kink(a, b)))
    return out


def deviation(A, B):
    """lệch hình lớn nhất (u) giữa hai chuỗi đoạn cùng cấu trúc"""
    m = 0.0
    for s, t in zip(A, B):
        if s[0] != 'C': continue
        Q = [_bez(t, k/200) for k in range(201)]
        for k in range(1, 40):
            p = _bez(s, k/40); m = max(m, min(math.dist(p, q) for q in Q))
    return m
