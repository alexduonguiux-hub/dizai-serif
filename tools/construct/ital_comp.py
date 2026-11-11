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

def _bez(sg, t):
    if sg[0] == 'L': a, b = sg[1], sg[2]; return (a[0] + (b[0] - a[0])*t, a[1] + (b[1] - a[1])*t)
    a, b, c, d = sg[1:]; u = 1 - t
    return tuple(u**3*a[k] + 3*u*u*t*b[k] + 3*u*t*t*c[k] + t**3*d[k] for k in (0, 1))

def _segs(p):
    cs = []; cur = st = None
    for v, ps in p.segments:
        if v == 'moveTo': cs.append([]); cur = st = ps[0]
        elif v == 'lineTo': cs[-1].append(['L', cur, ps[0]]); cur = ps[0]
        elif v == 'curveTo': cs[-1].append(['C', cur, *ps]); cur = ps[2]
        elif v == 'closePath':
            if math.dist(cur, st) > 1e-9: cs[-1].append(['L', cur, st])
    return cs

def _unit(v):
    L = math.hypot(*v); return (v[0]/L, v[1]/L) if L > 1e-9 else None
def _tin(sg):
    for q in sg[2:]:
        u = _unit((q[0] - sg[1][0], q[1] - sg[1][1]))
        if u: return u
def _tout(sg):
    for q in reversed(sg[1:-1]):
        u = _unit((sg[-1][0] - q[0], sg[-1][1] - q[1]))
        if u: return u
    return _tin(sg)
def _ang(a, b):
    if not a or not b: return 180.0
    return math.degrees(math.acos(max(-1.0, min(1.0, a[0]*b[0] + a[1]*b[1]))))

def _kap(sg, n=24):
    P0, P1, P2, P3 = sg[1:]; ks = []
    for i in range(n + 1):
        t = i/n; u = 1 - t
        d1 = [3*u*u*(P1[j] - P0[j]) + 6*u*t*(P2[j] - P1[j]) + 3*t*t*(P3[j] - P2[j]) for j in (0, 1)]
        d2 = [6*u*(P2[j] - 2*P1[j] + P0[j]) + 6*t*(P3[j] - 2*P2[j] + P1[j]) for j in (0, 1)]
        sp = math.hypot(*d1)
        if sp < 1e-9: return None
        ks.append((d1[0]*d2[1] - d1[1]*d2[0])/sp**3)
    return ks

