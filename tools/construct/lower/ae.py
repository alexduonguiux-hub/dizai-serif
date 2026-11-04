#!/usr/bin/env python3
"""a, e chữ thường: từ hình gốc của designer (src_ae.py, node 2107:5) → đơn vị font."""
import sys, re, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'ref'))
import pathops
from src_ae import PIECES, GLYPH, S, BASE
import vn_punct as V

# Luật S10 (rule book): nét chữ thường = 0.9 nét chữ hoa. Bản vẽ gốc dùng thân 102 (= V chữ hoa) nên a, e đậm hơn chữ hoa
# (mật độ mực a 0.445, e 0.411 so với H 0.387, D 0.365). Chỉnh trên chính khối dựng của designer (đơn vị px Figma):
STEM_IN = 102*0.1/S            # thân 102 → 92: mép trong dịch vào 10 u (mép ngoài giữ nguyên, như luật Bold đảo chiều)
COUNTER = 1.0                  # hệ số nở lòng (đặt bên dưới theo từng khối)
GROW = {'a_bowl': 1.12}   # lòng nở 12 %: thân 102 → 92 (S10), vòng 96 → 80–86
# e (vẽ lại 04/11): hai vách trái/phải 36 px = 102 u → 0.9 V; nét mảnh đỉnh vòm 48.5 u, đáy bụng 49.6 u → 40 u (như vai a).
# Chỉnh mép trong (lòng) của vòm và bụng; mép ngoài, thanh ngang và đầu cắt của designer giữ nguyên.
# Bold (docs/08): mép ngoài giữ nguyên, nét dày vào lòng; chữ thường giữ cùng tỉ lệ với chữ hoa như ở Regular:
# vách 0.9 V (Bold 0.9 × 139 = 125), nét mảnh = H (Bold 68), thanh ngang = H nở đều hai phía (39.6 → 68),
# đầu cắt dày vào lòng +28 (như tay dưới E/L Bold 40 → 68). Đơn vị px Figma.
EW = {'Regular': dict(wall=102*0.9/S, thin=40/S, bar=14.0, term=0.0),
      'Bold':    dict(wall=139*0.9/S, thin=68/S, bar=68/S, term=28/S)}
WEIGHT = 'Regular'
def _e_inner(key, x, y):
    E_WALL, E_THIN = EW[WEIGHT]['wall'], EW[WEIGHT]['thin']
    if key == 'e_bowl' and (x, y) in ((154.894, 50.4912), (143.437, 30.6786)):   # đầu cắt: mép trên dày lên
        return x, y + EW[WEIGHT]['term']
    if key == 'e_arch' and 35.9 <= x <= 136.1 and y >= 17:          # lòng vòm: tâm x 86, chân ở y 89
        kx = (50 + 36 - E_WALL)/50; ky = (89 - E_THIN)/(89 - 17.1562)
        return 86 + (x - 86)*kx, 89 - (89 - y)*ky
    if key == 'e_bowl' and 35.9 <= x <= 140 and y >= 17.5:          # lòng bụng: neo ở đầu cắt x 154.894, chân ở y 91
        kx = (154.894 - E_WALL)/(154.894 - 36); ky = (91 - E_THIN)/(91 - 17.542)
        return 154.894 - (154.894 - x)*kx, 91 - (91 - y)*ky
    return x, y

def _adjust(key, dstr):
    toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', dstr)
    if key == 'a_stem':
        # điểm thuộc mép trong của thân (x ≤ 93 trong khối gốc, kể cả loe chân trái và tay nắm đầu vòng vai) dịch +STEM_IN
        out = []; i = 0; xs = True
        while i < len(toks):
            t = toks[i]
            if t in 'MLCZ': out.append(t); i += 1; continue
            x, y = float(toks[i]), float(toks[i + 1])
            if 84.9 <= x <= 93.01 and (y > 50 or y < -20 or abs(x - 93) < 0.01): x += STEM_IN
            out += [repr(x), repr(y)]; i += 2
        return ' '.join(out)
    if key == 'e_bar' and False:
        k = EW[WEIGHT]['bar']/14
        return re.sub(r'(-?[\d.]+) (-?[\d.]+)', lambda m: f"{m.group(1)} {7 + (float(m.group(2)) - 7)*k!r}", dstr)
    if key == 'e_arch' and False:                        # chân vòm phải kéo xuống theo mép dưới thanh (thanh nở quá y 89)
        dd = (EW[WEIGHT]['bar'] - 14)/2
        dstr = dstr.replace('L172 89 L136 89', f'L172 {89 + dd!r} L136 {89 + dd!r}')
    if key in ('e_arch', 'e_bowl') and False:
        toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', dstr); out = []; i = 0
        while i < len(toks):
            if toks[i] in 'MLCZ': out.append(toks[i]); i += 1; continue
            x, y = _e_inner(key, float(toks[i]), float(toks[i + 1])); out += [repr(x), repr(y)]; i += 2
        return ' '.join(out)
    if key in GROW and GROW[key] != 1.0:
        # nở lòng (contour thứ hai) quanh tâm hộp của nó
        parts = dstr.split('M')[1:]; outer, inner = 'M' + parts[0], 'M' + parts[1]
        nums = [float(v) for v in re.findall(r'-?[\d.]+(?:e-?\d+)?', inner)]
        xs, ys = nums[0::2], nums[1::2]; cx, cy = (min(xs) + max(xs))/2, (min(ys) + max(ys))/2; k = GROW[key]
        it = iter(nums); new = []
        for t in re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', inner):
            if t in 'MLCZ': new.append(t)
        out = []; j = 0; tk = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', inner); q = 0
        while q < len(tk):
            if tk[q] in 'MLCZ': out.append(tk[q]); q += 1; continue
            x, y = float(tk[q]), float(tk[q + 1]); x, y = cx + (x - cx)*k, cy + (y - cy)*k
            out += [repr(x), repr(y)]; q += 2
        return outer + ' ' + ' '.join(out)
    return dstr

