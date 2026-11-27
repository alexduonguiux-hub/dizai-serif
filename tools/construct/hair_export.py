#!/usr/bin/env python3
"""Trục HAIR — nét mảnh (designer 26/11 "thêm thanh slide variable điều khiển nét mỏng của tất cả các glyph").
Master nét mảnh = CÙNG hệ luật Golden chạy với chuẩn nét mảnh nhỏ hơn (golden.py DIZAI_HAIR=16 → out/golden_hair, compat_masters,
post_compat). Glyph nào lệch cấu trúc điểm so với master mặc định thì giữ outline mặc định (không đổi theo trục).
Xuất: fonts/golden/variable/AnNamGolden[HAIR,wght].ttf (+ Italic) — trục Weight 400–700 × Hairline 16–34 (mặc định 34).
    (chạy sau export_font.py, cùng biến môi trường DIZAI_* của golden/run.sh; DIZAI_HAIR_OUT = thư mục outline nét mảnh)"""
import os, sys, json, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import export_font as EF
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor

HAIR_MIN, HAIR_DEF = float(os.environ.get('DIZAI_HAIR', 16)), 34.0
HOUT = os.environ.get('DIZAI_HAIR_OUT') or os.path.join(EF.ROOT, 'out', 'golden_hair')

def sig(d): return [[s[0] for s in c] for c in EF.parse(d)]

def align(dh, dd):
    """khớp cấu trúc outline nét mảnh với outline mặc định (cùng chữ, cùng weight): theo từng contour, so dãy đoạn (DP) — được BỎ một đoạn
    thẳng của bản nét mảnh (giá = độ dài, chỉ đoạn ngắn / thẳng hàng) hoặc CHÈN đoạn thẳng dài 0 (giá 6). Trả về None nếu không khớp được."""
    import math
    H, Dd = EF.parse(dh), EF.parse(dd)
    if len(H) != len(Dd): return None
    out = []
    for hc, dc in zip(H, Dd):
        hs = [s for s in hc if s[0] in 'LC']; ds = [s for s in dc if s[0] in 'LC']
        M0 = hc[0][1]; st = [M0] + [s[-1] for s in hs[:-1]]
        n, m = len(hs), len(ds); INF = 1e18
        C = [[INF]*(m + 1) for _ in range(n + 1)]; B = [[None]*(m + 1) for _ in range(n + 1)]; C[0][0] = 0
        for i in range(n + 1):
            for j in range(m + 1):
                if C[i][j] >= INF: continue
                if i < n and j < m and hs[i][0] == ds[j][0] and C[i][j] < C[i + 1][j + 1]: C[i + 1][j + 1] = C[i][j]; B[i + 1][j + 1] = 'm'
                if i < n and j < m and hs[i][0] == 'L' and ds[j][0] == 'C' and C[i][j] + 3 < C[i + 1][j + 1]:   # thẳng → cung suy biến (ff)
                    C[i + 1][j + 1] = C[i][j] + 3; B[i + 1][j + 1] = 'c'
                if i < n and hs[i][0] == 'L':
                    L_ = math.dist(st[i], hs[i][-1])
                    if L_ < 15 or True:
                        c_ = C[i][j] + (L_ if L_ < 15 else 30 + L_*0.01)
                        if c_ < C[i + 1][j]: C[i + 1][j] = c_; B[i + 1][j] = 'd'
                if j < m and ds[j][0] == 'L' and C[i][j] + 6 < C[i][j + 1]: C[i][j + 1] = C[i][j] + 6; B[i][j + 1] = 'i'
        if C[n][m] >= INF: return None
        ops = []; i, j = n, m
        while i or j:
            o = B[i][j]; ops.append(o)
            if o in 'mc': i -= 1; j -= 1
            elif o == 'd': i -= 1
            else: j -= 1
        ops.reverse()
        new = [hc[0]]; i = 0; cur = M0
        for o in ops:
            if o == 'm': new.append(hs[i]); cur = hs[i][-1]; i += 1
            elif o == 'c':
                e = hs[i][-1]; a_ = cur
                new.append(('C', [a_[0] + (e[0] - a_[0])/3, a_[1] + (e[1] - a_[1])/3], [a_[0] + 2*(e[0] - a_[0])/3, a_[1] + 2*(e[1] - a_[1])/3], list(e)))
                cur = e; i += 1
            elif o == 'd':
                if i == len(hs) - 1: new[0] = ('M', list(hs[i][-1])) if False else new[0]
                i += 1
            else: new.append(('L', list(cur)))
        new.append(('Z',))
        out.append(new)
    s_ = ''
    for c in out:
        for seg in c:
            if seg[0] == 'Z': s_ += 'Z'
            elif seg[0] == 'M': s_ += 'M%.2f %.2f' % tuple(seg[1])
            else: s_ += seg[0] + ' '.join('%.2f %.2f' % tuple(p) for p in seg[1:])
    return s_ if sig(s_) == sig(dd) else None
