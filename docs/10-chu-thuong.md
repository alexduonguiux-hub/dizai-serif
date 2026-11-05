# 10 — Chữ thường (v0.5, đang dựng)

Nguồn: bản vẽ designer, Figma frame `2115:421` (cập nhật 04/11; trước đó `2112:126`): a, e, d, b, q, p, g (hai tầng), **a Bold (mẫu)**.

Bản 2115:421 — designer: "các glyph này sẽ đồng bộ style với chữ hoa hơn": lòng a, d, b, q, p và vòng dưới g là **elip đứng lệch về phía thân** (như bụng D B chữ hoa).

Cập nhật 05/11 — **frame `2120:665`** (designer: "update lại một số chữ thường"):
- **a**: bụng mới là elip 123 × 132 px, xoay ~28°, lòng lệch về thân. Khối thân và vai giữ nguyên.
- **e**: lòng vòm thành elip xoay; mặt nối vòm–bụng dời xuống 1 px (y 279).
- **d b q p**: khối bụng mới 164 × 183.5 px, **xoay 15°**, lòng elip lệch về thân. Thân giữ nguyên.
- **o, g, t, r**: không đổi.
- **a Bold**: mẫu a Bold cũ có bụng đứng, không còn khớp nên bỏ. Nay dựng theo cùng luật như d b q p: thân +22.6 ra phía ngoài, kể cả loe chân; vai dày xuống +12.7, đầu cắt dày theo; bụng giãn +11.3, lòng co 10.5 %, dời về thân 9.9.

Cập nhật 05/11 — **r, t có bản vẽ** (designer: "update chữ t và r", `2127:982`, `2127:1008`), thay bản dựng từ nửa c:
- **r**: thân 36 px; loe trên chỉ phía trái; loe chân hai bên; tai riêng có mặt cắt đứng (rộng 87 px).
- **t**: thân 36 px, đỉnh 631 có loe hai bên; thanh 14 px (−24 / +36 px quanh thân); móc chân ngắn có mặt cắt đứng (69 px).
- Bold theo luật mẫu a: thân +8 px (22.6 u) ra phía ngoài, tức bên trái, loe trái trượt theo; tai r, móc t và thanh dày vào trong +4.5 px (12.7 u), đầu cắt dày theo.

**f, j dựng từ khối t** (designer 05/11: "đồng bộ móc f và j theo r, t"):
- **f** = móc chân t **lật dọc** đặt ở đỉnh: thân cong liền sang phải, đỉnh 707, mặt cắt đứng. Cộng thân, thanh t (cùng vị trí so với thân) và loe chân hai bên như r.
  - Designer 05/11: "chữ f đang lỗi". Bản trước ghép tai r lên một thân có đỉnh phẳng, tạo khấc ở chỗ tai mọc ra.
- **j** = móc chân t lật ngang (đầu cắt sang trái), đáy ở −209. Đỉnh thân ở x-height, loe hai bên như đỉnh t. Có chấm.
- Bold dùng cùng luật với r, t. Thân dày ra phía ngoài: f sang trái, j sang phải.

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

Gồm 13 chữ f h i j k l m n s u v w x y z, Regular và Bold (o, c, r, t đã có bản vẽ).
- Code: `tools/construct/lower/derive.py`, xuất ra `lower/lower_derived.json`.
- Trong `ref_glyphs.json` các chữ này mang `src: "rule"`. Bold suy ra của d b q p e g cũng vậy; riêng a Bold là bản vẽ.

| Module | Nguồn (designer) | Dùng cho |
|---|---|---|
| Vai + thân + loe chân | thân a (Bold: a Bold mẫu) | n, h (thân trái lên ascender), m (hai vai), u (n xoay 180°) |
| **Nửa c** (designer 05/11: "cập nhật lại các chữ thường còn lại theo c mới") | c: vách = thân (36 / Bold 44 px), đầu cắt đứng | (không còn dùng: f, j nay dựng từ khối r, t — xem dòng dưới) (designer 05/11: "móc trên chữ f và móc dưới chữ t hơi dài ra", "đồng bộ móc r và j theo f, t"). Chỉ thu phần bên phải vách, vách giữ nguyên nên không có bậc chỗ thân gặp nửa c |
| Loe | thân d: dài 69.6, chìa 22.6, mũi trên mặt cắt ngang | mọi đầu thân và đầu nét chéo tự do (i, j, l, k, v, w, x, y) |
| **S hoa** (designer 05/11: "chữ s thường phải giống chữ s hoa chứ?") | S của designer | s: thu ngang 0.85 (Bold 0.786), dọc về x-height, rồi bù nét bằng nét viền góc vuông (Regular 7, Bold 4 mỗi phía).
  - Nét mảnh trên/dưới 40.5 (= H; Bold 57). Sống 102 theo phương đứng (Bold 126).
  - Bold thu hẹp hơn (designer 05/11: "chữ s thường bold bề ngang hơi rộng"): S Bold vốn rộng hơn S Regular nhiều. Nay s Bold rộng 362, Regular 349 (+13), như vòng chữ thường Bold (+11). Bản dựng từ c (05/11) đã bỏ: s phải cùng dáng S hoa |

