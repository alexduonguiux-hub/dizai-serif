#!/usr/bin/env python3
"""Xuất font: UFO master Regular + Bold (Roman và Italic) → designspace → variable TTF (wght 400–700) + bản tĩnh OTF / TTF.
    python3 tools/construct/export_font.py      (sau spacing.py)  → fonts/

Designer 05/11: "làm bản variable luôn nhé, thêm cả Italic".
- Master: outlines.json (compat_masters.py đã đưa Regular / Bold về cùng cấu trúc); Medium 500 / SemiBold 600 là instance
  (TW 1/3, 2/3 → đúng bản tĩnh đã dựng).
- Chiều contour: chuẩn PostScript (ngoài ngược chiều kim đồng hồ) theo lồng nhau của master Regular, đảo cùng chỉ số ở Bold.
- Kerning: class (spacing.py) → groups public.kern1 / kern2; ngoại lệ chống va ghi tường minh ở CẢ HAI master (thiếu thì lấy giá
  trị class) để nội suy đúng.
- ccmp: chuỗi NFD (chữ gốc + dấu tổ hợp) → chữ dựng sẵn.
- Italic (I1): nghiêng 10° quanh y = ½ x-height (cách của chữ glyphic loe nét: Optima / Palatino Sans Italic là roman nghiêng
  có hệ thống). Mọi glyph nghiêng như nhau quanh cùng một đường → khe giữa hai chữ ở mọi cao độ giữ nguyên → spacing và kerning
  của Roman đúng tuyệt đối cho Italic.
- Bản tĩnh tạo bằng instancer từ chính file variable → trùng khít bản variable.
"""
import json, math, os, re, sys, unicodedata, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ufoLib2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'release')); import license_meta as LM
from fontTools.agl import UV2AGL
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
import spacing as SPc
ROOT = os.path.join(HERE, '..', '..'); OUT = os.path.join(ROOT, 'out', 'construct'); FONTS = os.path.join(ROOT, 'fonts')
BUILD = os.path.join(OUT, 'ufo')
FAMILY, PS = 'AnNam Serif', 'AnNamSerif'   # designer 06/11: AnNam → thêm chữ phân biệt với BT Annam Neue (BeauType)
VENDOR = 'DZAI'                                # Đìzai Studio (4 ký tự theo chuẩn OpenType — 'DIZAI' 5 ký tự không dùng được) — nên đăng ký với Microsoft (mstwsite@microsoft.com)
#          # designer 06/11 "Đổi tên Font thành AnNam" (trước: Dizai Serif / DizaiSerif)
VERSION = (0, 900)
ITALIC_ANGLE = 10.0
WGHT = {'Regular': 400, 'Medium': 500, 'SemiBold': 600, 'Bold': 700}

OUTI = os.path.join(ROOT, 'out', 'construct_italic')            # Italic I2 (italic.py): thiết kế italic đứng, nghiêng khi xuất
def use(style):
    """nạp outline / spacing / kerning của Roman hoặc Italic (I2 nếu có out/construct_italic, không thì Roman nghiêng — I1)"""
    global O, SP, KN
    d = OUTI if style == 'Italic' and os.path.exists(os.path.join(OUTI, 'kerning.json')) else OUT
    O = json.load(open(os.path.join(d, 'outlines.json'))); SP = json.load(open(os.path.join(d, 'spacing.json')))
    KN = json.load(open(os.path.join(d, 'kerning.json')))
    return d
use('Roman')
CHARS = sorted(SP['Regular'], key=ord)

def gname(c):
    u = ord(c)
    if c == ' ': return 'space'
    return UV2AGL.get(u) or ('uni%04X' % u)

def parse(d):
    """'M x y L x y C … Z' → [[('M', p), ('L', p), ('C', p1, p2, p3)…]]"""
    toks = re.findall(r'[MLCZ]|-?\d+(?:\.\d+)?', d); cs = []; cur = None; i = 0
    while i < len(toks):
        t = toks[i]
        if t == 'M': cur = [('M', (float(toks[i+1]), float(toks[i+2])))]; i += 3
        elif t == 'L': cur.append(('L', (float(toks[i+1]), float(toks[i+2])))); i += 3
        elif t == 'C': cur.append(('C',) + tuple((float(toks[i+1+2*k]), float(toks[i+2+2*k])) for k in range(3))); i += 7
        elif t == 'Z': cs.append(cur); cur = None; i += 1
        else: raise ValueError(t)
    return cs

