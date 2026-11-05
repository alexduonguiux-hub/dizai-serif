# 11 — Spacing và kerning (v0.6)

Code: `tools/construct/spacing.py`. Đầu vào là `out/construct/outlines.json`; đầu ra là `out/construct/spacing.json` (dịch outline `dx`, `advance`) và `out/construct/kerning.json` (class và ngoại lệ). Trang duyệt dùng cả hai khi xếp chữ mẫu.

Theo skill `typeface-construction` §15 và luật S14. Designer 05/11: "làm kerning cho toàn bộ. Dùng skill đang có để làm kerning cho chuẩn".

## Spacing (S14)

- **Đo**: profile trái/phải của mực quét mỗi 5 u, từ outline vector (không dùng raster).
- **Trắng một bên** A = trung bình theo cao độ, trong vùng chữ, của min(khoảng từ cực mực tới mép mực, 40). Độ sâu đo là 40.
  - Vùng chữ: hoa và số 0–700; chữ thường 0–495; dấu câu dùng vùng mực của chính nó.
- **Sidebearing** sb = (sb chuẩn + A chuẩn) − A. Kết quả là nét thẳng rộng hơn nét tròn:

  | Chuẩn | Regular | Bold |
  |---|---|---|
  | H (hoa, số, dấu câu) | 40 | 44 |
  | n (chữ thường) | 32 | 36 |

  Ví dụ Regular (sb trái): H 40, O 31, A 20, n 35, o 28. Dấu câu có sàn 20 mỗi bên.
- **Chữ có dấu, có sừng, Đ, đ**: giữ sidebearing và advance của chữ gốc. Dấu và sừng được phép tràn; kerning chặn va chạm.

## Kerning

- **Class** theo chữ gốc. Ơ, Ư, ơ, ư có class phải riêng, vì sừng đổi viền phải.
- **W** = khe nhỏ nhất giữa hai profile trong vùng chung, chỉ tính ở các cao độ hai chữ cùng có mực.
  - Vùng chung: hoa 0–700; có chữ thường thì 0–495; có dấu câu thì dùng vùng mực của dấu câu.
  - W được so với khe của cặp chuẩn cùng vùng (H H, n n, H n…).
- **kern** = −0.45 · (W − W chuẩn).
  - Chỉ kéo vào; giới hạn −150, riêng cặp có - – — = + × giới hạn −60.
  - Bỏ các giá trị dưới 10, làm tròn 5 về phía rộng.
- **Đã thử và bỏ**: dùng trung bình khoảng trắng thay cho khe nhỏ nhất. Cách đó kéo vào cả AH, AB… vì phần trắng riêng của A, vốn đã do spacing lo, rồi bộ chống va phải nới lại hơn 11.000 cặp.
- **Chặn va chạm**: mọi cặp chữ, số, dấu câu (tính dấu, sừng, ascender, descender) giữ khe mực ≥ 26 trên toàn chiều cao. Cặp vi phạm được nới thành ngoại lệ theo cặp ký tự.

| Cặp | Regular | Bold |
|---|---|---|
| AV | -115 | -125 |
| VA | -125 | -135 |
| AT | -40 | -40 |
| TA | -40 | -40 |
| AY | -95 | -90 |
| LT | -40 | -40 |
| LY | -90 | -90 |
| To | -50 | -55 |
| Ta | -50 | -55 |
| Ty | -50 | -50 |
| Yo | -100 | -95 |
| Va | -55 | -60 |
| Ve | -70 | -75 |
| Wo | -60 | -65 |
| P. | -150 | -145 |
| F. | -100 | -105 |
| r. | -75 | -75 |
| y. | -100 | -95 |
| v. | -100 | -95 |
| "A | -100 | -105 |
| A" | -90 | -100 |
| ko | -50 | -55 |

| | Regular | Bold |
|---|---|---|
| Cặp class | 2611 | 2445 |
| Ngoại lệ chống va | 1597 | 2115 |

- **QA**: khe mực nhỏ nhất của mọi cặp sau kerning ≥ 26 (bảo đảm bằng cách dựng).
- **Cặp có dấu lệch > 12 so với cặp chữ gốc**: Regular khoảng 1300, Bold khoảng 1700. Tất cả là ngoại lệ chống va, tức cặp được nới lên sàn 26 (ví dụ ẩ + Y: dấu chạm tay Y; ư + ?: sừng chạm đầu ?). Theo skill, các cặp này chỉ liệt kê, không phải lỗi.

**Chưa làm:**
- Kiểm theo âm tiết tiếng Việt (phụ âm đầu × vần × thanh).
- tnum cho số.
- cpsp khi set toàn hoa.
- Đưa vào file font (GPOS) khi xuất OTF/TTF.
