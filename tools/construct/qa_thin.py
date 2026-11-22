#!/usr/bin/env python3
"""QA nét mảnh (S72, designer 22/11 "đồng bộ hết … nét mỏng đứng N dày hơn nét mỏng của O"): đo trên outlines.json.
    python3 tools/construct/qa_thin.py <outlines.json> <chuẩn Regular> <chuẩn Bold> [hệ số ngang 0.88] [chars]
Mỗi đoạn THẲNG (≥ 40 u): bắn tia vuông góc vào trong ở 5 điểm dọc đoạn, chỉ nhận khi mép gặp song song (±8°) → bề dày nét.
Nét mảnh = bề dày < 1.6 × chuẩn Serif (42 / 56.5). Chuẩn đứng / chéo = chuẩn; nét NGANG = chuẩn × hệ số ngang. Báo nét lệch > 2.5 u."""
import json, math, re, sys
def polys(d):
    toks = re.findall(r'[MLCZ]|-?\d+(?:\.\d+)?', d); P = []; S = []; cur = []; seg = []; i = 0; last = None
    while i < len(toks):
        t = toks[i]
        if t == 'M': last = (float(toks[i+1]), float(toks[i+2])); cur = [last]; seg = []; i += 3
        elif t == 'L': p = (float(toks[i+1]), float(toks[i+2])); seg.append((last, p)); cur.append(p); last = p; i += 3
        elif t == 'C':
            c = [last] + [(float(toks[i+1+2*k]), float(toks[i+2+2*k])) for k in range(3)]
            for k in range(1, 25):
                s = k/24; cur.append(tuple((1-s)**3*c[0][j] + 3*(1-s)**2*s*c[1][j] + 3*(1-s)*s*s*c[2][j] + s**3*c[3][j] for j in (0, 1)))
            last = c[3]; i += 7
        elif t == 'Z':
            if math.dist(last, cur[0]) > 1e-6: seg.append((last, cur[0]))
            P.append(cur); S += seg; i += 1
    return P, S
def inside(pt, P):
    c = False
    for poly in P:
        for k in range(len(poly)):
            (x1, y1), (x2, y2) = poly[k - 1], poly[k]
            if (y1 > pt[1]) != (y2 > pt[1]) and pt[0] < (x2 - x1)*(pt[1] - y1)/(y2 - y1) + x1: c = not c
    return c
def ray(o, d, P):
    best = None
    for poly in P:
        for k in range(len(poly)):
            a, b = poly[k - 1], poly[k]; ex, ey = b[0] - a[0], b[1] - a[1]; den = d[0]*ey - d[1]*ex
            if abs(den) < 1e-12: continue
            t = ((a[0] - o[0])*ey - (a[1] - o[1])*ex)/den; u = ((a[0] - o[0])*d[1] - (a[1] - o[1])*d[0])/den
            if t > 0.5 and 0 <= u <= 1 and (best is None or t < best[0]): best = (t, (ex, ey))
    return best
def thin_lines(d, ser):
    P, S = polys(d); out = []
    for a, b in S:
        L = math.dist(a, b)
        if L < 40: continue
        u = ((b[0] - a[0])/L, (b[1] - a[1])/L); n = (-u[1], u[0])
        mid = ((a[0] + b[0])/2, (a[1] + b[1])/2)
        if not inside((mid[0] + 1.5*n[0], mid[1] + 1.5*n[1]), P): n = (-n[0], -n[1])
        ts = []
        for s in (0.15, 0.3, 0.5, 0.7, 0.85):
            p = (a[0] + (b[0] - a[0])*s, a[1] + (b[1] - a[1])*s); h = ray(p, n, P)
            if not h: continue
            e = h[1]; el = math.hypot(*e)
            if abs(e[0]/el*u[0] + e[1]/el*u[1]) < math.cos(math.radians(8)): continue
            ts.append(h[0])
        if ts:
            t = sorted(ts)[len(ts)//2]
            if t < 1.6*ser: out.append((t, abs(u[1]), (round(mid[0]), round(mid[1]))))
    return out
if __name__ == '__main__':
    O = json.load(open(sys.argv[1])); tR, tB = float(sys.argv[2]), float(sys.argv[3])
    bk = float(sys.argv[4]) if len(sys.argv) > 4 else 0.88
    chars = sys.argv[5] if len(sys.argv) > 5 else 'ABDEFHIKLMNPRTUVWXYZbdfhijklmnpqrtuvwxyz147'
    bad = 0
    for w, tg, ser in (('Regular', tR, 42.0), ('Bold', tB, 56.5)):
        row = []
        for ch in chars:
            k = f'{ch}-{w}'
            if k not in O: continue
            for t, uy, mid in thin_lines(O[k], ser):
                want = tg*bk if uy < 0.03 else tg                      # đoạn NGANG (u_y ≈ 0) → chuẩn × hệ số ngang
                if abs(t - want) > 2.5: row.append(f'{ch}{t:.0f}(≠{want:.0f})@{mid}'); bad += 1
        print(f'{w} chuẩn {tg} (ngang {tg*bk:.1f}): lệch > 2.5 u:', len(row)); print('   ', ' '.join(row[:60]))
    print('tổng nét mảnh lệch:', bad)
