#!/usr/bin/env python3
"""QA tay loe đầu thanh (S56, designer 20/11 "phần loe của T và E đang không bằng nhau"): mép cắt đứng ở đầu tay (gốc trên đường kẻ
0 / 700, dài 20–250) của E F L T Z Æ Œ phải dài BẰNG NHAU trong mỗi weight (lệch ≤ 1.5 u).
    python3 tools/construct/qa_arms.py <font %s>"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
def cuts(f, ch):
    gs = f.getGlyphSet(); pen = RecordingPen(); gs[f.getBestCmap()[ord(ch)]].draw(pen); out = []; last = None
    for op, pts in pen.value:
        if op == 'lineTo' and last and abs(last[0] - pts[0][0]) < 0.6:
            lo, hi = sorted((last[1], pts[0][1]))
            if (abs(hi - 700) < 0.6 or abs(lo) < 0.6) and 20 <= hi - lo <= 250: out.append(round(hi - lo, 1))
        if op == 'moveTo': last = pts[0]
        elif pts: last = pts[-1]
    return out
bad = 0
for w in ('Regular', 'Medium', 'SemiBold', 'Bold'):
    f = TTFont(sys.argv[1] % w); r = {c: cuts(f, c) for c in 'EFLTZÆŒ'}
    allv = [v for vs in r.values() for v in vs]
    spread = max(allv) - min(allv) if allv else 0; bad += spread > 1.5
    print(f'{w}: tay loe {r} · chênh {spread:.1f}')
print('tay loe không bằng nhau:', bad, 'weight')
