#!/usr/bin/env python3
"""S23 Cân độ đậm số 2, 8 (designer 07/11 "cân lại 2, 8, 4 luôn") → designer_B.json (khoá 2-Regular, 2-Bold, 8-Bold).
    python3 tools/construct/ref/fix_fig_weight.py      (đi từ bản lưu designer_B_prefig2.json → chạy lại cho cùng kết quả)

Đo độ dày LỚN NHẤT từng nét (vùng hộp mực, bỏ khớp), Regular → Bold:
  bụng 0 / 3 / 6 = 111 / 107 / 102 → 139 / 143 / 136 · 2 bụng 97 → 130 (nhẹ ~9 % ở CẢ HAI master)
  8 bụng dưới 98 → 132 · 8 bụng trên 86 → 106: Regular trên / dưới = 0.88 (vòng trên nhẹ hơn — luật), Bold tụt còn 0.80
  4 thân 104 → 143 = 1 thân 102 → 140: cân (qa_stroke so với 0 — nét tròn — nên báo nhầm "B/R 1.38")
Sửa:
  2, 8  làm đậm NGANG (Tiller–Hanson, symbols.hdilate, chỉ nét đứng +2·DX2) cả hai master — bụng ≈ trung bình 0 / 3 / 6;
        chiều cao, đường chân, đỉnh giữ nguyên. ? ¿ và dấu hỏi vẫn dựng từ số 2 GỐC (designer_Q.json)
  S37 (11/11 "tham khảo đường cong số 2 từ mẫu gốc", Figma 2168:109): 2 Bold = bản vẽ Bold MỚI của designer (vai phải
        vuông hơn, thanh 131, bụng 142, đầu nét trái 480) — đã đậm hơn bản làm đậm S23 nên KHÔNG làm đậm thêm; chỉ đổi
        đơn vị (× 711.3/251, lật trục y) và cho tay nắm góc chân trái suy biến như cũ. 2 Regular giữ đường cong gốc (+10 ngang)
  S37b (11/11 "cân lại độ dày số cho đồng bộ"): đo nét dày nhất từng nét chính (đường kính tròn nội tiếp lớn nhất,
        bỏ khớp) R / B: 0 111/139 · 1 103/139 · 2 106/142 · 3 107/144 · 4 106/145 · 5 107/143 · 7 108/137 · 8 107/139
        — riêng bụng 6, 9 nhẹ 102/136 (−4 %) → làm đậm ngang +4 (Regular) / +5 (Bold), cùng cách S23
  8  Bold: thu lòng trên (contour lỗ có tâm cao hơn) quanh tâm của nó — ngang −2·SX8, dọc −2·SY8 → bụng trên = 0.88 × bụng dưới
"""
import json, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
DX2 = {'2-Regular': 5.0, '2-Bold': 4.5, '8-Regular': 4.5, '8-Bold': 3.5,
       '6-Regular': 2.0, '9-Regular': 2.0, '6-Bold': 2.5, '9-Bold': 2.5}; DY2 = 0.0   # chỉ ngang: giữ đường chân / đỉnh (6, 9: S37b)
# S37: Figma 2168:109 "Union" (Bold), hộp 168.1 × 251 → đơn vị font ×711.3/251, y lật; góc chân trái 0.3 → 0, tay suy biến
FIG2_BOLD = ('M230.2 711.3C282.7 711.3 391.9 711.3 446.7 616.4C469.6 576.7 476.4 539.5 476.4 511.5C476.4 399.6 384.3 318.8 '
             '298.8 270.6C212.7 222.1 138.4 130.7 138.1 130.4L392.5 130.4C421 130.4 448.5 141.2 469.4 160.6L476.4 167.2L476.4 0'
             'L43.6 0C30.6 0 12.7 1.4 0 0C0 0 -7.9 72.7 58.4 170C114.8 252.7 177.4 293.9 211.5 318.8C370.2 435 363.1 581.6 '
             '262.2 608.6C213.2 621.7 146.3 596.5 99.5 562.5C77.3 546.3 37.6 491.7 29.1 480C28.2 535.2 28.8 600.8 28.8 656.1'
             'C65.5 677.3 127.8 711.3 230.2 711.3Z')
