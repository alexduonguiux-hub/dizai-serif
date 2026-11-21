#!/usr/bin/env python3
"""S63 — AnNam Serif variable gộp AnNam Golden (designer 21/11: "gộp 2 cái thành variable … Dùng An Nam Serif. Trục thì dùng
x-Height … kéo mượt").
    python3 tools/construct/xhgt_var.py      (sau khi build xong cả AnNam Serif và Golden)
→ fonts/variable/AnNamSerif[XHGT,wght].ttf, AnNamSerif-Italic[XHGT,wght].ttf (+ woff2)

Hai trục: wght 400–700 · XHGT "x-Height" 495 (AnNam Serif) → 535 (AnNam Golden), kéo mượt (nội suy toàn bộ: x-height, loe, nét mảnh,
khoảng cách chữ, kerning). 4 master mỗi kiểu (Serif R / B, Golden R / B) — outline cùng cấu trúc (328 chữ).
Chữ KHÁC cấu trúc giữa hai họ (t: đầu t Golden; l: chân móc t) → chữ thay thế <g>.gold, đổi qua rvrn khi XHGT ≥ 515:
  - master Golden: <g> = chữ AnNam Serif nâng x-height (y ≥ 503.4 → + 40); <g>.gold = chữ Golden;
  - master Serif:  <g> = chữ AnNam Serif; <g>.gold = chữ Golden hạ x-height (y ≥ 543.4 → − 40).
Italic: biến đổi trong toạ độ đứng (bỏ nghiêng 10° → đổi → nghiêng lại).
"""
import os, sys, math, copy, shutil, subprocess
import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SU = os.path.join(ROOT, 'out', 'construct', 'ufo'); GU = os.path.join(ROOT, 'out', 'golden', 'ufo')
BUILD = os.path.join(ROOT, 'out', 'xhgt'); VF = os.path.join(ROOT, 'fonts', 'variable')
OVT, DX = 503.4, 40.0; XH0, XH1, XSW = 495, 535, 515
# thang TRỤC người dùng 0–100 (designer 21/11 "thanh trục vẫn còn chỉ là k kéo được" trong Figma: trục tự đặt min = mặc định = 495
# thì Figma hiện thanh nhưng không kéo được) → 0 = AnNam Serif (x-height 495) … 100 = AnNam Golden (535), tuyến tính; t Golden từ 50
XU0, XU1, XUSW = 0, 100, 50
WG = {'Regular': 400, 'Medium': 500, 'SemiBold': 600, 'Bold': 700}
TAN = math.tan(math.radians(10.0))

def sig(g):
    return [tuple(p.type for p in c.points) for c in g.contours], len(g.components)

def remap(g, up, italic):
    """dời đứng phần trên x-height: up=True y ≥ OVT → +DX; up=False y ≥ OVT+DX → −DX (Italic: theo toạ độ đứng)"""
    for c in g.contours:
        for p in c.points:
            if up and p.y >= OVT - 0.01: dy = DX
            elif not up and p.y >= OVT + DX - 0.01: dy = -DX
            else: continue
            p.y += dy
            if italic: p.x += dy*TAN

