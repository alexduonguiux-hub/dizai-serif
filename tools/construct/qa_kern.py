#!/usr/bin/env python3
"""QA/QC kerning (dizai-serif-qa §2 Spacing/kerning; typeface-construction §15), Regular + Bold.
    python3 tools/construct/qa_kern.py            → in báo cáo + out/construct/qa_kern.json

Kiểm:
 A. Khe mực nhỏ nhất của MỌI cặp ký tự (chữ, số, dấu câu; tính dấu, sừng, ascender, descender) ≥ 26.
 B. Cặp có dấu / sừng so với cặp gốc (ưn = un, Ĩn = In, đĩ = đi): lệch kern ≤ 12, trừ khi lệch chỉ vì sàn 26 (liệt kê riêng).
 C. Âm tiết tiếng Việt (phụ âm đầu × vần × 6 thanh, ba kiểu viết: thường / Hoa đầu / HOA): mọi cặp kề → thống kê B.
 D. Cặp kinh điển: AV AT LT LY TA VA WA AW PA FA RV KO To Ty Te Yo P. F, r. y. v, "A 11 17 — giá trị và khoảng trắng.
 E. Cặp chữ gốc quá sát: khe nhỏ nhất sau kern < 0.38 × khe chuẩn cùng loại (HH / nn / Hn / nH) — sàn của cặp nêm đối nêm;
    cặp thường còn sàn mềm 0.55 trong spacing.py.
 F. Dấu câu × dấu câu: va chạm (< 26).  G. Mọi ký tự có class kern trái / phải.  H. Kern chạm trần mà khe còn rộng (thiếu kern).
 I. Kern class nhất quán giữa 4 weight (Medium / SemiBold ≈ nội suy R → B ±25, không đổi dấu).
"""
import json, os, sys, math, unicodedata, itertools, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'ref'))
import spacing as SPc
from make_ref import outline
OUT = os.environ.get('DIZAI_OUT') or os.path.join(HERE, '..', '..', 'out', 'construct')   # DIZAI_OUT: nhánh Italic (out/construct_italic)
O = json.load(open(os.path.join(OUT, 'outlines.json'))); SP = json.load(open(os.path.join(OUT, 'spacing.json')))
KN = json.load(open(os.path.join(OUT, 'kerning.json')))
YS = SPc.YS; MIN_GAP = SPc.MIN_GAP

def kern(w, a, b):
    K = KN[w]; v = K['exc'].get(f'{a}|{b}')
    return K['class'].get(f'{SPc.rclass(a)}|{SPc.lclass(b)}', 0.0) if v is None else v