def poly(c, n=8):
    P = []; p = None
    for s in c:
        if s[0] in 'ML': P.append(s[1]); p = s[1]
        else:
            a, b, e = s[1:]
            for k in range(1, n + 1):
                t = k/n; u = 1 - t
                P.append((u**3*p[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t**3*e[0], u**3*p[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t**3*e[1]))
            p = e
    return P

def area(P): return 0.5*sum(P[i-1][0]*P[i][1] - P[i][0]*P[i-1][1] for i in range(len(P)))

def inside(pt, P):
    x, y = pt; c = False
    for i in range(len(P)):
        (x0, y0), (x1, y1) = P[i-1], P[i]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0)*(x1 - x0)/(y1 - y0): c = not c
    return c

def flips(cs):
    """chỉ số contour cần đảo: độ sâu lồng chẵn → ngược chiều kim (diện tích dương), lẻ → cùng chiều"""
    Ps = [poly(c) for c in cs]; out = []
    for i, P in enumerate(Ps):
        probe = P[0]
        # điểm thử: dời nhẹ vào trong contour để tránh nằm trên biên contour khác
        depth = sum(1 for j, Q in enumerate(Ps) if j != i and abs(area(Q)) > abs(area(P)) and inside(probe, Q))
        want = 1 if depth % 2 == 0 else -1
        if (area(P) > 0) != (want > 0): out.append(i)
    return out

def reverse(c):
    """đảo chiều contour đóng, giữ điểm đầu"""
    pts = [c[0][1]]; segs = []
    for s in c[1:]:
        segs.append(s)
    # chuỗi nút: n0 → s1 → n1 …; contour đóng: nút cuối nối thẳng về n0 nếu khác
    nodes = [c[0][1]] + [s[-1] for s in segs]
    closing = None
    if nodes[-1] != nodes[0]: segs.append(('L', nodes[0])); nodes.append(nodes[0])
    rs = []
    for k in range(len(segs) - 1, -1, -1):
        s = segs[k]; start = nodes[k]
        rs.append(('L', start) if s[0] == 'L' else ('C', s[2], s[1], start))
    out = [('M', nodes[0])] + rs
    if out[-1][0] == 'L' and out[-1][1] == nodes[0]: out.pop()
    return out

def skew(p, a):
    t = math.tan(math.radians(a)); yc = SPc.XH/2
    return (p[0] + (p[1] - yc)*t, p[1])

def draw(glyph, cs, dx, ang):
    pen = glyph.getPen()
    T = (lambda p: skew((p[0] + dx, p[1]), ang)) if ang else (lambda p: (p[0] + dx, p[1]))
    for c in cs:
        pen.moveTo(T(c[0][1])); cur = c[0][1]
        for s in c[1:]:
            if all(math.dist(q, cur) < 0.01 for q in s[1:]): continue      # đoạn suy biến (độ dài 0) — fontbakery 06/11, '2' Bold
            if s[0] == 'L': pen.lineTo(T(s[1]))
            else: pen.curveTo(T(s[1]), T(s[2]), T(s[3]))
            cur = s[-1]
        pen.closePath()

def master(w, ang, FL, groups, kern):
    f = ufoLib2.Font()
    style = w + (' Italic' if ang else '') if w != 'Regular' or not ang else 'Italic'
    i = f.info
    i.familyName = FAMILY; i.styleName = style
    i.versionMajor, i.versionMinor = VERSION
    i.unitsPerEm = 1000; i.capHeight = 700; i.xHeight = int(SPc.XH)
    # S4 vertical metrics MỘT bộ cho cả family: typo = hhea (USE_TYPO_METRICS), dòng 1.2 em; usWin bao chồng dấu cao / thấp nhất
    i.ascender = 760; i.descender = -240
    i.openTypeOS2TypoAscender = i.openTypeHheaAscender = 960; i.openTypeOS2TypoDescender = i.openTypeHheaDescender = -240
    i.openTypeOS2TypoLineGap = i.openTypeHheaLineGap = 0
    i.openTypeOS2WinAscent = YMAX + 10; i.openTypeOS2WinDescent = -YMIN + 10
    i.italicAngle = -ang if ang else 0
    i.openTypeOS2WeightClass = WGHT[w]
    i.openTypeOS2VendorID = VENDOR
    i.copyright = 'Copyright 2026 Đìzai Studio'; i.openTypeNameDesigner = 'Đìzai Studio'   # designer 06/11: tên studio có dấu
    i.openTypeNameManufacturer = 'Đìzai Studio'
    i.postscriptUnderlinePosition = -120; i.postscriptUnderlineThickness = 40
    i.openTypeOS2Selection = [7]                                     # USE_TYPO_METRICS
    f.lib['public.glyphOrder'] = ['.notdef'] + [gname(c) for c in CHARS]
    g = f.newGlyph('.notdef'); g.width = 500
    pen = g.getPen()
    for r in ((50, 0, 450, 700), (100, 50, 400, 650)):
        x0, y0, x1, y1 = r
        pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)] if r[0] == 50 else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        pen.moveTo(pts[0]); [pen.lineTo(p) for p in pts[1:]]; pen.closePath()
    for c in CHARS:
        if c == '\xa0': continue                                   # U+00A0 trỏ về glyph space
        g = f.newGlyph(gname(c)); g.width = SP[w][c]['adv']
        g.unicodes = [ord(c)] + ([0x00A0] if c == ' ' else [])
        k = f'{c}-{w}'
        if k in O:
            cs = parse(O[k])
            for j in FL.get(c, []): cs[j] = reverse(cs[j])
            draw(g, cs, SP[w][c]['dx'], ang)
    f.lib['public.glyphOrder'] = [n for n in f.lib['public.glyphOrder'] if n in f]
    f.groups.update(groups)
    f.kerning.update(kern)
    f.features.text = features()
    if ang:
        i.openTypeHheaCaretSlopeRise = 1000; i.openTypeHheaCaretSlopeRun = round(1000*math.tan(math.radians(ang)))
    return f

