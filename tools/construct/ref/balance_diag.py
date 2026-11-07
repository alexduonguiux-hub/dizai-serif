#!/usr/bin/env python3
"""S21 Cân nét chéo chữ hoa Bold (designer 07/11: "N hơi nặng … kiểm tra lại các độ dày của các chữ bold khác … một số dày, một
số mỏng không đồng đều") → designer_B.json.
    python3 tools/construct/ref/balance_diag.py      (đi từ bản lưu designer_B_prediag.json → chạy lại cho cùng kết quả)

Đo (mép thẳng song song, khoảng cách vuông góc): nét chéo DÀY "\\" chữ hoa Regular đều 0.97–1.00 × thân (R chân 0.89); Bold
lệch ±10% (N 152, Y 151, A K M W 146, R 141, X 137, V 129 u — thân 140). Chữ thường Bold đều (124–125 = 0.99 × n), không đổi.
Luật:
  · nét chéo DÀY Bold = nét Regular × (thân Bold / thân Regular) = × 140/102 — giữ đúng tương quan giữa các chữ của bản vẽ Regular;
  · nét chéo MẢNH Bold = 70 u (0.5 thân = nét ngang Bold).
Cách làm: dời song song HAI mép của nét, mỗi mép ½ lượng chênh (trục nét đứng yên); đầu mép trượt theo cạnh kề (giao với đường
thẳng của cạnh kề, hoặc tiếp tuyến đầu đoạn cong kề) → loe, khấc, đỉnh giữ dạng.
"""
import json, math, os, re, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
CAPS = 'AKMRVWXY'               # N riêng: fix_N (hai khấc V cố định hai điểm → xoay nét chéo)
VR, VB, THIN = 102.0, 140.0, 70.0


def parse(d):
    toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', d); i = 0; cs = []; cur = None
    while i < len(toks):
        c = toks[i]; i += 1; n = {'M': 1, 'L': 1, 'C': 3, 'Z': 0}[c]
        pts = [(float(toks[i + 2*j]), float(toks[i + 2*j + 1])) for j in range(n)]; i += 2*n
        if c == 'M': cs.append([]); cur = pts[0]; start = cur
        elif c == 'L':
            if math.dist(cur, pts[0]) > 1.0: cs[-1].append(["L", cur, pts[0]]); cur = pts[0]   # bỏ đoạn ngắn < 1 u (điểm trùng)
            elif cs[-1]: cs[-1][-1][-1] = pts[0]; cur = pts[0]
            else: cur = pts[0]
        elif c == 'C': cs[-1].append(['C', cur] + pts); cur = pts[2]
        elif c == 'Z':
            if math.dist(cur, start) > 1e-6: cs[-1].append(['L', cur, start])
    return cs


def unparse(cs):
    out = []
    for c in cs:
        out.append('M%.1f %.1f' % c[0][1])
        for s in c: out.append('L%.1f %.1f' % s[2] if s[0] == 'L' else 'C%.1f %.1f %.1f %.1f %.1f %.1f' % (*s[2], *s[3], *s[4]))
        out.append('Z')
    return re.sub(r'\.0(?=[ MLCZ]|$)', '', ''.join(out))


def unit(v):
    L = math.hypot(*v); return (v[0]/L, v[1]/L)


def isect(p, u, q, v):
    den = u[0]*v[1] - u[1]*v[0]
    if abs(den) < 1e-9: return None
    t = ((q[0] - p[0])*v[1] - (q[1] - p[1])*v[0])/den; return (p[0] + t*u[0], p[1] + t*u[1])


