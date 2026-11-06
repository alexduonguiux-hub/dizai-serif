#!/usr/bin/env python3
"""S Regular + S Bold vẽ lại bởi designer trên Figma (06/11, file gGrYT5oldAplC9IedaAj7b, trang "Design v0.2 — cân bằng (Claude)"):
  Bold    node 2145:1225 "Union" trong Frame 2 2145:1227  → designer_B.json['S-Bold']
  Regular node 2145:1235 "Union" trong Frame 2 2145:1228  → designer_A.json['S-Regular']
    python3 tools/construct/ref/figma_S.py      (chạy lại bao nhiêu lần cũng cho cùng kết quả)

Bối cảnh: designer 06/11 "Các đường cong của chữ s và S. Cảm giác không smooth lắm" → thử luật G2 (S17, font/fair.py) →
"bây giờ bụng nó lại không cong tròn tự nhiên" → designer tự chỉnh vector ("Đọc vector mẫu ở đây", "mình vừa chỉnh lại nét").
Bản vẽ của designer là chuẩn; S17 tắt (compat_masters.FAIR rỗng).

Quy đổi toạ độ Figma (y xuống) → đơn vị font: giải từ bốn góc đầu nét không đổi so với bản cũ — Bold (19.8, 27.4) (19.8, 186.4)
(410.9, 689.6) (410.9, 533.5), Regular (11.3, 27.4) (11.3, 146.7) (354.3, 689.6) (354.3, 570.3); hai khung cùng một phép:
x = 2.8341·X − 0.04, y = 711.34 − 2.8341·Y (sai < 0.1 u).
"""
import json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
FIGMA_B = ("M 46.5 55.130859375 C 46.5 88.5 88.1943244934082 100.38976097106934 113.5 115 C 144.6701488494873 132.99609375 159 152 "
         "159 187.869140625 C 159 223.73828125 126 256 81.5 256 C 46.000099182128906 256 7 241.3291015625 7 241.3291015625 L 7 "
         "185.236328125 C 19 207.67412757873535 57 231 76 231 C 94.99999618530273 231 110.2076153755188 222.85941886901855 116 201.5 "
         "C 124 172 98.4247055053711 160.13159370422363 51.4248046875 132.99609375 C 4.424945831298828 105.8606014251709 0 81 0 "
         "57.130859375 C 0 19.5 41.00011444091797 0 76.5 0 C 111.99789810180664 0 144.9962746060919 7.670032492955215 145 "
         "7.6708984375 L 145 62.763671875 C 132.9999876022339 40.325883865356445 94.9999942779541 24.4228515625 76 24.4228515625 "
         "C 57.00001335144043 24.4228515625 46.5000149638945 35.49998664855957 46.5 55.130859375 Z")
FIGMA_R = ("M 34 57.130859375 C 34 82.49994850158691 56.831180572509766 92.09647941589355 96.59765625 115.0556640625 C 130.2762336730957 "
           "134.5 139 157.50004196166992 139 190.869140625 C 138.9999662937007 229.50000762939453 106.99988174438477 256 71.5 256 C "
           "36.01076889038086 256 4.019225679337978 241.33791437745094 4 241.3291015625 L 4 199.236328125 C 16.00002098083496 "
           "221.6741123199463 45.0000114440918 242.5771484375 64 242.5771484375 C 89 242.5771484375 104.99998198754838 224.50000190734863 "
           "105 192.869140625 C 105 164.10515785217285 86.5 150.6720790863037 45.40234375 126.9443359375 C 4.3046875 103.21659278869629 0 "
           "78.49995994567871 0 55.130859375 C 0 24.449277877807617 31.00011444091797 0 66.5 0 C 101.99710083007812 0 "
           "124.99637185689062 7.669688467634842 125 7.6708984375 L 125 49.763671875 C 112.9999942779541 27.325883865356445 "
           "88.9999942779541 13.4228515625 70 13.4228515625 C 48 13.422851562499545 34.00021331041353 29.805185317993164 34 "
           "57.130859375 Z")
S, X0, Y0 = 2.8341, -0.04, 711.34


