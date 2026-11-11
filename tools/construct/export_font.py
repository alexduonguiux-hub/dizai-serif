#!/usr/bin/env python3
"""Xuất font: UFO master Regular + Bold (Roman và Italic) → designspace → variable TTF (wght 400–700) + bản tĩnh OTF / TTF.
    python3 tools/construct/export_font.py      (sau spacing.py)  → fonts/

Designer 05/11: "làm bản variable luôn nhé, thêm cả Italic".
- Master: outlines.json (compat_masters.py đã đưa Regular / Bold về cùng cấu trúc); Medium 500 / SemiBold 600 là instance
  (TW 1/3, 2/3 → đúng bản tĩnh đã dựng).
- Chiều contour: chuẩn PostScript (ngoài ngược chiều kim đồng hồ) theo lồng nhau của master Regular, đảo cùng chỉ số ở Bold.
- Kerning: class (spacing.py) → groups public.kern1 / kern2; ngoại lệ chống va ghi tường minh ở CẢ HAI master (thiếu thì lấy giá
  trị class) để nội suy đúng.
- ccmp: chuỗi NFD (chữ gốc + dấu tổ hợp) → chữ dựng sẵn.
- Italic (I1): nghiêng 10° quanh y = ½ x-height (cách của chữ glyphic loe nét: Optima / Palatino Sans Italic là roman nghiêng
  có hệ thống). Mọi glyph nghiêng như nhau quanh cùng một đường → khe giữa hai chữ ở mọi cao độ giữ nguyên → spacing và kerning
  của Roman đúng tuyệt đối cho Italic.
- Bản tĩnh tạo bằng instancer từ chính file variable → trùng khít bản variable.
"""
import json, math, os, re, sys, unicodedata, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ufoLib2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'release')); import license_meta as LM
from fontTools.agl import UV2AGL
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
import spacing as SPc
ROOT = os.path.join(HERE, '..', '..'); OUT = os.path.join(ROOT, 'out', 'construct'); FONTS = os.path.join(ROOT, 'fonts')
BUILD = os.path.join(OUT, 'ufo')
FAMILY, PS = 'AnNam Serif', 'AnNamSerif'   # designer 06/11: AnNam → thêm chữ phân biệt với BT Annam Neue (BeauType)
VENDOR = 'DZAI'                                # Đìzai Studio (4 ký tự theo chuẩn OpenType — 'DIZAI' 5 ký tự không dùng được) — nên đăng ký với Microsoft (mstwsite@microsoft.com)
#          # designer 06/11 "Đổi tên Font thành AnNam" (trước: Dizai Serif / DizaiSerif)
VERSION = (0, 911)
ITALIC_ANGLE = 10.0
WGHT = {'Regular': 400, 'Medium': 500, 'SemiBold': 600, 'Bold': 700}

OUTI = os.path.join(ROOT, 'out', 'construct_italic')            # Italic I2 (italic.py): thiết kế italic đứng, nghiêng khi xuất
def use(style):
    """nạp outline / spacing / kerning của Roman hoặc Italic (I2 nếu có out/construct_italic, không thì Roman nghiêng — I1)"""
    global O, SP, KN
    d = OUTI if style == 'Italic' and os.path.exists(os.path.join(OUTI, 'kerning.json')) else OUT
    O = json.load(open(os.path.join(d, 'outlines.json'))); SP = json.load(open(os.path.join(d, 'spacing.json')))
    KN = json.load(open(os.path.join(d, 'kerning.json')))
    return d
use('Roman')
CHARS = sorted(SP['Regular'], key=ord)

def gname(c):
    u = ord(c)
    if c == ' ': return 'space'
    return UV2AGL.get(u) or ('uni%04X' % u)

def parse(d):
    """'M x y L x y C … Z' → [[('M', p), ('L', p), ('C', p1, p2, p3)…]]"""
    toks = re.findall(r'[MLCZ]|-?\d+(?:\.\d+)?', d); cs = []; cur = None; i = 0
    while i < len(toks):
        t = toks[i]
        if t == 'M': cur = [('M', (float(toks[i+1]), float(toks[i+2])))]; i += 3
        elif t == 'L': cur.append(('L', (float(toks[i+1]), float(toks[i+2])))); i += 3
        elif t == 'C': cur.append(('C',) + tuple((float(toks[i+1+2*k]), float(toks[i+2+2*k])) for k in range(3))); i += 7
        elif t == 'Z': cs.append(cur); cur = None; i += 1
        else: raise ValueError(t)
    return cs

