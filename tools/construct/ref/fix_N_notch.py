#!/usr/bin/env python3
"""S29 Đóng khấc nêm ở hai đỉnh nhọn của N (designer 10/11 "Hở mối nối N").
    python3 tools/construct/ref/fix_N_notch.py      (chạy lại nhiều lần cho cùng kết quả)

N Regular (bản vẽ) — và Bold theo S20 — có khấc nêm ở đỉnh dưới phải (chéo gặp thân phải ở đường chân) và đỉnh trên trái:
mép thân đi 14 u rồi mặt cắt dốc lệch 5.6 u → khe hẹp 5.6 × 14 u đọc thành VẾT HỞ ở cỡ chữ thường. Đóng: mép đáy / đỉnh
chạy thẳng tới chân / đỉnh nét chéo (một điểm), bỏ hai điểm khấc. Áp Regular (designer_A) + Bold (designer_B);
Medium / SemiBold nội suy lại (interp.py)."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
NUM = r'-?[\d.]+'

def close(d):
    # đáy: L{x} -11.3 L{x} 2.7 L{x2} -11.3 → L{x2} -11.3
    d2 = re.sub(rf'L({NUM}) -11\.3L\1 2\.7L({NUM}) -11\.3', r'L\2 -11.3', d)
    # đỉnh: M{a} 697.3 L{b} 711.3 … L{a} 711.3 L{a} 697.3 Z → M{b} 711.3 … Z
    m = re.match(rf'M({NUM}) 697\.3L({NUM}) 711\.3(.*)L\1 711\.3L\1 697\.3Z$', d2)
    if m: d2 = f'M{m.group(2)} 711.3{m.group(3)}Z'
    return d2

if __name__ == '__main__':
    for f, k in (('designer_A.json', 'N-Regular'), ('designer_B.json', 'N-Bold')):
        p = os.path.join(HERE, f); D = json.load(open(p)); d = D[k][0]; n = close(d)
        print(k, 'đóng khấc' if n != d else 'đã đóng'); D[k] = [n]
        json.dump(D, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
