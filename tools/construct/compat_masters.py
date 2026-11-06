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
3. Medium / SemiBold = nội suy đúng hai master (TW 1/3, 2/3) → bản tĩnh trùng khít bản variable.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'font'))
sys.path.insert(0, os.path.join(HERE, 'ref'))
from compat import compat, lerp_segs, to_d
from interp import contours, tocubic
from weights import WEIGHTS, TW
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

def main():
    O = json.load(open(os.path.join(OUT, 'outlines.json')))
    chars = sorted({k.rsplit('-', 1)[0] for k in O})
    stat = {'glyph': 0, 'ghép được': 0, 'không ghép': [], 'đoạn trước': 0, 'đoạn sau': 0}
    pre = dict(O)
    for c in chars:
        kr, kb = f'{c}-Regular', f'{c}-Bold'
        if kr not in O or kb not in O: continue
        stat['glyph'] += 1
        # đơn giản hoá TỪNG master trước (bỏ điểm thừa của boolean / làm đậm), rồi mới ghép cặp
        for k_ in (kr, kb):
            cs = [simplify_pair([list(x) for x in g], [list(x) for x in g])[0] for g in contours([O[k_]])]
            O[k_] = to_d(cs)
        try: C = compat(O[kr], O[kb])
        except Exception as e: stat['không ghép'].append(c); continue
        if not C: continue
        before = sum(len(g) for g in contours([pre[kr]]))
        out = []
        for Rr, Bb in C:
            Rr, Bb = simplify_pair([list(s) for s in Rr], [list(s) for s in Bb]); out.append((Rr, Bb))
        after = sum(len(a) for a, _ in out)
        stat['đoạn trước'] += before; stat['đoạn sau'] += after; stat['ghép được'] += 1
        for w in WEIGHTS:
            O[f'{c}-{w}'] = to_d([lerp_segs(a, b, TW[w]) for a, b in out])
    json.dump(O, open(os.path.join(OUT, 'outlines.json'), 'w'))
    print('compat:', {k: (v if not isinstance(v, list) else len(v)) for k, v in stat.items()}, 'không ghép:', stat['không ghép'][:30])

if __name__ == '__main__':
    main()