def convert(d):
    toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', d); out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t in 'MLCZ': out.append(t); i += 1; continue
        x, y = float(toks[i]), float(toks[i + 1]); i += 2
        out.append('%g %g' % (round(S*x + X0, 1) + 0.0, round(Y0 - S*y, 1) + 0.0))
    return re.sub(r' ?([MLCZ]) ?', r'\1', ' '.join(out))


# S19 bù đậm S Bold (designer 06/11: "sống S Bold mỏng: đo lại cân bằng weight với các ký tự cùng weight") — đo qa_stroke:
# T(S Bold) = 0.96 × nét đứng chuẩn, nhóm hoa cong C G O D B R = 1.04–1.06 (Regular: S 1.04, cân). Vector designer giữ DÁNG;
# làm đậm đều bằng offset song song Tiller–Hanson (dời từng cạnh đa giác điều khiển ra ngoài δ, giao lại — không thêm điểm neo
# → Medium / SemiBold vẫn nội suy); mặt cắt đầu nét giữ nguyên đường, góc = giao đường cong đã dời với mặt cắt; rồi co dọc về
# đúng cao cũ (−14.2 … 711.3); bề ngang tăng 2δ (bụng dày ra hai phía).
DELTA_B = float(os.environ.get('S19_DELTA', '6'))   # δ = 6 u → T(S Bold) = 146.7 = 1.048 × chuẩn (C G O D: 1.04–1.06)


def _segs(d):
    toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', d); i = 0; segs = []; cur = None
    while i < len(toks):
        c = toks[i]; i += 1
        n = {'M': 1, 'L': 1, 'C': 3, 'Z': 0}[c]; pts = [(float(toks[i + 2*j]), float(toks[i + 2*j + 1])) for j in range(n)]; i += 2*n
        if c == 'M': cur = pts[0]; start = cur
        elif c == 'L': segs.append(['L', cur, pts[0]]); cur = pts[0]
        elif c == 'C': segs.append(['C', cur] + pts); cur = pts[2]
    if cur != start: segs.append(['L', cur, start])
    return segs


def _unit(v):
    L = math.hypot(*v); return (v[0]/L, v[1]/L) if L > 1e-9 else None


def _isect(p, u, q, v):
    """giao của đường p + s·u và q + t·v (None nếu gần song song)"""
    den = u[0]*v[1] - u[1]*v[0]
    if abs(den) < 1e-6: return None
    s_ = ((q[0] - p[0])*v[1] - (q[1] - p[1])*v[0])/den
    return (p[0] + s_*u[0], p[1] + s_*u[1])