def run(w):
    chars = [k.rsplit('-', 1)[0] for k in O if k.endswith('-' + w) and SPc.kind(k.rsplit('-', 1)[0]) != 'mark']   # dấu tổ hợp: đè chủ ý
    PR = {c: SPc.profile(outline([O[f'{c}-{w}']])) for c in chars}
    def placed(c): L, R = PR[c]; d = SP[w][c]['dx']; return L + d, R + d
    PL = {c: placed(c) for c in chars}
    def gap(a, b, k=None):
        k = kern(w, a, b) if k is None else k; return PL[b][0] + SP[w][a]['adv'] + k - PL[a][1]
    def mingap(a, b, k=None):
        g = gap(a, b, k); return float(np.nanmin(g)) if np.any(~np.isnan(g)) else 999.0
    def white(a, b, k=None, cap=None):
        g = gap(a, b, k); m = ~np.isnan(g)
        if not m.any(): return None
        g = g[m]; return float(np.minimum(g, cap).mean()) if cap else float(g.mean())
    rep = {}
    # sàn khe theo cao độ: vùng sừng ơ ư Ơ Ư = MIN_GAP_HORN, còn lại MIN_GAP (như spacing.py)
    FL = {}
    def FLOOR(c):
        if c not in FL:
            if '\u031b' in unicodedata.normalize('NFD', c):
                Rc = PL[c][1]; Rb = PL[SPc.base(c)][1]; horn = ~np.isnan(Rc) & (np.isnan(Rb) | (Rc > Rb + 3))
                FL[c] = np.where(horn, SPc.MIN_GAP_HORN, MIN_GAP)
            else: FL[c] = np.full(len(YS), MIN_GAP)
        return FL[c]
    def at_floor(a, b):
        g = gap(a, b); return np.any(~np.isnan(g)) and np.nanmax(FLOOR(a) - g) > -5.5
    # ---- A: va chạm ----
    A = []
    for a in chars:
        for b in chars:
            if SPc.kind(a) == 'punct' and SPc.kind(b) == 'punct': continue
            g = gap(a, b); fl = FLOOR(a)
            if np.any(~np.isnan(g)) and np.nanmax(fl - g) > 0.5: A.append((a + b, round(float(np.nanmin(g)), 1)))
    rep['A_collisions'] = A
    # ---- B: cặp có dấu so với cặp gốc ----
    def base(c): return SPc.base(c)
    B, Bfloor = [], []
    for a in chars:
        for b in chars:
            if SPc.kind(a) == 'punct' and SPc.kind(b) == 'punct': continue
            a0, b0 = base(a), base(b)
            if (a0, b0) == (a, b) or a0 not in SP[w] or b0 not in SP[w]: continue
            d = kern(w, a, b) - kern(w, a0, b0)
            if abs(d) > 12:
                (Bfloor if at_floor(a, b) else B).append((a + b, a0 + b0, round(d)))
    rep['B_accent_dev'] = B; rep['B_accent_dev_at_floor'] = Bfloor
    # ---- C: âm tiết Việt ----
    ON = ['', 'b', 'c', 'ch', 'd', 'đ', 'g', 'gh', 'gi', 'h', 'k', 'kh', 'l', 'm', 'n', 'ng', 'ngh', 'nh', 'p', 'ph', 'qu', 'r', 's',
          't', 'th', 'tr', 'v', 'x']
    RH = ['a', 'ă', 'â', 'e', 'ê', 'i', 'o', 'ô', 'ơ', 'u', 'ư', 'y', 'ai', 'ao', 'au', 'ay', 'âu', 'ây', 'eo', 'êu', 'ia', 'iê', 'iu',
          'oa', 'oă', 'oe', 'oi', 'ôi', 'ơi', 'ua', 'uâ', 'uê', 'ui', 'uô', 'uơ', 'uy', 'ưa', 'ưi', 'ươ', 'ưu', 'yê']
    CODA = ['', 'c', 'ch', 'm', 'n', 'ng', 'nh', 'p', 't', 'i', 'o', 'u', 'y']
    TONES = ['', '́', '̀', '̉', '̃', '̣']
    def tone_on(r):                                       # đặt dấu thanh lên nguyên âm chính (đơn giản: ơ ư ê â ă ô ưu… ưu tiên)
        pri = 'ơưêâăô'
        for i, c in enumerate(r):
            if c in pri: return i
        vs = [i for i, c in enumerate(r) if c in 'aeiouy']
        return vs[-1] if len(vs) == 1 or r[-1] not in 'aeiouy' else vs[0]
    pairs = set()
    for on, rh, co in itertools.product(ON, RH, CODA):
        if co and rh[-1] in 'iouy' and co in 'iouy': continue
        for t in TONES:
            r = rh + co; i = tone_on(rh)
            r = unicodedata.normalize('NFC', r[:i + 1] + t + r[i + 1:])
            syl = on + r
            for s in (syl, syl[:1].upper() + syl[1:], syl.upper()):
                for x, y in zip(s, s[1:]): pairs.add(x + y)
    pairs = sorted(p for p in pairs if all(c in SP[w] for c in p))
    C = collections.Counter(); Cbad = []
    for p in pairs:
        a, b = p; a0, b0 = base(a), base(b)
        if (a0, b0) == (a, b): continue
        d = kern(w, a, b) - kern(w, a0, b0); fl = at_floor(a, b)
        C['tổng'] += 1
        if abs(d) <= 12: C['≤12'] += 1
        elif fl: C['>12 do sàn 26'] += 1
        else: C['>12'] += 1; Cbad.append((p, a0 + b0, round(d)))
    rep['C_vn_pairs'] = dict(C, n_pairs=len(pairs)); rep['C_vn_bad'] = Cbad
    # ---- E: cặp chữ gốc quá sát: khe nhỏ nhất sau kern < 0.55 × khe chuẩn (HH / nn / Hn) ----
    E = []
    letters = [c for c in chars if base(c) == c and SPc.kind(c) in ('caps', 'lower', 'fig')]
    refg = {}
    for a in letters:
        for b in letters:
            ra = 'n' if SPc.kind(a) == 'lower' else 'H'; rb = 'n' if SPc.kind(b) == 'lower' else 'H'
            if (ra, rb) not in refg: refg[(ra, rb)] = mingap(ra, rb)
            g = mingap(a, b)
            if g < SPc.WEDGE_SOFT*refg[(ra, rb)] - 2: E.append((a + b, round(g), kern(w, a, b)))   # sàn: 0.55 (thường) / 0.38 (cặp nêm đối nêm)
    E.sort(key=lambda t: t[1]); rep['E_tight'] = E; rep['E_ref'] = {f'{k[0]}{k[1]}': round(v) for k, v in refg.items()}
    # ---- D: cặp kinh điển ----
    D = {}
    for p in ['AV', 'AT', 'LT', 'LY', 'TA', 'VA', 'WA', 'AW', 'PA', 'FA', 'RV', 'KO', 'To', 'Ty', 'Te', 'Yo', 'P.', 'F,', 'r.', 'y.',
              'v,', '"A', '11', '17', 'Tb', 'Th', 'dT', 'fT', 'ĐO', 'Đo', 'đo', 'ươ', 'ưn', 'ơn', 'Ơn', 'ƯN', 'ĐÔ', 'Ỷe']:
        if all(c in SP[w] for c in p): D[p] = (kern(w, *p), round(mingap(*p), 1))
    rep['D_classic'] = D
    # ---- F: dấu câu × dấu câu (spacing.py không kern / không chặn va cặp này) — chỉ kiểm va chạm ----
    F = []
    for a in chars:
        if SPc.kind(a) != 'punct': continue
        for b in chars:
            if SPc.kind(b) != 'punct': continue
            g = gap(a, b)
            if np.any(~np.isnan(g)) and np.nanmin(g) < MIN_GAP - 0.5: F.append((a + b, round(float(np.nanmin(g)), 1)))
    rep['F_punct_punct'] = F
    # ---- G: phủ class: mọi ký tự có class trái / phải với đại diện có trong font (thiếu → cặp không bao giờ được kern) ----
    Gm = []
    for c in chars:
        if c in SPc.NOKERN: continue
        rc = unicodedata.normalize('NFC', SPc.rclass(c)); lc = unicodedata.normalize('NFC', SPc.lclass(c))
        if rc not in SP[w] or lc not in SP[w]: Gm.append(c)
    rep['G_no_class'] = Gm
    # ---- H: cặp kern chạm trần (−150 / −60 gạch) mà khe vẫn còn rộng hơn khe chuẩn > 60: kern bị chặn, có thể thiếu ----
    H = []
    KMIN = SPc.KMIN
    for key, v in KN[w]['class'].items():
        rc, lc = key.split('|'); a = unicodedata.normalize('NFC', rc); b = unicodedata.normalize('NFC', lc)
        if a not in PL or b not in PL: continue
        lo = SPc.KMIN_DASH if (a in '-–—=+×\u00ad' or b in '-–—=+×\u00ad') else KMIN
        if v <= lo:
            ra = 'n' if SPc.kind(a) == 'lower' else 'H'; rb = 'n' if SPc.kind(b) == 'lower' else 'H'
            g = mingap(a, b); r0 = mingap(ra, rb)
            if g - r0 > 60: H.append((a + b, v, round(g), round(r0)))
    rep['H_clamped'] = H
    rep['n_exc'] = len(KN[w]['exc']); rep['n_class'] = len(KN[w]['class'])
    return rep

