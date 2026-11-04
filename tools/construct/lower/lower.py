#!/usr/bin/env python3
"""Chữ thường từ bản vẽ designer (src_lower.py, Figma 2112:126) → đơn vị font, Regular + Bold.
    python3 tools/construct/lower/lower.py   → lower/lower.json (make_ref.py gộp vào ref_glyphs.json)

Regular = đúng bản vẽ (designer 04/11: thân chữ thường 36 px = 102 u = V chữ hoa, "đồng bộ độ dày của các chữ thường với
chữ hoa"); chỉ chốt cực trị tròn vào đường vượt (x-height 495 + 8.4, baseline − 11.3) và dọn nút (tidy).

Bold = luật Bold của chữ hoa (docs/08), cùng số với chữ hoa:
  - mép ngoài giữ nguyên, mực nở vào phía lòng;
  - thân 102 → 139 (+37): mép phía lòng dời vào 37 u, loe phía lòng trượt theo (giữ hình);
  - vòng / bụng: lòng co đều 37 u mọi phía, kể cả chỗ mảnh (như O: "lòng co đều ~38 mỗi phía");
  - nét ngang mảnh (thanh e, vai a): +28 (40 → 68, như thanh / tay E H L).
"""
import sys, re, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'ref'))
import pathops
from src_lower import SHAPES, GLYPH, S, BASE
import vn_punct as V

XH, OV_T, OV_B = 495.0, 503.4, -11.3          # guide chữ thường (khung 2107:5 / 2112:126)
B_IN = 37.0                                    # Bold: thân và vòng dày thêm vào phía lòng (139 − 102)
B_H = 28.0                                     # Bold: nét ngang mảnh dày thêm (68 − 40)
TOK = r'[MLCZ]|-?[\d.]+(?:e-?\d+)?'

# ---------- khối (px cục bộ) ----------
def _map_pts(dstr, f):
    toks = re.findall(TOK, dstr); out = []; i = 0
    while i < len(toks):
        if toks[i] in 'MLCZ': out.append(toks[i]); i += 1; continue
        x, y = f(float(toks[i]), float(toks[i + 1])); out += [repr(x), repr(y)]; i += 2
    return ' '.join(out)

def _bold_px(key, dstr):
    dv, dh = B_IN/S, B_H/S
    if key == 'stem':                          # mép trái (x ≤ 8, cả loe) là phía lòng: dời ra ngoài thân
        return _map_pts(dstr, lambda x, y: (x - dv, y) if x <= 8.01 else (x, y))
    if key == 'a_stem':
        def f(x, y):
            if 84.9 <= x <= 93.01: x -= dv                                    # mép trong thân a (kèm loe trái chân)
            if (x, y) in ((14.5005, 38.2495), (0.0, 71.249)) or abs(y + 19.7501) < 1e-3: y += dh   # vai a dày xuống
            return x, y
        return _map_pts(dstr, f)
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
def _outer(p):
    best = max(p.contours, key=lambda c: abs(c.area)); out = pathops.Path(); out.addPath(best)
    return pathops.op(out, out, pathops.PathOp.UNION)
def _dil(p, d):
    st = pathops.Path(); st.addPath(p); st.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    st.convertConicsToQuads(); return V.U(p, st)
def ring_bold(p, mask=None):
    """vòng / bụng: mực nở đều B_IN vào lòng; mép ngoài (hình bao) giữ nguyên"""
    return V.I(_dil(p, B_IN), mask if mask is not None else _outer(p))

def e_bold(pcs):
    """e: vòm + bụng nở vào lòng B_IN (chỉ tới mép dưới thanh Bold, mép ngoài và mặt đầu cắt giữ); thanh nở đều hai phía +B_H"""
    ink = V.U(pcs['e_arch'], pcs['e_bowl']); bar = pcs['e_bar']; bx0, by0, bx1, by1 = bar.bounds
    bw = pcs['e_bowl']; x_cut = bw.bounds[2]
    y_tt = max(q[1] for _, ps in bw.segments for q in ps if abs(q[0] - x_cut) < 0.5)      # mặt trên đầu cắt
    cy = (by0 + by1)/2; hb = (by1 - by0) + B_H; yb = cy - hb/2                             # mép dưới thanh Bold
    x_in = bw.bounds[0] + 60
    mask = _outer(V.U(ink, bar, V.rect(x_in, y_tt, x_cut, yb)))
    grown = V.U(V.I(_dil(pcs['e_arch'], B_IN), V.I(mask, V.halfplane(yb))), V.I(_dil(pcs['e_bowl'], B_IN), mask))
    barB = V.xform(bar, lambda x, y: (x, cy + (y - cy)*hb/(by1 - by0)))
    fill = V.rect(bx1 - 40, yb, bx1, by0)       # đầu phải thanh (vát) lấp thẳng đứng tới mép ngoài phần thò dưới mặt nối
    return V.U(grown, barB, fill)

def raw(ch, weight):
    pcs = {k: piece(k, m, weight) for k, m in GLYPH[ch]}
    if weight == 'Bold':
        if ch == 'e': o = e_bold(pcs)
        elif ch == 'a': o = V.U(pcs['a_stem'], ring_bold(pcs['a_bowl']))
        else: o = V.U(pcs['stem'], ring_bold(pcs['bowl']))
        o = _q2c(o)
    else:
        o = V.U(*pcs.values())
    return V.move(o, -o.bounds[0], 0)

# ---------- chốt đường vượt ----------
def _extreme(path, top):
    """cực trị tròn (lấy mẫu trên đoạn cong) trong vùng chữ x: bỏ qua thân vươn lên ascender / xuống descender"""
    best = None; cur = None
    for v, ps in path.segments:
        if v in ('moveTo', 'lineTo'): cur = ps[0]
        elif v == 'curveTo':
            c = (cur, *ps)
            for k in range(41):
                q = V.bez(c, k/40)
                if not (-60 < q[1] < XH + 60): continue
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
        return abs(t[1] - OV_T) < 0.05 and (b[1] > -2 or abs(b[1] - OV_B) < 0.05)
    for _ in range(12):
        p = snap(p)
        if ok(p): break
    p = tidy(p, True)
    for _ in range(6):
        if ok(p): break
        p = snap(p)
    return p

CHARS = 'aedbqp'
if __name__ == '__main__':
    out = {}
    for c in CHARS:
        for w in ('Regular', 'Bold'):
            out[f'{c}-{w}'] = [V.to_d(clean(raw(c, w)))]
    json.dump(out, open(os.path.join(HERE, 'lower.json'), 'w'))
    from make_ref import outline
    for k, v in out.items(): print(k, [round(x, 1) for x in outline(v).bounds])
