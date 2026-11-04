#!/usr/bin/env python3
"""Đìzai Serif — bộ dựng hình theo quy tắc (v0.3).

Mọi glyph được dựng từ luật trong `docs/07-rule-book-v0.3.md`: thân, thanh, chéo, vòng,
loe (L1), mỏ tay ngang (L2), đỉnh nhọn (J1). Không lấy lại vector cũ.

Đơn vị font: UPM 1000, cap 700, baseline 0, trục y hướng lên.
Mỗi glyph trả về:
  outline  – contour cuối cùng (sau phép hợp / trừ, skia-pathops)
  parts    – các hình dựng có tên (để vẽ guide)
  guides   – vòng compa của loe / mỏ, tâm & trục vòng, đường dựng đỉnh
Chạy:  python3 tools/construct/dizai.py  → out/construct/*.json + *.svg
"""
import json
import math
import os

import pathops

CAP, OVS_ROUND, OVS_APEX = 700, 12, 12
RULES = {
    "Regular": dict(V=102, Vr=106, D=100, t=44, Hb=40),
    "Bold": dict(V=139, Vr=146, D=146, t=74, Hb=68),
}
FLARE_R, FLARE_F = 112, 23      # L1: một vòng r, mũi cách mép nét f
BEAK_B = 54                     # L2: mỏ sâu b trên đường cắt đầu tay
APEX_A = 20                     # J1: đoạn cắt phẳng ở đỉnh
MID_ARM_SLANT = math.radians(26)  # tay giữa E/F cắt xiên
BAR_Y = {"H": 0.53, "A": 0.255}   # tâm thanh / cap
KAPPA, KAPPA_IN = 0.5523, 0.60

# bề ngang mực (u) — tỉ lệ đã duyệt ở v0.2
WIDTH = {
    "Regular": dict(H=499, I=148, E=374, T=397, L=408, N=499, A=672, V=672, O=723, D=558),
    "Bold": dict(H=541, I=185, E=422, T=445, L=456, N=555, A=695, V=695, O=723, D=609),
}


# ---------------------------------------------------------------- vector helpers
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def norm(a):
    L = math.hypot(*a)
    return (a[0] / L, a[1] / L)
def perp(a): return (-a[1], a[0])


def line_x_at_y(p, d, y):
    """x of the line through p with direction d at height y."""
    return p[0] + d[0] * (y - p[1]) / d[1]


class Shape:
    """A closed path: list of ('M',p) ('L',p) ('C',c1,c2,p) ('Z',)."""

    def __init__(self, name, cmds, kind="add"):
        self.name, self.cmds, self.kind = name, cmds, kind

    def to_pathops(self):
        p = pathops.Path()
        for c in self.cmds:
            if c[0] == "M": p.moveTo(*c[1])
            elif c[0] == "L": p.lineTo(*c[1])
            elif c[0] == "C": p.cubicTo(*c[1], *c[2], *c[3])
            elif c[0] == "Z": p.close()
        return p


def shape_from_pathops(name, p, kind="add"):
    cmds = []
    for verb, pts in p.segments:
        if verb == "moveTo": cmds.append(("M", pts[0]))
        elif verb == "lineTo": cmds.append(("L", pts[0]))
        elif verb == "curveTo": cmds.append(("C",) + tuple(pts))
        elif verb == "closePath": cmds.append(("Z",))
    return Shape(name, cmds, kind)


def poly(name, pts, kind="add"):
    return Shape(name, [("M", pts[0])] + [("L", q) for q in pts[1:]] + [("Z",)], kind)


def rect(name, x0, y0, x1, y1, kind="add"):
    return poly(name, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], kind)


def arc_cmds(c, r, a0, a1):
    """cubic segments of a circular arc from angle a0 to a1 (radians)."""
    n = max(1, math.ceil(abs(a1 - a0) / (math.pi / 2)))
    da = (a1 - a0) / n
    out = []
    for i in range(n):
        s, e = a0 + i * da, a0 + (i + 1) * da
        k = 4 / 3 * math.tan((e - s) / 4) * r
        p0 = (c[0] + r * math.cos(s), c[1] + r * math.sin(s))
        p3 = (c[0] + r * math.cos(e), c[1] + r * math.sin(e))
        c1 = (p0[0] - k * math.sin(s), p0[1] + k * math.cos(s))
        c2 = (p3[0] + k * math.sin(e), p3[1] - k * math.cos(e))
        out.append(("C", c1, c2, p3))
    return out


