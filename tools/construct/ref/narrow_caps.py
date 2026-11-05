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

# THU HẸP BẰNG NGHIÊNG KHỐI (designer 05/11 lần 3: "giảm bề ngang X, Y, V hoa"): mỗi nhánh chéo là một khối, nghiêng (shear ngang)
# quanh điểm gốc của nó — V: đáy nhọn · X: tâm giao (4 nhánh) · Y: đỉnh thân (thân + chân giữ nguyên). Shear giữ đường cap / chân,
# giữ HÌNH LOE (chỉ nghiêng 2–4°) và bề dày cắt ngang của nét; chỗ hai nhánh gặp nhau tự hạ xuống. Bề ngang mực −FRAC.
FRAC = {'V': 0.08, 'X': 0.08, 'Y': 0.08}
def despike(q, ang=4.0):
    """bỏ gai mảnh do phép hợp các dải nghiêng: đỉnh B của hai đoạn thẳng A→B→C mà BA, BC gần trùng hướng (< ang°) → bỏ B"""
    from fontTools.pens.recordingPen import RecordingPen
    rp = RecordingPen(); q.draw(rp); C = []; cur = None
    for v, ps in rp.value:
        if v == 'moveTo': cur = [('M', ps[0])]
        elif v == 'lineTo': cur.append(('L', ps[0]))
        elif v == 'curveTo': cur.append(('C', ps))
        elif v in ('closePath', 'endPath'): C.append(cur); cur = None
    def pt(e): return e[1] if e[0] != 'C' else e[1][-1]
    out = pathops.Path(); pen = out.getPen()
    for c in C:
        ch_ = True
        while ch_ and len(c) > 3:
            ch_ = False
            n = len(c)
            for i in range(n):
                a, b, cc = c[i - 1], c[i], c[(i + 1) % n]
                if b[0] == 'C' or cc[0] == 'C': continue
                A, B, Cp = pt(a), pt(b), pt(cc)
                u = (A[0] - B[0], A[1] - B[1]); w = (Cp[0] - B[0], Cp[1] - B[1])
                lu, lw = math.hypot(*u), math.hypot(*w)
                if lu < 1e-6 or lw < 1e-6 or math.degrees(math.acos(max(-1, min(1, (u[0]*w[0] + u[1]*w[1])/(lu*lw))))) < ang:
                    if b[0] == 'M': c[(i + 1) % n] = ('M', Cp); del c[i]
                    else: del c[i]
                    ch_ = True; break
        k = next(i for i, e in enumerate(c) if e[0] == 'M'); c = c[k:] + c[:k]
        pen.moveTo(c[0][1])
        for e in c[1:]:
            if e[0] == 'L': pen.lineTo(e[1])
            else: pen.curveTo(*e[1])
        pen.closePath()
    return out

