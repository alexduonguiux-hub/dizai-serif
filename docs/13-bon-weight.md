# 13 · Bốn weight: Regular · Medium · SemiBold · Bold (v0.5)

Yêu cầu của designer ngày 05/11: "thêm 2 weight medium và semi bold". Hai lựa chọn đã duyệt:
- **Tự sinh toàn bộ.** Designer không cần vẽ thêm.
- **Bậc đều theo độ dày nét.** Medium = 1/3 và SemiBold = 2/3 quãng Regular → Bold.

## Bảng weight (`tools/construct/weights.py`)
| Weight | t | usWeightClass | Nét thân thường |
|---|---|---|---|
| Regular | 0 | 400 | 101.8 |
| Medium | 1/3 | 500 | 109.4 |
| SemiBold | 2/3 | 600 | 116.9 |
| Bold | 1 | 700 | 124.5 |

- `lerp_w(d)` nhận bảng `{'Regular': x, 'Bold': y}` và thêm Medium / SemiBold bằng nội suy. Hàm này nội suy cả dict / tuple lồng nhau.
- Giá trị bool hoặc chuỗi lấy theo master gần hơn.

## Ba nguồn hình
1. **Chữ hoa + số (bản vẽ designer):** nội suy ĐIỂM giữa hai bản vẽ Regular / Bold (`ref/interp.py` → `ref/designer_M.json`, src `interp`).
   - Ghép contour theo tâm và kích thước hộp bao, để không nhầm lòng với viền ngoài (lỗi số 0 ở bản đầu).
   - Căn điểm neo bằng quy hoạch động vòng. Khi một bên có thừa điểm neo, chia đôi đoạn dài nhất ở bên kia. Đoạn thẳng đổi thành cubic.
   - Chỗ nối trơn ở CẢ HAI master (< 4°) được ép liền tiếp tuyến (G1), vì nội suy tuyến tính có thể sinh gãy nhỏ.
   - Glyph nội suy không qua bước tidy mạnh. Tidy mạnh từng xoá mực ở N Medium.
2. **Chữ thường, dấu, dấu câu, ký hiệu (dựng theo luật):**
   - Mọi tham số số học nội suy bằng `lerp_w`: W, N_OFF, ARCH_*, S_SX, S_D, CAP_D, LV, HOOK_S / HOOK_T / HOOK_VEC…
   - Phần "Bold thêm vào" (B_STEM, B_BAR, B_THIN, B_JOIN, B_KG…) nhân với t (`lower.set_weight(w)`).
   - Các nhánh `if w == 'Bold'` trước đây đổi thành nội suy.
3. **Ký tự ghép** (Æ œ ß £ § þ µ ð…): dựng lại từ module của chính weight đó.

## Spacing / kerning
- `spacing.py` chạy cho cả 4 weight. SB_REF và SPACE được nội suy (space: Regular 230, Bold 245).
- Kerning tính riêng từng weight bằng cùng phương pháp min-gap.

| | Regular | Medium | SemiBold | Bold |
|---|---|---|---|---|
| Class / ngoại lệ | 4270 / 1823 | 4184 / 2060 | 4103 / 2282 | 3974 / 2407 |
| A · va chạm < 26 | 0 | 0 | 0 | 0 |
| C · cặp âm tiết Việt ≤ 12 hoặc do sàn | 5202 / 5214 | 5202 / 5214 | 5202 / 5214 | 5202 / 5214 |
| E · cặp gốc quá sát | 0 | 0 | 0 | 0 |

12 cặp lệch còn lại trong mục C giống nhau ở cả 4 weight: đó là các cặp sừng ư / ơ, đã chốt "giữ ư như cũ".

## QA bổ sung
- `qa_cover.py`: đủ 312 ký tự × 4 weight, xuất không lỗi.
- `qa_weight.py`: kiểm 324 ký tự.
  - Diện tích mực tăng NGHIÊM NGẶT R < M < SB < B.
  - Bề rộng mực và advance không giảm.
  - Bước đều: tỉ lệ hai bước liền nhau trong khoảng 0.6–1.6.
  - Kết quả: 0 lỗi.
- `qa_outline.py`: với glyph nội suy, góc được chấp nhận khi nằm giữa góc của hai master (±2°). Còn lại: điểm thẳng hàng ở A Medium và V SemiBold (vô hại), cùng hai góc cắt đã biết ở c và e Bold.
- `qa_kern.py`: chạy cho 4 weight.
- Trong quá trình làm, cặp ngoặc `{ }` từng bị mất ở các bản preview trước do mất dòng gán; đã khôi phục. `qa_cover` ra đời để bắt lỗi kiểu này.

## Việc sau
- Xuất OTF / TTF:
  - name ID 16 / 17 cho Medium và SemiBold;
  - GPOS kern và mark;
  - usWin bao Ẳ Bold 1051.
- Thêm tnum.
- Khi xuất variable font: master chữ hoa đã tương thích điểm sau bước căn của `interp.py`.