def ellipse(name, c, rx, ry, rot=0.0, kappa=KAPPA, kind="add"):
    ca, sa = math.cos(rot), math.sin(rot)
    tf = lambda x, y: (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)
    kx, ky = kappa * rx, kappa * ry
    cmds = [("M", tf(rx, 0)),
            ("C", tf(rx, ky), tf(kx, ry), tf(0, ry)),
            ("C", tf(-kx, ry), tf(-rx, ky), tf(-rx, 0)),
            ("C", tf(-rx, -ky), tf(-kx, -ry), tf(0, -ry)),
            ("C", tf(kx, -ry), tf(rx, -ky), tf(rx, 0)), ("Z",)]
    return Shape(name, cmds, kind)


def half_ellipse_right(name, cx, cy, rx, ry, kappa=KAPPA, kind="add", left_ext=0):
    """right half of an ellipse closed by its vertical diameter (extended left_ext)."""
    kx, ky = kappa * rx, kappa * ry
    cmds = [("M", (cx - left_ext, cy - ry)), ("L", (cx, cy - ry)),
            ("C", (cx + kx, cy - ry), (cx + rx, cy - ky), (cx + rx, cy)),
            ("C", (cx + rx, cy + ky), (cx + kx, cy + ry), (cx, cy + ry)),
            ("L", (cx - left_ext, cy + ry)), ("Z",)]
    return Shape(name, cmds, kind)


