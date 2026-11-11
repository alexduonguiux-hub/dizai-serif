#!/usr/bin/env python3
"""S39 Mép ngoài bụng S liền độ cong (designer 11/11: "kiểm tra lại đường cong chữ S theo cách này luôn" — cách S38 số 2).
    python3 tools/construct/ref/fix_S_fair.py      (đi từ bản lưu designer_{A,B}_preSfair.json → chạy lại cho cùng kết quả)

Độ cong mép ngoài tụt rồi lên lại tại cực trị (gợn): bụng trên cực trái Regular −5.4 → −2.4 | −6.4 → −7.4 (tỉ 2.7), Bold 2.0;
bụng dưới cực phải Regular −5.1 → −2.4 | −4.5 → −5.9 (1.9). Làm mượt CẢ CHUỖI mép ngoài mỗi bụng (cách fix_2_fair):
  - cố định: điểm uốn sống (vị trí + tiếp tuyến), góc đầu nét (tay suy biến giữ suy biến);
  - cực trái / phải trượt DỌC, đỉnh / đáy trượt NGANG trên tiếp tuyến của nó (bề ngang, chiều cao giữ); mọi tay đổi độ dài (giữ hướng);
  - mục tiêu: Σ (dκ/ds)² + nhảy độ cong tại nút + độ cong tụt rồi lên lại (một đỉnh) + cấm đổi chiều cong; lệch ≤ MAXDEV u so với
    bản vẽ (S34/S35 đã duyệt).
"""
import json, math, os, shutil, sys
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, '..'), os.path.join(HERE, '..', 'font')]
MAXDEV = 3.0
LIM = 25.0                                   # trượt tối đa trên tiếp tuyến (u)
# chuỗi: [(nút, kiểu)] — 'x' cố định, 'v' trượt dọc, 'h' trượt ngang, 't' trượt dọc tiếp tuyến của nút
CHAINS = {'S-Regular': [[((274, 385), 'x'), ((394, 170), 'v'), ((199, -14), 'x')],   # dừng ở ĐÁY: kéo cả đuôi → độ cong rơi
                                                                                  # gắt ngay sau đáy (−5.3 → −2.2)
                        [((129, 352), 'x'), ((0, 555), 'v'), ((204, 711), 'x')],
                        # LÒNG (11/11, lược độ cong): lòng dưới cực phải 4.5 | 5.3 → 7.9, lòng trên cực trái 5.3 | 8.2 → 10.7
                        [((11.3, 146.7), 'x'), ((185.3, 23.9), 't'), ((297.5, 164.7), 't'), ((128.6, 351.6), 'x')],
                        [((354.2, 570.3), 'x'), ((198.3, 673.3), 't'), ((96.3, 549.4), 't'), ((273.7, 385.3), 'x')]],
          'S-Bold':    [[((149, 330), 'x'), ((0, 546), 'v'), ((223, 711), 'x')],      # bụng dưới Bold đã liền (tỉ 1.23): giữ
                        [((25.8, 201.6), 'x'), ((229.4, 67.4), 't'), ((328.9, 145.2), 't'), ((148.7, 329.5), 'x')],
                        [((416.9, 518.0), 'x'), ((221.4, 631.4), 't'), ((143.7, 551.7), 't'), ((330.6, 389.9), 'x')]]}
# bụng trên: chuỗi dừng ở ĐỈNH (cố định) — tay trên (đỉnh → đầu nét) vốn liền với đỉnh; kéo cả tay → cong gắt ngay sau đỉnh
TS = np.linspace(0, 1, 33)

def bez(P, t):
    u = 1 - t; return u**3*P[0] + 3*u*u*t*P[1] + 3*u*t*t*P[2] + t**3*P[3]
def kap(P, t):
    u = 1 - t
    a = 3*u*u*(P[1] - P[0]) + 6*u*t*(P[2] - P[1]) + 3*t*t*(P[3] - P[2]); b = 6*u*(P[2] - 2*P[1] + P[0]) + 6*t*(P[3] - 2*P[2] + P[1])
    s = np.hypot(*a); return (a[0]*b[1] - a[1]*b[0])/s**3 if s > 1e-9 else np.nan

def find(S, nodes):
    n = len(S); idx = []
    for k in range(len(nodes) - 1):
        idx.append(next(i for i in range(n) if S[i][0] == 'C' and math.dist(S[i][1], nodes[k]) < 2 and math.dist(S[i][4], nodes[k + 1]) < 2))
    return idx

