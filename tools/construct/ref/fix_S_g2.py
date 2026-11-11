#!/usr/bin/env python3
"""S34 S liền độ cong có ràng buộc (designer 11/11: "tôi cảm giác S glyph các đường cong vẫn hơi gãy").
    python3 tools/construct/ref/fix_S_g2.py      (đi từ bản lưu designer_{A,B}_preS34.json → chạy lại cho cùng kết quả)

Góc ở mọi nút S đã liền (G1); cái "gãy" mắt thấy là BƯỚC NHẢY ĐỘ CONG tại nút (bụng ngoài trái −1.9 → −7.8 ×10⁻³, đáy lòng dưới
Bold 15.5 → 5.0 …). S17 (ép G2 toàn bộ) làm bụng mất tròn; lần này có ràng buộc:
  - giữ MỌI điểm neo và HƯỚNG tiếp tuyến (vector Figma của designer) — chỉ đổi ĐỘ DÀI tay nắm (× 0.75 … 1.35)
  - mỗi đoạn lệch hình học ≤ MAXDEV u so với Figma; không thêm điểm uốn; nút có độ cong đổi dấu (điểm uốn sống S) bỏ qua
  - dò từng nút, nhiều lượt (coordinate descent): giảm Σ (κ trái − κ phải)² / κ² tại các nút liền
"""
import json, math, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, '..'), os.path.join(HERE, '..', 'font')]
MAXDEV = 3.0      # u (2 u: đỉnh S chưa liền; 3 u: đỉnh + hai lòng liền, chồng hình gần trùng Figma)
FACT = [0.75 + 0.025*k for k in range(25)]

def kap(sg, t):
    P0, P1, P2, P3 = sg[1:]; u = 1 - t
    d1 = [3*u*u*(P1[j] - P0[j]) + 6*u*t*(P2[j] - P1[j]) + 3*t*t*(P3[j] - P2[j]) for j in (0, 1)]
    d2 = [6*u*(P2[j] - 2*P1[j] + P0[j]) + 6*t*(P3[j] - 2*P2[j] + P1[j]) for j in (0, 1)]
    sp = math.hypot(*d1); return (d1[0]*d2[1] - d1[1]*d2[0])/sp**3 if sp > 1e-9 else None
def bez(sg, t):
    a, b, c, d = sg[1:]; u = 1 - t
    return tuple(u**3*a[k] + 3*u*u*t*b[k] + 3*u*t*t*c[k] + t**3*d[k] for k in (0, 1))
def dev(a, b):
    A = [bez(a, t/24) for t in range(25)]; B = [bez(b, t/48) for t in range(49)]
    return max(min(math.dist(p, q) for q in B) for p in A)
def dev2(a, o1, o2):
    """lệch hình học của đoạn a so với HỢP hai đoạn gốc o1 + o2"""
    A = [bez(a, t/24) for t in range(25)]; B = [bez(o1, t/48) for t in range(49)] + [bez(o2, t/48) for t in range(49)]
    return max(min(math.dist(p, q) for q in B) for p in A)
def flips(sg):
    ks = [kap(sg, t/24) for t in range(25)]
    return None in ks or (min(ks)*max(ks) < 0 and max(abs(k) for k in ks) > 2e-4)

def with_len(orig, cur, which, f):
    sg = list(cur)
    if which == 0: p, h = orig[1], orig[2]; sg[2] = (p[0] + (h[0] - p[0])*f, p[1] + (h[1] - p[1])*f)
    else: p, h = orig[4], orig[3]; sg[3] = (p[0] + (h[0] - p[0])*f, p[1] + (h[1] - p[1])*f)
    return sg

def fair(S0):
    from compat_masters import angle, tan_out, tan_in
    S = [list(s) for s in S0]; n = len(S)
    joints = [i for i in range(n) if S[i][0] == 'C' and S[(i + 1) % n][0] == 'C' and angle(tan_out(S[i]), tan_in(S[(i + 1) % n])) < 0.6]
    def jcost(i):
        a, b = S[i], S[(i + 1) % n]
        if a[0] != 'C' or b[0] != 'C': return 0.0
        ka, kb = kap(a, 1.0), kap(b, 0.0)
        if ka is None or kb is None or ka*kb <= 0: return 0.0
        return (ka - kb)**2/max(abs(ka), abs(kb))**2
    from compat_masters import tan_out as _to
    for _ in range(6):
        for i in joints:
            j = (i + 1) % n
            if (lambda a, b: a is None or b is None or a*b <= 0)(kap(S[i], 1.0), kap(S[j], 0.0)): continue
            best = None; ci, cj = S[i], S[j]
            P = ci[4]; tdir = _to(ci)                                   # nút trượt DỌC tiếp tuyến của nó (tiếp tuyến giữ)
            la0, lb0 = math.dist(S0[i][3], S0[i][4]), math.dist(S0[j][1], S0[j][2])
            for sh in (-12, -8, -4, 0, 4, 8, 12):
                Pn = (P[0] + tdir[0]*sh, P[1] + tdir[1]*sh)
                for fa in FACT:
                    A = list(ci); A[4] = Pn; A[3] = (Pn[0] - tdir[0]*la0*fa, Pn[1] - tdir[1]*la0*fa)
                    if dev(S0[i], A) > MAXDEV or (flips(A) and not flips(S0[i])): continue
                    for fb in FACT:
                        B = list(cj); B[1] = Pn; B[2] = (Pn[0] + tdir[0]*lb0*fb, Pn[1] + tdir[1]*lb0*fb)
                        if (flips(B) and not flips(S0[j])): continue
                        # lệch hình: so với cả hai đoạn gốc (nút dời → so hợp hai đoạn)
                        if max(dev2(A, S0[i], S0[j]), dev2(B, S0[i], S0[j])) > MAXDEV: continue
                        S[i], S[j] = A, B
                        c = jcost(i) + jcost((i - 1) % n) + jcost(j) + 0.02*(abs(math.log(fa)) + abs(math.log(fb))) + 0.002*abs(sh)
                        if best is None or c < best[0]: best = (c, A, B)
            S[i], S[j] = (best[1], best[2]) if best else (ci, cj)
    return S

def run(d):
    from interp import contours
    from compat import to_d
    return to_d([fair(S) for S in contours([d])])

if __name__ == '__main__':
    from interp import contours
    for f, k in (('designer_A.json', 'S-Regular'), ('designer_B.json', 'S-Bold')):
        p = os.path.join(HERE, f); keep = os.path.join(HERE, f.replace('.json', '_preS34.json'))
        if not os.path.exists(keep): shutil.copy(p, keep)
        src = json.load(open(keep)); D = json.load(open(p))
        D[k] = [run(src[k][0])]; print(k, 'liền độ cong (≤ %.1f u)' % MAXDEV)
        json.dump(D, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
