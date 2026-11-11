#!/usr/bin/env python3
"""S38 Mép ngoài bụng số 2 liền độ cong (designer 11/11: "cảm giác đường cong vẫn còn gợn chứ không có mượt").
    python3 tools/construct/ref/fix_2_fair.py      (đi từ bản lưu designer_B_pre2fair.json → chạy lại cho cùng kết quả)

Đo độ cong dọc mép ngoài bụng (đỉnh → vai → cực phải → vào nét chéo): lên – tụt – lên lại (Regular −6.1 → −2.9 → −8.2 ×10⁻³,
Bold −5.9 → −4.0 → −5.8) và nhảy −2.2 → 0 ngay đỉnh = "gợn". Làm mượt cả CHUỖI (không chỉ từng nút):
  - cố định: góc đầu nét trái (29, 656), điểm vào nét chéo (vị trí + tiếp tuyến), ĐỈNH (y = 711.3, tiếp tuyến ngang),
    CỰC PHẢI (x = bề ngang, tiếp tuyến đứng) — chiều cao, bề ngang số giữ nguyên;
  - được đổi: độ dài mọi tay nắm; đỉnh trượt ngang, cực phải trượt dọc; nút vai dời và xoay nhẹ (giới hạn LIM);
  - mục tiêu: Σ (dκ/ds)² trên toàn chuỗi (độ cong biến thiên đều) + phạt nhảy độ cong tại nút + phạt độ cong tụt rồi lên lại (một đỉnh duy nhất); ràng buộc lệch ≤ MAXDEV u (Regular 4, Bold 3)
    so với bản vẽ (Figma).
"""
import json, math, os, shutil, sys
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, '..'), os.path.join(HERE, '..', 'font')]
MAXDEV = {'2-Regular': 4.0, '2-Bold': 3.0}   # Regular: 3 u chưa đủ gỡ chỗ tụt độ cong giữa vai và cực phải
LIM = (30.0, 10.0, 10.0, 6.0, 25.0)   # đỉnh trượt ngang · vai dx, dy · vai xoay (°) · cực phải trượt dọc (trượt trên tiếp tuyến ≈ không đổi hình)
# chuỗi mép ngoài: (điểm đầu cố định, đỉnh, vai, cực phải, điểm vào chéo)
CHAIN = {'2-Regular': [(28.9, 656.2), (206.6, 711.3), (424.3, 618.6), (458.2, 511.5), (265.4, 254.3)],
         '2-Bold':    [(28.8, 656.1), (230.2, 711.3), (446.7, 616.4), (476.4, 511.5), (298.8, 270.6)]}

def bez(P, t):
    u = 1 - t; return u**3*P[0] + 3*u*u*t*P[1] + 3*u*t*t*P[2] + t**3*P[3]
def d1(P, t):
    u = 1 - t; return 3*u*u*(P[1] - P[0]) + 6*u*t*(P[2] - P[1]) + 3*t*t*(P[3] - P[2])
def d2(P, t):
    u = 1 - t; return 6*u*(P[2] - 2*P[1] + P[0]) + 6*t*(P[3] - 2*P[2] + P[1])
def kap(P, t):
    a, b = d1(P, t), d2(P, t); s = np.hypot(*a); return (a[0]*b[1] - a[1]*b[0])/s**3
TS = np.linspace(0, 1, 33)

def unit(v): v = np.asarray(v, float); return v/np.hypot(*v)

def find(S, pts):
    """chỉ số các đoạn của chuỗi: đoạn i đi từ pts[k] tới pts[k+1]"""
    n = len(S); idx = []
    for k in range(len(pts) - 1):
        i = next(i for i in range(n) if S[i][0] == 'C' and math.dist(S[i][1], pts[k]) < 1 and math.dist(S[i][4], pts[k + 1]) < 1)
        idx.append(i)
    return idx

