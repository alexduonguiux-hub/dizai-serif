# Dizai Serif v0.2 — Bản dựng & Preview (04/11/2026)

Trang Figma: **"v0.2 — Bản dựng & Preview (Claude)"** (page 2032:2). Nguồn là các glyph trên
trang "Design v0.2 — cân bằng (Claude)". Mọi thứ trên trang là bản sao, nên khi sửa glyph
nguồn phải dựng lại trang này.

## Bản dựng (56 ô)
Gồm chữ hoa Regular A–Z, bộ số 0–9 và chữ hoa Bold A–T.

Mỗi ô có:
- cap line và baseline (xám), overshoot ±10 px (nét chấm);
- glyph tô xám;
- các hình dựng gốc tách từ chính cây boolean của glyph: **đỏ** là hình cộng; **xanh nét đứt** là lòng hoặc phần cắt (con thứ 2 trở đi của Subtract, Exclude, Intersect);
- nhãn bề ngang mực theo u.

**(Đã xử lý, xem mục cuối)** Trước đây E, F, S, Z (Regular) và E, F, S (Bold) đã bị gộp (flatten). Các ô này
chỉ có viền path. Theo luật "guide là chính phép dựng", nên dựng lại các chữ này từ hình
gốc (thân, tay, loe, vòng) trước khi mở rộng bộ chữ.

## Preview
- Glyph xếp ở 50 %, canh theo baseline, mỗi bên chừa 40 u. Đây là spacing tạm, chưa kerning.
- Các dòng: bảng chữ Regular và Bold, bộ số, các từ (DIZAI SERIF, SAIGON 1975, HAMBURGEFONSTIV, VAN HOA QUOC NGU 2026, SAIGON HOA PHO, BIEN HOA DAT GIA).
- Dòng kiểm màu: HOH0H1…H9H, OXO VAV AWA LYL TYT, HOHOHMHNHRHSHTH (Bold).
- Nhận xét: màu chữ và số đều nhau trong dòng HOH0…H9H. Các cặp LY, TY, AV, AW còn
  thưa vì chưa kerning, sẽ xử lý ở bước spacing/kerning.

## Dựng lại E F S Z từ hình gốc (04/11)
Thay các path đã gộp bằng Union của các phần dựng, mỗi phần là một vector có tên:
- **E:** Thân · Loe trên-trái · Loe dưới-trái · Tay trên · Mỏ tay trên · Tay giữa · Tay dưới · Mỏ tay dưới.
  - Loe dùng đúng đường cong loe của D, B.
  - Mỏ: nhô 19 px trên đoạn 33 px.
  - Tay giữa có đầu cắt xiên.
- **F:** như E, không có tay dưới; chân loe cả hai bên (Loe chân).
- **Z:** Thanh trên + mỏ · Thanh dưới + mỏ · Chéo (dải hai mép song song, chồng 6 px vào mỗi thanh).
- **S:** chia tại hai cặp điểm đối nhau trên hai mép nét (cực trái của vòng trên, cực phải của vòng dưới), thành Vòng trên + đầu nét trên · Sống · Vòng dưới + đầu nét dưới. Các đoạn cong giữ nguyên từ path gốc.

Áp cho E, F, S, Z (Regular) và E, F, S (Bold). Các mảnh chồng nhau để phép hợp không có cạnh trùng khít.

**Kiểm tra:**
- Khung bao trùng khít bản cũ (lệch 0).
- Diện tích mực bằng nhau: E 13016/13016, S 13380/13380, Z 14046/14045.
- Chỉ vài pixel ở mép ghép lệch ≤ 32/255 độ xám, mắt không thấy được.
- Các ô bản dựng tương ứng đã dựng lại.

**Lệch phát hiện khi tách phần (giữ nguyên, chờ designer quyết):**
- **F Bold:** tay trên dày 14 px (mỏ sâu 33), trong khi E Bold và T Bold dày 24 px (mỏ sâu 43).
- **Z Regular:** thanh trên và dưới dày 16 px, trong khi H chuẩn là 14.
