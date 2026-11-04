#!/usr/bin/env python3
"""ref_glyphs.json = hình gốc của designer (designer_A.json: Regular A–Z; designer_B.json: Bold A–T + bộ số mới nhất,
khung 2059:2) + guide hình học nhận diện từ chính đường cong:
  ellipse  — cung elip (cubic có hai tay nắm cùng tỉ lệ, xem ellfit.py), vẽ trọn vòng + 2 trục
  circle   — cung tròn nhỏ (loe, mỏ, móc), vẽ trọn vòng compa
  line     — đoạn thẳng chéo dài > 120u, kéo dài
  hline    — đoạn ngang trong (thanh, mép tay) ở cao độ khác 0 / cap
  handles  — đường cong tự do dài: tay nắm Bézier
    python3 tools/construct/ref/make_ref.py
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ellfit
from tidy import tidy
import pathops

def parse(d):
    toks = re.findall(r"[MLCZ]|-?[\d.]+(?:e-?\d+)?", d); i = 0; out = []
    while i < len(toks):
        c = toks[i]; i += 1; n = {"M": 1, "L": 1, "C": 3, "Z": 0}[c]
        out.append((c, [(float(toks[i + 2 * j]), float(toks[i + 2 * j + 1])) for j in range(n)])); i += 2 * n
    return out

def outline(paths):
    acc = None
    for d in paths:
        p = pathops.Path()
        for c, pts in parse(d):
            if c == "M": p.moveTo(*pts[0])
            elif c == "L": p.lineTo(*pts[0])
            elif c == "C": p.cubicTo(*pts[0], *pts[1], *pts[2])
            else: p.close()
        acc = p if acc is None else pathops.op(acc, p, pathops.PathOp.UNION)
    return acc

R = lambda p: [round(p[0], 1), round(p[1], 1)]
def build(paths, strong=False):
    o = tidy(outline(paths), strong); cmds, guides, ells, circ, lines, hl, cur, start = [], [], [], [], [], set(), None, None
    for verb, ps in o.segments:
        if verb == "moveTo": cmds.append(["M", R(ps[0])]); cur = start = ps[0]
        elif verb in ("lineTo", "closePath"):
            q = ps[0] if verb == "lineTo" else start
            if verb == "lineTo": cmds.append(["L", R(q)])
            dx, dy = q[0] - cur[0], q[1] - cur[1]; L = math.hypot(dx, dy)
            if L > 120 and abs(dx) > 8 and abs(dy) > 8:
                d = (dx / L, dy / L)
                if not any(abs(d[0] * e[1][1] - d[1] * e[1][0]) < 0.01 and abs((cur[0] - e[0][0]) * d[1] - (cur[1] - e[0][1]) * d[0]) < 2 for e in lines):
                    lines.append((cur, d))
            if abs(dy) < 0.5 and L > 60 and 15 < cur[1] < 685: hl.add(round(cur[1]))
            if verb == "closePath": cmds.append(["Z"])
            cur = q
        elif verb == "curveTo":
            cmds.append(["C"] + [R(p) for p in ps]); e = ellfit.ellipse_of([cur] + list(ps))
            if e and e["rl"] < 900:
                if abs(e["rl"] - e["rs"]) < 6 and e["rl"] < 200:
                    if not any(math.dist(e["c"], c["c"]) < 3 and abs(e["rl"] - c["r"]) < 3 for c in circ): circ.append({"c": e["c"], "r": e["rl"]})
                elif not any(ellfit.same(e, f) for f in ells): ells.append(e)
            elif math.dist(cur, ps[2]) > 150: guides.append({"type": "handles", "p": [R(cur)] + [R(p) for p in ps]})
            cur = ps[2]
    xs_all = [q[0] for v, ps in o.segments for q in ps]; W = max(xs_all)
    def fits(e):  # elip guide phải nằm trong ô chữ (±60u): loại các elip nhận diện nhầm từ cung ngắn
        a = math.radians(e["ang"]); ca, sa = math.cos(a), math.sin(a)
        ex = math.hypot(e["rl"] * ca, e["rs"] * sa); ey = math.hypot(e["rl"] * sa, e["rs"] * ca)
        return e["c"][0] - ex > -60 and e["c"][0] + ex < W + 60 and e["c"][1] - ey > -75 and e["c"][1] + ey < 775
    ells = [e for e in ells if fits(e)]
    for e in ells:
        guides.append({"type": "ellipse", "c": R(e["c"]), "rx": round(e["rl"], 1), "ry": round(e["rs"], 1), "rot": round(math.radians(e["ang"]), 4), "axes": abs(e["rl"] - e["rs"]) > 4})
    for c in circ: guides.append({"type": "circle", "c": R(c["c"]), "r": round(c["r"], 1)})
    for p, d in lines: guides.append({"type": "line", "p": R(p), "d": [round(d[0], 4), round(d[1], 4)]})
    for y in sorted(hl): guides.append({"type": "hline", "y": y})
    xs = [p[1][0] for p in cmds if p[0] != "Z"] + [q[0] for p in cmds if p[0] == "C" for q in p[1:]]
    return {"cmds": cmds, "guides": guides, "W": round(max(xs))}

if __name__ == "__main__":
    src = {}
    for f in ("designer_A.json", "designer_B.json", "designer_C.json", "../lower/lower_ae.json"):
        if os.path.exists(os.path.join(HERE, f)): src.update(json.load(open(os.path.join(HERE, f))))
    Wover = src.pop("_W", {})   # designer_C: chữ có dấu giữ bề ngang của chữ gốc (dấu được phép tràn)
    Cset = set(json.load(open(os.path.join(HERE, "designer_C.json")))) if os.path.exists(os.path.join(HERE, "designer_C.json")) else set()
    out = {k: build(v, k in Cset) for k, v in src.items()}   # QA: dọn nét thừa (mạnh cho glyph dựng theo luật)
    for k, w in Wover.items(): out[k]["W"] = w
    C = json.load(open(os.path.join(HERE, "designer_C.json"))) if os.path.exists(os.path.join(HERE, "designer_C.json")) else {}
    for k in out: out[k]["src"] = "rule" if k in C else "designer"   # nguồn: A/B = bản vẽ designer; C = dựng theo luật (vn_punct.py)

    json.dump(out, open(os.path.join(HERE, "..", "ref_glyphs.json"), "w"), separators=(",", ":"))
    print("ok", len(out), {k: (v["W"], sum(g["type"] == "ellipse" for g in v["guides"]), sum(g["type"] == "circle" for g in v["guides"])) for k, v in list(out.items())[:8]})
