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

## Quyết định 06/11: Italic = Roman nghiêng 10°

Designer: "thử giữ nguyên bản các glyph rồi làm italic thử" → "bạn nên giữ lại glyph gốc cho cả chữ hoa". Italic xuất từ glyph Roman (chữ thường, chữ hoa, số, dấu) **nguyên vẹn**, chỉ nghiêng 10° quanh ½ x-height; spacing / kerning dùng chung Roman. `italic.py` giữ các luật I2 sau cờ `LOWER_I2 = False` (chữ thường: đuôi ra, f, v w y, nét vào, chân gọn) và `CAPS_COND = False` (chữ hoa hẹp 0.94) để thử lại khi cần. QA file font 34 / 34.

## Kiểm tra toàn bộ glyph Italic (06/11)

Designer: "kiểm tra lại toàn bộ glyph italic có lỗi không". Ba lớp:

1. **QA trên file font** (`qa_font.py`, HarfBuzz): variable 400–700 + 16 bản tĩnh — advance, kerning mọi cặp, NFD = NFC, hộp bao glyph = outline nghiêng 10°: 34 / 34 đạt.
2. **fontbakery check-universal** (variable, TTF, OTF):
   - Lỗi thật đã sửa:
     - **{ }**: hai nửa elip ở mũi chỉ chạm nhau MỘT điểm → 2 contour, mũi thắt. Nay có khối nối 2 × 0.16 thân, rộng 0.3 thân → liền khối, mũi cắt đứng (Roman và Italic).
     - **'2' Bold TTF**: đoạn cong ngắn bị làm tròn về cùng một điểm sau cu2qu → bỏ điểm trùng liên tiếp khi hậu xử lý TTF; khi vẽ UFO bỏ đoạn độ dài 0.
     - File: TTF thêm `prep` smart dropout; bỏ bảng tên Mac; STAT (wght + ital) cho cả bản tĩnh, mỗi trục một giá trị.
   - Còn lại là chủ ý / không áp dụng:
     - ß 2 contour (bụng trên có lòng kín);
     - U+00AD có glyph (gạch mềm hiển thị khi ngắt dòng);
     - dấu toán khác bề ngang (+ = ≠ ¬ chưa đồng bề ngang — có thể làm khi cần);
     - interpolation_issues 8 & ® § (gãy nhỏ trong nội suy — kiểm bằng mắt ở Medium / SemiBold không thấy);
     - thiếu avar (không bắt buộc);
     - namecheck (cần mạng).
3. **Soát bằng mắt** toàn bộ 324 glyph Italic Regular / Bold.

## File variable gộp Roman + Italic (06/11)

Designer: "italic không kết hợp trong variable luôn được hả". Thêm `fonts/variable/DizaiSerif[slnt,wght].ttf`: trục **wght** 400–700 + **slnt** 0 … −10°, 4 master (Regular / Bold × đứng / nghiêng — cùng cấu trúc vì Italic = Roman nghiêng 10°), 8 instance (Regular … Bold Italic), STAT wght + slnt. Nghiêng liên tục 0 … 10°. Giữ hai file `DizaiSerif[wght].ttf` + `DizaiSerif-Italic[wght].ttf` cho ứng dụng chỉ nhận nút in nghiêng qua file Italic riêng (Word, Office).

Kiểm: so file gộp với hai file riêng ở 8 vị trí (4 weight × đứng / nghiêng), 2608 lần — hộp bao đường cong lệch tối đa 0.51 u (khác nhau do đổi sang đường cong bậc hai qua 4 master), diện tích < 0.5 %, advance / kerning trùng. fontbakery: 0 lỗi glyph; 1 FAIL STAT_strings (quy ước Google Fonts: nhãn trục slnt không dùng chữ "Italic").

Preview mục "Font variable" dùng file gộp: thanh trượt wght + nghiêng (slnt), nút Roman / Italic.

## Đổi tên bộ chữ: AnNam (06/11)

Designer: "Đổi tên Font thành AnNam". Tên họ (name ID 1 / 16) "AnNam", tên PostScript `AnNam-Regular` … `AnNam-BoldItalic`, file `AnNam[wght].ttf`, `AnNam-Italic[wght].ttf`, `AnNam[slnt,wght].ttf`, `fonts/otf|ttf/AnNam-*.{otf,ttf}`. Bản quyền / designer giữ "Dizai Studio". Preview: tiêu đề và mast "AnNam". Tên dự án, repo, thư mục, skill giữ "dizai-serif".

## Kiểm tính unique (06/11)

- **Trong gói:** mã định danh (name ID 3) dạng `0.900;<vendor>;<PostScript>` (+ `-VF` cho variable), tên PostScript, tên đầy đủ, (họ, kiểu), (weight, italic) — không trùng trong từng định dạng. Đã sửa: file gộp `AnNam[slnt,wght].ttf` từng trùng tên PostScript / mã định danh `AnNam-Regular` với `AnNam[wght].ttf` → nay tiền tố `AnNamSlnt` (name ID 25).
- **Vendor ID** (OS/2 achVendID) chưa có — đang ghi `NONE` trong mã định danh; cần chọn mã 4 ký tự và (nên) đăng ký với Microsoft.
- **Tên trên thị trường:** đã có họ thương mại **BT Annam Neue** (BeauType, Duong Nguyen — chữ Việt, cảm hứng bút dẹt và mái Hoàng thành Huế, có Roman + Italic; theo KREATIV phát triển từ một font "Annam" gốc). Tên "AnNam" dễ nhầm — chờ designer quyết định giữ hay đổi.
