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

def compensate(d, ang, stem, raw=False, smooth=True):
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
        if smooth: _refit(before, after)
        if raw: return before, after
        if smooth: _g2([(before, after)])
        return _ser(after)
    return None if raw else to_d(out)


def _refit(before, after):
    """S38: mỗi đoạn cong sau bù = đường SONG SONG mượt của đoạn Roman: độ dời theo pháp tuyến δ(t) (đo từ bước bù) làm trơn
    thành bậc 2 theo t, điểm mẫu Q(t) = Roman(t) + δ(t)·n(t); giữ hai điểm neo (sau bù) + hướng tiếp tuyến Roman, khớp độ dài hai
    tay (bình phương tối thiểu). Bước bù dời điểm điều khiển không đều → méo cục bộ (cực phải 2 Bold Italic: độ cong × 2).
    Đoạn tịnh tiến nguyên (loe) giữ nguyên."""
    import numpy as np
    T = np.linspace(0, 1, 25)
    def pts(sg):
        P = np.array(sg[1:], float); u = 1 - T[:, None]
        return u**3*P[0] + 3*u*u*T[:, None]*P[1] + 3*u*T[:, None]**2*P[2] + T[:, None]**3*P[3]
    def der(sg):
        P = np.array(sg[1:], float); u = 1 - T[:, None]
        return 3*u*u*(P[1] - P[0]) + 6*u*T[:, None]*(P[2] - P[1]) + 3*T[:, None]**2*(P[3] - P[2])
    def offs(a0, a1):
        """độ dời pháp tuyến đã làm trơn (hệ số bậc 2), hoặc None"""
        dv = [(q1[0] - q0[0], q1[1] - q0[1]) for q0, q1 in zip(a0[1:], a1[1:])]
        if max(math.dist(dv[0], x) for x in dv) < 0.05: return None           # tịnh tiến nguyên (đoạn loe)
        B0, B1, D = pts(a0), pts(a1), der(a0); sp = np.hypot(D[:, 0], D[:, 1])
        if sp.min() < 1e-6: return None
        N = np.stack([-D[:, 1]/sp, D[:, 0]/sp], 1)
        return np.polyfit(T, ((B1 - B0)*N).sum(1), 2), B0, N
    from scipy.interpolate import UnivariateSpline
    after_orig = {id(S1): [list(x) for x in S1] for S1 in after}
    for S0, S1 in zip(before, after):
        n = len(S0); O_ = [offs(a0, a1) if a0[0] == 'C' == a1[0] else None for a0, a1 in zip(S0, S1)]
        sm = [_ang(_tout(S0[i]), _tin(S0[(i + 1) % n])) < 0.5 for i in range(n)]
        # chuỗi đoạn cong nối LIỀN (C–C, nút liền ở Roman): làm trơn δ theo độ dài cung qua cả chuỗi (spline bậc 3) — δ làm trơn
        # riêng từng đoạn gãy đạo hàm ở nút → nhảy độ cong
        used = [False]*n; chains = []
        for i0 in range(n):
            if not O_[i0] or used[i0]: continue
            st = i0
            for _ in range(n):                                              # lùi tới đầu chuỗi
                p_ = (st - 1) % n
                if O_[p_] and sm[p_] and p_ != i0 and not used[p_]: st = p_
                else: break
            ch = [st]; used[st] = True; k = st
            while sm[k] and O_[(k + 1) % n] and not used[(k + 1) % n]:
                k = (k + 1) % n; ch.append(k); used[k] = True
            chains.append(ch)
        dl = {}; dd = {}
        for ch in chains:
            S_, D_, off = [], [], 0.0
            for k in ch:
                c, B0, N = O_[k]; seg = np.hypot(*np.diff(B0, axis=0).T); sk = np.concatenate([[0], np.cumsum(seg)])
                raw = ((pts(after_orig[id(S1)][k]) - B0)*N).sum(1)
                S_.append(off + sk); D_.append(raw); off += sk[-1]
            S_ = np.concatenate(S_); D_ = np.concatenate(D_)
            o = np.argsort(S_, kind='stable'); S_, D_ = S_[o], D_[o]
            keep = np.concatenate([[True], np.diff(S_) > 1e-6]); S_, D_ = S_[keep], D_[keep]
            if len(S_) > 5:
                spl = UnivariateSpline(S_, D_, k=3, s=len(S_)*0.15**2); dsp = spl.derivative()
            else: spl = None
            off = 0.0
            for k in ch:
                c, B0, N = O_[k]; seg = np.hypot(*np.diff(B0, axis=0).T); sk = np.concatenate([[0], np.cumsum(seg)])
                dl[k] = spl(off + sk) if spl is not None else np.polyval(c, T)
                dd[k] = (float(dsp(off)), float(dsp(off + sk[-1]))) if spl is not None else None
                off += sk[-1]
        jd = {}                                                             # δ' chung ở mỗi nút (chuỗi kín: spline không tuần hoàn
        for i in range(n):                                                  # → hai đầu lệch nhau)
            j = (i + 1) % n
            if i in dl and j in dl and sm[i] and dd.get(i) and dd.get(j): jd[i] = (dd[i][1] + dd[j][0])/2
        for i in range(n):                                                  # neo ở nút liền C–C: neo Roman + δ·n
            j = (i + 1) % n
            if i not in dl or j not in dl or not sm[i]: continue
            dlt = (dl[i][-1] + dl[j][0])/2; Nn = (O_[i][2][-1] + O_[j][2][0])/2
            Nn = Nn/np.hypot(*Nn); P = S0[i][4]; Pn = (P[0] + dlt*Nn[0], P[1] + dlt*Nn[1])
            S1[i] = list(S1[i]); S1[j] = list(S1[j]); S1[i][4] = Pn; S1[j][1] = Pn
        def fit(k, rot):
            a0, a1 = S0[k], S1[k]
            d0 = _unit((a0[2][0] - a0[1][0], a0[2][1] - a0[1][1])); d1 = _unit((a0[3][0] - a0[4][0], a0[3][1] - a0[4][1]))
            if not d0 or not d1: return None                                    # tay suy biến: giữ
            c, B0, N = O_[k]
            # tiếp tuyến đường song song q = p + δ·n: q' ∝ t + δ'·n → ở nút liền TRONG chuỗi, hướng tay xoay theo δ' (Roman: tay ép
            # đúng hướng gốc → đoạn bẻ gắt ở đầu mút, cực phải 2 Italic độ cong × 1.8). Góc thật / nút cạnh đoạn không khớp: hướng Roman
            p_ = (k - 1) % n
            if p_ in rot:
                Nn = (O_[p_][2][-1] + N[0])/2; Nn = Nn/np.hypot(*Nn); g = jd[p_]
                d0 = _unit((d0[0] + g*Nn[0], d0[1] + g*Nn[1]))
            if k in rot:
                Nn = (N[-1] + O_[(k + 1) % n][2][0])/2; Nn = Nn/np.hypot(*Nn); g = jd[k]
                d1 = _unit((d1[0] - g*Nn[0], d1[1] - g*Nn[1]))
            Q = B0 + dl[k][:, None]*N
            P0, P3 = np.array(a1[1], float), np.array(a1[4], float); u = 1 - T[:, None]
            base = u**3*P0 + 3*u*u*T[:, None]*P0 + 3*u*T[:, None]**2*P3 + T[:, None]**3*P3
            A1 = 3*u*u*T[:, None]*np.array(d0); A2 = 3*u*T[:, None]**2*np.array(d1)
            la, lb = np.linalg.lstsq(np.stack([A1.ravel(), A2.ravel()], 1), (Q - base).ravel(), rcond=None)[0]
            c0 = math.dist(a1[1], a1[4])
            if not (0.05*c0 < la < 1.2*c0 and 0.05*c0 < lb < 1.2*c0): return None
            new = ['C', a1[1], (a1[1][0] + d0[0]*la, a1[1][1] + d0[1]*la), (a1[4][0] + d1[0]*lb, a1[4][1] + d1[1]*lb), a1[4]]
            if _flip(new) and not _flip(a1): return None
            return new
        rot = set(jd)
        for _ in range(6):                                                  # đoạn không khớp → bỏ xoay ở hai nút của nó, khớp lại
            res = {k: fit(k, rot) for k in dl}
            bad = {k for k, v in res.items() if v is None}
            r2 = {i for i in rot if i not in bad and (i + 1) % n not in bad}
            if r2 == rot: break
            rot = r2
        orig = after_orig[id(S1)]
        for k in range(n):
            if res.get(k) is not None: S1[k] = res[k]
            elif S1[k][0] == 'C':                                           # không khớp: tay dời theo neo (giữ hướng)
                o_ = orig[k]; x = list(S1[k])
                x[2] = (o_[2][0] + x[1][0] - o_[1][0], o_[2][1] + x[1][1] - o_[1][1])
                x[3] = (o_[3][0] + x[4][0] - o_[4][0], o_[3][1] + x[4][1] - o_[4][1]); S1[k] = x


