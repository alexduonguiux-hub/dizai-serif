#!/usr/bin/env python3
"""S45 Cân độ dày bụng a b d p q (designer 19/11: "các chữ vừa update khi nãy chưa cân bằng weight với các chữ cũ. có điểm mỏng hơn
và dày hơn").
    python3 tools/construct/lower/balance_bowls.py   → ghi khối D_*_S45 vào lower/src_lower.py (chạy lại cho cùng kết quả)

Đo vòng bụng (mỗi điểm mép ngoài → khoảng cách nhỏ nhất tới mép lòng, bỏ vùng thân): bản vẽ S44 nét nhấn 107–109 u (bản cũ đã
duyệt 96.2), nét mảnh 33–34 u (cũ 42.1); a 106 / 64 (cũ 96 / 75). Giữ MÉP NGOÀI và HƯỚNG NGHIÊNG lòng của bản vẽ; chỉ dời + co giãn
lòng (tịnh tiến + co giãn ĐỀU quanh tâm lòng — S45b: giữ tỉ lệ và góc nghiêng elip lòng; co hai trục khác nhau làm lòng a tròn, mất góc) để nét nhấn / nét mảnh về đúng số bản
cũ, thay đổi nhỏ nhất. Luật Bold (lower.bold) đọc lòng bản Regular → Bold cân theo."""
import math, os, re, subprocess, sys
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, '..'), os.path.join(HERE, '..', 'ref')]
import src_lower as SL
OLD_COMMIT = 'ed3182d'                                   # v0.916: bụng đã duyệt
TOK = r'[MLCZ]|-?[\d.]+(?:e-?\d+)?'

def contours(d):
    toks = re.findall(TOK, d); i = 0; cs = []; cur = None
    while i < len(toks):
        t = toks[i]; i += 1
        if t == 'Z': cs.append(cur); continue
        k = {'M': 1, 'L': 1, 'C': 3}[t]; P = [(float(toks[i + 2*j]), float(toks[i + 2*j + 1])) for j in range(k)]; i += 2*k
        if t == 'M': cur = [['M', P]]
        else: cur.append([t, P])
    return cs
def to_str(cs):
    return ' '.join(' '.join(c + ' '.join('%.3f %.3f' % p for p in P) for c, P in C) + ' Z' for C in cs)
def sample(C, m=(1, 0, 0, 0, 1, 0), n=40):
    a, b, c, dd, e, f = m; T = lambda p: np.array((a*p[0] + b*p[1] + c, dd*p[0] + e*p[1] + f)); out = []; last = None
    for t, P in C:
        if t in ('M', 'L'): last = T(P[0]); out.append(last)
        else:
            p1, p2, p3 = map(T, P)
            for s in np.linspace(0, 1, n)[1:]:
                u = 1 - s; out.append(u**3*last + 3*u*u*s*p1 + 3*u*s*s*p2 + s**3*p3)
            last = p3
    return np.array(out)
def stats(outer, inner, excl):
    o = outer[~((outer[:, 0] >= excl[0]) & (outer[:, 0] <= excl[1]))] if excl else outer
    d = np.min(np.hypot(o[:, None, 0] - inner[None, :, 0], o[:, None, 1] - inner[None, :, 1]), 1)*SL.S
    return d.max(), d.min()
def stem_excl(G, SH, ch):
    k, m = [x for x in G[ch] if 'stem' in x[0]][0]; P = sample(contours(SH[k])[0], m); return (P[:, 0].min() - 4, P[:, 0].max() + 4)