def poly(c, n=8):
    P = []; p = None
    for s in c:
        if s[0] in 'ML': P.append(s[1]); p = s[1]
        else:
            a, b, e = s[1:]
            for k in range(1, n + 1):
                t = k/n; u = 1 - t
                P.append((u**3*p[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t**3*e[0], u**3*p[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t**3*e[1]))
            p = e
    return P

def area(P): return 0.5*sum(P[i-1][0]*P[i][1] - P[i][0]*P[i-1][1] for i in range(len(P)))

def inside(pt, P):
    x, y = pt; c = False
    for i in range(len(P)):
        (x0, y0), (x1, y1) = P[i-1], P[i]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0)*(x1 - x0)/(y1 - y0): c = not c
    return c

def flips(cs):
    """chỉ số contour cần đảo: độ sâu lồng chẵn → ngược chiều kim (diện tích dương), lẻ → cùng chiều"""
    Ps = [poly(c) for c in cs]; out = []
    for i, P in enumerate(Ps):
        probe = P[0]
        # điểm thử: dời nhẹ vào trong contour để tránh nằm trên biên contour khác
        depth = sum(1 for j, Q in enumerate(Ps) if j != i and abs(area(Q)) > abs(area(P)) and inside(probe, Q))
        want = 1 if depth % 2 == 0 else -1
        if (area(P) > 0) != (want > 0): out.append(i)
    return out

def reverse(c):
    """đảo chiều contour đóng, giữ điểm đầu"""
    pts = [c[0][1]]; segs = []
    for s in c[1:]:
        segs.append(s)
    # chuỗi nút: n0 → s1 → n1 …; contour đóng: nút cuối nối thẳng về n0 nếu khác
    nodes = [c[0][1]] + [s[-1] for s in segs]
    closing = None
    if nodes[-1] != nodes[0]: segs.append(('L', nodes[0])); nodes.append(nodes[0])
    rs = []
    for k in range(len(segs) - 1, -1, -1):
        s = segs[k]; start = nodes[k]
        rs.append(('L', start) if s[0] == 'L' else ('C', s[2], s[1], start))
    out = [('M', nodes[0])] + rs
    if out[-1][0] == 'L' and out[-1][1] == nodes[0]: out.pop()
    return out

def skew(p, a):
    t = math.tan(math.radians(a)); yc = SPc.XH/2
    return (p[0] + (p[1] - yc)*t, p[1])

def _kends(sg):
    """độ cong ở hai đầu một đoạn cong (None nếu tay suy biến)"""
    P0, P1, P2, P3 = sg[1:]
    def k(u, w):
        L = math.hypot(*u); return (u[0]*w[1] - u[1]*w[0])/L**3 if L > 1e-6 else None
    return (k((P1[0] - P0[0], P1[1] - P0[1]), (P2[0] - P1[0], P2[1] - P1[1])),
            k((P3[0] - P2[0], P3[1] - P2[1]), (P1[0] - P2[0], P1[1] - P2[1])))


def _snap_smooth(segs):
    """10/11 ("kiểm tra lại italic các chữ có loe"): làm tròn toạ độ nguyên sau khi nghiêng làm nút liền lệch tới 2–3° (tay nắm
    loe ~20 u, toạ độ không còn nguyên). Neo làm tròn; ở nút liền (< 0.5° trước làm tròn), tay nắm đặt vào điểm NGUYÊN thẳng hàng
    nhất với tiếp tuyến bên kia (cạnh thẳng, hoặc tay nắm dài hơn), dò độ dài ±4 u quanh độ dài gốc.
    S38 (11/11): khi hoà (tiếp tuyến đứng / ngang — mọi độ dài đều thẳng hàng) chọn độ dài GẦN GỐC nhất; trước đây lấy độ dài
    dò đầu tiên = NGẮN nhất (tay ở cực trị ngắn đi tới 3 u → nhảy độ cong, vd. 2 Regular cực phải 24.6 → 22 u)"""
    def u_(a, b):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); return ((b[0] - a[0])/L, (b[1] - a[1])/L) if L > 1e-9 else None
    def ang(a, b):
        return 180.0 if not a or not b else math.degrees(math.acos(max(-1.0, min(1.0, a[0]*b[0] + a[1]*b[1]))))
    n = len(segs)
    def t_end(sg): return u_(sg[-2] if sg[0] == 'C' and math.dist(sg[-2], sg[-1]) > 1e-9 else sg[1], sg[-1])
    def t_start(sg): return u_(sg[1], sg[2] if sg[0] == 'C' and math.dist(sg[2], sg[1]) > 1e-9 else sg[-1])
    smooth = [ang(t_end(segs[i]), t_start(segs[(i + 1) % n])) < 1.5 for i in range(n)]   # góc cố ý đều > 25°
    R = [[sg[0]] + [(round(q[0]), round(q[1])) for q in sg[1:]] for sg in segs]
    def best(P, d, L0):
        bb = None
        for k in range(-8, 9):
            L = L0 + k*0.5
            if L < 1: continue
            q = (round(P[0] + d[0]*L), round(P[1] + d[1]*L)); v = u_(P, q)
            if not v: continue
            e = ang(v, d) + 0.001*abs(k)                             # hoà (tiếp tuyến đứng / ngang): độ dài gần gốc nhất
            if bb is None or e < bb[0] - 1e-6: bb = (e, q)
        return bb[1] if bb else None
    def best_lc(Q, P, L0, cmax=1e9):
        # cạnh thẳng Q → P (P = nút), tay nắm từ P: dò P' = P ± 1 u (gần đường thẳng QP ≤ 0.8 u) × độ dài tay ±4 u
        dq = u_(Q, P); bb = None
        if not dq: return None
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                P2 = (P[0] + ox, P[1] + oy)
                off = abs((P2[0] - Q[0])*dq[1] - (P2[1] - Q[1])*dq[0])
                if off > 0.8: continue
                d2 = u_(Q, P2)
                if not d2: continue
                for k in range(-8, 9):
                    L = (L0 if L0 >= 5 else min(7.0, cmax)) + k*0.5      # tay tí hon (< 5 u) kéo dài: làm tròn tay 3 u lệch tới 10°
                    if L < 1 or (L0 < 5 and L < min(5, cmax)) or L > max(L0, cmax): continue
                    q = (round(P2[0] + dq[0]*L), round(P2[1] + dq[1]*L)); v = u_(P2, q)
                    if not v: continue
                    e = ang(v, d2) + 0.3*(abs(ox) + abs(oy)) + 0.001*abs(k)
                    if bb is None or e < bb[0] - 1e-6: bb = (e, P2, q)
        return bb
    for i in range(n):
        if not smooth[i]: continue
        a, b = R[i], R[(i + 1) % n]; P = a[-1]
        if a[0] == 'L' and b[0] == 'C':
            r = best_lc(a[1], P, math.dist(segs[(i + 1) % n][2], segs[(i + 1) % n][1]), 0.9*math.dist(segs[(i + 1) % n][1], segs[(i + 1) % n][4]))
            if r: a[2] = r[1]; b[1] = r[1]; b[2] = r[2]
        elif a[0] == 'C' and b[0] == 'L':
            r = best_lc(b[2], P, math.dist(segs[i][3], segs[i][4]), 0.9*math.dist(segs[i][1], segs[i][4]))
            if r: a[4] = r[1]; b[1] = r[1]; a[3] = r[2]
        elif a[0] == 'C' and b[0] == 'C':
            # bộ ba (tay vào, neo, tay ra) NGUYÊN thẳng hàng nhất: neo ±1, tay dài ±1, tay ngắn dò theo hướng (tay 3 u: lệch tới 10°)
            sa, sb = segs[i], segs[(i + 1) % n]
            la, lb = math.dist(sa[3], sa[4]), math.dist(sb[2], sb[1])
            kf = _kends(sa) + _kends(sb)                               # S38: độ cong 4 đầu đoạn (bản số thực) — làm tròn tay nắm sát
            def kcost(P2, Hin, Hout):                                  # tiếp tuyến làm độ cong đổi tới 30 % (2 Bold cực phải 4.9 → 3.4)
                kn = _kends(['C', a[1], a[2], Hin, P2]) + _kends(['C', P2, Hout, b[3], b[4]]); c = 0.0
                for x, y in zip(kf, kn):
                    if x is None or abs(x) < 5e-4: continue
                    c += 3.0 if (y is None or x*y <= 0) else abs(math.log(abs(y/x)))
                return c
            if la < 0.5 or lb < 0.5: continue                         # tay suy biến (trùng neo): giữ
            bb = None
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    P2 = (P[0] + ox, P[1] + oy)
                    for hx in (-1, 0, 1):
                        for hy in (-1, 0, 1):
                            if la >= lb:
                                H = (a[3][0] + hx, a[3][1] + hy); dd = u_(H, P2)
                                if not dd: continue
                                for k in range(-6, 7):
                                    cm_ = 0.9*math.dist(sb[1], sb[4])
                                    L = (lb if lb >= 5 else min(7.0, cm_)) + k*0.5
                                    if L < 1 or (lb < 5 and L < min(5, cm_)) or L > max(lb, cm_): continue
                                    q = (round(P2[0] + dd[0]*L), round(P2[1] + dd[1]*L)); e = ang(dd, u_(P2, q))
                                    c_ = e + 0.25*(abs(ox) + abs(oy) + abs(hx) + abs(hy)) + 0.001*abs(k)
                                    if bb is not None and c_ - 2.0 > bb[0]: continue
                                    c_ += 2.0*kcost(P2, H, q)
                                    if bb is None or c_ < bb[0] - 1e-6: bb = (c_, P2, H, q)
                            else:
                                H = (b[2][0] + hx, b[2][1] + hy); dd = u_(P2, H)
                                if not dd: continue
                                for k in range(-6, 7):
                                    cm_ = 0.9*math.dist(sa[1], sa[4])
                                    L = (la if la >= 5 else min(7.0, cm_)) + k*0.5
                                    if L < 1 or (la < 5 and L < min(5, cm_)) or L > max(la, cm_): continue
                                    q = (round(P2[0] - dd[0]*L), round(P2[1] - dd[1]*L)); e = ang(u_(q, P2), dd)
                                    c_ = e + 0.25*(abs(ox) + abs(oy) + abs(hx) + abs(hy)) + 0.001*abs(k)
                                    if bb is not None and c_ - 2.0 > bb[0]: continue
                                    c_ += 2.0*kcost(P2, q, H)
                                    if bb is None or c_ < bb[0] - 1e-6: bb = (c_, P2, q, H)
            if bb:
                _, P2, Hin, Hout = bb; a[3] = Hin; a[4] = P2; b[1] = P2; b[2] = Hout
    for i in range(n):                                            # điểm cuối đoạn = điểm đầu đoạn sau
        R[(i + 1) % n][1] = R[i][-1]
    for sg in R:                                                  # đoạn cong co còn ≤ 2 u sau làm tròn (@ Medium Italic: góc cắt
        if sg[0] == 'C' and math.dist(sg[1], sg[4]) <= 3.0:      # lòng sau bù) → tay về hai đầu: không xoắn; giữ số điểm
            sg[2], sg[3] = sg[1], sg[4]
    # làm tròn làm độ cong sát 0 ở mũi loe LẬT DẤU (gợn, bán kính > 1000 u): nhích tay nắm KHÔNG nằm ở nút liền ±1–2 u
    def kap(sg, m=24):
        P0, P1, P2, P3 = sg[1:]; ks = []
        for k in range(m + 1):
            t = k/m; v = 1 - t
            d1 = [3*v*v*(P1[j] - P0[j]) + 6*v*t*(P2[j] - P1[j]) + 3*t*t*(P3[j] - P2[j]) for j in (0, 1)]
            d2 = [6*v*(P2[j] - 2*P1[j] + P0[j]) + 6*t*(P3[j] - 2*P2[j] + P1[j]) for j in (0, 1)]
            sp = math.hypot(*d1)
            if sp < 1e-9: return None
            ks.append((d1[0]*d2[1] - d1[1]*d2[0])/sp**3)
        return ks
    def flip(sg):
        ks = kap(sg); return ks is not None and min(ks)*max(ks) < 0
    def straightish(sg):                                          # đoạn cong gần thẳng (độ cong × dây cung < 0.02): dấu độ cong
        ks = kap(sg); c = math.dist(sg[1], sg[4])                # dao động vì làm tròn — không phải gợn
        return ks is None or max(abs(k) for k in ks)*c < 0.02
    for i in range(n):
        if R[i][0] != 'C' or flip(segs[i]) or not flip(R[i]) or straightish(segs[i]): continue
        free = [k for k, fixed in ((2, smooth[(i - 1) % n]), (3, smooth[i])) if not fixed]   # tay ở nút liền: không đụng
        if not free: continue
        bb = None
        for k in free:
            for ddx in (-2, -1, 0, 1, 2):
                for ddy in (-2, -1, 0, 1, 2):
                    c_ = [list(q) if isinstance(q, tuple) else q for q in R[i]]; c_ = [R[i][0]] + list(R[i][1:])
                    c_[k] = (R[i][k][0] + ddx, R[i][k][1] + ddy)
                    if not flip(c_) and (bb is None or abs(ddx) + abs(ddy) < bb[0]): bb = (abs(ddx) + abs(ddy), c_)
        if bb: R[i] = bb[1]
    return R

