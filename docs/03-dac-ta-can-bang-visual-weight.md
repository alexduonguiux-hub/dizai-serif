# Dizai Serif — Đặc tả cân bằng visual weight (v0.2, 04/11/2026)

> **Ghi đè:** phần về số (Hf 40, Vf 96, "số đậm hơn 15–20 %") đã bị huỷ. Xem đầu `04-v0.2-thay-doi-trong-figma.md`.

> **Đã duyệt 04/11/2026** (lời designer: "ngang số để 40, vòng tăng lên 106"):
> Hf = 40 cho 2 3 4 5 7; Vr = 106 cho O Q C G D. Các luật S2-Vr và S2-Hf đã chốt.

Ghi đè `02-so-do-va-qa-regular.md` ở các điểm dưới đây. Mọi điểm khác vẫn đúng.

**Sửa số đo v0.1.** Lần trước, nét chéo và nét tròn được đo bằng một đường cắt ngang,
nên số bị phóng to. Lần này đo **vuông góc nét** bằng `tools/perp_thickness.py`
(skeleton + distance transform, ±3 u). Hệ quả:
- Q1 cũ ("X Y mảnh 60") là sai. Nét mảnh thực ra đã đều.
- Nét chéo dày nhẹ hơn thân, không dày hơn như đã ghi.

## 1. Số đo vuông góc (Regular, cap 700)

| Loại nét | Đo được | Đánh giá |
|---|---|---|
| Thân đứng V | 101–104 (E 107) | đều |
| Chéo dày | A 98 · V 97 · W 100 · Z 100 · M 99–104 · Y 88–99 · **X 88–93 · N 85–90 · K chân 83** | **N X K nhẹ hơn rõ** |
| Nét mảnh | A 43 · M 40–47 · N 42–47 · V 41 · W 44 · X 46 · Y 46 · K tay 42 | đều (41–47) |
| Ngang mảnh | H E F 42 · Z 43 · T 38 · **A thanh 36 · B D đỉnh 36 · P R đỉnh 33 · L chân 33** | **5 chữ nhẹ hơn** |
| Vòng (dày nhất) | O 99 · Q 99 · C 101 · G 101 · D 101 · **0: 109** | O nhẹ hơn 0 |
| Sống S | **84–87** | **nhẹ nhất bộ**. Luật: sống phải nặng nhất (≥ 1.0 V) |
| Ngang của SỐ | **2 đáy 91 · 3 nóc 91 · 5 nóc 91 · 4 thanh 91 · 7 nóc ~100** | **gấp đôi ngang của chữ (42)** |
| Thân / chéo số | 1: 102 · 4: 102 · 2 chéo 77–90 · 7 chéo 106 | |

Độ dày nét trung bình (diện tích mực ÷ chiều dài xương):
- chữ hoa thẳng: 61–74; chữ tròn và chéo: 46–64;
- **số: 70–84**.

→ **Số đậm hơn chữ khoảng 15–20 %.** Đây là lỗi visual weight lớn nhất.

## 2. Đặc tả chỉnh (Vr và Hf đã duyệt; các mục khác theo bảng nét)

Bảng nét đích (Regular), đo vuông góc:

| Ký hiệu | Phần | Đích | Ghi chú |
|---|---|---|---|
| V | thân | 101 | |
| Vr | dày nhất của vòng | 106 (1.05 V) | bù quang học cho nét tròn |
| D | chéo dày | 98 | X 95: hai nét giao nhau nên cho phép nhẹ hơn 3 % (ghi ngoại lệ) |
| t | mảnh (chéo, thân M N) | 44 | |
| H | ngang mảnh | 42 | chỉ mỏng xuống ~36 ở đúng chỗ khớp với thân |
| Sp | sống S | 104 (1.03 V) | |
| Vf | thân và vòng số | 0.95 × chữ: thân 96, vòng 101 | |
| Hf | ngang của số | 0.95 × H: 40 | áp cho 2 3 4 5 7. Thay đổi mạnh nhất, xem mục 3 |

Danh sách chỉnh theo glyph:

| Glyph | Hiện tại → Đích | Luật |
|---|---|---|
| N | chéo 85–90 → 98 | D |
| K | chân 83 → 98 | D |
| X | chéo 88–93 → 95 | D (ngoại lệ X) |
| Y | chéo trái 88 → 98 | D |
| O Q | 99 → 106 | Vr |
| C G D | 101 → 106 | Vr |
| S | sống 85 → 104, bụng dưới giữ lớn hơn bụng trên | Sp |
| A | thanh 36 → 42 | H |
| B D P R | đỉnh/đáy bụng 33–36 → 42, mỏng ở khớp | H |
| L | chân 33 → 42 | H |
| T | tay 38 → 42 | H |
| 0 | 109 → 101 | Vf |
| 1 4 | thân 102 → 96 | Vf |
| 6 8 9 3 5 | vòng ~100–104 → 101 | Vf |
| 2 3 4 5 7 | ngang 91–100 → 40 | Hf |

Kèm theo:
- **Overshoot** O Q (+16 / −7) và C G (+9 / −12) đưa về một giá trị **+10 / −10**.
- **Cap height** L M 707 đưa về 700 (nếu nguồn cũng lệch).
- **Spacing số:** mỗi bên bằng khoảng trắng của 0. 7|8 và 0|1 phải có khe ≥ 26.

Bản Bold: dùng cùng các tỉ lệ trên với bảng nét Bold, sau khi đo được ảnh hoặc nguồn
Bold. Lòng A trên thanh giữ chiều cao tính theo đơn vị Regular.

## 3. Hai điểm đã quyết (giữ lại để tham khảo lý do)

1. **Nét ngang của số (91 → 40).** Ngang dày làm 2, 3, 5, 7 có dáng đậm, kiểu
   "poster". Đưa về 40 thì số cùng màu với chữ, nhưng dáng số đổi khá nhiều.
   - Phương án trung gian: 60 (≈ 1.4 H).
   - Phương án đề xuất: 40, kèm một bộ số `.ss01` giữ ngang dày cho tiêu đề.
2. **Vòng 106.** Theo nguyên lý, nét tròn dày hơn thân 4–6 % để trông bằng thân.
   Ở bộ này O cùng màu với H thì O 99 trông nhẹ hơn. Nếu anh/chị thấy O đang vừa mắt
   thì giữ 101.