def build(tag):
    it = bool(tag)
    S = {w: ufoLib2.Font.open(os.path.join(SU, f'AnNamSerif{tag}-{w}.ufo')) for w in ('Regular', 'Bold')}
    G = {w: ufoLib2.Font.open(os.path.join(GU, f'AnNamGolden{tag}-{w}.ufo')) for w in ('Regular', 'Bold')}
    names = [g.name for g in S['Regular']]
    bad = [n for n in names if n in G['Regular'] and any(sig(S[w][n]) != sig(G[w][n]) for w in ('Regular', 'Bold'))]
    print(tag or '-Roman', 'chữ khác cấu trúc:', bad)
    for n in bad:
        alt = n + '.gold'
        for w in ('Regular', 'Bold'):
            gs, gg = S[w][n], G[w][n]
            a_g = G[w].newGlyph(alt); a_g.width = gg.width; gg.drawPoints(a_g.getPointPen())
            a_s = S[w].newGlyph(alt); a_s.width = gg.width; gg.drawPoints(a_s.getPointPen()); remap(a_s, False, it)
            nb = copy.deepcopy(gs); gg.clearContours(); gg.clearComponents(); nb.drawPoints(gg.getPointPen())
            remap(gg, True, it); gg.width = gs.width
            for f in (S[w], G[w]):
                for gname, mem in list(f.groups.items()):
                    if n in mem and alt not in mem: f.groups[gname] = list(mem) + [alt]
    left = [n for n in names if n in G['Regular'] and any(sig(S[w][n]) != sig(G[w][n]) for w in ('Regular', 'Bold'))]
    assert not left, left
    if S['Regular'].groups != G['Regular'].groups:                      # nhóm kerning phải giống nhau giữa các master
        print('  nhóm kerning khác giữa hai họ → dùng nhóm AnNam Serif cho mọi master')
        for w in ('Regular', 'Bold'): G[w].groups.clear(); G[w].groups.update(copy.deepcopy(S['Regular'].groups))
    os.makedirs(BUILD, exist_ok=True)
    ds = DesignSpaceDocument()
    for name, t, lo, df, hi in (('Weight', 'wght', 400, 400, 700), ('x-Height', 'XHGT', XU0, XU0, XU1)):
        ax = AxisDescriptor(); ax.name, ax.tag, ax.minimum, ax.default, ax.maximum = name, t, lo, df, hi; ds.addAxis(ax)
    for fam, F, xh in (('Serif', S, XU0), ('Golden', G, XU1)):
        for w in ('Regular', 'Bold'):
            p = os.path.join(BUILD, f'{fam}{tag}-{w}.ufo')
            if os.path.exists(p): shutil.rmtree(p)
            F[w].info.familyName = 'AnNam Serif'; F[w].save(p)
            s = SourceDescriptor(); s.path = p; s.location = {'Weight': WG[w], 'x-Height': xh}; s.familyName = 'AnNam Serif'
            s.styleName = f'{"" if fam == "Serif" else "Golden "}{w}'; ds.addSource(s)
    for fam, xh in (('', XU0), ('Golden ', XU1)):
        for w, v in WG.items():
            ins = InstanceDescriptor(); ins.familyName = 'AnNam Serif'
            st = (w if w != 'Regular' or fam == '' else '').strip()
            sty = f'{fam}{w}'.strip()
            if it: sty = (sty.replace('Regular', '').strip() + ' Italic').strip()
            ins.styleName = sty; ins.location = {'Weight': v, 'x-Height': xh}
            ins.postScriptFontName = 'AnNamSerif-' + sty.replace(' ', ''); ds.addInstance(ins)
    r = RuleDescriptor(); r.name = 'golden-forms'; r.conditionSets = [[dict(name='x-Height', minimum=XUSW, maximum=XU1)]]
    r.subs = [(n, n + '.gold') for n in bad]; ds.addRule(r)
    ds.rulesProcessingLast = True                                      # thay chữ SAU chữ ghép (rclt): t f → t_f → t_f.gold
    dsp = os.path.join(BUILD, f'AnNamSerif{tag}-XHGT.designspace'); ds.write(dsp)
    out = os.path.join(BUILD, 'vf'); shutil.rmtree(out, ignore_errors=True)
    subprocess.run(['fontmake', '-m', dsp, '-o', 'variable', '--output-dir', out, '--flatten-components'], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    src = [f for f in os.listdir(out) if f.endswith('.ttf')][0]
    dst = os.path.join(VF, f'AnNamSerif{tag}[XHGT,wght].ttf'); os.makedirs(VF, exist_ok=True); shutil.move(os.path.join(out, src), dst)
    finish(dst, it)
    return dst

def finish(dst, it):
    from fontTools.ttLib import TTFont
    from fontTools.otlLib.builder import buildStatTable
    f = TTFont(dst)
    wv = [dict(value=v, name=n) for n, v in WG.items()]; wv[0].update(flags=0x2, linkedValue=700)
    xv = [dict(value=XU0, name='Serif', flags=0x2), dict(value=XU1, name='Golden')]
    iv = [dict(value=1, name='Italic')] if it else [dict(value=0, name='Roman', flags=0x2, linkedValue=1)]
    buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='XHGT', name='x-Height', values=xv),
                       dict(tag='ital', name='Italic', values=iv)])
    nm = f['name']; ps = 'AnNamSerifXH' + ('Italic' if it else '')
    for rec in list(nm.names):                                      # tên PostScript riêng (không trùng AnNamSerif[wght])
        if rec.nameID == 6: rec.string = rec.toUnicode().replace('AnNamSerif-', 'AnNamSerifXH-')
    nm.setName(ps, 25, 3, 1, 0x409)
    for inst in f['fvar'].instances:
        if inst.postscriptNameID != 0xFFFF:
            r = nm.getName(inst.postscriptNameID, 3, 1, 0x409)
            if r: nm.setName(r.toUnicode().replace('AnNamSerif-', 'AnNamSerifXH-'), inst.postscriptNameID, 3, 1, 0x409)
    nm.names = [n for n in nm.names if n.platformID != 1]
    import re as _re
    V = _re.search(r'^VERSION = \((\d+), (\d+)\)', open(os.path.join(HERE, 'export_font.py')).read(), _re.M)
    ver = f'{int(V.group(1))}.{int(V.group(2)):03d}'; f['head'].fontRevision = float(ver)          # version = export_font.VERSION
    for rec in list(nm.names):
        if rec.nameID == 5: rec.string = _re.sub(r'\d+\.\d{3}', ver, rec.toUnicode(), count=1)
        if rec.nameID == 3: rec.string = f"{ver};{f['OS/2'].achVendID.strip() or 'NONE'};{nm.getDebugName(6)}-VF"
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'release')); import license_meta as LM; LM.apply(f)
    f.save(dst)
    w2 = os.path.join(ROOT, 'fonts', 'woff2', 'variable'); os.makedirs(w2, exist_ok=True)
    f.flavor = 'woff2'; f.save(os.path.join(w2, os.path.basename(dst).replace('.ttf', '.woff2')))

