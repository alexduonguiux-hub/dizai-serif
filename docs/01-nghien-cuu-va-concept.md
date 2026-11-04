# Dizai Serif — Nghiên cứu và concept (v0.1, 04/11/2026)

Tài liệu đầu tiên của dự án. Phương pháp lấy từ ba skill của dự án Định Tường
(`typeface-construction`, `type-design-principles`, `type-qa-qc`), đã chỉnh cho
một bộ chữ CÓ TƯƠNG PHẢN. Bản chỉnh nằm ở `.claude/skills/dizai-serif-design` và
`.claude/skills/dizai-serif-qa`.

Nguồn: 4 ảnh bản Regular trong `reference/regular/` (hoa A–Z, số 0–9) và 1 ảnh
bản Bold (A–T) gửi trong chat. Bản Bold chưa có file nên chưa đo được.

## 1. Thể loại: chữ loe nét, gốc chữ khắc La Mã

Đo trên bản Regular (cap = 700 u):

| Đặc điểm | Số đo | Kết luận |
|---|---|---|
| Tương phản ngang / đứng | thanh H/E/F 39 / thân 101 = **0.39** | tương phản cao, thuộc nhóm glyphic (0.30–0.40) |
| Logic nét dày / mảnh | A: chân phải 107, chân trái 45 · M: thân trái 45, chéo 108, chéo 47, thân phải 101 · N: thân 45, chéo 106 · V: 109 / 46 | đúng **logic bút dẹt của chữ khắc La Mã**: nét đi từ trên-trái xuống dưới-phải là nét dày |
| Đầu thân | thân 101 loe ra 142 ở chân và đỉnh (+21 mỗi bên) trên ~60 u, đường loe lõm; góc cuối bo nhẹ ~5 u | **loe nét (flare)**, không có chân ngang thật |
| Trục nét tròn | O, Q, 0: chỗ dày ở dưới-trái và trên-phải | **trục nghiêng** (trục nhân văn), không phải trục đứng |
| Tỉ lệ | O 726 · M 672 · A = V = X = Y 667 · H 495 · E = F 374 · S 393 | tỉ lệ **chữ La Mã cổ điển**: O, M, A, V rộng; E, F, L, S hẹp |
| Thanh ngang | A ở 0.25 cap (thấp), H/E/F ở 0.50 cap, P/R khép bụng ở ~0.50 cap | có hơi hướng chữ khắc La Mã |
| Bộ số | cao bằng chữ hoa (700), nét 101–102, 0 là oval (578 so với O 726) | số lining |

**Kết luận:** Dizai Serif là chữ **glyphic / loe nét** (nhóm Incises trong phân loại
Vox-ATypI). Cùng họ với Optima, Albertus và Friz Quadrata, nhưng giữ nhịp dày–mảnh của
chữ khắc Trajan. Đây không phải chữ "serif sách" (không có chân ngang có bracket), cũng
không phải chữ đều nét như DINHTUONG60s.

## 2. Ẩn dụ vật liệu (luật gốc: mọi đặc điểm suy ra từ một ẩn dụ)

Đề xuất: **"đục đá theo nét bút dẹt"**. Bút dẹt (khoảng 30°) quyết định chỗ nào dày
và chỗ nào mảnh. Mũi đục quyết định đầu nét: loe lõm rồi cắt bằng.

Từ ẩn dụ suy ra:

| Bộ phận | Quy tắc suy ra |
|---|---|
| Nét dày / mảnh | theo hướng bút: nét \ dày, nét / mảnh, thân đứng dày, nét ngang mảnh |
| Đầu nét tự do | loe lõm, MỘT hình loe cho mọi thân và mọi chéo |
| Vòng | trục nghiêng (một góc cho O Q C G D 0 6 9 8) |
| Mối nối | nét mảnh mọc ra khỏi nét dày với góc sắc. Ở đỉnh nhọn (A, M, N, V, W) các nét đè lên nhau như vết đục |
| Đuôi (Q, R, K, J) | là nét bút: một đường cong đều, mảnh dần theo hướng bút. Ở bộ này nét **được phép** mảnh dần, khác với DINHTUONG60s |

