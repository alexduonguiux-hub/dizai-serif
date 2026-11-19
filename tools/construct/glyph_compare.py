#!/usr/bin/env python3
"""Trang so sánh toàn bộ glyph (designer 19/11: "cho preview html tất cả glyph để so sánh").
    python3 tools/construct/glyph_compare.py [commit_cũ]   → docs/preview/glyph-compare.html + docs/preview/cmp/{old,new}/*.woff2
Bản cũ mặc định = commit phát hành v0.916 (bộ zip đã gửi); font woff2 hai bản chép vào docs/preview/cmp/. Glyph "đổi" = outline hoặc advance khác nhau giữa hai file OTF."""
import io, json, os, subprocess, sys, unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
OLD = sys.argv[1] if len(sys.argv) > 1 else 'ed3182d'
STY = ['Regular', 'Medium', 'SemiBold', 'Bold', 'Italic', 'MediumItalic', 'SemiBoldItalic', 'BoldItalic']
sys.path[:0] = [HERE, os.path.join(HERE, 'ref')]
import spacing as SPc
SP = json.load(open(os.path.join(ROOT, 'out', 'construct', 'spacing.json')))
LIG = {'ﬀ': 'ff', '': 'ft', '': 'tf', '': 'tt'}
chars = sorted(SP['Regular'], key=ord)
import shutil
for s_ in STY:
    os.makedirs(os.path.join(ROOT, 'docs', 'preview', 'cmp', 'new'), exist_ok=True); os.makedirs(os.path.join(ROOT, 'docs', 'preview', 'cmp', 'old'), exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'fonts', 'woff2', 'ttf', f'AnNamSerif-{s_}.woff2'), os.path.join(ROOT, 'docs', 'preview', 'cmp', 'new'))
    b_ = subprocess.run(['git', 'show', f'{OLD}:fonts/woff2/ttf/AnNamSerif-{s_}.woff2'], cwd=ROOT, capture_output=True).stdout
    open(os.path.join(ROOT, 'docs', 'preview', 'cmp', 'old', f'AnNamSerif-{s_}.woff2'), 'wb').write(b_)

def font(path=None, blob=None):
    return TTFont(io.BytesIO(blob)) if blob is not None else TTFont(path)
def outlines(f):
    gs = f.getGlyphSet(); hm = f['hmtx']; out = {}
    for g in f.getGlyphOrder():
        p = RecordingPen(); gs[g].draw(p); out[g] = (hm[g][0], repr(p.value))
    return out
cmap_names = {}
changed = {}; advs = {}
for s in STY:
    newf = font(os.path.join(ROOT, 'fonts', 'otf', f'AnNamSerif-{s}.otf'))
    blob = subprocess.run(['git', 'show', f'{OLD}:fonts/otf/AnNamSerif-{s}.otf'], cwd=ROOT, capture_output=True).stdout
    oldf = font(blob=blob) if blob else None
    N = outlines(newf); Oo = outlines(oldf) if oldf else {}
    cm = newf.getBestCmap(); ocm = oldf.getBestCmap() if oldf else {}
    lign = {'ﬀ': 'f_f', '': 'f_t', '': 't_f', '': 't_t'}
    ch = []; ad = {}
    for c in chars:
        gn = lign.get(c) or cm.get(ord(c))
        if gn is None: continue
        cmap_names[c] = gn
        go = lign.get(c) if c in lign else ocm.get(ord(c))
        old = Oo.get(go) if go else None
        if old is None: ch.append(c); ad[c] = [None, N[gn][0]]
        elif old != N[gn]:
            ch.append(c); ad[c] = [old[0], N[gn][0]]
    changed[s] = ''.join(ch); advs[s] = ad

def group(c):
    if c in LIG: return 'lig'
    k = SPc.kind(c)
    if k == 'mark': return 'mark'
    if k == 'fig': return 'fig'
    if k == 'caps': return 'caps' if c.isascii() else 'capsx'
    if k == 'lower': return 'lower' if c.isascii() else 'lowerx'
    return 'punct'
G = {}
for c in chars:
    if c in ('\xa0',): continue
    G.setdefault(group(c), []).append(c)
data = dict(groups=[[k, ''.join(G.get(k, []))] for k in ('caps', 'lower', 'fig', 'capsx', 'lowerx', 'lig', 'punct', 'mark')],
            lig=LIG, names={c: cmap_names.get(c, '') for c in chars}, changed=changed, adv=advs,
            old_label='v0.916', new_label='bản hiện tại')
tpl = open(os.path.join(HERE, 'glyph_compare_template.html'), encoding='utf-8').read()
ff = '\n'.join('@font-face { font-family: "%s-%s"; src: url("cmp/%s/AnNamSerif-%s.woff2") format("woff2"); font-display: block }' % (p, s, d, s)
               for p, d in (('N', 'new'), ('O', 'old')) for s in STY)
out = tpl.replace('/*DATA*/null', json.dumps(data, ensure_ascii=False)).replace('/*FONTFACES*/', ff)
open(os.path.join(ROOT, 'docs', 'preview', 'glyph-compare.html'), 'w', encoding='utf-8').write(out)
print('glyph:', len(chars), '· đổi:', {s: len(v) for s, v in changed.items()})
