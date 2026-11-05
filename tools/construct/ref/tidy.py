"""Dọn outline sau phép boolean (QA: "nét thừa và lỗi").
  strong=True  (glyph dựng theo luật): gộp đoạn < 2.5 u (khấc), bỏ gai do mẩu < 12 u quay ngược, nắn gãy nhỏ < 12° giữa hai
               đoạn cong thành liền mạch G1, bỏ điểm trùng, gộp đoạn thẳng thẳng hàng, bỏ vòng kín < 400 u².
  strong=False (bản vẽ designer): gộp mẩu thừa < 2.5 u, bỏ điểm thẳng hàng, nắn gãy < 20° giữa hai đoạn cong (G1);
               giữ nguyên mọi mũi nhọn chủ ý (mỏ E, đầu S, C, mũi loe).
"""
import math
import pathops

def _contours(path):
    out, cur, start, p = [], [], None, None
    for v, ps in path.segments:
        if v == 'moveTo': cur = []; start = p = ps[0]
        elif v == 'lineTo': cur.append(['L', p, ps[0]]); p = ps[0]
        elif v == 'curveTo': cur.append(['C', p, ps[0], ps[1], ps[2]]); p = ps[2]
        elif v == 'qCurveTo':
            a, b = ps[0], ps[1]; c1 = (p[0] + 2/3*(a[0]-p[0]), p[1] + 2/3*(a[1]-p[1])); c2 = (b[0] + 2/3*(a[0]-b[0]), b[1] + 2/3*(a[1]-b[1]))
            cur.append(['C', p, c1, c2, b]); p = b
        elif v == 'closePath':
            if math.dist(p, start) > 1e-9: cur.append(['L', p, start])
            out.append(cur); cur = []
    return out

def _len(s): return sum(math.dist(a, b) for a, b in zip(s[1:], s[2:]))
def _ang(a, b): return math.atan2(b[1] - a[1], b[0] - a[0])
def _tin(s):
    for q in reversed(s[1:-1]):
        if math.dist(q, s[-1]) > 1e-6: return _ang(q, s[-1])
def _tout(s):
    for q in s[2:]:
        if math.dist(q, s[1]) > 1e-6: return _ang(s[1], q)
def _turn(a, b):
    if a is None or b is None: return None
    return abs((math.degrees(b - a) + 180) % 360 - 180)
def _area(c):
    pts = [s[1] for s in c]
    return 0.5*sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(pts, pts[1:] + pts[:1]))

def _set_start(s, q):
    d = (q[0] - s[1][0], q[1] - s[1][1]); s[1] = q
    if s[0] == 'C': s[2] = (s[2][0] + d[0], s[2][1] + d[1])
def _set_end(s, q):
    d = (q[0] - s[-1][0], q[1] - s[-1][1]); s[-1] = q
    if s[0] == 'C': s[3] = (s[3][0] + d[0], s[3][1] + d[1])

def _pass(c, strong):
    n = len(c); changed = False
    # 1. đoạn suy biến / quá ngắn: gộp vào điểm giữa
    lim = 2.5   # khấc / mẩu thừa < 2.5 u: gộp (lệch hình < 1.3 u, không thấy được)
    for i in range(n):
        s = c[i]
        if len(c) > 3 and _len(s) < lim:
            m = ((s[1][0] + s[-1][0])/2, (s[1][1] + s[-1][1])/2)
            _set_end(c[i - 1], m); _set_start(c[(i + 1) % len(c)], m); del c[i]; return True
    # 2. đường thẳng thẳng hàng
    for i in range(len(c)):
        a, b = c[i], c[(i + 1) % len(c)]
        if a[0] == 'L' and b[0] == 'L' and len(c) > 3:
            t = _turn(_ang(a[1], a[2]), _ang(b[1], b[2]))
            if t is not None and t < 0.6:
                a[2] = b[2]; del c[(i + 1) % len(c)]; return True
    # 3. gai (chỉ glyph dựng theo luật: ở bản vẽ designer, mũi nhọn là chủ ý — mỏ E, đầu S, C)
    if not strong: return _g1(c, 20)
    # 3. gai: mẩu ngắn quay ngược
    for i in range(len(c)):
        a, b = c[i], c[(i + 1) % len(c)]
        t = _turn(_tin(a), _tout(b))
        if t is not None and t > 150 and (_len(a) < 12 or _len(b) < 12) and len(c) > 4:
            j = i if _len(a) < _len(b) else (i + 1) % len(c)
            s = c[j]; m = s[1] if j == i else s[-1]
            # bỏ mẩu ngắn hơn, nối hai bên
            prv, nxt = c[j - 1], c[(j + 1) % len(c)]
            # chỉ là gai khi phần bỏ đi gần như không có diện tích (sợi); mũi nhọn thật (chóp mỏ T trong ™: đoạn cong 11.5 u gãy
            # 150°+ vào mép đứng, tam giác bỏ đi ≈ 160 u²) thì giữ — designer 05/11 "Module T trong cụm TM vẫn lỗi"
            A_, B_, C_ = s[1], s[-1], nxt[-1]
            if abs((B_[0] - A_[0])*(C_[1] - A_[1]) - (B_[1] - A_[1])*(C_[0] - A_[0]))/2 > 30: continue
            _set_end(prv, s[1]); _set_start(nxt, s[1]); del c[j]; return True
    return _g1(c, 20)

def _g1(c, maxturn):
    """gãy nhỏ giữa hai đoạn cong: xoay tay nắm về tiếp tuyến trung bình (liền mạch G1); chạy một lần"""
    for i in range(len(c)):
        a, b = c[i], c[(i + 1) % len(c)]
        if a[0] == 'C' and b[0] == 'C':
            ta, tb = _tin(a), _tout(b); t = _turn(ta, tb)
            if t is not None and 0.5 < t < maxturn:
                d = (tb - ta + math.pi) % (2*math.pi) - math.pi; tm = ta + d/2; p = a[-1]
                la, lb = math.dist(a[3], p), math.dist(b[2], p)
                if la < 1.5: la = 0.3*math.dist(a[1], p)            # tay nắm suy biến (< 1.5 u): dựng lại 0.3 dây cung
                if lb < 1.5: lb = 0.3*math.dist(b[-1], p)
                if la > 1e-6 and lb > 1e-6:
                    a[3] = (p[0] - la*math.cos(tm), p[1] - la*math.sin(tm)); b[2] = (p[0] + lb*math.cos(tm), p[1] + lb*math.sin(tm))
    return False

def tidy(path, strong=True):
    out = pathops.Path()
    for c in _contours(path):
        if strong and abs(_area(c)) < 400: continue
        for _ in range(200):
            if not _pass(c, strong): break
        for _ in range(6): _g1(c, 20)     # nắn G1 hội tụ (tay nắm suy biến cần vài lượt)
        if len(c) < 2: continue
        out.moveTo(*c[0][1])
        for s in c:
            if s[0] == 'L': out.lineTo(*s[2])
            else: out.cubicTo(*s[2], *s[3], *s[4])
        out.close()
    return out