def shear_narrow(ch, d, frac):
    """chia theo TỪNG NÉT: nét \\ và nét / là dải giữa hai mép thẳng của nó (kéo dài) + vùng đầu nét (loe); mỗi dải nghiêng một
    chiều duy nhất quanh điểm gốc (V: đáy · X: tâm giao · Y: đỉnh thân, thân + chân giữ nguyên) → không cạnh nào bị bẻ;
    chỗ hai nét chồng nhau gộp lại (khe giữa hai nét tự hạ xuống)"""
    p = outline([d]); x0, y0, x1, y1 = p.bounds; dw = frac*(x1 - x0)/2; R = V.rect; BIG = 3000
    segs = [(a, ps[-1]) for t, a, ps in segs_of(p) if t == 'L' and math.dist(a, ps[-1]) > 60 and abs(ps[-1][0] - a[0]) > 5 and abs(ps[-1][1] - a[1]) > 5]
    xat = lambda l, y: l[0][0] + (y - l[0][1])*(l[1][0] - l[0][0])/(l[1][1] - l[0][1])
    if ch == 'X': yp = (y0 + y1)/2; s = dw/((y1 - y0)/2)
    elif ch == 'V': yp = y0; s = dw/(y1 - y0)
    else:
        vs = [(a, ps[-1]) for t, a, ps in segs_of(p) if t == 'L' and abs(ps[-1][0] - a[0]) < 0.5 and abs(ps[-1][1] - a[1]) > 100]
        tops = sorted(max(a[1], b[1]) for a, b in vs); yp = tops[0]; yp2 = tops[-1]; s = dw/(y1 - yp)
        xc_stem = sum(a[0] for a, b in vs)/len(vs); sxl, sxr = min(a[0] for a, b in vs), max(a[0] for a, b in vs)
    ym = yp + 0.5*(y1 - yp) if ch != 'X' else yp
    M = 6.0                                                  # nới dải: mép dưới / trên của bản vẽ không thẳng hàng tuyệt đối
    def edges(fs):
        ls = [l for l in segs if ((l[1][0] - l[0][0])*(l[1][1] - l[0][1]) > 0) == fs]
        G = []
        for l in sorted(ls, key=lambda l: xat(l, ym)):
            if G and abs(xat(l, ym) - xat(G[-1], ym)) < 3: continue
            G.append(l)
        return G[0], G[-1]
    def band(a, b):
        ya, yb = y0 - 60, y1 + 60
        core = V.poly([(xat(a, ya), ya), (xat(b, ya), ya), (xat(b, yb), yb), (xat(a, yb), yb)])
        wide = V.poly([(xat(a, ya) - M, ya), (xat(b, ya) + M, ya), (xat(b, yb) + M, yb), (xat(a, yb) - M, yb)])
        if ch == 'X':                                        # X: chỉ nới xa tâm giao (gần tâm, phần nới cắt vào nét / → khấc)
            return V.U(core, V.I(wide, V.U(R(-BIG, yp + 120, BIG, BIG), R(-BIG, -BIG, BIG, yp - 120))))
        return wide
    xmid = (x0 + x1)/2
    ba, bb = edges(False); fa, fb = edges(True)
    bs = band(ba, bb)                                        # nét \\ (V: tay trái · Y: tay trái · X: nét dày)
    if ch == 'X': ends = V.U(R(-BIG, yp + 200, xmid, BIG), R(xmid, -BIG, BIG, yp - 200))
    else: ends = R(-BIG, yp + 0.55*(y1 - yp), xmid, BIG)
    reg_bs = V.U(bs, ends)
    if ch in 'VY':
        # dưới chỗ hai tay gặp nhau (đáy lòng C = giao mép trong hai tay), chia theo đường C → điểm gốc: phần bên phải thuộc tay phải
        def isect(l1, l2):
            (p1, p2), (p3, p4) = l1, l2
            d1 = (p2[0] - p1[0], p2[1] - p1[1]); d2 = (p4[0] - p3[0], p4[1] - p3[1]); den = d1[0]*d2[1] - d1[1]*d2[0]
            t = ((p3[0] - p1[0])*d2[1] - (p3[1] - p1[1])*d2[0])/den; return (p1[0] + t*d1[0], p1[1] + t*d1[1])
        C = isect(bb, fa)
        if ch == 'V':
            bot = V.I(p, R(-BIG, y0 - 1, BIG, y0 + 3)); P0 = ((bot.bounds[0] + bot.bounds[2])/2, y0 - 60)
        else: P0 = (xc_stem, yp - 1)
        dx = (C[0] - P0[0])/max(C[1] - P0[1], 1e-6)
        left_of = V.poly([(-BIG, -BIG), (P0[0] + dx*(-BIG - P0[1]), -BIG), (C[0], C[1]), (C[0], BIG), (-BIG, BIG)])
        reg_bs = V.I(reg_bs, left_of)
    yq = yp
    if ch == 'Y':                                            # giữ nguyên cả cột thân; tay trái nghiêng quanh đỉnh thân trái (yp),
        low = V.U(V.I(p, R(-BIG, -BIG, BIG, yp)), V.I(p, R(sxl, -BIG, sxr, yp2)))   # tay phải quanh đỉnh thân phải (yp2)
        up = V.D(p, low); yq = yp2
    else: low = None; up = p
    part_bs = V.I(up, reg_bs); part_fs = V.D(up, reg_bs)
    q = V.U(V.xform(part_bs, lambda x, y: (x + s*(y - yp), y)), V.xform(part_fs, lambda x, y: (x - s*(y - yq), y)))
    if low is not None: q = V.U(q, low)
    q = pathops.op(q, q, pathops.PathOp.UNION); q = V.move(q, -q.bounds[0], 0)
    q = despike(q)
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
            if ch not in FRAC: continue
            if k not in orig: orig[k] = d[k]; orig['_W_' + k] = W.get(k)
            s_, q = shear_narrow(ch, orig[k][0], FRAC[ch])
            d[k] = [s_]
            ow = outline(orig[k]).bounds[2]
            if orig.get('_W_' + k) is not None: W[k] = round(orig['_W_' + k] - (ow - q.bounds[2])); d['_W'] = W
            print(k, 'bề ngang', round(ow), '→', round(q.bounds[2]), '· contour', len(list(q.contours)))
        json.dump(d, open(P, 'w'), separators=(',', ':'))
    json.dump(orig, open(ORIG, 'w'), separators=(',', ':'))

if __name__ == '__main__':
    main()
