#!/usr/bin/env python3
"""Thu hẹp V X Y hoa (giữ loe bản vẽ gốc) (designer 05/11: "giảm bề ngang chữ X hoa 1 chút" → "các chữ XVY hoa giảm bề ngang lại").
    python3 tools/construct/ref/narrow_caps.py   → sửa V- X- Y- trong designer_A.json (Regular) / designer_B.json (Bold);
    bản gốc của designer giữ trong designer_AB_orig.json (chạy lại nhiều lần luôn đi từ bản gốc, cùng kết quả).
Sau đó chạy interp.py (Medium / SemiBold nội suy lại).

Phép thu GIỮ ĐỘ DÀY NÉT:
  1. co ngang quanh tâm hộp × NARROW (Y: chỉ phần tay trên đỉnh thân; góc tay gặp thân = giao mép tay mới với mép thân đứng);
  2. nét chéo dốc hơn nên mỏng đi → dời song song hai mép mỗi nét chéo (derive.thicken) cho bề dày vuông góc = bản gốc.
"""
import json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'lower'))
sys.path.insert(0, os.path.join(HERE, '..'))
import pathops
from make_ref import outline
import vn_punct as V
import derive as Dv

NARROW = {}   # TẮT (designer 05/11: "bản của bạn lỗi quá" — dời mép nét làm méo loe); V X Y = bản vẽ gốc, V Bold = Figma 2138:1203
ORIG = os.path.join(HERE, 'designer_AB_orig.json')

def segs_of(p):
    out = []
    for c in Dv._contours(p):
        a = c['start']
        for t, ps in c['segs']:
            out.append((t, a, ps)); a = ps[-1]
    return out

def diag_strokes(p):
    """các nét chéo: mỗi nhóm hướng (\\ hoặc /) → cặp mép (đường thẳng dài > 100) theo thứ tự x ở giữa cao"""
    L = [(a, ps[-1]) for t, a, ps in segs_of(p) if t == 'L' and math.dist(a, ps[-1]) > 100 and abs(ps[-1][0] - a[0]) > 5 and abs(ps[-1][1] - a[1]) > 5]
    xat = lambda l, y: l[0][0] + (y - l[0][1])*(l[1][0] - l[0][0])/(l[1][1] - l[0][1])
    res = {}
    for fs in (False, True):
        ls = [l for l in L if ((l[1][0] - l[0][0])*(l[1][1] - l[0][1]) > 0) == fs]
        ys = 500.0
        E = []
        for l in sorted(ls, key=lambda l: xat(l, ys)):
            if E and abs(xat(l, ys) - xat(E[-1][0], ys)) < 3: E[-1].append(l)
            else: E.append([l])
        res[fs] = (E, xat)
    return res

def perp(E0, E1, xat):
    l = E0[0]; dx, dy = l[1][0] - l[0][0], l[1][1] - l[0][1]; th = math.atan2(abs(dy), abs(dx))
    return abs(xat(E1[0], 500) - xat(E0[0], 500))*math.sin(th)