def piece(key):
    m, dstr = PIECES[key]; dstr = _adjust(key, dstr); a, b, c, d, e, f = m
    tr = lambda x, y: ((a*x + b*y + c)*S, (BASE - (d*x + e*y + f))*S)
    toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', dstr); p = pathops.Path(); i = 0
    while i < len(toks):
        cmd = toks[i]; i += 1; n = {'M': 1, 'L': 1, 'C': 3, 'Z': 0}[cmd]
        pts = [tr(float(toks[i + 2*j]), float(toks[i + 2*j + 1])) for j in range(n)]; i += 2*n
        if cmd == 'M': p.moveTo(*pts[0])
        elif cmd == 'L': p.lineTo(*pts[0])
        elif cmd == 'C': p.cubicTo(*pts[0], *pts[1], *pts[2])
        else: p.close()
    return pathops.op(p, p, pathops.PathOp.UNION)

def raw(ch):
    o = V.U(*[piece(k) for k in GLYPH[ch]]); return V.move(o, -o.bounds[0], 0)

# Guide chữ thường (đo trên khung 2107:5, cùng thang chữ hoa): x-height 495, vượt trên 8.4 → 503.4, vượt dưới −11.3
XH, OV_T, OV_B = 495.0, 503.4, -11.3

def _extreme(path, top):
    """điểm cực trị thật của đường cong (lấy mẫu): (x, y)"""
    best = None; cur = None
    for v, ps in path.segments:
        if v == 'moveTo': cur = ps[0]
        elif v == 'lineTo': cur = ps[0]
        elif v == 'curveTo':
            c = (cur, *ps)
            for k in range(41):
                q = V.bez(c, k/40)
                if best is None or (q[1] > best[1] if top else q[1] < best[1]): best = q
            cur = ps[2]
    return best

def snap(path):
    """uốn mềm cục bộ để cực trị trên/dưới nằm đúng đường vượt: điểm (cả tay nắm) dịch dy·wx·wy, trọng số giảm tuyến
    tính theo khoảng cách tới cực trị (ngang 170 u, dọc 140 u). Chân phẳng ở baseline / mặt cắt ở x-height không bị kéo."""
    moves = []
    for top in (True, False):
        e = _extreme(path, top)
        if e is None: continue
        target = OV_T if top else OV_B
        if not top and e[1] > -2: continue
        moves.append((e, target - e[1]))
    def f(x, y):
        for (ex, ey), dy in moves:
            if abs(y) < 0.6 or abs(y - XH) < 0.6: continue          # giữ nguyên đường thẳng trên baseline / x-height
            wx = max(0.0, 1 - abs(x - ex)/170); wy = max(0.0, 1 - abs(y - ey)/140)
            y += dy*wx*wy
        return (x, y)
    return V.xform(path, f)

def clean(ch):
    from tidy import tidy
    p = raw(ch)
    for _ in range(12):                                   # lặp tới khi cực trị nằm đúng đường vượt (sai số < 0.05 u)
        p = snap(p); t = _extreme(p, True)[1]; b = _extreme(p, False)[1]
        if abs(t - OV_T) < 0.05 and (b > -2 or abs(b - OV_B) < 0.05): break
    p = tidy(p, True)
    for _ in range(6):                                    # tidy nắn G1 có thể xê dịch cực trị: chốt lại lần cuối
        p = snap(p)
        if abs(_extreme(p, False)[1] - OV_B) < 0.05 or _extreme(p, False)[1] > -2: break
    return p

# e Bold (bản vẽ lại lần 2, lòng elip xoay): luật Bold docs/08 — mép ngoài giữ nguyên, mực nở vào lòng. Vòm + bụng nở đều
# E_BOLD_IN = 0.9 × (O Bold − O Regular mỗi phía ≈ 37) ≈ 33 u về phía lòng (giãn mực bằng nét tròn rồi cắt theo hình bao ngoài
# Regular, nên mép ngoài và mặt đầu cắt không đổi); thanh ngang nở đều hai phía 39.6 → 67.6 (+28 như thanh E/H Bold).
E_BOLD_IN, E_BAR_B = 33.0, 67.6
def _outer(p):
    cs = list(p.contours); best = max(cs, key=lambda c: abs(c.area)); out = pathops.Path(); out.addPath(best)
    return pathops.op(out, out, pathops.PathOp.UNION)
