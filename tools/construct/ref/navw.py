"""S73 (designer 22/11 "Update N và A" + "có cả W và V nữa", Figma 2272:822 — "chỉ tham khảo glyph. Độ dày giữ như hiện tại.
chỉ đổi độ dày thanh chéo N cho dày hơn một chút"): dựng lại N A V W chữ hoa (Regular + Bold) theo dáng bản vẽ, giữ độ dày.

  - Đỉnh / đáy PHẲNG trên đường kẻ (bỏ nhọn vượt 711.3 / −11.3): cắt theo dải 0 … 700.
  - Vạt loe cong (đúng hình Figma, 1 px = 700/247 u):
      A  đỉnh, phía nét DÀY (phải): nhô 40.1 u ngoài mép nét dày, cong về mép đó ở 107.7 u dưới đỉnh
      V  đáy, phía nét MẢNH (phải): nhô 49.8 u ngoài mép nét mảnh, cong về mép đó ở 107.7 u trên đáy
      W  hai đáy, phía phải: như A lật dọc (nhô 43.7 u)
      N  đầu trên thân trái (loe ra trái) + chân thân phải (loe ra phải) = đối xứng dọc của loe sẵn có ở hai thân
  - Thanh chéo N dày hơn: 99.7 → 108 (Regular), 136.8 → 148 (Bold) — hai mép dời ra đều, song song.
  - Nét mảnh: hair_sync / golden đưa về chuẩn như mọi chữ (không đổi ở đây).
Nguồn giữ: designer_A_preNAVW.json, designer_B_preNAVW.json.
    python3 tools/construct/ref/navw.py
"""
import json, math, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import vn_punct as V

PX = 700/247
N_DIAG = {'Regular': 108.0, 'Bold': 148.0}

def parse(d):
    import re
    toks = re.findall(r'[MLCZ]|-?\d+(?:\.\d+)?', d); out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t == 'M': out.append(('M', (float(toks[i+1]), float(toks[i+2])))); i += 3
        elif t == 'L': out.append(('L', (float(toks[i+1]), float(toks[i+2])))); i += 3
        elif t == 'C': out.append(('C', (float(toks[i+1]), float(toks[i+2])), (float(toks[i+3]), float(toks[i+4])), (float(toks[i+5]), float(toks[i+6])))); i += 7
        elif t == 'Z': out.append(('Z',)); i += 1
    return out

def path(ds): return V.U(*[V.P(parse(d)) for d in ds])

def x_at(a, b, y):
    return a[0] + (b[0] - a[0])*(y - a[1])/(b[1] - a[1])

def lines(ds, minlen=200):
    """các đoạn thẳng dài (đỉnh liên tiếp L)"""
    out = []
    for d in ds:
        cur = None; start = None
        for c in parse(d):
            if c[0] == 'M': cur = c[1]; start = cur
            elif c[0] == 'L':
                if math.dist(cur, c[1]) >= minlen: out.append((cur, c[1]))
                cur = c[1]
            elif c[0] == 'C': cur = c[3]
            elif c[0] == 'Z':
                if math.dist(cur, start) >= minlen: out.append((cur, start))
    return out

def flare_top(E0x, y_top, edge, side, D):
    """vạt loe ở đỉnh (A): E0x = mép nét tại y_top; side +1 nhô sang phải; D: bảng toạ độ tương đối (u) [T, P1, C1, C2, P2], P3 trên mép"""
    T, P1, C1, C2, P2 = [(E0x + side*dx, y_top + dy) for dx, dy in D]
    y3 = y_top - 107.7; P3 = (x_at(*edge, y3), y3)
    inner = (P3[0] - side*45, y3); inner2 = (E0x - side*45, y_top)
    return V.P([('M', inner2), ('L', T), ('L', P1), ('C', C1, C2, P2), ('L', P3), ('L', inner), ('Z',)])

