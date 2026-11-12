#!/usr/bin/env python3
"""S40b S Bold suy từ S Regular mới (designer 12/11: "dựa trên S regular tính lại cho các weight khác").
    python3 tools/construct/ref/fix_S_bold_from_reg.py   (từ bản lưu designer_{A,B}_preS40.json + designer_A.json S Regular mới)

Bold mới = Regular mới + (Bold cũ − Regular cũ), cộng THEO TỪNG ĐIỂM ĐIỀU KHIỂN (hai bản cũ cùng cấu trúc 14 đoạn: neo ở cùng
cực trị / điểm uốn / góc đầu nét) — giữ nguyên phần chênh weight designer đã duyệt (độ đậm, tương phản, mặt cắt đầu nét, S19), dáng
bụng theo bản Regular mới. Rồi làm mượt độ cong như S39 (fix_S_fair.fair_chain, lệch ≤ MAXDEV u). Medium / SemiBold = nội suy.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, '..'), os.path.join(HERE, '..', 'font')]
MAXDEV = 2.0
CHAINS = [[(1, 'x'), (2, 'v'), (3, 'x')], [(8, 'x'), (9, 'v'), (10, 'x')],
          [(5, 'x'), (6, 't'), (7, 't'), (8, 'x')], [(12, 'x'), (13, 't'), (0, 't'), (1, 'x')]]

if __name__ == '__main__':
    from interp import contours
    from compat import to_d
    import fix_S_fair as F
    R0 = contours(json.load(open(os.path.join(HERE, 'designer_A_preS40.json')))['S-Regular'])[0]
    B0 = contours(json.load(open(os.path.join(HERE, 'designer_B_preS40.json')))['S-Bold'])[0]
    R1 = contours(json.load(open(os.path.join(HERE, 'designer_A.json')))['S-Regular'])[0]
    assert [s[0] for s in R0] == [s[0] for s in B0] == [s[0] for s in R1], 'cấu trúc khác'
    B1 = []
    for r0, b0, r1 in zip(R0, B0, R1):
        B1.append([r1[0]] + [(round(q1[0] + qb[0] - q0[0], 2), round(q1[1] + qb[1] - q0[1], 2)) for q0, qb, q1 in zip(r0[1:], b0[1:], r1[1:])])
    for i in range(len(B1)): B1[i][1] = B1[i - 1][-1]
    # nút liền ở Regular mới: hai tay Bold về CHUNG hướng (phân giác), giữ độ dài — cộng chênh từng tay làm lệch 1.3–1.9° ở chỗ
    # tiếp tuyến Regular mới xoay khác bản cũ (SemiBold nội suy gãy 3.5° sau làm tròn)
    n = len(B1)
    for i in range(n):
        j = (i + 1) % n; a, b, ra, rb = B1[i], B1[j], R1[i], R1[j]
        if a[0] != 'C' or b[0] != 'C': continue
        u = (ra[4][0] - ra[3][0], ra[4][1] - ra[3][1]); v = (rb[2][0] - rb[1][0], rb[2][1] - rb[1][1])
        if math.hypot(*u) < 1 or math.hypot(*v) < 1: continue
        if math.degrees(abs(math.atan2(u[0]*v[1] - u[1]*v[0], u[0]*v[0] + u[1]*v[1]))) > 0.5: continue
        P = a[4]; hi, ho = a[3], b[2]
        di = (P[0] - hi[0], P[1] - hi[1]); do = (ho[0] - P[0], ho[1] - P[1]); li, lo = math.hypot(*di), math.hypot(*do)
        if li < 1 or lo < 1: continue
        m = (di[0]/li + do[0]/lo, di[1]/li + do[1]/lo); L = math.hypot(*m); m = (m[0]/L, m[1]/L)
        a[3] = (round(P[0] - m[0]*li, 2), round(P[1] - m[1]*li, 2)); b[2] = (round(P[0] + m[0]*lo, 2), round(P[1] + m[1]*lo, 2))
    F.MAXDEV = MAXDEV; anc = [sg[1] for sg in B1]
    for ch in CHAINS:
        r, dv = F.fair_chain(B1, [(anc[i], k) for i, k in ch]); print(f'  chuỗi quanh neo {ch[1][0]}: lệch {dv:.2f} u')
    p = os.path.join(HERE, 'designer_B.json'); D = json.load(open(p)); D['S-Bold'] = [to_d([B1])]
    json.dump(D, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('S-Bold ←', D['S-Bold'][0][:80], '…')
