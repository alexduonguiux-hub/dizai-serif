#!/usr/bin/env python3
"""Italic I2 — italic thật (designer 06/11: "làm italic thật I2").
    python3 tools/construct/italic.py        (sau build.py của Roman)  → out/construct_italic/outlines.json
    DIZAI_OUT=out/construct_italic python3 tools/construct/compat_masters.py && … spacing.py …

Dựng thiết kế italic ĐỨNG (chưa nghiêng) từ outline Roman của hai master Regular / Bold; nghiêng 10° áp lúc xuất font
(export_font.py) quanh ½ x-height — mọi glyph nghiêng như nhau nên khe giữa hai chữ giữ nguyên, spacing / kerning tính trên
bản đứng là đúng cho bản nghiêng. Luật (docs/14-italic.md):
  I2.2  chữ thường hẹp ngang CONDENSE = 0.94 (nét đứng nhẹ theo — italic gọn và nhẹ hơn roman một bậc)
  I2.3  đuôi ra: chân phải của i ı l n m h u d = móc chân của t (cùng module, cùng bề dày thân)
  I2.4  a GIỮ HAI TẦNG như Roman (designer 06/11: "giữ a hai tầng như roman") — chỉ hẹp ngang + nghiêng; single_a() giữ lại để đối chiếu
  I2.5  f có đuôi xuống: phần trên của f + thân và móc dưới của j (cùng module móc j)
  I2.6  chữ có dấu: chữ gốc italic + dấu của Roman (giữ nguyên hình), dời theo tâm chữ gốc; sừng ư ơ và thanh đ dời theo mép thân
  I2.7  chữ hoa, số, dấu câu, ký hiệu: giữ hình Roman (chỉ nghiêng)
"""
import json, os, sys, math, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
for p in ('', 'ref', 'lower', 'font'): sys.path.insert(0, os.path.join(HERE, p))
import pathops
import vn_punct as V
from make_ref import outline
import spacing as SPc
OUT = os.path.join(HERE, '..', '..', 'out', 'construct'); OUTI = os.path.join(HERE, '..', '..', 'out', 'construct_italic')
XH = 495.0
CONDENSE = 0.94
TAIL = set('ilnmhud') | {'ı'}                 # a giữ hai tầng như Roman (designer 06/11), không đuôi
BIG = 3000
# designer 06/11 "thử giữ nguyên bản các glyph rồi làm italic thử" + "trừ các chữ hoa như nãy đã duyệt": chữ thường giữ glyph Roman
# (chỉ nghiêng khi xuất); chữ hoa hẹp 0.94 (I2.12). Phần I2 chữ thường (đuôi ra, f, v w y, nét vào, chân gọn) giữ trong code, bật bằng LOWER_I2
LOWER_I2 = False
# designer 06/11 "bạn nên giữ lại glyph gốc cho cả chữ hoa": chữ hoa cũng giữ glyph Roman → Italic = Roman nghiêng 10° (I1)
CAPS_COND = False

def P(d): return outline([d])
def runs_at(p, y):
    x0, _, x1, _ = p.bounds; r = V.I(p, V.rect(x0 - 10, y - 0.05, x1 + 10, y + 0.05))
    return sorted((c.bounds[0], c.bounds[2]) for c in r.contours)
def cond(p): return V.xform(p, lambda x, y: (x*CONDENSE, y))
def clean(p, amin=300):
    out = pathops.Path()
    for c in p.contours:
        if abs(c.area) >= amin: out.addPath(c)
    return pathops.op(out, out, pathops.PathOp.UNION)

def tail_module(t):
    """móc chân t: phần dưới cao độ yh (nơi thân t còn thẳng, đúng bề dày thân) — trả (móc, mép trái thân, mép phải thân, yh)"""
    s0, s1 = runs_at(t, 250)[0]; sw = s1 - s0; yh = 250.0
    for y in range(250, 20, -2):                             # đi xuống tới khi thân bắt đầu cong (rộng ra / lệch)
        r = runs_at(t, y)[0]
        if abs((r[1] - r[0]) - sw) > 1.0 or abs(r[0] - s0) > 1.0: break
        yh = y
    yc = yh + 30                                             # cắt trong đoạn thẳng, trên chỗ cong 30 u
    hook = V.I(t, V.rect(-BIG, -BIG, BIG, yc))
    return hook, s0, s1, yc

