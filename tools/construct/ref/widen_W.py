#!/usr/bin/env python3
"""S41 W hoa rộng ra (designer 12/11: "Điều chỉnh lại bề rộng chữ W hoa để spacing giữa các glyph của nó rộng ra xíu không bị nặng").
    python3 tools/construct/ref/widen_W.py      (từ bản lưu designer_{A,B}_preW.json → chạy lại cho cùng kết quả)

W = 4 nét chéo thẳng (dày \\, mảnh /, dày \\, mảnh /) + mặt cắt phẳng đỉnh / đáy + 4 cụm loe đầu nét trên. Nới lòng mà KHÔNG
làm nét đậm lên:
  1. mỗi mép nét (cạnh thẳng dài) giãn ngang quanh tâm chữ × f (f = (rộng + DW) / rộng) → tâm nét, đỉnh, đáy giãn ra;
  2. dời mép vào phía mực e = (f·w − w·cosθ / cosθ') / 2 (w: bề ngang nét đo ngang tới mép song song đối diện) → bề dày đo
     VUÔNG GÓC giữ nguyên;
  3. neo giữa hai mép / mép với đường đỉnh 700 – đáy −11.3: giao điểm lại (mặt cắt đáy V giữ dáng);
  4. cụm loe (đoạn cong + cạnh ngắn giữa mép nét và đường đỉnh): DỜI + XOAY CỨNG theo mép mang nó (giữ hình loe đã duyệt),
     đầu chạm đường đỉnh đặt lại đúng y = 700.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, '..'), os.path.join(HERE, '..', 'font')]
DW = {'W-Regular': 40.0, 'W-Bold': 40.0}   # bề ngang THỰC tăng (cụm loe ngoài giữ hình → giải hệ số giãn cho đúng)
TOP, BOT = 700.0, -11.3

def widen(segs, dw):
    n = len(segs)
    xs = [p[0] for s in segs for p in s[1:]]; x0, x1 = min(xs), max(xs); c = (x0 + x1)/2; f = (x1 - x0 + dw)/(x1 - x0)
    area = sum(s[1][0]*s[-1][1] - s[-1][0]*s[1][1] for s in segs)/2; ccw = area > 0
    def is_edge(s): return s[0] == 'L' and math.dist(s[1], s[2]) > 40 and abs(s[1][1] - s[2][1]) > 20
    def is_flat(s): return s[0] == 'L' and abs(s[1][1] - s[2][1]) < 1e-6 and abs(s[1][1] - TOP) < 0.5 or (s[0] == 'L' and abs(s[1][1] - BOT) < 0.5 and abs(s[2][1] - BOT) < 0.5)
    # đường mép: x = a·y + b; phía mực: mực bên trái hướng đi nếu contour ngược chiều kim đồng hồ
    E = {}
    for i, s in enumerate(segs):
        if not is_edge(s): continue
        (xa, ya), (xb, yb) = s[1], s[2]; a = (xb - xa)/(yb - ya); b = xa - a*ya
        d = (xb - xa, yb - ya); left = (-d[1], d[0]); ink = left if ccw else (d[1], -d[0])
        E[i] = dict(a=a, b=b, side=1 if ink[0] > 0 else -1)
    for i, e in E.items():                                   # bề ngang nét: mép song song gần nhất phía mực
        best = None
        for j, g in E.items():
            if j == i or abs(g['a'] - e['a']) > 0.01 or g['side'] == e['side']: continue
            dx = (g['b'] - e['b'])*e['side']
            if dx > 5 and (best is None or dx < best): best = dx
        e['w'] = best
    ws = [e['w'] for e in E.values() if e['w']]
    for e in E.values():
        w = e['w'] or sum(ws)/len(ws)
        th, th2 = math.atan(abs(e['a'])), math.atan(abs(e['a'])*f)
        ero = (f*w - w*math.cos(th)/math.cos(th2))/2
        e['a2'] = e['a']*f; e['b2'] = c + f*(e['b'] - c) + ero*e['side']
    X = lambda e, y: e['a2']*y + e['b2']
    Xo = lambda e, y: e['a']*y + e['b']
    def carrier(i):
        s = segs[i]
        if i in E: return ('E', E[i])
        if is_flat(s): return ('H', s[1][1])
        return None
    def isect(c1, c2):
        if c1[0] == 'H' and c2[0] == 'H': return None
        if c1[0] == 'H': return (X(c2[1], c1[1]), c1[1])
        if c2[0] == 'H': return (X(c1[1], c2[1]), c2[1])
        e, g = c1[1], c2[1]
        if abs(e['a2'] - g['a2']) < 1e-9: return None
        y = (g['b2'] - e['b2'])/(e['a2'] - g['a2']); return (X(e, y), y)
    new = [list(s) for s in segs]
    # neo giữa hai đoạn có giá (mép / đường ngang)
    for i in range(n):
        j = (i + 1) % n; ci, cj = carrier(i), carrier(j)
        if ci and cj:
            P = isect(ci, cj)
            if P: new[i][-1] = P; new[j][1] = P
    # cụm loe: chuỗi đoạn không giá giữa một mép và đường ngang → dời + xoay cứng theo mép
    i = 0; seen = set()
    for i in range(n):
        if carrier(i) or i in seen: continue
        k = i
        while not carrier((k - 1) % n): k = (k - 1) % n
        grp = []; m = k
        while not carrier(m): grp.append(m); seen.add(m); m = (m + 1) % n
        before, after = carrier((k - 1) % n), carrier(m)
        if before and before[0] == 'E': e, P = before[1], segs[k][1]
        elif after and after[0] == 'E': e, P = after[1], segs[grp[-1]][-1]
        else: continue
        y0 = P[1]; Pn = (X(e, y0), y0)
        dth = math.atan(e['a2']) - math.atan(e['a'])          # mép quay quanh trục đứng: góc so với phương đứng
        cs, sn = math.cos(-dth), math.sin(-dth)
        def T(q):
            dx, dy = q[0] - P[0], q[1] - P[1]
            return (Pn[0] + dx*cs - dy*sn, Pn[1] + dx*sn + dy*cs)
        for g in grp: new[g] = [segs[g][0]] + [T(q) for q in segs[g][1:]]
        # nối: đầu cụm gắn mép = Pn; đầu kia trên đường ngang → đặt lại y
        other = before if after and after[0] == 'E' and not (before and before[0] == 'E') else after
        if before and before[0] == 'E': new[(k - 1) % n][-1] = new[k][1]
        else: new[(k - 1) % n][-1] = new[k][1]
        new[m][1] = new[grp[-1]][-1]
        for (end, hidx, nb) in ((new[grp[-1]], -1, m), (new[k], 1, (k - 1) % n)):
            pass
        # đầu cụm trên đường ngang lệch khỏi y = 700 sau khi xoay → co giãn DỌC cả cụm quanh điểm gắn (affine: nút trong cụm vẫn liền)
        for gi, idx in ((k, 1), (grp[-1], -1)):
            q, q0 = new[gi][idx], segs[gi][idx]
            for H in (TOP, BOT):
                if abs(q0[1] - H) < 1e-6 and abs(q[1] - Pn[1]) > 1e-6 and abs(q[1] - H) > 1e-6:
                    sy = (H - Pn[1])/(q[1] - Pn[1])
                    for g in grp: new[g] = [new[g][0]] + [(r[0], Pn[1] + (r[1] - Pn[1])*sy) for r in new[g][1:]]
        new[(k - 1) % n][-1] = new[k][1]; new[m][1] = new[grp[-1]][-1]
    # đường ngang nối với cụm loe: đầu kia đã dời → cạnh ngang tự theo
    for i in range(n): new[i][1] = new[i - 1][-1]
    return new, f, {i: (round(e['w'] or -1, 1), round(math.degrees(math.atan(e['a'])), 2), round(math.degrees(math.atan(e['a2'])), 2)) for i, e in E.items()}

if __name__ == '__main__':
    from interp import contours
    from compat import to_d
    for f_, k in (('designer_A.json', 'W-Regular'), ('designer_B.json', 'W-Bold')):
        p = os.path.join(HERE, f_); keep = os.path.join(HERE, f_.replace('.json', '_preW.json'))
        src = json.load(open(keep)); D = json.load(open(p))
        cs = [[list(x) for x in S] for S in contours(src[k])]
        out = []
        for S in cs:
            w0 = max(p[0] for s_ in S for p in s_[1:]) - min(p[0] for s_ in S for p in s_[1:]); g = DW[k]
            for _ in range(6):                                   # giải dw nội bộ để bề ngang thực tăng đúng DW
                N, f, info = widen(S, g); w1 = max(p[0] for s_ in N for p in s_[1:]) - min(p[0] for s_ in N for p in s_[1:])
                if abs(w1 - w0 - DW[k]) < 0.05: break
                g *= DW[k]/(w1 - w0)
            out.append(N)
        D[k] = [to_d(out)]; json.dump(D, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
        print(k, 'f = %.4f' % f, 'rộng %.1f → %.1f' % (w0, w1))