**v w x y k z = chữ hoa của designer thu nhỏ** (designer 05/11: "chữ z cũng không đồng bộ style do thiếu module", "đồng bộ v w x y k theo chữ hoa"). Thay bản dựng theo luật nét chéo trước đó.
- **Cách thu**: giữ loe S5, đỉnh, mỏ của chữ hoa. Thu ngang 0.80, dọc về x-height. Bù nét 6 (Bold 3) mỗi phía bằng nét viền góc vuông, góc giữ sắc. Kết quả nét mảnh ≈ 44, chéo dày ≈ 100, thanh z = 39 (Bold 54).
- **Làm dày nét \\ cho v x y** (designer 05/11: "đồng bộ lại độ dày các glyph"; "chữ v hơi rộng", "v và y", "x cũng rộng"; "chữ y, x, v lỗi module").
  - Vì sao: nếu chỉ thu ngang, nét \\ chỉ còn ≈ 0.88 thân (v y nhẹ hơn chữ thường trung bình 40 %), mà chữ lại quá rộng (v 568, x 540, n 444).
  - Cách làm: thu hẹp hơn (v y 0.55, x 0.565), rồi dời song song hai mép nét \\ ra ngoài, mỗi bên ½ Δ theo phương ngang. Δ giải để nét \\ dày bằng thân (101.8 / Bold 124.5).
  - Loe và vát ở đầu mép tịnh tiến theo mép, nên cung module loe giữ nguyên bán kính như chữ hoa. Đỉnh nối mép với nét / tính lại bằng giao điểm.
  - Bản ngòi dẹt trước đó (cộng Minkowski với một đoạn thẳng) quét cả phần loe, làm cung module vỡ thành nhiều mảnh và méo đầu nét. Đã bỏ.
  - Kết quả: v y rộng 411 (Bold 422), x 423 (Bold 434). Nét / Regular ≈ 37–42, Bold ≈ 48–52.
  - **k và z** (designer 05/11: "kiểm tra lại module chữ k và z"): chân k (nét \\) và chéo z (nét /) cũng chỉ ≈ 0.89 thân (Regular 90.6 / 89.7, Bold 116 / 106). Nay dùng cùng cách dời song song hai mép: chân k và chéo z = 101.8 / Bold 124.4. Tay k (45 / 55) và thanh z (39 / 54) là nét mảnh, giữ nguyên. Mỏ, loe tịnh tiến theo mép, giữ cung chữ hoa. Thu ngang chỉnh để giữ bề rộng: k 0.785 (rộng 452 / Bold 472), z 0.772 (387 / 398).
  - w giữ như cũ (thu 0.80, không làm dày; rộng 654 / Bold 656) (designer 05/11: "giữ bề rộng chữ w như cũ"; "chữ w bold hơi dính").

**Nét tròn Bold dày thêm đúng B_STEM như thân** (designer 05/11: "kiểm tra lại độ dày các chữ còn lại").
- Đo bằng đường tròn nội tiếp (độ dày thật vuông góc nét), ở thành bụng xa thân. Regular đều: nét đậm 96–104 ở mọi chữ.
- Bold trước đó lệch: co lòng 10.5 % chung cho mọi chữ, nên lòng nhỏ co ít. Kết quả o +17.6, s +17.5, g +13.4, a +13.5, trong khi thân +22.6.
- Nay hệ số co lòng giải riêng cho từng chữ: o 0.140, g 0.196, a 0.193 (`B_KG`). s bù nét Bold 7 (trước 4), thu ngang 0.772 để giữ bề rộng.
- Kết quả Bold: o 123.7, g 123.8, a 119.0, s 120.4, e 122, b d p q 125, c 129.
- w Regular 94: giữ như cũ theo designer.

