#!/usr/bin/env python3
"""QA độ dày nét (designer 05/11: "QA/QC lại đồng bộ hết độ dày các glyph với nhau" — "đảm bảo không glyph nào lỗi nét").
    python3 tools/construct/qa_stroke.py [Regular,Bold] [chars]   → in báo cáo + out/construct/qa_stroke.json

Đo bằng TRỤC GIỮA (medial axis) trên ảnh raster 0.5 px/u: bề dày nét tại mỗi điểm trục = 2 × khoảng cách tới mép.
Bỏ vùng khớp (điểm trục bậc ≥ 3, bán kính 1.3 × nửa bề dày ở đó) và vùng đầu nét (điểm trục bậc 1, bán kính 1.0 × bề dày).
Mỗi glyph:
  T  = phân vị 97 bề dày (nét chính dày)       → so với chuẩn nhóm (hoa: H, thường: n, số: 0) — lệch > ±10 % là lỗi
  Tx = bề dày lớn nhất (ngoài khớp)            → > 1.25 × chuẩn: cục mực
  t  = phân vị 3 (nét mảnh nhất ngoài đầu nét) → < 0.75 × nét mảnh chuẩn (thanh H / đỉnh vòm n): nét quá mảnh
Ký hiệu / dấu câu: so với chuẩn gần nhất trong {hoa, thường} (ký hiệu dựng theo chữ hoa hoặc chữ thường).
"""
import json, os, sys, math, unicodedata
import numpy as np
from scipy import ndimage
from skimage.draw import polygon as skpoly
from skimage.morphology import medial_axis
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'ref'))
import spacing as SPc
from make_ref import outline
import vn_punct as V
OUT = os.path.join(HERE, '..', '..', 'out', 'construct')
SC = 0.5

def polys(o):
    out = []; cur = []; p = None
    for v, ps in o.segments:
        if v == 'moveTo': cur = [ps[0]]; p = ps[0]
        elif v == 'lineTo': cur.append(ps[0]); p = ps[0]
        elif v == 'curveTo': c = (p, *ps); cur += [V.bez(c, k/24) for k in range(1, 25)]; p = ps[2]
        elif v == 'qCurveTo': cur += list(ps); p = ps[-1]
        elif v == 'closePath': out.append(cur)
    return out

def mask_of(d):
    o = outline([d]); P = polys(o)
    xs = [q[0] for c in P for q in c]; ys = [q[1] for c in P for q in c]
    x0, y0 = min(xs) - 6, min(ys) - 6; W = int((max(xs) - x0 + 6)*SC) + 2; H = int((max(ys) - y0 + 6)*SC) + 2
    m = np.zeros((H, W), bool)
    for c in P:
        r = [(y - y0)*SC for _, y in c]; cc = [(x - x0)*SC for x, _ in c]
        rr, ccc = skpoly(r, cc, (H, W)); t = np.zeros((H, W), bool); t[rr, ccc] = True; m ^= t
    return m, (x0, y0)

def measure(d):
    m, org = mask_of(d)
    if m.sum() < 20: return None
    sk, dist = medial_axis(m, return_distance=True)
    # tỉa nhánh: bỏ dần điểm cuối 30 lượt (60 u) — nhánh trục giữa chạy vào góc loe / đầu nét không phải nét
    K3 = np.ones((3, 3), int)
    for _ in range(min(30, int(1.2*dist.max()))):          # ≤ 1.2 × nửa nét lớn nhất: glyph nhỏ (‹ ›) không bị tỉa hết
        dg = ndimage.convolve(sk.astype(int), K3, mode='constant') - 1
        ends = sk & (dg <= 1)
        if not ends.any(): break
        sk = sk & ~ends
    if sk.sum() < 5: sk, dist = medial_axis(m, return_distance=True)
    deg = ndimage.convolve(sk.astype(int), np.ones((3, 3), int), mode='constant') - 1
    keep = sk.copy()
    yy, xx = np.nonzero(sk)
    J = [(y, x) for y, x in zip(yy, xx) if deg[y, x] >= 3]
    E = [(y, x) for y, x in zip(yy, xx) if deg[y, x] <= 1]
    Y, X = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    excl = np.zeros_like(sk)
    for (y, x) in J:
        r = 1.3*dist[y, x] + 1; excl |= (Y - y)**2 + (X - x)**2 <= r*r
    keep &= ~excl
    w = 2*dist[keep]/SC
    if len(w) < 8: keep = sk; w = 2*dist[sk]/SC
    pts = np.argwhere(keep)
    def at(v):                                       # toạ độ font của điểm trục có bề dày gần v
        i = int(np.argmin(np.abs(2*dist[keep]/SC - v))); y, x = pts[i] if len(pts) else (0, 0)
        return round(x/SC + org[0]), round(y/SC + org[1])
    T, Tx, t = float(np.percentile(w, 97)), float(w.max()), float(np.percentile(w, 3))
    return dict(T=round(T, 1), Tx=round(Tx, 1), t=round(t, 1), Tx_at=at(Tx), t_at=at(t))

