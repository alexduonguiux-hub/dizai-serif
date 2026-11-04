"""Nhận diện cung elip trong cubic: cubic có hai tay nắm cùng tỉ lệ ρ với giao điểm tiếp tuyến Q
⇔ xấp xỉ chuẩn của cung conic (P0, Q, P3, w), w = ρ / (4/3 − ρ). Trả tâm, trục, góc của elip."""
import math
import numpy as np

def inter(p0, p1, p3, p2):
    d1 = np.subtract(p1, p0); d2 = np.subtract(p2, p3); A = np.array([d1, -d2]).T
    if abs(np.linalg.det(A)) < 1e-9: return None
    s, t = np.linalg.solve(A, np.subtract(p3, p0)); return np.add(p0, s * d1), s, t

def ellipse_of(p):
    p0, p1, p2, p3 = map(np.array, p)
    r = inter(p0, p1, p3, p2)
    if r is None: return None
    Q, s, t = r
    if s <= 0 or t <= 0: return None
    r0, r3 = 1 / s, 1 / t                                  # |P1-P0| / |Q-P0|
    if abs(r0 - r3) > 0.02 or not (0.45 < r0 < 0.66): return None
    rho = (r0 + r3) / 2; w = rho / (4 / 3 - rho)
    if w >= 0.999: return None
    C = (p0 + p3 - 2 * w * w * Q) / (2 * (1 - w * w))
    S = (p0 + 2 * w * Q + p3) / (2 + 2 * w)
    rows = [[x * x, 2 * x * y, y * y] for x, y in (p0 - C, p3 - C, S - C)]
    try: a, b, c = np.linalg.solve(np.array(rows), np.ones(3))
    except np.linalg.LinAlgError: return None
    ev, evec = np.linalg.eigh(np.array([[a, b], [b, c]]))
    if (ev <= 0).any(): return None
    ax = 1 / np.sqrt(ev)                                    # semi-axes
    i = int(np.argmax(ax)); v = evec[:, i]; ang = math.degrees(math.atan2(v[1], v[0])) % 180
    return {"c": [float(C[0]), float(C[1])], "rl": float(ax[i]), "rs": float(ax[1 - i]), "ang": ang,
            "M": [float(a), float(b), float(c)]}

def same(e, f, tol=8.0):
    if math.dist(e["c"], f["c"]) > tol or abs(e["rl"] - f["rl"]) > tol or abs(e["rs"] - f["rs"]) > tol: return False
    if abs(e["rl"] - e["rs"]) < 2: return True               # gần tròn: góc không quan trọng
    da = abs(e["ang"] - f["ang"]) % 180; return min(da, 180 - da) < 3