# ---------------------------------------------------------------- rules
class Glyph:
    def __init__(self, name, weight):
        self.name, self.weight = name, weight
        self.r = RULES[weight]
        self.parts, self.guides = [], []
        self.width = WIDTH[weight][name]

    def part(self, s):
        self.parts.append(s)
        return s

    # L1 / L2: one circle r tangent to the stroke edge, through tip P
    def flare(self, name, Eg, u, n, P, r=FLARE_R):
        """Eg: edge point on the guideline/cut; u: unit along the edge into the stroke;
        n: unit normal pointing out of the stroke on the flared side; P: tip."""
        w = sub(P, Eg)
        uw, nw = dot(u, w), dot(n, w)
        disc = uw * uw - dot(w, w) + 2 * r * nw
        s = uw + math.sqrt(disc)
        T = add(Eg, mul(u, s))
        C = add(T, mul(n, r))
        a0 = math.atan2(P[1] - C[1], P[0] - C[0])
        a1 = math.atan2(T[1] - C[1], T[0] - C[0])
        d = a1 - a0
        while d > math.pi: d -= 2 * math.pi
        while d < -math.pi: d += 2 * math.pi
        ov = 3  # chồng 3 u vào trong nét: không có cạnh trùng khít
        cmds = [("M", add(Eg, mul(n, -ov))), ("L", P)] + arc_cmds(C, r, a0, a0 + d) + \
               [("L", add(T, mul(n, -ov))), ("Z",)]
        self.part(Shape(name, cmds))
        self.guides.append(dict(type="compass", c=C, r=r, a0=a0, a1=a0 + d, tip=P, tangent=T, rule="L1" if r == FLARE_R else "L2"))

    def stem_flares(self, x0, x1, y, left=True, right=True):
        """flares at a vertical stem end lying on guideline y (0 or CAP)."""
        u = (0, 1) if y == 0 else (0, -1)
        if left:
            self.flare(f"Loe {'chân' if y == 0 else 'đỉnh'} trái", (x0, y), u, (-1, 0), (x0 - FLARE_F, y))
        if right:
            self.flare(f"Loe {'chân' if y == 0 else 'đỉnh'} phải", (x1, y), u, (1, 0), (x1 + FLARE_F, y))

    def diag_flares(self, p_edge_a, p_edge_b, d, y, name):
        """flares on both sides of a diagonal stroke end on guideline y.
        p_edge_a/p_edge_b: points on the two edges; d: unit direction of the stroke (any sense)."""
        u = d if (d[1] > 0) == (y == 0) else mul(d, -1)  # into the stroke away from guideline
        ea = (line_x_at_y(p_edge_a, d, y), y)
        eb = (line_x_at_y(p_edge_b, d, y), y)
        left, right = (ea, eb) if ea[0] < eb[0] else (eb, ea)
        nl = perp(u) if perp(u)[0] < 0 else mul(perp(u), -1)
        self.flare(f"Loe {name} trái", left, u, nl, (left[0] - FLARE_F, y))
        self.flare(f"Loe {name} phải", right, u, mul(nl, -1), (right[0] + FLARE_F, y))

    def beak(self, name, x_end, y_edge, down=True):
        """L2: beak at an arm end (vertical cut at x_end), hanging from the arm's inner edge."""
        n = (0, -1) if down else (0, 1)
        side = -1 if x_end > self.width / 2 else 1
        self.flare(name, (x_end, y_edge), (side, 0), n, (x_end, y_edge + n[1] * BEAK_B))

    # J1: two outer edges meet a flat cut of width APEX_A on the overshoot line
    def apex_guide(self, p, d1, d2, y):
        self.guides.append(dict(type="apex", p=p, d1=d1, d2=d2, y=y))

    def build(self):
        getattr(self, "g_" + self.name)()
        acc = None
        for s in self.parts:
            if s.kind != "add": continue
            acc = s.to_pathops() if acc is None else pathops.op(acc, s.to_pathops(), pathops.PathOp.UNION)
        for s in self.parts:
            if s.kind == "counter":
                acc = pathops.op(acc, s.to_pathops(), pathops.PathOp.DIFFERENCE)
        self.outline = acc
        return self

    # ------------------------------------------------------------ glyphs
    def stem(self, x0, y0=0, y1=CAP, name="Thân", w=None):
        w = w or self.r["V"]
        return self.part(rect(name, x0, y0, x0 + w, y1))

    def g_I(self):
        x0 = FLARE_F
        self.stem(x0)
        self.stem_flares(x0, x0 + self.r["V"], 0)
        self.stem_flares(x0, x0 + self.r["V"], CAP)

    def g_H(self):
        V, Hb, W = self.r["V"], self.r["Hb"], self.width
        xl, xr = FLARE_F, W - FLARE_F - V
        self.stem(xl, name="Thân trái"); self.stem(xr, name="Thân phải")
        yc = BAR_Y["H"] * CAP
        self.part(rect("Thanh", xl + V - 3, yc - Hb / 2, xr + 3, yc + Hb / 2))
        for x in (xl, xr):
            self.stem_flares(x, x + V, 0); self.stem_flares(x, x + V, CAP)

    def g_E(self):
        V, Hb, W = self.r["V"], self.r["Hb"], self.width
        x0 = FLARE_F
        self.stem(x0)
        self.stem_flares(x0, x0 + V, 0, right=False); self.stem_flares(x0, x0 + V, CAP, right=False)
        self.part(rect("Tay trên", x0 + V - 3, CAP - Hb, W, CAP))
        self.part(rect("Tay dưới", x0 + V - 3, 0, W, Hb))
        yc = BAR_Y["H"] * CAP
        xt = W - Hb * math.tan(MID_ARM_SLANT)
        self.part(poly("Tay giữa", [(x0 + V - 3, yc - Hb / 2), (W, yc - Hb / 2), (xt, yc + Hb / 2), (x0 + V - 3, yc + Hb / 2)]))
        self.beak("Mỏ tay trên", W, CAP - Hb, down=True)
        self.beak("Mỏ tay dưới", W, Hb, down=False)

    def g_L(self):
        V, Hb, W = self.r["V"], self.r["Hb"], self.width
        x0 = FLARE_F
        self.stem(x0)
        self.stem_flares(x0, x0 + V, CAP)
        self.stem_flares(x0, x0 + V, 0, right=False)
        self.part(rect("Tay dưới", x0 + V - 3, 0, W, Hb))
        self.beak("Mỏ tay dưới", W, Hb, down=False)

    def g_T(self):
        V, Hb, W = self.r["V"], self.r["Hb"], self.width
        self.part(rect("Thanh trên", 0, CAP - Hb, W, CAP))
        x0 = W / 2 - V / 2
        self.stem(x0, 0, CAP - Hb + 3)
        self.stem_flares(x0, x0 + V, 0)
        self.beak("Mỏ trái", 0, CAP - Hb, down=True)
        self.beak("Mỏ phải", W, CAP - Hb, down=True)

    def _leg(self, name, outer_foot, outer_top, thick, inward):
        """diagonal leg: outer edge through outer_foot (y=0) and outer_top (y=CAP+OVS_APEX);
        inner edge parallel at perpendicular distance `thick` on the `inward` side (+1 right, -1 left)."""
        d = norm(sub(outer_top, outer_foot))
        nrm_in = perp(d) if (perp(d)[0] > 0) == (inward > 0) else mul(perp(d), -1)
        off = mul(nrm_in, thick)
        yb, yt = 0, CAP + OVS_APEX
        o0 = (line_x_at_y(outer_foot, d, yb), yb); o1 = (line_x_at_y(outer_foot, d, yt), yt)
        ip = add(outer_foot, off)
        i0 = (line_x_at_y(ip, d, yb), yb); i1 = (line_x_at_y(ip, d, yt), yt)
        leg = poly(name, [o0, o1, i1, i0])
        self.part(leg)
        return d, outer_foot, ip, leg

    def g_A(self, flip=False):
        r, W = self.r, self.width
        xc = W / 2
        top_l, top_r = (xc - APEX_A / 2, CAP + OVS_APEX), (xc + APEX_A / 2, CAP + OVS_APEX)
        foot_l, foot_r = (FLARE_F, 0), (W - FLARE_F, 0)
        tl, tr = (r["t"], r["D"]) if not flip else (r["D"], r["t"])
        dl, pl, ipl, legl = self._leg("Chân trái", foot_l, top_l, tl, +1)
        dr, pr, ipr, legr = self._leg("Chân phải", foot_r, top_r, tr, -1)
        # J1: đỉnh nằm gọn giữa hai mép ngoài — cắt mỗi chân theo mép ngoài chân kia
        hull = poly("", [(line_x_at_y(pl, dl, -60), -60), top_l, top_r, (line_x_at_y(pr, dr, -60), -60)]).to_pathops()
        for leg in (legl, legr):
            clipped = pathops.op(leg.to_pathops(), hull, pathops.PathOp.INTERSECTION)
            idx = self.parts.index(leg); self.parts[idx] = shape_from_pathops(leg.name, clipped)
        self.diag_flares(pl, ipl, dl, 0, "chân trái")
        self.diag_flares(pr, ipr, dr, 0, "chân phải")
        self.apex_guide((xc, CAP + OVS_APEX), dl, dr, CAP + OVS_APEX)
        if not flip:
            yc, Hb = BAR_Y["A"] * CAP, r["Hb"]
            xa = line_x_at_y(ipl, dl, yc) - 3; xb = line_x_at_y(ipr, dr, yc) + 3
            self.part(rect("Thanh", xa, yc - Hb / 2, xb, yc + Hb / 2))

    def g_V(self):
        # V = A lật dọc (đỉnh dưới baseline − 12), chân trái dày theo bút
        self.g_A(flip=True)
        fl = lambda p: (p[0], CAP - p[1])
        for s in self.parts:
            s.cmds = [(c[0],) + tuple(fl(p) for p in c[1:]) for c in s.cmds]
        for g in self.guides:
            for k in ("c", "tip", "tangent", "p"):
                if k in g: g[k] = fl(g[k])
            if g["type"] == "compass": g["a0"], g["a1"] = -g["a0"], -g["a1"]
            if g["type"] == "apex":
                g["y"] = CAP - g["y"]; g["d1"] = (g["d1"][0], -g["d1"][1]); g["d2"] = (g["d2"][0], -g["d2"][1])

    def g_N(self):
        """J2: thân mảnh phẳng trên đường kẻ; mép trên chéo qua góc trong-trên thân trái,
        mép dưới chéo qua góc trong-dưới thân phải."""
        r, W = self.r, self.width
        t, D = r["t"], r["D"]
        s0, sR = FLARE_F, W - FLARE_F
        self.stem(s0, 0, CAP, "Thân trái", t)
        self.stem(sR - t, 0, CAP, "Thân phải", t)
        self.stem_flares(s0, s0 + t, 0)
        self.stem_flares(sR - t, sR, CAP)
        P1, P2 = (s0 + t, CAP), (sR - t, 0)
        v = sub(P2, P1)
        L = math.hypot(*v)
        ang = math.atan2(v[1], v[0]) + math.asin(D / L)
        d = (math.cos(ang), math.sin(ang))
        n = perp(d)
        if dot(n, v) < 0: n = mul(n, -1)
        bot = add(P1, mul(n, D))
        pts = [(line_x_at_y(P1, d, CAP), CAP), (line_x_at_y(P1, d, 0), 0), (line_x_at_y(bot, d, 0), 0), (line_x_at_y(bot, d, CAP), CAP)]
        clipped = pathops.op(poly("Chéo", pts).to_pathops(), rect("", s0, 0, sR, CAP).to_pathops(), pathops.PathOp.INTERSECTION)
        self.part(shape_from_pathops("Chéo", clipped))
        self.apex_guide(P1, (0, -1), d, CAP)
        self.apex_guide(P2, (0, 1), mul(d, -1), 0)

    def g_O(self):
        r, W = self.r, self.width
        R = W / 2
        c = (W / 2, CAP / 2)
        self.part(ellipse("Vòng ngoài", c, R, R))
        rx = R - r["Vr"]
        ry = R - (R - (CAP / 2 + OVS_ROUND)) - (r["Hb"] - 6)  # đỉnh/đáy mảnh ≈ Hb − 6
        self.part(ellipse("Lòng", c, rx, ry, rot=math.radians(30), kind="counter"))
        self.guides.append(dict(type="center", c=c))
        self.guides.append(dict(type="axis", c=c, len=ry * 1.1, rot=math.radians(30) + math.pi / 2))

    def g_D(self):
        r, W = self.r, self.width
        V, Hb, Vr = r["V"], r["Hb"], r["Vr"]
        x0 = FLARE_F
        self.stem(x0)
        self.stem_flares(x0, x0 + V, 0, right=False); self.stem_flares(x0, x0 + V, CAP, right=False)
        xm = x0 + V + (W - x0 - V) * 0.25
        self.part(half_ellipse_right("Bụng ngoài", xm, CAP / 2, W - xm, CAP / 2, left_ext=xm - x0 - V + 3))
        xi = x0 + V
        self.part(half_ellipse_right("Lòng", xi, CAP / 2, W - Vr - xi, CAP / 2 - Hb, kappa=KAPPA_IN, kind="counter", left_ext=0))
        self.guides.append(dict(type="center", c=(xm, CAP / 2)))
        self.guides.append(dict(type="center", c=(xi, CAP / 2)))


