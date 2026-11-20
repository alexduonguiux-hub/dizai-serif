#!/usr/bin/env python3
"""QA đoạn thẳng (S51, designer 20/11 "nét trong của Z bị dốc"): luật nét mảnh chỉ được dời đoạn thẳng SONG SONG.
    python3 tools/construct/qa_lines.py <font gốc %s> <font mới %s> [weights…]
So từng đoạn thẳng (dài ≥ 40 u) của font gốc với đoạn cùng vị trí (contour, thứ tự) ở font mới:
  - đoạn NGANG / ĐỨNG ở bản gốc phải còn ngang / đứng (lệch ≤ 0.3°);
  - mép thẳng nằm trên đường kẻ (0 / 700 / x-height 495 → --xh=535 cho Golden) phải còn nằm đúng trên đó;
  - (--all) mọi đoạn thẳng giữ hướng (lệch ≤ 0.5°) — dùng cho AnNam Serif (không có phép giãn ngang / nâng x-height).
Glyph đổi cấu trúc (số contour / đoạn khác) liệt kê riêng, so theo hướng gần nhất.
"""
import math, sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

def lines(font, ch):
    gs = font.getGlyphSet(); gn = font.getBestCmap().get(ord(ch))
    if gn is None: return None
    pen = RecordingPen(); gs[gn].draw(pen); out = []; cur = []; last = None
    for op, pts in pen.value:
        if op == 'moveTo': cur = []; last = pts[0]; start = pts[0]
        elif op == 'lineTo': cur.append(('L', last, pts[0])); last = pts[0]
        elif op == 'curveTo': cur.append(('C', last, pts[-1])); last = pts[-1]
        elif op in ('closePath', 'endPath'):
            if last != start: cur.append(('L', last, start))
            out.append(cur)
    return out

def ang(a, b): return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
def dang(x, y): d = (x - y + 180) % 360 - 180; return abs(d)

XH = 495.0
def check(base, new, chars, allang):
    bad, struct = [], []
    GMAP = {0.0: 0.0, 700.0: 700.0, 495.0: XH}
    for ch in chars:
        A, B = lines(base, ch), lines(new, ch)
        if not A or not B: continue
        same = len(A) == len(B) and all(len(a) == len(b) for a, b in zip(A, B))
        if not same: struct.append(ch)
        for ci, ca in enumerate(A):
            for si, sa in enumerate(ca):
                if sa[0] != 'L' or math.dist(sa[1], sa[2]) < 40: continue
                a0 = ang(sa[1], sa[2])
                axis = min(dang(a0, k) for k in (0, 90, 180, -90)) < 0.05
                if not axis and not allang: continue
                if same: cands = [B[ci][si]] if B[ci][si][0] == 'L' else []
                else: cands = [s for c in B for s in c if s[0] == 'L' and math.dist(s[1], s[2]) >= 30]
                if not cands: continue
                sb = min(cands, key=lambda s: dang(ang(s[1], s[2]), a0) + 0.01*math.dist(s[1], sa[1]))
                d = dang(ang(sb[1], sb[2]), a0)
                tol = max(0.3 if axis else 0.5, math.degrees(math.atan2(1.2, math.dist(sa[1], sa[2]))))   # + sai số làm tròn toạ độ nguyên (±0.6 u mỗi đầu)
                if d > tol:
                    bad.append((ch, round(d, 2), [round(v) for v in sb[1]], [round(v) for v in sb[2]]))
                gy = next((g for g in GMAP if abs(sa[1][1] - g) < 0.5 and abs(sa[2][1] - g) < 0.5), None)
                if gy is not None and same and (abs(sb[1][1] - GMAP[gy]) > 0.5 or abs(sb[2][1] - GMAP[gy]) > 0.5):
                    bad.append((ch, 'rời đường kẻ', gy, [round(v) for v in sb[1]], [round(v) for v in sb[2]]))
    return bad, struct

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; allang = '--all' in sys.argv
    XH = next((float(a.split('=')[1]) for a in sys.argv if a.startswith('--xh=')), 495.0)
    pb, pn = args[0], args[1]; ws = args[2:] or ['Regular', 'Bold']
    tot = 0
    for w in ws:
        fb, fn = TTFont(pb % w), TTFont(pn % w)
        chars = [chr(u) for u in sorted(fb.getBestCmap()) if chr(u).isprintable() and not chr(u).isspace()]
        bad, struct = check(fb, fn, chars, allang)
        tot += len(bad)
        print(f'{w}: đoạn thẳng đổi hướng {len(bad)}', ''.join(sorted({b[0] for b in bad})), '· đổi cấu trúc:', ''.join(struct)[:80])
        for b in bad[:40]: print('   ', *b)
    print('tổng đoạn thẳng đổi hướng:', tot)
