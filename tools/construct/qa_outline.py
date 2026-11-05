#!/usr/bin/env python3
"""QA outline: quét mọi glyph trong ref_glyphs.json, liệt kê nét thừa và lỗi hình học.
    python3 tools/construct/qa_outline.py [--all] [--json out.json]
Mặc định chỉ báo glyph dựng theo luật (src = rule); --all quét cả bản vẽ designer (chỉ báo, không sửa).

Các loại lỗi:
  short    đoạn (thẳng hoặc cong) ngắn < 2.5 u — thường là khấc / mẩu thừa sau phép boolean
  spike    gai: hai đoạn kề nhau quay ngược > 150° (mũi nhọn thò ra / thụt vào)
  kink     gãy góc nhỏ 3–35° giữa hai đoạn cong (chỗ đáng lẽ liền mạch G1)
  dup      hai điểm liên tiếp trùng nhau (< 0.3 u)
  colin    điểm thừa giữa hai đoạn thẳng thẳng hàng
  speck    vòng kín diện tích < 400 u² (lỗ / mảnh li ti)
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def contours(cmds):
    out, cur = [], []
    for c in cmds:
        if c[0] == 'M': cur = [c]
        elif c[0] == 'Z': out.append(cur); cur = []
        else: cur.append(c)
    if cur: out.append(cur)
    return out

def segs(cont):
    """[(kind, p0, ctrl..., p3)] cho một contour, kể cả đoạn khép"""
    s = []; p = tuple(cont[0][1]); start = p
    for c in cont[1:]:
        if c[0] == 'L': q = tuple(c[1]); s.append(('L', p, q)); p = q
        elif c[0] == 'C': a, b, q = tuple(c[1]), tuple(c[2]), tuple(c[3]); s.append(('C', p, a, b, q)); p = q
    if math.dist(p, start) > 1e-6: s.append(('L', p, start))
    return s

def tan_out(sg):   # hướng ở đầu đoạn
    pts = sg[1:]
    for q in pts[1:]:
        if math.dist(q, pts[0]) > 1e-6: return math.atan2(q[1] - pts[0][1], q[0] - pts[0][0])
    return None
def tan_in(sg):    # hướng ở cuối đoạn
    pts = sg[1:]
    for q in reversed(pts[:-1]):
        if math.dist(q, pts[-1]) > 1e-6: return math.atan2(pts[-1][1] - q[1], pts[-1][0] - q[0])
    return None
def seglen(sg):
    pts = sg[1:]
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) if sg[0] == 'C' else math.dist(pts[0], pts[1])
def area(cont):
    pts = [tuple(cont[0][1])] + [tuple(c[-1]) for c in cont[1:]]
    return 0.5*sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(pts, pts[1:] + pts[:1]))

def check(cmds):
    issues = []
    for ci, cont in enumerate(contours(cmds)):
        if len(cont) < 2: continue
        A = abs(area(cont))
        if A < 400: issues.append(('speck', ci, tuple(cont[0][1]), round(A))); continue
        S = segs(cont); n = len(S)
        for i, sg in enumerate(S):
            L = seglen(sg)
            if L < 0.3: issues.append(('dup', ci, sg[1], round(L, 2))); continue
            if L < 2.5: issues.append(('short', ci, sg[1], round(L, 2)))
            nx = S[(i + 1) % n]; a, b = tan_in(sg), tan_out(nx)
            if a is None or b is None: continue
            turn = abs((math.degrees(b - a) + 180) % 360 - 180)
            if turn > 150: issues.append(('spike', ci, sg[-1], round(turn)))
            elif sg[0] == 'L' and nx[0] == 'L' and turn < 0.5: issues.append(('colin', ci, sg[-1], round(turn, 2)))
            elif sg[0] == 'C' and nx[0] == 'C' and 3 < turn < 35: issues.append(('kink', ci, sg[-1], round(turn)))
    return issues

if __name__ == '__main__':
    ref = json.load(open(os.path.join(HERE, 'ref_glyphs.json')))
    import unicodedata
    allg = '--all' in sys.argv; rep = {}; inherited = 0
    BASE = {'$': 'S', '€': 'C', '&': '8', 'Æ': 'AE', 'Œ': 'OE', 'æ': 'ae', 'œ': 'oe', '™': 'TM', '®': 'R', '©': 'C', '¢': 'c',
            'Ð': 'D', 'Ø': 'O', 'ø': 'o', 'Þ': 'P', 'þ': 'pb', 'µ': 'u', '¥': 'Y', '£': 'f', 'ð': 'o', 'ß': 'l', '§': 'S', '‰': '%'}
    for k, v in ref.items():
        if not allg and v.get('src') not in ('rule', 'interp'): continue
        iss = check(v['cmds'])
        ch, w = k.rsplit('-', 1); bases = BASE.get(ch) or unicodedata.normalize('NFD', ch)[0]
        bks = [f'{b}-{w}' for b in bases if f'{b}-{w}' in ref and b != ch]
        if v.get('src') == 'interp': bks = [f'{ch}-Regular', f'{ch}-Bold']        # nội suy: lỗi kế thừa từ chính chữ đó ở hai master
        if v.get('src') in ('rule', 'interp') and bks:
            # lỗi kế thừa nguyên vẹn từ chữ gốc (mũi mỏ E, đầu nhọn S/C, đỉnh M, đầu cắt e…) không tính là lỗi dựng. Ký tự ghép
            # (Æ Œ æ œ ™ ® Ë…) dời toạ độ chữ gốc → so theo HÌNH góc (cùng loại, cùng góc ±2°), không theo toạ độ
            bi = [y for bk in bks for y in check(ref[bk]['cmds'])]
            if v.get('src') == 'interp':                           # nội suy: góc nằm giữa góc hai master (±2°) = kế thừa
                keep = [x for x in iss if not (any(x[0] == y[0] for y in bi) and
                        min(y[3] for y in bi if y[0] == x[0]) - 2 <= x[3] <= max(y[3] for y in bi if y[0] == x[0]) + 2)]
            else: keep = [x for x in iss if not any(x[0] == y[0] and abs(x[3] - y[3]) <= 2 for y in bi)]
            inherited += len(iss) - len(keep); iss = keep
        if iss: rep[k] = iss
    print('bỏ qua (kế thừa từ bản vẽ designer):', inherited)
    from collections import Counter
    tot = Counter(t for v in rep.values() for t, *_ in v)
    print('glyph có lỗi:', len(rep), '·', dict(tot))
    for k, v in sorted(rep.items(), key=lambda kv: -len(kv[1]))[:40]:
        print(f'  {k:12s}', len(v), ' '.join(f'{t}@({p[0]:.0f},{p[1]:.0f})' for t, _, p, _ in v[:6]))
    if '--json' in sys.argv: json.dump(rep, open(sys.argv[sys.argv.index('--json') + 1], 'w'), ensure_ascii=False, default=list)
