#!/usr/bin/env python3
"""S40 S Regular vẽ lại bởi designer (12/11: "Update lại đường cong bụng chữ S" + "Update lại lần nữa" — tay trên rộng thêm
3 đv Figma; + "Tôi có update nét bụng 1 chút" — lòng bụng dưới ±1 đv; Figma 2145:1228 → vector 2179:2 "s").
    python3 tools/construct/ref/fix_S_figma2.py     → designer_A.json['S-Regular'] (chạy lại cho cùng kết quả)

Bản vẽ mới 133.02 × 239.25 (Figma) — tỉ lệ khác bản 06/11 (2.8341). Quy đổi theo CHIỀU CAO S (đáy −14.2, đỉnh 711.3 — giữ
overshoot): x = k·X, y = 711.3 − k·Y, k = 725.5 / 239.25 = 3.0324; kiểm: mặt cắt hai đầu nét 39.6 × k = 120 u (bản cũ 119.3).
Bản vẽ designer là chuẩn: thay S34 / S35 / S39 (fix_S_g2, fix_S_fair) cho S Regular; S Bold giữ (khung 2145:1227 chưa vẽ lại).

Vector mới 39 đoạn, nút gãy 1–3.1° (đường nhiều điểm), khác cấu trúc 14 đoạn của S Bold → DỰNG LẠI đúng cấu trúc S Bold:
  1. neo trên bản vẽ mới: cực trị (trái / phải / đỉnh / đáy, mép ngoài + lòng), điểm uốn sống (đổi chiều cong), góc đầu nét;
     tiếp tuyến lấy từ bản vẽ (cực trị: đúng đứng / ngang);
  2. mỗi đoạn một cubic, độ dài hai tay khớp bình phương tối thiểu (khoảng cách hai chiều) — lệch ≤ 2.2 u;
  3. làm mượt độ cong các chuỗi như S39 (fix_S_fair.fair_chain), lệch thêm ≤ MAXDEV u.
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
FIGMA_R2 = ("M31.68 53.46 C31.68 60.28 34.22 66.11 37.3 70.95 C40.6 75.79 45 80.19 50.5 84.15 C56 87.89 62.27 91.63 69.31 95.37 C76"
            ".35 99.11 86.023 104.688 93.42 109.58 C107.859 119.13 114.806 126.752 122.11 137.61 C129.859 149.13 133.02 162.91 133."
            "02 178.53 C133.02 190.85 128.16 201.63 122.44 210.87 C116.72 219.89 109.02 226.93 99.34 231.99 C89.66 236.83 78.77 239"
            ".25 66.67 239.25 C59.85 239.25 52.81 238.59 45.55 237.27 C38.29 235.95 31.58 234.41 25.42 232.65 C19.26 230.67 14.2 22"
            "9.02 10.24 227.7 C6.5 226.38 4.63 225.72 4.63 225.72 L4.63 186.12 C8.37 193.16 13.43 199.76 19.81 205.92 C26.19 212.08"
            " 32.12 217.14 39.6 221.1 C47.08 224.84 55.23 226.71 62.05 226.71 C68.65 226.71 75.7 224.73 81.2 220.77 C86.92 216.59 9"
            "2.43 210.98 95.73 203.94 C99.25 196.9 101.01 188.98 101.01 180.18 C101.01 170.28 97.03 162.14 93.07 155.76 C89.11 149."
            "38 83.06 143.44 74.92 137.94 C66.78 132.44 56.33 125.95 43.57 118.47 C30.81 110.99 21.35 103.29 15.19 95.37 C9.25 87.4"
            "5 0 76.6299 0 52.48 C0 42.14 3.86 32.12 9.58 24.42 C15.3 16.72 23.22 10.78 33.34 6.6 C43.46 2.2 58.12 0 71.32 0 C77.48"
            " 0 83.42 0.33 89.14 0.99 C95.08 1.65 100.36 2.53 104.98 3.63 C109.82 4.51 113.67 5.28 116.53 5.94 C119.39 6.6 120.82 6"
            ".93 120.82 6.93 L120.82 46.53 C117.96 41.25 114.44 36.52 110.26 32.34 C106.3 28.16 101.9 24.64 97.06 21.78 C92.22 18.7"
            " 87.38 16.39 82.54 14.85 C77.92 13.31 73.52 12.54 69.34 12.54 C60.54 12.54 49.73 16.17 42.91 23.43 C36.09 30.47 31.68 "
            "40.48 31.68 53.46 Z")
K, Y0 = 725.5/239.25, 711.3
MAXDEV = 2.0
# neo (xấp xỉ, tinh chỉnh trên bản vẽ) theo thứ tự cấu trúc S Bold; kiểu: cực trị trục / điểm uốn / góc
ANCH = [((96.07, 549.19), 'xmin'), ((210, 422), 'infl'), ((403.37, 170), 'xmax'), ((202, -14.2), 'ymin'), ((14.04, 26.8), 'pt'),
        ((14.04, 146.9), 'pt'), ((188, 24), 'ymin'), ((306, 165), 'xmax'), ((132, 352), 'infl'), ((0, 552), 'xmin'),
        ((216, 711.3), 'ymax'), ((366.4, 690.3), 'pt'), ((366.4, 570.2), 'pt'), ((210, 673), 'ymax')]
LINES = (4, 11)                    # mặt cắt đầu nét (cạnh thẳng)
# chuỗi làm mượt theo CHỈ SỐ neo (thứ tự ANCH): 'x' cố định, 'v' trượt dọc, 't' trượt dọc tiếp tuyến
CHAINS = [[(1, 'x'), (2, 'v'), (3, 'x')],                  # mép ngoài bụng dưới (điểm uốn → cực phải → đáy)
          [(8, 'x'), (9, 'v'), (10, 'x')],                 # mép ngoài bụng trên (điểm uốn → cực trái → đỉnh)
          [(5, 'x'), (6, 't'), (7, 't'), (8, 'x')],        # lòng dưới
          [(12, 'x'), (13, 't'), (0, 't'), (1, 'x')]]      # lòng trên


def rebuild(d):
    import sys; sys.path[:0] = [HERE, os.path.join(HERE, '..'), os.path.join(HERE, '..', 'font')]
    import numpy as np
    from scipy.optimize import least_squares
    from interp import contours
    S = contours([d])[0]
    bez = lambda P, t: (1 - t)**3*P[0] + 3*(1 - t)**2*t*P[1] + 3*(1 - t)*t*t*P[2] + t**3*P[3]
    pts, tan = [], []
    for sg in S:
        if sg[0] == 'L':
            A, B = np.array(sg[1]), np.array(sg[2])
            for t in np.linspace(0, 1, 60, endpoint=False): pts.append(A + (B - A)*t); tan.append((B - A)/np.hypot(*(B - A)))
        else:
            P = np.array(sg[1:], float)
            for t in np.linspace(0, 1, 200, endpoint=False):
                u = 1 - t; dv = 3*u*u*(P[1] - P[0]) + 6*u*t*(P[2] - P[1]) + 3*t*t*(P[3] - P[2]); L = np.hypot(*dv)
                pts.append(bez(P, t)); tan.append(dv/L if L > 1e-9 else np.array([np.nan, np.nan]))
    pts, tan = np.array(pts), np.array(tan); N = len(pts)
    T = lambda q: tan[q] if np.all(np.isfinite(tan[q])) else tan[(q + 3) % N]
    def refine(p, kind):
        i = int(np.argmin(np.hypot(*(pts - np.array(p)).T))); win = [(i + d_) % N for d_ in range(-300, 301)]
        if kind == 'xmin': return min(win, key=lambda q: pts[q][0])
        if kind == 'xmax': return max(win, key=lambda q: pts[q][0])
        if kind == 'ymin': return min(win, key=lambda q: pts[q][1])
        if kind == 'ymax': return max(win, key=lambda q: pts[q][1])
        if kind == 'infl':
            turn = lambda q: T((q - 2) % N)[0]*T((q + 2) % N)[1] - T((q - 2) % N)[1]*T((q + 2) % N)[0]
            c = [q for q in win[50:-50] if turn(q)*turn((q + 1) % N) < 0]
            return min(c, key=lambda q: abs(q - i)) if c else i
        return i
    I = [refine(p, k) for p, k in ANCH] + []; I.append(I[0])
    def tdir(k, j, side):                                      # hướng đi tới tại neo k
        kind = ANCH[k % len(ANCH)][1]; t = T(j if side == 'out' else (j - 3) % N)
        if kind in ('xmin', 'xmax'): return np.array([0.0, np.sign(t[1])])
        if kind in ('ymin', 'ymax'): return np.array([np.sign(t[0]), 0.0])
        return t
    segs, devs = [], []
    for k in range(len(ANCH)):
        a, b = I[k], I[k + 1]
        if k in LINES: segs.append(['L', tuple(pts[a]), tuple(pts[b])]); continue
        Q = pts[[(a + q) % N for q in range(((b - a) % N) + 1)]]
        P0, P3 = pts[a], pts[b]
        d0 = T((a + 3) % N) if ANCH[k][1] == 'pt' else tdir(k, a, 'out')
        d1 = -T((b - 3) % N) if ANCH[(k + 1) % len(ANCH)][1] == 'pt' else -tdir(k + 1, b, 'in')
        L = np.hypot(*(P3 - P0)); Ts = np.linspace(0, 1, 120)
        def res(x):
            C = np.array([P0, P0 + d0*x[0], P3 + d1*x[1], P3]); B = np.array([bez(C, t) for t in Ts]); q = Q[::4]
            return np.concatenate([np.min(np.hypot(*(B[:, None, :] - q[None]).transpose(2, 0, 1)), 1),
                                   np.min(np.hypot(*(q[:, None, :] - B[None]).transpose(2, 0, 1)), 1)])
        r = least_squares(res, [L/3, L/3], bounds=([1, 1], [L, L]))
        segs.append(['C', tuple(P0), tuple(P0 + d0*r.x[0]), tuple(P3 + d1*r.x[1]), tuple(P3)]); devs.append(res(r.x).max())
    segs = [[s_[0]] + [(round(float(p[0]), 2), round(float(p[1]), 2)) for p in s_[1:]] for s_ in segs]
    for i in range(len(segs)): segs[i][1] = segs[i - 1][-1] if i else segs[i][1]
    print('  dựng lại 14 đoạn, lệch tối đa %.2f u' % max(devs))
    return segs


def fair(segs):
    import fix_S_fair as F
    from compat import to_d
    F.MAXDEV = MAXDEV; cs = [[list(x) for x in segs]]
    anc = [sg[1] for sg in segs]
    for ch in CHAINS:
        spec = [(anc[i], k) for i, k in ch]
        r, dv = F.fair_chain(cs[0], spec); print(f'  chuỗi quanh neo {ch[1][0]}: lệch {dv:.2f} u')
    return to_d(cs)


def convert(d):
    toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', d); out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t in 'MLCZ': out.append(t); i += 1; continue
        x, y = float(toks[i]), float(toks[i + 1]); i += 2
        out.append('%g %g' % (round(K*x, 2) + 0.0, round(Y0 - K*y, 2) + 0.0))
    return re.sub(r' ?([MLCZ]) ?', r'\1', ' '.join(out))


if __name__ == '__main__':
    p = os.path.join(HERE, 'designer_A.json'); D = json.load(open(p))
    D['S-Regular'] = [fair(rebuild(convert(FIGMA_R2)))]
    json.dump(D, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('S-Regular ← Figma 2179:2', D['S-Regular'][0][:80], '…')
