#!/usr/bin/env python3
"""Trục HAIR — nét mảnh (designer 26/11 "thêm thanh slide variable điều khiển nét mỏng của tất cả các glyph").
Master nét mảnh = CÙNG hệ luật Golden chạy với chuẩn nét mảnh nhỏ hơn (golden.py DIZAI_HAIR=16 → out/golden_hair, compat_masters,
post_compat). Glyph nào lệch cấu trúc điểm so với master mặc định thì giữ outline mặc định (không đổi theo trục).
Xuất: fonts/golden/variable/AnNamGolden[HAIR,wght].ttf (+ Italic) — trục Weight 400–700 × Hairline 16–34 (mặc định 34).
    (chạy sau export_font.py, cùng biến môi trường DIZAI_* của golden/run.sh; DIZAI_HAIR_OUT = thư mục outline nét mảnh)"""
import os, sys, json, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import export_font as EF
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor

HAIR_MIN, HAIR_DEF = float(os.environ.get('DIZAI_HAIR', 16)), 34.0
HOUT = os.environ.get('DIZAI_HAIR_OUT') or os.path.join(EF.ROOT, 'out', 'golden_hair')

def sig(d): return [[s[0] for s in c] for c in EF.parse(d)]
def gsig(g): return [[(p.type or 'o') for p in c.points] for c in g.contours]

def main():
    H = json.load(open(os.path.join(HOUT, 'outlines.json')))
    VF = os.path.join(EF.FONTS, 'variable'); os.makedirs(VF, exist_ok=True)
    EF.YMAX, EF.YMIN = EF._ybounds()
    for ang, tag in ((0, ''), (EF.ITALIC_ANGLE, '-Italic')):
        EF.use('Italic' if tag else 'Roman'); D0 = EF.O
        M = dict(D0); keep = set()
        for c in EF.CHARS:
            ks = [f'{c}-{w}' for w in ('Regular', 'Bold')]
            if all(k in D0 and k in H and sig(D0[k]) == sig(H[k]) for k in ks):
                for k in ks: M[k] = H[k]
            elif all(k in D0 for k in ks): keep.add(c)
        EF.O = M; EF._PAIR.clear(); EF._STEM.clear()
        FL = {}
        for c in EF.CHARS:
            if f'{c}-Regular' in M:
                fl = EF.flips(EF.parse(M[f'{c}-Regular']))
                if fl: FL[c] = fl
        groups, ks = EF.kerning_data()
        MS = {w: EF.master(w, ang, FL, groups, ks[w]) for w in ('Regular', 'Bold')}
        EF.pair_fix(MS['Regular'], MS['Bold'])
        import ufoLib2
        fixed = 0
        for w in ('Regular', 'Bold'):
            base = ufoLib2.Font.open(os.path.join(EF.BUILD, f'{EF.PS}{tag}-{w}.ufo'))
            for g in MS[w]:
                if g.name in base and gsig(base[g.name]) != gsig(g):       # lệch cấu trúc với master mặc định → giữ mặc định
                    g.clearContours(); base[g.name].drawPoints(g.getPointPen()); fixed += 1
            p = os.path.join(EF.BUILD, f'{EF.PS}{tag}-{w}-Hair.ufo')
            if os.path.exists(p): shutil.rmtree(p)
            MS[w].save(p)
        print(f'HAIR{tag or " Roman"}: giữ mặc định {len(keep)} chữ (lệch cấu trúc: {"".join(sorted(keep))}) · sửa sau dựng {fixed}')
        ds = DesignSpaceDocument()
        for name, t_, lo, df, hi in (('Weight', 'wght', 400, 400, 700), ('Hairline', 'HAIR', HAIR_MIN, HAIR_DEF, HAIR_DEF)):
            ax = AxisDescriptor(); ax.name, ax.tag, ax.minimum, ax.default, ax.maximum = name, t_, lo, df, hi; ds.addAxis(ax)
        for w in ('Regular', 'Bold'):
            for hair, suf in ((HAIR_DEF, ''), (HAIR_MIN, '-Hair')):
                s = SourceDescriptor(); s.path = os.path.join(EF.BUILD, f'{EF.PS}{tag}-{w}{suf}.ufo')
                s.location = {'Weight': EF.WGHT[w], 'Hairline': hair}; s.familyName = EF.FAMILY; ds.addSource(s)
        for w in EF.WGHT:
            ins = InstanceDescriptor(); ins.familyName = EF.FAMILY
            ins.styleName = (w + ' Italic' if w != 'Regular' else 'Italic') if ang else w
            ins.location = {'Weight': EF.WGHT[w], 'Hairline': HAIR_DEF}
            ins.postScriptFontName = f'{EF.PS}Hair-' + (w + 'Italic' if ang and w != 'Regular' else ('Italic' if ang else w))
            ds.addInstance(ins)
        dsp = os.path.join(EF.BUILD, f'{EF.PS}{tag}-Hair.designspace'); ds.write(dsp)
        before = set(os.listdir(VF))
        subprocess.run(['fontmake', '-m', dsp, '-o', 'variable', '--output-dir', VF, '--flatten-components'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        new = [f_ for f_ in os.listdir(VF) if f_ not in before][0]
        dst = os.path.join(VF, f'{EF.PS}{tag}[HAIR,wght].ttf'); os.replace(os.path.join(VF, new), dst)
        from fontTools.ttLib import TTFont
        from fontTools.otlLib.builder import buildStatTable
        f = TTFont(dst)
        wv = [dict(value=v, name=n) for n, v in EF.WGHT.items()]; wv[0].update(flags=0x2, linkedValue=700)
        hv = [dict(value=HAIR_DEF, name='Normal', flags=0x2), dict(value=HAIR_MIN, name='Hairline')]
        buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='HAIR', name='Hairline', values=hv)])
        nm = f['name']                                                # tên PostScript riêng (không trùng file [wght])
        for rec in list(nm.names):
            if rec.nameID == 6 and 'Hair' not in rec.toUnicode(): rec.string = rec.toUnicode().replace(EF.PS + '-', EF.PS + 'Hair-')
        nm.setName(EF.PS + 'Hair', 25, 3, 1, 0x409)
        nm.names = [n for n in nm.names if n.platformID != 1]
        f.save(dst)
        W2 = os.path.join(EF.FONTS, 'woff2', 'variable'); os.makedirs(W2, exist_ok=True)
        t = TTFont(dst); t.flavor = 'woff2'; t.save(os.path.join(W2, os.path.basename(dst).rsplit('.', 1)[0] + '.woff2'))
        print('  ', os.path.relpath(dst, EF.ROOT), os.path.getsize(dst)//1024, 'KB')

if __name__ == '__main__':
    main()