if __name__ == '__main__':
    old_src = subprocess.run(['git', 'show', f'{OLD_COMMIT}:tools/construct/lower/src_lower.py'], capture_output=True, text=True,
                             cwd=os.path.join(HERE, '..', '..', '..')).stdout
    ns = {}; exec(compile(old_src, 'src_lower_old', 'exec'), ns)
    out = {}
    for ch, key, const in (('a', 'a_bowl', 'D_A_BOWL_S45'), ('d', 'd_bowl', 'D_D_BOWL_S45'), ('q', 'q_bowl', 'D_Q_BOWL_S45'), ('p', 'p_bowl', 'D_P_BOWL_S45')):
        ko, mo = [x for x in ns['GLYPH'][ch] if 'bowl' in x[0]][0]
        oc = contours(ns['SHAPES'][ko]); oo, oi = sorted(oc, key=lambda C: -np.ptp(sample(C, mo)[:, 0]))[:2]
        tmax, tmin = stats(sample(oo, mo), sample(oi, mo), stem_excl(ns['GLYPH'], ns['SHAPES'], ch))
        src = getattr(SL, key.upper() + '_S44') if hasattr(SL, key.upper() + '_S44') else SL.SHAPES[key]
        src = {'a_bowl': SL.D_A_BOWL_S44, 'd_bowl': SL.D_D_BOWL_S44, 'q_bowl': SL.D_Q_BOWL_S44, 'p_bowl': SL.D_P_BOWL_S44}[key]
        m = [x for x in SL.GLYPH[ch] if 'bowl' in x[0]][0][1]
        cs = contours(src); outer, inner = sorted(cs, key=lambda C: -np.ptp(sample(C)[:, 0]))[:2]
        ex = stem_excl(SL.GLYPH, SL.SHAPES, ch) if ch != 'a' else stem_excl(SL.GLYPH, SL.SHAPES, 'a')
        # khung toạ độ của chữ (áp m) chỉ để bỏ vùng thân; lòng biến đổi trong toạ độ bản vẽ (cùng hệ với m = tịnh tiến)
        Po = sample(outer, m); Pi0 = sample(inner)
        c0 = Pi0.mean(0); U, s, Vt = np.linalg.svd(Pi0 - c0, full_matrices=False); R = Vt          # trục lòng
        def A_(x):
            dx, dy, la, lb = x
            if ch == 'a': lb = la                                      # S45b: a co giãn ĐỀU — giữ tỉ lệ + góc nghiêng lòng bản vẽ
            M = R.T @ np.diag([math.exp(la), math.exp(lb)]) @ R      # (designer: "mất góc của bụng chữ a"); d q p: hai trục (S45)
            return lambda p: (M @ (np.array(p) - c0) + c0 + np.array([dx, dy]))
        # S45b: a — lòng KHÔNG dời xuống (y Figma hướng xuống: dy > 0): dời xuống 7 px làm đáy lòng sát chân thân, nét còn 19 u
        # S45b: vùng gần thân (dải 30 px ngoài thân, cả hai phía): lòng không được tiến sát mép ngoài hơn bản vẽ (a dời lòng 20 u
        # → nét đáy cạnh thân còn 19 u)
        band = (ex[0] - 30, ex[1] + 30)
        def junction(Pi):
            o = Po[((Po[:, 0] >= band[0]) & (Po[:, 0] < ex[0])) | ((Po[:, 0] > ex[1]) & (Po[:, 0] <= band[1]))]
            if not len(o): return 1e9
            return float(np.min(np.hypot(o[:, None, 0] - Pi[None, :, 0], o[:, None, 1] - Pi[None, :, 1])))*SL.S
        jmin0 = junction(sample(inner, m)); mn0 = stats(Po, sample(inner, m), ex)[1]
        # độ CẮT SÂU của lòng vào thân (bản vẽ ~9 px → góc lòng–thân rõ): giữ ≥ bản vẽ — dời lòng ra khỏi thân làm lòng chạm hờ mép
        # thân, góc lưng chừng 13–17° (q Medium–Bold gãy)
        stem_right = (ex[0] + ex[1])/2 > Po[:, 0].mean()
        def depth(Pi): return (Pi[:, 0].max() - (ex[0] + 4)) if stem_right else ((ex[1] - 4) - Pi[:, 0].min())
        dep0 = depth(sample(inner, m))
        def cost(x):
            T = A_(x); Pi = np.array([T(p) for p in Pi0])
            a, b, c, dd, e, f = m; Pi = np.stack([a*Pi[:, 0] + b*Pi[:, 1] + c, dd*Pi[:, 0] + e*Pi[:, 1] + f], 1)
            mx, mn = stats(Po, Pi, ex)
            # a: nét mảnh chỉ cần KHÔNG MỎNG HƠN bản vẽ (đỉnh a mảnh hơn a cũ là chủ ý của bản vẽ)
            return ((mx - tmax)/tmax)**2 + (((mn - tmin)/tmin)**2 if ch != 'a' else 4*max(0.0, (mn0 - mn)/mn0)**2) + 1e-4*(x[0]**2 + x[1]**2) + 0.05*(x[2]**2 + x[3]**2) + 50*max(0.0, (jmin0 - junction(Pi))/jmin0)**2 + (5*max(0.0, x[1] - 0.5)**2 if ch == 'a' else 0.0) + 5*max(0.0, dep0 - depth(Pi))**2
        r = minimize(cost, [0, 0, 0, 0], method='Nelder-Mead', options=dict(xatol=1e-4, fatol=1e-10, maxiter=4000))
        T = A_(r.x)
        inner2 = [[t, [tuple(T(p)) for p in P]] for t, P in inner]
        Pi = sample(inner2, m); mx, mn = stats(Po, Pi, ex); mx0, mn0 = stats(Po, sample(inner, m), ex)
        print(f'{ch}: cắt vào thân {dep0:.1f} → {depth(Pi):.1f} px · ', end='')
        print(f'{ch}: nhấn {mx0:.1f} → {mx:.1f} (đích {tmax:.1f}) · mảnh {mn0:.1f} → {mn:.1f} (đích {tmin:.1f}) · '
              f'dời ({r.x[0]:.2f}, {r.x[1]:.2f}) px · giãn {math.exp(r.x[2]):.3f} / {math.exp(r.x[2] if ch == "a" else r.x[3]):.3f}')
        out[const] = to_str([outer, inner2])
    p = os.path.join(HERE, 'src_lower.py'); s = open(p).read()
    blk = '# --- S45 (lower/balance_bowls.py, sinh tự động): lòng bụng cân theo độ dày bản đã duyệt ---\n' + \
          ''.join(f'{k} = "{v}"\n' for k, v in out.items()) + '# --- hết S45 ---\n'
    s = re.sub(r'# --- S45 .*?# --- hết S45 ---\n', '', s, flags=re.S)
    i = s.index('SHAPES = {'); s = s[:i] + blk + '\n' + s[i:]
    s = re.sub(r"'a_bowl': D_A_BOWL_S4[45], 'd_bowl': D_D_BOWL_S4[45], 'q_bowl': D_Q_BOWL_S4[45], 'p_bowl': D_P_BOWL_S4[45],",
               "'a_bowl': D_A_BOWL_S45, 'd_bowl': D_D_BOWL_S45, 'q_bowl': D_Q_BOWL_S45, 'p_bowl': D_P_BOWL_S45,", s)
    open(p, 'w').write(s)