def features():
    L = []
    for c in CHARS:
        d = unicodedata.normalize('NFD', c)
        if len(d) > 1 and all(x in SP['Regular'] for x in d):
            L.append('    sub ' + ' '.join(gname(x) for x in d) + ' by ' + gname(c) + ';')
    # i / j + dấu trên → ı ȷ (đã có chữ dựng sẵn cho tiếng Việt; dấu rời cho chữ khác)
    return 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\n\nfeature ccmp {\n' + '\n'.join(sorted(L, key=lambda s: -s.count(' '))) + '\n} ccmp;\n'

def kerning_data():
    rc = {}; lc = {}
    for c in CHARS:
        if c in (' ', '\xa0') or SPc.kind(c) == 'mark': continue
        rc.setdefault(SPc.rclass(c), []).append(gname(c)); lc.setdefault(SPc.lclass(c), []).append(gname(c))
    rn = {k: 'public.kern1.R%03d' % i for i, k in enumerate(sorted(rc))}; ln = {k: 'public.kern2.L%03d' % i for i, k in enumerate(sorted(lc))}
    groups = {rn[k]: v for k, v in rc.items()}; groups.update({ln[k]: v for k, v in lc.items()})
    ks = {}
    for w in ('Regular', 'Bold'):
        K = KN[w]; d = {}
        for key, v in K['class'].items():
            for i_ in [i_ for i_, ch in enumerate(key) if ch == '|']:
                a, b = key[:i_], key[i_ + 1:]
                if a in rn and b in ln: d[(rn[a], ln[b])] = v; break
        ks[w] = d
    # ngoại lệ: hợp hai master, ghi tường minh ở cả hai
    exc = set(KN['Regular']['exc']) | set(KN['Bold']['exc'])
    for w in ('Regular', 'Bold'):
        K = KN[w]
        for key in exc:
            a, b = key[0], key[2:]
            if a not in SP[w] or b not in SP[w]: continue
            v = K['exc'].get(key)
            if v is None: v = K['class'].get(f'{SPc.rclass(a)}|{SPc.lclass(b)}', 0)
            ks[w][(gname(a), gname(b))] = v
    return groups, ks

