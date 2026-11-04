import math
def bez(p, t):
    u = 1 - t
    return (u**3*p[0][0]+3*u*u*t*p[1][0]+3*u*t*t*p[2][0]+t**3*p[3][0], u**3*p[0][1]+3*u*u*t*p[1][1]+3*u*t*t*p[2][1]+t**3*p[3][1])
def circ3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
    if abs(d) < 1e-9: return None
    ux = ((ax*ax+ay*ay)*(by-cy) + (bx*bx+by*by)*(cy-ay) + (cx*cx+cy*cy)*(ay-by)) / d
    uy = ((ax*ax+ay*ay)*(cx-bx) + (bx*bx+by*by)*(ax-cx) + (cx*cx+cy*cy)*(bx-ax)) / d
    return (ux, uy), math.hypot(ax-ux, ay-uy)
def fit(p):
    """p = 4 điểm cubic. Trả (center, r, dev_max, tangent_err_deg) hoặc None nếu gần thẳng."""
    m = bez(p, .5); r = circ3(p[0], m, p[3])
    if r is None: return None
    c, R = r
    dev = max(abs(math.hypot(*(x - y for x, y in zip(bez(p, t/20), c))) - R) for t in range(21))
    def tan_err(P, Q):  # tangent of cubic at P (toward Q) vs circle tangent (perp radius)
        tx, ty = Q[0]-P[0], Q[1]-P[1]; rx, ry = P[0]-c[0], P[1]-c[1]
        if math.hypot(tx, ty) < 1e-6: return 0
        return math.degrees(math.asin(min(1, abs(tx*rx+ty*ry)/math.hypot(tx,ty)/math.hypot(rx,ry))))
    return c, R, dev, max(tan_err(p[0], p[1]), tan_err(p[3], p[2]))
