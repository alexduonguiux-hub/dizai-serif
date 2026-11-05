#!/usr/bin/env python3
"""Chữ thường từ bản vẽ designer (src_lower.py, Figma 2112:126) → đơn vị font, Regular + Bold.
    python3 tools/construct/lower/lower.py   → lower/lower.json (make_ref.py gộp vào ref_glyphs.json)

Regular = đúng bản vẽ (designer 04/11: thân chữ thường 36 px = 102 u = V chữ hoa, "đồng bộ độ dày của các chữ thường với
chữ hoa"); chỉ chốt cực trị tròn vào đường vượt (x-height 495 + 8.4, baseline − 11.3) và dọn nút (tidy).

Bold = luật Bold của chữ hoa (docs/08), cùng số với chữ hoa:
  - mép ngoài giữ nguyên, mực nở vào phía lòng;
  - thân 102 → 139 (+37): mép phía lòng dời vào 37 u, loe phía lòng trượt theo (giữ hình);
  - vòng / bụng giãn ngang 40 u (e 36, như C G) như chữ hoa Bold rộng ra; thân trượt theo mép vòng, giữ hình;
  - lòng co đều 35 u mọi phía (cộng phần giãn: vách ~ +40, như O D Bold);
  - nét ngang mảnh (thanh e, vai a): +28 (40 → 68, như thanh / tay E H L).
"""
import sys, re, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'ref'))
import pathops
from src_lower import SHAPES, GLYPH, GLYPH_BOLD, S, BASE
import math
import vn_punct as V

XH, OV_T, OV_B = 495.0, 503.4, -11.3          # guide chữ thường (khung 2107:5 / 2112:126)
# Bold — rút từ MẪU a Bold của designer (2115:551), so với a Regular (2115:440):
B_STEM = 22.6                  # thân 102 → 124.5 (36 → 44 px): dày RA PHÍA NGOÀI; mép trong giữ khoảng chồng với vòng
B_WIDE = 11.3                  # vòng (mép ngoài) giãn ngang +11.3 quanh tâm (bụng a 130 → 134 px)
B_MAJ, B_MIN = 12.7, 12.7      # (tham chiếu) a: lòng 39 × 47 → 34.5 × 42.5 px = −12.7 u mỗi bán trục
B_K = 0.105                    # lòng co THEO TỈ LỆ bán trục −10.5 % (trung bình a: 11.5 % / 9.6 %): lòng lớn co nhiều hơn
# nét tròn Bold dày thêm đúng B_STEM như thân (designer 05/11: "kiểm tra lại độ dày các chữ còn lại"): co lòng 10.5 % chung
# cho mọi chữ làm lòng nhỏ co ít → o +17.6, g +13.4, a +13.5 (thân +22.6). Hệ số co lòng giải riêng để thành bụng xa thân
# (đo bằng đường tròn nội tiếp) = Regular + B_STEM: o 101.2 → 123.8, g 101.1 → 123.7, a 96.6 → 119.2
B_KG = {'o': 0.1396, 'g': 0.1955, 'a': 0.1929}
B_SHIFT = 9.9                  # lòng dời về phía thân 9.9 (a: lệch tâm 10 → 13.5 px)
B_BAR = 12.7                   # nét ngang mảnh (thanh e) dày thêm bằng phần lòng co
B_THIN = 6.4                   # nét nối / tai g: nở đều mỗi phía (= nửa phần trên)
B_JOIN = 5.0                   # chỗ nối tai / móc–thân (r t f j) Bold dày thêm ngoài B_BAR, cho bằng chỗ nối bụng–thân b d p q
TOK = r'[MLCZ]|-?[\d.]+(?:e-?\d+)?'

# ---------- khối (px cục bộ) ----------
def _map_pts(dstr, f):
    toks = re.findall(TOK, dstr); out = []; i = 0
    while i < len(toks):
        if toks[i] in 'MLCZ': out.append(toks[i]); i += 1; continue
        x, y = f(float(toks[i]), float(toks[i + 1])); out += [repr(x), repr(y)]; i += 2
    return ' '.join(out)

def _bold_px(key, dstr):
    if key == 'stem':                          # thân dày +B_STEM chia đều hai phía (mỗi mép 11.3, cả loe): Bold chỉ rộng thêm ½ phần nét
        h = B_STEM/2/S
        return _map_pts(dstr, lambda x, y: (x + h, y) if x >= 43.99 else ((x - h, y) if x <= 8.01 else (x, y)))
    return dstr