SX8, SY8 = 10.0, 5.0          # bụng trên Bold 106 → 116 = 0.88 × bụng dưới 132


def to_d(p):
    out = []
    for v, ps in p.segments:
        if v == 'moveTo': out.append('M%.1f %.1f' % ps[0])
        elif v == 'lineTo': out.append('L%.1f %.1f' % ps[0])
        elif v == 'curveTo': out.append('C' + ' '.join('%.1f %.1f' % q for q in ps))
        elif v == 'closePath': out.append('Z')
    return re.sub(r'\.0(?=[ MLCZ]|$)', '', ''.join(out))


if __name__ == '__main__':
    import pathops
    import symbols as SY
    import vn_punct as V
    from make_ref import outline
    p = os.path.join(HERE, 'designer_B.json'); keep = os.path.join(HERE, 'designer_B_prefig2.json')
    if not os.path.exists(keep): shutil.copy(p, keep)
    src = json.load(open(keep)); B = json.load(open(p))
    def dil(g, dx):
        b0 = g.bounds; h = SY.hdilate(g, dx, DY2); b1 = h.bounds
        y0 = b0[1]                                                   # chữ đứng trên đường chân (2): không điểm nào xuống dưới
        return V.xform(h, lambda x, y: (x - b1[0] + b0[0], max(y, y0) if abs(y0) < 0.5 else y))
    for k in ('2-Regular', '8-Regular', '6-Regular', '9-Regular', '6-Bold', '9-Bold'):
        d = to_d(dil(outline(src[k]), DX2[k]))
        if k[0] == '2':                                              # góc chân trái: tay nắm suy biến như 2 Regular (2 Bold vẽ
            d = re.sub(r'(C-?[\d.]+ -?[\d.]+ )-?\d(?:\.\d)? -?\d(?:\.\d)? (-?0 -?0)(?=L)', r'\1\2 \2', d)   # móc 3 u → gai khi nội suy)
            d = d.replace('-0 ', '0 ')
        B[k] = [d]; print(k, 'đậm ngang +%.0f' % (2*DX2[k]))
    B['2-Bold'] = [FIG2_BOLD]; print('2-Bold = Figma 2168:109 (S37)')
    # 8 Bold: làm đậm cả glyph, rồi THAY lòng trên bằng lòng gốc thu quanh tâm (thu thêm DX ngang = phần làm đậm) — lòng gốc có
    # đoạn 6 u ở đáy, làm đậm Tiller–Hanson trên đó sinh gai
    g = outline(src['8-Bold']); dx = DX2['8-Bold']
    def upper(p):
        cs = list(p.contours); W = p.bounds[2] - p.bounds[0]
        return max(range(len(cs)), key=lambda i: cs[i].bounds[1] if cs[i].bounds[2] - cs[i].bounds[0] < W - 5 else -1e9)
    up = list(g.contours)[upper(g)]; ub = up.bounds; cx, cy = (ub[0] + ub[2])/2 + dx, (ub[1] + ub[3])/2
    kx = 1 - 2*(SX8 + dx)/(ub[2] - ub[0]); ky = 1 - 2*SY8/(ub[3] - ub[1])
    h = dil(g, dx); hu = upper(h); out = pathops.Path()
    for i, c in enumerate(h.contours):
        q = pathops.Path(c) if i != hu else V.xform(pathops.Path(up), lambda x, y: (cx + (x - cx + dx)*kx, cy + (y - cy)*ky))
        out.addPath(q)
    B['8-Bold'] = [to_d(out)]; print('8-Bold lòng trên −%.0f / −%.0f, đậm ngang +%.0f' % (2*SX8, 2*SY8, 2*dx))
    json.dump(B, open(p, 'w'), separators=(',', ':'))