# ---------------------------------------------------------------- output
def svg_d_from_pathops(p, fy):
    out = []
    for verb, pts in p.segments:
        if verb == "moveTo": out.append("M %.1f %.1f" % (pts[0][0], fy(pts[0][1])))
        elif verb == "lineTo": out.append("L %.1f %.1f" % (pts[0][0], fy(pts[0][1])))
        elif verb == "curveTo": out.append("C " + " ".join("%.1f %.1f" % (q[0], fy(q[1])) for q in pts))
        elif verb == "qCurveTo":
            out.append("Q " + " ".join("%.1f %.1f" % (q[0], fy(q[1])) for q in pts))
        elif verb == "closePath": out.append("Z")
    return " ".join(out)


def svg_d_from_cmds(cmds, fy):
    out = []
    for c in cmds:
        if c[0] == "Z": out.append("Z")
        else: out.append(c[0] + " " + " ".join("%.1f %.1f" % (p[0], fy(p[1])) for p in c[1:]))
    return " ".join(out)


def cell_svg(g, scale=247 / 700, pad=60, top=120, bottom=140):
    """one construction cell as SVG (units → px by `scale`)."""
    adv = g.width + 80
    Wpx = (adv + 2 * pad) * scale
    Hpx = (CAP + top + bottom) * scale
    fx = lambda x: (x + 40 + pad) * scale
    fy = lambda y: (top + CAP - y) * scale
    S = lambda d: d  # already px
    # build glyph paths in px
    def tr_cmds(cmds):
        return [(c[0],) + tuple((fx(p[0]), fy(p[1])) for p in c[1:]) for c in cmds]
    outline_px = pathops.Path()
    for verb, pts in g.outline.segments:
        q = [(fx(x), fy(y)) for x, y in pts]
        getattr(outline_px, {"moveTo": "moveTo", "lineTo": "lineTo", "curveTo": "cubicTo", "closePath": "close", "qCurveTo": "quadTo"}[verb])(*[c for p in q for c in p]) if q else outline_px.close()
    od = svg_d_from_pathops(outline_px, lambda y: y)
    el = []
    C = dict(metric="#B3ADA3", sb="#CCC7BE", glyph="#E6E1D8", ink="#1C1C1C", red="#DB4A2B", blue="#2C68DB", orange="#EC8418")
    # metrics
    for y, dash in ((CAP, None), (0, None), (CAP + OVS_ROUND, "2 3"), (-OVS_ROUND, "2 3")):
        el.append(f'<line x1="0" y1="{fy(y):.1f}" x2="{Wpx:.1f}" y2="{fy(y):.1f}" stroke="{C["metric"]}" stroke-width="{0.75 if not dash else 0.5}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
    for x in (-40, g.width + 40):
        el.append(f'<line x1="{fx(x):.1f}" y1="{fy(CAP + 70):.1f}" x2="{fx(x):.1f}" y2="{fy(-70):.1f}" stroke="{C["sb"]}" stroke-width="0.75" stroke-dasharray="1 3"/>')
    el.append(f'<path d="{od}" fill="{C["glyph"]}" fill-rule="nonzero"/>')
    # parts (clipped to the glyph)
    el.append(f'<clipPath id="g{g.name}{g.weight}"><path d="{od}"/></clipPath>')
    parts = "".join(f'<path d="{svg_d_from_cmds(tr_cmds(s.cmds), lambda y: y)}" fill="none" stroke="{C["red"]}" stroke-width="0.8"/>' for s in g.parts if s.kind == "add")
    el.append(f'<g clip-path="url(#g{g.name}{g.weight})">{parts}</g>')
    for s in g.parts:
        if s.kind == "counter" and not s.name.startswith("cắt"):
            el.append(f'<path d="{svg_d_from_cmds(tr_cmds(s.cmds), lambda y: y)}" fill="none" stroke="{C["blue"]}" stroke-width="0.8"/>')
    el.append(f'<path d="{od}" fill="none" stroke="{C["ink"]}" stroke-width="0.6"/>')
    # guides
    for gd in g.guides:
        if gd["type"] == "compass":
            c, r = gd["c"], gd["r"]
            ext = math.radians(22) * (1 if gd["a1"] > gd["a0"] else -1)
            cmds = [("M", (c[0] + r * math.cos(gd["a0"] - ext), c[1] + r * math.sin(gd["a0"] - ext)))] + arc_cmds(c, r, gd["a0"] - ext, gd["a1"] + ext)
            el.append(f'<path d="{svg_d_from_cmds(tr_cmds(cmds), lambda y: y)}" fill="none" stroke="{C["orange"]}" stroke-width="0.6"/>')
            el.append(f'<line x1="{fx(c[0]):.1f}" y1="{fy(c[1]):.1f}" x2="{fx(gd["tangent"][0]):.1f}" y2="{fy(gd["tangent"][1]):.1f}" stroke="{C["orange"]}" stroke-width="0.5" stroke-dasharray="2 2"/>')
            el.append(f'<circle cx="{fx(c[0]):.1f}" cy="{fy(c[1]):.1f}" r="1.6" fill="{C["orange"]}"/>')
            el.append(f'<circle cx="{fx(gd["tip"][0]):.1f}" cy="{fy(gd["tip"][1]):.1f}" r="1.3" fill="none" stroke="{C["orange"]}" stroke-width="0.6"/>')
        elif gd["type"] == "center":
            x, y = fx(gd["c"][0]), fy(gd["c"][1])
            el.append(f'<path d="M {x-5:.1f} {y:.1f} L {x+5:.1f} {y:.1f} M {x:.1f} {y-5:.1f} L {x:.1f} {y+5:.1f}" stroke="{C["blue"]}" stroke-width="0.75"/>')
        elif gd["type"] == "axis":
            c, L, a = gd["c"], gd["len"], gd["rot"]
            p1 = (c[0] + L * math.cos(a), c[1] + L * math.sin(a)); p2 = (c[0] - L * math.cos(a), c[1] - L * math.sin(a))
            el.append(f'<line x1="{fx(p1[0]):.1f}" y1="{fy(p1[1]):.1f}" x2="{fx(p2[0]):.1f}" y2="{fy(p2[1]):.1f}" stroke="{C["blue"]}" stroke-width="0.6" stroke-dasharray="4 3"/>')
        elif gd["type"] == "apex":
            p, y = gd["p"], gd["y"]
            for d in (gd["d1"], gd["d2"]):
                q = (p[0] + d[0] * 110, p[1] + d[1] * 110)
                el.append(f'<line x1="{fx(p[0]):.1f}" y1="{fy(p[1]):.1f}" x2="{fx(q[0]):.1f}" y2="{fy(q[1]):.1f}" stroke="{C["blue"]}" stroke-width="0.6" stroke-dasharray="4 3"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx:.1f}" height="{Hpx:.1f}" viewBox="0 0 {Wpx:.1f} {Hpx:.1f}">' + "".join(el) + "</svg>", od


CONTROL = ["H", "I", "E", "T", "L", "N", "A", "V", "O", "D"]

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "out", "construct")
    os.makedirs(out, exist_ok=True)
    index = {}
    for w in ("Regular", "Bold"):
        for ch in CONTROL:
            g = Glyph(ch, w).build()
            svg, od = cell_svg(g)
            fn = f"{ch}-{w}"
            open(os.path.join(out, fn + ".svg"), "w").write(svg)
            index[fn] = dict(width=g.width, svg_len=len(svg), parts=[s.name for s in g.parts], guides=len(g.guides))
    json.dump(index, open(os.path.join(out, "index.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: (v["svg_len"], v["guides"]) for k, v in index.items()}))


def figma_svg(g, scale=247 / 700, pad=60, top=120, bottom=140):
    """SVG cho Figma: lớp có id để plugin dựng mask; không dùng clipPath."""
    adv = g.width + 80
    Wpx, Hpx = (adv + 2 * pad) * scale, (CAP + top + bottom) * scale
    fx = lambda x: (x + 40 + pad) * scale
    fy = lambda y: (top + CAP - y) * scale
    tr = lambda cmds: [(c[0],) + tuple((fx(p[0]), fy(p[1])) for p in c[1:]) for c in cmds]
    o = pathops.Path()
    for verb, pts in g.outline.segments:
        q = [v for x, y in pts for v in (fx(x), fy(y))]
        {"moveTo": o.moveTo, "lineTo": o.lineTo, "curveTo": o.cubicTo, "closePath": o.close}[verb](*q)
    od = svg_d_from_pathops(o, lambda y: y)
    D = lambda cmds: svg_d_from_cmds(tr(cmds), lambda y: y)
    C = dict(metric="#B3ADA3", sb="#CCC7BE", glyph="#E6E1D8", ink="#1C1C1C", red="#DB4A2B", blue="#2C68DB", orange="#EC8418")
    m = []
    for y, dash in ((CAP, ""), (0, ""), (CAP + OVS_ROUND, "2 3"), (-OVS_ROUND, "2 3")):
        m.append(f'<path d="M 0 {fy(y):.1f} L {Wpx:.1f} {fy(y):.1f}" stroke="{C["metric"]}" stroke-width="{0.5 if dash else 0.75}"' + (f' stroke-dasharray="{dash}"' if dash else "") + "/>")
    for x in (-40, g.width + 40):
        m.append(f'<path d="M {fx(x):.1f} {fy(CAP + 70):.1f} L {fx(x):.1f} {fy(-70):.1f}" stroke="{C["sb"]}" stroke-width="0.75" stroke-dasharray="1 3"/>')
    parts = "".join(f'<path d="{D(s.cmds)}" fill="none" stroke="{C["red"]}" stroke-width="0.8"/>' for s in g.parts if s.kind == "add")
    counters = "".join(f'<path d="{D(s.cmds)}" fill="none" stroke="{C["blue"]}" stroke-width="0.8"/>' for s in g.parts if s.kind == "counter")
    gd = []
    for q in g.guides:
        if q["type"] == "compass":
            c, r = q["c"], q["r"]
            ext = math.radians(22) * (1 if q["a1"] > q["a0"] else -1)
            cm = [("M", (c[0] + r * math.cos(q["a0"] - ext), c[1] + r * math.sin(q["a0"] - ext)))] + arc_cmds(c, r, q["a0"] - ext, q["a1"] + ext)
            gd.append(f'<path d="{D(cm)}" fill="none" stroke="{C["orange"]}" stroke-width="0.6"/>')
            gd.append(f'<path d="M {fx(c[0]):.1f} {fy(c[1]):.1f} L {fx(q["tangent"][0]):.1f} {fy(q["tangent"][1]):.1f}" stroke="{C["orange"]}" stroke-width="0.5" stroke-dasharray="2 2"/>')
            gd.append(f'<circle cx="{fx(c[0]):.1f}" cy="{fy(c[1]):.1f}" r="1.6" fill="{C["orange"]}"/>')
        elif q["type"] == "center":
            x, y = fx(q["c"][0]), fy(q["c"][1])
            gd.append(f'<path d="M {x-5:.1f} {y:.1f} L {x+5:.1f} {y:.1f} M {x:.1f} {y-5:.1f} L {x:.1f} {y+5:.1f}" stroke="{C["blue"]}" stroke-width="0.75"/>')
        elif q["type"] == "axis":
            c, L, a = q["c"], q["len"], q["rot"]
            gd.append(f'<path d="M {fx(c[0]+L*math.cos(a)):.1f} {fy(c[1]+L*math.sin(a)):.1f} L {fx(c[0]-L*math.cos(a)):.1f} {fy(c[1]-L*math.sin(a)):.1f}" stroke="{C["blue"]}" stroke-width="0.6" stroke-dasharray="4 3"/>')
        elif q["type"] == "apex":
            p = q["p"]
            for dd in (q["d1"], q["d2"]):
                gd.append(f'<path d="M {fx(p[0]):.1f} {fy(p[1]):.1f} L {fx(p[0]+dd[0]*110):.1f} {fy(p[1]+dd[1]*110):.1f}" stroke="{C["blue"]}" stroke-width="0.6" stroke-dasharray="4 3"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx:.1f}" height="{Hpx:.1f}" viewBox="0 0 {Wpx:.1f} {Hpx:.1f}">'
           f'<g id="metrics">{"".join(m)}</g>'
           f'<path id="glyph" d="{od}" fill="{C["glyph"]}"/>'
           f'<g id="parts"><path id="mask" d="{od}" fill="#000"/>{parts}</g>'
           f'<g id="counters">{counters}</g>'
           f'<path id="outline" d="{od}" fill="none" stroke="{C["ink"]}" stroke-width="0.6"/>'
           f'<g id="guides">{"".join(gd)}</g></svg>')
    return svg


def export_figma(names, weights=("Regular", "Bold")):
    out = os.path.join(os.path.dirname(__file__), "..", "..", "out", "construct", "figma")
    os.makedirs(out, exist_ok=True)
    bundle = {}
    for w in weights:
        for ch in names:
            g = Glyph(ch, w).build()
            bundle[f"{ch}-{w}"] = dict(svg=figma_svg(g), width=g.width)
    json.dump(bundle, open(os.path.join(out, "bundle.json"), "w"), ensure_ascii=False)
    return bundle
