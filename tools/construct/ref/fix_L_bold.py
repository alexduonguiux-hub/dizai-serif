#!/usr/bin/env python3
"""L Bold: tay dưới theo nguyên tắc Bold (docs/08) — thanh/tay 40 → 68, tay dưới dày lên phía trên, mỏ giữ hình và trượt
theo mép (+28.3 u). Bản vẽ gốc giữ tay dưới 40 như Regular; designer 04/11: "glyph của chữ L hoa hình như lỗi độ dày".
    python3 tools/construct/ref/fix_L_bold.py   → designer_B.json: L-Bold (chạy lại nhiều lần vẫn cho cùng kết quả)
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); f = os.path.join(HERE, 'designer_B.json')
B = json.load(open(f))
GOC = "M161.5 39.7L362.8 39.7C396.6 39.7 428.5 55.8 448.5 83L456.3 93.5L456.3 0L0 0L7.7 13.5C17.5 30.7 22.7 50.1 22.7 69.8L22.7 630.2C22.7 649.9 17.5 669.3 7.7 686.5L0 700L161.5 700L161.5 39.7Z"
dy = 68 - 39.7
MOI = (f"M161.5 {39.7+dy:.1f}L362.8 {39.7+dy:.1f}C396.6 {39.7+dy:.1f} 428.5 {55.8+dy:.1f} 448.5 {83+dy:.1f}L456.3 {93.5+dy:.1f}"
       "L456.3 0L0 0L7.7 13.5C17.5 30.7 22.7 50.1 22.7 69.8L22.7 630.2C22.7 649.9 17.5 669.3 7.7 686.5L0 700L161.5 700"
       f"L161.5 {39.7+dy:.1f}Z")
if B['L-Bold'][0] in (GOC, MOI):
    B['L-Bold'] = [MOI]; json.dump(B, open(f, 'w'), ensure_ascii=False, separators=(',', ':')); print('L-Bold: tay dưới 68')
else:
    print('L-Bold đã khác bản gốc — không sửa tự động')
