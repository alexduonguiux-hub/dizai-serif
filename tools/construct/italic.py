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
    bx0, bx1 = band_x(base_r); ax0, _ = band_x(acc_r); dx = ax0 - bx0           # vị trí chữ gốc trong chữ có dấu
    horn = '\u031b' in unicodedata.normalize('NFD', ch)
    if horn or ch in 'đ' or base_r.bounds[1] < -30: marks = clean(V.D(acc_r, V.move(base_r, dx, 0)), 200)
    else:                                                        # dấu trên / dưới: theo dải cao độ (không trừ boolean → dấu
        tb = V.move(base_r, dx, 0).bounds                        # không vỡ mảnh có cạnh chung)
        marks = V.U(V.I(acc_r, V.rect(-BIG, tb[3] + 2, BIG, BIG)), V.I(acc_r, V.rect(-BIG, -BIG, BIG, tb[1] - 2)))
    if '̛' in unicodedata.normalize('NFD', ch):              # sừng: theo mép phải ở 0.8 x-height
        y = XH*0.8; sh = edge_at(base_i, y) - edge_at(base_r, y) - 3      # lấn vào thân 3 u (không hở, không cạnh trùng)
    elif ch in 'đ':                                              # thanh đ: theo mép trái thân (ở 600)
        sh = edge_at(base_i, 600, False) - edge_at(base_r, 600, False)
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
    for c in base_set:
        g = cond(P(O[f'{c}-{w}']))
        if c == 'f': g = italic_f(g, cond(P(O[f'j-{w}'])))
        elif c in TAIL: g = with_tail(g, T, bowl=(c in 'ud'))
        G[c] = g
    for c in low:
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