def with_tail(g, T, bowl=False):
    """thay chân phải (thân phải + loe chân) của g bằng móc t: canh mép trái thân, giãn ngang theo bề dày thân đích
    (thân t mảnh hơn thân n → mép phải thụt ở mối nối); bowl (u a d): không cắt loe trái (bụng nhập thân ở đó)"""
    hook, t0, t1, yc = T
    rs = runs_at(g, yc); x0, x1 = rs[-1]
    cut = V.rect(x0 - 0.5, -BIG, BIG, yc)
    if not bowl: cut = V.U(cut, V.rect(x0 - 40, -BIG, x0 + 1, 40))
    body = V.D(g, cut)
    k = (x1 - x0)/(t1 - t0)
    h = V.xform(hook, lambda x, y: (x0 + (x - t0)*k, y))
    stem_fill = V.rect(x0, yc - 2, x1, yc + 2)                  # phủ mối nối (không cạnh trùng khít)
    return clean(V.U(body, h, stem_fill))

def stem_runs(g, y, sw, tol=22):
    """các đoạn mực ở cao độ y có bề rộng ≈ thân (thân đứng, không phải bụng / nét chéo)"""
    return [r for r in runs_at(g, y) if abs((r[1] - r[0]) - sw) <= tol]

def entry(g, sw):
    """I2.8 nét vào: đầu thân ở x-height bỏ loe phải (chỉ khi loe đứng riêng — không phải vai / bụng nối từ thân), giữ loe trái
    làm cờ nét vào"""
    for x0, x1 in stem_runs(g, XH - 120, sw):
        box = V.rect(x1 + 0.5, XH - 75, x1 + 48, XH + 6); piece = V.I(g, box)
        if list(piece.segments) and piece.bounds[2] < x1 + 42: g = V.D(g, box)
    return g

def cut_foot(g, x0, x1, ybot):
    """I2.9 chân gọn: chân thân (đáy ở ybot) bỏ loe hai bên, cắt thẳng"""
    sw = x1 - x0; yf = ybot + 150
    for y in range(int(ybot + 150), int(ybot), -2):
        rr = [r for r in runs_at(g, y) if r[1] > x0 - 1 and r[0] < x1 + 1]
        if not rr or (rr[0][1] - rr[0][0]) > sw + 1.0: break
        yf = y
    g = V.D(g, V.rect(x0 - 50, ybot - 30, x1 + 50, yf))
    return V.U(g, V.rect(x0, ybot, x1, yf + 1))

FOOT = set('nmhrk')                                  # chân thân ở đường chân (trừ chân đã có đuôi ra)
FOOT_DESC = set('pq')                                # chân thân dưới đường chân
ENTRY = set('ijmnpru') | {'ı', 'ȷ'}

def feet(c, g, sw):
    if c in FOOT:
        rs = stem_runs(g, 120, sw)
        if c == 'k': rs = rs[:1]
        if c in TAIL: rs = rs[:-1]
        for x0, x1 in rs: g = cut_foot(g, x0, x1, 0.0)
    if c in FOOT_DESC:
        yb = g.bounds[1]
        for x0, x1 in stem_runs(g, yb + 140, sw)[:1]: g = cut_foot(g, x0, x1, yb)
    return g

def _q2c(p):
    import symbols as Sy
    return Sy.q2c(p)
