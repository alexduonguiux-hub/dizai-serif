#!/usr/bin/env python3
"""Spacing + kerning (luật S14), Regular + Bold.
    python3 tools/construct/spacing.py   → out/construct/spacing.json (lsb, advance) + out/construct/kerning.json

Phương pháp (typeface-construction §15, rule book S14):
SPACING — khoảng trắng quang học theo H (hoa, số) / n (thường), độ sâu đo DEPTH = 40:
    trắng một bên A = trung bình theo cao độ (vùng chữ) của min(khoảng từ cực mực tới mép mực, DEPTH)
    sb = (sb_chuẩn + A_chuẩn) − A        sb_chuẩn: H 40 / Bold 44, n 32 / Bold 36
    dấu câu: vùng đo là vùng mực của chính nó, chuẩn H. Chữ có dấu / sừng giữ sb và advance của chữ gốc.
KERNING — theo class chữ gốc (Ơ Ư ơ ư có class phải riêng: sừng đổi viền phải):
    W = khe NHỎ NHẤT giữa hai profile trong vùng chung (hoa 0–700; có chữ thường 0–495; dấu câu: vùng mực của nó), chỉ ở
    các cao độ hai chữ cùng có mực; so với khe nhỏ nhất của cặp chuẩn (H H / n n …) cùng vùng.
    (Trung bình khoảng trắng kéo vào cả AH, AB… vì trắng riêng của A — phần đó spacing đã lo; kerning chỉ sửa chỗ hai
    profile để hở bất thường: AV To LT F. …)
    kern = −K_F · (W − W_chuẩn), K_F 0.45, chỉ kéo vào (≤ 0, ≥ −150; cặp có - – — = + × ≥ −60), bỏ |kern| < 10, làm tròn 5 về phía rộng.
    Chặn va chạm: mọi cặp (tính dấu, sừng, descender, ascender) giữ khe mực ≥ MIN_GAP = 26; vi phạm → nới (kern dương / bớt âm)
    thành ngoại lệ theo cặp ký tự.
"""
import json, os, sys, math, unicodedata
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'ref'))
from make_ref import outline
import vn_punct as V

OUT = os.path.join(HERE, '..', '..', 'out', 'construct')
STEP = 5.0; Y0, Y1 = -260.0, 1100.0
YS = np.arange(Y0, Y1 + 0.1, STEP)
DEPTH = 40.0
SB_REF = {'Regular': {'caps': 40.0, 'lower': 32.0}, 'Bold': {'caps': 44.0, 'lower': 36.0}}
G_CAP, K_F, MIN_GAP, KMIN = 300.0, 0.45, 26.0, -150.0
KMIN_DASH = -60.0                    # cặp có gạch / dấu toán: gạch rơi vào miệng C c L… chỉ kéo vào vừa phải
CAP, XH = 700.0, 495.0

src = open(os.path.join(HERE, 'glyphs.js')).read()
import re
VN = re.search(r"const VN = '([^']*)'", src).group(1); VNL = re.search(r"const VNL = '([^']*)'", src).group(1)
PUNCT = list('.,:;!?\'"’‘”“-–—()[]/+=×#%$€&@')
CAPS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); LOWER = list('abcdefghijklmnopqrstuvwxyz'); FIG = list('0123456789')

def kind(ch):
    if ch in CAPS or ch in VN: return 'caps'
    if ch in LOWER or ch in VNL: return 'lower'
    if ch in FIG: return 'fig'
    return 'punct'
def base(ch):
    if ch in 'Đđ₫': return {'Đ': 'D', 'đ': 'd', '₫': '₫'}[ch]
    b = unicodedata.normalize('NFD', ch)[0]; return b if b != ch or ch in CAPS + LOWER else ch
def rclass(ch):                       # class phía phải (chữ đứng trước)
    nfd = unicodedata.normalize('NFD', ch)
    if '̛' in nfd: return nfd[0] + '̛'   # sừng
    return base(ch)