def draw(glyph, cs, dx, ang):
    pen = glyph.getPen()
    T = (lambda p: skew((p[0] + dx, p[1]), ang)) if ang else (lambda p: (p[0] + dx, p[1]))
    for c in cs:
        segs = []; cur = c[0][1]
        for s in c[1:]:
            if all(math.dist(q, cur) < 0.01 for q in s[1:]): continue      # đoạn suy biến (độ dài 0) — fontbakery 06/11, '2' Bold
            segs.append(['L', T(cur), T(s[1])] if s[0] == 'L' else ['C', T(cur), T(s[1]), T(s[2]), T(s[3])])
            cur = s[-1]
        if not segs: continue
        if math.dist(segs[-1][-1], segs[0][1]) > 1e-6:                 # cạnh khép NGẦM (closePath) → tường minh: nút đoạn cuối ↔
            segs.append(['L', segs[-1][-1], segs[0][1]])               # cạnh khép được làm liền như mọi nút (7: gãy 2.2°)
        segs = _snap_smooth(segs)                                  # cả Roman: cùng làm tròn → cùng số điểm (variable)
        pen.moveTo(segs[0][1])
        for sg in segs:
            if sg[0] == 'L': pen.lineTo(sg[2])
            else: pen.curveTo(sg[2], sg[3], sg[4])
        pen.closePath()