def _ybounds():
    Y = [p[1] for d in O.values() for c in parse(d) for s in c for p in s[1:]]
    return math.ceil(max(Y)), math.floor(min(Y))

def main():
    global YMAX, YMIN
    YMAX, YMIN = _ybounds(); print('y lớn / nhỏ nhất', YMAX, YMIN)
    os.makedirs(BUILD, exist_ok=True); os.makedirs(FONTS, exist_ok=True)
    FL = {}
    for c in CHARS:
        if f'{c}-Regular' in O:
            fl = flips(parse(O[f'{c}-Regular']))
            if fl: FL[c] = fl
    print('đảo chiều contour:', sum(len(v) for v in FL.values()), 'contour ở', len(FL), 'glyph')
    groups, ks = kerning_data()
    print('kerning: nhóm', len(groups), '· cặp R / B', len(ks['Regular']), len(ks['Bold']))
    for ang, tag in ((0, ''), (ITALIC_ANGLE, '-Italic')):
        print('nguồn', tag or '-Roman', use('Italic' if tag else 'Roman'))
        FL = {}
        for c in CHARS:
            if f'{c}-Regular' in O:
                fl = flips(parse(O[f'{c}-Regular']))
                if fl: FL[c] = fl
        groups, ks = kerning_data()
        ds = DesignSpaceDocument()
        ax = AxisDescriptor(); ax.name = 'Weight'; ax.tag = 'wght'; ax.minimum, ax.default, ax.maximum = 400, 400, 700
        ds.addAxis(ax)
        for w in ('Regular', 'Bold'):
            f = master(w, ang, FL, groups, ks[w]); p = os.path.join(BUILD, f'{PS}{tag}-{w}.ufo')
            if os.path.exists(p): shutil.rmtree(p)
            f.save(p)
            s = SourceDescriptor(); s.path = p; s.location = {'Weight': WGHT[w]}; s.familyName = FAMILY
            s.styleName = f.info.styleName; ds.addSource(s)
        for w in WGHT:
            ins = InstanceDescriptor(); ins.familyName = FAMILY
            ins.styleName = (w + ' Italic' if w != 'Regular' else 'Italic') if ang else w
            ins.location = {'Weight': WGHT[w]}; ins.postScriptFontName = f'{PS}-' + (w + 'Italic' if ang and w != 'Regular' else ('Italic' if ang else w))
            ins.styleMapFamilyName = FAMILY if w in ('Regular', 'Bold') else f'{FAMILY} {w}'
            ins.styleMapStyleName = ({'Regular': 'regular', 'Bold': 'bold'}.get(w, 'regular') if not ang else
                                     {'Regular': 'italic', 'Bold': 'bold italic'}.get(w, 'italic'))
            ds.addInstance(ins)
        dsp = os.path.join(BUILD, f'{PS}{tag}.designspace'); ds.write(dsp)
        print('designspace', dsp)

def stat_static(path, italic):
    """STAT bản tĩnh: mỗi trục đúng MỘT giá trị (weight của chính file, ital 0 / 1)"""
    from fontTools.ttLib import TTFont
    from fontTools.otlLib.builder import buildStatTable
    f = TTFont(path); wc = f['OS/2'].usWeightClass; n = {v: k for k, v in WGHT.items()}.get(wc, 'Regular')
    wv = [dict(value=wc, name=n, flags=0x2 if wc == 400 else 0)]
    if wc == 400: wv[0]['linkedValue'] = 700
    iv = [dict(value=1, name='Italic')] if italic else [dict(value=0, name='Roman', flags=0x2, linkedValue=1)]
    buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='ital', name='Italic', values=iv)])
    f.save(path)

def stat(path, italic):
    """STAT: trục wght (Regular elidable, liên kết Bold) + trục ital (Roman elidable liên kết Italic) để app ghép Roman / Italic"""
    from fontTools.ttLib import TTFont
    from fontTools.otlLib.builder import buildStatTable
    f = TTFont(path)
    wv = [dict(value=v, name=n) for n, v in WGHT.items()]
    wv[0].update(flags=0x2, linkedValue=700)
    iv = [dict(value=1, name='Italic')] if italic else [dict(value=0, name='Roman', flags=0x2, linkedValue=1)]
    buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='ital', name='Italic', values=iv)])
    f.save(path)