def lclass(ch): return base(ch)       # class phía trái (chữ đứng sau)

# ---------- profile ----------
def flatten(p, n=16):
    polys = []; cur = []; pt = None
    for v, ps in p.segments:
        if v == 'moveTo': cur = [ps[0]]; pt = ps[0]
        elif v == 'lineTo': cur.append(ps[0]); pt = ps[0]
        elif v == 'curveTo':
            c = (pt, *ps); cur += [V.bez(c, k/n) for k in range(1, n + 1)]; pt = ps[2]
        elif v == 'closePath':
            if len(cur) > 2: polys.append(np.array(cur))
            cur = []
    return polys
def profile(p):
    """mép trái / phải của mực ở mỗi cao độ YS (NaN: không có mực)"""
    L = np.full(len(YS), np.nan); R = np.full(len(YS), np.nan)
    for poly in flatten(p):
        a = poly; b = np.roll(poly, -1, axis=0)
        for i, y in enumerate(YS):
            m = (a[:, 1] - y)*(b[:, 1] - y) < 0
            if not m.any(): continue
            xa, ya, xb, yb = a[m, 0], a[m, 1], b[m, 0], b[m, 1]
            xs = xa + (y - ya)*(xb - xa)/(yb - ya)
            lo, hi = xs.min(), xs.max()
            L[i] = lo if np.isnan(L[i]) else min(L[i], lo); R[i] = hi if np.isnan(R[i]) else max(R[i], hi)
    return L, R

def band(ch, prof):
    k = kind(ch)
    if k in ('caps', 'fig'): return (0.0, CAP)
    if k == 'lower': return (0.0, XH)
    L, _ = prof; ys = YS[~np.isnan(L)]; return (ys.min(), ys.max())

def white(prof, side, b):
    L, R = prof; m = (YS >= b[0]) & (YS <= b[1])
    if side == 'L':
        x = L[m]; ext = np.nanmin(L[m]) if np.any(~np.isnan(x)) else 0; d = x - ext
    else:
        x = R[m]; ext = np.nanmax(R[m]) if np.any(~np.isnan(x)) else 0; d = ext - x
    d = np.where(np.isnan(d), DEPTH, np.minimum(d, DEPTH)); return float(d.mean())

