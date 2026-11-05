# 13 · Bốn weight: Regular · Medium · SemiBold · Bold (v0.5)

Yêu cầu của designer ngày 05/11: "thêm 2 weight medium và semi bold". Hai lựa chọn đã duyệt:
- **Tự sinh toàn bộ.** Designer không cần vẽ thêm.
- **Bậc đều theo độ dày nét.** Medium = 1/3 và SemiBold = 2/3 quãng Regular → Bold.

## Bảng weight (`tools/construct/weights.py`)
| Weight | t | usWeightClass | Nét thân thường |
|---|---|---|---|
| Regular | 0 | 400 | 101.8 |
| Medium | 1/3 | 500 | 109.3 |
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
