# Dizai Serif — Audit đồng bộ weight trước khi bổ sung glyph (v0.2, 04/11/2026)

Đo trên render 1:1 của trang "Design v0.2 — cân bằng (Claude)" (cap = 247 px):
- **Độ dày nét:** 2 × distance transform trên xương nét, lấy p97.
- **Mật độ mực:** mực ÷ (bề ngang + 2 × 40 u) ÷ cap.

## Kết quả

| Nhóm | Nét dày p97 (px) | Trung vị | Mật độ trung bình |
|---|---|---|---|
| Chữ hoa Regular (26) | 34.9–38.2 | 36.0 | 0.306 |
| Bộ số (10) | 33.0–40.0 | 38.0 | 0.314 (+2.4 % so với chữ) |
| Chữ hoa Bold (A–T) | 50.0–52.7 | 50.0 | 0.412 (Bold/Regular = 1.30) |

## Đạt
- Thân, vòng và chéo dày của chữ hoa Regular nằm trong ±1.5 px quanh 36. X 33.9 là ngoại lệ đã duyệt.
- Bold: mọi glyph trong 50–52.7 px.
- Số và chữ cùng màu: số chỉ đậm hơn 2.4 %, nằm trong ngưỡng ±5 %.
- Tỉ lệ Bold/Regular 1.30 đều ở cả nhóm.

## Số 2: đã thử sửa rồi huỷ
- Lần thử làm dày nét chéo cong (dời điểm giữa của mép trái và các tay nắm) gây hai lỗi:
  - **góc dưới-trái bị bo tròn** (designer: "Không bo tròn");
  - sau khi trả tay nắm của góc về chỗ cũ, mép trái có chỗ uốn gãy.
- Độ dày đo lại gần như không tăng (p97 33.5 → 33.5), nên **đã trả số 2 về đúng path gốc**.
- Số 2 dày 33.5 px, so với Z 35.8 và 7 37.9. Nếu cần dày hơn thì designer vẽ lại đường cong trực tiếp; không vá bằng cách dời điểm.

## Nằm ở giới hạn, có chủ ý (không sửa)
- **Số 8:** vòng trên 31 px, vòng dưới 36 px (0.86). Đây là thiết kế của designer: vòng trên nhẹ hơn. Số đo p97 = 33 của cả chữ phản ánh vòng trên này.
- **Nét tròn của số dày 36 px (= thân), chữ hoa dày 37.5 px (1.05 V).** Màu chung vẫn cân vì số có nét ngang dày 32 px.
- **Số 6 (p97 40) nặng hơn 9 (38.1)** khoảng 2 px ở chỗ đuôi nối vào bụng. Cần chồng 6 xoay 180° lên 9 để xem đó là khác biệt chủ ý hay lệch.

## Còn mở (quyết định thiết kế, không phải lỗi weight)
- **Trục nét tròn:** O, Q, 0, 6, 8, 9 có trục nghiêng (lòng xoay 15–30°), còn C, G có trục đứng (lòng không xoay).
  - Vì vậy C trông nhẹ hơn O một chút: p90 Regular 34.7 so với 36.7, Bold 47.5 so với 50.5.
  - Luật S4 nói mọi chữ tròn dùng một trục. Cần designer chọn: xoay lòng C, G theo trục O, hay ghi C, G là ngoại lệ.
