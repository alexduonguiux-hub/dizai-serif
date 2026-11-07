#!/usr/bin/env python3
"""S26 bù quang học Italic (designer 07/11 duyệt đề xuất): Italic = Roman nghiêng 10° (trượt ngang x' = x + y·tan α) giữ lượng
mực nhưng đổi độ dày VUÔNG GÓC của nét theo hướng: nét hướng u dày × 1/|S·u| — thân đứng × 0.985, nét "\\" 45° × 1.09, "/" × 0.92
(đo trên font: o O s S x X +7…+9 %, nét mảnh vòng −8 %, n H −3 %).
Bù TRƯỚC khi nghiêng: mỗi cạnh đa giác điều khiển dời song song (Tiller–Hanson, symbols.hdilate) một khoảng
    k = t · (|S·u| − 1) / 2          (dương = nới ra ngoài mực)
t = độ dày nét TẠI CHỖ (bắn tia từ mép vào trong tới mép đối diện; chặn ≤ TCAP × thân H cùng weight — vùng khớp / chân loe
tia đi xa). Sau khi nghiêng mọi nét có độ dày vuông góc ≈ Roman. Không đổi số điểm → variable vẫn tương thích."""
import math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, 'ref'))
TCAP = 1.15

def _polys(p, n=16):
    out = []; cur = None; pl = []
    for v, ps in p.segments:
        if v == 'moveTo': cur = ps[0]; pl = [cur]
        elif v == 'lineTo': pl.append(ps[0]); cur = ps[0]
        elif v == 'curveTo':
            a, b, c = ps
            for i in range(1, n + 1):
                t = i/n; u = 1 - t
                pl.append(tuple(u**3*cur[k] + 3*u*u*t*a[k] + 3*u*t*t*b[k] + t**3*c[k] for k in (0, 1)))
            cur = c
        elif v == 'closePath': out.append(pl)
    return out

def _ray(polys, o, dvec):
    best = None
    for P in polys:
        for a, b in zip(P, P[1:] + P[:1]):
            ex, ey = b[0] - a[0], b[1] - a[1]; den = dvec[0]*ey - dvec[1]*ex
            if abs(den) < 1e-12: continue
            s = ((a[0] - o[0])*ey - (a[1] - o[1])*ex)/den; r = ((a[0] - o[0])*dvec[1] - (a[1] - o[1])*dvec[0])/den
            if 0 <= r <= 1 and s > 2.0 and (best is None or s < best): best = s
    return best

def to_d(p):
    out = []
    for v, ps in p.segments:
        if v == 'moveTo': out.append('M%.2f %.2f' % ps[0])
        elif v == 'lineTo': out.append('L%.2f %.2f' % ps[0])
        elif v == 'curveTo': out.append('C' + ' '.join('%.2f %.2f' % q for q in ps))
        elif v == 'closePath': out.append('Z')
    return ''.join(out)

def stem_of(dH):
    from make_ref import outline
    import vn_punct as V
    p = outline([dH]); b = p.bounds
    I = V.I(p, V.rect(b[0] - 5, 149.95, b[2] + 5, 150.05))   # dưới thanh ngang (H Bold: thanh chạm y 350)
    return min(q.bounds[2] - q.bounds[0] for q in I.contours)

def compensate(d, ang, stem):
    from make_ref import outline
    import symbols as SY
    import numpy as np
    p = outline([d]); P = _polys(p); kk = math.tan(math.radians(ang)); cap = TCAP*stem
    A = np.array([a for pl in P for a in pl]); B = np.array([b for pl in P for b in pl[1:] + pl[:1]]); E = B - A
    def dist(pt, u, nv):
        f = math.hypot(u[0] + kk*u[1], u[1]) - 1.0                # |S·u| − 1
        if abs(f) < 1e-4: return 0.0
        i = int(np.argmin(((A - pt)**2).sum(1))); q = A[i]          # điểm trên mép gần nhất (tay nắm nằm ngoài mép)
        o = q - 0.5*np.array(nv); dv = -np.array(nv)
        den = dv[0]*E[:, 1] - dv[1]*E[:, 0]; ok = np.abs(den) > 1e-12
        with np.errstate(divide='ignore', invalid='ignore'):
            sA = ((A[:, 0] - o[0])*E[:, 1] - (A[:, 1] - o[1])*E[:, 0])/den
            rA = ((A[:, 0] - o[0])*dv[1] - (A[:, 1] - o[1])*dv[0])/den
        m = ok & (rA >= 0) & (rA <= 1) & (sA > 2.0)
        t = float(sA[m].min()) if m.any() else cap
        return min(t, cap)*f/2
    return to_d(SY.hdilate(p, 0.1*stem, 0.0, dist=dist))