def piece(key, m, weight):
    dstr = SHAPES[key] if weight == 'Regular' else _bold_px(key, SHAPES[key])
    a, b, c, d, e, f = m
    tr = lambda x, y: ((a*x + b*y + c)*S, (BASE - (d*x + e*y + f))*S)
    toks = re.findall(TOK, dstr); p = pathops.Path(); i = 0
    while i < len(toks):
        cmd = toks[i]; i += 1; n = {'M': 1, 'L': 1, 'C': 3, 'Z': 0}[cmd]
        pts = [tr(float(toks[i + 2*j]), float(toks[i + 2*j + 1])) for j in range(n)]; i += 2*n
        if cmd == 'M': p.moveTo(*pts[0])
        elif cmd == 'L': p.lineTo(*pts[0])
        elif cmd == 'C': p.cubicTo(*pts[0], *pts[1], *pts[2])
        else: p.close()
    return pathops.op(p, p, pathops.PathOp.UNION)

# ---------- Bold: nở vào lòng ----------
def _q2c(p):
    out = pathops.Path(); cur = None
    for v, ps in p.segments:
        if v == 'moveTo': out.moveTo(*ps[0]); cur = ps[0]
        elif v == 'lineTo': out.lineTo(*ps[0]); cur = ps[0]
        elif v == 'curveTo': out.cubicTo(*ps[0], *ps[1], *ps[2]); cur = ps[2]
        elif v == 'qCurveTo':
            pts = list(ps)
            for i in range(len(pts) - 1):
                a = pts[i]; b = pts[i + 1] if i + 1 < len(pts) - 1 else None
                end = ((a[0] + b[0])/2, (a[1] + b[1])/2) if b else pts[-1]
                c1 = (cur[0] + 2/3*(a[0] - cur[0]), cur[1] + 2/3*(a[1] - cur[1])); c2 = (end[0] + 2/3*(a[0] - end[0]), end[1] + 2/3*(a[1] - end[1]))
                out.cubicTo(*c1, *c2, *end); cur = end
        elif v == 'closePath': out.close()
    return out
import numpy as np
def _dil(p, d):
    st = pathops.Path(); st.addPath(p); st.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    st.convertConicsToQuads(); return _q2c(V.U(p, st))
def _first_contour(dstr):
    return 'M' + dstr.split('M')[1]
def _ell_from_pts(pts):
    """elip qua điểm mẫu (bình phương tối thiểu, conic): → (tâm, M 2×2) với elip = tâm + M·(cos t, sin t)"""
    P = np.array(pts); x, y = P[:, 0], P[:, 1]
    A = np.column_stack([x*x, x*y, y*y, x, y]); sol = np.linalg.lstsq(A, np.ones(len(x)), rcond=None)[0]
    a, b, c, d, e = sol; Q = np.array([[a, b/2], [b/2, c]]); ctr = np.linalg.solve(2*Q, -np.array([d, e]))
    k = 1 + ctr @ Q @ ctr; w, V_ = np.linalg.eigh(Q/k)
    return ctr, V_ @ np.diag(1/np.sqrt(w))
def _ell_path(ctr, M, dmaj=0.0, dmin=0.0, shift=(0.0, 0.0), k=None):
    U, Sg, _ = np.linalg.svd(M); rot = math.degrees(math.atan2(U[1, 0], U[0, 0])); k = B_K if k is None else k
    return V.ellipse((ctr[0] + shift[0], ctr[1] + shift[1]), Sg[0]*(1 - k), Sg[1]*(1 - k), rot)
def _samples(p, n=12):
    pts = []; cur = None
    for v, ps in p.segments:
        if v in ('moveTo', 'lineTo'): cur = ps[-1]
        elif v == 'curveTo':
            c = (cur, *ps); pts += [V.bez(c, j/n) for j in range(n + 1)]; cur = ps[2]
    return pts
def _tr(m, weight='Regular'):
    a, b, c, d, e, f = m
    return lambda x, y: ((a*x + b*y + c)*S, (BASE - (d*x + e*y + f))*S)