BARRED = {'đ': 'd', 'Đ': 'D'}
def bar_morph(dc, db, hb, r):
    """chữ có gạch (đ Đ) lệch cấu trúc: từ outline MẶC ĐỊNH — điểm trùng điểm chữ gốc mặc định dời như chữ gốc nét mảnh (cùng cấu trúc),
    điểm còn lại (gạch) ép theo tỉ lệ r quanh trục giữa gạch"""
    C, B0, B1 = EF.parse(dc), EF.parse(db), EF.parse(hb)
    if sig(db) != sig(hb): return None
    mv = {}
    for c0, c1 in zip(B0, B1):
        for s0, s1 in zip(c0, c1):
            for p0, p1 in zip(s0[1:], s1[1:]): mv[(round(p0[0], 1), round(p0[1], 1))] = (p1[0] - p0[0], p1[1] - p0[1])
    other = [p[1] for c in C for s in c for p in s[1:] if (round(p[0], 1), round(p[1], 1)) not in mv]
    if not other: return None
    ys = sorted(other); ym = (ys[0] + ys[-1])/2
    def f(p):
        k = (round(p[0], 1), round(p[1], 1))
        if k in mv: return (p[0] + mv[k][0], p[1] + mv[k][1])
        return (p[0], ym + (p[1] - ym)*r)
    s_ = ''
    for c in C:
        for seg in c:
            if seg[0] == 'M': s_ += 'M%.2f %.2f' % f(seg[1])
            else: s_ += seg[0] + ' '.join('%.2f %.2f' % f(p) for p in seg[1:])
        s_ += 'Z'
    return s_
def reconcile(gh, gb):
    """điểm UFO bản nét mảnh lệch bản mặc định (bước xuất bỏ nút thẳng hàng / đoạn suy biến / đổi điểm đầu khác nhau ở hai bản):
    theo từng contour — thử mọi điểm đầu (xoay vòng), DP khớp dãy kiểu điểm: được BỎ điểm 'line' của bản nét mảnh (giá = độ lệch
    khỏi đường nối hai điểm kề) hoặc CHÈN điểm 'line' trùng điểm trước (giá 4). Trả về danh sách contour điểm mới hoặc None."""
    import math
    if len(gh.contours) != len(gb.contours): return None
    out = []
    for ch, cb in zip(gh.contours, gb.contours):
        H = [((p.x, p.y), p.type) for p in ch.points]; B = [p.type for p in cb.points]
        best = None
        for r in range(len(H)):
            R = H[r:] + H[:r]; n, m = len(R), len(B); INF = 1e18
            C = [[INF]*(m + 1) for _ in range(n + 1)]; P = [[None]*(m + 1) for _ in range(n + 1)]; C[0][0] = 0
            for i in range(n + 1):
                for j in range(m + 1):
                    c0 = C[i][j]
                    if c0 >= INF: continue
                    if i < n and j < m and R[i][1] == B[j] and c0 < C[i + 1][j + 1]: C[i + 1][j + 1] = c0; P[i + 1][j + 1] = 'm'
                    if i < n and R[i][1] == 'line':
                        a, b, e = R[i - 1][0], R[i][0], R[(i + 1) % n][0]
                        ux, uy = e[0] - a[0], e[1] - a[1]; L = math.hypot(ux, uy) or 1
                        dev = abs((b[0] - a[0])*uy - (b[1] - a[1])*ux)/L + 0.01*math.dist(a, b)
                        if c0 + dev < C[i + 1][j]: C[i + 1][j] = c0 + dev; P[i + 1][j] = 'd'
                    if j < m and B[j] == 'line' and c0 + 4 < C[i][j + 1]: C[i][j + 1] = c0 + 4; P[i][j + 1] = 'i'
            if C[n][m] < INF and (best is None or C[n][m] < best[0]): best = (C[n][m], R, P, n, m)
        if best is None or best[0] > 12: return None
        _, R, P, i, j = best; ops = []
        while i or j:
            o = P[i][j]; ops.append(o)
            if o == 'm': i -= 1; j -= 1
            elif o == 'd': i -= 1
            else: j -= 1
        ops.reverse(); pts = []; i = 0
        for o in ops:
            if o == 'm': pts.append(R[i]); i += 1
            elif o == 'd': i += 1
            else: pts.append(((pts[-1][0] if pts else R[i][0]), 'line'))
        out.append(pts)
    return out