def main():
    allr = {}
    sys.path.insert(0, HERE); from weights import WEIGHTS
    for w in WEIGHTS:
        r = run(w); allr[w] = r
        print(f'===== {w}: class {r["n_class"]} · ngoại lệ {r["n_exc"]}')
        print(f' A va chạm (< 26): {len(r["A_collisions"])}', r['A_collisions'][:10])
        print(f' B cặp dấu lệch cặp gốc > 12: {len(r["B_accent_dev"])} (thêm {len(r["B_accent_dev_at_floor"])} cặp chỉ vì sàn 26)')
        print('   ', r['B_accent_dev'][:25])
        print(' C âm tiết Việt:', r['C_vn_pairs']); print('   lệch:', r['C_vn_bad'][:25])
        print(' D kinh điển (kern, khe nhỏ nhất):', ' '.join(f'{k}{v[0]:+.0f}/{v[1]:.0f}' for k, v in r['D_classic'].items()))
        E = r['E_tight']; print(f' E cặp chữ gốc sát (< 0.38 khe chuẩn {r["E_ref"]}): {len(E)}', E[:40])
    # ---- I: nhất quán 4 weight: kern class Medium / SemiBold nằm gần nội suy R → B (±25), không đổi dấu ----
    from weights import TW
    keys = set().union(*[set(KN[w]['class']) for w in WEIGHTS]); I = []
    for k in sorted(keys):
        vs = {w: KN[w]['class'].get(k, 0.0) for w in WEIGHTS}
        for w in ('Medium', 'SemiBold'):
            e = vs['Regular'] + (vs['Bold'] - vs['Regular'])*TW[w]
            if abs(vs[w] - e) > 25 or (vs['Regular']*vs['Bold'] < 0 and abs(vs['Regular'] - vs['Bold']) > 30):
                I.append((k.replace('|', ''), [vs[x] for x in WEIGHTS])); break
    allr['I_cross_weight'] = I
    for w in WEIGHTS:
        r = allr[w]
        print(f' {w}: F dấu câu × dấu câu va chạm {len(r["F_punct_punct"])} {r["F_punct_punct"][:20]} · G thiếu class {r["G_no_class"]} · H kern chạm trần còn thưa {len(r["H_clamped"])} {r["H_clamped"][:15]}')
    print(f' I kern lệch giữa 4 weight: {len(I)}', I[:30])
    json.dump(allr, open(os.path.join(OUT, 'qa_kern.json'), 'w'), ensure_ascii=False, indent=0)

if __name__ == '__main__':
    main()
