#!/usr/bin/env python3
"""Tính outline cuối cùng từ parts.json (do glyphs.js xuất) bằng skia-pathops, render SVG kiểm tra.

    node tools/construct/export.js > out/construct/parts.json
    python3 tools/construct/build.py            → out/construct/sheet-*.svg, outlines.json
"""
import json
import math
import os
import sys

import pathops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "out", "construct")
CAP = 700


def to_path(cmds):
    p = pathops.Path()
    for c in cmds:
        k = c[0]
        if k == "M": p.moveTo(*c[1])
        elif k == "L": p.lineTo(*c[1])
        elif k == "C": p.cubicTo(*c[1], *c[2], *c[3])
        elif k == "Z": p.close()
    return p


def part_path(s):
    p = to_path(s["cmds"])
    if s.get("minus"): p = pathops.op(p, to_path(s["minus"]), pathops.PathOp.DIFFERENCE)
    if s.get("clip"): p = pathops.op(p, to_path(s["clip"]), pathops.PathOp.INTERSECTION)
    if s.get("clip2"): p = pathops.op(p, to_path(s["clip2"]), pathops.PathOp.INTERSECTION)
    return p


def outline(g):
    acc = None
    for s in g["parts"]:
        if s.get("counter") or s.get("post"): continue
        q = part_path(s)
        acc = q if acc is None else pathops.op(acc, q, pathops.PathOp.UNION)
    for s in g["parts"]:
        if s.get("counter"): acc = pathops.op(acc, part_path(s), pathops.PathOp.DIFFERENCE)
    for s in g["parts"]:
        if s.get("post"): acc = pathops.op(acc, part_path(s), pathops.PathOp.UNION)
    return acc


def d_of(p, fx, fy):
    out = []
    for verb, pts in p.segments:
        q = " ".join("%.1f %.1f" % (fx(x), fy(y)) for x, y in pts)
        out.append({"moveTo": "M ", "lineTo": "L ", "curveTo": "C ", "qCurveTo": "Q ", "closePath": "Z"}[verb] + q)
    return " ".join(out)


def bounds(p):
    xs, ys = [], []
    for verb, pts in p.segments:
        for x, y in pts: xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def sheet(data, names, weight, scale=0.25, path=None, sb=40):
    x, items = 20, []
    H = (CAP + 400) * scale
    for ch in names:
        g = data[f"{ch}-{weight}"]
        o = outline(g)
        fx = lambda u, x=x: x + (u + sb) * scale
        fy = lambda v: (CAP + 160 - v) * scale
        items.append(f'<path d="{d_of(o, fx, fy)}" fill="#111"/>')
        x += (g["W"] + 2 * sb) * scale
    W = x + 20
    lines = "".join(f'<line x1="0" x2="{W:.0f}" y1="{(CAP + 160 - y) * scale:.1f}" y2="{(CAP + 160 - y) * scale:.1f}" stroke="#d9d4cc" stroke-width="0.6"/>' for y in (0, CAP))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}"><rect width="100%" height="100%" fill="#fff"/>{lines}{"".join(items)}</svg>'
    if path: open(path, "w").write(svg)
    return svg


if __name__ == "__main__":
    data = json.load(open(os.path.join(OUT, "parts.json")))
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    figs = list("0123456789")
    for w in ("Regular", "Bold"):
        sheet(data, letters[:13], w, path=os.path.join(OUT, f"sheet-{w}-1.svg"))
        sheet(data, letters[13:], w, path=os.path.join(OUT, f"sheet-{w}-2.svg"))
        sheet(data, figs, w, path=os.path.join(OUT, f"sheet-{w}-fig.svg"))
    outl = {k: d_of(outline(v), lambda x: x, lambda y: y) for k, v in data.items() if "parts" in v}
    json.dump(outl, open(os.path.join(OUT, "outlines.json"), "w"))
    print("ok", len(outl))