def _path(dstr, m):
    tr = _tr(m); toks = re.findall(TOK, dstr); p = pathops.Path(); i = 0
    while i < len(toks):
        cmd = toks[i]; i += 1; n = {'M': 1, 'L': 1, 'C': 3, 'Z': 0}[cmd]
        pts = [tr(float(toks[i + 2*j]), float(toks[i + 2*j + 1])) for j in range(n)]; i += 2*n
        if cmd == 'M': p.moveTo(*pts[0])
        elif cmd == 'L': p.lineTo(*pts[0])
        elif cmd == 'C': p.cubicTo(*pts[0], *pts[1], *pts[2])
        else: p.close()
    return pathops.op(p, p, pathops.PathOp.UNION)
def _inner_pts(dstr, m, sel):
    """điểm mẫu trên cung lòng (các đoạn cong có điểm cuối thoả sel, toạ độ px cục bộ) → toạ độ font"""
    tr = _tr(m); toks = re.findall(TOK, dstr); i = 0; cur = None; pts = []
    while i < len(toks):
        cmd = toks[i]; i += 1; n = {'M': 1, 'L': 1, 'C': 3, 'Z': 0}[cmd]
        q = [(float(toks[i + 2*j]), float(toks[i + 2*j + 1])) for j in range(n)]; i += 2*n
        if cmd == 'C' and sel(cur) and sel(q[-1]):
            pts += [tr(*V.bez((cur, *q), j/16)) for j in range(17)]
        if n: cur = q[-1]
    return pts

def raw(ch, weight):
    spec = None   # GLYPH_BOLD (mẫu a Bold cũ, bụng đứng) không còn dùng: a Bold theo luật (bold())
    if spec:                                                   # bản vẽ Bold của designer
        o = V.U(*[_path(SHAPES[k], m) for k, m in spec]); return V.move(o, -o.bounds[0], 0)
    if weight == 'Regular':
        o = V.U(*[piece(k, m, weight) for k, m in GLYPH[ch]]); return V.move(o, -o.bounds[0], 0)
    o = _q2c(bold(ch)); return V.move(o, -o.bounds[0], 0)

def _stretch(ring_bounds):
    x0, _, x1, _ = ring_bounds; c = (x0 + x1)/2; k = (x1 - x0 + B_WIDE)/(x1 - x0)
    return c, k, (lambda x, y: (c + (x - c)*k, y))