def pairs(cs, minlen=40, ink=None):
    """các NÉT chéo = cặp ĐƯỜNG MÉP song song cách nhau 20–180 u. Một đường mép có thể gồm nhiều đoạn thẳng hàng (mép bị thanh
    ngang / chỗ giao cắt chia đôi) → gom theo đường, dời cả nhóm"""
    segs = [(ci, si) for ci, c in enumerate(cs) for si, s in enumerate(c) if s[0] == 'L' and math.dist(s[1], s[2]) >= minlen]
    lines = []                                                     # [u, điểm gốc, [đoạn]]
    for k in segs:
        s = cs[k[0]][k[1]]; u = unit((s[2][0] - s[1][0], s[2][1] - s[1][1]))
        ang = math.degrees(math.atan2(u[1], u[0])) % 180
        if ang < 5 or ang > 175 or 85 <= ang <= 95: continue
        for Ln in lines:
            v, o, ks = Ln
            if abs(u[0]*v[1] - u[1]*v[0]) < math.sin(math.radians(1)) and abs((s[1][0] - o[0])*v[1] - (s[1][1] - o[1])*v[0]) < 1.5:
                ks.append(k); break
        else: lines.append([u, s[1], [k]])
    lines = [Ln for Ln in lines if sum(math.dist(cs[c][i][1], cs[c][i][2]) for c, i in Ln[2]) >= 120]
    out = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            (u, o, ka), (v, q, kb) = lines[i], lines[j]
            if abs(u[0]*v[1] - u[1]*v[0]) > math.sin(math.radians(3)): continue
            dist = abs((q[0] - o[0])*u[1] - (q[1] - o[1])*u[0])
            if not 20 < dist < 180: continue
            P = lambda k: [((p[0] - o[0])*u[0] + (p[1] - o[1])*u[1]) for p in cs[k[0]][k[1]][1:]]
            ra = [x for k in ka for x in P(k)]; rb = [x for k in kb for x in P(k)]
            lo_, hi_ = max(min(ra), min(rb)), min(max(ra), max(rb))
            if hi_ - lo_ < 60: continue                                    # phải chồng hình chiếu đủ dài
            if ink is not None:                                            # giữa hai mép phải là MỰC (không phải khe trắng)
                tm = (lo_ + hi_)/2; pa = (o[0] + tm*u[0], o[1] + tm*u[1])
                nrm = (-u[1], u[0]); sd = (q[0] - o[0])*nrm[0] + (q[1] - o[1])*nrm[1]
                mid = (pa[0] + nrm[0]*sd/2, pa[1] + nrm[1]*sd/2)
                if not ink.contains(mid): continue
            out.append((dist, i, j))
    out.sort(); used = set(); res = []
    for dist, i, j in out:
        if i in used or j in used: continue
        used |= {i, j}; res.append((dist, lines[i][2], lines[j][2]))
    return res


YLINES = (-11.3, 0.0, 700.0, 711.3)


