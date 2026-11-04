#!/usr/bin/env python3
"""Số Bold = bản vẽ của designer (Figma 2062:452: 1 3 2 5 6 9 7) + 0 4 8 suy ra từ Regular,
cân weight bằng offset đều đường viền (Tiller–Hanson, không boolean) tới mật độ mực mục tiêu
= mật độ Regular × (Bold/Regular của chữ A–T), rồi giãn về đúng khung mực; nắn liền tiếp tuyến (G1) ở các nút trơn.
    python3 tools/construct/ref/adjust_bold_fig.py
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
import pathops
from make_ref import outline
import diff
YMIN = {'0': -11.3, '1': 0, '3': -11.3, '2': 0, '5': -11.3, '6': -11.3, '9': -11.3, '7': 0}

def segs_of(p):
    """pathops → list contour; mỗi contour = list đoạn ('L', P0, P1) / ('C', P0, P1, P2, P3)"""
    out, cur, pos, start = [], [], None, None
    for v, ps in p.segments:
        if v == 'moveTo': cur = []; pos = start = ps[0]
        elif v == 'lineTo':
            if math.dist(pos, ps[0]) > 0.05: cur.append(['L', pos, ps[0]])
            pos = ps[0]
        elif v == 'curveTo': cur.append(['C', pos, ps[0], ps[1], ps[2]]); pos = ps[2]
        elif v == 'closePath':
            if math.dist(pos, start) > 0.05: cur.append(['L', pos, start])
            if cur: out.append(cur)
    return out

def to_path(cs):
    p = pathops.Path()
    for c in cs:
        p.moveTo(*c[0][1])
        for s in c:
            if s[0] == 'L': p.lineTo(*s[2])
            else: p.cubicTo(*s[2], *s[3], *s[4])
        p.close()
    return p

def legs(s):
    pts = s[1:]; out = []
    for a, b in zip(pts, pts[1:]):
        if math.dist(a, b) > 2.0: out.append((a, b))   # tay nắm quá ngắn (< 2u) không cho hướng tin cậy
    if not out and math.dist(pts[0], pts[-1]) > 1e-3: out.append((pts[0], pts[-1]))
    return out

FIX = {'xs': (), 'ys': (0, 700, -11.3, 711.3, 702.8, 708.5)}
def off_line(a, b, d, fixed=True):
    # cạnh nằm trên đường kẻ (baseline, cap, overshoot): giữ nguyên; mặt cắt ở mép trái/phải ô chữ: chỉ khi là cạnh THẲNG (fixed)
    if abs(a[1] - b[1]) < 2 and any(abs(a[1] - m) < 2 and abs(b[1] - m) < 2 for m in FIX['ys']): d = 0
    if fixed and abs(a[0] - b[0]) < 0.6 and any(abs(a[0] - m) < 0.6 for m in FIX['xs']): d = 0
    L = math.dist(a, b); n = ((b[1] - a[1]) / L, -(b[0] - a[0]) / L)   # bên phải hướng đi = phía ngoài mực (contour ngoài ngược chiều kim đồng hồ)
    return (a[0] + n[0] * d, a[1] + n[1] * d), (b[0] + n[0] * d, b[1] + n[1] * d)

def inter(l1, l2):
    (p, q), (r, s) = l1, l2
    d1 = (q[0] - p[0], q[1] - p[1]); d2 = (s[0] - r[0], s[1] - r[1]); den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-6 * math.hypot(*d1) * math.hypot(*d2): return None
    t = ((r[0] - p[0]) * d2[1] - (r[1] - p[1]) * d2[0]) / den
    return (p[0] + d1[0] * t, p[1] + d1[1] * t)

def offset_contour(c, d):
    """Tiller–Hanson: dời từng cạnh của đa giác điều khiển, lấy giao điểm cạnh kề"""
    n = len(c); new = []
    for i, s in enumerate(c):
        L = legs(s)
        if not L: new.append(s); continue
        OL = [off_line(a, b, d, s[0] == 'L') for a, b in L]
        prevL = legs(c[i - 1]); pl = off_line(*prevL[-1], d, c[i - 1][0] == 'L') if prevL else OL[0]
        p0 = inter(pl, OL[0]) or OL[0][0]
        if math.dist(p0, s[1]) > 4 * abs(d) + 1: p0 = OL[0][0]   # góc rất nhọn: giữ điểm dời thẳng
        if s[0] == 'L':
            nxt = legs(c[(i + 1) % n]); nl = off_line(*nxt[0], d, c[(i + 1) % n][0] == 'L') if nxt else OL[0]
            p1 = inter(OL[0], nl) or OL[0][1]
            if math.dist(p1, s[2]) > 4 * abs(d) + 1: p1 = OL[0][1]
            new.append(['L', p0, p1])
        else:
            P = [s[1], s[2], s[3], s[4]]; Q = [p0]
            # điểm điều khiển: dời theo pháp tuyến của cạnh tương ứng (giữ hướng tay nắm)
            k = 0
            for j in (1, 2):
                a, b = P[j - 1], P[j]
                if math.dist(a, b) > 2.0: la = off_line(a, b, d, False)
                else: la = off_line(P[j], P[j + 1], d, False) if math.dist(P[j], P[j + 1]) > 2.0 else off_line(P[0], P[3], d, False)
                ix = None
                nb = P[j + 1]
                if math.dist(P[j], nb) > 2.0 and math.dist(a, b) > 2.0: ix = inter(la, off_line(P[j], nb, d, False))
                Q.append(ix if ix and math.dist(ix, P[j]) < 6 * abs(d) + 2 else (P[j][0] + (la[0][0] - a[0]), P[j][1] + (la[0][1] - a[1])))
            nxt = legs(c[(i + 1) % n]); nl = off_line(*nxt[0], d, c[(i + 1) % n][0] == 'L') if nxt else OL[-1]
            p3 = inter(OL[-1], nl) or OL[-1][1]
            if math.dist(p3, s[4]) > 4 * abs(d) + 1: p3 = OL[-1][1]
            Q.append(p3); new.append(['C'] + Q)
    for i in range(n):  # nối liền điểm đầu/cuối các đoạn kề
        a = new[i - 1]; b = new[i]; e = a[-1]; f = b[1]; m = ((e[0] + f[0]) / 2, (e[1] + f[1]) / 2)
        a[-1] = m; b[1] = m
    return new

def g1(c, maxdeg=8):
    """nút trơn (lệch tiếp tuyến < maxdeg): gióng hai tay nắm thẳng hàng"""
    n = len(c)
    for i in range(n):
        a, b = c[i - 1], c[(i) % n]
        if a[0] != 'C' and b[0] != 'C': continue
        P = b[1]
        tin = (P[0] - a[-2][0], P[1] - a[-2][1]) if a[0] == 'C' else (P[0] - a[1][0], P[1] - a[1][1])
        tout = (b[2][0] - P[0], b[2][1] - P[1]) if b[0] == 'C' else (b[2][0] - P[0], b[2][1] - P[1])
        Li, Lo = math.hypot(*tin), math.hypot(*tout)
        if Li < 1e-3 or Lo < 1e-3: continue
        ang = math.degrees(math.acos(max(-1, min(1, (tin[0] * tout[0] + tin[1] * tout[1]) / Li / Lo))))
        if 0.05 < ang < maxdeg:
            if a[0] == 'L': u = (tin[0] / Li, tin[1] / Li)
            elif b[0] == 'L': u = (tout[0] / Lo, tout[1] / Lo)
            else: u = ((tin[0] / Li + tout[0] / Lo), (tin[1] / Li + tout[1] / Lo)); L = math.hypot(*u); u = (u[0] / L, u[1] / L)
            if a[0] == 'C': a[-2] = (P[0] - u[0] * Li, P[1] - u[1] * Li)
            if b[0] == 'C': b[2] = (P[0] + u[0] * Lo, P[1] + u[1] * Lo)
    return c

def bbox(cs):
    """khung theo đường cong thật (lấy mẫu), không theo điểm điều khiển"""
    xs, ys = [], []
    for c in cs:
        for s in c:
            if s[0] == 'L': pts = [s[1], s[2]]
            else:
                P = s[1:]; pts = []
                for i in range(21):
                    t = i / 20; u = 1 - t
                    pts.append(tuple(u**3*P[0][k] + 3*u*u*t*P[1][k] + 3*u*t*t*P[2][k] + t**3*P[3][k] for k in (0, 1)))
            xs += [p[0] for p in pts]; ys += [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

SNAPY = [0, 700, -11.3, 711.3]
def tidy(c):
    """nắn cạnh gần đứng / gần ngang cho thẳng tuyệt đối, bám đường kẻ, bỏ đoạn rỗng"""
    sy = lambda y: next((v for v in SNAPY if abs(y - v) < 1.5), y)
    for s in c:
        for k in range(1, len(s)):
            p = s[k]; s[k] = (p[0], sy(p[1])) if (k == 1 or k == len(s) - 1) else p
    for s in c:
        if s[0] != 'L': continue
        (x0, y0), (x1, y1) = s[1], s[2]
        if abs(x1 - x0) < 2.5 and abs(y1 - y0) > 15: x = round((x0 + x1) / 2, 1); s[1] = (x, y0); s[2] = (x, y1)
        elif abs(y1 - y0) < 2.5 and abs(x1 - x0) > 15: y = sy((y0 + y1) / 2); s[1] = (x0, y); s[2] = (x1, y)
    n = len(c)
    for i in range(n):   # đồng bộ điểm nối sau khi nắn (ưu tiên điểm của đoạn thẳng)
        a, b = c[i - 1], c[i]
        if b[0] == 'L': a[-1] = b[1]
        else: b[1] = a[-1]
    out = []
    for s in c:
        if s[0] == 'L' and math.dist(s[1], s[2]) < 0.6: continue
        if s[0] == 'C' and math.dist(s[1], s[4]) < 8 and max(math.dist(s[1], s[2]), math.dist(s[4], s[3])) < 1.5: s = ['L', s[1], s[4]]   # cung tí hon → thẳng
        if s[0] == 'C' and any(all(abs(p[1] - m) < 1.5 for p in s[1:]) for m in SNAPY): s = ['L', (s[1][0], sy(s[1][1])), (s[4][0], sy(s[4][1]))]   # cung gần trùng đường kẻ → thẳng trên đường kẻ
        out.append(s)
    for i in range(len(out)): out[i][1] = out[i - 1][-1]
    return out

def fit_box(cs, box):
    bx = bbox(cs); sx = (box[2] - box[0]) / (bx[2] - bx[0]); sy = (box[3] - box[1]) / (bx[3] - bx[1])
    return [[[s[0]] + [(box[0] + (p[0] - bx[0]) * sx, box[1] + (p[1] - bx[1]) * sy) for p in s[1:]] for s in c] for c in cs]

def dens(p):
    A = diff.raster(p); xs = A.any(0).nonzero()[0]; return A.sum() / ((xs.max() - xs.min() + 80) * 700)

def shift(p, dy):
    cs = segs_of(p); return to_path([[[s[0]] + [(q[0], q[1] + dy) for q in s[1:]] for s in c] for c in cs])

def d_of(cs):
    out = ''
    for c in cs:
        out += 'M%.1f %.1f' % c[0][1]
        for s in c:
            out += ('L%.1f %.1f' % s[2]) if s[0] == 'L' else ('C%.1f %.1f %.1f %.1f %.1f %.1f' % (*s[2], *s[3], *s[4]))
        out += 'Z'
    return out

if __name__ == '__main__':
    A = json.load(open(os.path.join(HERE, 'designer_A.json'))); B = json.load(open(os.path.join(HERE, 'designer_B.json')))
    raw = json.load(open(os.path.join(HERE, 'designer_boldfig_raw.json')))
    L = lambda k: outline(A.get(k) or B.get(k))
    ratio = sum(dens(L(f'{c}-Bold')) for c in 'ABCDEFGHIJKLMNOPQRST') / sum(dens(L(f'{c}-Regular')) for c in 'ABCDEFGHIJKLMNOPQRST')
    def ell_contour(c, rx, ry, rot, hole=True, k=0.5523):
        ca, sa = math.cos(rot), math.sin(rot); T = lambda x, y: (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)
        P = [T(rx, 0), T(0, ry), T(-rx, 0), T(0, -ry)]
        H = [((T(rx, k * ry)), T(k * rx, ry)), (T(-k * rx, ry), T(-rx, k * ry)), (T(-rx, -k * ry), T(-k * rx, -ry)), (T(k * rx, -ry), T(rx, -k * ry))]
        segs = [['C', P[i], H[i][0], H[i][1], P[(i + 1) % 4]] for i in range(4)]
        if hole: segs = [['C', s_[4], s_[3], s_[2], s_[1]] for s_ in reversed(segs)]
        return segs
    # 0 và 8: vòng ngoài giữ nguyên của Regular; lòng = elip của Regular co lại (như O Bold: trục dài −34, trục ngắn −40) × hệ số f
    RG = json.load(open(os.path.join(HERE, '..', 'ref_glyphs.json')))
    def round_bold(ch):
        R = pathops.simplify(L(f'{ch}-Regular'), fix_winding=True); cs = segs_of(R)
        outer = max(cs, key=lambda c: (bbox([c])[2] - bbox([c])[0]) * (bbox([c])[3] - bbox([c])[1]))
        ells = [g for g in RG[f'{ch}-Regular']['guides'] if g['type'] in ('ellipse', 'circle')]
        if ch == '0': cnt = [g for g in ells if g['type'] == 'ellipse' and g['ry'] < 250]
        else: cnt = [{'c': g['c'], 'rx': g.get('rx', g.get('r')), 'ry': g.get('ry', g.get('r')), 'rot': g.get('rot', 0)} for g in ells
                     if (g['type'] == 'circle' and g['r'] > 100) or (g['type'] == 'ellipse' and g.get('rx', 0) < 200)]
        target = dens(L(f'{ch}-Regular')) * ratio; lo, hi = 0.0, 2.0
        for it in range(16):
            f = (lo + hi) / 2
            cs2 = [outer] + [ell_contour(g['c'], g['rx'] - 34.4 * f * g['rx'] / max(g['rx'], g['ry']), g['ry'] - 34.4 * f * g['ry'] / max(g['rx'], g['ry']), g['rot']) for g in cnt]
            if dens(to_path(cs2)) < target: lo = f
            else: hi = f
        print(ch, 'lòng co hệ số %.2f, %d lòng, mật độ %.3f (mục tiêu %.3f)' % (f, len(cnt), dens(to_path(cs2)), target))
        return cs2
    for ch in '0123456789':
        if ch in '08' and ch not in raw:   # chỉ khi chưa có bản vẽ
            cur = round_bold(ch); x0 = bbox(cur)[0]; cur = [[[s_[0]] + [(p[0] - x0, p[1]) for p in s_[1:]] for s_ in c] for c in cur]
            B[f'{ch}-Bold'] = [d_of(cur)]; continue
        if ch == '0' and ch in raw:   # 0 của designer: vòng ngoài giữ nguyên, lòng (elip) phóng/co quanh tâm tới mật độ mục tiêu
            cs = segs_of(pathops.simplify(shift(outline(raw[ch]), YMIN[ch]), fix_winding=True))
            big = max(cs, key=lambda c: (bbox([c])[2] - bbox([c])[0]))
            inner = [c for c in cs if c is not big][0]; ib = bbox([inner]); cx, cy = (ib[0] + ib[2]) / 2, (ib[1] + ib[3]) / 2
            target = dens(L('0-Regular')) * ratio; lo, hi = 0.9, 1.2
            for it in range(18):
                f = (lo + hi) / 2
                cur = [big, [[s_[0]] + [(cx + (p[0] - cx) * f, cy + (p[1] - cy) * f) for p in s_[1:]] for s_ in inner]]
                if dens(to_path(cur)) > target: lo = f
                else: hi = f
            x0 = bbox(cur)[0]; cur = [[[s_[0]] + [(p[0] - x0, p[1]) for p in s_[1:]] for s_ in c] for c in cur]
            B['0-Bold'] = [d_of(cur)]; print('0 lòng × %.3f, mật độ %.3f (mục tiêu %.3f)' % (f, dens(to_path(cur)), target)); continue
        if ch == '1':
            cs = segs_of(pathops.simplify(shift(outline(raw[ch]), YMIN[ch]), fix_winding=True)); B['1-Bold'] = [d_of([tidy(g1(c)) for c in cs])]; continue
        src = shift(outline(raw[ch]), YMIN[ch]) if ch in raw else L(f'{ch}-Bold')
        src = pathops.simplify(src, fix_winding=True); cs = segs_of(src); box = bbox(cs); FIX['xs'] = (box[0], box[2])
        target = dens(L(f'{ch}-Regular')) * ratio
        lo, hi = -15.0, 15.0
        for it in range(14):
            d = (lo + hi) / 2
            cur = fit_box([g1(offset_contour(c, d)) for c in cs], box)
            if dens(to_path(cur)) < target: lo = d
            else: hi = d
        d = (lo + hi) / 2; cur = [tidy(g1(c, 3)) for c in fit_box([g1(offset_contour(c, d)) for c in cs], box)]   # nắn lại sau khi giãn khung
        x0 = bbox(cur)[0]; cur = [[[s[0]] + [(p[0] - x0, p[1]) for p in s[1:]] for s in c] for c in cur]
        B[f'{ch}-Bold'] = [d_of(cur)]
        print(ch, 'offset %+.1f u  density %.3f → %.3f (target %.3f)' % (d, dens(src), dens(to_path(cur)), target))
    json.dump(B, open(os.path.join(HERE, 'designer_B.json'), 'w'), separators=(',', ':'))
