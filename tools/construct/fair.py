"""Làm trơn chuỗi cung (S69, designer 21/11 "bụng cong dấu hỏi hơi gợn"): giữ MỌI điểm neo và hướng tiếp tuyến, chỉ chọn lại độ dài
tay nắm trên mỗi chuỗi cung nối trơn (G1) — tối thiểu ∫(dκ/ds)² + bậc độ cong ở mối nối (G2), lệch đường cũ ≤ maxdev đơn vị.
Góc chủ ý (lệch hướng > 3°) và đoạn thẳng giữ nguyên.
    fair_contours(contours, maxdev) — contours: [[('M', p) | ('L', p) | ('C', c1, c2, p) …], …] (đóng)."""
import math
import numpy as np
from scipy.optimize import minimize

T = np.linspace(0, 1, 21)[:, None]
def _bez(P, t=T): return (1-t)**3*P[0] + 3*(1-t)**2*t*P[1] + 3*(1-t)*t*t*P[2] + t**3*P[3]
def _kap(P, t=T):
    d1 = 3*((1-t)**2*(P[1]-P[0]) + 2*(1-t)*t*(P[2]-P[1]) + t*t*(P[3]-P[2])); d2 = 6*((1-t)*(P[2]-2*P[1]+P[0]) + t*(P[3]-2*P[2]+P[1]))
    sp = np.hypot(d1[:, 0], d1[:, 1]); return (d1[:, 0]*d2[:, 1] - d1[:, 1]*d2[:, 0])/np.maximum(sp, 1e-9)**3, sp
def _unit(v): n = math.hypot(*v); return np.array(v, float)/n if n > 1e-9 else None

def _segments(cont):
    segs = []; cur = np.array(cont[0][1], float); start = cur
    for it in cont[1:]:
        if it[0] == 'L': p = np.array(it[1], float); segs.append(('L', [cur, p])); cur = p
        elif it[0] == 'C': P = [cur] + [np.array(q, float) for q in it[1:]]; segs.append(('C', P)); cur = P[3]
    if np.hypot(*(cur - start)) > 1e-6: segs.append(('L', [cur, start]))
    return segs

def _tan(seg, end):
    k, P = seg
    if k == 'L': return _unit(P[1] - P[0])
    if end: return _unit(P[3] - P[2]) if np.hypot(*(P[3]-P[2])) > 1e-6 else _unit(P[3] - P[1])
    return _unit(P[1] - P[0]) if np.hypot(*(P[1]-P[0])) > 1e-6 else _unit(P[2] - P[0])

def fair_contours(contours, maxdev=2.0, min_len=30.0):
    out = []
    for cont in contours:
        segs = _segments(cont); n = len(segs)
        smooth = []                                                    # mối nối i: cuối seg i → đầu seg i+1
        for i in range(n):
            a, b = segs[i], segs[(i + 1) % n]; ta, tb = _tan(a, True), _tan(b, False)
            ok = ta is not None and tb is not None and math.degrees(math.acos(max(-1, min(1, float(ta @ tb))))) < 3.0
            smooth.append(ok and a[0] == 'C' and b[0] == 'C')
        idx = [i for i in range(n) if segs[i][0] == 'C' and math.hypot(*(segs[i][1][3] - segs[i][1][0])) >= min_len]
        if not idx or all(smooth[i] for i in range(n)):                # vòng kín trơn (chấm tròn): giữ
            out.append(cont); continue
        old = {i: [p.copy() for p in segs[i][1]] for i in idx}
        # mối nối trơn giữa hai đoạn tối ưu: điểm neo dời theo pháp tuyến ≤ maxdev, tiếp tuyến xoay ≤ 4°
        J = [i for i in idx if smooth[i] and (i + 1) % n in old]
        tj = {i: _tan(segs[i], True) for i in J}
        dirs = {i: (_tan(segs[i], False), _tan(segs[i], True)) for i in idx}
        L0 = [v for i in idx for v in (math.hypot(*(old[i][1]-old[i][0])), math.hypot(*(old[i][3]-old[i][2])))]
        x0 = np.array(L0 + [0.0]*(2*len(J)))
        samp = np.vstack([_bez(old[i], np.linspace(0, 1, 201)[:, None]) for i in idx])
        def rot(u, a): c, s_ = math.cos(a), math.sin(a); return np.array([u[0]*c - u[1]*s_, u[0]*s_ + u[1]*c])
        def build(x):
            nL = 2*len(idx); P0 = {i: old[i][0] for i in idx}; P3 = {i: old[i][3] for i in idx}
            U0 = {i: dirs[i][0] for i in idx}; U1 = {i: dirs[i][1] for i in idx}
            for m, i in enumerate(J):
                j = (i + 1) % n; d_, a_ = x[nL + 2*m], math.radians(x[nL + 2*m + 1]); t = tj[i]; nrm = np.array([-t[1], t[0]])
                q = old[i][3] + nrm*d_; u = rot(t, a_); P3[i] = q; P0[j] = q; U1[i] = u; U0[j] = u
            return {i: [P0[i], P0[i] + U0[i]*x[2*k], P3[i] - U1[i]*x[2*k+1], P3[i]] for k, i in enumerate(idx)}
        def cost(x):
            S = build(x); c = 0.0; K = {}; SP = {}
            allb = []
            for i in idx:
                k, sp = _kap(S[i]); K[i] = k; SP[i] = sp; ds = sp/20; c += float(np.sum(np.diff(k)**2/np.maximum(ds[1:], 1e-6)))*1e3
                allb.append(_bez(S[i]))
            for i in J:
                j = (i + 1) % n; c += 1e3*(K[i][-1] - K[j][0])**2/2.0          # bậc độ cong ở mối nối = như trên 2 u cung
            b = np.vstack(allb); dv = float(np.sqrt(((b[:, None, :] - samp[None, :, :])**2).sum(-1)).min(1).max())
            c += 1e4*max(0.0, dv - maxdev)**2
            return c
        nL = 2*len(idx)
        bnds = [(3, None)]*nL + [b for _ in J for b in ((-maxdev, maxdev), (-4.0, 4.0))]
        r = minimize(cost, x0, method='L-BFGS-B', bounds=bnds, options=dict(maxiter=4000, ftol=1e-13, gtol=1e-10))
        S = build(r.x)
        new = [cont[0]]; k = 0
        for it in cont[1:]:
            if it[0] == 'C':
                if k in S: P = S[k]; new.append(('C', tuple(P[1]), tuple(P[2]), tuple(P[3])))
                else: new.append(it)
            elif it[0] == 'L': new.append(it)
            if it[0] in ('L', 'C'): k += 1
        if (n - 1) in S and segs[n - 1][0] == 'C' and smooth[n - 1]: new[0] = ('M', tuple(S[n - 1][3]))
        out.append(new)
    return out