def gsig(g): return [[(p.type or 'o') for p in c.points] for c in g.contours]

def main():
    H = json.load(open(os.path.join(HOUT, 'outlines.json')))
    VF = os.path.join(EF.FONTS, 'variable'); os.makedirs(VF, exist_ok=True)
    EF.YMAX, EF.YMIN = EF._ybounds()
    for ang, tag in ((0, ''), (EF.ITALIC_ANGLE, '-Italic')):
        EF.use('Italic' if tag else 'Roman'); D0 = EF.O
        M = dict(D0); keep = set(); nal = 0
        for c in EF.CHARS:
            ks = [f'{c}-{w}' for w in ('Regular', 'Bold')]
            if all(k in D0 and k in H for k in ks) and any(sig(D0[k]) != sig(H[k]) for k in ks):
                al = {k: (H[k] if sig(D0[k]) == sig(H[k]) else align(H[k], D0[k])) for k in ks}
                if not all(al.values()) and c in BARRED:                # đ: dựng từ đ mặc định + d nét mảnh + gạch ép mảnh
                    b = BARRED[c]
                    al = {k: bar_morph(D0[k], D0[f'{b}-{k.rsplit("-", 1)[1]}'], H[f'{b}-{k.rsplit("-", 1)[1]}'], HAIR_MIN/HAIR_DEF) for k in ks}
                if all(al.values()): H = dict(H); H.update(al); nal += 1
            if all(k in D0 and k in H and sig(D0[k]) == sig(H[k]) for k in ks):
                for k in ks: M[k] = H[k]
            elif all(k in D0 for k in ks): keep.add(c)
        EF.O = M; EF._PAIR.clear(); EF._STEM.clear()
        FL = {}
        for c in EF.CHARS:
            if f'{c}-Regular' in M:
                fl = EF.flips(EF.parse(M[f'{c}-Regular']))
                if fl: FL[c] = fl
        groups, ks = EF.kerning_data()
        MS = {w: EF.master(w, ang, FL, groups, ks[w]) for w in ('Regular', 'Bold')}
        EF.pair_fix(MS['Regular'], MS['Bold'])
        import ufoLib2
        fixed = 0; fixn = []
        for w in ('Regular', 'Bold'):
            base = ufoLib2.Font.open(os.path.join(EF.BUILD, f'{EF.PS}{tag}-{w}.ufo'))
            for g in MS[w]:
                if g.name in base and gsig(base[g.name]) != gsig(g):       # lệch cấu trúc với master mặc định → khớp lại điểm; không được thì giữ mặc định
                    rc = reconcile(g, base[g.name])
                    if rc is not None:
                        g.clearContours(); pen = g.getPointPen()
                        for pts in rc:
                            pen.beginPath()
                            for xy, tp in pts: pen.addPoint(xy, segmentType=tp)
                            pen.endPath()
                    if rc is None or gsig(base[g.name]) != gsig(g):
                        if os.environ.get('HAIR_DEBUG'): print('DEBUG', g.name, w, [[(round(p.x), round(p.y), (p.type or 'o')[0]) for p in c.points] for c in g.contours], [[(round(p.x), round(p.y), (p.type or 'o')[0]) for p in c.points] for c in base[g.name].contours])
                        g.clearContours(); base[g.name].drawPoints(g.getPointPen()); fixed += 1; fixn.append(f'{g.name}/{w[0]}')
                    else: fixn.append(f'{g.name}/{w[0]}:khớp lại')
            p = os.path.join(EF.BUILD, f'{EF.PS}{tag}-{w}-Hair.ufo')
            if os.path.exists(p): shutil.rmtree(p)
            MS[w].save(p)
        print(f'HAIR{tag or " Roman"}: khớp cấu trúc {nal} chữ · giữ mặc định {len(keep)} chữ (lệch cấu trúc: {"".join(sorted(keep))}) · sửa sau dựng {fixed} {fixn}')
        ds = DesignSpaceDocument()
        for name, t_, lo, df, hi in (('Weight', 'wght', 400, 400, 700), ('Hairline', 'HAIR', HAIR_MIN, HAIR_DEF, HAIR_DEF)):
            ax = AxisDescriptor(); ax.name, ax.tag, ax.minimum, ax.default, ax.maximum = name, t_, lo, df, hi; ds.addAxis(ax)
        for w in ('Regular', 'Bold'):
            for hair, suf in ((HAIR_DEF, ''), (HAIR_MIN, '-Hair')):
                s = SourceDescriptor(); s.path = os.path.join(EF.BUILD, f'{EF.PS}{tag}-{w}{suf}.ufo')
                s.location = {'Weight': EF.WGHT[w], 'Hairline': hair}; s.familyName = EF.FAMILY; ds.addSource(s)
        for w in EF.WGHT:
            ins = InstanceDescriptor(); ins.familyName = EF.FAMILY
            ins.styleName = (w + ' Italic' if w != 'Regular' else 'Italic') if ang else w
            ins.location = {'Weight': EF.WGHT[w], 'Hairline': HAIR_DEF}
            ins.postScriptFontName = f'{EF.PS}Hair-' + (w + 'Italic' if ang and w != 'Regular' else ('Italic' if ang else w))
            ds.addInstance(ins)
        dsp = os.path.join(EF.BUILD, f'{EF.PS}{tag}-Hair.designspace'); ds.write(dsp)
        before = set(os.listdir(VF))
        subprocess.run(['fontmake', '-m', dsp, '-o', 'variable', '--output-dir', VF, '--flatten-components'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        new = [f_ for f_ in os.listdir(VF) if f_ not in before][0]
        dst = os.path.join(VF, f'{EF.PS}{tag}[HAIR,wght].ttf'); os.replace(os.path.join(VF, new), dst)
        from fontTools.ttLib import TTFont
        from fontTools.otlLib.builder import buildStatTable
        f = TTFont(dst)
        wv = [dict(value=v, name=n) for n, v in EF.WGHT.items()]; wv[0].update(flags=0x2, linkedValue=700)
        hv = [dict(value=HAIR_DEF, name='Normal', flags=0x2), dict(value=HAIR_MIN, name='Hairline')]
        buildStatTable(f, [dict(tag='wght', name='Weight', values=wv), dict(tag='HAIR', name='Hairline', values=hv)])
        nm = f['name']                                                # tên PostScript riêng (không trùng file [wght])
        for rec in list(nm.names):
            if rec.nameID == 6 and 'Hair' not in rec.toUnicode(): rec.string = rec.toUnicode().replace(EF.PS + '-', EF.PS + 'Hair-')
        nm.setName(EF.PS + 'Hair', 25, 3, 1, 0x409)
        nm.names = [n for n in nm.names if n.platformID != 1]
        f.save(dst)
        W2 = os.path.join(EF.FONTS, 'woff2', 'variable'); os.makedirs(W2, exist_ok=True)
        t = TTFont(dst); t.flavor = 'woff2'; t.save(os.path.join(W2, os.path.basename(dst).rsplit('.', 1)[0] + '.woff2'))
        print('  ', os.path.relpath(dst, EF.ROOT), os.path.getsize(dst)//1024, 'KB')

if __name__ == '__main__':
    main()
