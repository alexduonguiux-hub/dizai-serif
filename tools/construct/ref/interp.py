#!/usr/bin/env python3
"""Nội suy weight từ bản vẽ designer (chữ hoa + số): Regular ↔ Bold → Medium (t = 1/3), SemiBold (t = 2/3).
Designer 05/11: "thêm 2 weight medium và semi bold" — chọn "tự sinh toàn bộ", bậc đều theo độ dày nét.
    python3 tools/construct/ref/interp.py   → designer_M.json

Giữ ĐIỂM NEO của bản vẽ (không lấy mẫu lại):
 1. Ghép contour Regular ↔ Bold theo tâm (toạ độ chuẩn hoá theo hộp glyph), cùng chiều (diện tích có dấu).
 2. Căn chuỗi điểm neo hai contour bằng quy hoạch động (vòng, thử mọi điểm bắt đầu): chi phí = khoảng cách chuẩn hoá + lệch
    hướng tiếp tuyến; điểm neo một bên không có cặp → tách đoạn tương ứng bên kia tại tham số gần điểm đó nhất.
 3. Đoạn thẳng ↔ đoạn cong: đổi thẳng thành cubic (tay nắm 1/3, 2/3). Nội suy từng điểm: P = (1 − t)·R + t·B.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from make_ref import parse
WT = {'Medium': 1/3, 'SemiBold': 2/3}

def contours(paths):
    out = []
    for d in paths:
        cur = None
        for c, pts in parse(d):
            if c == 'M': cur = {'s': pts[0], 'g': []}; last = pts[0]
            elif c == 'L': cur['g'].append(['L', last, pts[0]]); last = pts[0]
            elif c == 'C': cur['g'].append(['C', last, pts[0], pts[1], pts[2]]); last = pts[2]
            elif c == 'Z':
                if math.dist(last, cur['s']) > 1e-6: cur['g'].append(['L', last, cur['s']])
                out.append(cur['g'])
    return out

def area(g):
    pts = [s[1] for s in g]; return sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(pts, pts[1:] + pts[:1]))/2

def reverse(g):
    out = []
    for s in reversed(g):
        out.append(['L', s[2], s[1]] if s[0] == 'L' else ['C', s[4], s[3], s[2], s[1]])
    return out

def bez(s, t):
    if s[0] == 'L': a, b = s[1], s[2]; return (a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t)
    a, b, c, d = s[1:]; u = 1 - t
    return (u**3*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t**3*d[0], u**3*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t**3*d[1])

def split(s, t):
    if s[0] == 'L':
        m = bez(s, t); return ['L', s[1], m], ['L', m, s[2]]
    a, b, c, d = s[1:]; L = lambda p, q: (p[0] + (q[0] - p[0])*t, p[1] + (q[1] - p[1])*t)
    ab, bc, cd = L(a, b), L(b, c), L(c, d); abc, bcd = L(ab, bc), L(bc, cd); m = L(abc, bcd)
    return ['C', a, ab, abc, m], ['C', m, bcd, cd, d]

def tan_in(s):  # hướng tiếp tuyến tại điểm đầu đoạn
    if s[0] == 'L': a, b = s[1], s[2]
    else:
        a = s[1]; b = next((q for q in s[2:] if math.dist(q, a) > 1e-6), s[4])
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1; return ((b[0] - a[0])/L, (b[1] - a[1])/L)

def align(gr, gb, nr, nb):
    """căn hai chuỗi đoạn (cùng chiều). nr / nb: hàm chuẩn hoá toạ độ. Trả về hai danh sách đoạn cùng độ dài."""
    best = None
    A = [s[1] for s in gr]; B = [s[1] for s in gb]; TA = [tan_in(s) for s in gr]; TB = [tan_in(s) for s in gb]
    def cost(i, j):
        pa, pb = nr(A[i]), nb(B[j]); dt = 1 - (TA[i][0]*TB[j][0] + TA[i][1]*TB[j][1])
        return math.dist(pa, pb) + 0.15*dt
    GAP = 0.08
    n, m = len(gr), len(gb)
    for sh in range(m):
        Bi = [(j + sh) % m for j in range(m)]
        D = [[math.inf]*(m + 1) for _ in range(n + 1)]; P = [[None]*(m + 1) for _ in range(n + 1)]
        D[0][0] = 0
        for i in range(n + 1):
            for j in range(m + 1):
                if i == 0 and j == 0: continue
                c = []
                if i and j: c.append((D[i-1][j-1] + cost(i - 1, Bi[j - 1]), 'M'))
                if i: c.append((D[i-1][j] + GAP, 'A'))          # neo của R không cặp
                if j: c.append((D[i][j-1] + GAP, 'B'))          # neo của B không cặp
                D[i][j], P[i][j] = min(c)
        # neo đầu tiên phải ghép đôi (mốc vòng)
        if best is None or D[n][m] < best[0]:
            ops = []; i, j = n, m
            while i or j:
                o = P[i][j]; ops.append(o)
                if o == 'M': i -= 1; j -= 1
                elif o == 'A': i -= 1
                else: j -= 1
            best = (D[n][m], sh, ops[::-1])
    _, sh, ops = best
    gb = gb[sh:] + gb[:sh]
    # dựng lại: mỗi 'A' (R có neo, B không) → tách đoạn B đang đi; mỗi 'B' → tách đoạn R
    R, Bo = [], []; i = j = 0; pend_r = []; pend_b = []
    # gom thành các khối: một neo ghép đôi 'M' mở một đoạn chung; các neo lẻ sau nó chia đoạn bên kia
    blocks = []
    for o in ops:
        if o == 'M': blocks.append({'r': [gr[i]], 'b': [gb[j]]}); i += 1; j += 1
        elif o == 'A':
            if not blocks: blocks.append({'r': [], 'b': []})
            blocks[-1]['r'].append(gr[i]); i += 1
        else:
            if not blocks: blocks.append({'r': [], 'b': []})
            blocks[-1]['b'].append(gb[j]); j += 1
    # khối đầu có thể bắt đầu bằng neo lẻ (trước 'M' đầu): gộp vào khối cuối (vòng)
    if blocks and (not blocks[0]['r'] or not blocks[0]['b']):
        f = blocks.pop(0); blocks[-1]['r'] += f['r']; blocks[-1]['b'] += f['b']
    for bl in blocks:
        rs, bs = bl['r'], bl['b']
        while len(rs) < len(bs): rs = split_longest(rs, len(bs))
        while len(bs) < len(rs): bs = split_longest(bs, len(rs))
        R += rs; Bo += bs
    return R, Bo

def seglen(s):
    pts = [bez(s, k/12) for k in range(13)]; return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))

def split_longest(segs, target):
    i = max(range(len(segs)), key=lambda k: seglen(segs[k])); a, b = split(segs[i], 0.5)
    return segs[:i] + [a, b] + segs[i+1:]

def tocubic(s):
    if s[0] == 'C': return s
    a, b = s[1], s[2]; return ['C', a, (a[0] + (b[0] - a[0])/3, a[1] + (b[1] - a[1])/3), (a[0] + 2*(b[0] - a[0])/3, a[1] + 2*(b[1] - a[1])/3), b]

def lerp(p, q, t):
    x, y = p[0] + (q[0] - p[0])*t, p[1] + (q[1] - p[1])*t
    # điểm nằm TRÊN đường chân / cap ở một master, sát đường đó (< 20) ở master kia (móc loe chân K Regular ↔ chân cắt nhọn K
    # Bold): nội suy ra một VÁT XIÊN ở Medium / SemiBold (designer 05/11: "lỗi nét chân chữ k") → đặt lên đường đó
    for yl in (0.0, 700.0):
        if (abs(p[1] - yl) < 0.6 and abs(q[1] - yl) < 20) or (abs(q[1] - yl) < 0.6 and abs(p[1] - yl) < 20): y = yl
    return (x, y)

def interp_glyph(pr, pb, t):
    cr, cb = contours(pr), contours(pb)
    assert len(cr) == len(cb), (len(cr), len(cb))
    def bbox(cs):
        xs = [q[0] for g in cs for s in g for q in s[1:]]; ys = [q[1] for g in cs for s in g for q in s[1:]]
        return min(xs), min(ys), max(xs), max(ys)
    br, bb = bbox(cr), bbox(cb)
    nr = lambda p: ((p[0] - br[0])/(br[2] - br[0]), (p[1] - br[1])/(br[3] - br[1]))
    nb = lambda p: ((p[0] - bb[0])/(bb[2] - bb[0]), (p[1] - bb[1])/(bb[3] - bb[1]))
    def sig(g, n):                                                 # tâm + cỡ hộp (chuẩn hoá): tách contour ngoài / lòng cùng tâm (0 O)
        P = [n(q) for s in g for q in s[1:]]; xs = [p[0] for p in P]; ys = [p[1] for p in P]
        return ((min(xs) + max(xs))/2, (min(ys) + max(ys))/2, max(xs) - min(xs), max(ys) - min(ys))
    used = set(); pairs = []
    for g in cr:
        c = sig(g, nr); k = min((k for k in range(len(cb)) if k not in used), key=lambda k: math.dist(c, sig(cb[k], nb)))
        used.add(k); pairs.append((g, cb[k]))
    out = []
    for g, h in pairs:
        if (area(g) > 0) != (area(h) > 0): h = reverse(h)
        R, B = align(g, h, nr, nb)
        segs = []
        for s, u in zip(R, B):
            if s[0] == 'L' and u[0] == 'L': segs.append(['L', lerp(s[1], u[1], t), lerp(s[2], u[2], t)])
            else:
                s, u = tocubic(s), tocubic(u); segs.append(['C'] + [lerp(a, b, t) for a, b in zip(s[1:], u[1:])])
        # chỗ nối TRƠN ở CẢ HAI master (điểm tách thêm luôn trơn) → bản nội suy cũng trơn: tay nắm hai bên thẳng hàng theo hướng
        # trung bình (hai master trơn nhưng khác hướng tiếp tuyến thì nội suy làm tay nắm lệch → gãy). Góc có trong bản vẽ giữ nguyên.
        def tout(sg):                                              # hướng tiếp tuyến ở cuối đoạn
            if sg[0] == 'L': a, b = sg[1], sg[2]
            else:
                b = sg[4]; a = next((q for q in (sg[3], sg[2], sg[1]) if math.dist(q, b) > 1e-6), sg[1])
            L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1; return ((b[0] - a[0])/L, (b[1] - a[1])/L)
        def smooth(lst, k):
            a, b = tout(lst[k]), tan_in(lst[(k + 1) % len(lst)]); return a[0]*b[0] + a[1]*b[1] > math.cos(math.radians(4))
        n = len(segs)
        for k in range(n):
            a, b = segs[k], segs[(k + 1) % n]
            if a[0] != 'C' or b[0] != 'C' or not (smooth(R, k) and smooth(B, k)): continue
            p = a[4]; h1 = (p[0] - a[3][0], p[1] - a[3][1]); h2 = (b[2][0] - p[0], b[2][1] - p[1])
            l1, l2 = math.hypot(*h1), math.hypot(*h2)
            if l1 < 1e-6 or l2 < 1e-6: continue
            dx, dy = h1[0]/l1 + h2[0]/l2, h1[1]/l1 + h2[1]/l2; L = math.hypot(dx, dy)
            if L < 1e-6: continue
            dx, dy = dx/L, dy/L
            a[3] = (p[0] - dx*l1, p[1] - dy*l1); b[2] = (p[0] + dx*l2, p[1] + dy*l2)
        cmds = ['M%.2f %.2f' % segs[0][1]]
        for sg in segs:
            if sg[0] == 'L': cmds.append('L%.2f %.2f' % sg[2])
            else: cmds.append('C%.2f %.2f %.2f %.2f %.2f %.2f' % (*sg[2], *sg[3], *sg[4]))
        out.append(''.join(cmds) + 'Z')
    return [' '.join(out)]

def build():
    S = {}; W = {}
    for f in ('designer_A.json', 'designer_B.json'):
        d = json.load(open(os.path.join(HERE, f))); W.update(d.pop('_W', {})); S.update(d)
    out = {}; Wo = {}
    for ch in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        for w, t in WT.items():
            out[f'{ch}-{w}'] = interp_glyph(S[f'{ch}-Regular'], S[f'{ch}-Bold'], t)
            wr, wb = W.get(f'{ch}-Regular'), W.get(f'{ch}-Bold')
            if wr is not None and wb is not None: Wo[f'{ch}-{w}'] = round(wr + (wb - wr)*t)
    out['_W'] = Wo
    json.dump(out, open(os.path.join(HERE, 'designer_M.json'), 'w'), separators=(',', ':'))
    print('ok', len(out) - 1)

if __name__ == '__main__':
    build()