# Figma (px, đo từ mép nét tại đường kẻ) → u. A: đỉnh (y xuống trong Figma → âm ở đây)
A_FL = [(14.15*PX, 0), (12.665*PX, -4.009*PX), (8.827*PX, -14.37*PX), (9.447*PX, -25.86*PX), (14.378*PX, -35.75*PX)]
V_FL = [(17.56*PX, 0), (16.90*PX, 1.334*PX), (11.70*PX, 11.756*PX), (11.30*PX, 23.93*PX), (15.81*PX, 34.66*PX)]   # đáy V (y lên)
W_FL = [(15.43*PX, 0), (14.31*PX, 2.25*PX), (9.38*PX, 12.14*PX), (8.76*PX, 23.63*PX), (12.60*PX, 33.99*PX)]

def flare_bot(E0x, edge, D, side=1):
    """vạt loe ở đáy (V, W): E0x = mép nét mảnh phải tại y 0"""
    Q3, Q2, C2, C1, Q1 = [(E0x + side*dx, dy) for dx, dy in D]
    y0 = 107.7; Q0 = (x_at(*edge, y0), y0)
    return V.P([('M', (E0x - side*25, 0)), ('L', Q3), ('L', Q2), ('C', C2, C1, Q1), ('L', Q0), ('L', (Q0[0] - side*28, y0)), ('Z',)])

BAND = V.rect(-200, 0, 1200, 700)

def do_N(ds, w):
    p = V.I(path(ds), BAND)
    d0 = parse(ds[0])
    seq = []                                                                         # (lệnh, điểm đầu)
    cur = None
    for c in d0:
        if c[0] == 'M': cur = c[1]
        elif c[0] in 'LC': seq.append((c, cur)); cur = c[-1]
    vert = sorted({round(c[1][0], 2) for c, a in seq if c[0] == 'L' and abs(c[1][0] - a[0]) < 0.01 and abs(c[1][1] - a[1]) > 300})
    lout, lin, rin, rout = vert[0], vert[1], vert[-2], vert[-1]                      # thân trái ngoài / trong, thân phải trong / ngoài
    L = [(a, c[1]) for c, a in seq if c[0] == 'L' and abs(c[1][0] - a[0]) > 100 and math.dist(a, c[1]) > 300]
    up = max(L, key=lambda l: l[0][1] + l[1][1])                                     # mép trên (đi từ đỉnh trái xuống thân phải)
    lo = min(L, key=lambda l: l[0][1] + l[1][1])
    u = (up[1][0] - up[0][0], up[1][1] - up[0][1]); n_ = math.hypot(*u); nv = (u[1]/n_, -u[0]/n_)
    t0 = abs((lo[0][0] - up[0][0])*nv[0] + (lo[0][1] - up[0][1])*nv[1]); dlt = (N_DIAG[w] - t0)/2
    def strip(l):
        a, b = l; mid = ((a[0] + b[0])/2, (a[1] + b[1])/2)
        sg = 1 if not p.contains((mid[0] + nv[0]*3, mid[1] + nv[1]*3)) else -1          # hướng ra ngoài nét
        e = (sg*nv[0]*dlt, sg*nv[1]*dlt); o = (-sg*nv[0]*4, -sg*nv[1]*4); k = 3000/n_
        a2 = (a[0] - u[0]*k, a[1] - u[1]*k); b2 = (b[0] + u[0]*k, b[1] + u[1]*k)
        return V.P([('M', (a2[0] + o[0], a2[1] + o[1])), ('L', (b2[0] + o[0], b2[1] + o[1])), ('L', (b2[0] + e[0], b2[1] + e[1])), ('L', (a2[0] + e[0], a2[1] + e[1])), ('Z',)])
    keep = V.rect(lin - 6, 0, rin + 6, 700)                                          # mép mới chỉ trong khoảng giữa hai thân
    p = V.U(p, V.I(strip(up), keep), V.I(strip(lo), keep))
    flip = lambda q: (q[0], 700 - q[1])
    # loe chân thân trái: C từ (7.7,13.5) tới (lout, 69.8) → đối xứng dọc: loe đầu thân trái
    cl, al = next((c, a) for c, a in seq if c[0] == 'C' and abs(c[3][0] - lout) < 0.01 and c[3][1] < 350)
    tipl = next(a for c, a in seq if c[0] == 'L' and abs(c[1][0] - al[0]) < 0.01 and abs(c[1][1] - al[1]) < 0.01)   # (0,0) trước (7.7,13.5)
    fl_tl = V.P([('M', (lout + 6, flip(c_ := cl[3])[1])), ('L', flip(cl[3])), ('C', flip(cl[2]), flip(cl[1]), flip(al)), ('L', flip(tipl)), ('L', (lout + 6, 700.0)), ('Z',)])
    # loe đầu thân phải: C từ (491.1,686.5) tới (rout, 630.2), trước đó L (498.8,700) → đối xứng dọc: loe chân thân phải
    cr, ar = next((c, a) for c, a in seq if c[0] == 'C' and abs(c[3][0] - rout) < 0.01 and c[3][1] > 350)
    tipr = next(a for c, a in seq if c[0] == 'L' and abs(c[1][0] - ar[0]) < 0.01 and abs(c[1][1] - ar[1]) < 0.01)
    fl_br = V.P([('M', (rout - 6, flip(cr[3])[1])), ('L', flip(cr[3])), ('C', flip(cr[2]), flip(cr[1]), flip(ar)), ('L', flip(tipr)), ('L', (rout - 6, 0.0)), ('Z',)])
    print(f'  N {w}: thân {lout}/{lin} · {rin}/{rout}; chéo {t0:.1f} → {N_DIAG[w]}')
    return V.U(p, fl_tl, fl_br)

