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
sys.path.insert(0, HERE)
from weights import WEIGHTS, lerp_w
lerp_w(SB_REF)
G_CAP, K_F, MIN_GAP, KMIN = 300.0, 0.45, 26.0, -150.0
SOFT = 0.55                          # sàn mềm khe chữ gốc (× khe chuẩn HH / nn / Hn)
MIN_GAP_HORN = 14.0                  # sàn khe ở vùng sừng ơ ư
WEDGE_U0, WEDGE_G, WEDGE_SOFT = 110.0, 0.35, 0.32   # designer 05/11 lần 2: "RA KA XA cũng hơi xa" — 0.25 / 0.38 → 0.35 / 0.32
# cặp NÊM ĐỐI NÊM (designer 05/11: "KA, RA, LA, ƯA, XA…" thưa): khe nhỏ nhất ở CHÂN (đường chân) nên luật khe nhỏ nhất không
# kéo vào, nhưng phía trên là hai khoảng trắng hình nêm đối nhau, sâu quá DEPTH 40 mà spacing một phía không bù hết.
# U = trung bình theo cao độ (vùng chung) của phần trắng sâu quá 40 ở CẢ HAI phía (chỉ đếm cao độ cả hai cùng > 40, mỗi phía
# tối đa 200). U > 110 → kern ≤ −0.25 (U − 110); sàn mềm của cặp nêm hạ xuống 0.38 khe chuẩn (chân gần như chân serif)
KMIN_DASH = -60.0                    # cặp có gạch / dấu toán: gạch rơi vào miệng C c L… chỉ kéo vào vừa phải
# lề phải bù KHẤC SÂU (designer 05/11: "kerning chữ k và i hơi xa"): k phải là khe chữ V sâu giữa đầu tay và chân (trắng sâu quá 40
# trung bình 105, gấp ~5 lần chữ thường khác); đo trắng chặn ở DEPTH 40 nên lề phải 14 vẫn thưa (ki trắng TB 218, ni 116) → rút 12
NOTCH_RS = {}   # bỏ (05/11): ki … theo trắng cặp tham chiếu
# A (designer 05/11: "RA KA XA… ĐA DA… AT TA cũng cần kiểm lại cho gần hơn" — mọi cặp có A thưa): hai khoảng trắng nêm của A
# lớn (trắng sâu quá 40 trung bình 120 / 114, cao nhất bộ hoa cùng V W X Y) mà spacing chặn ở DEPTH 40 → rút lề hai bên 15
SIDE_ADJ = {}   # bỏ (05/11): kern cặp chữ theo trắng cặp tham chiếu (REF_KERN) đã bao
# chỉnh tay theo designer (05/11: "ƯA hơi xa"): U / Ư + A (mọi A có dấu cùng class trái 'A') khe chân 134 — gấp đôi HA (67);
# kéo thêm 20 ở hai master (ƯA = UA theo luật ơn = on). Medium / SemiBold nội suy theo
KADJ = {}   # bỏ (05/11): UA ƯA AU theo trắng cặp tham chiếu   # + AU ("và AU"): A + U / Ư / Ú … (cùng class trái 'U')
CAP, XH = 700.0, 495.0

src = open(os.path.join(HERE, 'glyphs.js')).read()
import re
VN = re.search(r"const VN = '([^']*)'", src).group(1); VNL = re.search(r"const VNL = '([^']*)'", src).group(1)
def _jsconst(name):
    m = re.search(r'const ' + name + r' = ("(?:[^"\\]|\\.)*")', src); return json.loads(m.group(1)) if m else ''
SYM, COMB, LOWX = _jsconst('SYM'), _jsconst('COMB'), _jsconst('LOWX')
LATU, LATL, MATH = _jsconst('LATU'), _jsconst('LATL'), _jsconst('MATH')       # nhóm 3
PUNCT = list('.,:;!?\'"’‘”“-–—()[]/+=×#%$€&@') + list(SYM) + list(MATH)
SPACE = lerp_w({'Regular': 230, 'Bold': 245})                                    # space / nbsp: chỉ bề ngang (≈ 0.46 n)
# ký hiệu không kern class theo hình chữ (chỉ chống va): ký hiệu toán / đứng riêng — kern theo profile làm ~ · − ^ ` trượt
# vào miệng C, lòng b d (C~ −150, ^d −150 — QA 05/11). Dấu câu đi liền chữ (… ‚ „ « » ‹ › ¡ ¿ { } gạch mềm) vẫn kern.
NOKERN = set('*<>\\^_`|~•·©®™°±÷−‰§¶†‡£¥¢µ') | set(MATH)
CAPS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); LOWER = list('abcdefghijklmnopqrstuvwxyz'); FIG = list('0123456789')