def fair_chain(S, spec):
    nodes = [p for p, _ in spec]; kinds = [k for _, k in spec]
    idx = find(S, nodes); base = [np.array(S[i][1:], float) for i in idx]; m = len(base)
    L0 = [(np.hypot(*(b[1] - b[0])), np.hypot(*(b[3] - b[2]))) for b in base]
    D0 = [((b[1] - b[0])/L if L > 1.0 else None, (b[2] - b[3])/M if M > 1.0 else None) for b, (L, M) in zip(base, L0)]   # tay < 1 u: suy biến, giữ
    N = [base[0][0]] + [b[3] for b in base]
    free = [k for k in range(len(N)) if kinds[k] != 'x']
    TG = {k: (base[k][1] - base[k][0])/np.hypot(*(base[k][1] - base[k][0])) for k in range(1, len(N) - 1)}   # tiếp tuyến tại nút trong
    dense = np.concatenate([[bez(P, t) for t in np.linspace(0, 1, 400)] for P in base])
    sgn = np.sign(np.nanmedian([kap(P, t) for P in base for t in TS]))
    def build(x):
        Nn = [p.copy() for p in N]
        for q, k in enumerate(free):
            if kinds[k] == 't': Nn[k] = Nn[k] + TG[k]*x[2*m + q]
            else: Nn[k] = Nn[k] + (np.array([0.0, x[2*m + q]]) if kinds[k] == 'v' else np.array([x[2*m + q], 0.0]))
        out = []
        for k in range(m):
            A, B = Nn[k], Nn[k + 1]; da, db = D0[k]
            p1 = A + da*L0[k][0]*x[2*k] if da is not None else base[k][1] - base[k][0] + A
            p2 = B + db*L0[k][1]*x[2*k + 1] if db is not None else base[k][2] - base[k][3] + B
            out.append(np.array([A, p1, p2, B]))
        return out
    def sample(segs):
        p, k = [], []
        for P in segs:
            for t in TS: p.append(bez(P, t)); k.append(kap(P, t))
        return np.array(p), np.array(k)
    def devmax(segs):
        p, _ = sample(segs); return max(np.min(np.hypot(*(dense - q).T)) for q in p)
    n_ = len(S); nxt, prv = S[(idx[-1] + 1) % n_], S[(idx[0] - 1) % n_]
    k_next = kap(np.array(nxt[1:], float), 0)*1e3 if nxt[0] == 'C' else np.nan   # đoạn kế NGOÀI chuỗi (không đổi): độ cong ở
    k_prev = kap(np.array(prv[1:], float), 1)*1e3 if prv[0] == 'C' else np.nan   # chỗ nối phải khớp
    def cost(x):
        segs = build(x); p, k = sample(segs)
        k = k*sgn*1e3; ok = np.isfinite(k) & (np.abs(k) < 60); p, k = p[ok], k[ok]   # κ dương = cong đúng chiều bụng; bỏ mẫu
                                                                        # sát tay tí hon ở góc đầu nét
        ds = np.hypot(*np.diff(p, axis=0).T); dk = np.diff(k); mm = ds > 1e-6
        e = float(np.sum(dk[mm]**2/ds[mm]))
        jump = 0.0
        for a, b in zip(segs, segs[1:]):
            ka, kb = kap(a, 1)*1e3, kap(b, 0)*1e3
            if np.isfinite(ka) and np.isfinite(kb) and max(abs(ka), abs(kb)) < 60: jump += (ka - kb)**2
        for kx, ki in ((k_next, kap(segs[-1], 1)*1e3), (k_prev, kap(segs[0], 0)*1e3)):
            if np.isfinite(kx) and np.isfinite(ki) and max(abs(kx), abs(ki)) < 60 and abs(kx) > 1.0: jump += 10*(kx - ki)**2   # khớp đoạn ngoài chuỗi (sống)
        pre = np.maximum.accumulate(k); post = np.maximum.accumulate(k[::-1])[::-1]
        dip = 50*float(np.sum(np.maximum(0, np.minimum(pre, post) - k)**2))
        neg = 1e3*float(np.sum(np.maximum(0, -k[3:-3])**2))           # bỏ hai đầu (điểm uốn sống, góc đầu nét)
        pen = 3e4*max(0, devmax(segs) - MAXDEV)**2
        box = 1e3*sum(max(0, abs(v) - LIM)**2 for v in x[2*m:])
        hl = 1e3*sum(max(0, 0.5 - v)**2 + max(0, v - 1.8)**2 for v in x[:2*m]) + 1e3*sum(v*v for v in x[2*m + len(free):])
        return e + 100*jump + dip + neg + pen + box + hl
    x0 = np.array([1.0]*(2*m) + [0.0]*len(free))
    r = minimize(cost, x0, method='Powell', options=dict(maxiter=30000, xtol=1e-4, ftol=1e-10))
    segs = build(r.x)
    for i, P in zip(idx, segs): S[i] = ['C'] + [tuple(map(float, q)) for q in P]
    n = len(S)
    for i in idx:
        j = (i + 1) % n; S[j][1] = S[i][4]
        h = (i - 1) % n; S[h] = list(S[h]); S[h][-1] = S[i][1]
    return r, devmax(segs)

def run(d, key):
    from interp import contours
    from compat import to_d
    cs = [[list(x) for x in S] for S in contours([d])]
    for spec in CHAINS[key]:
        for S in cs:
            try: r, dv = fair_chain(S, spec); print(f'  {key} chuỗi {spec[1][0]}: lệch {dv:.2f} u · {np.round(r.x, 3).tolist()}'); break
            except StopIteration: continue
    return to_d(cs)

if __name__ == '__main__':
    for f, k in (('designer_A.json', 'S-Regular'), ('designer_B.json', 'S-Bold')):
        if len(sys.argv) > 1 and k not in sys.argv[1:]: continue
        p = os.path.join(HERE, f); keep = os.path.join(HERE, f.replace('.json', '_preSfair.json'))
        if not os.path.exists(keep): shutil.copy(p, keep)
        src = json.load(open(keep)); D = json.load(open(p))
        D[k] = [run(src[k][0], k)]
        json.dump(D, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
