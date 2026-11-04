#!/usr/bin/env python3
"""Sinh ref_glyphs.json: đường viền v0.2 (đơn vị font) cho các glyph có đường cong tự do của designer
(S, Q, 2, 3, 5). Guide: elip trọn vòng (nhận diện từ chính cung của bản vẽ, xem ellfit.py) + trục;
đoạn cong tự do: tay nắm Bézier.   python3 tools/construct/ref/make_ref.py
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import v02, ellfit
KEYS = ["S-Regular", "Q-Regular", "S-Bold", "Q-Bold", "2-Regular"]
R = lambda p: [round(p[0], 1), round(p[1], 1)]
out = {}
import pathops
def shifted(p, tx, ty, sy=1.0):
    q = pathops.Path(); pen = q.getPen() if hasattr(q, "getPen") else None
    for verb, pts in p.segments:
        P_ = [(x + tx, (y + ty) * sy) for x, y in pts]
        if verb == "moveTo": q.moveTo(*P_[0])
        elif verb == "lineTo": q.lineTo(*P_[0])
        elif verb == "curveTo": q.cubicTo(*P_[0], *P_[1], *P_[2])
        elif verb == "closePath": q.close()
    return q
def bold_from(p, dx=37, dy=30, n=16):
    acc = p
    for i in range(1, n + 1): acc = pathops.op(acc, shifted(p, i * dx / n, 0), pathops.PathOp.UNION)
    h = acc
    for j in range(1, n + 1): acc = pathops.op(acc, shifted(h, 0, j * dy / n), pathops.PathOp.UNION)
    return shifted(acc, 0, 0, 700 / (700 + dy))
DERIVED = {"2-Bold": "2-Regular"}   # chưa có bản Bold v0.2: suy ra từ Regular
for k in KEYS + list(DERIVED):
    o = v02.outline(k) if k not in DERIVED else bold_from(v02.outline(DERIVED[k]))
    cmds, guides, ells, cur = [], [], [], None
    for verb, ps in o.segments:
        if verb == "moveTo": cmds.append(["M", R(ps[0])]); cur = ps[0]
        elif verb == "lineTo": cmds.append(["L", R(ps[0])]); cur = ps[0]
        elif verb == "curveTo":
            cmds.append(["C"] + [R(p) for p in ps]); e = ellfit.ellipse_of([cur] + list(ps))
            if e and e["rl"] < 900:
                if not any(ellfit.same(e, f) for f in ells): ells.append(e)
            else: guides.append({"type": "handles", "p": [R(cur)] + [R(p) for p in ps]})
            cur = ps[2]
        elif verb == "closePath": cmds.append(["Z"])
    for e in ells:
        guides.append({"type": "ellipse", "c": R(e["c"]), "rx": round(e["rl"], 1), "ry": round(e["rs"], 1),
                       "rot": round(math.radians(e["ang"]), 4), "axes": abs(e["rl"] - e["rs"]) > 4})
    out[k] = {"cmds": cmds, "guides": [] if k in DERIVED else guides}
json.dump(out, open(os.path.join(HERE, "..", "ref_glyphs.json"), "w"), separators=(",", ":"))
print("ok", {k: (len(v["cmds"]), sum(g["type"] == "ellipse" for g in v["guides"])) for k, v in out.items()})
