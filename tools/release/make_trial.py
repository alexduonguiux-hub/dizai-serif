"""Bản dùng thử AnNam Serif Trial: Regular + Bold + Italic, chỉ Basic Latin (không dấu Việt), dùng thử cá nhân.

Ra dist/AnNamSerif-Trial-v0.900.zip (OTF + EULA Trial + README). Đổi tên họ để không đụng bản thương mại khi cài cùng máy.
"""
import os, sys, zipfile, io
from fontTools.ttLib import TTFont
from fontTools import subset
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import license_meta as LM
ROOT = os.path.join(HERE, '..', '..'); FONTS = os.path.join(ROOT, 'fonts'); DIST = os.path.join(ROOT, 'dist')
FAM, PS, TFAM, TPS = 'AnNam Serif', 'AnNamSerif', 'AnNam Serif Trial', 'AnNamSerifTrial'
STYLES = ['Regular', 'Bold', 'Italic']
UNI = list(range(0x20, 0x7F)) + [0xA0]                      # Basic Latin — không có chữ Việt, ký hiệu mở rộng


def build(style):
    t = TTFont(os.path.join(FONTS, 'otf', f'{PS}-{style}.otf'))
    o = subset.Options(); o.layout_features = ['*']; o.name_IDs = ['*']; o.name_languages = ['*']; o.notdef_outline = True
    s = subset.Subsetter(o); s.populate(unicodes=UNI); s.subset(t)
    nm = t['name']
    for r in nm.names:
        v = r.toUnicode()
        if r.nameID in (1, 3, 4, 16, 18, 21): v = v.replace(FAM, TFAM)
        if r.nameID in (3, 6, 20): v = v.replace(PS, TPS)
        if r.nameID == 4: v = v.replace(PS, TPS)
        r.string = v
    if 'CFF ' in t:
        cff = t['CFF '].cff; top = cff.topDictIndex[0]
        cff.fontNames = [n.replace(PS, TPS) for n in cff.fontNames]
        top.FamilyName = TFAM; top.FullName = top.FullName.replace(FAM, TFAM)
    t['OS/2'].fsType = 2                                     # Restricted License embedding: không nhúng được (bản thử)
    LM.apply(t, LM.TRIAL_DESC)
    b = io.BytesIO(); t.save(b); return f'{TPS}-{style}.otf', b.getvalue()


README = """AnNam Serif Trial — Version 0.900
Design: Đìzai Studio

This trial contains Regular, Bold and Italic with the Basic Latin character set only
(no Vietnamese letters, no extended symbols). It is for personal, non-commercial
testing and layout mockups that are not published. See EULA-Trial.txt.

The full family (8 styles + variable fonts, 134 Vietnamese letters, woff2)
is available under a Web, App / Game or Logo / Brand license.

© 2026 Đìzai Studio
"""

if __name__ == '__main__':
    os.makedirs(DIST, exist_ok=True)
    zp = os.path.join(DIST, 'AnNamSerif-Trial-v0.900.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for st in STYLES:
            n, data = build(st); z.writestr(f'AnNamSerif-Trial/{n}', data)
        z.writestr('AnNamSerif-Trial/README.txt', README)
        z.write(os.path.join(ROOT, 'commercial', 'EULA-Trial.txt'), 'AnNamSerif-Trial/EULA-Trial.txt')
    print('→', os.path.relpath(zp, ROOT), os.path.getsize(zp)//1024, 'KB')