import ital_comp as IC
_STEM = {}
_PAIR = {}
from weights import TW
def _lerp_d(a, b, t):
    """nội suy hai chuỗi path cùng cấu trúc (None nếu khác)"""
    ta, tb = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', a), re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', b)
    if len(ta) != len(tb) or any((x in 'MLCZ') != (y in 'MLCZ') or (x in 'MLCZ' and x != y) for x, y in zip(ta, tb)): return None
    out = []
    for x, y in zip(ta, tb):
        out.append(x if x in 'MLCZ' else '%.3f' % (float(x) + (float(y) - float(x))*t))
    d = ''
    for tok in out: d += tok if tok in 'MLCZ' else (' ' if d and d[-1] not in 'MLCZ' else '') + tok
    return d
def pair_fix(fR, fB):
    """10/11 ("sửa luôn mấy chỗ gãy x ¥ còn lại"): Medium / SemiBold là NỘI SUY của hai master đã làm tròn số nguyên — mỗi master
    liền nhưng tỉ lệ tay nắm / cạnh lệch nhau sau làm tròn → bản nội suy gãy 2–2.4° (x, ¥). Ở mỗi nút liền (< 1.5° ở cả hai
    master), dò CẶP điểm nguyên cho tay nắm (tay ngắn hơn nếu hai bên đều cong) ở hai master (±2 u), chọn cặp có góc gãy lớn
    nhất tại t = 0, ⅓, ⅔, 1 nhỏ nhất (phạt nhẹ độ dời)"""
    def u_(a, b):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); return ((b[0] - a[0])/L, (b[1] - a[1])/L) if L > 1e-9 else None
    def ang(a, b):
        return 180.0 if not a or not b else math.degrees(math.acos(max(-1.0, min(1.0, a[0]*b[0] + a[1]*b[1]))))
    lerp = lambda a, b, t: (a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t)
    TS = (0.0, 1/3, 2/3, 1.0); nfix = 0
    for g in fR:
        if g.name not in fB: continue
        gb = fB[g.name]
        if len(g.contours) != len(gb.contours): continue
        for cR, cB in zip(g.contours, gb.contours):
            pR, pB = cR.points, cB.points; n = len(pR)
            if n != len(pB) or n < 3: continue
            for i in range(n):
                if pR[i].segmentType is None: continue
                a_, b_ = (i - 1) % n, (i + 1) % n
                # hai lân cận: (điểm trước, điểm sau) — tay nắm nếu off-curve, điểm neo nếu cạnh thẳng
                P = lambda pts, k: (pts[k].x, pts[k].y)
                kin = ang(u_(P(pR, a_), P(pR, i)), u_(P(pR, i), P(pR, b_)))
                kib = ang(u_(P(pB, a_), P(pB, i)), u_(P(pB, i), P(pB, b_)))
                if kin > 3.0 or kib > 3.0: continue                      # góc cố ý đều > 25°
                offa, offb = pR[a_].segmentType is None, pR[b_].segmentType is None
                if not (offa or offb): continue
                def worst(Ra, Rb, Ba, Bb):
                    m = 0.0
                    for t in TS:
                        A = lerp(Ra, Ba, t); X = lerp(P(pR, i), P(pB, i), t); Bq = lerp(Rb, Bb, t)
                        m = max(m, ang(u_(A, X), u_(X, Bq)))
                    return m
                base = worst(P(pR, a_), P(pR, b_), P(pB, a_), P(pB, b_))
                if base < 1.0: continue
                # tay nắm được dời: tay off-curve; hai bên đều off-curve → tay ngắn hơn (ở master Regular)
                if offa and offb:
                    mv = a_ if math.dist(P(pR, a_), P(pR, i)) < math.dist(P(pR, b_), P(pR, i)) else b_
                else: mv = a_ if offa else b_
                best = (base, 0, None)
                rng = (-2, -1, 0, 1, 2)
                for dxr in rng:
                    for dyr in rng:
                        for dxb in rng:
                            for dyb in rng:
                                hr = (pR[mv].x + dxr, pR[mv].y + dyr); hb = (pB[mv].x + dxb, pB[mv].y + dyb)
                                if mv == a_: w_ = worst(hr, P(pR, b_), hb, P(pB, b_))
                                else: w_ = worst(P(pR, a_), hr, P(pB, a_), hb)
                                cost = w_ + 0.15*(abs(dxr) + abs(dyr) + abs(dxb) + abs(dyb))
                                if cost < best[0] + 0.15*best[1] - 1e-6: best = (w_, abs(dxr) + abs(dyr) + abs(dxb) + abs(dyb), (hr, hb))
                if best[2]:
                    (pR[mv].x, pR[mv].y), (pB[mv].x, pB[mv].y) = best[2]; nfix += 1
    return nfix