def bold(ch):
    """Bold theo mẫu a: vòng giãn +B_WIDE; lòng (elip) co B_MAJ/B_MIN, dời về phía thân B_SHIFT; thân +B_STEM ra ngoài"""
    G = dict(GLYPH[ch])
    if ch == 'a':
        # a Bold (bản a 05/11 bụng xoay; mẫu a Bold cũ bụng đứng không còn khớp): cùng luật — thân + B_STEM ra phía ngoài (phải,
        # cả loe chân), vai dày xuống B_BAR (đầu cắt dày theo); bụng: mép ngoài giãn +B_WIDE, lòng elip co B_K, dời về thân B_SHIFT
        dS, dH = B_STEM/S, B_BAR/S
        def fs(x, y):
            if x >= 128.99: x += dS/2                                           # thân chia đều hai phía
            elif 84.9 <= x <= 93.01: x -= dS/2
            if (x, y) in ((14.5005, 24.2497), (0.0, 57.249)) or abs(y + 19.7501) < 1e-3: y += dH
            return x, y
        stem = _path(_map_pts(SHAPES['a_stem'], fs), G['a_stem'])
        bm = G['a_bowl']; outer = _path(_first_contour(SHAPES['a_bowl']), bm); c, k, st = _stretch(outer.bounds)
        cpts = [st(*q) for q in _samples(_path('M' + SHAPES['a_bowl'].split('M')[2], bm))]; ctr, M = _ell_from_pts(cpts)
        # lòng a KHÔNG dời về thân (designer 05/11, kiểm độ dày chỗ nối): bụng a nối thân ở đáy, dời B_SHIFT làm chỗ nối Bold
        # còn 76 < Regular 80; không dời → 90.6 (đo đứng sát thân), dày theo weight như b d p q
        bowl = V.D(V.xform(outer, st), _ell_path(ctr, M, shift=(0, 0), k=B_KG['a']))
        return V.U(bowl, V.move(stem, (k - 1)*(outer.bounds[2] - c), 0))
    if ch in 'dbqp':
        bm, sm = G['bowl'], G['stem']
        outer = _path(_first_contour(SHAPES['bowl']), bm); c, k, st = _stretch(outer.bounds)
        cpts = [st(*q) for q in _samples(_path('M' + SHAPES['bowl'].split('M')[2], bm))]
        ctr, M = _ell_from_pts(cpts)
        stem = piece('stem', sm, 'Bold'); sx = (stem.bounds[0] + stem.bounds[2])/2; side = 1 if sx > c else -1
        x0, _, x1, _ = outer.bounds; edge = x1 if side > 0 else x0
        bowl = V.D(V.xform(outer, st), _ell_path(ctr, M, B_MAJ, B_MIN, (side*B_SHIFT, 0)))
        return V.U(bowl, V.move(stem, (k - 1)*(edge - c), 0))
    if ch in 'rtfj':
        # r t (bản vẽ 05/11) và f j (dựng từ khối r t): thân + 8 px (B_STEM) RA PHÍA NGOÀI (r t f: trái; j: phải), loe phía đó
        # trượt theo; tai / móc / thanh dày vào trong + 4.5 px (B_BAR): mép trong tai, móc dời vào, đầu cắt dày theo; thanh dày xuống.
        # thân chia đều hai phía (mỗi mép h = ½ B_STEM, loe theo mép); tai / móc trượt theo mép trong; thanh dài thêm hai đầu
        dS, dH = B_STEM/S, B_BAR/S; h = dS/2; out = []
        # mép trong tai / móc dày thêm B_BAR + B_JOIN: chỗ nối tai–thân Bold dày như chỗ nối bụng–thân b d p q Bold (+15 so với
        # Regular; chỉ B_BAR thì r Bold nhẹ hơn 5–8 u — designer 05/11, kiểm độ dày chỗ nối)
        dJ = (B_BAR + B_JOIN)/S
        for key, m in GLYPH[ch]:
            d = SHAPES[key]
            if key in ('r_stem', 't_stem', 'f_stem', 'j_stem'):
                d = _map_pts(d, lambda x, y: (x - h, y) if x < 0.01 else ((x + h, y) if x > 35.99 else (x, y)))
            elif key == 'fl1': d = _map_pts(d, lambda x, y: (x + h, y) if x > 35.9 else ((x - h, y) if x < 0.01 else (x, y)))
            elif key == 'fl2': d = _map_pts(d, lambda x, y: (x - h, y) if x < 8.01 else ((x + h, y) if x > 43.9 else (x, y)))
            elif key == 'r_ear':
                inner = {(86.9834, 34.5068), (70.6928, 20.6864), (52.007, 16.6259), (37.7812, 25.9814), (28.0556, 32.3776),
                         (22.0545, 43.9654)}
                d = _map_pts(d, lambda x, y: (x + h, y + dJ) if (x, y) in inner else (x + h, y))
            elif key == 't_hook':
                inner = {(69.0, 34.5107), (56.2644, 20.6885), (49.2621, 16.5), (41.5, 20.9814), (33.8969, 27.3775), (36.0, 43.5)}
                def f(x, y):
                    if (x, y) in inner: return x + h, y + dJ
                    if x < 0.01: return x - h, y                                                        # mép ngoài theo thân
                    return x + h, y
                d = _map_pts(d, f)
            elif key == 't_bar': d = _map_pts(d, lambda x, y: (x - h if x < 0.01 else (x + h if x > 95.99 else x), y + dH if y > 13.9 else y))
            out.append(_path(d, m))
        return V.U(*out)
    if ch == 'c':
        # c: vách trái = thân Bold (36 → 36 + B_STEM); đỉnh/đáy và đầu cắt + B_BAR (nét mảnh); lòng vẫn cắt qua mặt cắt
        # (miệng c mở). Lòng Bold là elip đứng: mép trái ở x = 36 + B_STEM, cắt mặt cắt ở mép trong đầu cắt Bold.
        from src_lower import D_C_OUTER, C_CTR, C_R, C_CUT, C_TT
        m = G['c_shape']; tr = _tr(m); dS, dH = B_STEM/S, B_BAR/S
        ry = C_R[1] - dH; yt = C_TT + dH; dy = C_CTR[1] - yt; q = math.sqrt(1 - (dy/ry)**2)
        left = (C_CTR[0] - C_R[0]) + dS; rx = (C_CUT - left)/(1 + q); cx = left + rx
        outer = _path(D_C_OUTER, m); c0, k, st = _stretch(outer.bounds)
        ctr = tr(cx, C_CTR[1]); counter = V.ellipse(ctr, rx*S, ry*S)
        return V.xform(V.D(outer, counter), st)
    if ch == 'o':
        m = G['o_ring']; outer = _path(_first_contour(SHAPES['o_ring']), m); c, k, st = _stretch(outer.bounds)
        cpts = [st(*q) for q in _samples(_path('M' + SHAPES['o_ring'].split('M')[2], m))]; ctr, M = _ell_from_pts(cpts)
        return V.D(V.xform(outer, st), _ell_path(ctr, M, k=B_KG['o']))
    if ch == 'g':
        allp = V.U(*[_path(SHAPES[kk], m) for kk, m in GLYPH['g']]); c, k, st = _stretch(_path(_first_contour(SHAPES['g_bowl']), G['g_bowl']).bounds)
        out = []
        for kk in ('g_bowl', 'g_loop'):
            m = G[kk]; outer = _path(_first_contour(SHAPES[kk]), m)
            cpts = [st(*q) for q in _samples(_path('M' + SHAPES[kk].split('M')[2], m))]; ctr, M = _ell_from_pts(cpts)
            out.append(V.D(V.xform(outer, st), _ell_path(ctr, M, B_MAJ, B_MIN, k=B_KG['g'])))
        for kk in ('g_link', 'g_ear'):
            p = _path(SHAPES[kk], G[kk]); px = (p.bounds[0] + p.bounds[2])/2
            q = _dil(p, B_THIN)
            if kk == 'g_ear': q = _q2c(V.I(q, V.rect(-9999, -9999, p.bounds[2], 9999)))   # mặt cắt tai giữ phẳng
            out.append(V.move(q, (k - 1)*(px - c), 0))
        return V.U(*out)
    if ch == 'e':
        arch_m, bowl_m, bar_m = G['e_arch'], G['e_bowl'], G['e_bar']
        arch_o = _path("M86 0 C133.496 0 172 38.8865 172 86.8555 L172 90 L0 90 L0 86.8555 C0 38.8865 38.5035 0 86 0 Z", arch_m)
        bowl_o = _path("M88.5 0 C114.943 0 138.677 11.6383 154.894 30.0879 L154.894 91 L0 91 L0 88.8076 C0 39.7607 39.6228 0 88.5 0 Z", bowl_m)
        c, k, st = _stretch(V.U(arch_o, bowl_o).bounds)
        e1 = _ell_from_pts([st(*q) for q in _inner_pts(SHAPES['e_arch'], arch_m, lambda p: 30 < p[0] < 140 and p[1] < 90.5)])
        e2 = _ell_from_pts([st(*q) for q in _inner_pts(SHAPES['e_bowl'], bowl_m, lambda p: 32 < p[0] < 155 and 15 < p[1] < 91.5)])
        bar = V.xform(_path(SHAPES['e_bar'], bar_m), st); bx0, by0, bx1, by1 = bar.bounds; cy = (by0 + by1)/2; hb = by1 - by0 + B_BAR
        barB = V.xform(bar, lambda x, y: (x, cy + (y - cy)*hb/(by1 - by0)))
        arch = V.D(V.xform(arch_o, st), _ell_path(*e1, B_MAJ, B_MIN))
        # đầu cắt đuôi e (designer 05/11: "e bold đuôi móc cao và nhọn quá"): lòng co làm mép lòng cắt mặt cắt cao hơn và nhọn
        # hơn. Dời lòng bụng sang phải tới khi mặt cắt đuôi Bold = mặt cắt Regular + B_BAR (đầu cắt dày như nét mảnh).
        bo_st = V.xform(bowl_o, st); x_cut = bo_st.bounds[2]
        def cross(p):                                          # đáy lòng tại mặt cắt (mép trên đầu cắt)
            q = V.I(p, V.rect(x_cut - 0.6, -5000, x_cut - 0.4, 5000)); return q.bounds[1] if list(q.segments) else None
        ry_reg = cross(_ell_path(*e2, 0, 0)) if False else None
        reg_bowl = _path(SHAPES['e_bowl'], bowl_m); xr = reg_bowl.bounds[2]
        qr = V.I(reg_bowl, V.rect(xr - 0.6, -5000, xr - 0.4, 5000)); y_face_reg = qr.bounds[3]   # mép trên mặt cắt Regular
        target = y_face_reg + B_BAR
        # giữ mép TRÁI lòng bụng (khớp mép lòng mắt e ở đầu trái thanh — designer 05/11: "chỗ này e bold hơi kỳ"), chỉ giãn
        # lòng về bên phải (hệ số k quanh mép trái) tới khi mặt cắt đuôi = Regular + B_BAR
        cnt0 = _ell_path(*e2)
        # mép lòng bụng ngay dưới thanh trùng mép lòng mắt ngay trên thanh (không bậc ở đầu trái thanh)
        def xin(p, y):
            q = V.I(p, V.rect(-5000, y - 0.3, 5000, y + 0.3)); return q.bounds[0] if list(q.segments) else None
        cnt_a = _ell_path(*e1); xa = xin(cnt_a, cy + hb/2 + 1); xb = xin(cnt0, cy - hb/2 - 1)
        if xa is not None and xb is not None: cnt0 = V.move(cnt0, xa - xb, 0)
        xl = cnt0.bounds[0]
        def cnt(k): return V.xform(cnt0, lambda x, y: (xl + (x - xl)*k, y))
        lo, hi = 1.0, 1.6
        for _ in range(30):
            mid = (lo + hi)/2; yc = cross(cnt(mid))
            if yc is None or yc > target: lo = mid
            else: hi = mid
        bowl = V.D(bo_st, cnt(hi))
        # đầu phải thanh lấp thẳng đứng tới mép ngoài phần thò dưới mặt nối vòm–bụng
        fill = V.rect(bx1 - 40, cy - hb/2, bx1, by0)
        return V.U(arch, bowl, barB, fill)
    raise KeyError(ch)