def _ser(after):
    o2 = []
    for S1 in after:
        o2.append('M%.2f %.2f' % S1[0][1])
        for sg in S1:
            o2.append(('L%.2f %.2f' % sg[2]) if sg[0] == 'L' else 'C' + ' '.join('%.2f %.2f' % q for q in sg[2:]))
        o2.append('Z')
    return ''.join(o2)


def compensate_pair(dR, dB, ang, sR, sB, smooth=True):
    """S38: bù hai master Italic (Regular, Bold), rồi liền độ cong với hệ số CHUNG ở mỗi nút — tỉ lệ tay vào : tay ra giữ bằng nhau
    ở hai master (compat_masters) → bản nội suy (Medium, SemiBold, variable) không gãy (chỉnh riêng từng master: 9 Italic gãy 5°)"""
    rR = compensate(dR, ang, sR, raw=True, smooth=smooth); rB = compensate(dB, ang, sB, raw=True, smooth=smooth)
    if rR and rB and [[x[0] for x in c] for c in rR[0]] == [[x[0] for x in c] for c in rB[0]]:
        if smooth:
            _g2([rR, rB])
            import compat_masters as CM                                     # nút mà bản nội suy gãy (tỉ lệ tay hai master lệch,
            for R, B in zip(rR[1], rB[1]):                                  # tiếp tuyến khác hướng): đồng bộ tỉ lệ như compat_masters
                n = len(R)
                for i in range(n):
                    j = (i + 1) % n
                    if R[i][0] == B[i][0] and R[j][0] == B[j][0] and 'C' in (R[i][0], R[j][0]) and \
                            max(_ang(_tout(R[i]), _tin(R[j])), _ang(_tout(B[i]), _tin(B[j]))) < 0.5 and CM._mid_kink(R, B, i, j) > 1.0:
                        CM._sync_ratio(R, B, i, j)
        return _ser(rR[1]), _ser(rB[1])
    return compensate(dR, ang, sR, smooth=smooth), compensate(dB, ang, sB, smooth=smooth)


