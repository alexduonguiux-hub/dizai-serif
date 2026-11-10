---
name: dizai-serif-qa
description: Checklist QA/QC của Dizai Serif (chữ glyphic loe nét, tương phản theo bút dẹt). Chạy sau mọi thay đổi glyph, luật, dấu, spacing, kerning hoặc build, trước khi gửi cho designer. Dùng kèm dizai-serif-design.
---

> Tên phát hành: **AnNam Serif** (designer 06/11: "AnNam", thêm "Serif" để phân biệt với BT Annam Neue của BeauType); PostScript / file `AnNamSerif`; vendor ID `DZAI` (nên đăng ký Microsoft). Tên dự án / thư mục / skill giữ "dizai-serif". Mỗi lần phát hành: kiểm unique — name ID 3 `version;DZAI;PostScript(-VF)`, PostScript không trùng trong từng định dạng, file gộp tiền tố `AnNamSerifSlnt`.

# Dizai Serif — QA/QC

Skill này lấy từ `type-qa-qc` của DINHTUONG60s. Phần chung (đo chứ không nhìn, chạy ở
mọi weight và trên mọi glyph cùng luật, báo cáo theo thứ tự đạt → nằm sát giới hạn →
đã đổi) giữ nguyên. Các check riêng cho chữ tương phản được thêm vào hoặc thay thế.
Số hiệu luật (S1…) lấy từ `dizai-serif-design`.

## 0. Cách chạy
- Một chỗ sửa là một luật. Gọi tên luật bị vi phạm → sửa trong code dựng → build lại
  mọi weight → chạy lại toàn bộ checklist.
- Chưa có file nguồn: đo trên ảnh bằng `tools/measure_sheet.py` (±3 u). Ghi rõ "đo từ
  ảnh". Không kết luận chắc chắn về nét chéo hay nét tròn từ số đo cắt ngang.
- Việc dài (kerning, QA toàn cặp, build) chạy nền.
- Mỗi glyph đã đổi: render to cạnh glyph tham chiếu (H|N, O|Q, A|V, R|K, 0|O, B|P),
  kèm overlay outline R / M / B. Tự nhìn trước khi gửi.

## 1. Check riêng cho chữ tương phản

### 1.1 Bảng nét (S2, S3)
- Đo mọi thân với V, chéo dày với D, nét mảnh (chéo / và thân M N) với t, nét ngang với
  H, ở từng glyph, từng weight. Đo vuông góc nét, không đo cắt ngang.
- **Một giá trị cho mỗi loại** (±4 u Regular). v0.1 trượt ở hai chỗ:
  - mảnh chéo: X Y 4 = 60–62, các chữ khác 43–50;
  - ngang mảnh: 33 / 36 / 39 / 42 / 46.
- Kiểm logic bút: nét \ dày, nét / mảnh. Liệt kê ngoại lệ chủ ý (Z, U, 2, 7) để không
  bị "sửa" nhầm.
- Tương phản theo weight: in t/V và H/V cho R, M, B. Mọi glyph phải theo cùng một bảng.

### 1.2 Loe (S5)
- Liệt kê mọi đầu nét tự do (thân, chéo, tay) ở mọi glyph và mọi weight. Đo F (vuông
  góc nét) và L. Regular: F 21 ± 3, L 60 ± 6. Đường loe lõm, góc cuối bo đều.
- Không loe ở đỉnh nhọn hay vertex, không loe vào khấc, không loe vượt cap line hoặc
  baseline.
- Render A V W M N H E T cạnh nhau ở cỡ lớn. Loe phải đọc thành một đặc điểm duy nhất.

### 1.3 Vòng và trục (S4)
- Đo góc trục dày (đường nối hai điểm mỏng nhất) của O Q C G D 0 6 9 8: một góc, ±3°.
- Overshoot của mọi chữ tròn bằng nhau. v0.1: O Q +16 / −7, C G +9 / −12 → lỗi.
- Lòng là elip thật, không có đoạn phẳng. Bề ngang C và G so với O theo luật đã duyệt.

### 1.4 Khớp, đỉnh, lòng nhỏ (S7, S8, S13)
- Khớp mỏng hơn nét, góc trong sắc, không bo.
- Lòng nhỏ đo theo đơn vị Regular ở mọi weight: lòng A trên thanh, lòng B trên và dưới,
  lòng P R, lòng 4, 6, 8, 9. Lòng ở Bold không được nhỏ quá mức hệ số K cho phép
  (v0.1 Bold: lòng A gần bít, theo quan sát bằng mắt).
- Nét ngang bụng B D P R dày bằng H suốt nét, chỉ mỏng ở chỗ khớp.
- Một chữ có hai lòng (B, 8, 3): lòng trên nhỏ hơn, cân thị giác.

### 1.5 Đuôi bút (S9)
- Q R K J (và đuôi chữ thường sau này): độ cong ở chỗ đuôi rời bụng hoặc thân liên tục
  G2 (tỉ số độ cong 1.0–1.3).