def move_edge(cs, ci, si, delta, towards):
    """dời mép (ci, si) song song delta về phía 'towards'. Hai đầu, mỗi đầu đi dọc chuỗi kề:
      · đoạn thẳng thẳng hàng (< 5°) → dời theo cùng mép (cả đoạn), đi tiếp;
      · đoạn cong nối trơn (tiếp tuyến lệch < 8°: loe) → dời điểm nối + tay nắm kề (loe giữ nối mượt);
      · còn lại: đầu mép = giao đường đã dời với cạnh kề (đường thẳng / tiếp tuyến cong); đầu nằm trên đường chân / đỉnh
        (khấc, mặt cắt chân) → trượt NGANG trên đường đó; giao vọt xa (gần song song) → chỉ tịnh tiến."""
    c = cs[ci]; n = len(c); s = c[si]
    u = unit((s[2][0] - s[1][0], s[2][1] - s[1][1])); nv = (-u[1], u[0])
    sg = 1 if (towards[0] - s[1][0])*nv[0] + (towards[1] - s[1][1])*nv[1] > 0 else -1
    off = (nv[0]*delta*sg, nv[1]*delta*sg); p0 = (s[1][0] + off[0], s[1][1] + off[1])
    T = lambda p: (p[0] + off[0], p[1] + off[1])
    lim = 3*abs(delta) + 10
    def ang(v1, v2): return math.degrees(math.acos(max(-1.0, min(1.0, abs(v1[0]*v2[0] + v1[1]*v2[1])))))
    s[1], s[2] = T(s[1]), T(s[2])
    for step in (1, -1):                                           # 1: phía sau (đầu cuối), -1: phía trước (đầu đầu)
        k = si
        while True:
            k = (k + step) % n; X = c[k]
            if k == si: break
            if X[0] == 'L':
                vx = unit((X[2][0] - X[1][0], X[2][1] - X[1][1])) if math.dist(X[1], X[2]) > 1e-9 else u
                if ang(vx, u) < 5:                                 # thẳng hàng → dời cả đoạn, đi tiếp
                    X[1], X[2] = T(X[1]), T(X[2]); continue
            jp = X[1] if step == 1 else X[-1]                      # điểm nối (đã dời ở bên mép: phải đặt lại)
            orig = (jp[0] - 0, jp[1] - 0)
            if X[0] == 'C':
                h = X[2] if step == 1 else X[3]
                if math.dist(h, jp) < 1e-9: h = X[3] if step == 1 else X[2]
                tv = unit((h[0] - jp[0], h[1] - jp[1]))
                if ang(tv, u) < 8:                                 # loe nối trơn → dời điểm nối + tay nắm kề
                    if step == 1: X[1], X[2] = T(X[1]), T(X[2])
                    else: X[4], X[3] = T(X[4]), T(X[3])
                    newp = X[1] if step == 1 else X[4]
                    self_end = 2 if step == 1 else 1
                    prevk = (k - step) % n; c[prevk][-1 if step == 1 else 1] = newp
                    break
                q, v = jp, tv
            else:
                q, v = jp, unit((X[2][0] - X[1][0], X[2][1] - X[1][1]))
            if any(abs(jp[1] - Y) < 0.6 for Y in YLINES): q, v = jp, (1.0, 0.0)     # trên đường chân / đỉnh → trượt ngang
            P = isect(p0, u, q, v)
            if P is None or math.dist(P, jp) > lim: P = T(jp)
            d_ = (P[0] - jp[0], P[1] - jp[1])
            if step == 1:
                X[1] = P
                if X[0] == 'C': X[2] = (X[2][0] + d_[0], X[2][1] + d_[1])
            else:
                X[-1] = P
                if X[0] == 'C': X[3] = (X[3][0] + d_[0], X[3][1] + d_[1])
            prevk = (k - step) % n; c[prevk][-1 if step == 1 else 1] = P
            break


def fix_flats(csR, csB):
    """mặt đáy đỉnh nhọn (đoạn ngang ngắn < 40 u trên đường chân): Bold ≥ Regular × VB/VR (W Bold 12.5 < Regular 20 —
    đỉnh nhọn mảnh hơn Regular). Nới đều hai bên quanh tâm; đầu cạnh chéo kề trượt theo đường chân."""
    def flats(cs):
        return [(ci, si) for ci, c in enumerate(cs) for si, s in enumerate(c) if s[0] == 'L' and abs(s[1][1] - s[2][1]) < 0.5
                and min(s[1][1], s[2][1]) < 5 and math.dist(s[1], s[2]) < 40]
    fr, fb = flats(csR), flats(csB)
    if len(fr) != len(fb): return []
    log = []
    key = lambda cs, k: (cs[k[0]][k[1]][1][0] + cs[k[0]][k[1]][2][0])/2
    for kr, kb in zip(sorted(fr, key=lambda k: key(csR, k)), sorted(fb, key=lambda k: key(csB, k))):
        lr = math.dist(*csR[kr[0]][kr[1]][1:]); s = csB[kb[0]][kb[1]]; lb = math.dist(s[1], s[2]); tgt = lr*VB/VR
        if lb >= tgt - 0.5: continue
        u = unit((s[2][0] - s[1][0], s[2][1] - s[1][1])); e = (tgt - lb)/2
        a = (s[1][0] - e*u[0], s[1][1]); b = (s[2][0] + e*u[0], s[2][1])
        c = csB[kb[0]]; n = len(c); prv, nxt = c[(kb[1] - 1) % n], c[(kb[1] + 1) % n]
        prv[-1] = a; nxt[1] = b; s[1], s[2] = a, b
        log.append(f'mặt đỉnh {lb:.1f}→{tgt:.1f}')
    return log


