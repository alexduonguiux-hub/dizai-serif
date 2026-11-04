#!/usr/bin/env python3
"""Thư viện dựng cho Figma, lưu trong text node ẩn "_dizai_lib" trên trang dựng, gọi bằng AsyncFunction.
    python3 mklib.py store > out/construct/figma/store.js     # lưu thư viện (1 lần mỗi khi glyphs.js đổi)
    python3 mklib.py run "[['Regular','2048:16',['A','B']]]"  # mã gọi một lượt dựng
"""
import json, re, sys
from mkrun import mini
PAGE = '2048:2'
def lib():
    g = open('glyphs.js').read().split("if (typeof module")[0]
    return mini(g) + "\n" + mini(open('render_figma.js').read())
if __name__ != '__main__': pass
elif sys.argv[1] == 'store':
    print(f"""const pg = await figma.getNodeByIdAsync('{PAGE}'); await figma.setCurrentPageAsync(pg);
await figma.loadFontAsync({{ family: 'Inter', style: 'Regular' }});
let t = pg.findOne(n => n.name === '_dizai_lib'); if (!t) {{ t = figma.createText(); pg.appendChild(t); t.name = '_dizai_lib'; t.visible = false; t.x = -5000; t.y = -5000; }}
t.characters = {json.dumps(lib(), ensure_ascii=False)};
return t.characters.length;""")
else:
    jobs = json.loads(sys.argv[2].replace("'", '"'))
    ref = json.load(open('ref_glyphs.json'))
    need = {f"{ch}-{w}" for w, _, chars in jobs for ch in chars}
    sub = {k: v for k, v in ref.items() if k in need}
    print(f"""const pg = await figma.getNodeByIdAsync('{PAGE}'); await figma.setCurrentPageAsync(pg);
const src = pg.findOne(n => n.name === '_dizai_lib').characters;
const AF = Object.getPrototypeOf(async function () {{}}).constructor;
return await (new AF('PAGE_ID', 'JOBS', 'REF_DATA', src))('{PAGE}', {json.dumps(jobs)}, {json.dumps(sub, separators=(',', ':'))});""")