def master(w, ang, FL, groups, kern):
    f = ufoLib2.Font()
    style = w + (' Italic' if ang else '') if w != 'Regular' or not ang else 'Italic'
    i = f.info
    i.familyName = FAMILY; i.styleName = style
    i.versionMajor, i.versionMinor = VERSION
    i.unitsPerEm = 1000; i.capHeight = 700; i.xHeight = int(SPc.XH)
    # S4 vertical metrics MỘT bộ cho cả family: typo = hhea (USE_TYPO_METRICS), dòng 1.2 em; usWin bao chồng dấu cao / thấp nhất
    i.ascender = 760; i.descender = -240
    i.openTypeOS2TypoAscender = i.openTypeHheaAscender = 960; i.openTypeOS2TypoDescender = i.openTypeHheaDescender = -240
    i.openTypeOS2TypoLineGap = i.openTypeHheaLineGap = 0
    i.openTypeOS2WinAscent = YMAX + 10; i.openTypeOS2WinDescent = -YMIN + 10
    i.italicAngle = -ang if ang else 0
    i.openTypeOS2WeightClass = WGHT[w]
    i.openTypeOS2VendorID = VENDOR
    i.copyright = 'Copyright 2026 Đìzai Studio'; i.openTypeNameDesigner = 'Đìzai Studio'   # designer 06/11: tên studio có dấu
    i.openTypeNameManufacturer = 'Đìzai Studio'
    i.postscriptUnderlinePosition = -120; i.postscriptUnderlineThickness = 40
    i.openTypeOS2Selection = [7]                                     # USE_TYPO_METRICS
    f.lib['public.glyphOrder'] = ['.notdef'] + [gname(c) for c in CHARS]
    g = f.newGlyph('.notdef'); g.width = 500
    pen = g.getPen()
    for r in ((50, 0, 450, 700), (100, 50, 400, 650)):
        x0, y0, x1, y1 = r
        pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)] if r[0] == 50 else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        pen.moveTo(pts[0]); [pen.lineTo(p) for p in pts[1:]]; pen.closePath()
    for c in CHARS:
        if c == '\xa0': continue                                   # U+00A0 trỏ về glyph space
        g = f.newGlyph(gname(c)); g.width = SP[w][c]['adv']
        g.unicodes = [ord(c)] + ([0x00A0] if c == ' ' else [])
        k = f'{c}-{w}'
        if k in O:
            d_ = O[k]
            if ang:                                                # S26: bù quang học trước khi nghiêng (ital_comp.py)
                if w not in _STEM: _STEM[w] = IC.stem_of(O[f'H-{w}'])
                d_ = None
                if f'{c}-Regular' in O and f'{c}-Bold' in O:      # S38: hai master bù CHUNG (nội suy liền); Medium / SemiBold Italic
                    if c not in _PAIR:                             # = nội suy hai master đã bù (khớp bản variable, liền độ cong)
                        for w2 in ('Regular', 'Bold'):
                            if w2 not in _STEM: _STEM[w2] = IC.stem_of(O[f'H-{w2}'])
                        _PAIR[c] = IC.compensate_pair(O[f'{c}-Regular'], O[f'{c}-Bold'], ang, _STEM['Regular'], _STEM['Bold'],
                                                      smooth=c != '@')   # @: góc cắt bụng cố ý (designer 10/11)
                    if w in ('Regular', 'Bold'): d_ = _PAIR[c][0 if w == 'Regular' else 1]
                    else: d_ = _lerp_d(*_PAIR[c], TW[w])
                if d_ is None: d_ = IC.compensate(O[k], ang, _STEM[w], smooth=c != '@')
            cs = parse(d_)
            for j in FL.get(c, []): cs[j] = reverse(cs[j])
            draw(g, cs, SP[w][c]['dx'], ang)
    f.lib['public.glyphOrder'] = [n for n in f.lib['public.glyphOrder'] if n in f]
    f.groups.update(groups)
    f.kerning.update(kern)
    f.features.text = features()
    if ang:
        i.openTypeHheaCaretSlopeRise = 1000; i.openTypeHheaCaretSlopeRun = round(1000*math.tan(math.radians(ang)))
    return f

