# 10 — Chữ thường (v0.5, đang dựng)

Nguồn: bản vẽ designer, Figma frame `2112:126` (cập nhật 04/11): a, e, d, b, q, p, g (hai tầng), **a Bold (mẫu)**.
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
- **Vòng trục nghiêng như O**: lòng của a, e, d, b, q, p, g là elip xoay, dày ở dưới-trái và trên-phải.
- **g hai tầng**: bụng trên (elip 144 × 134 px), vòng dưới (144 × 88 px), cổ nối, tai. Đáy vòng dưới ở −198 (đường descender).
- **d b q p dùng chung một khối bụng và một khối thân**: d là bản gốc, b lật ngang, q lật dọc, p xoay 180°.
  - Thân có loe ở hai đầu, như chân a.
- **Loe chân thân**: theo chân a của designer, dài 70, chìa 22.6 mỗi bên.
- Chỉ chốt cực trị tròn vào đường vượt (uốn mềm cục bộ) và dọn nút (`tidy`). Thân vươn lên ascender hoặc xuống descender không bị kéo.

## Bold — theo MẪU a Bold của designer (2115:384)

Designer 04/11 gửi a Bold làm mẫu. a Bold dùng đúng bản vẽ, và luật Bold của chữ thường rút từ chính mẫu này. Hai bản trước đều không khớp mẫu:
- bản "lòng nở đều 37 u, giữ bề ngang": lòng bị bóp;
- bản "giãn 40 rồi lòng co đều 35": nét mảnh dày bằng nét dày, mất tương phản.

Số đo trên mẫu a (SVD elip lòng, đơn vị u):

| | Regular | Bold | Δ |
|---|---|---|---|
| Thân | 102 | 130 (46 px) | +28, dày **ra phía ngoài** |
| Bề ngang chữ | 434 | 484 | +50 |
| Bụng (mép ngoài) | 141 px | 148 px | +20 |
| Lòng: bán trục dài / ngắn | 144.5 / 96.4 | 130.2 / 78.8 | −14.3 / −17.6 |
| Tâm lòng | | dời về phía thân 33 | |
| Vách trái (nét dày theo bút) | 74 | 126 | +52 |
| Nét mảnh (đỉnh bụng, vai) | | | +6…+22 |

Luật áp cho d, b, q, p, e, g (`lower.py: bold()`):
1. **Mép ngoài vòng giãn ngang +20** quanh tâm.
2. **Lòng là elip** (khớp từ bản vẽ): bán trục dài −14.3, bán trục ngắn −17.6, tâm dời về phía thân 33 (d b q p). e và g không có thân nên không dời.
3. **Thân 102 → 130, dày ra phía ngoài.** Mép trong giữ khoảng chồng với vòng; thân trượt theo mép vòng (+10). Loe ngoài trượt theo.
4. **Thanh e** +16, nở đều hai phía.
5. **Cổ nối và tai g** nở đều 8 mỗi phía; mặt cắt tai giữ phẳng.
6. **Đầu thân nối bụng không có loe phía lòng**, như thân D, B, P chữ hoa. Designer đã áp ở bản vẽ cho chân a, chân d b, đỉnh q p.

| Chữ | Rộng R → B | Mật độ R | Mật độ B | B / R |
|---|---|---|---|---|
| a (mẫu) | 434 → 484 | 0.317 | 0.384 | 1.21 |
| e | 486 → 506 | 0.263 | 0.314 | 1.20 |
| d b q p | 509 → 557 | 0.359 | 0.431 | 1.20 |
| g | 462 → 481 | 0.383 | 0.453 | 1.18 |

Chữ thường Bold nhẹ hơn chữ hoa Bold một chút (B/R của chữ hoa 1.26–1.43). Đây là theo mẫu a của designer.

## Lịch sử e

- **Bản 1**: lòng đứng, có nét chéo.
- **Bản 2**: vòm, thanh ngang, bụng có đầu cắt đứng.
- **Bản 3** (hiện tại): như bản 2, nhưng lòng là elip xoay.
