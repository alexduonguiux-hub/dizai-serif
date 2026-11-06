# Kiểm tra tính độc đáo của hình glyph (06/11)

Designer: "Kiểm tra xem font có trùng tạo hình glyph với Font khác không".

## Phương pháp (`tools/construct/qa_similarity.py`)

62 glyph A–Z a–z 0–9 của AnNam Serif Regular so với cùng glyph ở từng font tham chiếu: chuẩn hoá chiều cao (cap cho hoa / số, x-height cho thường), canh đường chân, canh giữa ngang, giữ tỉ lệ bề ngang; raster 220 px; chỉ số IoU = mực trùng / mực hợp. Font variable lấy ở wght 400.

Tham chiếu (38 font): serif loe nét / glyphic / chữ khắc — Marcellus, Marcellus SC, Cinzel, Cinzel Decorative, Forum, Federo, Belleza, Tenor Sans, Philosopher, Bellefair, Gilda Display, Italiana, Aboreto, Elsie; serif sách / hiển thị — Cormorant, Cormorant Garamond, EB Garamond, Lora, Spectral, Playfair Display, Crimson Pro, Newsreader, Fraunces, Bodoni Moda, Prata, Rufina, Alice, Junge, Rosarivo, Della Respira, Sorts Mill Goudy, Josefin Slab, Trirong, Taviraj; hệ thống — Liberation Serif, DejaVu Serif, Caladea, FreeSerif.

## Mốc so sánh

| Cặp | IoU TB | glyph ≥ 0.85 |
|---|---|---|
| font độc lập khác designer (Lora ↔ Spectral, Marcellus ↔ Forum, Crimson Pro ↔ EB Garamond, Lora ↔ Caladea…) | 0.57–0.70 | 1–5 |
| cùng gốc / cùng xưởng (Trirong ↔ Taviraj) | 0.78 | 20 |

## Kết quả AnNam Serif

- IoU TB cao nhất: Federo 0.60, Marcellus 0.58, Trirong 0.58, Liberation Serif 0.58 — nằm trong vùng font độc lập; thấp hơn Lora ↔ Spectral (0.70).
- Glyph ≥ 0.90: chỉ I (Federo 0.95, Belleza 0.94) và z (Federo 0.90) — I là thân thẳng loe hai đầu, mọi chữ glyphic loe nét đều trùng ở mức này; chồng hình (`docs/img/similarity-overlay.png`) cho thấy khác ở hình loe, chân bút dẹt, vai.
- Không có font nào trùng nhiều glyph như một bản dẫn xuất.

## Giới hạn

Chỉ so với font mã nguồn mở / có sẵn. Chưa so được với font thương mại cùng dòng (Optima, Friz Quadrata, Albertus, Trajan, Copperplate, Lydian, BT Annam Neue…). Muốn chắc chắn hơn: chạy lại script với file font thương mại (nếu có bản quyền), hoặc dùng dịch vụ so khớp hình chữ (WhatTheFont, Font Squirrel Matcherator) với ảnh chụp chữ mẫu.