def _kend(sg, end):
    """độ cong ở đầu (end=0) / cuối (end=1) đoạn cong, bỏ hệ số ⅔ (chỉ dùng tỉ lệ)"""
    P0, P1, P2, P3 = sg[1:]
    if end: u = (P3[0] - P2[0], P3[1] - P2[1]); w = (P1[0] - P2[0], P1[1] - P2[1])     # B''(1) ∝ (P3−P2) − (P2−P1)
    else: u = (P1[0] - P0[0], P1[1] - P0[1]); w = (P2[0] - P1[0], P2[1] - P1[1])
    L = math.hypot(*u)
    return (u[0]*w[1] - u[1]*w[0])/L**3 if L > 1e-6 else None


def _flip(sg):
    ks = _kap(sg); return ks is None or (min(ks)*max(ks) < 0 and max(abs(k) for k in ks) > 2e-4)


G2 = True     # S38: sau _refit; chỉ nhận thay đổi làm GIẢM tổng lệch ở nút đó + hai nút bên cạnh (không kéo lệch nút khác)
FAR = True    # S38: phương án "tay ở đầu kia" (có kiểm tra nút bên cạnh — không kéo lệch đỉnh 2 Bold Italic)


def _g2(masters):
    """S38 (11/11 "đường cong vẫn còn gợn"): phép nghiêng giữ TỈ LỆ độ cong hai bên mỗi nút (affine), bước bù đổi độ dài tay làm tỉ
    lệ lệch (bụng phải 2 SemiBold Italic: Roman 1.0 → 3.1). Ở nút liền C–C: κ cuối đoạn = ⅔·C / L² (C không phụ thuộc độ dài tay L)
    → chỉnh tay (giữ hướng) cho tỉ lệ về như Roman: f = (ρ_Roman / ρ_Italic)^¼ (kẹp 0.82–1.22) riêng từng master; nếu bản nội
    suy giữa hai master gãy > 0.5° (tỉ lệ tay hai master lệch, tiếp tuyến khác hướng) thì dùng f chung (trung bình nhân);
    phương án: hai tay (× f, ÷ f) · chỉ tay vào (× f²) · chỉ tay ra (÷ f²) — lấy phương án đầu tiên hợp lệ ở MỌI master
    (không đổi chiều cong, tổng tay ≤ 1.2 dây cung). masters = [(before, after), …] cùng cấu trúc; sửa tại chỗ after"""
    if not G2: return
    # độ dài tay TRƯỚC bước này: đổi cộng dồn kẹp 0.6–1.6 (nhiều lượt nhân dồn: tay đỉnh 2 Bold 43 → 14 u → bản nội suy giữa
    # hai master mất liền độ cong)
    base_len = [[[(math.dist(sg[1], sg[2]), math.dist(sg[3], sg[4])) if sg[0] == 'C' else None for sg in C] for C in after]
                for before, after in masters]
    def okseg(sg, sg0, m=None, ci=None, k=None):
        long_ = lambda q: math.dist(q[1], q[2]) + math.dist(q[3], q[4]) > 1.2*math.dist(q[1], q[4]) + 1
        if long_(sg) and not long_(sg0): return False
        if _flip(sg) and not _flip(sg0): return False
        if m is not None:
            b = base_len[m][ci][k]
            for L, l0 in ((math.dist(sg[1], sg[2]), b[0]), (math.dist(sg[3], sg[4]), b[1])):
                if l0 > 1e-6 and not (0.6*l0 - 0.5 <= L <= 1.6*l0 + 0.5): return False
        return True
    B0 = masters[0][0]
    for _ in range(6):
        for ci, C0 in enumerate(B0):
            n = len(C0)
            for i in range(n):
                j = (i + 1) % n; fs = []
                for before, after in masters:
                    S0, S1 = before[ci], after[ci]; a0, b0, a1, b1 = S0[i], S0[j], S1[i], S1[j]
                    if not (a0[0] == b0[0] == a1[0] == b1[0] == 'C') or _ang(_tout(a0), _tin(b0)) > 0.5: fs = None; break
                    if math.dist(a1[1], a1[2]) < 0.5 or math.dist(b1[3], b1[4]) < 0.5: fs = None; break   # tay suy biến ở đầu kia:
                    ks = (_kend(a0, 1), _kend(b0, 0), _kend(a1, 1), _kend(b1, 0))                         # hướng tiếp tuyến ở đó
                    if None in ks or min(map(abs, ks)) < 2e-4 or ks[0]*ks[1] <= 0 or ks[2]*ks[3] <= 0: fs = None; break   # = tay đang chỉnh
                    fs.append((ks[1]/ks[0])/(ks[3]/ks[2]))
                if not fs: continue
                def opts(f):
                    f = min(1.22, max(0.82, f**0.25)); return ((f, 1/f), (f*f, 1.0), (1.0, 1/(f*f)))
                def trial(per):                                         # per: hệ số từng master → [(A, B)] hoặc None
                    out = []
                    for m, ((before, after), f) in enumerate(zip(masters, per)):
                        a1, b1 = after[ci][i], after[ci][j]; P = a1[4]; got = None
                        if abs(math.log(f)) < 0.05: out.append((a1, b1)); continue
                        for fa, fb in opts(f):
                            A, B = list(a1), list(b1)
                            A[3] = (P[0] + (a1[3][0] - P[0])*fa, P[1] + (a1[3][1] - P[1])*fa)
                            B[2] = (P[0] + (b1[2][0] - P[0])*fb, P[1] + (b1[2][1] - P[1])*fb)
                            if okseg(A, a1, m, ci, i) and okseg(B, b1, m, ci, j): got = (A, B); break
                        if not got: return None
                        out.append(got)
                    return out
                def midkink(new):                                       # góc gãy ở bản nội suy giữa hai master (t = ½)
                    if len(new) < 2: return 0.0
                    (A1, B1), (A2, B2) = new[0], new[1]
                    m = lambda p, q: ((p[0] + q[0])/2, (p[1] + q[1])/2)
                    h, P, k = m(A1[3], A2[3]), m(A1[4], A2[4]), m(B1[2], B2[2])
                    return _ang(_unit((P[0] - h[0], P[1] - h[1])), _unit((k[0] - P[0], k[1] - P[1])))
                def free_end(k_from, k_to):                             # nút giữa đoạn k_from → k_to: đổi tay ở đó không làm gãy
                    angs = []                                           # bản nội suy (góc thật ở Roman, hoặc tiếp tuyến cùng hướng
                    for before, after in masters:                       # ở mọi master: đỉnh ngang, cực phải đứng)
                        S0, S1 = before[ci], after[ci]
                        if _ang(_tout(S0[k_from]), _tin(S0[k_to])) > 0.5: return True
                        angs.append(math.atan2(*reversed(_tout(S1[k_from]))))
                    return max(angs) - min(angs) < math.radians(0.3)
                def far(fs):
                    """S38: nút vai 2 Italic — hai master cần chỉnh ngược chiều, tiếp tuyến hai master khác hướng (chỉnh tay ở nút gãy
                    nội suy). κ đầu đoạn tuyến tính theo vị trí tay nắm ở ĐẦU KIA (tay đó trượt dọc hướng của nó): giữ κ một bên, đặt κ
                    bên kia = κ × ρ_Roman bằng tay ở đầu kia, nếu nút đầu kia 'tự do'"""
                    out = []
                    jb = (j + 1) % n; ia = (i - 1) % n
                    for m, ((before, after), f) in enumerate(zip(masters, fs)):
                        S0, S1 = before[ci], after[ci]; a1, b1 = S1[i], S1[j]; got = None
                        r0 = _kend(S0[j], 0)/_kend(S0[i], 1)
                        if free_end(j, jb):                              # κ_b(0) = cross(u, P2 − P1)/|u|³, P2 = P3 + t·d
                            u = (b1[2][0] - b1[1][0], b1[2][1] - b1[1][1]); P3 = b1[4]; dd = _unit((b1[3][0] - P3[0], b1[3][1] - P3[1]))
                            if dd:
                                cr = lambda v: u[0]*v[1] - u[1]*v[0]; L3 = math.hypot(*u)**3
                                kt = _kend(a1, 1)*r0; c0 = cr((P3[0] - b1[2][0], P3[1] - b1[2][1])); cd = cr(dd)
                                t0 = math.dist(b1[3], P3)
                                if abs(cd) > 1e-9:
                                    t = (kt*L3 - c0)/cd
                                    if 0.7*t0 <= t <= 1.4*t0:
                                        B = list(b1); B[3] = (P3[0] + dd[0]*t, P3[1] + dd[1]*t)
                                        if okseg(B, b1, m, ci, j): got = (a1, B)
                        if not got and free_end(ia, i):                  # κ_a(1) bằng tay ở đầu kia của đoạn a
                            u = (a1[4][0] - a1[3][0], a1[4][1] - a1[3][1]); P0 = a1[1]; dd = _unit((a1[2][0] - P0[0], a1[2][1] - P0[1]))
                            if dd:
                                cr = lambda v: u[0]*v[1] - u[1]*v[0]; L3 = math.hypot(*u)**3
                                kt = _kend(b1, 0)/r0; c0 = cr((P0[0] - a1[3][0], P0[1] - a1[3][1])); cd = cr(dd)
                                t0 = math.dist(a1[2], P0)
                                if abs(cd) > 1e-9:
                                    t = (kt*L3 - c0)/cd
                                    if 0.7*t0 <= t <= 1.4*t0:
                                        A = list(a1); A[2] = (P0[0] + dd[0]*t, P0[1] + dd[1]*t)
                                        if okseg(A, a1, m, ci, i): got = (A, b1)
                        if not got: return None
                        out.append(got)
                    return out
                cur = [(after[ci][i], after[ci][j]) for _, after in masters]
                base = midkink(cur)
                new = trial(fs)                                         # chỉnh riêng từng master; bản nội suy gãy thêm → hệ số chung
                if new is None or midkink(new) > max(0.5, base + 0.1):
                    g = math.exp(sum(math.log(x) for x in fs)/len(fs)); new = trial([g]*len(fs))
                    if new is not None and midkink(new) > max(0.5, base + 0.1): new = None
                def resid(nw):                                          # lệch tỉ lệ độ cong còn lại (lớn nhất giữa các master)
                    r = 0.0
                    for (before, after), (A, B) in zip(masters, nw):
                        S0 = before[ci]; ka, kb = _kend(A, 1), _kend(B, 0)
                        if not ka or not kb or ka*kb <= 0: return 9.0
                        r = max(r, abs(math.log((kb/ka)/(_kend(S0[j], 0)/_kend(S0[i], 1)))))
                    return r
                if FAR and len(masters) > 1 and resid(new or cur) > 0.1:
                    alt = far(fs)
                    if alt and midkink(alt) <= max(0.5, base + 0.1) and resid(alt) < resid(new or cur): new = alt
                def local(nw):                                          # Σ lệch² tỉ lệ độ cong ở nút i−1, i, i+1 (mọi master)
                    tot = 0.0
                    for m, (before, after) in enumerate(masters):
                        S0 = before[ci]; S1 = list(after[ci])
                        if nw is not None: S1[i], S1[j] = nw[m]
                        for q in ((i - 1) % n, i, j):
                            r_ = (q + 1) % n
                            if not (S0[q][0] == S0[r_][0] == S1[q][0] == S1[r_][0] == 'C') or _ang(_tout(S0[q]), _tin(S0[r_])) > 0.5: continue
                            k0 = (_kend(S0[q], 1), _kend(S0[r_], 0), _kend(S1[q], 1), _kend(S1[r_], 0))
                            if None in k0 or min(map(abs, k0)) < 2e-4 or k0[0]*k0[1] <= 0: continue
                            tot += 9.0 if k0[2]*k0[3] <= 0 else math.log((k0[3]/k0[2])/(k0[1]/k0[0]))**2
                    return tot
                if new and local(new) >= local(None) - 1e-4: new = None
                if new:
                    for (before, after), (A, B) in zip(masters, new): after[ci][i], after[ci][j] = A, B