def _dil(p, r):
    s_ = pathops.Path(); s_.addPath(p); s_.stroke(2*r, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s_.convertConicsToQuads(); return V.U(p, _q2c(s_))
def _ero(p, r):
    s_ = pathops.Path(); s_.addPath(p); s_.stroke(2*r, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
    s_.convertConicsToQuads(); return V.D(p, _q2c(s_))

def round_bottom(g, sw, pairs=1, yr=XH*0.45):
    """I2.10 v w đáy tròn: dưới yr (0.45 x-height) hai nét cong về đáy (tiếp tuyến ngang ở đáy) — mép ngoài đáy ở −8 (vượt đường
    chân như o), mép trong đáy ở −8 + 0.85 thân; mỗi mép là hai cubic: từ mép nét ở yr (tiếp tuyến theo mép) → điểm đáy"""
    R1 = runs_at(g, yr); st = 30.0; R2 = runs_at(g, yr + st)
    while len(R2) != len(R1) and st > 6: st /= 2; R2 = runs_at(g, yr + st)
    top = V.I(g, V.rect(-BIG, yr - 2, BIG, BIG)); parts = [top]
    def dirn(xa, xb):
        dx, dy = xa - xb, -st; L = math.hypot(dx, dy); return (dx/L, dy/L)
    def half(P0, d0, B, right):                              # P0 (mép, yr) → B (đáy, tiếp tuyến ngang)
        h1 = 0.55*(P0[1] - B[1])/abs(d0[1]); h2 = 0.55*abs(B[0] - P0[0])
        c1 = (P0[0] + d0[0]*h1, P0[1] + d0[1]*h1); c2 = (B[0] + (h2 if right else -h2), B[1])
        return c1, c2
    for k in range(pairs):
        (oL, iL), (iR, oR) = R1[2*k], R1[2*k + 1]
        (oL2, iL2), (iR2, oR2) = R2[2*k], R2[2*k + 1]
        dOL, dOR, dIL, dIR = dirn(oL, oL2), dirn(oR, oR2), dirn(iL, iL2), dirn(iR, iR2)
        Bo = ((oL + oR)/2, -8.0); Bi = ((iL + iR)/2, -8.0 + 0.85*sw)
        u = pathops.Path(); u.moveTo(oL, yr)
        c1, c2 = half((oL, yr), dOL, Bo, False); u.cubicTo(*c1, *c2, *Bo)
        c1, c2 = half((oR, yr), dOR, Bo, True); u.cubicTo(*c2, *c1, oR, yr)
        u.lineTo(oR, yr + 4); u.lineTo(iR, yr + 4); u.lineTo(iR, yr)
        c1, c2 = half((iR, yr), dIR, Bi, True); u.cubicTo(*c1, *c2, *Bi)
        c1, c2 = half((iL, yr), dIL, Bi, False); u.cubicTo(*c2, *c1, iL, yr)
        u.lineTo(iL, yr + 4); u.lineTo(oL, yr + 4); u.close()
        parts.append(pathops.op(u, u, pathops.PathOp.UNION, fix_winding=True))
    return clean(V.U(*parts))

def y_hook(y_, j, yc=-40.0):
    """I2.11 y đuôi cong: phần dưới yc của nét mảnh y thay bằng móc j, nghiêng theo nét mảnh và giãn theo bề ngang nét"""
    (a0, a1), (b0, b1) = runs_at(y_, yc)[0], runs_at(y_, yc - 100)[0]
    sl = ((a0 + a1)/2 - (b0 + b1)/2)/100.0                     # dx / dy của nét mảnh
    j0, j1 = runs_at(j, yc)[0]; k = (a1 - a0)/(j1 - j0)
    jb = V.I(j, V.rect(-BIG, -BIG, BIG, yc + 10))
    jb = V.xform(jb, lambda x, y: (a0 + (x - j0)*k + (y - yc)*sl, y))
    return clean(V.U(V.D(y_, V.rect(-BIG, -BIG, BIG, yc)), jb))

def single_a(d, T):
    """a một tầng: thân d cắt ngang ở x-height (phần bên phải mép trái thân, trên XH), chân phải = đuôi ra"""
    s0, s1 = runs_at(d, 300)[-1]
    a = V.D(d, V.U(V.rect(s0 - 0.5, XH, BIG, BIG), V.rect(-BIG, XH + 15, BIG, BIG)))
    return with_tail(a, T, bowl=True)

def italic_f(f, j):
    """f: phần trên của f + thân / móc dưới của j, canh mép trái thân"""
    f0, f1 = runs_at(f, 200)[0]; j0, j1 = runs_at(j, 200)[0]
    top = V.D(f, V.rect(f0 - 80, -BIG, f1 + 80, 120))
    k = (f1 - f0)/(j1 - j0)                                       # thân j giãn ngang theo bề dày thân f (không gờ ở mối nối)
    jb = V.xform(V.I(j, V.rect(-BIG, -BIG, BIG, 160)), lambda x, y: (f0 + (x - j0)*k, y))
    return clean(V.U(top, jb, V.rect(f0, 110, f1, 170)))

def band_x(p, ylo=5.0, yhi=XH - 5):
    q = V.I(p, V.rect(-BIG, ylo, BIG, yhi)); b = q.bounds; return b[0], b[2]

def edge_at(p, y, right=True):
    r = runs_at(p, y); return r[-1][1] if right else r[0][0]

def rebase(acc_r, base_r, base_i, ch):
    """chữ có dấu: dấu (= chữ Roman − chữ gốc Roman) dời theo chữ gốc italic"""
    bx0, bx1 = band_x(base_r); ax0, ax1 = band_x(acc_r)
    dx = (ax1 - bx1) if ch in 'đĐ' else (ax0 - bx0)                            # vị trí chữ gốc trong chữ có dấu (Đ: thanh chìa trái → canh mép phải)
    horn = '\u031b' in unicodedata.normalize('NFD', ch)
    if horn or ch in 'đĐ' or base_r.bounds[1] < -30: marks = clean(V.D(acc_r, V.move(base_r, dx, 0)), 200)
    if ch in 'đĐ': marks = V.U(marks, V.move(marks, 3, 0), V.move(marks, -3, 0))   # thanh: nới 3 u mỗi phía → luôn chồng lên thân
    else:                                                        # dấu trên / dưới: theo dải cao độ (không trừ boolean → dấu
        tb = V.move(base_r, dx, 0).bounds                        # không vỡ mảnh có cạnh chung)
        marks = V.U(V.I(acc_r, V.rect(-BIG, tb[3] + 2, BIG, BIG)), V.I(acc_r, V.rect(-BIG, -BIG, BIG, tb[1] - 2)))
    if '̛' in unicodedata.normalize('NFD', ch):              # sừng: theo mép phải ở 0.8 x-height
        y = 0.8*base_r.bounds[3]; sh = edge_at(base_i, y) - edge_at(base_r, y) - 3      # lấn vào thân 3 u (không hở, không cạnh trùng)
    elif ch in 'đĐ':                                             # thanh đ Đ: theo mép trái thân
        yy = 600 if ch == 'đ' else 560
        sh = edge_at(base_i, yy, False) - edge_at(base_r, yy, False)
    else:                                                        # dấu trên / dưới: theo tâm chữ gốc
        ix0, ix1 = band_x(base_i); sh = (ix0 + ix1)/2 - (bx0 + bx1)/2
    return clean(V.U(V.move(base_i, dx, 0), V.move(marks, sh, 0)))

def orient(d):
    """chiều contour theo độ lồng (ngoài ngược chiều kim đồng hồ, lòng cùng chiều) — hai master cùng chiều, nội suy không
    co méo (chấm i / ä ở Bold từng ngược chiều Regular → Medium chấm co lại)"""
    import export_font as E
    cs = E.parse(d)
    for j in E.flips(cs): cs[j] = E.reverse(cs[j])
    o = []
    for c in cs:
        o.append('M%.1f %.1f' % c[0][1])
        for s_ in c[1:]:
            o.append(('L%.1f %.1f' % s_[1]) if s_[0] == 'L' else ('C' + ' '.join('%.1f %.1f' % q for q in s_[1:])))
        o.append('Z')
    return ''.join(o)

def build(O, w):
    chars = sorted({k.rsplit('-', 1)[0] for k in O if k.endswith('-' + w)})
    low = [c for c in chars if SPc.kind(c) == 'lower']
    G = {}
    T = tail_module(cond(P(O[f't-{w}'])))
    base_set = [c for c in low if SPc.base(c) == c or c in 'ıȷ']
    sw = runs_at(cond(P(O[f'n-{w}'])), 250)[0]; sw = sw[1] - sw[0]
    jj = cond(P(O[f'j-{w}']))
    for c in (base_set if LOWER_I2 else []):
        g = cond(P(O[f'{c}-{w}']))
        if c == 'f': g = italic_f(g, jj)
        elif c in TAIL: g = with_tail(g, T, bowl=(c in 'ud'))
        if c in 'vw': g = round_bottom(g, sw, 2 if c == 'w' else 1)
        if c == 'y': g = y_hook(g, jj)
        g = feet(c, g, sw)
        if c in ENTRY: g = entry(g, sw)
        G[c] = clean(g)
    caps = [c for c in chars if SPc.kind(c) == 'caps'] if CAPS_COND else []               # I2.12 chữ hoa hẹp ngang như chữ thường, dấu giữ nguyên
    for c in caps:
        if SPc.base(c) == c: G[c] = cond(P(O[f'{c}-{w}']))
    for c in caps:
        if c in G: continue
        b = SPc.base(c)
        G[c] = rebase(cond(P(O[f'{c}-{w}'])), cond(P(O[f'{b}-{w}'])), G[b], c) if b in G else cond(P(O[f'{c}-{w}']))
    for c in (low if LOWER_I2 else []):
        if c in G: continue
        b = SPc.base(c)
        if b == 'i' and unicodedata.normalize('NFD', c)[1:2] not in ('\u0323',):   # dấu trên của i: chữ gốc là ı (không chấm)
            b = 'ı'
        if b not in G: G[c] = cond(P(O[f'{c}-{w}'])); continue
        G[c] = rebase(cond(P(O[f'{c}-{w}'])), cond(P(O[f'{b}-{w}'])), G[b], c)
    out = {}
    for c in chars:
        if c in G: g = G[c]; out[f'{c}-{w}'] = orient(V.to_d(V.move(g, -g.bounds[0], 0)))
        else: out[f'{c}-{w}'] = O[f'{c}-{w}']
    return out

def main():
    O = json.load(open(os.path.join(OUT, 'outlines.json')))
    os.makedirs(OUTI, exist_ok=True)
    R = {}
    for w in ('Regular', 'Bold'): R.update(build(O, w))
    json.dump(R, open(os.path.join(OUTI, 'outlines.json'), 'w'))
    import shutil
    shutil.copy(os.path.join(OUT, 'ref_ratios.json'), os.path.join(OUTI, 'ref_ratios.json'))
    print('italic:', len(R), 'glyph (Regular + Bold)')

if __name__ == '__main__':
    main()
