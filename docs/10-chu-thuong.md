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

Designer 04/11: "Bold hơi sai và không đồng bộ về glyph". Bản đầu giữ nguyên bề ngang, chỉ cho lòng co đều 37. Kết quả là lòng a, e bị bóp, chữ đen và chật hơn chữ hoa Bold (chữ hoa Bold rộng ra). Bản hiện tại:

1. **Vòng giãn ngang** quanh tâm của nó, như chữ hoa Bold rộng ra:
   - a, d, b, q, p: +40;
   - e: +36, như C và G.
2. **Thân và vai a giữ nguyên hình**, chỉ trượt theo mép vòng phía nó. Thân dày vào phía lòng: 102 → 139 (+37). Loe phía ngoài giữ nguyên.
3. **Lòng co đều 35 mọi phía**, mép ngoài giữ nguyên. Cộng thêm phần giãn, vách dày thêm khoảng 40, như O và D Bold.
4. **Nét ngang mảnh** +28 (40 → 68):
   - thanh e nở đều hai phía;
   - vai a dày xuống;
   - đầu cắt e dày lên.
5. **Đầu thân nối bụng không có loe phía lòng**, như thân D, B, P chữ hoa. Áp ở cả hai weight, tại các chỗ:
   - chân d, b, a;
   - đỉnh q, p.

   Lý do: loe ở đó thò thành mẩu nhọn cạnh bụng.

| Chữ | Rộng R → B | Mật độ R | Mật độ B | B / R |
|---|---|---|---|---|
| a | 434 → 474 | 0.317 | 0.396 | 1.25 |
| e | 486 → 522 | 0.263 | 0.361 | 1.37 |
| d b q p | 509 → 549 | 0.359 | 0.461 | 1.28 |
| H (hoa) | | 0.387 | 0.491 | 1.27 |
| O (hoa) | | 0.263 | 0.377 | 1.43 |

## Lịch sử e

- **Bản 1**: lòng đứng, có nét chéo.
- **Bản 2**: vòm, thanh ngang, bụng có đầu cắt đứng.
- **Bản 3** (hiện tại): như bản 2, nhưng lòng là elip xoay.
