# 16. Đường cong S s — S Regular + Bold vẽ lại theo vector của designer; S18 nội suy liền tiếp tuyến

## Diễn biến (06/11)

1. Designer: "Các đường cong của chữ s và S. Cảm giác không smooth lắm" (ảnh cắt cực trái bụng trên S).
2. Đo: đường liền tiếp tuyến (G1) nhưng bán kính cong nhảy ở điểm cực, ví dụ cực trái bụng trên S Regular 129 / 473 (×3.7).
   Đã thử luật **S17 độ cong liền G2** (`font/fair.py`): chỉnh độ dài tay nắm để bán kính hai bên mỗi nút bằng nhau.
3. Designer: "bây giờ bụng nó lại không cong tròn tự nhiên".
   G2 kéo dài tay nắm ở chính các góc tư bụng (cung gần elip), làm bụng phình vuông.
4. Designer tự vẽ lại S Regular + Bold trên Figma ("Đọc vector mẫu ở đây", "mình vừa chỉnh lại nét"):
   file `gGrYT5oldAplC9IedaAj7b`, node `2145:1225`.

## Kết luận

- **Bản vẽ của designer là chuẩn.** S17 **tắt**: `compat_masters.FAIR = set()`. Code `font/fair.py` giữ lại để tham khảo.
- Vector của designer **không** G2: tỉ lệ bán kính hai bên một số nút vẫn ×3–4. "Tròn tự nhiên" theo mắt quan trọng hơn chỉ số G2.
  Không dùng G2 làm luật tự động cho bụng chữ.
- `ref/figma_S.py` ghi vector vào `designer_B.json['S-Bold']`.
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
- S Regular: designer gửi tiếp (node `2145:1235` trong Frame `2145:1228`). Cùng phép quy đổi, ghi vào `designer_A.json['S-Regular']`.
  Điểm nối bụng trên → sống và cực trái bụng trên đổi như bản Bold. Lòng dưới gọn hơn: đáy lòng (181, 24), lòng phải (297.5, 164.7).

## S18 Nội suy liền tiếp tuyến (designer 06/11: "bụng s medium và semi bold lỗi")

- **Lỗi:** hai master ghép điểm neo theo thứ tự.
  - s Regular neo ở cực phải bụng dưới (349, 123). s Bold, thu nhỏ từ S Bold mới, neo ở chỗ xiên (311, 31).
  - Medium / SemiBold nội suy giữa hai hướng tiếp tuyến khác nhau nên gãy 14° / 13° ở mép ngoài bụng dưới. Đó là chỗ phồng designer thấy.
- **Sửa** (`compat_masters.reanchor`), chỉ ở nút mà bản nội suy giữa gãy > 2°:
  1. Một master neo ở cực trị, master kia neo xiên → dời nút của master kia về cực trị cùng trục, trên chính đường cong của nó.
     Cắt de Casteljau và khớp lại phần còn lại, sai số ≤ 2.5 u.
  2. Cả hai master đều xiên → đặt tỉ lệ tay nắm vào / ra của hai master bằng nhau. Chỉ nhận khi master lệch ≤ 2.5 u.
  3. Hai đoạn thẳng: một master thẳng hàng, master kia có góc (góc đầu nét dưới s Regular có bậc ngang 5 u) → đặt điểm chia theo tỉ lệ độ dài của master có góc. Hình master không đổi.
- **Kết quả:** gãy ở Medium / SemiBold về 0 ở s š ơ ư (và mọi chữ có sừng) k ç £ § ® W.
  - Master xê dịch ≤ 2–3 u. S Regular / Bold giữ đúng vector designer (S chỉ gãy 1.3° < ngưỡng).
  - Còn lại & (20°), @ (22°), Š (7°): không sửa được trong giới hạn 2.5 u, cần vẽ lại điểm neo tương ứng.
