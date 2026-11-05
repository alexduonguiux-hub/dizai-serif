#!/usr/bin/env python3
"""QA phủ ký tự: mọi ký tự trong glyphs.js (ALL) có outline ở MỌI weight; export không lỗi.
    python3 tools/construct/qa_cover.py   (chạy sau export.js + build.py)"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from weights import WEIGHTS
src = open(os.path.join(HERE, 'glyphs.js')).read()
def js(name):
    m = re.search(r"const " + name + r" = ('([^']*)'|(\"(?:[^\"\\\\]|\\\\.)*\"))", src)
    return (m.group(2) if m.group(2) is not None else json.loads(m.group(3))) if m else ''
PUNCT = list('.,:;!?\'"’‘”“-–—()[]/+=×#%$€&@')
ALL = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') + list(js('VN')) + PUNCT + list(js('LOWER')) + list(js('VNL')) + \
      list(js('SYM')) + list(js('COMB')) + list(js('LOWX')) + list(js('LATU')) + list(js('LATL')) + list(js('MATH'))
O = json.load(open(os.path.join(HERE, '..', '..', 'out', 'construct', 'outlines.json')))
P = json.load(open(os.path.join(HERE, '..', '..', 'out', 'construct', 'parts.json')))
miss = [f'{c}-{w}' for w in WEIGHTS for c in ALL if f'{c}-{w}' not in O]
errs = [k for k, v in P.items() if 'error' in v]
print(f'ký tự {len(ALL)} × {len(WEIGHTS)} weight · thiếu outline: {len(miss)} {miss[:20]} · lỗi export: {len(errs)} {errs[:10]}')
sys.exit(1 if miss or errs else 0)
