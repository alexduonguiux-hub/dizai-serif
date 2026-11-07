#!/usr/bin/env python3
"""S20 Đồng bộ cấu trúc Bold theo Regular (designer 07/11 duyệt đề xuất "các chữ còn lại": 5, M, N) → designer_B.json.
    python3 tools/construct/ref/fix_struct_bold.py      (chạy lại nhiều lần cho cùng kết quả)

Khấc / loe là module CỐ ĐỊNH theo đơn vị Regular (bằng nhau ở mọi weight). Bản vẽ Bold thiếu hoặc khác → Medium / SemiBold
nội suy giữa hai cấu trúc khác nhau (góc ↔ trơn).
  N  khấc chữ V ở hai đỉnh chéo: Regular cạnh thân đi 14 u rồi mặt cắt dốc về chân lệch 5.6 u; Bold chỉ bậc 5.8 u
     → Bold: cạnh thân 14 u, chân khấc lệch 5.6 u, cạnh chéo xoay ~0.8° tới chân khấc (đỉnh dưới phải + đỉnh trên trái)
  M  loe đỉnh thân trái: Regular = module loe chuẩn (bắt đầu 630.2, cong tới 7.7 686.5, thẳng tới 0 700 — như chân N Bold);
     Bold loe ngắn từ 665.6, gãy 18° → dùng đúng module chuẩn
  5  khấc vát chỗ mép phẳng chân thân gặp mép trong vai bụng: Regular vát 13.4 × 15.5 u; Bold phẳng → Bold: mép phẳng dừng
     ở 73.1, vát lên 86.5 414.7, đường cong bụng bắt đầu từ đó (tay nắm giữ nguyên)
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
FIX = {
    'N-Bold': [('M96.4 705.5L459.1 235.8', 'M96.4 697.3L102 711.3L459.1 235.8'),
               ('L96.4 711.3L96.4 705.5Z', 'L96.4 711.3L96.4 697.3Z'),
               ('L459.1 -11.3L459.1 -5.5L96.4 466.1', 'L459.1 -11.3L459.1 2.7L453.5 -11.3L96.4 466.1')],
    'M-Bold': [('L22.7 665.6C20.3 672.8 17.2 679.8 13.4 686.5L5.7 700L87.9 700Z', 'L22.7 630.2C22.7 649.9 17.5 669.3 7.7 686.5L0 700L87.9 700Z')],
    '5-Bold': [('L4.3 399.2L86.5 399.2C175.0 416.1', 'L4.3 399.2L73.1 399.2L86.5 414.7C175.0 416.1')],
}

if __name__ == '__main__':
    p = os.path.join(HERE, 'designer_B.json'); B = json.load(open(p))
    for k, reps in FIX.items():
        d = B[k][0]
        for old, new in reps:
            if new in d: continue                                   # đã áp
            if old not in d: print('  bỏ qua (đã đổi bởi balance_diag):', k); continue
            d = d.replace(old, new)
        B[k] = [d]
        print(k, 'ok')
    json.dump(B, open(p, 'w'), separators=(',', ':'))