def compensate(d, ang, stem):
    """S26 (+ 10/11 "kiểm tra lại italic các chữ có loe"): MỘT độ dày t cho mỗi đoạn (đo ở giữa đoạn) — mỗi cạnh điều khiển một
    t riêng làm đoạn loe gợn (đổi chiều cong); sau khi dời, nút liền ở Roman được làm liền lại (cạnh thẳng giữ hướng)"""
    import numpy as np
    from make_ref import outline
    import symbols as SY
    p = outline([d]); P = _polys(p); kk = math.tan(math.radians(ang)); cap = TCAP*stem
    A = np.array([a for pl in P for a in pl]); B = np.array([b for pl in P for b in pl[1:] + pl[:1]]); E = B - A
    def thick(q, nv):
        o = np.array(q) - 0.5*np.array(nv); dv = -np.array(nv)
        den = dv[0]*E[:, 1] - dv[1]*E[:, 0]; ok = np.abs(den) > 1e-12
        with np.errstate(divide='ignore', invalid='ignore'):
            sA = ((A[:, 0] - o[0])*E[:, 1] - (A[:, 1] - o[1])*E[:, 0])/den
            rA = ((A[:, 0] - o[0])*dv[1] - (A[:, 1] - o[1])*dv[0])/den
        m = ok & (rA >= 0) & (rA <= 1) & (sA > 2.0)
        return min(float(sA[m].min()) if m.any() else cap, cap)
    def dist(pt, u, nv, sg):
        f = math.hypot(u[0] + kk*u[1], u[1]) - 1.0                # |S·u| − 1
        if abs(f) < 1e-4: return 0.0
        i = int(np.argmin(((A - np.array(pt))**2).sum(1)))           # độ dày tại điểm mép gần đầu cạnh nhất (o bút dẹt: nét dày
        return thick(A[i], nv)*f/2                                  # lệch khỏi giữa đoạn — đo giữa đoạn thiếu bù: o +6 %)
    before = _segs(p)
    out = SY.hdilate(p, 0.1*stem, 0.0, dist=dist)
    after = _segs(out)
    if [len(c) for c in before] == [len(c) for c in after] and all(x[0] == y[0] for c0, c1 in zip(before, after) for x, y in zip(c0, c1)):
        # HƯỚNG tay nắm = Roman (dời song song Tiller–Hanson không đổi hướng cạnh điều khiển; nhưng neo dời tới giao điểm mới còn tay
        # ngắn đứng yên → quay hướng: góc nhọn z 153° → 27°, ? , 5 …). Giữ độ dài sau bù (chỉ cứu tay < 8 u / < ½ Roman). Nút liền ở
        # Roman tự liền lại (hai tay / cạnh thẳng cùng hướng gốc, cạnh thẳng dời song song)
        for S0, S1 in zip(before, after):
            for i, (a0, a1) in enumerate(zip(S0, S1)):
                if a1[0] != 'C': continue
                c0, c1 = math.dist(a0[1], a0[4]), math.dist(a1[1], a1[4])
                sc = min(1.3, max(0.7, c1/c0)) if c0 > 1e-6 else 1.0
                for hi, ai in ((2, 1), (3, 4)):
                    d0 = _unit((a0[hi][0] - a0[ai][0], a0[hi][1] - a0[ai][1]))
                    if not d0: a1[hi] = a1[ai]; continue                   # tay suy biến ở Roman: GIỮ suy biến (đuôi S Italic uốn)
                    # 11/11 ("QA lại đường curve 2, S"): độ dài = Roman × tỉ lệ dây cung — độ dài tay từ giao cạnh dời làm độ cong
                    # dồn (bụng phải 2 Italic 4.5 → 22 ×10⁻³; W loe tay 12 → 110 u)
                    Lr = math.dist(a0[hi], a0[ai])*sc; L1_ = math.dist(a1[hi], a1[ai])
                    L = min(max(L1_, 0.92*Lr), 1.08*Lr)                    # giữ phần bù (o O e) nhưng kẹp ±8 % quanh Roman
                    a1[hi] = (a1[ai][0] + d0[0]*L, a1[ai][1] + d0[1]*L)
        # ĐOẠN LOE (nhập cạnh thẳng > 40 u, đầu kia trên đường chân / x-height / cap / descender; dây cung ≤ 110 u): KHÔNG dời từng
        # cạnh (điểm chân và điểm nhập dời khác nhau → dây cung méo, độ cong dồn một đầu: K Italic 0.35 → 1.5) — TỊNH TIẾN NGANG
        # nguyên đoạn loe Roman cho điểm nhập nằm trên mép thẳng ĐÃ BÙ: hình module giữ nguyên, liền tiếp tuyến (mép bù song song),
        # chân vẫn trên đường chân / đỉnh
        for S0, S1 in zip(before, after):
            n = len(S0)
            for i, (a0, a1) in enumerate(zip(S0, S1)):
                if a0[0] != 'C': continue
                ih, ij = (i - 1) % n, (i + 1) % n
                cand = [(ih, 1), (ij, 0)]                                  # (chỉ số cạnh thẳng, đầu nối: 1 = cuối đoạn loe)
                sm = {ih: _ang(_tout(S0[ih]), _tin(a0)) < 0.5, ij: _ang(_tout(a0), _tin(S0[ij])) < 0.5}
                lines = [(k, e) for k, e in cand if S0[k][0] == 'L' and math.dist(S0[k][1], S0[k][2]) > 40 and sm[k]]
                if len(lines) != 1: continue                           # cạnh nhập = cạnh thẳng nối LIỀN; đầu kia là góc chân
                k, e = lines[0]
                J0 = a0[1] if k == ih else a0[4]; F0 = a0[4] if k == ih else a0[1]
                other = S0[ij] if k == ih else S0[ih]                      # cạnh ở đầu CHÂN: ngang (đường chân, x-height, cap,
                horiz = other[0] == 'L' and abs(other[1][1] - other[2][1]) < 0.5   # descender, mặt cắt đuôi y −136 …)
                if not horiz and min(abs(F0[1] - y) for y in (0.0, 495.0, 700.0, -202.0)) > 1.5: continue
                if math.dist(a0[1], a0[4]) > 110: continue
                Ln = S1[k]; (x1, y1), (x2, y2) = Ln[1], Ln[2]
                if abs(y2 - y1) < 1e-6: continue
                vx = x1 + (J0[1] - y1)*(x2 - x1)/(y2 - y1) - J0[0]              # điểm nhập lên mép đã bù, cùng cao độ
                if abs(vx) > 15: continue
                S1[i] = [a0[0]] + [(q[0] + vx, q[1]) for q in a0[1:]]
                Jn, Fn = (J0[0] + vx, J0[1]), (F0[0] + vx, F0[1])
                if k == ih: S1[ih][2] = Jn; S1[ij][1] = Fn
                else: S1[ij][1] = Jn; S1[ih][2] = Fn
                if S1[ih][0] == 'C' and k != ih: pass
        o2 = []
        for S1 in after:
            o2.append('M%.2f %.2f' % S1[0][1])
            for sg in S1:
                o2.append(('L%.2f %.2f' % sg[2]) if sg[0] == 'L' else 'C' + ' '.join('%.2f %.2f' % q for q in sg[2:]))
            o2.append('Z')
        return ''.join(o2)
    return to_d(out)