def combined(VF):
    ds = DesignSpaceDocument()
    for name, tag, lo, df, hi in (('Weight', 'wght', 400, 400, 700), ('Slant', 'slnt', -ITALIC_ANGLE, 0, 0)):
        ax = AxisDescriptor(); ax.name, ax.tag, ax.minimum, ax.default, ax.maximum = name, tag, lo, df, hi; ds.addAxis(ax)
    for w in ('Regular', 'Bold'):
        for it in (False, True):
            s_ = SourceDescriptor(); s_.path = os.path.join(BUILD, f'{PS}{"-Italic" if it else ""}-{w}.ufo')
            s_.location = {'Weight': WGHT[w], 'Slant': -ITALIC_ANGLE if it else 0}; s_.familyName = FAMILY
            s_.styleName = (('Italic' if w == 'Regular' else f'{w} Italic') if it else w); ds.addSource(s_)
    for it in (False, True):
        for w in WGHT:
            ins = InstanceDescriptor(); ins.familyName = FAMILY
            ins.styleName = (('Italic' if w == 'Regular' else f'{w} Italic') if it else w)
            ins.location = {'Weight': WGHT[w], 'Slant': -ITALIC_ANGLE if it else 0}
            ins.postScriptFontName = f'{PS}-' + ((('Italic' if w == 'Regular' else w + 'Italic')) if it else w)
            ds.addInstance(ins)
    dsp = os.path.join(BUILD, f'{PS}-Combined.designspace'); ds.write(dsp)
    before = set(os.listdir(VF))
    subprocess.run(['fontmake', '-m', dsp, '-o', 'variable', '--output-dir', VF, '--flatten-components'], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    new = [f_ for f_ in os.listdir(VF) if f_ not in before][0]
    dst = os.path.join(VF, f'{PS}[slnt,wght].ttf'); os.replace(os.path.join(VF, new), dst)
    from fontTools.ttLib import TTFont
    from fontTools.otlLib.builder import buildStatTable
    f = TTFont(dst)
    wv = [dict(value=v, name=n) for n, v in WGHT.items()]; wv[0].update(flags=0x2, linkedValue=700)
    sv = [dict(value=0, name='Upright', flags=0x2), dict(value=-ITALIC_ANGLE, name='Italic')]
    buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='slnt', name='Slant', values=sv)])
    # tên PostScript riêng cho file gộp (kiểm tính unique 06/11: trùng 'AnNam-Regular' với AnNam[wght].ttf → macOS coi là một font)
    nm = f['name']
    for rec in list(nm.names):
        if rec.nameID == 6: rec.string = rec.toUnicode().replace(PS + '-', PS + 'Slnt-')
    nm.setName(PS + 'Slnt', 25, 3, 1, 0x409)
    for inst in f['fvar'].instances:
        if inst.postscriptNameID != 0xFFFF:
            r = nm.getName(inst.postscriptNameID, 3, 1, 0x409)
            if r: nm.setName(r.toUnicode().replace(PS + '-', PS + 'Slnt-'), inst.postscriptNameID, 3, 1, 0x409)
    f.save(dst)