def features():
    L = []
    for c in CHARS:
        d = unicodedata.normalize('NFD', c)
        if len(d) > 1 and all(x in SP['Regular'] for x in d):
            L.append('    sub ' + ' '.join(gname(x) for x in d) + ' by ' + gname(c) + ';')
    # i / j + dấu trên → ı ȷ (đã có chữ dựng sẵn cho tiếng Việt; dấu rời cho chữ khác)
    return 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n\nfeature ccmp {\n' + '\n'.join(sorted(L, key=lambda s: -s.count(' '))) + '\n} ccmp;\n'

def kerning_data():
    rc = {}; lc = {}
    for c in CHARS:
        if c in (' ', '\xa0') or SPc.kind(c) == 'mark': continue
        rc.setdefault(SPc.rclass(c), []).append(gname(c)); lc.setdefault(SPc.lclass(c), []).append(gname(c))
    rn = {k: 'public.kern1.R%03d' % i for i, k in enumerate(sorted(rc))}; ln = {k: 'public.kern2.L%03d' % i for i, k in enumerate(sorted(lc))}
    groups = {rn[k]: v for k, v in rc.items()}; groups.update({ln[k]: v for k, v in lc.items()})
    ks = {}
    for w in ('Regular', 'Bold'):
        K = KN[w]; d = {}
        for key, v in K['class'].items():
            for i_ in [i_ for i_, ch in enumerate(key) if ch == '|']:
                a, b = key[:i_], key[i_ + 1:]
                if a in rn and b in ln: d[(rn[a], ln[b])] = v; break
        ks[w] = d
    # ngoại lệ: hợp hai master, ghi tường minh ở cả hai
    exc = set(KN['Regular']['exc']) | set(KN['Bold']['exc'])
    for w in ('Regular', 'Bold'):
        K = KN[w]
        for key in exc:
            a, b = key[0], key[2:]
            if a not in SP[w] or b not in SP[w]: continue
            v = K['exc'].get(key)
            if v is None: v = K['class'].get(f'{SPc.rclass(a)}|{SPc.lclass(b)}', 0)
            ks[w][(gname(a), gname(b))] = v
    return groups, ks

def _ybounds():
    Y = [p[1] for d in O.values() for c in parse(d) for s in c for p in s[1:]]
    return math.ceil(max(Y)), math.floor(min(Y))

def main():
    global YMAX, YMIN
    YMAX, YMIN = _ybounds(); print('y lớn / nhỏ nhất', YMAX, YMIN)
    os.makedirs(BUILD, exist_ok=True); os.makedirs(FONTS, exist_ok=True)
    FL = {}
    for c in CHARS:
        if f'{c}-Regular' in O:
            fl = flips(parse(O[f'{c}-Regular']))
            if fl: FL[c] = fl
    print('đảo chiều contour:', sum(len(v) for v in FL.values()), 'contour ở', len(FL), 'glyph')
    groups, ks = kerning_data()
    print('kerning: nhóm', len(groups), '· cặp R / B', len(ks['Regular']), len(ks['Bold']))
    for ang, tag in ((0, ''), (ITALIC_ANGLE, '-Italic')):
        print('nguồn', tag or '-Roman', use('Italic' if tag else 'Roman'))
        FL = {}
        for c in CHARS:
            if f'{c}-Regular' in O:
                fl = flips(parse(O[f'{c}-Regular']))
                if fl: FL[c] = fl
        groups, ks = kerning_data()
        ds = DesignSpaceDocument()
        ax = AxisDescriptor(); ax.name = 'Weight'; ax.tag = 'wght'; ax.minimum, ax.default, ax.maximum = 400, 400, 700
        ds.addAxis(ax)
        MS = {w: master(w, ang, FL, groups, ks[w]) for w in ('Regular', 'Bold')}
        # 10/11: outline bản TĨNH Medium / SemiBold dựng thẳng từ toạ độ số thực cùng weight (qua _snap_smooth) — instance nội suy
        # từ hai master NGUYÊN rồi làm tròn lần nữa làm tay nắm ngắn lệch hướng: 110–170 nút gãy 2–11° (j Medium 11°)
        for w in ('Medium', 'SemiBold'):
            fm = master(w, ang, FL, groups, ks.get(w, ks['Regular'])); pm = os.path.join(BUILD, f'{PS}{tag}-{w}-snap.ufo')
            if os.path.exists(pm): shutil.rmtree(pm)
            fm.save(pm)
        print('nút liền khi nội suy (đặt cặp tay nắm nguyên):', pair_fix(MS['Regular'], MS['Bold']))
        for w in ('Regular', 'Bold'):
            f = MS[w]; p = os.path.join(BUILD, f'{PS}{tag}-{w}.ufo')
            if os.path.exists(p): shutil.rmtree(p)
            f.save(p)
            s = SourceDescriptor(); s.path = p; s.location = {'Weight': WGHT[w]}; s.familyName = FAMILY
            s.styleName = f.info.styleName; ds.addSource(s)
        for w in WGHT:
            ins = InstanceDescriptor(); ins.familyName = FAMILY
            ins.styleName = (w + ' Italic' if w != 'Regular' else 'Italic') if ang else w
            ins.location = {'Weight': WGHT[w]}; ins.postScriptFontName = f'{PS}-' + (w + 'Italic' if ang and w != 'Regular' else ('Italic' if ang else w))
            ins.styleMapFamilyName = FAMILY if w in ('Regular', 'Bold') else f'{FAMILY} {w}'
            ins.styleMapStyleName = ({'Regular': 'regular', 'Bold': 'bold'}.get(w, 'regular') if not ang else
                                     {'Regular': 'italic', 'Bold': 'bold italic'}.get(w, 'italic'))
            ds.addInstance(ins)
        dsp = os.path.join(BUILD, f'{PS}{tag}.designspace'); ds.write(dsp)
        print('designspace', dsp)

