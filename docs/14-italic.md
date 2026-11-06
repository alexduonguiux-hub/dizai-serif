# Italic I2 — italic thật (06/11)

Designer: "làm italic thật I2"; "giữ a hai tầng như roman".

## Quy trình

`tools/construct/italic.py` (sau build Roman) dựng **thiết kế italic đứng** từ outline Roman của hai master Regular / Bold → `out/construct_italic/outlines.json`; `DIZAI_OUT=out/construct_italic` cho `compat_masters.py` (ghép cặp R / B, nội suy Medium / SemiBold), `spacing.py`, `qa_kern.py`, `qa_weight.py`, `qa_stroke.py`. `export_font.py` lấy nhánh Italic từ thư mục này và **nghiêng 10° khi xuất** (quanh ½ x-height): mọi glyph nghiêng như nhau nên khe giữa hai chữ ở mọi cao độ giữ nguyên — spacing / kerning tính trên bản đứng đúng cho bản nghiêng.

## Luật

| Số | Luật |
|---|---|
| I2.1 | nghiêng 10° (post.italicAngle −10, caret 1000 / 176) |
| I2.2 | chữ thường hẹp ngang 0.94 (nét đứng nhẹ theo — italic gọn và nhẹ hơn roman một bậc; thân n 96 / 120 so với roman 104 / 128) |
| I2.3 | **đuôi ra**: chân phải của i ı l n m h u d = móc chân của t (cùng module), giãn ngang đúng bề dày thân đích (thân t mảnh hơn → mép phải không thụt ở mối nối); i l n m h cắt loe trái chân phải, u d giữ (bụng nhập thân) |
| I2.4 | **a giữ hai tầng như Roman** (chỉ hẹp + nghiêng, không đuôi); a một tầng (`single_a`) giữ trong code để đối chiếu |
| I2.5 | **f có đuôi xuống**: phần trên của f + thân và móc dưới của j, giãn ngang theo bề dày thân f |
| I2.6 | chữ có dấu: chữ gốc italic + dấu của Roman (giữ nguyên hình), dời theo tâm chữ gốc; dấu trên của i dùng ı làm gốc; sừng ư ơ dời theo mép phải ở 0.8 x-height (lấn 3 u vào thân), thanh đ theo mép thân |
| I2.7 | chữ hoa, số, dấu câu, ký hiệu: hình Roman, chỉ nghiêng |

## Sửa trong lúc dựng

- Chiều contour chuẩn theo độ lồng cho mọi glyph italic; `font/compat.py` so chiều bằng diện tích **đường cong lấy mẫu** (diện tích theo điểm neo của contour 2 đoạn cong — chấm i sau đơn giản hoá — bằng 0 → master Bold bị đảo, Medium / SemiBold chấm co lại). Roman build lại: 0 glyph đổi.
- Dấu trên / dưới tách theo dải cao độ (phép trừ boolean làm dấu vỡ mảnh có cạnh chung → R / B khác số contour); chữ có phần dưới đường chân (ỵ) và sừng / thanh đ vẫn dùng phép trừ.

## QA (Italic)

Ghép cặp 324 / 324 · va chạm 0 · âm tiết Việt 0 cặp lệch > 12 ngoài sàn 26 · kerning nhất quán 4 weight · weight đơn điệu 0 lỗi · QA file font (variable 400–700 + 8 bản tĩnh): advance, kerning mọi cặp, NFD = NFC, hộp bao (bản đứng nghiêng 10°) — 34 / 34 đạt (Roman + Italic).

Ghi chú: Tb / Th italic kern +35 / +40 (khe 100 u, roman 65) — theo tỉ số trắng cặp tham chiếu với n italic hẹp hơn.