def build(S, idx, x, base):
    """x: [la0,lb0, la1,lb1, la2,lb2, la3,lb3, apex_dx, sh_dx, sh_dy, sh_rot, rx_dy] (độ dài tay = tỉ lệ × gốc)"""
    P = base
    nodes = [P[0][0], P[0][3], P[1][3], P[2][3], P[3][3]]
    T = [unit(base[0][1] - base[0][0]), unit(base[1][1] - base[1][0]), unit(base[2][1] - base[2][0]),
         unit(base[3][1] - base[3][0]), unit(base[3][3] - base[3][2])]
    N = [np.array(p, float) for p in nodes]
    N[1] = N[1] + [x[8], 0]
    N[2] = N[2] + [x[9], x[10]]
    a = math.radians(x[11]); c, s_ = math.cos(a), math.sin(a); T[2] = np.array([T[2][0]*c - T[2][1]*s_, T[2][0]*s_ + T[2][1]*c])
    N[3] = N[3] + [0, x[12]]
    L0 = [(np.hypot(*(b[1] - b[0])), np.hypot(*(b[3] - b[2]))) for b in base]
    out = []
    for k in range(4):
        A, D = N[k], N[k + 1]
        out.append(np.array([A, A + T[k]*L0[k][0]*x[2*k], D - T[k + 1]*L0[k][1]*x[2*k + 1], D]))
    return out

def sample(segs):
    pts, ks = [], []
    for P in segs:
        for t in TS: pts.append(bez(P, t)); ks.append(kap(P, t))
    return np.array(pts), np.array(ks)

def fair_chain(S, key):
    idx = find(S, CHAIN[key])
    base = [np.array([S[i][1], S[i][2], S[i][3], S[i][4]], float) for i in idx]
    ref, _ = sample(base)
    dense = np.concatenate([[bez(P, t) for t in np.linspace(0, 1, 400)] for P in base])
    def devmax(segs):
        p, _ = sample(segs); return max(np.min(np.hypot(*(dense - q).T)) for q in p)
    def cost(x):
        segs = build(S, idx, x, base); p, k = sample(segs)
        ds = np.hypot(*np.diff(p, axis=0).T); dk = np.diff(k)
        m = ds > 1e-6; e = float(np.sum(dk[m]**2/ds[m]))*1e3
        jump = sum((kap(segs[j], 1) - kap(segs[j + 1], 0))**2 for j in range(3))*1e5
        a_ = np.abs(k)*1e3; pre = np.maximum.accumulate(a_); post = np.maximum.accumulate(a_[::-1])[::-1]
        dip = 50*float(np.sum(np.maximum(0, np.minimum(pre, post) - a_)**2))   # một đỉnh độ cong: không tụt rồi lên lại
        e += dip + 1e3*float(np.sum(np.maximum(0, k*1e3)**2))   # mép ngoài bụng cong một chiều (κ < 0), không gợn ngược
        dv = devmax(segs); pen = 1e3*max(0, dv - MAXDEV[key])**2
        box = 1e3*sum(max(0, abs(v) - lim)**2 for v, lim in zip(x[8:], LIM))
        hl = 1e3*sum(max(0, 0.5 - v)**2 + max(0, v - 1.8)**2 for v in x[:8])
        return e + jump + pen + box + hl
    x0 = np.array([1.0]*8 + [0, 0, 0, 0, 0])
    r = minimize(cost, x0, method='Powell', options=dict(maxiter=20000, xtol=1e-4, ftol=1e-9))
    segs = build(S, idx, r.x, base)
    for i, P in zip(idx, segs): S[i] = ['C'] + [tuple(map(float, q)) for q in P]
    # đoạn kế cận dùng chung nút: cập nhật điểm đầu / cuối
    n = len(S)
    for i in idx:
        j = (i + 1) % n
        if S[j][0] in ('C', 'L'): S[j][1] = S[i][4]
    return S, r, devmax(segs)

def run(d, key):
    from interp import contours
    from compat import to_d
    cs = [[list(x) for x in S] for S in contours([d])]
    out = []
    for S in cs:
        try: S, r, dv = fair_chain(S, key); print(f'  {key}: lệch {dv:.2f} u · x = {np.round(r.x, 3).tolist()}')
        except StopIteration: pass
        out.append(S)
    return to_d(out)

if __name__ == '__main__':
    p = os.path.join(HERE, 'designer_B.json'); keep = os.path.join(HERE, 'designer_B_pre2fair.json')
    if not os.path.exists(keep): shutil.copy(p, keep)
    src = json.load(open(keep)); D = json.load(open(p))
    for k in (sys.argv[1:] or ('2-Regular', '2-Bold')):
        D[k] = [run(src[k][0], k)]
    json.dump(D, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