# nhóm ký hiệu cùng luật nét: mỗi ký tự trong ±10 % trung vị nhóm (cùng weight)
FAM = {
    'gạch / toán': "-\u00ad–—_|¦+−=±×≠≤≥<>¬~≈/\\«»‹›",
    'ngoặc':       "()[]{}§!¡",
    'ký hiệu chữ': "&$¥¢£€@",
    'nháy thẳng':  "'\"′″",
}
SKIP_THIN = set(".:…·•,;‘’‚“”„") | set(SPc.COMB)   # chấm / giọt: trục giữa của hình tròn không đo được nét mảnh

def main():
    O = json.load(open(os.path.join(OUT, 'outlines.json')))
    from weights import WEIGHTS, TW
    ws = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] else list(WEIGHTS)
    only = sys.argv[2] if len(sys.argv) > 2 else None
    chars = sorted({k.rsplit('-', 1)[0] for k in O})
    if only: chars = [c for c in chars if c in only]
    M = {w: {c: measure(O[f'{c}-{w}']) for c in set(chars) | set('Hn0')} for w in ws}
    rep = {}
    for w in ws:
        R = M[w]; ref = {'caps': R['H'], 'lower': R['n'], 'fig': R['0']}
        hair = {'caps': 0.6*_B(w, 40, 68), 'lower': 0.6*(40.4 + 12.7*TW[w]), 'fig': 0.6*_B(w, 40, 68)}
        bad = []
        fmed = {f: float(np.median([R[c]['T'] for c in cs if c in R and R[c]])) for f, cs in FAM.items() if any(c in R for c in cs)}
        for c in chars:
            r = R[c]
            if r is None: continue
            k = SPc.kind(c); iss = []
            if k in ('caps', 'lower', 'fig') and SPc.base(c) == c:
                dv = r['T']/ref[k]['T'] - 1
                if abs(dv) > 0.10: iss.append(f'nét chính {r["T"]:.0f} vs {"Hn0"[["caps","lower","fig"].index(k)]} {ref[k]["T"]:.0f} ({dv*100:+.0f}%)')
                if r['Tx'] > 1.25*ref[k]['T']: iss.append(f'cục mực {r["Tx"]:.0f}@{r["Tx_at"]}')
            for f, cs in FAM.items():
                if c in cs:
                    dv = r['T']/fmed[f] - 1
                    if abs(dv) > 0.10: iss.append(f'nhóm {f}: {r["T"]:.0f} vs trung vị {fmed[f]:.0f} ({dv*100:+.0f}%)')
            kk = k if k in hair else 'caps'
            if c not in SKIP_THIN and r['t'] < hair[kk]: iss.append(f'mảnh {r["t"]:.0f}@{r["t_at"]} (< {hair[kk]:.0f})')
            if iss: bad.append((c, iss))
        rep[w] = dict(ref={k: v['T'] for k, v in ref.items()}, fam=fmed, glyphs={c: R[c] for c in chars}, bad=bad)
        print(f'===== {w}: chuẩn H n 0 =', [ref[k]['T'] for k in ('caps', 'lower', 'fig')], '· nhóm', {f: round(v) for f, v in fmed.items()},
              f'· cần xem: {len(bad)}')
        for c, iss in bad: print(f'  {c!r:6} ' + ' · '.join(iss))
    # ---- chéo weight: nét chính tăng đều R → M → SB → B; tỉ lệ B/R của từng ký tự so với tỉ lệ chuẩn của nhóm ----
    if 'Regular' in ws and 'Bold' in ws:
        print('===== chéo weight')
        nb = 0
        for c in chars:
            Ts = [M[w][c]['T'] for w in ws if M[w][c]]
            if len(Ts) != len(ws): continue
            if any(b < a - 3 for a, b in zip(Ts, Ts[1:])): print(f'  {c!r:6} không tăng: {Ts}'); nb += 1; continue
            k = SPc.kind(c); fam = next((f for f, cs in FAM.items() if c in cs), None)
            if k in ('caps', 'lower', 'fig') and SPc.base(c) == c: rr = M['Bold']['Hn0'[['caps','lower','fig'].index(k)]]['T']/M['Regular']['Hn0'[['caps','lower','fig'].index(k)]]['T']
            elif fam: rr = float(np.median([M['Bold'][x]['T']/M['Regular'][x]['T'] for x in FAM[fam] if x in M['Bold'] and M['Bold'][x] and M['Regular'][x]]))
            else: continue
            r_ = Ts[-1]/Ts[0]
            if abs(r_/rr - 1) > 0.10: print(f'  {c!r:6} B/R {r_:.2f} vs chuẩn {rr:.2f}'); nb += 1
        print(f'  lệch chéo weight: {nb}')
    json.dump(rep, open(os.path.join(OUT, 'qa_stroke.json'), 'w'), ensure_ascii=False, indent=0)

def _B(w, a, b):
    from weights import TW
    return a + (b - a)*TW[w]

if __name__ == '__main__':
    main()