def stat_static(path, italic):
    """STAT bản tĩnh: mỗi trục đúng MỘT giá trị (weight của chính file, ital 0 / 1)"""
    from fontTools.ttLib import TTFont
    from fontTools.otlLib.builder import buildStatTable
    f = TTFont(path); wc = f['OS/2'].usWeightClass; n = {v: k for k, v in WGHT.items()}.get(wc, 'Regular')
    wv = [dict(value=wc, name=n, flags=0x2 if wc == 400 else 0)]
    if wc == 400: wv[0]['linkedValue'] = 700
    iv = [dict(value=1, name='Italic')] if italic else [dict(value=0, name='Roman', flags=0x2, linkedValue=1)]
    buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='ital', name='Italic', values=iv)])
    f.save(path)

def stat(path, italic):
    """STAT: trục wght (Regular elidable, liên kết Bold) + trục ital (Roman elidable liên kết Italic) để app ghép Roman / Italic"""
    from fontTools.ttLib import TTFont
    from fontTools.otlLib.builder import buildStatTable
    f = TTFont(path)
    wv = [dict(value=v, name=n) for n, v in WGHT.items()]
    wv[0].update(flags=0x2, linkedValue=700)
    iv = [dict(value=1, name='Italic')] if italic else [dict(value=0, name='Roman', flags=0x2, linkedValue=1)]
    buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='ital', name='Italic', values=iv)])
    f.save(path)

def combined(VF):
    ds = DesignSpaceDocument()
    for name, tag, lo, df, hi in (('Weight', 'wght', 400, 400, 700), ('Slant', 'slnt', -ITALIC_ANGLE, 0, 0)):
        ax = AxisDescriptor(); ax.name, ax.tag, ax.minimum, ax.default, ax.maximum = name, tag, lo, df, hi; ds.addAxis(ax)
    for w in ('Regular', 'Bold'):
        for it in (False, True):
            s_ = SourceDescriptor(); s_.path = os.path.join(BUILD, f'{PS}{"-Italic" if it else ""}-{w}.ufo')
            s_.location = {'Weight': WGHT[w], 'Slant': -ITALIC_ANGLE if it else 0}; s_.familyName = FAMILY
            s_.styleName = (('Italic' if w == 'Regular' else f'{w} Italic') if it else w); ds.addSource(s_)
    for it in (False, True):
        for w in WGHT:
            ins = InstanceDescriptor(); ins.familyName = FAMILY
            ins.styleName = (('Italic' if w == 'Regular' else f'{w} Italic') if it else w)
            ins.location = {'Weight': WGHT[w], 'Slant': -ITALIC_ANGLE if it else 0}
            ins.postScriptFontName = f'{PS}-' + ((('Italic' if w == 'Regular' else w + 'Italic')) if it else w)
            ds.addInstance(ins)
    dsp = os.path.join(BUILD, f'{PS}-Combined.designspace'); ds.write(dsp)
    before = set(os.listdir(VF))
    subprocess.run(['fontmake', '-m', dsp, '-o', 'variable', '--output-dir', VF, '--flatten-components'], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    new = [f_ for f_ in os.listdir(VF) if f_ not in before][0]
    dst = os.path.join(VF, f'{PS}[slnt,wght].ttf'); os.replace(os.path.join(VF, new), dst)
    from fontTools.ttLib import TTFont
    from fontTools.otlLib.builder import buildStatTable
    f = TTFont(dst)
    wv = [dict(value=v, name=n) for n, v in WGHT.items()]; wv[0].update(flags=0x2, linkedValue=700)
    sv = [dict(value=0, name='Upright', flags=0x2), dict(value=-ITALIC_ANGLE, name='Italic')]
    buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='slnt', name='Slant', values=sv)])
    # tên PostScript riêng cho file gộp (kiểm tính unique 06/11: trùng 'AnNam-Regular' với AnNam[wght].ttf → macOS coi là một font)
    nm = f['name']
    for rec in list(nm.names):
        if rec.nameID == 6: rec.string = rec.toUnicode().replace(PS + '-', PS + 'Slnt-')
    nm.setName(PS + 'Slnt', 25, 3, 1, 0x409)
    for inst in f['fvar'].instances:
        if inst.postscriptNameID != 0xFFFF:
            r = nm.getName(inst.postscriptNameID, 3, 1, 0x409)
            if r: nm.setName(r.toUnicode().replace(PS + '-', PS + 'Slnt-'), inst.postscriptNameID, 3, 1, 0x409)
    f.save(dst)