def offset(d, delta):
    """dời đường viền kín ra ngoài delta (Tiller–Hanson cho cubic, giao tiếp tuyến ở góc)"""
    S_ = _segs(d); n = len(S_)
    area = sum((s[1][0]*s[-1][1] - s[-1][0]*s[1][1]) for s in S_)/2
    nrm = lambda u: (u[1], -u[0]) if area > 0 else (-u[1], u[0])   # CCW (diện tích dương): pháp tuyến ngoài = bên phải hướng đi
    def ctrl(s):                                      # các cạnh đa giác điều khiển khác 0
        P = s[1:]; E = []
        for a_, b_ in zip(P, P[1:]):
            u = _unit((b_[0] - a_[0], b_[1] - a_[1]))
            if u: E.append((a_, u))
        return P, E
    def off_line(p, u): nv = nrm(u); return (p[0] + delta*nv[0], p[1] + delta*nv[1]), u
    out = []
    for s in S_:
        P, E = ctrl(s); L = [off_line(p, u) for p, u in E]
        if s[0] == 'L':                               # mặt cắt đầu nét: GIỮ nguyên đường (chỉ đường cong được làm đậm)
            out.append(['L', P[0], P[1]]); continue
        if len(L) == 1:
            q0 = L[0][0]; q1 = (q0[0] + P[-1][0] - P[0][0], q0[1] + P[-1][1] - P[0][1])
            out.append(['L' if s[0] == 'L' else 'C', q0, q1] if s[0] == 'L' else ['C', q0, q0, q1, q1]); continue
        # điểm điều khiển trong: giao các cạnh dời liên tiếp; tay nắm 0 giữ trùng điểm đầu / cuối
        a0 = L[0][0]; a3 = (P[3][0] + delta*nrm(E[-1][1])[0], P[3][1] + delta*nrm(E[-1][1])[1])
        z0 = math.dist(P[0], P[1]) < 1e-6; z3 = math.dist(P[2], P[3]) < 1e-6
        if len(L) == 3:
            c1 = _isect(*L[0], *L[1]) or (P[1][0] + delta*nrm(E[0][1])[0], P[1][1] + delta*nrm(E[0][1])[1])
            c2 = _isect(*L[1], *L[2]) or (P[2][0] + delta*nrm(E[2][1])[0], P[2][1] + delta*nrm(E[2][1])[1])
        else:                                         # một tay nắm bằng 0: hai cạnh
            m = _isect(*L[0], *L[1]) or a0
            c1, c2 = (a0, m) if z0 else (m, a3)
        out.append(['C', a0, c1, c2, a3])
    # nút: giao tiếp tuyến dời của hai đoạn kề (góc) — nút trơn hai giá trị trùng nhau
    for i in range(n):
        j = (i + 1) % n; A, B_ = out[i], out[j]
        ua = _unit((A[-1][0] - A[-2][0], A[-1][1] - A[-2][1])) or _unit((A[-1][0] - A[1][0], A[-1][1] - A[1][1]))
        ub = _unit((B_[2][0] - B_[1][0], B_[2][1] - B_[1][1])) or _unit((B_[-1][0] - B_[1][0], B_[-1][1] - B_[1][1]))
        if ua and ub and abs(ua[0]*ub[1] - ua[1]*ub[0]) > 0.02:
            x = _isect(A[-1], ua, B_[1], ub)
            if x:
                shift_a = (x[0] - A[-1][0], x[1] - A[-1][1]); shift_b = (x[0] - B_[1][0], x[1] - B_[1][1])
                if A[0] == 'C' and math.dist(A[-2], A[-1]) < 1e-6: A[-2] = x
                if B_[0] == 'C' and math.dist(B_[1], B_[2]) < 1e-6: B_[2] = x
                A[-1] = x; B_[1] = x
        else:
            mpt = ((A[-1][0] + B_[1][0])/2, (A[-1][1] + B_[1][1])/2); A[-1] = mpt; B_[1] = mpt
    return out


def to_d(segs):
    o = ['M%.1f %.1f' % segs[0][1]]
    for s in segs: o.append('L%.1f %.1f' % s[2] if s[0] == 'L' else 'C%.1f %.1f %.1f %.1f %.1f %.1f' % (*s[2], *s[3], *s[4]))
    return ''.join(o) + 'Z'


def embolden(d, delta):
    if delta <= 0: return d
    segs = offset(d, delta)
    def bb(S_): xs = [p[0] for s in S_ for p in s[1:]]; ys = [p[1] for s in S_ for p in s[1:]]; return min(xs), min(ys), max(xs), max(ys)
    x0, y0, x1, y1 = bb(_segs(d)); X0_, Y0_, X1_, Y1_ = bb(segs)
    sy = (y1 - y0)/(Y1_ - Y0_); sx = 1.0     # cao giữ nguyên; ngang KHÔNG co (co ngang làm đầu cắt lệch so với bụng) → rộng thêm 2δ
    f = lambda p: (x0 + (p[0] - X0_)*sx, y0 + (p[1] - Y0_)*sy)
    return to_d([[s[0]] + [f(p) for p in s[1:]] for s in segs])


if __name__ == '__main__':
    for f, k, src, dl in (('designer_B.json', 'S-Bold', FIGMA_B, DELTA_B), ('designer_A.json', 'S-Regular', FIGMA_R, 0)):
        p = os.path.join(HERE, f); J = json.load(open(p))
        old = J[k][0]; J[k] = [embolden(convert(src), dl)]
        json.dump(J, open(p, 'w'), separators=(',', ':'))
        print(k, 'cũ :', old[:110]); print(k, 'mới:', J[k][0][:110])