def do_A(ds, w):
    p = V.I(path(ds), BAND)
    L = lines(ds, 300)
    thick = max(L, key=lambda l: max(l[0][0], l[1][0]))                           # mép ngoài nét dày (phải)
    E0x = x_at(*thick, 700.0)
    return V.U(p, flare_top(E0x, 700.0, thick, 1, A_FL))

def do_VW(ds, w, ch):
    p = V.I(path(ds), BAND)
    pts = [c[1] if c[0] in 'ML' else c[3] for d in ds for c in parse(d) if c[0] != 'Z']
    bots = sorted({round(q[0], 2) for q in pts if q[1] < -5})
    # mỗi đáy: cặp điểm đáy (trái, phải); mép mảnh phải = đoạn từ điểm đáy phải đi lên
    pieces = []
    d0 = [c for c in parse(ds[0])]
    seq = [c[1] if c[0] in 'ML' else c[3] for c in d0 if c[0] != 'Z']
    for i, q in enumerate(seq):
        if q[1] < -5:
            nb = [seq[i - 1], seq[(i + 1) % len(seq)]]
            other = [r for r in nb if r[1] < -5]
            up_ = [r for r in nb if r[1] > 0]
            if other and q[0] > other[0][0] and up_:
                e = (q, up_[0]); E0x = x_at(*e, 0.0)
                pieces.append(flare_bot(E0x, e, V_FL if ch == 'V' else W_FL))
    return V.U(p, *pieces)

def main():
    for f, tag, w in (('designer_A.json', 'A', 'Regular'), ('designer_B.json', 'B', 'Bold')):
        fp = os.path.join(HERE, f); keep = os.path.join(HERE, f'designer_{tag}_preNAVW.json')
        if not os.path.exists(keep): shutil.copy(fp, keep)
        src = json.load(open(keep)); out = json.load(open(fp))
        for ch, fn in (('N', do_N), ('A', do_A), ('V', lambda d, w: do_VW(d, w, 'V')), ('W', lambda d, w: do_VW(d, w, 'W'))):
            k = f'{ch}-{w}'; p = fn(src[k], w); p.simplify()
            out[k] = [V.to_d(p)]
            b = p.bounds; print(k, 'y', round(b[1], 1), '…', round(b[3], 1), 'x', round(b[0], 1), '…', round(b[2], 1))
        json.dump(out, open(fp, 'w'), separators=(',', ':'))

if __name__ == '__main__':
    main()
