"""Đọc v0.2_paths.json → đường viền đơn vị font (y lên, mép mực trái = 0)."""
import json, os, re, math
import pathops
K = 700 / 247
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "v02_paths.json")))

def parse(d):
    toks = re.findall(r"[MLCZ]|-?[\d.]+(?:e-?\d+)?", d); i = 0; out = []
    while i < len(toks):
        c = toks[i]; i += 1
        n = {"M": 1, "L": 1, "C": 3, "Z": 0}[c]
        pts = [(float(toks[i + 2 * j]), float(toks[i + 2 * j + 1])) for j in range(n)]; i += 2 * n
        out.append((c, pts))
    return out

def glyph_cmds(key):
    e = DATA[key]; res = []
    for d, t in e["g"]:
        a, b, tx, c, dd, ty = t
        f = lambda p: (((a * p[0] + b * p[1] + tx) - e["left"]) * K, (e["base"] - (c * p[0] + dd * p[1] + ty)) * K)
        res.append([(cmd, [f(p) for p in pts]) for cmd, pts in parse(d)])
    return res

def to_path(cmds):
    p = pathops.Path()
    for c, pts in cmds:
        if c == "M": p.moveTo(*pts[0])
        elif c == "L": p.lineTo(*pts[0])
        elif c == "C": p.cubicTo(*pts[0], *pts[1], *pts[2])
        else: p.close()
    return p

def outline(key):
    acc = None
    for cm in glyph_cmds(key):
        q = to_path(cm); acc = q if acc is None else pathops.op(acc, q, pathops.PathOp.UNION)
    return acc
