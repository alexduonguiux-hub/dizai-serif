"""S73 (designer 22/11 "Update N và A" + "có cả W và V nữa", Figma 2272:822 — "chỉ tham khảo glyph. Độ dày giữ như hiện tại.
chỉ đổi độ dày thanh chéo N cho dày hơn một chút"): dựng lại N A V W chữ hoa (Regular + Bold) theo dáng bản vẽ, giữ độ dày.

  - Đỉnh / đáy PHẲNG trên đường kẻ (bỏ nhọn vượt 711.3 / −11.3): cắt theo dải 0 … 700.
  - Vạt loe cong (đúng hình Figma, 1 px = 700/247 u):
      A  đỉnh, phía nét MẢNH (trái; designer 23/11 "update lại móc đỉnh A", trước ở phía nét dày): nhô 44.4 u ngoài mép nét mảnh, cong về mép đó ở 107.7 u dưới đỉnh
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
OLD = 'AVW'          # designer 23/11 "bỏ móc trên A để A, V, W về phiên bản cũ": chỉ N theo bản vẽ mới
VW_FLARE = False     # designer 23/11 "bỏ móc mới của V và W" (giữ đáy phẳng)
FL_K = {'Regular': 1.0, 'Bold': 56.5/42.0}   # designer 23/11 "bold lên thì móc đỉnh A bị nhỏ lại": vạt loe phóng theo tỉ lệ nét mảnh (Bold 1.345)

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

def straighten(cmds, deg=6.0, minlen=60.0):
    """nắn thẳng mép gồm hai đoạn L lệch nhau < deg (W Bold: mép ngoài nét dày gãy 5° ở y 81 — trước nằm trong mũi vượt đáy, cắt đáy phẳng
    làm lộ ra) — bỏ điểm giữa; đường viền xét VÒNG KÍN (điểm gãy có thể là điểm M)"""
    pts = []; kinds = []
    for c in cmds:
        if c[0] == 'M': pts.append(c[1]); kinds.append('L')
        elif c[0] == 'L': pts.append(c[1]); kinds.append('L')
        elif c[0] == 'C': pts.append(c[3]); kinds.append(('C', c[1], c[2]))
    if len(pts) > 1 and math.dist(pts[-1], pts[0]) < 1e-6: pts.pop(); k0 = kinds.pop(); kinds[0] = k0   # đoạn khép tường minh
    changed = True
    while changed and len(pts) > 3:
        changed = False; n = len(pts)
        for i in range(n):
            p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
            if kinds[i] != 'L' or kinds[(i + 1) % n] != 'L': continue        # cả hai đoạn kề điểm i là đoạn thẳng
            if math.dist(p0, p1) < minlen and math.dist(p1, p2) < minlen: continue
            u = (p1[0] - p0[0], p1[1] - p0[1]); v = (p2[0] - p1[0], p2[1] - p1[1])
            if math.hypot(*u) < 1e-6 or math.hypot(*v) < 1e-6: continue
            ang = math.degrees(math.acos(max(-1, min(1, (u[0]*v[0] + u[1]*v[1])/math.hypot(*u)/math.hypot(*v)))))
            if ang < deg: del pts[i]; del kinds[i]; changed = True; break
    out = [('M', pts[0])]
    for i in range(1, len(pts) + 1):
        q = pts[i % len(pts)]; k = kinds[i % len(pts)]
        out.append(('L', q) if k == 'L' else ('C', k[1], k[2], q))
    return out + [('Z',)]

def path(ds, straight=False): return V.U(*[V.P(straighten(parse(d)) if straight else parse(d)) for d in ds])

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

# Vạt loe đo trên Figma theo KHOẢNG CÁCH NGANG TỪ MÉP NÉT ở từng độ cao (px; dương = ra ngoài nét) — mép font dốc khác bản vẽ
# (V 0.448, W 0.372 px/px) nên đặt theo toạ độ tuyệt đối thì đường cong cắt vào mép trước điểm nối (W Bold gãy 10–14°).
# (độ cao từ đường kẻ, khoảng cách ra ngoài): A đỉnh (đo xuống), V W đáy (đo lên). Điểm cuối nằm ĐÚNG trên mép, tay nắm kề dọc mép.
A_FL = [(0, 15.65), (4.009, 12.37), (14.37, 3.887), (25.86, 0.0), (35.75, 0.0)]          # T P1 C1 C2 P2 — rồi P3 trên mép ở 38 px
V_FL = [(0, 17.56), (1.334, 16.30), (11.756, 6.43), (23.926, 0.0), (34.664, 0.0)]        # Q3 Q2 C2 C1 Q1 — rồi Q0 trên mép ở 38 px
W_FL = [(0, 15.43), (2.25, 13.47), (12.14, 4.87), (23.63, 0.0), (33.99, 0.0)]

def flare_top(E0x, y_top, edge, side, D, k=1.0):
    """vạt loe ở đỉnh (A): side −1 nhô sang trái (ra ngoài mép nét mảnh trái)"""
    pts = [(x_at(*edge, y_top - h*PX*k) + side*o*PX*k, y_top - h*PX*k) for h, o in D]
    T, P1, C1, C2, P2 = pts
    y3 = y_top - 38*PX*k; P3 = (x_at(*edge, y3), y3)
    inner = (P3[0] - side*20, y3); inner2 = (E0x - side*20, y_top)
    return V.P([('M', inner2), ('L', T), ('L', P1), ('C', C1, C2, P2), ('L', P3), ('L', inner), ('Z',)])

def flare_bot(E0x, edge, D, side=1, k=1.0):
    """vạt loe ở đáy (V, W): nhô sang phải ra ngoài mép nét mảnh phải"""
    pts = [(x_at(*edge, h*PX*k) + side*o*PX*k, h*PX*k) for h, o in D]
    Q3, Q2, C2, C1, Q1 = pts
    y0 = 38*PX*k; Q0 = (x_at(*edge, y0), y0)
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
    L = [l for l in lines(ds, 300) if abs(l[0][0] - l[1][0]) > 100]
    thin = min(L, key=lambda l: min(l[0][0], l[1][0]))                            # mép ngoài nét MẢNH (trái) — designer 23/11 "update lại móc đỉnh A"
    E0x = x_at(*thin, 700.0)
    return V.U(p, flare_top(E0x, 700.0, thin, -1, A_FL, FL_K[w]))

def do_VW(ds, w, ch):
    p = V.I(path(ds, straight=True), BAND)
    if not VW_FLARE: return p                                                     # designer 23/11 "bỏ móc mới của V và W": chỉ đáy phẳng
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
                pieces.append(flare_bot(E0x, e, V_FL if ch == 'V' else W_FL, k=FL_K[w]))
    return V.U(p, *pieces)

def main():
    for f, tag, w in (('designer_A.json', 'A', 'Regular'), ('designer_B.json', 'B', 'Bold')):
        fp = os.path.join(HERE, f); keep = os.path.join(HERE, f'designer_{tag}_preNAVW.json')
        if not os.path.exists(keep): shutil.copy(fp, keep)
        src = json.load(open(keep)); out = json.load(open(fp))
        for ch in OLD:                                                       # designer 23/11 "bỏ móc trên A để A, V, W về phiên bản cũ"
            out[f'{ch}-{w}'] = src[f'{ch}-{w}']
        if w == 'Bold':                                                      # S76 (designer 23/11 "A lỗi chân các weight"): chân trái
            o_ = 'L135.2 81.7C134.1 79.2 133.3 71.4 133.3 71.3C126 47.3 124.8 21.7 137.4 0'   # A Bold: tay nắm suy biến (71.4 → 71.3)
            n_ = 'L135.2 81.7C122.5 54.5 124.8 21.7 137.4 0'                  # → một cung, tiếp tuyến theo mép chân (hướng 171.2,158.7 → 135.2,81.7)
            assert o_ in out['A-Bold'][0]; out['A-Bold'] = [out['A-Bold'][0].replace(o_, n_)]
        for ch, fn in (('N', do_N), ('A', do_A), ('V', lambda d, w: do_VW(d, w, 'V')), ('W', lambda d, w: do_VW(d, w, 'W'))):
            if ch in OLD: continue
            k = f'{ch}-{w}'; p = fn(src[k], w); p.simplify()
            out[k] = [V.to_d(p)]
            b = p.bounds; print(k, 'y', round(b[1], 1), '…', round(b[3], 1), 'x', round(b[0], 1), '…', round(b[2], 1))
        json.dump(out, open(fp, 'w'), separators=(',', ':'))

if __name__ == '__main__':
    main()
