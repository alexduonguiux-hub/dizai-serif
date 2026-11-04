# Dizai Serif — Số đo và QA bản Regular từ ảnh (v0.1, 04/11/2026)

Đo bằng `tools/measure_sheet.py` trên `reference/regular/*`. Số đo đã quy về
cap = 700 u. Sai số ±3 u (1 px ảnh). Các số này chỉ để **chẩn đoán**. Số chính thức
phải đo lại trên outline khi có file nguồn (.glyphs, .ufo hoặc Figma vector).

## 1. Metrics

| | Giá trị | Ghi chú |
|---|---|---|
| Cap height | 700 | nét thẳng ở ảnh 1 và 3 nằm đúng đường kẻ |
| Overshoot trên / dưới, C G (ảnh 1) | +9 / −12 | |
| Overshoot O Q (ảnh 2) | +16 / −7 | **lệch với C G**: trên lớn gấp đôi, dưới nhỏ hơn. Cần kiểm trong nguồn |
| Overshoot S, U | +8 / −14 | |
| Đỉnh nhọn A, N | +9 / +16 | |
| L, M (ảnh 2) | đỉnh 707 | **cao hơn P R (700) khoảng 7 u**. Có thể do ảnh xuất, có thể là lỗi cap height thật |
| Số | 700, tròn 711 / −11 | |

## 2. Bảng nét đo được (Regular)

| Phần | Giá trị | Glyph |
|---|---|---|
| Thân đứng V | 100–104 | H I E F L P R T B D U, 1: 102, 4: 102 |
| Chéo dày | 106–114 | A 107, M 108, N 106, V 109, W 106–109, X 111–114, Y 111, Z 111–114, 7: 113 |
| Chéo mảnh | 43–50, **60–62** | A 45, M 47, V 46, W 43–46, K 50 · X 60–62, Y 60, 4: 62 |
| Thân mảnh (logic bút) | 45 | M thân trái, N hai thân |
| Ngang mảnh | **33 / 36 / 39 / 42 / 43–46** | B D P R đỉnh/đáy 33 · B giữa 36 · H E F T 38–39 · E F tay trên 42 · Z 43–46 |
| Đỉnh / đáy vòng | O 54–57, 0: 60, C 42–44, G 39–44 | phải đo vuông góc nét mới so được |
| Loe thân | 101 → 142 ở mép (+21 mỗi bên), dài ~60 u, đường lõm | I, H, E giống nhau, đối xứng trên/dưới |

**Tỉ lệ:** chéo dày / thân = 1.06–1.13 (chuẩn skill 0.87–0.92 dùng cho chữ đều nét;
với chữ La Mã, chéo dày hơn thân là bình thường). Ngang / thân = 0.39.

## 3. Bề ngang mực (Regular, u)

| A 667 | B 472 | C 537 | D 558 | E 374 | F 374 | G 540 | H 495 | I 145 |
|---|---|---|---|---|---|---|---|---|
| **J 303** | **K 498** | **L 408** | **M 672** | **N 497** | **O 726** | **P 474** | **Q 759** | **R 526** |
| **S 393** | **T 396** | **U 494** | **V 667** | **W 776** | **X 667** | **Y 667** | **Z 464** | |

Số: 0 578 · 1 198 · 2 451 · 3 448 · 4 530 · 5 448 · 6 527 · 9 527 (7 và 8 dính nhau trong ảnh).

## 4. Kết quả QA (theo `dizai-serif-qa`)

### Đạt
- Cap height 700 đều trên ảnh 1 và 3. Thân đứng đều 100–104 ở mọi chữ thẳng.
- Hình loe giống nhau ở I, H, E (+21 trên ~60 u, lệch ≤ 3 u), đối xứng trên/dưới.
- Logic dày–mảnh theo bút dẹt nhất quán ở A M N V W K.
- Có module dùng chung: A = V = X = Y = 667 bề ngang. 3 và 5 trùng bụng dưới
  (số đo ngang ở 25% và 50% giống hệt). 6 và 9 cùng bề ngang 527.

### Lỗi / nghi lỗi (ghi kèm luật bị vi phạm)
| # | Vấn đề | Luật | Đề xuất |
|---|---|---|---|
| Q1 | Mảnh chéo X Y 4 = 60–62 khác mảnh chéo còn lại 43–50 | S2 (một bảng nét) | đưa về một giá trị, hoặc ghi ngoại lệ |
| Q2 | Có 4–5 giá trị nét ngang mảnh (33–46) | S2 | một giá trị h; chỉ khớp được mỏng |
| Q3 | Overshoot O/Q (+16 / −7) khác C/G (+9 / −12) | S1 | một overshoot cho mọi chữ tròn |
| Q4 | L M cao 707, P R cao 700 | S1 | kiểm lại trong nguồn |
| Q5 | **7 và 8 chạm nhau**. 0 và 1 chỉ cách ~11 u | S14 (khe mực ≥ 26) | chỉnh sidebearing số theo luật khoảng trắng của 0 |
| Q6 | C/O = 0.74 trong khi D/O = 0.77 | S4 | chờ quyết định ở concept mục 4.1 |
| Q7 | Số dày bằng chữ hoa (101–102) | S2 (số 0.95) | chờ quyết định ở concept mục 4.5 |
| Q8 | Nét ngang bụng B D P R (33) mảnh hơn thanh H (39) suốt cả nét, không chỉ ở khớp | S2 / S7 | dày lên 39, chỉ mỏng ở chỗ khớp |

### Bản Bold (ảnh trong chat, nhận xét bằng mắt, CHƯA ĐO)
Cần file ảnh (hoặc tốt hơn: file nguồn) đặt vào `reference/bold/` để đo. Nhìn bằng mắt:
- **A Bold:** lòng tam giác trên thanh rất nhỏ. Thanh A vẫn đặt ở vị trí tương đối của
  Regular nên lòng bị nét dày ăn mất. Luật S13: lòng tính theo đơn vị Regular. Nâng
  thanh hoặc giữ chiều cao lòng cố định.
- **M, N Bold:** nét mảnh gần như không dày thêm, trong khi nét dày tăng nhiều. Cần đo
  tỉ lệ mảnh/dày R → B: tương phản phải giữ đều hoặc tăng nhẹ có chủ ý, không được tăng
  ngẫu nhiên giữa các chữ.
- **G, J, K, R, Q Bold:** cấu trúc giống Regular, đúng nguyên tắc "một khung xương".
  Cần chồng outline R/B để kiểm đuôi Q, chân R, chân K: đuôi không được ngắn đi ở Bold.
- **B, P, R Bold:** lòng trên nhỏ. Kiểm lòng mất đi tính theo Δ nét (S13).
- Cần đo bề ngang từng chữ: mọi chữ Bold phải rộng hơn Regular (bảng K của R2c).

## 5. Việc tiếp theo
1. Anh/chị duyệt 6 điểm ở concept mục 4.
2. Gửi file nguồn (hoặc ảnh Bold) để đo chính xác. Chạy lại QA ở cả hai weight.
3. Chốt rule book v0.2 bằng số. Sửa Q1–Q8 bằng luật. Viết luật chữ thường và dấu
   rồi làm control set.
