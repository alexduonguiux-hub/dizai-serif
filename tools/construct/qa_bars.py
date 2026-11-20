#!/usr/bin/env python3
"""QA thanh ngang (S52, designer 20/11 "thanh ngang của T sao lại dày hơn của các chữ khác"):
    python3 tools/construct/qa_bars.py <font %s> <chuẩn Regular> <chuẩn Bold> [chars]
Rasterize 1 u / px. Ở mỗi cột x, mỗi đoạn mực đứng có mép trên VÀ mép dưới phẳng (lệch ≤ 0.6 u trên ±12 cột) và dày ≤ 1.8 × chuẩn
là một THANH NGANG. Độ dày thanh của chữ = trung vị các cột. Báo chữ lệch chuẩn > 3 u (Regular / Bold).
"""
import sys
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from PIL import Image, ImageDraw

def raster(font, ch):
    gs = font.getGlyphSet(); gn = font.getBestCmap().get(ord(ch))
    if gn is None: return None
    pen = RecordingPen(); gs[gn].draw(pen); polys = []; cur = []; last = None
    for op, pts in pen.value:
        if op == 'moveTo': cur = [pts[0]]; last = pts[0]
        elif op == 'lineTo': cur.append(pts[0]); last = pts[0]
        elif op == 'curveTo':
            p0 = last
            for k in range(1, 25):
                t = k/24; cur.append(tuple((1-t)**3*p0[i] + 3*(1-t)**2*t*pts[0][i] + 3*(1-t)*t*t*pts[1][i] + t**3*pts[2][i] for i in (0, 1)))
            last = pts[2]
        elif op in ('closePath', 'endPath'): polys.append(cur)
    W, H, X0, Y0 = 1400, 1300, 200, 400                 # x ∈ [−200, 1200], y ∈ [−400, 900]
    m = np.zeros((H, W), bool)
    for pl in polys:
        im = Image.new('1', (W, H), 0); ImageDraw.Draw(im).polygon([(x + X0, 900 - y) for x, y in pl], fill=1); m ^= np.array(im)
    return m

def bars(m, tgt):
    H, W = m.shape; th = []
    runs = {}
    for x in range(W):
        col = m[:, x]
        if not col.any(): continue
        d = np.diff(np.concatenate([[0], col.astype(int), [0]])); st = np.nonzero(d == 1)[0]; en = np.nonzero(d == -1)[0]
        runs[x] = list(zip(st, en))
    for x, rs in runs.items():
        for s, e in rs:
            t = e - s
            if t > 1.8*tgt or t < 0.4*tgt: continue
            ok = True
            for dx in (-12, -6, 6, 12):
                nb = runs.get(x + dx)
                if not nb or not any(abs(s2 - s) <= 0.6 and abs(e2 - e) <= 0.6 for s2, e2 in nb): ok = False; break
            if ok: th.append(t)
    return th

if __name__ == '__main__':
    pat, tR, tB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    chars = sys.argv[4] if len(sys.argv) > 4 else 'ABDEFGHJKLMNPRTUZaefgstz'
    bad = []
    for w, tgt in (('Regular', tR), ('Bold', tB)):
        f = TTFont(pat % w); row = []
        for ch in chars:
            m = raster(f, ch)
            if m is None: continue
            th = bars(m, tgt)
            if len(th) < 8: continue
            med = float(np.median(th)); row.append(f'{ch}{med:.0f}')
            if abs(med - tgt) > 3: bad.append((w, ch, round(med, 1)))
        print(f'{w} chuẩn {tgt:.0f}:', ' '.join(row))
    print('thanh ngang lệch chuẩn > 3 u:', len(bad), bad)