def compile_fonts():
    VF = os.path.join(FONTS, 'variable')
    for d in ('variable', 'otf', 'ttf', 'woff2'): shutil.rmtree(os.path.join(FONTS, d), ignore_errors=True)
    for tag in ('', '-Italic'):
        dsp = os.path.join(BUILD, f'{PS}{tag}.designspace')
        subprocess.run(['fontmake', '-m', dsp, '-o', 'variable', '--output-dir', VF, '--flatten-components'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        dst = os.path.join(VF, f'{PS}{tag}[wght].ttf'); os.replace(os.path.join(VF, f'{PS}{tag}-VF.ttf'), dst); stat(dst, bool(tag))
        for fmt in ('otf', 'ttf'):
            subprocess.run(['fontmake', '-m', dsp, '-i', '-o', fmt, '--output-dir', os.path.join(FONTS, fmt), '--flatten-components'],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # file gộp Roman + Italic (designer 06/11 "italic không kết hợp trong variable luôn được hả"): trục wght 400–700 + slnt 0 … −10°
    # — Italic = Roman nghiêng 10° nên nghiêng là một trục liên tục, 4 master (R / B × đứng / nghiêng) cùng cấu trúc
    combined(VF)
    from fontTools.ttLib import TTFont
    for fmt in ('otf', 'ttf'):                                         # tên file = tên PostScript (DizaiSerif-SemiBoldItalic.otf)
        for f_ in os.listdir(os.path.join(FONTS, fmt)):
            p = os.path.join(FONTS, fmt, f_); ps = TTFont(p)['name'].getDebugName(6); q = os.path.join(FONTS, fmt, f'{ps}.{fmt}')
            os.replace(p, q); stat_static(q, 'Italic' in ps)                    # STAT cho cả bản tĩnh (ghép Roman ↔ Italic)
    # chuẩn hoá file (fontbakery 06/11): TTF có 'prep' bật smart dropout control (nét mảnh không mất khi chữ rất nhỏ);
    # bỏ bảng tên Mac (platform 1) — chỉ giữ Windows
    from fontTools.ttLib.tables import ttProgram
    for dp, _, fs in os.walk(FONTS):
        for f_ in fs:
            p = os.path.join(dp, f_); t = TTFont(p)
            t['name'].names = [n for n in t['name'].names if n.platformID != 1]
            # mã định danh (name ID 3) riêng từng file: phiên bản; vendor; tên PostScript (+ '-VF' cho file variable)
            vend = t['OS/2'].achVendID.strip() or 'NONE'
            uid = f"{VERSION[0]}.{VERSION[1]:03d};{vend};{t['name'].getDebugName(6)}" + ('-VF' if 'fvar' in t else '')
            t['name'].setName(uid, 3, 3, 1, 0x409)
            LM.apply(t)                                               # name ID 13/14: giấy phép thương mại (tools/release/license_meta.py)
            if 'glyf' in t and 'gvar' not in t:                       # bỏ điểm trùng liên tiếp (làm tròn sau cu2qu → đoạn độ dài 0)
                from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
                for gn in t.getGlyphOrder():
                    g = t['glyf'][gn]
                    if g.numberOfContours <= 0: continue
                    co, fl, ends = list(g.coordinates), list(g.flags), g.endPtsOfContours
                    nco, nfl, nends, st = [], [], [], 0
                    for e in ends:
                        pts = list(range(st, e + 1)); keep = []
                        for i in pts:
                            if keep and co[i] == co[keep[-1]]: continue
                            keep.append(i)
                        if len(keep) > 1 and co[keep[-1]] == co[keep[0]]: keep.pop()
                        nco += [co[i] for i in keep]; nfl += [fl[i] for i in keep]; nends.append(len(nco) - 1); st = e + 1
                    if len(nco) != len(co):
                        g.coordinates = GlyphCoordinates(nco); g.flags = bytearray(nfl); g.endPtsOfContours = nends
            if 'glyf' in t:
                prog = ttProgram.Program(); prog.fromAssembly(['PUSHW[ ]', '511', 'SCANCTRL[ ]', 'PUSHB[ ]', '4', 'SCANTYPE[ ]'])
                if 'prep' not in t:
                    from fontTools.ttLib import newTable
                    t['prep'] = newTable('prep')
                t['prep'].program = prog
            t.save(p)
    # woff2 cho web (designer 06/11 "làm thêm file woff2 cho web luôn"): nén Brotli từ variable/*.ttf và ttf/*.ttf
    W2 = os.path.join(FONTS, 'woff2'); shutil.rmtree(W2, ignore_errors=True)
    for sub in ('variable', 'ttf'):
        os.makedirs(os.path.join(W2, sub), exist_ok=True)
        for f_ in sorted(os.listdir(os.path.join(FONTS, sub))):
            t = TTFont(os.path.join(FONTS, sub, f_)); t.flavor = 'woff2'; t.save(os.path.join(W2, sub, f_.rsplit('.', 1)[0] + '.woff2'))
    for dp, _, fs in os.walk(FONTS):
        for f_ in sorted(fs): print('  ', os.path.relpath(os.path.join(dp, f_), ROOT), os.path.getsize(os.path.join(dp, f_))//1024, 'KB')

if __name__ == '__main__':
    main()
    if '--no-compile' not in sys.argv: compile_fonts()