def compile_fonts():
    VF = os.path.join(FONTS, 'variable')
    for d in ('variable', 'otf', 'ttf', 'woff2'): shutil.rmtree(os.path.join(FONTS, d), ignore_errors=True)
    for tag in ('', '-Italic'):
        dsp = os.path.join(BUILD, f'{PS}{tag}.designspace')
        subprocess.run(['fontmake', '-m', dsp, '-o', 'variable', '--output-dir', VF, '--flatten-components'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        dst = os.path.join(VF, f'{PS}{tag}[wght].ttf'); os.replace(os.path.join(VF, f'{PS}{tag}-VF.ttf'), dst); stat(dst, bool(tag))
        INST = os.path.join(BUILD, f'inst{tag}'); shutil.rmtree(INST, ignore_errors=True)
        subprocess.run(['fontmake', '-m', dsp, '-i', '-o', 'ufo', '--output-dir', INST], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for u_ in sorted(os.listdir(INST)):
            if not u_.endswith('.ufo'): continue
            up = os.path.join(INST, u_); fi = ufoLib2.Font.open(up)
            w = next((x for x in ('SemiBold', 'Medium') if x in (fi.info.styleName or '')), None)
            if w:
                fs = ufoLib2.Font.open(os.path.join(BUILD, f'{PS}{tag}-{w}-snap.ufo'))
                for g in fi:
                    if g.name in fs and len(fs[g.name].contours) == len(g.contours) and not g.components:
                        g.clearContours(); fs[g.name].drawPoints(g.getPointPen())
                fi.save(up, overwrite=True)
            for fmt in ('otf', 'ttf'):
                subprocess.run(['fontmake', '-u', up, '-o', fmt, '--output-dir', os.path.join(FONTS, fmt), '--flatten-components'],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # file gộp Roman + Italic (designer 06/11 "italic không kết hợp trong variable luôn được hả"): trục wght 400–700 + slnt 0 … −10°
    # — Italic = Roman nghiêng 10° nên nghiêng là một trục liên tục, 4 master (R / B × đứng / nghiêng) cùng cấu trúc
    combined(VF)
    from fontTools.ttLib import TTFont
    for fmt in ('otf', 'ttf'):                                         # tên file = tên PostScript (DizaiSerif-SemiBoldItalic.otf)
        for f_ in os.listdir(os.path.join(FONTS, fmt)):
            p = os.path.join(FONTS, fmt, f_); ps = TTFont(p)['name'].getDebugName(6); q = os.path.join(FONTS, fmt, f'{ps}.{fmt}')
            os.replace(p, q); stat_static(q, 'Italic' in ps)                    # STAT cho cả bản tĩnh (ghép Roman ↔ Italic)
    # chuẩn hoá file (fontbakery 06/11): TTF có 'prep' bật smart dropout control (nét mảnh không mất khi chữ rất nhỏ);
    # bỏ bảng tên Mac (platform 1) — chỉ giữ Windows
    from fontTools.ttLib.tables import ttProgram
    for dp, _, fs in os.walk(FONTS):
        for f_ in fs:
            p = os.path.join(dp, f_); t = TTFont(p)
            t['name'].names = [n for n in t['name'].names if n.platformID != 1]
            # mã định danh (name ID 3) riêng từng file: phiên bản; vendor; tên PostScript (+ '-VF' cho file variable)
            vend = t['OS/2'].achVendID.strip() or 'NONE'
            uid = f"{VERSION[0]}.{VERSION[1]:03d};{vend};{t['name'].getDebugName(6)}" + ('-VF' if 'fvar' in t else '')
            t['name'].setName(uid, 3, 3, 1, 0x409)
            LM.apply(t)                                               # name ID 13/14: giấy phép thương mại (tools/release/license_meta.py)
            if 'glyf' in t and 'gvar' not in t:                       # bỏ điểm trùng liên tiếp (làm tròn sau cu2qu → đoạn độ dài 0)
                from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
                for gn in t.getGlyphOrder():
                    g = t['glyf'][gn]
                    if g.numberOfContours <= 0: continue
                    co, fl, ends = list(g.coordinates), list(g.flags), g.endPtsOfContours
                    nco, nfl, nends, st = [], [], [], 0
                    for e in ends:
                        pts = list(range(st, e + 1)); keep = []
                        # hai điểm trùng: GIỮ điểm on-curve (bit 0 của flag). Bản cũ giữ điểm đầu → ở góc đuôi cắt S (cubic tay nắm 0
                        # → off-curve trùng góc) điểm góc bị bỏ, góc bo tròn trong TTF / woff2 tĩnh (designer 06/11 "đuôi cắt chữ S lỗi")
                        for i in pts:
                            if keep and co[i] == co[keep[-1]]:
                                if fl[i] & 1: keep[-1] = i
                                continue
                            keep.append(i)
                        if len(keep) > 1 and co[keep[-1]] == co[keep[0]]:
                            if fl[keep[-1]] & 1 and not fl[keep[0]] & 1: keep[0] = keep[-1]
                            keep.pop()
                        nco += [co[i] for i in keep]; nfl += [fl[i] for i in keep]; nends.append(len(nco) - 1); st = e + 1
                    if len(nco) != len(co):
                        g.coordinates = GlyphCoordinates(nco); g.flags = bytearray(nfl); g.endPtsOfContours = nends
            if 'glyf' in t:
                prog = ttProgram.Program(); prog.fromAssembly(['PUSHW[ ]', '511', 'SCANCTRL[ ]', 'PUSHB[ ]', '4', 'SCANTYPE[ ]'])
                if 'prep' not in t:
                    from fontTools.ttLib import newTable
                    t['prep'] = newTable('prep')
                t['prep'].program = prog
            t.save(p)
    # woff2 cho web (designer 06/11 "làm thêm file woff2 cho web luôn"): nén Brotli từ variable/*.ttf và ttf/*.ttf
    W2 = os.path.join(FONTS, 'woff2'); shutil.rmtree(W2, ignore_errors=True)
    for sub in ('variable', 'ttf'):
        os.makedirs(os.path.join(W2, sub), exist_ok=True)
        for f_ in sorted(os.listdir(os.path.join(FONTS, sub))):
            t = TTFont(os.path.join(FONTS, sub, f_)); t.flavor = 'woff2'; t.save(os.path.join(W2, sub, f_.rsplit('.', 1)[0] + '.woff2'))
    for dp, _, fs in os.walk(FONTS):
        for f_ in sorted(fs): print('  ', os.path.relpath(os.path.join(dp, f_), ROOT), os.path.getsize(os.path.join(dp, f_))//1024, 'KB')

if __name__ == '__main__':
    main()
    if '--no-compile' not in sys.argv: compile_fonts()
