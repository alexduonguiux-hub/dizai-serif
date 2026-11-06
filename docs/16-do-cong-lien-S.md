# 16. Đường cong S s — S Bold vẽ lại theo vector của designer

## Diễn biến (06/11)

1. Designer: "Các đường cong của chữ s và S. Cảm giác không smooth lắm" (ảnh cắt cực trái bụng trên S).
2. Đo: đường liền tiếp tuyến (G1) nhưng bán kính cong nhảy ở điểm cực, ví dụ cực trái bụng trên S Regular 129 / 473 (×3.7).
   Đã thử luật **S17 độ cong liền G2** (`font/fair.py`): chỉnh độ dài tay nắm để bán kính hai bên mỗi nút bằng nhau.
3. Designer: "bây giờ bụng nó lại không cong tròn tự nhiên".
   G2 kéo dài tay nắm ở chính các góc tư bụng (cung gần elip), làm bụng phình vuông.
4. Designer tự vẽ lại S Bold trên Figma ("Đọc vector mẫu ở đây", "mình vừa chỉnh lại nét"):
   file `gGrYT5oldAplC9IedaAj7b`, node `2145:1225`.

## Kết luận

- **Bản vẽ của designer là chuẩn.** S17 **tắt**: `compat_masters.FAIR = set()`. Code `font/fair.py` giữ lại để tham khảo.
- Vector của designer **không** G2: tỉ lệ bán kính hai bên một số nút vẫn ×3–4. "Tròn tự nhiên" theo mắt quan trọng hơn chỉ số G2.
  Không dùng G2 làm luật tự động cho bụng chữ.
- `ref/figma_S_bold.py` ghi vector vào `designer_B.json['S-Bold']`.
  - Quy đổi: x = 2.8341·X − 0.04, y = 711.34 − 2.8341·Y, giải từ 4 góc đầu nét không đổi; sai < 0.1 u.
  - S Bold trong font khớp vector: lệch 0.00 u.

## Điều designer đã đổi ở S Bold (so với bản trước)

| Chỗ | Trước | Sau |
|---|---|---|
| Nút sống (bụng trên → sống, mép trên) | (361.5, 374.5) | (321.6, 385.4), tay nắm dài theo hướng sống |
| Cực phải bụng dưới | y 170.4 | y 178.9 |
| Đáy lòng dưới | (232.4, 55) | (215.4, 56.7) |
| Lòng phải bụng dưới | cực trị (320.2, 164.7) | điểm xiên (328.7, 140.3) |
| Cực trái bụng trên | y 555.1 | y 549.4, tay nắm trên dài 87 → 107 |
| Tay nắm đáy ngoài | 101 | 126 |

Hệ quả:
- **Sống S Bold mỏng đi:** đường kính nội tiếp giữa sống 146 → 131. SemiBold 133 → 123. s Bold 118 → 106, vì s là S thu nhỏ.
- Bảng nét cũ ghi sống S Bold 143. Chờ designer xác nhận độ mỏng mới là chủ ý.
- Medium / SemiBold nội suy lại (`ref/interp.py`). s, $, Š, š, § đi theo S.
- S Regular **chưa đổi**: designer mới gửi mẫu Bold.