Những điểm khác hẳn bộ Định Tường nên KHÔNG được áp máy móc:

- Luật "không thu nét" (R5h) và "monoline" của DINHTUONG60s **không áp dụng** ở đây.
  Ở Dizai Serif, độ dày đổi theo hướng bút. Nét chỉ được mảnh dần khi hướng nét
  đổi so với hướng bút; không được mảnh đi một cách tuỳ tiện.
- Hình loe F 7/8/9 trên L 120 của DINHTUONG60s không dùng được. Bộ này loe lớn hơn
  nhiều: khoảng 0.21 V mỗi bên, trên khoảng 0.6 V.

## 3. So với các bộ anh em

| | DINHTUONG60s | Kẻ bảng hiệu | Khắc kẽm | **Dizai Serif** |
|---|---|---|---|---|
| Tương phản | đều (0.83) | đều | 0.30–0.40 | **0.39** |
| Đầu nét | cắt dọc + loe nhỏ 7–9 | cắt ngang | mỏ nêm, chân nêm | **loe lõm 21/60, không chân** |
| Vòng | oval theo hộp, trục đứng | vòng compa | elip / siêu elip | **oval trục nghiêng** |
| Tỉ lệ | đều | đều | đều | **La Mã cổ điển (rộng / hẹp)** |
| Logic nét | không | không | đục khắc | **bút dẹt** |

## 4. Những điểm cần anh/chị duyệt (A/B, có đề xuất)

1. **Bề ngang C, G so với O.** Hiện C/O = 0.74, G/O = 0.74, D/O = 0.77. Ở chữ La Mã
   cổ điển, C, D, G thuộc họ "tròn" và rộng gần bằng O. Skill cũ đặt chuẩn c/o ≈ C/O ≈ 0.82.
   - A: giữ như hiện tại, coi C và G là nửa oval hẹp có chủ ý, rồi ghi thành luật.
   - **B (đề xuất): nới C và G lên khoảng 0.80–0.82 O.** O sẽ đỡ trông "quá to" khi đứng
     cạnh C và G (OCG).
2. **Nét mảnh chéo.** Hiện có các giá trị A 45, M 45/47, N 45, V 46, W 43–46, K 50,
   nhưng X 60–62 và Y 60. **Đề xuất:** đưa về một giá trị mảnh chéo duy nhất (~46). Nếu
   anh/chị muốn X, Y mảnh dày hơn để bù chỗ giao nhau thì ghi thành ngoại lệ có số.
3. **Nét ngang mảnh** đang có 4 giá trị: 33 (đỉnh/đáy bụng B D P R), 36 (giữa B),
   39 (thanh H E F T), 43–46 (thanh Z). **Đề xuất:** một giá trị h = 39. Nét ngang trên
   bụng được mỏng ở chỗ nối thân (khớp mỏng), không mỏng suốt cả nét. Z giữ 43 thì ghi
   lý do.
4. **U.** Hai thân hiện cùng dày 100–103. Chữ La Mã có thân phải mảnh.
   - **A (đề xuất): giữ hai thân dày** cho dễ đọc, ghi thành ngoại lệ chủ ý.
   - B: thân phải mảnh 45 theo logic bút.
5. **Độ dày nét số.** Số đang dày 101–102, bằng chữ hoa. Chuẩn trong skill là 0.95 nét
   hoa (~96). **Đề xuất:** dùng 0.95 để số không đen hơn chữ khi đứng chung.
6. **Chữ thường và dấu tiếng Việt.** Chưa có. Phải viết luật trước khi vẽ (rule book
   mục S10–S12), làm control set n o a e g s + dấu, rồi trình duyệt.