def combined3():
    """designer 21/11 "dựng chung 1 bản cho serif": MỘT file đủ ba trục — wght 400–700 · XHGT 495–535 · slnt 0 … −10° (Italic = Roman
    nghiêng 10° nên 8 master cùng cấu trúc). → AnNamSerif[XHGT,slnt,wght].ttf (+ woff2)"""
    from fontTools.ttLib import TTFont
    from fontTools.otlLib.builder import buildStatTable
    ds = DesignSpaceDocument()
    for name, t, lo, df, hi in (('Weight', 'wght', 400, 400, 700), ('x-Height', 'XHGT', XU0, XU0, XU1), ('Slant', 'slnt', -10, 0, 0)):
        ax = AxisDescriptor(); ax.name, ax.tag, ax.minimum, ax.default, ax.maximum = name, t, lo, df, hi; ds.addAxis(ax)
    for fam, xh in (('Serif', XU0), ('Golden', XU1)):
        for tag, sl in (('', 0), ('-Italic', -10)):
            for w in ('Regular', 'Bold'):
                s = SourceDescriptor(); s.path = os.path.join(BUILD, f'{fam}{tag}-{w}.ufo'); s.familyName = 'AnNam Serif'
                s.location = {'Weight': WG[w], 'x-Height': xh, 'Slant': sl}
                s.styleName = (f'{"" if fam == "Serif" else "Golden "}{w}' + (' Italic' if tag else '')).replace('Regular Italic', 'Italic')
                ds.addSource(s)
    for fam, xh in (('', XU0), ('Golden ', XU1)):
        for tag, sl in (('', 0), (' Italic', -10)):
            for w, v in WG.items():
                sty = f'{fam}{w}{tag}'.replace('Regular Italic', 'Italic').strip()
                ins = InstanceDescriptor(); ins.familyName = 'AnNam Serif'; ins.styleName = sty
                ins.location = {'Weight': v, 'x-Height': xh, 'Slant': sl}; ins.postScriptFontName = 'AnNamSerif-' + sty.replace(' ', '')
                ds.addInstance(ins)
    bad = sorted({g.name[:-5] for g in ufoLib2.Font.open(os.path.join(BUILD, 'Serif-Regular.ufo')) if g.name.endswith('.gold')})
    r = RuleDescriptor(); r.name = 'golden-forms'; r.conditionSets = [[dict(name='x-Height', minimum=XUSW, maximum=XU1)]]
    r.subs = [(n, n + '.gold') for n in bad]; ds.addRule(r); ds.rulesProcessingLast = True
    dsp = os.path.join(BUILD, 'AnNamSerif-XHGT-slnt.designspace'); ds.write(dsp)
    out = os.path.join(BUILD, 'vf3'); shutil.rmtree(out, ignore_errors=True)
    subprocess.run(['fontmake', '-m', dsp, '-o', 'variable', '--output-dir', out, '--flatten-components'], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    src = [f for f in os.listdir(out) if f.endswith('.ttf')][0]
    dst = os.path.join(VF, 'AnNamSerif[XHGT,slnt,wght].ttf'); shutil.move(os.path.join(out, src), dst)
    for old_ in ('AnNamSerifVF[XHGT,slnt,wght].ttf',):
        for d_ in (VF, os.path.join(ROOT, 'fonts', 'woff2', 'variable')):
            for e_ in ('.ttf', '.woff2'):
                q_ = os.path.join(d_, old_.replace('.ttf', e_))
                if os.path.exists(q_): os.remove(q_)
    f = TTFont(dst)
    wv = [dict(value=v, name=n) for n, v in WG.items()]; wv[0].update(flags=0x2, linkedValue=700)
    xv = [dict(value=XU0, name='Serif', flags=0x2), dict(value=XU1, name='Golden')]
    sv = [dict(value=0, name='Upright', flags=0x2), dict(value=-10, name='Italic')]
    buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='XHGT', name='x-Height', values=xv),
                       dict(tag='slnt', name='Slant', values=sv)])
    nm = f['name']
    # tên họ "AnNam Serif" (designer 21/11 "giữ An Nam Serif thôi" — bỏ họ riêng "AnNam Serif VF" của 0.930); chỉ tên PostScript
    # riêng AnNamSerifAll-… để không trùng bản tĩnh. Máy dùng file này nên cài MỘT MÌNH nó (README).
    for rec in list(nm.names):
        if rec.nameID == 6: rec.string = rec.toUnicode().replace('AnNamSerif-', 'AnNamSerifAll-')
    nm.setName('AnNamSerifAll', 25, 3, 1, 0x409)
    for inst in f['fvar'].instances:
        if inst.postscriptNameID != 0xFFFF:
            rr = nm.getName(inst.postscriptNameID, 3, 1, 0x409)
            if rr: nm.setName(rr.toUnicode().replace('AnNamSerif-', 'AnNamSerifAll-'), inst.postscriptNameID, 3, 1, 0x409)
    nm.names = [n for n in nm.names if n.platformID != 1]
    import re as _re
    V = _re.search(r'^VERSION = \((\d+), (\d+)\)', open(os.path.join(HERE, 'export_font.py')).read(), _re.M)
    ver = f'{int(V.group(1))}.{int(V.group(2)):03d}'; f['head'].fontRevision = float(ver)
    for rec in list(nm.names):
        if rec.nameID == 5: rec.string = _re.sub(r'\d+\.\d{3}', ver, rec.toUnicode(), count=1)
        if rec.nameID == 3: rec.string = f"{ver};{f['OS/2'].achVendID.strip() or 'NONE'};{nm.getDebugName(6)}-VF"
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'release')); import license_meta as LM; LM.apply(f)
    f.save(dst)
    w2 = os.path.join(ROOT, 'fonts', 'woff2', 'variable'); f.flavor = 'woff2'; f.save(os.path.join(w2, os.path.basename(dst).replace('.ttf', '.woff2')))
    return dst

if __name__ == '__main__':
    for tag in ('', '-Italic'): print('→', build(tag))
    print('→', combined3())
