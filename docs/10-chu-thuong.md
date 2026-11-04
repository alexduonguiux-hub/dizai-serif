# 10 — Chữ thường (v0.5, đang dựng)

Nguồn: bản vẽ designer, Figma frame `2112:126` (cập nhật 04/11): a, e, d, b, q, p.
- Code: `tools/construct/lower/src_lower.py` (hình gốc) và `tools/construct/lower/lower.py` (đổi đơn vị, Bold, chốt đường vượt).
- Kết quả: `lower/lower.json`, được `ref/make_ref.py` gộp vào `ref_glyphs.json`.

## S10 — Lưới và nét

| | u | Figma px |
|---|---|---|
| x-height | 495 | 192 |
| Vượt trên (tròn) | 503.4 | 189 |
| Vượt dưới (tròn) | −11.3 | 371 |
| Đỉnh thân ascender (d, b) | 698.6 ≈ cap | 120 |
| Chân thân descender (q, p) | −200.8 | 438 |

- **Thân chữ thường = V chữ hoa** (36 px = 102 u; Bold 139).
  - Designer 04/11: "đồng bộ độ dày của các chữ thường với chữ hoa".
  - Thay luật cũ "v ≈ 0.9 V". Bản a, e trước đó được làm mỏng còn 92; nay bỏ, Regular giữ đúng bản vẽ.
- **Vòng trục nghiêng như O**: lòng của a, e, d, b, q, p là elip xoay, dày ở dưới-trái và trên-phải.
- **d b q p dùng chung một khối bụng và một khối thân**: d là bản gốc, b lật ngang, q lật dọc, p xoay 180°.
  - Thân có loe ở hai đầu, như chân a.
- **Loe chân thân**: theo chân a của designer, dài 70, chìa 22.6 mỗi bên.
- Chỉ chốt cực trị tròn vào đường vượt (uốn mềm cục bộ) và dọn nút (`tidy`). Thân vươn lên ascender hoặc xuống descender không bị kéo.

## Bold — cùng luật với chữ hoa (docs/08)

- Mép ngoài giữ nguyên, mực nở vào phía lòng.
- **Thân** 102 → 139 (+37): mép phía lòng dời vào 37. Loe phía lòng trượt theo, giữ nguyên hình.
- **Vòng, bụng**: lòng co đều 37 mọi phía, kể cả chỗ mảnh, như O ("lòng co đều ~38 mỗi phía").
- **Nét ngang mảnh** +28 (40 → 68, như thanh và tay E, H, L):
  - thanh e nở đều hai phía;
  - vai a dày xuống;
  - đầu cắt e dày lên.

Mật độ mực (mực ÷ ((rộng + 80) × 700)):

| Chữ | Regular | Bold | Bold / Regular |
|---|---|---|---|
| a | 0.318 | 0.408 | 1.28 |
| e | 0.263 | 0.363 | 1.38 |
| d b q p | 0.360 | 0.473 | 1.31 |
| H (hoa) | 0.387 | 0.491 | 1.27 |
| O (hoa) | 0.263 | 0.377 | 1.43 |

Tỉ lệ của chữ thường nằm trong khoảng của chữ hoa (1.26–1.43).

## Lịch sử e

- **Bản 1**: lòng đứng, có nét chéo.
- **Bản 2**: vòm, thanh ngang, bụng có đầu cắt đứng.
- **Bản 3** (hiện tại): như bản 2, nhưng lòng là elip xoay.
