#!/usr/bin/env python3
"""Ảnh lớn của vài glyph kèm các phần dựng (đỏ) để kiểm: python3 preview.py out.svg S-Regular 2-Regular ..."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from build import outline, part_path, d_of, OUT, CAP
data = json.load(open(os.path.join(OUT, "parts.json")))
sc, x, items = 0.5, 10, []
for key in sys.argv[2:]:
    g = data[key]
    fx = lambda u, x=x: x + (u + 60) * sc
    fy = lambda v: (CAP + 220 - v) * sc
    items.append(f'<path d="{d_of(outline(g), fx, fy)}" fill="#e6e1d8" stroke="#111" stroke-width="0.7"/>')
    for s in g["parts"]:
        items.append(f'<path d="{d_of(part_path(s), fx, fy)}" fill="none" stroke="{"#2c68db" if s.get("counter") else "#db4a2b"}" stroke-width="0.6"/>')
    for y in (0, CAP): items.append(f'<line x1="{x}" x2="{x + (g["W"] + 120) * sc}" y1="{fy(y)}" y2="{fy(y)}" stroke="#bbb" stroke-width="0.5"/>')
    x += (g["W"] + 120) * sc
open(sys.argv[1], "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{x+10:.0f}" height="{(CAP+440)*sc:.0f}"><rect width="100%" height="100%" fill="#fff"/>{"".join(items)}</svg>')
