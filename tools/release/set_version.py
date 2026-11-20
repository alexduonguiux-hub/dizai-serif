"""Đặt version cho MỌI file font đã build (fonts/ và fonts/golden/): head.fontRevision, name ID 3 / 5, CFF version.
    python3 tools/release/set_version.py 0.918 0.919
Dùng khi chỉ đổi số version (không dựng lại outline). export_font.py VERSION phải đổi cùng để bản build sau khớp."""
import os, sys
from fontTools.ttLib import TTFont
old, new = sys.argv[1], sys.argv[2]
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'); n = 0
for dp, _, fs in os.walk(os.path.join(ROOT, 'fonts')):
    for f in fs:
        if not f.endswith(('.otf', '.ttf', '.woff2')): continue
        p = os.path.join(dp, f); t = TTFont(p)
        t['head'].fontRevision = float(new)
        for r in t['name'].names:
            if r.nameID in (3, 5):
                s = r.toUnicode()
                if old in s: r.string = s.replace(old, new)
        if 'CFF ' in t:
            top = t['CFF '].cff.topDictIndex[0]
            if getattr(top, 'version', None): top.version = top.version.replace(old, new)
        if f.endswith('.woff2'): t.flavor = 'woff2'
        t.save(p); n += 1
print('đổi version', old, '→', new, ':', n, 'file')
