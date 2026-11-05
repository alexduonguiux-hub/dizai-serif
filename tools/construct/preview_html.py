#!/usr/bin/env python3
"""Trang duyệt glyph (HTML, cùng cấu trúc trang duyệt Dinh Tuong): lưới glyph, ngăn xem lớn hai weight kèm guide dựng,
đánh dấu Đạt / Cần sửa (lưu chung qua db của Artifact), chữ mẫu xếp bằng chính outline.
    python3 tools/construct/build.py && python3 tools/construct/preview_html.py   → docs/preview/dizai-serif.html
"""
import json, os, re, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
outl = json.load(open(os.path.join(ROOT, "out", "construct", "outlines.json")))
ref = json.load(open(os.path.join(HERE, "ref_glyphs.json")))
src = open(os.path.join(HERE, "glyphs.js")).read()
VN = re.search(r"const VN = '([^']*)'", src).group(1)
VNL = re.search(r"const VNL = '([^']*)'", src).group(1)
PUNCT = list('.,:;!?\'"’‘”“-–—()[]/+=×#%$€&@')
FIG = list("0123456789")
CAPS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LOWER = list(re.search(r"const LOWER = '([^']*)'", src).group(1))
# glyph dựng theo luật nhưng không nằm trong designer_C: Bold U–Z (docs/08)
RULE_EXTRA = {f"{c}-Bold" for c in "UVWXYZ"}

def short(d):
    d = re.sub(r"(\d+)\.(\d)\d*", lambda m: m.group(1) if m.group(2) == "0" else m.group(1) + "." + m.group(2), d)
    return re.sub(r" ?([MLCZ]) ?", r"\1", d).strip()

def rg(g):
    o = dict(g)
    for k, v in o.items():
        if isinstance(v, float): o[k] = round(v, 3 if k in ("rot",) else 1)
        elif isinstance(v, list): o[k] = [round(x, 4 if k == "d" else 1) if isinstance(x, float) else ([round(y, 1) for y in x] if isinstance(x, list) else x) for x in v]
    return o

def entry(ch, w, grp):
    k = f"{ch}-{w}"; r = ref.get(k, {})
    rule = r.get("src") == "rule" or k in RULE_EXTRA
    xs = [float(v) for v in re.findall(r"-?\d+\.?\d*", outl[k])[0::2]]       # toạ độ x (cặp x y xen kẽ)
    return {"c": ch, "u": ord(ch), "g": grp, "a": r.get("W", 0) + 80, "W": r.get("W", 0), "p": short(outl[k]),
            "bx": [round(min(xs)), round(max(xs))] if xs else [0, 0],
            "s": "rule" if rule else "designer", "gd": [rg(x) for x in r.get("guides", []) if x["type"] != "handles"]}

data = {"weights": {}}
for w in ("Regular", "Bold"):
    L = []
    for grp, chars in (("caps", CAPS), ("lower", LOWER), ("fig", FIG), ("vn", list(VN)), ("vnl", list(VNL)), ("punct", PUNCT)):
        L += [entry(c, w, grp) for c in chars if f"{c}-{w}" in outl]
    data["weights"][w] = L
js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

html = open(os.path.join(HERE, "preview_template.html")).read().replace("/*DATA*/{}", js)
os.makedirs(os.path.join(ROOT, "docs", "preview"), exist_ok=True)
out = os.path.join(ROOT, "docs", "preview", "dizai-serif.html")
open(out, "w").write(html)
print(out, round(len(html) / 1024), "KB", {w: len(v) for w, v in data["weights"].items()})
