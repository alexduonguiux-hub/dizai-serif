#!/usr/bin/env python3
"""QA trên CHÍNH FILE FONT (sau export_font.py), shape bằng HarfBuzz:
    python3 tools/construct/qa_font.py
  1. advance từng glyph = spacing.json (mọi weight, variable ở wght 400/500/600/700 + bản tĩnh)
  2. kerning mọi cặp chữ / số / dấu câu = kerning.json (lệch ≤ 1 u do làm tròn biến thiên)
  3. NFD = NFC: chuỗi chữ gốc + dấu tổ hợp ra đúng glyph dựng sẵn (ccmp)
  4. outline: hộp bao glyph của instance variable = outlines.json (lệch ≤ 1 u); Italic = Roman nghiêng 10° quanh ½ x-height
  5. bản tĩnh = variable (advance + kerning)
"""
import json, os, sys, math, unicodedata, itertools
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import spacing as SPc
import export_font as E
ROOT = os.path.join(HERE, '..', '..'); F = os.path.join(ROOT, 'fonts')
WG = E.WGHT

def face(path, wght=None):
    blob = hb.Blob.from_file_path(path); fc = hb.Face(blob); ft = hb.Font(fc)
    if wght: ft.set_variations({'wght': wght})
    return ft

def shape(ft, s):
    b = hb.Buffer(); b.add_str(s); b.guess_segment_properties(); hb.shape(ft, b, {'kern': True, 'liga': False})
    return b.glyph_infos, b.glyph_positions

def kern_exp(w, a, b):
    v = KN[w]['exc'].get(f'{a}|{b}')
    return KN[w]['class'].get(f'{SPc.rclass(a)}|{SPc.lclass(b)}', 0.0) if v is None else v

def check(ft, w, tag, rep, pairs=True):
    chars = [c for c in E.CHARS if c not in '\xa0\xad']                 # U+00AD: HarfBuzz ẩn (đúng chuẩn)
    bad_adv = [c for c in chars if abs(shape(ft, c)[1][0].x_advance - SP[w][c]['adv']) > 1.0]
    bad_k = []
    if pairs:
        cs = [c for c in chars if SPc.kind(c) != 'mark' and c != ' ']
        for a, b in itertools.product(cs, cs):
            if SPc.kind(a) == 'punct' and SPc.kind(b) == 'punct': continue
            _, pos = shape(ft, a + b); k = pos[0].x_advance - SP[w][a]['adv']
            if abs(k - kern_exp(w, a, b)) > 1.01: bad_k.append((a + b, k, kern_exp(w, a, b)))
    rep[tag] = dict(adv=len(bad_adv), kern=len(bad_k), ex_adv=bad_adv[:10], ex_kern=bad_k[:10])
    print(f'  {tag:34} advance lệch {len(bad_adv):3} · kerning lệch {len(bad_k):4}', bad_adv[:5], bad_k[:5])

def nfd(ft, tag, rep):
    bad = []
    for c in E.CHARS:
        d = unicodedata.normalize('NFD', c)
        if len(d) < 2 or not all(x in SP['Regular'] for x in d): continue
        g1 = [i.codepoint for i in shape(ft, c)[0]]; g2 = [i.codepoint for i in shape(ft, d)[0]]
        if g1 != g2: bad.append(c)
    rep[tag + ' NFD'] = bad; print(f'  {tag:34} NFD ≠ NFC: {len(bad)}', bad[:10])

def outlines(vf, w, ang, tag, rep):
    from fontTools.varLib.instancer import instantiateVariableFont
    f = instantiateVariableFont(TTFont(vf), {'wght': WG[w]}); gs = f.getGlyphSet(); bad = []
    t = math.tan(math.radians(ang))
    for c in E.CHARS:
        k = f'{c}-{w}'
        if k not in O: continue
        cs = E.parse(O[k]); dx = SP[w][c]['dx']
        P = [E.skew((p[0] + dx, p[1]), ang) if ang else (p[0] + dx, p[1]) for co in cs for p in E.poly(co, 24)]
        xb = (min(p[0] for p in P), min(p[1] for p in P), max(p[0] for p in P), max(p[1] for p in P))
        bp = BoundsPen(gs); gs[E.gname(c)].draw(bp)
        if bp.bounds is None or max(abs(u - v) for u, v in zip(xb, bp.bounds)) > 1.6: bad.append((c, [round(v) for v in xb], bp.bounds))
    rep[tag + ' outline'] = len(bad); print(f'  {tag:34} hộp bao lệch > 1.6 u: {len(bad)}', bad[:4])

def main():
    rep = {}
    global SP, KN, O
    for ital, sfx in ((0, ''), (E.ITALIC_ANGLE, '-Italic')):
        E.use('Italic' if sfx else 'Roman'); SP, KN, O = E.SP, E.KN, E.O
        vf = os.path.join(F, 'variable', f'{E.PS}{sfx}[wght].ttf'); print('==', os.path.basename(vf))
        for w in WG:
            check(face(vf, WG[w]), w, f'VF{sfx} wght {WG[w]}', rep)
            outlines(vf, w, ital, f'VF{sfx} {w}', rep)
        nfd(face(vf, 400), f'VF{sfx}', rep)
        for w in WG:
            st = w + ('Italic' if sfx and w != 'Regular' else '') if sfx else w
            if sfx and w == 'Regular': st = 'Italic'
            for fmt in ('otf', 'ttf'):
                check(face(os.path.join(F, fmt, f'{E.PS}-{st}.{fmt}')), w, f'{fmt} {st}', rep)
    json.dump(rep, open(os.path.join(E.OUT, 'qa_font.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