**Bề ngang Bold** (designer 05/11: "các chữ bold thường tăng độ rộng hơn nhiều so với regular"; luật tiến triển weight: bề rộng tăng ½ phần nét tăng):
- Thân Bold dày thêm 22.6, chia đều hai phía (mỗi mép 11.3), không dồn ra ngoài như trước. Lòng co, vị trí thân giữ theo Regular.
- Chữ một thân: +23 (a b d f i j l p q r t). n h u: +23. m: +34 (thân giữa chia đều cho hai lòng). k: +20 (thân dày đều hai phía; chéo giữ vươn ngang của Regular tính từ mép phải thân).
- Chữ tròn c e g o: +11. s +13. v x y z: +11, w +2 (Bold giải hệ số thu ngang để đúng Regular + 11.3).
- Trước đây n h u Bold rộng hơn Regular 51, m 79, k 46.
- Vai n m h u Bold suy ra từ chính vai Regular (mép ngoài +11.3, mép lòng −11.3, vai dày xuống +12.7), nên giữ khuyết cong chỗ vai gặp thân (designer 05/11: "chữ m, n, h, u bold bị mất nét góc lúc nãy").
- **Vai n m h u dựng bằng hai ellipse** (designer 05/11: "độ cong của các nét này không smooth", "đường cong không tự nhiên", "nên thử áp dụng cách dựng bằng 2 ellipse như các chữ tròn khác"). Mỗi nửa trên là một cung ellipse liền, độ cong biến thiên đều. Thay cho vai a ghép hai đoạn, vốn có độ cong nhảy ở đỉnh và tay nắm suy biến ở chỗ vai chuyển sang thân phải.
  - Hai ellipse cùng tâm cao 340.8 (chỗ thân phải bắt đầu thẳng).
  - Ellipse ngoài: mép phải = mép ngoài thân phải, đỉnh = đường vượt 503.4. Đi qua khuyết trên mép phải thân trái (Regular 448.4, Bold 458.9).
  - Ellipse trong (lòng): mép phải = mép trong thân phải, đỉnh thấp hơn đường vượt 40.4 (Bold 53.1). Đi qua nách, đặt sao cho chỗ nối vai–thân (đo đứng sát mép thân) dày bằng chỗ nối bụng–thân của b d p q: Regular 67.1, Bold 81.8, nên nách ở 381.3 / 377.1. Trước đó nách 420.8 / 418.2, chỗ nối chỉ 27.5 / 40.6, khoảng 40 % các chữ khác (designer 05/11: "chỗ nối m, n, u có bị bất đồng bộ độ dày với các glyph khác không?").
  - Ellipse lòng **nghiêng** như bụng d (designer 05/11: "nét nối của u, m, n, h vẫn cảm giác bị mỏng hơn so với các glyph khác"). Trục lớn nghiêng 72.2° (Bold 67.8°). Giải sao cho: đỉnh lòng đúng đỉnh trên, mép phải lòng chạm mép trong thân phải ở cao 340.8, đi qua nách. Lòng trục đứng làm nét vai mỏng nhanh khi rời thân (cách thân 20 u chỉ 45, so với b d p q 55).
  - Độ dày chỗ nối, đo đứng cách thân 1 / 8 / 20 / 40 u: Regular 66 / 62 / 56 / 49 (b d p q 67 / 62 / 55 / 49). Bold 81.5 / 79 / 74 / 66 (b d p q 82 / 77 / 72 / 68). Nách Bold đặt theo chỗ nối b d p q Bold 81.8.
  - m: ellipse ngoài vai sau kéo sang trái, đè lên vai trước. Hai cung ngoài cắt nhau thành nách nhọn trên thân giữa.
  - Chân thân phải có loe hai bên.
- **Chỗ nối a, r Bold** (designer 05/11: kiểm độ dày chỗ nối r, a với các chữ khác):
  - a Bold: lòng bụng không dời về thân nữa. Bụng a nối thân ở đáy, dời 9.9 làm chỗ nối Bold còn 76, mỏng hơn cả Regular (80). Nay 90.5.
  - r t f j Bold: mép trong tai / móc dày thêm B_BAR + 5 (B_JOIN), cho chỗ nối bằng b d p q Bold. r Bold: 77 → 80.5 (b d p q 82).
- **k**: tay, chân cắt ngoài mép thân rồi mới bù nét. Trước đó nhát cắt ăn 0.5 u vào thân K, bù nét làm dải này thành gờ 6 u dọc mép phải thân (designer 05/11: "chữ k bị lỗi nét").
- **k**: thân K giữ nguyên chiều cao (= ascender 698.6 ≈ cap). Ở Bold, thân thu về 124.5 (thân Bold chữ thường). Loe phải ở đỉnh và chân đi theo thân. Chỉ tay và chân thu về x-height (ngang 0.85).
- **y**: lấy v (từ V), kéo nét mảnh xuống descender, có loe chân. Nét dày dừng ở cao độ mép trái của nó gặp mép trái nét mảnh. Chữ hoa Y khác cấu trúc nên không dùng.
- Chấm i, j: đường kính 118 (Bold 146), cách x-height 70.
- t: đỉnh 640, có loe hai bên. Thanh ngang của f và t: dày H, mép trên ở x-height.

QA (`qa_outline.py`): còn các mũi nhọn chủ ý.
- Mũi loe ở phía góc nhọn của nét chéo (x, k).
- Góc đầu cắt ở c, e Bold.

**Chưa làm:**
- Spacing và kerning chữ thường (trang duyệt đang dùng bề ngang mực + 80).
- Dấu chữ thường (á, ơ, ư, đ…).

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


**Đuôi e Bold** (designer 05/11: "e bold đuôi móc cao và nhọn quá"): lòng bụng e Bold dời sang phải tới khi mặt cắt đuôi = Regular + 12.7 (69.6 → 82.5), góc gặp tù như Regular.