def main():
    O = json.load(open(os.path.join(OUT, 'outlines.json')))
    spacing, kerning = {}, {}
    for w in ('Regular', 'Bold'):
        chars = [k.rsplit('-', 1)[0] for k in O if k.endswith('-' + w)]
        P = {ch: outline([O[f'{ch}-{w}']]) for ch in chars}
        PR = {ch: profile(P[ch]) for ch in chars}
        # ---- spacing: chữ gốc ----
        T = {}
        for ref, kd in (('H', 'caps'), ('n', 'lower')):
            b = band(ref, PR[ref]); T[kd] = SB_REF[w][kd] + (white(PR[ref], 'L', b) + white(PR[ref], 'R', b))/2
        sp = {}
        for ch in chars:
            if base(ch) != ch and base(ch) in P: continue
            k = kind(ch); t = T['lower'] if k == 'lower' else T['caps']
            b = band(ch, PR[ch]); x0, _, x1, _ = P[ch].bounds
            ls, rs = t - white(PR[ch], 'L', b), t - white(PR[ch], 'R', b)
            if k == 'punct': ls, rs = max(ls, 20.0), max(rs, 20.0)
            sp[ch] = (round(ls - x0), round(x1 - x0 + ls + rs))          # (dịch outline, advance)
        for ch in chars:                                                   # chữ có dấu: theo chữ gốc
            if ch not in sp:
                b0 = base(ch); dx, adv = sp[b0]; bx0 = P[b0].bounds[0]
                sp[ch] = (dx + round(bx0 - P[b0].bounds[0]), adv)
        spacing[w] = {ch: {'dx': v[0], 'adv': v[1]} for ch, v in sp.items()}

        # ---- kerning theo class ----
        def placed(ch):                     # profile đặt theo spacing (gốc toạ độ = đầu ô)
            L, R = PR[ch]; dx = sp[ch][0]; return L + dx, R + dx
        def pair_gap(a, b_, kern=0.0):
            La, Ra = placed(a); Lb, Rb = placed(b_); return (Lb + sp[a][1] + kern) - Ra
        def W(a, b_, bnd):
            """khe NHỎ NHẤT giữa hai profile trong vùng (chỉ các cao độ cả hai cùng có mực); None nếu không đối diện nhau"""
            g = pair_gap(a, b_); m = (YS >= bnd[0]) & (YS <= bnd[1]); g = g[m]; g = g[~np.isnan(g)]
            return float(g.min()) if len(g) else None
        def ref(ch): return 'n' if kind(ch) == 'lower' else 'H'
        def pband(a, b_):
            ka, kb = kind(a), kind(b_)
            if ka == 'punct': return band(a, PR[a])
            if kb == 'punct': return band(b_, PR[b_])
            if 'lower' in (ka, kb): return (0.0, XH)
            return (0.0, CAP)
        bases = [c for c in chars if base(c) == c]
        rcls = sorted({rclass(c) for c in chars}); lcls = sorted({lclass(c) for c in chars})
        def rep(side, cl):                                                 # đại diện class: chữ gốc; sừng: Ơ Ư ơ ư
            c = unicodedata.normalize('NFC', cl); return c if c in P else None
        rep_ = {('R', rc): rep('R', rc) for rc in rcls}; rep_.update({('L', lc): rep('L', lc) for lc in lcls})
        KC = {}
        for rc in rcls:
            a = rep_.get(('R', rc))
            if a is None: continue
            for lc in lcls:
                b_ = rep_.get(('L', lc))
                if b_ is None: continue
                if kind(a) == 'punct' and kind(b_) == 'punct': continue
                bnd = pband(a, b_); wv = W(a, b_, bnd); wr = W(ref(a), ref(b_), bnd) if kind(a) != 'punct' and kind(b_) != 'punct' \
                    else W(ref(a) if kind(a) != 'punct' else 'H', ref(b_) if kind(b_) != 'punct' else 'H', (0.0, CAP))
                if wv is None or wr is None: continue
                k = -K_F*(wv - wr)
                k = max(KMIN_DASH if (a in '-–—=+×' or b_ in '-–—=+×') else KMIN, min(0.0, k))
                k = math.ceil(k/5)*5                                       # tròn về phía rộng
                if k <= -10: KC[f'{rc}|{lc}'] = k
        # ---- chặn va chạm: mọi cặp ký tự chữ / số / dấu câu ----
        EXC = {}; worst = []
        for a in chars:
            Ra = placed(a)[1]
            for b_ in chars:
                if kind(a) == 'punct' and kind(b_) == 'punct': continue
                k = KC.get(f'{rclass(a)}|{lclass(b_)}', 0.0)
                g = pair_gap(a, b_, k); gm = np.nanmin(g) if np.any(~np.isnan(g)) else 999
                if gm < MIN_GAP:
                    need = math.ceil((MIN_GAP - gm)/5)*5; k2 = k + need
                    EXC[f'{a}|{b_}'] = k2; worst.append((round(gm, 1), a + b_, k, k2))
        kerning[w] = {'class': KC, 'exc': EXC}
        nexc = len(EXC); top = sorted(KC.items(), key=lambda kv: kv[1])[:12]
        print(w, 'spacing', len(sp), '· class kern', len(KC), '· ngoại lệ chống va', nexc)
        print('   mạnh nhất:', ' '.join(f'{k.replace("|", "")}{v:.0f}' for k, v in top))
    json.dump(spacing, open(os.path.join(OUT, 'spacing.json'), 'w'), ensure_ascii=False)
    json.dump(kerning, open(os.path.join(OUT, 'kerning.json'), 'w'), ensure_ascii=False)

if __name__ == '__main__':
    main()
