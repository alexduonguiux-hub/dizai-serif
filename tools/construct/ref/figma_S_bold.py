#!/usr/bin/env python3
"""S Bold vẽ lại bởi designer trên Figma (06/11, file gGrYT5oldAplC9IedaAj7b, node 2145:1225 "Union" trong Frame 2 2145:1227,
trang "Design v0.2 — cân bằng (Claude)") → designer_B.json['S-Bold'].
    python3 tools/construct/ref/figma_S_bold.py      (chạy lại bao nhiêu lần cũng cho cùng kết quả)

Bối cảnh: designer 06/11 "Các đường cong của chữ s và S. Cảm giác không smooth lắm" → thử luật G2 (S17, font/fair.py) →
"bây giờ bụng nó lại không cong tròn tự nhiên" → designer tự chỉnh vector ("Đọc vector mẫu ở đây", "mình vừa chỉnh lại nét").
Bản vẽ của designer là chuẩn; S17 tắt (compat_masters.FAIR rỗng).

Quy đổi toạ độ Figma (y xuống) → đơn vị font: giải từ bốn góc đầu nét không đổi so với S Bold cũ
(19.8, 27.4) (19.8, 186.4) (410.9, 689.6) (410.9, 533.5): x = 2.8341·X − 0.04, y = 711.34 − 2.8341·Y (sai < 0.1 u).
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
FIGMA = ("M 46.5 55.130859375 C 46.5 88.5 88.1943244934082 100.38976097106934 113.5 115 C 144.6701488494873 132.99609375 159 152 "
         "159 187.869140625 C 159 223.73828125 126 256 81.5 256 C 46.000099182128906 256 7 241.3291015625 7 241.3291015625 L 7 "
         "185.236328125 C 19 207.67412757873535 57 231 76 231 C 94.99999618530273 231 110.2076153755188 222.85941886901855 116 201.5 "
         "C 124 172 98.4247055053711 160.13159370422363 51.4248046875 132.99609375 C 4.424945831298828 105.8606014251709 0 81 0 "
         "57.130859375 C 0 19.5 41.00011444091797 0 76.5 0 C 111.99789810180664 0 144.9962746060919 7.670032492955215 145 "
         "7.6708984375 L 145 62.763671875 C 132.9999876022339 40.325883865356445 94.9999942779541 24.4228515625 76 24.4228515625 "
         "C 57.00001335144043 24.4228515625 46.5000149638945 35.49998664855957 46.5 55.130859375 Z")
S, X0, Y0 = 2.8341, -0.04, 711.34


def convert(d):
    toks = re.findall(r'[MLCZ]|-?[\d.]+(?:e-?\d+)?', d); out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t in 'MLCZ': out.append(t); i += 1; continue
        x, y = float(toks[i]), float(toks[i + 1]); i += 2
        out.append('%g %g' % (round(S*x + X0, 1) + 0.0, round(Y0 - S*y, 1) + 0.0))
    return re.sub(r' ?([MLCZ]) ?', r'\1', ' '.join(out))


if __name__ == '__main__':
    p = os.path.join(HERE, 'designer_B.json'); B = json.load(open(p))
    old = B['S-Bold'][0]; B['S-Bold'] = [convert(FIGMA)]
    json.dump(B, open(p, 'w'), separators=(',', ':'))
    print('S-Bold cũ :', old[:120]); print('S-Bold mới:', B['S-Bold'][0][:120])