def kind(ch):
    if ch in COMB: return 'mark'
    if ch in CAPS or ch in VN or ch in LATU: return 'caps'
    if ch in LOWER or ch in VNL or ch in LOWX or ch in LATL: return 'lower'
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
    # thứ tự: Regular, Bold trước; Medium / SemiBold lấy kern CLASS nội suy từ hai master (như variable font — QA kerning
    # 05/11: kern đo riêng từng weight nhảy bậc ở ngưỡng hình học, vd. c- −60 / −60 / −60 / 0, L» −115 / −115 / 0 / 0),
    # rồi chặn va chạm riêng theo outline của chính weight đó
    from weights import TW
    for w in ('Regular', 'Bold') + tuple(x for x in WEIGHTS if x not in ('Regular', 'Bold')):
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
            k = kind(ch)
            if k == 'mark': continue
            t = T['lower'] if k == 'lower' else T['caps']
            b = band(ch, PR[ch]); x0, _, x1, _ = P[ch].bounds
            ls, rs = t - white(PR[ch], 'L', b), t - white(PR[ch], 'R', b)
            if k == 'punct': ls, rs = max(ls, 20.0), max(rs, 20.0)
            rs += NOTCH_RS.get(ch, 0.0); ls += SIDE_ADJ.get(ch, (0.0, 0.0))[0]; rs += SIDE_ADJ.get(ch, (0.0, 0.0))[1]
            sp[ch] = (round(ls - x0), round(x1 - x0 + ls + rs))          # (dịch outline, advance)
        for ch in chars:                                                   # chữ có dấu: theo chữ gốc
            if ch not in sp and kind(ch) != 'mark':
                # canh theo PHẦN CHỮ GỐC (trung vị lệch profile ở các cao độ cả hai cùng có mực, trong vùng chữ), không theo
                # mép mực: Đ / đ có thanh chìa trái, dấu / sừng có thể chìa ngang → canh theo mép mực đặt lệch cả chữ
                # (QA kerning 05/11: Đ lệch 40.5 u, Bold 63.5, mọi cặp Đ + chữ sau đều sát / chạm)
                b0 = base(ch); dx, adv = sp[b0]; bnd = band(b0, PR[b0])
                (La, Ra), (Lb, Rb) = PR[ch], PR[b0]
                m = ~np.isnan(La) & ~np.isnan(Lb) & (YS >= bnd[0]) & (YS <= bnd[1])
                off = float(np.median(np.concatenate([(La - Lb)[m], (Ra - Rb)[m]])))
                dxa = dx - round(off)
                if ch in 'Đđ':                                             # thanh chìa trái: lề trái tính lại như chữ gốc
                    k = kind(ch); t = T['lower'] if k == 'lower' else T['caps']
                    ls = t - white(PR[ch], 'L', band(ch, PR[ch])); x0 = P[ch].bounds[0]
                    need = round(ls - x0) - dxa                            # dịch thêm để lề trái thanh = lề quang học
                    if need > 0: dxa += need; adv += need
                sp[ch] = (dxa, adv)
        # dấu tổ hợp: bề ngang 0, đặt về TRƯỚC (đè lên chữ đứng trước): tâm dấu ở giữa ô n trước đó; sừng U+031B bám mép phải
        # mực của chữ trước (= − lề phải n). Vị trí chính xác theo từng chữ sẽ làm bằng anchor GPOS mark khi xuất font.
        n_dx, n_adv = sp['n']; n_rsb = n_adv - n_dx - round(P['n'].bounds[2])
        for ch in chars:
            if kind(ch) != 'mark': continue
            sp[ch] = (-n_rsb, 0) if ch == '\u031b' else (-round(n_adv/2), 0)
        spacing[w] = {ch: {'dx': v[0], 'adv': v[1]} for ch, v in sp.items()}
        for ch in (' ', '\u00a0'): spacing[w][ch] = {'dx': 0, 'adv': round(SPACE[w])}       # space, nbsp
        chars = [c for c in chars if kind(c) != 'mark']                    # kerning: không kern dấu tổ hợp

        # ---- kerning theo class ----
        def placed(ch):                     # profile đặt theo spacing (gốc toạ độ = đầu ô)
            L, R = PR[ch]; dx = sp[ch][0]; return L + dx, R + dx
        def pair_gap(a, b_, kern=0.0):
            La, Ra = placed(a); Lb, Rb = placed(b_); return (Lb + sp[a][1] + kern) - Ra
        def ext(ch):                        # cao độ mực của chữ
            L, _ = PR[ch]; ys = YS[~np.isnan(L)]; return (ys.min(), ys.max())
        def pband(a, b_):
            """vùng đo = phần chồng nhau của tầm cao mực hai chữ (chữ hoa / số: cả 0–700; thường: tới đỉnh mực của nó). Thanh T với
            đỉnh b h nằm trong vùng (T b, T h không bị kéo tới sàn 26); thanh T với o thì không (T o kéo vào dưới thanh)"""
            (a0, a1), (b0, b1) = ext(a), ext(b_)
            if kind(a) in ('caps', 'fig'): a0, a1 = min(a0, 0.0), max(a1, CAP)
            if kind(b_) in ('caps', 'fig'): b0, b1 = min(b0, 0.0), max(b1, CAP)
            return (max(a0, b0), min(a1, b1))
        def W(a, b_, bnd):
            """khe NHỎ NHẤT giữa hai profile trong vùng (chỉ các cao độ cả hai cùng có mực); None nếu không đối diện nhau"""
            g = pair_gap(a, b_); m = (YS >= bnd[0]) & (YS <= bnd[1]); g = g[m]; g = g[~np.isnan(g)]
            return float(g.min()) if len(g) else None
        def ref(ch): return 'n' if kind(ch) == 'lower' else 'H'
        rcls = sorted({rclass(c) for c in chars}); lcls = sorted({lclass(c) for c in chars})
        def rep(side, cl):                                                 # đại diện class: chữ gốc; sừng: Ơ Ư ơ ư
            c = unicodedata.normalize('NFC', cl); return c if c in P else None
        rep_ = {('R', rc): rep('R', rc) for rc in rcls}; rep_.update({('L', lc): rep('L', lc) for lc in lcls})
        KC = {}
        RF = os.path.join(OUT, 'ref_ratios.json')
        REFR = None
        if os.path.exists(RF):                                             # trung bình tỉ số Regular + Bold tham chiếu cho CẢ HAI master:
            RR = json.load(open(RF)); REFR = {p_: [(RR['Regular'][p_][0] + RR['Bold'][p_][0])/2] for p_ in RR['Regular'] if p_ in RR['Bold']}
            # (font Bold tham chiếu dàn khác Regular của chúng → kern đổi dấu giữa hai master, vd. Fa −30 / +5)
        from ref_kern import white as _white
        for rc in rcls:
            a = rep_.get(('R', rc))
            if a is None: continue
            for lc in lcls:
                b_ = rep_.get(('L', lc))
                if b_ is None: continue
                if kind(a) == 'punct' and kind(b_) == 'punct': continue
                if a in NOKERN or b_ in NOKERN: continue
                bnd = pband(a, b_); wv = W(a, b_, bnd)
                ra = ref(a) if kind(a) != 'punct' else 'H'; rb = ref(b_) if kind(b_) != 'punct' else 'H'
                wr = W(ra, rb, (0.0, XH if 'n' in (ra, rb) else CAP))
                if wv is None or wr is None: continue
                k = -K_F*(wv - wr)
                lo = KMIN_DASH if (a in '-–—=+×\u00ad' or b_ in '-–—=+×\u00ad') else KMIN
                k = max(lo, min(0.0, k)); k = math.ceil(k/5)*5                # chỉ kéo vào; tròn về phía rộng
                wedge = False
                if kind(a) != 'punct' and kind(b_) != 'punct':
                    La_, Ra_ = PR[a]; Lb_, Rb_ = PR[b_]
                    wa_ = np.nanmax(Ra_) - Ra_; wb_ = Lb_ - np.nanmin(Lb_)
                    m_ = (YS >= bnd[0]) & (YS <= bnd[1])
                    both = m_ & ~np.isnan(wa_) & ~np.isnan(wb_) & (wa_ > DEPTH) & (wb_ > DEPTH)
                    u = float(np.where(both, np.minimum(wa_ - DEPTH, 200) + np.minimum(wb_ - DEPTH, 200), 0)[m_].mean()) if m_.any() else 0.0
                    if u > WEDGE_U0:
                        wedge = True; k = min(k, max(lo, math.ceil(-WEDGE_G*(u - WEDGE_U0)/5)*5))
                # sàn mềm: cặp chữ gốc giữ khe nhỏ nhất ≥ SOFT × khe chuẩn (ff ft vt yt… Regular chỉ 32–36 so với nn 70 — QA
                # kerning 05/11); thiếu thì đẩy nhẹ ra (kern dương)
                if kind(a) != 'punct' and kind(b_) != 'punct' and '\u031b' not in rc:   # sừng: đã có sàn riêng
                    g = pair_gap(a, b_, k); gm = float(np.nanmin(g)) if np.any(~np.isnan(g)) else 999.0
                    fl_ = (WEDGE_SOFT if wedge else SOFT)*wr
                    if gm < fl_: k += math.ceil((fl_ - gm)/5)*5
                k += KADJ.get(f'{rc}|{lc}', 0)
                # TRẮNG CẶP THEO THAM CHIẾU (skill type-qa-qc §3.1 S1c, DINHTUONG60s; designer 05/11 "dùng skill kerning của Dinh
                # Tuong đã đo sẵn"): cặp chữ / số → kern để W(a, b) / W(n n | H H) = trung vị của các font serif tham chiếu
                # (ref_kern.py); Ư Ơ ư ơ dùng cặp gốc (ƯA = UA). Giới hạn: |k| ≤ 0.4 advance hẹp hơn; va chạm chặn ở bước sau
                ra_, rb_ = base(a), base(b_)
                if REFR is not None and ra_ + rb_ in REFR:
                    lower_ = ra_.islower() or rb_.islower()
                    band_ = (0.0, XH) if lower_ else (0.0, CAP)
                    Wn = _white(placed('n' if lower_ else 'H'), placed('n' if lower_ else 'H'), sp['n' if lower_ else 'H'][1], 0.0, band_, YS, 0.12*XH)
                    W0 = _white(placed(ra_), placed(rb_), sp[ra_][1], 0.0, band_, YS, 0.12*XH)
                    if Wn and W0 is not None:
                        k = REFR[ra_ + rb_][0]*Wn - W0
                        lim = 0.4*min(sp[ra_][1], sp[rb_][1]); k = max(-lim, min(lim, k)); k = math.ceil(k/5)*5
                if k <= -10 or k >= 5: KC[f'{rc}|{lc}'] = k
        if w not in ('Regular', 'Bold'):
            KR, KB = kerning['Regular']['class'], kerning['Bold']['class']; t_ = TW[w]; KC = {}
            for key in set(KR) | set(KB):
                v = KR.get(key, 0.0) + (KB.get(key, 0.0) - KR.get(key, 0.0))*t_; v = math.ceil(v/5)*5
                if v <= -10 or v >= 5: KC[key] = v
        # ---- chặn va chạm: mọi cặp ký tự chữ / số / dấu câu ----
        # sàn khe theo cao độ: vùng SỪNG (ơ ư Ơ Ư và chữ có dấu của chúng — chỗ viền phải khác chữ gốc) chỉ cần MIN_GAP_HORN:
        # sừng là chi tiết nhỏ ở cao, sàn 26 đẩy mọi cặp ư ơ + chữ sau ra ≈ +30 (ưu, ươ, ƯỜ thưa hẳn — QA kerning 05/11;
        # luật S14: ươ = uo, ơn = on)
        FLOOR = {}
        for c in chars:
            if '\u031b' not in unicodedata.normalize('NFD', c): continue
            b0 = base(c); Rc = placed(c)[1]; Rb = placed(b0)[1]
            horn = ~np.isnan(Rc) & (np.isnan(Rb) | (Rc > Rb + 3))
            FLOOR[c] = np.where(horn, MIN_GAP_HORN, MIN_GAP)
        EXC = {}; worst = []
        for a in chars:
            Ra = placed(a)[1]
            for b_ in chars:
                if kind(a) == 'punct' and kind(b_) == 'punct': continue
                k = KC.get(f'{rclass(a)}|{lclass(b_)}', 0.0)
                g = pair_gap(a, b_, k)
                if not np.any(~np.isnan(g)): continue
                short = np.nanmax(FLOOR.get(a, MIN_GAP) - g)                  # thiếu bao nhiêu so với sàn (theo cao độ)
                gm = np.nanmin(g)
                if short > 0:
                    need = math.ceil(short/5)*5; k2 = k + need
                    EXC[f'{a}|{b_}'] = k2; worst.append((round(gm, 1), a + b_, k, k2))
        kerning[w] = {'class': KC, 'exc': EXC}
        nexc = len(EXC); top = sorted(KC.items(), key=lambda kv: kv[1])[:12]
        print(w, 'spacing', len(sp), '· class kern', len(KC), '· ngoại lệ chống va', nexc)
        print('   mạnh nhất:', ' '.join(f'{k.replace("|", "")}{v:.0f}' for k, v in top))
    spacing = {x: spacing[x] for x in WEIGHTS}; kerning = {x: kerning[x] for x in WEIGHTS}
    json.dump(spacing, open(os.path.join(OUT, 'spacing.json'), 'w'), ensure_ascii=False)
    json.dump(kerning, open(os.path.join(OUT, 'kerning.json'), 'w'), ensure_ascii=False)

if __name__ == '__main__':
    main()
