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
def _jsconst(name):
    m = re.search(r'const ' + name + r' = ("(?:[^"\\]|\\.)*")', src); return json.loads(m.group(1)) if m else ''
SYMX = list(_jsconst('SYM')) + list(_jsconst('LOWX')) + list(_jsconst('COMB')) + list(_jsconst('LATU')) + list(_jsconst('LATL')) + list(_jsconst('MATH'))     # ký tự bổ sung nhóm 1 + 2
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
    if k not in outl: return None
    return {"c": ch, "u": ord(ch), "g": grp, "a": r.get("W", 0) + 80, "W": r.get("W", 0), "p": short(outl[k]),
            "bx": [round(min(xs)), round(max(xs))] if xs else [0, 0],
            "s": "interp" if r.get("src") == "interp" else ("rule" if rule else "designer"), "gd": [rg(x) for x in r.get("guides", []) if x["type"] != "handles"]}

import unicodedata as _ud
SP = json.load(open(os.path.join(ROOT, "out", "construct", "spacing.json")))
KN = json.load(open(os.path.join(ROOT, "out", "construct", "kerning.json")))
def _base(ch):
    if ch in "Đđ": return {"Đ": "D", "đ": "d"}[ch]
    return _ud.normalize("NFD", ch)[0]
def _rc(ch):
    nfd = _ud.normalize("NFD", ch); return nfd[0] + "\u031b" if "\u031b" in nfd else _base(ch)
data = {"weights": {}, "kern": {w: {"c": KN[w]["class"], "e": KN[w]["exc"]} for w in KN}}
for w in ("Regular", "Medium", "SemiBold", "Bold"):
    L = []
    for grp, chars in (("caps", CAPS), ("lower", LOWER), ("fig", FIG), ("vn", list(VN)), ("vnl", list(VNL)), ("punct", PUNCT), ("sym", SYMX)):
        L += [entry(c, w, grp) for c in chars if f"{c}-{w}" in outl]
    for e in L:                                     # spacing (S14) + class kerning
        sp = SP[w].get(e["c"])
        if sp: e["a"], e["dx"] = sp["adv"], sp["dx"]
        e["rc"], e["lc"] = _rc(e["c"]), _base(e["c"])
    data["weights"][w] = L
# Italic (designer 06/11 "bản italic chưa có trên preview"): outline nhánh Italic (out/construct_italic — hiện = glyph Roman),
# nghiêng 10° quanh ½ x-height như export_font; kerning / spacing dùng chung Roman
import math
_T = math.tan(math.radians(10)); _YC = 495.0/2
_OI = os.path.join(ROOT, "out", "construct_italic", "outlines.json")
outl_i = json.load(open(_OI)) if os.path.exists(_OI) else outl
def _skew(d):
    nums = list(re.finditer(r"-?\d+(?:\.\d+)?", d)); out = []; last = 0
    for i in range(0, len(nums) - 1, 2):
        mx, my = nums[i], nums[i + 1]; x, y = float(mx.group()), float(my.group())
        out.append(d[last:mx.start()]); out.append(f"{x + (y - _YC)*_T:.1f}"); out.append(d[mx.end():my.start()]); out.append(my.group()); last = my.end()
    out.append(d[last:]); return "".join(out)
for w in ("Regular", "Medium", "SemiBold", "Bold"):
    wi = "Italic" if w == "Regular" else f"{w} Italic"; L = []
    for e in data["weights"][w]:
        k = f"{e['c']}-{w}"; d = short(outl_i.get(k, outl[k])); p = _skew(d)
        xs = [float(v) for v in re.findall(r"-?\d+\.?\d*", p)[0::2]]
        L.append(dict(e, p=p, gd=[], bx=[round(min(xs)), round(max(xs))] if xs else [0, 0]))
    data["weights"][wi] = L; data["kern"][wi] = data["kern"][w]
js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

html = open(os.path.join(HERE, "preview_template.html")).read().replace("/*DATA*/{}", js)
# font variable thật (export_font.py) nhúng woff2 base64 → mục "Font variable" của trang
import base64, io
FF = []
for fam, fn in (("Dizai Serif VF", "DizaiSerif[wght].ttf"), ("Dizai Serif VF Italic", "DizaiSerif-Italic[wght].ttf"),
                ("Dizai Serif VF Combined", "DizaiSerif[slnt,wght].ttf")):
    fp = os.path.join(ROOT, "fonts", "variable", fn)
    if not os.path.exists(fp): continue
    from fontTools.ttLib import TTFont
    f = TTFont(fp); f.flavor = "woff2"; b = io.BytesIO(); f.save(b)
    FF.append('@font-face { font-family: "%s"; src: url(data:font/woff2;base64,%s) format("woff2"); font-weight: 400 700; font-display: block; }'
              % (fam, base64.b64encode(b.getvalue()).decode()))
html = html.replace("/*FONTS*/", "\n".join(FF))
os.makedirs(os.path.join(ROOT, "docs", "preview"), exist_ok=True)
out = os.path.join(ROOT, "docs", "preview", "dizai-serif.html")
open(out, "w").write(html)
print(out, round(len(html) / 1024), "KB", {w: len(v) for w, v in data["weights"].items()})
