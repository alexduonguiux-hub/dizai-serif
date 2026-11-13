#!/usr/bin/env python3
"""S42b 1 Bold thiếu loe phải ở chân (designer 13/11: "Kiểm tra lại chân loe các chữ thẳng xem 2 mặt loe đã đồng bộ chưa").
    python3 tools/construct/ref/fix_1_bold_flare.py     (từ bản lưu designer_B_pre1flare.json)

Quét 207 thân có loe hai bên chân × 4 weight: mọi cặp khớp ≤ 0.6 u (k 0.8 u) — riêng 1 Bold: mép phải thân đi thẳng xuống
đường chân (Regular loe cả hai bên) → Medium / SemiBold nội suy ra vệt loe phải cao 165 / 260 u. Thêm loe phải = ảnh gương loe
trái qua trục thân (vươn 22.7, cao 69.8, cùng tay nắm)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, '..'), os.path.join(HERE, '..', 'font')]
if __name__ == '__main__':
    from interp import contours
    from compat import to_d
    src = json.load(open(os.path.join(HERE, 'designer_B_pre1flare.json')))
    S = [list(x) for x in contours(src['1-Bold'])[0]]
    xl = 76.5; xr = 215.4
    i = next(i for i, sg in enumerate(S) if sg[0] == 'C' and abs(sg[1][0] - xl) < 0.1 and abs(sg[1][1] - 69.8) < 0.1)   # loe trái
    left = S[i], S[i + 1]                       # C (thân → 13.5) + L (→ chân)
    m = lambda p: (round(xr + (xl - p[0]), 2), p[1])                                       # gương qua trục thân
    c, l = left
    foot, mid = m(l[2]), m(l[1])
    flare = [['L', foot, mid], ['C', mid, m(c[3]), m(c[2]), (xr, c[1][1])]]                 # chân → 13.5 → thân (đi lên)
    j = next(j for j, sg in enumerate(S) if sg[0] == 'L' and abs(sg[1][0] - xr) < 0.1 and abs(sg[1][1]) < 0.1)   # mép phải đi lên
    S[j] = ['L', (xr, c[1][1]), S[j][2]]
    S = S[:j] + flare + S[j:]
    b = next(q for q, sg in enumerate(S) if sg[0] == 'L' and abs(sg[2][0] - xr) < 0.1 and abs(sg[2][1]) < 0.1 and abs(sg[1][1]) < 0.1)
    S[b] = ['L', S[b][1], foot]                                                             # cạnh đáy kéo tới chân loe mới
    for q in range(len(S)): S[q][1] = S[q - 1][-1]
    D = json.load(open(os.path.join(HERE, 'designer_B.json'))); D['1-Bold'] = [to_d([S])]
    json.dump(D, open(os.path.join(HERE, 'designer_B.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    for sg in S: print(sg[0], [tuple(round(v, 1) for v in q) for q in sg[1:]])