def _q2c(p):
    out = pathops.Path(); cur = None
    for v, ps in p.segments:
        if v == 'moveTo': out.moveTo(*ps[0]); cur = ps[0]
        elif v == 'lineTo': out.lineTo(*ps[0]); cur = ps[0]
        elif v == 'curveTo': out.cubicTo(*ps[0], *ps[1], *ps[2]); cur = ps[2]
        elif v == 'qCurveTo':
            pts = list(ps)
            ons = []                                      # TrueType: các điểm off liên tiếp có điểm on ẩn ở giữa
            for i in range(len(pts) - 1):
                a = pts[i]; b = pts[i + 1] if i + 1 < len(pts) - 1 else None
                end = ((a[0] + b[0])/2, (a[1] + b[1])/2) if b else pts[-1]
                c1 = (cur[0] + 2/3*(a[0] - cur[0]), cur[1] + 2/3*(a[1] - cur[1])); c2 = (end[0] + 2/3*(a[0] - end[0]), end[1] + 2/3*(a[1] - end[1]))
                out.cubicTo(*c1, *c2, *end); cur = end
        elif v == 'closePath': out.close()
    return out
def e_bold():
    pcs = {k: piece(k) for k in ('e_arch', 'e_bowl', 'e_bar')}
    allp = V.U(*pcs.values()); dx = -allp.bounds[0]; pcs = {k: V.move(v, dx, 0) for k, v in pcs.items()}
    ink = V.U(pcs['e_arch'], pcs['e_bowl']); bar = pcs['e_bar']; bx0, by0, bx1, by1 = bar.bounds
    bw = pcs['e_bowl']; x_cut = bw.bounds[2]
    y_tt = max(q[1] for _, ps in bw.segments for q in ps if abs(q[0] - x_cut) < 0.5)      # mặt trên đầu cắt
    d = E_BOLD_IN; cy = (by0 + by1)/2; yb = cy - E_BAR_B/2                                    # mép dưới thanh Bold
    # hình bao = mực + thanh + vùng mở giữa đầu cắt và thanh (chỉ phía trong, x từ 60, tới mép dưới thanh Bold): lòng được nở,
    # mép ngoài và mặt đầu cắt không; thanh Bold thêm vào sau nên không bị cắt
    mask = _outer(V.U(ink, bar, V.rect(60, y_tt, x_cut, yb)))
    def dil(p):
        st = pathops.Path(); st.addPath(p); st.stroke(2*d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        st.convertConicsToQuads(); return V.U(p, st)
    # vòm nở riêng và chỉ tới mép dưới thanh Bold: chân vách phải của vòm không thò xuống khoảng mở
    grown = V.U(V.I(dil(pcs['e_arch']), V.I(mask, V.halfplane(yb))), V.I(dil(pcs['e_bowl']), mask))
    barB = V.xform(bar, lambda x, y: (x, cy + (y - cy)*E_BAR_B/(by1 - by0)))
    # thanh Bold thò dưới mặt nối 251.7: đầu phải (vát 10 px) lấp thẳng đứng tới mép ngoài, không khấc ở góc phải
    fill = V.rect(bx1 - 40, yb, bx1, by0)
    return _q2c(V.U(grown, barB, fill))

def clean_path(p):
    from tidy import tidy
    for _ in range(12):
        p = snap(p); t = _extreme(p, True)[1]; b = _extreme(p, False)[1]
        if abs(t - OV_T) < 0.05 and (b > -2 or abs(b - OV_B) < 0.05): break
    p = tidy(p, True)
    for _ in range(6):
        p = snap(p)
        if abs(_extreme(p, False)[1] - OV_B) < 0.05 or _extreme(p, False)[1] > -2: break
    return p

BUILD = [('a', 'Regular'), ('e', 'Regular'), ('e', 'Bold')]
if __name__ == '__main__':
    raw_, out = {}, {}
    for c, w in BUILD:
        WEIGHT = w
        if (c, w) == ('e', 'Bold'):
            r = e_bold(); raw_[f'{c}-{w}'] = [V.to_d(r)]; out[f'{c}-{w}'] = [V.to_d(clean_path(r))]
        else:
            raw_[f'{c}-{w}'] = [V.to_d(raw(c))]; out[f'{c}-{w}'] = [V.to_d(clean(c))]
    json.dump(raw_, open(os.path.join(HERE, 'raw_ae.json'), 'w'))
    json.dump(out, open(os.path.join(HERE, 'lower_ae.json'), 'w'))
    from make_ref import outline
    print({k: [round(x, 1) for x in outline(v).bounds] for k, v in out.items()})