## Sửa sau khi có 4 weight (05/11)
- **ß, "vẫn dư nét dưới bụng":** lòng vòng dưới lệch trái (thành trái 0.35, thành phải 0.92 thân), nên đỉnh lòng ở `cxi = cxu − 0.285·thân`, không phải ở `cxu`. Trước đây eo và vòng dưới cắt ở `cxu`, để lại một bậc nhỏ dưới bụng. Nay cắt ở `cxi`: đáy eo chạy ngang rồi vào đúng tiếp tuyến ngang ở đỉnh lòng.
- **ß, "glyph dưới bị dính":** đầu cắt dưới-trái của vòng dưới trước chỉ cách mép loe chân thân 25 (Regular) và 8 (Bold). Nay cách đúng 50 ở mọi weight, theo luật khe nhỏ cố định theo Regular.
- **g Medium → Bold, "lỗi so với g Regular":**
  - Lòng bụng trên và lòng vòng dưới trước bị thay bằng một elip khớp gần đúng, làm mất hình lòng của bản vẽ (góc dưới-phải nặng ngay từ Medium). Nay lòng Bold = chính lòng Regular, thu nhỏ quanh tâm theo cùng hệ số `B_KG['g']`.
  - Nét nối và tai g trước được nở bằng stroke + boolean, sinh điểm thừa và bậc ở chỗ nối. Nay dùng `offset_path` (dời song song từng đoạn), giữ đúng số điểm của bản vẽ.
- **Æ, "lỗi glyph góc trái":**
  - Lỗi: đỉnh A (vượt lên 712) nhô trên thanh E, và loe trái đầu thân E chìa ra ngoài nét chéo.
  - Sửa: cắt cả khối ở mặt trên thanh E (cap 700). Phần trên 400 cắt theo mép ngoài nét chéo trái của A kéo dài, nên góc trên-trái là một góc nhọn ở đường cap.
- **Æ, "lỗi vòng khuyết":**
  - Lỗi: đỉnh lòng A nằm trái thân E, để lại một đoạn xiên ngắn từ đỉnh lòng xuống thân.
  - Sửa: lòng dựng lại thành tam giác giới hạn bởi mép trong nét chéo trái, mép trái thân E và mặt trên thanh A. Lòng có một đỉnh nhọn ở thân.

## QA độ dày nét toàn bộ glyph (designer 05/11: "đồng bộ hết độ dày các glyph", "đảm bảo không glyph nào lỗi nét")

### Công cụ: `tools/construct/qa_stroke.py`
- Đo bề dày theo trục giữa (medial axis) trên ảnh raster 0.5 px/u.
- Tỉa nhánh vào góc loe và đầu nét; bỏ vùng khớp.
- Các phép kiểm:
  - Chữ / số gốc: nét chính so với H / n / 0, lệch tối đa ±10 %.
  - Ký hiệu: trong ±10 % trung vị nhóm cùng luật. Bốn nhóm: gạch / toán, ngoặc, ký hiệu chữ, nháy thẳng.
  - Chéo weight: nét chính tăng R → M → SB → B, và tỉ lệ B/R khớp nhóm.

### Đã sửa
| Glyph | Trước | Sau |
|---|---|---|
| w | hai nét \ mảnh hơn v 11 % | dùng chung `thicken` với v x z (hàm mở rộng cho 4 mép) |
| e Medium → Bold | nhẹ hơn n tới 12 % | lòng co như o (`B_KG['e']`) |
| ~ ≈ | nét 116 / 90, gấp đôi nhóm toán (60) | cùng đường sin của dấu ngã, vẽ lại bằng bút nhóm toán, nét 0.60 V |
| – — | 0.9 × gạch nối | dày bằng gạch nối |
| { } | thân 0.70 V | 0.85 V, như ( ) [ ] |
| § | nét 66 (0.65 V) | nét 0.85 V (90), cùng nhóm ngoặc |
| vòng ̊ (Å å) | 0.34 V, mảnh hơn mọi dấu ~30 % | 0.66 N dấu, bằng đáy trăng |

### Móc dưới (U+0327, Ç ç) vẽ lại
Designer: "đuôi móc không giống các font cùng dòng".
- Cổ đứng mảnh.
- ¾ vòng elip (ering4): cong sang phải rồi về trái, mở hẳn về trái.
- Thành phải 0.62 thân thường; trên / đáy là nét mảnh.
- Đuôi phẳng mặt trên, cắt đứng thẳng hàng mép trái cổ.

### Còn lại, đã kiểm tay (không phải lỗi)
- 2 3 5 8: tương phản theo bản vẽ / luật số của designer. Đo trực tiếp thì thành bụng 3 5 Bold vẫn dày lên.
- Æ Bold, ‹ › Bold, ! ¡ ' “ ;: lệch do thước đo trên glyph nhỏ hoặc hình giọt. Đo trực tiếp thì thân / diện tích tăng đều.