- Tầm vươn của Regular là sàn cho mọi weight: in tầm vươn R ≤ M ≤ B.
- Đầu đuôi không thành mũi kim: góc mép trong gặp nhát cắt ≥ 25°.
- Đuôi được mảnh dần **chỉ** theo hướng bút. Đo độ dày dọc đuôi: phải đơn điệu, không
  có chỗ eo hay phình.

### 1.6 Số (S12)
- Nét số = 0.95 nét hoa (khi đã duyệt).
- 3 và 5 chung bụng dưới, 6 và 9 chung bụng: so object outline.
- 1 có cờ cùng góc và cùng tầm vươn ở mọi weight.
- Khoảng trắng mỗi bên của số bằng của 0 (±3). Không cặp số nào chạm nhau. v0.1: 7 và 8
  chạm nhau, 0 và 1 cách 11 u → lỗi.

### 1.7 Metrics (S1)
- Cap 700 cho mọi chữ thẳng (v0.1: L M đo được 707 → kiểm nguồn).
- Vertical metrics bao chồng dấu cao nhất (Ẳ Bold) và thấp nhất (ỵ).

### 1.8 Sửa path có sẵn (bài học 04/11, số 2: "Không bo tròn")
- **Không dời tay nắm của điểm góc.** Một góc nhọn chỉ giữ nhọn khi hai tay nắm ở hai phía
  góc giữ nguyên hướng. Muốn đổi độ dày gần góc thì dựng lại đoạn đó.
- Sau khi dời điểm trên đường cong, kiểm tra độ cong: không có chỗ uốn ngược hay gãy. Render
  ×4 vùng đã sửa cạnh bản gốc và tự nhìn.
- Đo lại sau khi sửa. Nếu số đo không đổi đáng kể thì huỷ thay đổi; không giữ một chỉnh sửa
  làm xấu hình mà không đem lại gì.
- Khi Figma tự chuẩn hoá gốc toạ độ path sau mỗi lần ghi, so điểm bằng toạ độ tuyệt đối
  (absoluteTransform), không so bằng toạ độ cục bộ.

## 2. Check giữ nguyên từ `type-qa-qc`
- **Tiến triển weight:** chồng outline R/M/B. Đường cong song song, nhát cắt cùng chỗ,
  góc đầu nét lệch ≤ ±3°. Đuôi không ngắn đi.
- **Bề ngang (R2c):** chiều cao giữ nguyên. Bề ngang mực và advance tăng đơn điệu.
  Lòng mất đi tính theo bội Δ: thẳng ≈ 1.0Δ, tròn ≈ 1.3Δ.
- **Outline:** không có mực nhọn < 25°, không có đoạn < 6 u. Không có bậc chỗ hai phép
  dựng chồng nhau. Phép hợp chồng nhau 3–6 u. Closing r 18 không đổi topology.
- **Retired glyph:** sau mọi lần đổi thiết kế, kiểm mọi ký hiệu, chữ ghép và ordinal.
- **Dấu tiếng Việt:** overlay dấu hoa và dấu thường cùng hệ. Sắc một độ dài. Trên ă mọi
  dấu thanh nằm trên trăng. Khe ≥ 30 / ≥ 36. Phủ đủ 134 chữ. NFD = NFC.
- **Spacing / kerning:** kiểm khoảng trắng trước rồi mới kern. Khe ≥ 26. Cặp có dấu giữ
  khoảng của cặp gốc ±12. Kiểm âm tiết Việt ở ba kiểu viết hoa. Cặp La Mã kinh điển:
  AV AT LT LY TA VA WA AW PA FA RV KO.
- **Phát hành:** OTF và TTF khớp nhau, cmap đủ, version tăng.

## 3. Mẫu báo cáo
1. Đạt (kèm số).
2. Nằm đúng giới hạn (và vì sao không dời được).
3. Đã đổi (luật, số cũ → số mới).
4. Còn mở (chờ designer).
Ghi vào `docs/` kèm version và ngày.

