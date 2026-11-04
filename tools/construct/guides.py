#!/usr/bin/env python3
"""Bản dựng kiểu "guide vẽ tay" của designer: glyph xám, elip trọn vòng + trục, các mép chéo kéo dài,
đường kẻ ngang (cap, baseline, overshoot nét đứt, các mốc dựng màu cam). Có thể đặt cạnh bản v0.2.

    node tools/construct/export.js > out/construct/parts.json
    python3 tools/construct/guides.py "6789" Regular out/construct/guide-6789.svg [--v02]
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import outline, d_of, CAP, OUT

def ell_path(c, rx, ry, rot, fx, fy, n=72):
    ca, sa = math.cos(rot), math.sin(rot); pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n; x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((fx(c[0] + x * ca - y * sa), fy(c[1] + x * sa + y * ca)))
    return "M " + " L ".join("%.1f %.1f" % p for p in pts) + " Z"

def cell(g, o, sc, ox, ref=None):
    W = g["W"]; fx = lambda u: ox + (u + 60) * sc; fy = lambda v: (CAP + 140 - v) * sc
    out = []
    if ref is not None:
        out.append(f'<path d="{d_of(ref, fx, fy)}" fill="none" stroke="#2a7de1" stroke-width="1.4" stroke-dasharray="4 3"/>')
    out.insert(0, f'<path d="{d_of(o, fx, fy)}" fill="#9a9a9a" stroke="#111" stroke-width="0.8"/>')
    L = 900
    for q in g["guides"]:
        t = q["type"]
        if t == "ellipse":
            out.append(f'<path d="{ell_path(q["c"], q["rx"], q["ry"], q["rot"], fx, fy)}" fill="none" stroke="#111" stroke-width="0.7"/>')
            if q.get("axes"):
                for a in (q["rot"], q["rot"] + math.pi / 2):
                    dx, dy = math.cos(a), math.sin(a)
                    out.append(f'<line x1="{fx(q["c"][0] - dx * L * .6):.1f}" y1="{fy(q["c"][1] - dy * L * .6):.1f}" x2="{fx(q["c"][0] + dx * L * .6):.1f}" y2="{fy(q["c"][1] + dy * L * .6):.1f}" stroke="#111" stroke-width="0.6"/>')
        elif t == "line":
            p, d = q["p"], q["d"]
            out.append(f'<line x1="{fx(p[0] - d[0] * L):.1f}" y1="{fy(p[1] - d[1] * L):.1f}" x2="{fx(p[0] + d[0] * L):.1f}" y2="{fy(p[1] + d[1] * L):.1f}" stroke="#111" stroke-width="0.6"/>')
        elif t == "hline":
            out.append(f'<line x1="{fx(-60):.1f}" x2="{fx(W + 60):.1f}" y1="{fy(q["y"]):.1f}" y2="{fy(q["y"]):.1f}" stroke="#ef7b50" stroke-width="0.7"/>')
        elif t == "compass":
            out.append(f'<circle cx="{fx(q["c"][0]):.1f}" cy="{fy(q["c"][1]):.1f}" r="{q["r"] * sc:.1f}" fill="none" stroke="#e8a33a" stroke-width="0.6"/>')
        elif t == "handles":
            p = q["p"]
            for a, b in ((p[0], p[1]), (p[3], p[2])):
                out.append(f'<line x1="{fx(a[0]):.1f}" y1="{fy(a[1]):.1f}" x2="{fx(b[0]):.1f}" y2="{fy(b[1]):.1f}" stroke="#8a4fd8" stroke-width="0.6"/><circle cx="{fx(b[0]):.1f}" cy="{fy(b[1]):.1f}" r="1.6" fill="#8a4fd8"/>')
    return "".join(out), (W + 120) * sc

def sheet(chars, weight, path, v02=False, sc=0.42):
    data = json.load(open(os.path.join(OUT, "parts.json")))
    refs = {}
    if v02:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref")); import v02 as V
        refs = {k: V.outline(k) for k in V.DATA if not k.startswith("_")}
    x, body = 0, []
    for ch in chars:
        g = data[f"{ch}-{weight}"]; s, w = cell(g, outline(g), sc, x, refs.get(f"{ch}-{weight}")); body.append(s); x += w
    H = (CAP + 300) * sc; fy = lambda v: (CAP + 140 - v) * sc
    lines = "".join(f'<line x1="0" x2="{x:.0f}" y1="{fy(y):.1f}" y2="{fy(y):.1f}" stroke="{c}" stroke-width="0.8" {"stroke-dasharray=\"5 3\"" if dash else ""}/>'
                    for y, c, dash in ((CAP, "#8a4fd8", True), (0, "#8a4fd8", True), (CAP + 12, "#ef7b50", True), (-12, "#ef7b50", True)))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{x:.0f}" height="{H:.0f}"><rect width="100%" height="100%" fill="#f4f4f4"/>{"".join(body)}{lines}</svg>'
    open(path, "w").write(svg); return svg

if __name__ == "__main__":
    sheet(sys.argv[1], sys.argv[2], sys.argv[3], "--v02" in sys.argv)