def fix_N(d, tgt):
    """N Bold: chân khấc dưới P1 và chân khấc trên P2 cố định (khấc 14 u như Regular) → nét chéo = hai đường song song qua P1, P2;
    chọn HƯỚNG sao cho khoảng cách = tgt (|P1P2|·sin δ = tgt), cùng phía lệch như hiện tại — nét chéo chỉ xoay ~1°"""
    P1, P2, xs_l, xs_r = (453.5, -11.3), (102.0, 711.3), 96.4, 459.1
    vx, vy = P2[0] - P1[0], P2[1] - P1[1]; Lv = math.hypot(vx, vy); a0 = math.atan2(vy, vx)
    cur = re.search(r'L459\.1 -11\.3L459\.1 2\.7L453\.5 -11\.3L([\d.\-]+) ([\d.\-]+)', d)
    a_cur = math.atan2(float(cur.group(2)) - P1[1], float(cur.group(1)) - P1[0])
    dl = math.asin(tgt/Lv); a = a0 + dl if a_cur > a0 else a0 - dl
    u = (math.cos(a), math.sin(a))
    Lo = (xs_l, P1[1] + (xs_l - P1[0])/u[0]*u[1]); Up = (xs_r, P2[1] + (xs_r - P2[0])/u[0]*u[1])
    d = re.sub(r'L102 711\.3L459\.1 [\d.\-]+L459\.1 630\.2', 'L102 711.3L459.1 %.1fL459.1 630.2' % Up[1], d)
    d = re.sub(r'L453\.5 -11\.3L96\.4 [\d.\-]+L96\.4 69\.8', 'L453.5 -11.3L96.4 %.1fL96.4 69.8' % Lo[1], d)
    return d


if __name__ == '__main__':
    p = os.path.join(HERE, 'designer_B.json'); keep = os.path.join(HERE, 'designer_B_prediag.json')
    if not os.path.exists(keep): shutil.copy(p, keep)
    Bsrc = json.load(open(keep)); A = json.load(open(os.path.join(HERE, 'designer_A.json'))); Bout = json.load(open(p))
    for ch in CAPS:
        csR = parse(A[f'{ch}-Regular'][0]); csB = parse(Bsrc[f'{ch}-Bold'][0])
        import pathops
        sys_path = os.path.join(HERE); import sys as _s; _s.path.insert(0, HERE)
        from make_ref import outline
        thickR = max((d for d, *_ in pairs(csR, ink=outline(A[f'{ch}-Regular'])) if d > 0.7*VR), default=None)
        log = []
        for it in range(6):                                            # lặp: nét chung đỉnh kéo nhau → đo lại, cân lại
          for dist, x, y in pairs(csB, ink=outline([unparse(csB)])):
              if dist > 0.75*VB and thickR: tgt = thickR*VB/VR                     # nét dày
              elif dist < 0.75*VB: tgt = THIN                                      # nét mảnh
              else: continue
              dl = (dist - tgt)/2
              if abs(dl) < 1.0: continue
              ex, ey = csB[x[0][0]][x[0][1]], csB[y[0][0]][y[0][1]]
              cx = ((ex[1][0] + ex[2][0])/2, (ex[1][1] + ex[2][1])/2); cy = ((ey[1][0] + ey[2][0])/2, (ey[1][1] + ey[2][1])/2)
              for k in x: move_edge(csB, *k, dl, cy)
              for k in y: move_edge(csB, *k, dl, cx)
              log.append(f'{dist:.0f}→{tgt:.0f}')
        log += fix_flats(parse(A[f'{ch}-Regular'][0]), csB)
        Bout[f'{ch}-Bold'] = [unparse(csB)]
        print(ch, ' '.join(log))
    csR = parse(A['N-Regular'][0]); thickR = max(d for d, *_ in pairs(csR, ink=outline(A['N-Regular'])) if d > 0.7*VR)
    Bout['N-Bold'] = [fix_N(Bsrc['N-Bold'][0], thickR*VB/VR)]; print('N', f'xoay nét chéo → {thickR*VB/VR:.0f}')
    json.dump(Bout, open(p, 'w'), separators=(',', ':'))
