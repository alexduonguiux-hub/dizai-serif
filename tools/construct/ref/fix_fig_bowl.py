#!/usr/bin/env python3
"""S22 Thành bụng dưới 3, 5 Bold (designer 07/11 "sửa luôn các chỗ còn lại" — qa_stroke: 3, 5 Medium nhẹ ~10 %).
    python3 tools/construct/ref/fix_fig_bowl.py      (đi từ bản lưu designer_B_prefig.json → chạy lại cho cùng kết quả)

Đo ngang tại cực phải bụng dưới: thành bụng 3 / 5 = 95 u (Regular) → 93 (Bold) — KHÔNG dày lên; 6: 92 → 130 (× 1.41).
Bản vẽ Bold nở mép ngoài 39 u nhưng lòng bụng cũng nở theo. Sửa: giữ mép ngoài (bề ngang số), dời mép LÒNG ở thành phải
vào trong — mỗi điểm neo (và tay nắm của nó) dời (d·min(0, nx), 0), nx = thành phần ngang của pháp tuyến hướng vào lòng:
thành phải dời nhiều nhất, đỉnh / đáy lòng (pháp tuyến đứng) và thành trái (phía đuôi) đứng yên. d giải để thành bụng = WALL.
"""
import json, math, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
WALL = 130.0                                                      # = thành bụng 6 Bold
START = {'3-Bold': (89.6, 398.1), '5-Bold': (86.5, 414.7)}        # điểm đầu chuỗi mép lòng (chỗ nối vai)
NCHAIN = 3                                                        # 3 đoạn cong quanh lòng; đoạn thứ 4 (tới đầu đuôi) giữ


def parse(d):
    toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', d); i = 0; out = []
    while i < len(toks):
        c = toks[i]; i += 1; n = {'M': 1, 'L': 1, 'C': 3, 'Z': 0}[c]
        out.append([c, [(float(toks[i + 2*j]), float(toks[i + 2*j + 1])) for j in range(n)]]); i += 2*n
    return out


def unparse(cmds):
    s = ''.join(c + ' '.join('%.1f %.1f' % p for p in pts) for c, pts in cmds)
    return re.sub(r'\.0(?=[ MLCZ]|$)', '', s)


def apply(d, start, dd):
    cmds = parse(d); cur = None; k0 = None
    for k, (c, pts) in enumerate(cmds):
        if pts and k0 is None and cur is not None and math.dist(cur, start) < 0.2 and c == 'C': k0 = k
        if pts: cur = pts[-1]
    assert k0 is not None, start
    chain = cmds[k0:k0 + NCHAIN]
    # pháp tuyến hướng vào lòng tại mỗi neo cuối đoạn (lòng ở bên PHẢI hướng đi của mép lòng — mép lòng chạy ngược kim đồng hồ
    # của nét ⇒ kiểm bằng hướng tới tâm lòng)
    ends = [pts[2] for _, pts in chain]
    cx = sum(p[0] for p in ends)/len(ends); cy = sum(p[1] for p in ends)/len(ends)
    for j, (c, pts) in enumerate(chain):
        if j == NCHAIN - 1: break                                 # neo cuối chuỗi (chỗ chuyển sang đuôi): giữ
        p = pts[2]; h = pts[1]; t = (p[0] - h[0], p[1] - h[1]); L = math.hypot(*t); t = (t[0]/L, t[1]/L)
        n = (-t[1], t[0])
        if (cx - p[0])*n[0] + (cy - p[1])*n[1] < 0: n = (-n[0], -n[1])
        dx = dd*min(0.0, n[0])
        pts[2] = (p[0] + dx, p[1]); pts[1] = (pts[1][0] + dx, pts[1][1])
        nxt = cmds[k0 + j + 1][1]; nxt[0] = (nxt[0][0] + dx, nxt[0][1])       # tay nắm đầu đoạn sau dời theo neo
    return unparse(cmds)


def wall(d):
    import vn_punct as V
    from make_ref import outline
    p = outline([d]); b = p.bounds; y = 233.8
    I = V.I(p, V.rect(b[0] - 5, y - 0.05, b[2] + 5, y + 0.05)); runs = sorted((c.bounds[0], c.bounds[2]) for c in I.contours)
    return runs[-1][1] - runs[-1][0]


if __name__ == '__main__':
    p = os.path.join(HERE, 'designer_B.json'); keep = os.path.join(HERE, 'designer_B_prefig.json')
    if not os.path.exists(keep): shutil.copy(p, keep)
    src = json.load(open(keep)); B = json.load(open(p))
    for k, st in START.items():
        d0 = src[k][0]; lo, hi = 0.0, 120.0
        for _ in range(40):                                      # chia đôi: thành bụng = WALL
            mid = (lo + hi)/2
            if wall(apply(d0, st, mid)) < WALL: lo = mid
            else: hi = mid
        B[k] = [apply(d0, st, hi)]
        print(k, 'thành bụng %.0f → %.0f (d = %.1f)' % (wall(d0), wall(B[k][0]), hi))
    json.dump(B, open(p, 'w'), separators=(',', ':'))
