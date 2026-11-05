# 10 — Chữ thường (v0.5, đang dựng)

Nguồn: bản vẽ designer, Figma frame `2115:421` (cập nhật 04/11; trước đó `2112:126`): a, e, d, b, q, p, g (hai tầng), **a Bold (mẫu)**.

Bản 2115:421 — designer: "các glyph này sẽ đồng bộ style với chữ hoa hơn": lòng a, d, b, q, p và vòng dưới g là **elip đứng lệch về phía thân** (như bụng D B chữ hoa).

Cập nhật 05/11 (designer: "cập nhật lại e và o"):
- **e** lòng vòm và lòng bụng thành elip đứng, đầu cắt cao hơn (mặt trên ở 54.7 px).
- **o** có bản vẽ riêng (`2123:788`): vòng 172 × 181 px, **lòng elip xoay như O hoa**; thay o dựng tạm.
- **c** có bản vẽ riêng (`2123:922`, designer: "có thêm chữ c mới"), thay c dựng tạm.
  - Mép ngoài là elip, lòng là elip đứng, hai đầu cắt đứng ở x 150 px. Cùng hệ với C hoa.
  - c Bold theo luật mẫu a:
    - vách trái 36 → 44 px (= thân Bold);
    - đỉnh, đáy và đầu cắt dày thêm 12.7 (nét mảnh);
    - lòng vẫn là elip đứng và cắt qua mặt cắt, nên miệng c vẫn mở;
    - mép ngoài giãn ngang +11.3.
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

## Chữ suy ra từ module (TẠM, chờ designer duyệt hoặc vẽ lại)

Gồm 15 chữ f h i j k l m n r s t u v w x y z, Regular và Bold (o, c đã có bản vẽ).
- Code: `tools/construct/lower/derive.py`, xuất ra `lower/lower_derived.json`.
- Trong `ref_glyphs.json` các chữ này mang `src: "rule"`. Bold suy ra của d b q p e g cũng vậy; riêng a Bold là bản vẽ.

| Module | Nguồn (designer) | Dùng cho |
|---|---|---|
| Vai + thân + loe chân | thân a (Bold: a Bold mẫu) | n, h (thân trái lên ascender), m (hai vai), u (n xoay 180°) |
| **Nửa c** (designer 05/11: "cập nhật lại các chữ thường còn lại theo c mới") | c: vách = thân (36 / Bold 44 px), đầu cắt đứng | r (nửa trên, thu 0.70), f (nửa trên nâng lên ascender, 0.72), t (nửa dưới, 0.78), j (nửa dưới lật ngang, 0.78). Chỉ thu phần bên phải vách, vách giữ nguyên nên không có bậc chỗ thân gặp nửa c |
| Loe | thân d: dài 69.6, chìa 22.6, mũi trên mặt cắt ngang | mọi đầu thân và đầu nét chéo tự do (i, j, l, k, v, w, x, y) |
| **c nhỏ** (designer 05/11: "làm lại s theo c mới") | luật c: mép ngoài elip, lòng elip đứng, vách = thân, đỉnh mảnh 16 px (Bold +12.7), đầu cắt đứng cách mép phải lòng 5 px | s: mỗi bụng là nửa trên của một c cao 300. Bụng được dựng với tỉ lệ ngang của c thật rồi thu phần bên phải vách về bề ngang s 330 (Bold 341). Bụng dưới là bản xoay 180°. Sống gồm hai mép Hermite đi từ vách trái bụng trên (ở tâm bụng, tiếp tuyến đứng) xuống vách phải bụng dưới; nối G1, dày bằng vách. Thay bản cũ thu từ S hoa |

Nét chéo (luật S3):

| Nét | Regular | Bold |
|---|---|---|
| \ dày D | 100 | 122 |
| / mảnh t | 44 | 56.7 |

- Đỉnh dưới của v, w cắt phẳng 20.
- w là hai chữ v chồng lên nhau, đỉnh giữa không có loe.
- y: nét mảnh kéo xuống descender, có loe; nét dày dừng khi lọt hẳn vào nét mảnh.
- k: tay mảnh mọc từ thân lên x-height; chân dày mọc từ tay, không thò lên trên mép tay.
- z: hai thanh mảnh H và một nét chéo dày. Chưa có mỏ như Z hoa.
- Chấm i, j: đường kính 118 (Bold 146), cách x-height 70.
- t: đỉnh 640, có loe hai bên. Thanh ngang của f và t: dày H, mép trên ở x-height.

QA (`qa_outline.py`): còn các mũi nhọn chủ ý.
- Mũi loe ở phía góc nhọn của nét chéo (x, k).
- Góc đầu cắt ở c, e Bold.

**Chưa làm:**
- Spacing và kerning chữ thường (trang duyệt đang dùng bề ngang mực + 80).
- Dấu chữ thường (á, ơ, ư, đ…).
- Mỏ cho z.

## Dấu tiếng Việt cho chữ thường (TẠM, luật S11)

Phạm vi: 67 chữ, cùng ₫, cho Regular và Bold.
- Code: `tools/construct/lower/vn_lower.py`, xuất ra `lower/lower_vn.json`.
- Trong `ref_glyphs.json` các chữ này mang `src: "rule"`. Chữ có dấu giữ bề ngang của chữ gốc (`_W`).

Cách đặt dấu:
- **Bộ dấu**: dùng chung với chữ hoa (`vn_punct.marks`), cùng nét bút S15. Sắc và huyền là cặp đối xứng gương, mũ, trăng lưỡi liềm, ngã, hỏi, nặng, sừng.
- **Đáy dấu thấp nhất ở 542.4** = x-height 495 + vượt 8.4 + khe 36 + 3, cách tính như chữ hoa (700 + 11.3 + 36 + 3).
- **Tâm ngang dấu** là tâm hộp mực của phần x-height, nên bỏ qua đuôi y và sừng.
- **Mũ đi với sắc, huyền, hỏi**: dấu thanh nằm bên phải mũ. Mọi dấu khác chồng lên, khe ≥ 30.
- **i có dấu trên** dùng i không chấm; ị giữ chấm.
- **Nặng** nằm dưới đáy thật của chữ, khe 36. Ở ỵ, dấu nặng dời sang trái tới khi cách đuôi 36.
- **Sừng ơ** bám vòng o ở **góc 48°**; chữ hoa Ơ bám ở 38°. Vòng chữ thường nhỏ, sừng ở 38° chỉ nhô 33 khỏi x-height nên ơ đọc thành σ. Ở 48°, đầu sừng nhô khoảng 70.
- **Sừng ư** bám mép ngoài thân phải ở cùng cao độ với ơ. Sừng thay cho loe ngoài ở đỉnh thân phải, như Ư.
- **đ**: thanh ngang H cắt qua thân d ở 600, vươn ra ngoài thân 0.62 V và vào trong 0.9 V, như Đ.
- **₫**: đ cộng gạch dưới dày H ở −160.

QA (máy đo, 67 chữ × 2 weight):
- Khe dấu–chữ nhỏ nhất 38 (luật ≥ 36).
- Khe dấu–dấu và dấu–sừng nhỏ nhất 32.1 (luật ≥ 30).
- Chữ cao nhất là ẳ Bold, đỉnh ở 873.5.

## Lịch sử e

- **Bản 1**: lòng đứng, có nét chéo.
- **Bản 2**: vòm, thanh ngang, bụng có đầu cắt đứng.
- **Bản 3** (hiện tại): như bản 2, nhưng lòng là elip xoay.