# ---------- chốt đường vượt ----------
def _extreme(path, top):
    """cực trị tròn (lấy mẫu trên đoạn cong) trong vùng chữ x: bỏ qua thân vươn lên ascender / xuống descender"""
    best = None; cur = None
    for v, ps in path.segments:
        if v in ('moveTo', 'lineTo'): cur = ps[0]
        elif v == 'curveTo':
            c = (cur, *ps)
            for k in range(41):
                q = V.bez(c, k/40); dq = V.dbez(c, k/40)
                if not ((XH - 30 < q[1] < XH + 30) if top else (-30 < q[1] < 30)): continue   # chỉ cực trị sát đường vượt
                if abs(dq[1]) > 0.15*math.hypot(*dq): continue        # chỉ điểm tiếp tuyến ngang (đỉnh/đáy vòng thật)
                if best is None or (q[1] > best[1] if top else q[1] < best[1]): best = q
            cur = ps[2]
    return best

def snap(path):
    """uốn mềm cục bộ: cực trị tròn trên / dưới về đúng đường vượt; trọng số giảm tuyến tính (ngang 170 u, dọc 140 u).
    Đường thẳng trên baseline / x-height không bị kéo."""
    moves = []
    for top in (True, False):
        e = _extreme(path, top)
        if e is None or (not top and e[1] > -2): continue
        moves.append((e, (OV_T if top else OV_B) - e[1]))
    def f(x, y):
        for (ex, ey), dy in moves:
            if abs(y) < 0.6 or abs(y - XH) < 0.6: continue
            wx = max(0.0, 1 - abs(x - ex)/170); wy = max(0.0, 1 - abs(y - ey)/140)
            y += dy*wx*wy
        return (x, y)
    return V.xform(path, f)

def clean(p):
    from tidy import tidy
    def ok(p):
        t, b = _extreme(p, True), _extreme(p, False)
        return (t is None or abs(t[1] - OV_T) < 0.05) and (b is None or b[1] > -2 or abs(b[1] - OV_B) < 0.05)
    for _ in range(12):
        p = snap(p)
        if ok(p): break
    p = tidy(p, True)
    for _ in range(6):
        if ok(p): break
        p = snap(p)
    return p

CHARS = 'aedbqpgocrt'
if __name__ == '__main__':
    out = {}
    for c in CHARS:
        for w in ('Regular', 'Bold'):
            out[f'{c}-{w}'] = [V.to_d(clean(raw(c, w)))]
    json.dump(out, open(os.path.join(HERE, 'lower.json'), 'w'))
    from make_ref import outline
    for k, v in out.items(): print(k, [round(x, 1) for x in outline(v).bounds])