## 4. Check bổ sung v0.6–v0.7 (05–06/11)
- **Ghép cặp master:** `compat_masters.py` phải báo ghép được 324 / 324 (Roman và `DIZAI_OUT=out/construct_italic`). Không ghép → bước xuất font hỏng — KHÔNG commit font khi chưa qua bước này.
- **Số contour hai master bằng nhau** cho mọi glyph; chiều contour giống nhau (chấm i, ä từng ngược chiều → Medium chấm co).
- **QA trên file font** `qa_font.py` (HarfBuzz): variable 400 / 500 / 600 / 700 + 16 bản tĩnh — advance, kerning mọi cặp, NFD = NFC, hộp bao = outline (Italic: nghiêng 10°) → phải 34 / 34.
- **fontbakery check-universal** riêng từng nhóm (variable / ttf / otf): 0 FAIL. Cảnh báo chủ ý: ß 2 contour, U+00AD có glyph, dấu toán khác bề ngang, interpolation gãy nhỏ (8 & ® §), thiếu avar, namecheck.
- **qa_stroke số:** số 4 so với 1 (`STEMFIG`, thân thẳng), không so với 0 (nét tròn) — S23. Ký tự dựng từ số (? ¿ hỏi ← 2, & ← 8) dùng bản GỐC trong `ref/designer_Q.json`: cân lại số không kéo theo ký hiệu đã duyệt.
- **Italic (S26):** đo Italic so với Roman cùng weight bằng độ dày vuông góc (không chỉ diện tích mực — phép nghiêng giữ mực nhưng đổi màu theo hướng nét). Chuẩn: nét chính ±3 %. Bù quang học ở `ital_comp.py`.
- **Module loe (S27):** đoạn loe nhập mép chéo phải liền tiếp tuyến VÀ cong đều (vẽ lược độ cong so với loe V); kiểm cả nút cong ↔ thẳng, không chỉ cong ↔ cong. Nách chéo là MỘT điểm (không mặt phẳng ngắn).
- **Nút gãy trong FONT (S29):** quét nút cong ↔ cong và cong ↔ thẳng 2–12° trên file OTF của cả 8 style (không chỉ outline số thực): làm tròn toạ độ nguyên + nội suy hai master nguyên tạo gãy ở tay nắm ngắn. Bản tĩnh Medium / SemiBold dựng outline từ số thực (`*-snap.ufo`), không dùng instance nội suy.
- **Khấc nêm hẹp (S29):** khe < 6 u × 14 u ở đỉnh nhọn đọc thành vết hở (N) — đỉnh chéo gặp thân là MỘT điểm.
- **Pipeline:** chạy các bước bằng `&&`, không bằng vòng `for … > /dev/null` (S21–S22 `lower/derive.py` lỗi ở x mà không ai thấy).
- **qa_stroke:** dấu giọt / nháy (, ; ‘ ’ ‚ “ ” „ ' " ′ ″) đo "nét chính" bằng đường kính hình tròn nội tiếp lớn nhất (trục giữa của giọt không ổn định).
- **Nét chéo chữ thường:** nét mảnh v w x y k / thân n = nét mảnh / thân V hoa (±5 %).
- **Dấu nặng:** mọi chấm cùng đỉnh −49 (ỵ bên phải đuôi), cùng kích thước dấu chấm câu.
- **Kerning:** sau mỗi thay đổi glyph chạy `qa_kern.py` cả 4 weight: va chạm 0, âm tiết Việt 0 lệch ngoài sàn, kern nhất quán 4 weight.
- **Render to** từng glyph đã đổi ở cả 4 weight (Medium / SemiBold là nội suy — lỗi cấu trúc chỉ lộ ở đây) + chữ chạy Roman và Italic trước khi gửi.
- **File gộp [slnt,wght]:** so với hai file riêng ở 8 vị trí bằng instancer + BoundsPen (đường cong thật, không dùng hộp bao điểm điều khiển): lệch ≤ 1.5 u, diện tích ≤ 0.5 %, advance trùng.
- **Độc đáo hình glyph** (`qa_similarity.py`, `docs/15-kiem-tra-doc-dao.md`): IoU TB với từng font tham chiếu phải trong vùng font độc lập (≤ 0.70); glyph ≥ 0.90 chỉ chấp nhận ở chữ cấu trúc đơn (I, l, i).
- **Đường cong bụng:** độ cong G2 chỉ để chẩn đoán, không phải tiêu chí đạt (designer 06/11 chọn bụng tròn tự nhiên hơn G2). Vector designer gửi phải khớp font (lệch ≤ 0.1 u); đo lại độ dày sống S s sau khi thay vector và báo thay đổi so với bảng nét.
- **Gãy khi nội suy (S18):** mọi nút trơn ở Medium / SemiBold gãy ≤ 2°. Bảng `S18 …` in cuối `build.py` liệt kê glyph đã chỉnh. Còn & @ Š chờ vẽ lại điểm neo. Render to s, ơ, ư, k ở Medium / SemiBold, nhìn mép bụng không phồng.
- **TTF / woff2 tĩnh giữ góc** (designer 06/11 "đuôi cắt chữ S lỗi"): bước bỏ điểm trùng trong `export_font.py` phải giữ điểm on-curve. Cubic có tay nắm 0 ở góc (đuôi cắt S, a, 2, $, &) sinh off-curve trùng góc; bỏ nhầm điểm góc thì góc bo tròn chỉ ở TTF. Render to TTF cạnh OTF các chữ có góc đầu nét trước khi đăng.
- **Thay contour bằng contour chữ gốc phải so HAI CHIỀU** (Đ 06/11: so một chiều làm mất thanh trong lòng). Sau mọi thay đổi ghép cặp: so ảnh mọi glyph với bản trước; glyph khác > 150 px phải nằm trong danh sách cố ý đổi. Bậc thừa < 6 u (dejog) không phải khấc thiết kế.
- **Độ đậm Bold theo loại nét (S21):** đo nét chéo bằng cặp mép thẳng song song (có mực ở giữa). Nét chéo dày Bold = nét Regular × V_B/V_R (±2%), nét chéo mảnh Bold = 0.5 V_B; chữ thường so với n. qa_stroke (một số / chữ, ±10%) không đủ nhạy cho cảm giác "chữ dày chữ mỏng".
