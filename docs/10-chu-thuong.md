# 10 — Chữ thường (v0.5, đang dựng)

Nguồn: bản vẽ designer, Figma frame `2115:421` (cập nhật 04/11; trước đó `2112:126`): a, e, d, b, q, p, g (hai tầng), **a Bold (mẫu)**.

Bản 2115:421 — designer: "các glyph này sẽ đồng bộ style với chữ hoa hơn": lòng a, d, b, q, p và vòng dưới g là **elip đứng lệch về phía thân** (như bụng D B chữ hoa); e và bụng trên g giữ lòng xoay.
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
- **Lòng elip đứng lệch về phía thân** (a, d, b, q, p, vòng dưới g), như bụng D B chữ hoa: vách đối diện thân dày (34 px), đỉnh/đáy mảnh (16 px). e và bụng trên g: lòng elip xoay.
- **g hai tầng**: bụng trên (elip 144 × 134 px), vòng dưới (144 × 88 px), cổ nối, tai. Đáy vòng dưới ở −198 (đường descender).
- **d b q p dùng chung một khối bụng và một khối thân**: d là bản gốc, b lật ngang, q lật dọc, p xoay 180°.
  - Thân có loe ở hai đầu, như chân a.
- **Loe chân thân**: theo chân a của designer, dài 70, chìa 22.6 mỗi bên.
- Chỉ chốt cực trị tròn vào đường vượt (uốn mềm cục bộ) và dọn nút (`tidy`). Thân vươn lên ascender hoặc xuống descender không bị kéo.

## Bold — theo MẪU a Bold của designer (2115:551)

a Bold dùng đúng bản vẽ. Luật Bold của các chữ khác rút từ mẫu này (`lower.py: bold()`):

| | a Regular | a Bold (mẫu) | Luật |
|---|---|---|---|
| Thân | 36 px = 102 u | 44 px = 124.5 u | +22.6, dày **ra phía ngoài**; mép trong giữ khoảng chồng với vòng |
| Bụng (mép ngoài) | 130 px | 134 px | giãn ngang +11.3 quanh tâm |
| Lòng (elip) | 39 × 47 px | 34.5 × 42.5 px | co theo tỉ lệ bán trục −10.5 % |
| Tâm lòng | lệch về thân 10 px | 13.5 px | dời thêm về phía thân 9.9 |

- e và g không có thân nên lòng không dời.
- Thanh e +12.7, nở đều hai phía.
- Cổ nối và tai g nở 6.4 mỗi phía; mặt cắt tai giữ phẳng.
- Đầu thân nối bụng không có loe phía lòng, như thân D, B, P chữ hoa (designer đã áp trong bản vẽ).
- Lòng co theo tỉ lệ chứ không theo số cố định. Lý do: co cố định 12.7 thì chữ có lòng lớn (d, e) chỉ đạt B/R 1.15–1.16, nhẹ hơn mẫu a (1.20).

| Chữ | Rộng R → B | Mật độ R | Mật độ B | B / R |
|---|---|---|---|---|
| a (mẫu) | 430 → 470 | 0.308 | 0.368 | 1.20 |
| e | 486 → 498 | 0.263 | 0.316 | 1.20 |
| d b q p | 509 → 543 | 0.337 | 0.404 | 1.20 |
| g | 462 → 473 | 0.374 | 0.429 | 1.15 |

Chữ thường Bold nhẹ hơn chữ hoa Bold (B/R của chữ hoa 1.26–1.43). Đây là theo mẫu a của designer.

## Lịch sử e

- **Bản 1**: lòng đứng, có nét chéo.
- **Bản 2**: vòm, thanh ngang, bụng có đầu cắt đứng.
- **Bản 3** (hiện tại): như bản 2, nhưng lòng là elip xoay.