def narrow(ch, d, s):
    p = outline([d]); x0, _, x1, _ = p.bounds; cx = (x0 + x1)/2
    st0 = diag_strokes(p)
    T0 = {fs: [perp(E[i], E[i + 1], xat) for i in range(0, len(E) - 1, 2)] for fs, (E, xat) in st0.items()}
    if ch == 'Y':
        # thân đứng: các đường thẳng đứng dài; đỉnh thân = góc tay gặp thân (giữ nguyên thân + chân loe)
        vs = [(a, ps[-1]) for t, a, ps in segs_of(p) if t == 'L' and abs(ps[-1][0] - a[0]) < 0.5 and abs(ps[-1][1] - a[1]) > 100]
        sx = sorted({round(l[0][0], 2) for l in vs}); cx = (sx[0] + sx[-1])/2
        yj = {round(l[0][0], 2): max(l[0][1], l[1][1]) for l in vs}
        def f(x, y):
            for xs_, yt in yj.items():
                if abs(x - xs_) < 0.5 and abs(y - yt) < 0.5: return (x, y)          # góc tay–thân: tính lại dưới
            return (cx + (x - cx)*s, y) if y > min(yj.values()) + 0.5 else (x, y)
        q = V.xform(p, f)
        # góc tay–thân = giao mép tay (đã co) với mép thân đứng
        cmds = []
        for c in Dv._contours(q):
            pts = [c['start']] + [ps[-1] for t, ps in c['segs']]
            n = len(c['segs']); A = list(pts)
            for i in range(n):
                pt = pts[i]
                for xs_, yt in yj.items():
                    if abs(pt[0] - xs_) < 0.5 and abs(pt[1] - yt) < 0.5:
                        # đoạn kề đi lên (tay): điểm kia của đoạn có y lớn hơn
                        nb = [pts[(i - 1) % n], pts[(i + 1) % n]]; up = max(nb, key=lambda r: r[1])
                        upo = [r for r in nb if r[1] == up[1]][0]
                        # hướng tay gốc: từ điểm gốc của up (trước khi co) tới góc gốc → sau co: (dx*s, dy)
                        ux0 = cx + (up[0] - cx)/s; dx, dy = (pt[0] - ux0)*s, pt[1] - up[1]
                        t_ = (xs_ - up[0])/dx if abs(dx) > 1e-9 else 0; A[i] = (xs_, up[1] + t_*dy)
            A[n] = A[0]; cmds.append(('M', A[0]))
            for i, (t, ps) in enumerate(c['segs']):
                if t == 'L': cmds.append(('L', A[i + 1]))
                else:
                    d1, d2 = A[i][0] - pts[i][0], A[i + 1][0] - pts[i + 1][0]; e1, e2 = A[i][1] - pts[i][1], A[i + 1][1] - pts[i + 1][1]
                    cmds.append(('C', (ps[0][0] + d1, ps[0][1] + e1), (ps[1][0] + d2, ps[1][1] + e2), A[i + 1]))
            cmds.append(('Z',))
        q = V.P(cmds)
    else:
        q = V.xform(p, lambda x, y: (cx + (x - cx)*s, y))
    # bù độ dày từng hướng nét chéo (tuyến tính theo delta → hai lần đo)
    for fs in (False, True):
        st = diag_strokes(q)[fs]
        if len(st[0]) not in (2, 4): continue
        t0 = sum(perp(st[0][i], st[0][i + 1], st[1]) for i in range(0, len(st[0]) - 1, 2))
        q1 = Dv.thicken(q, 20.0, ylo=40.0, yhi=660.0, fs=fs); st1 = diag_strokes(q1)[fs]
        t1 = sum(perp(st1[0][i], st1[0][i + 1], st1[1]) for i in range(0, len(st1[0]) - 1, 2))
        tgt = sum(T0[fs])
        if abs(t1 - t0) < 1e-6: continue
        q = Dv.thicken(q, 20.0*(tgt - t0)/(t1 - t0), ylo=40.0, yhi=660.0, fs=fs)
    q = pathops.op(q, q, pathops.PathOp.UNION)
    q = V.move(q, -q.bounds[0], 0)
    out = []
    for v, ps in q.segments:
        out.append({'moveTo': 'M', 'lineTo': 'L', 'curveTo': 'C', 'closePath': 'Z'}[v] + ' '.join('%.1f %.1f' % pt for pt in ps))
    return ''.join(out), q

def main():
    orig = json.load(open(ORIG)) if os.path.exists(ORIG) else {}
    for f in ('designer_A.json', 'designer_B.json'):
        P = os.path.join(HERE, f); d = json.load(open(P)); W = d.get('_W', {})
        for k in list(d):
            ch = k.split('-')[0]
            if ch not in NARROW: continue
            if k not in orig: orig[k] = d[k]; orig['_W_' + k] = W.get(k)
            s, q = narrow(ch, orig[k][0], NARROW[ch])
            d[k] = [s]
            if orig.get('_W_' + k) is not None:
                W[k] = round(orig['_W_' + k]*NARROW[ch]); d['_W'] = W
            print(k, 'bề ngang', round(outline(orig[k]).bounds[2]), '→', round(q.bounds[2]))
        # A K (và loe V X Y): GIỮ ĐÚNG BẢN VẼ GỐC (designer 05/11: "hư hết rồi — coi lại bản gốc", Figma 2138:1200 — loe đầu nét
        # chéo của bản vẽ đã đúng module 2138:1189). Bản dựng lại loe theo module đã bỏ; trả A K về bản gốc nếu từng bị sửa.
        for k in [k for k in d if k.split('-')[0] in ('A', 'K')]:
            if k in orig: d[k] = orig[k]
        json.dump(d, open(P, 'w'), separators=(',', ':'))
    json.dump(orig, open(ORIG, 'w'), separators=(',', ':'))

if __name__ == '__main__':
    main()
