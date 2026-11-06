# 16. Độ cong liền (G2) cho S s — luật S17

Designer 06/11: "Các đường cong của chữ s và S. Cảm giác không smooth lắm" (ảnh cắt cực trái bụng trên S).

## Chẩn đoán

Đường viền liền tiếp tuyến (G1, không gãy góc), nhưng **độ cong nhảy** ở các điểm neo. Đo bán kính cong hai bên mỗi nút:

| Chỗ | Trước (R vào / R ra) | Tỉ lệ |
|---|---|---|
| S Regular, cực trái bụng trên | 473 / 129 | ×3.7 |
| S Regular, đỉnh | 219 / 700 | ×3.2 |
| S Regular, cực phải bụng dưới | 196 / 967 | ×4.9 |
| S Bold, cực trái bụng trên | 98 / 503 | ×5.1 |
| s Regular, cực trái | 95 / 219 | ×2.3 |

Mắt đọc chỗ nhảy độ cong là "cong gắt rồi bỗng thẳng". Đây đúng là đoạn trong ảnh của designer. Nguyên nhân: tay nắm Bézier hai bên điểm cực dài không cân nhau.

## Luật S17 (`tools/construct/font/fair.py`, gọi trong `compat_masters.py`)

- Áp cho **S s Š š $ §**, cả hai master Regular / Bold; Medium / SemiBold nội suy như cũ.
- **Giữ** số điểm, loại đoạn (master vẫn tương thích cho variable) và hướng tiếp tuyến ở mọi nút.
- Nút trơn còn gãy nhẹ (< 6°, sót từ boolean / đơn giản hoá) → hai tay nắm về chung một hướng.
- Đổi độ dài tay nắm, và cho nút trượt dọc tiếp tuyến của chính nó tối đa 8 u, để độ cong hai bên mỗi nút bằng nhau.
  - Trượt dọc tiếp tuyến nên nút ở cực trái / đỉnh vẫn là cực trị, toạ độ cực không đổi.
  - Bình phương tối thiểu, có phạt độ lệch hình.

## Kết quả

| | Tỉ lệ bán kính lớn nhất ở nút trơn | Lệch hình lớn nhất |
|---|---|---|
| S Regular | 5.0 → 1.07 | ~8 u |
| S Bold | 5.6 → 1.12 | ~13 u (vùng sống – bụng trên) |
| s Regular / Bold | 7.5 / 4.2 → 1.00 | ~2 u |

- Còn 2 cờ gãy ~2° ở s Regular / SemiBold, do làm tròn toạ độ nguyên khi xuất (tay nắm ngắn), lệch ~1 u.
- Lòng s có chỗ ngoặt gắt R ≈ 37 ở khuỷu trong bụng trên. Đó là hình thiết kế: độ cong vẫn liền, không nhảy.
- Ảnh so sánh có lược độ cong: `docs/img/S-G2-compare.png`.

Quét toàn bộ font (Regular): 46 glyph có tỉ lệ bán kính > 3 ở nút trơn (họ a ă â…, j, &, 5, g, t, f, 2, ~, dấu phẩy và nháy…). Luật S17 hiện **chỉ** áp cho S s; mở rộng cần designer duyệt.
