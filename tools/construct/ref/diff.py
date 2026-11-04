"""% diện tích lệch (XOR) giữa bản dựng và bản v0.2, đo bằng raster 1u."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
from build import outline, OUT
import v02
def polys(p):
    out, pts, cur = [], [], None
    for v, ps in p.segments:
        if v == "moveTo":
            if pts: out.append(pts)
            pts = [ps[0]]; cur = ps[0]
        elif v == "lineTo": pts.append(ps[0]); cur = ps[0]
        elif v == "curveTo":
            p0 = cur
            for i in range(1, 13):
                t = i / 12; u = 1 - t
                pts.append(tuple(u**3*p0[k] + 3*u*u*t*ps[0][k] + 3*u*t*t*ps[1][k] + t**3*ps[2][k] for k in (0, 1)))
            cur = ps[2]
        elif v == "closePath": out.append(pts); pts = []
    if pts: out.append(pts)
    return out
def raster(p):
    acc = np.zeros((1000, 1000), bool)
    for pl in polys(p):
        im = Image.new("1", (1000, 1000)); ImageDraw.Draw(im).polygon([(x + 100, 850 - y) for x, y in pl], fill=1)
        acc ^= np.array(im)
    return acc
def diff(a, b):
    A, B = raster(a), raster(b); return 100 * (A ^ B).sum() / B.sum()
if __name__ == "__main__":
    data = json.load(open(os.path.join(OUT, "parts.json")))
    for k in v02.DATA:
        if k[0] != "_": print(f"{k:12s} lệch {diff(outline(data[k]), v02.outline(k)):5.1f}%")
