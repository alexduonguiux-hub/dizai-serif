---
name: dizai-serif-design
description: Rule book và nguyên tắc dựng chữ của Dizai Serif (chữ glyphic loe nét, logic bút dẹt, tương phản cao). Dùng trước khi vẽ, sửa hoặc review bất kỳ glyph, weight, dấu, spacing nào của Dizai Serif. Dùng kèm dizai-serif-qa.
---

> Tên phát hành: **AnNam Serif** (designer 06/11: "AnNam", thêm "Serif" để phân biệt với BT Annam Neue của BeauType); PostScript / file `AnNamSerif`; vendor ID `DZAI` (nên đăng ký Microsoft). Tên dự án / thư mục / skill giữ "dizai-serif". Mỗi lần phát hành: kiểm unique — name ID 3 `version;DZAI;PostScript(-VF)`, PostScript không trùng trong từng định dạng, file gộp tiền tố `AnNamSerifSlnt`.

# Dizai Serif — luật dựng chữ

Skill này lấy phương pháp của bộ Định Tường (`typeface-construction`,
`type-design-principles`) và chỉnh cho một bộ chữ **có tương phản**. Phần phương pháp
chung (quy tắc trước rồi mới vẽ, chỉ dựng hình học, control set, cổng duyệt, sổ lỗi)
giữ nguyên. Rule book bên dưới thay rule book DINHTUONG60s.

Concept và số đo nằm ở `docs/01-nghien-cuu-va-concept.md` và
`docs/02-so-do-va-qa-regular.md`. Số trong bảng là số Regular đo từ ảnh
(v0.1, ±3 u). Chốt lại trên outline khi có file nguồn.

## 0. Luật gốc (giữ từ Định Tường)
1. Mọi thay đổi là thay đổi một luật có số hiệu và số đo. Không vá riêng một chữ.
   Luật áp cho mọi glyph dùng nó, ở mọi weight.
2. Chỉ dựng hình học: Bézier tính từ luật, boolean vector. Không dựng trên raster rồi
   dò viền. Guide sinh từ code dựng.
3. Yêu cầu trái nguyên lý: nói rõ và đề xuất bản đúng nguyên lý.
4. Regular là bản vẽ gốc. Medium và Bold là cùng thiết kế đó, thêm nét.
5. Một đặc điểm phong cách phải có ở mọi chỗ hoặc không có ở đâu cả. Ngoại lệ phải
   ghi thành văn bản.

## 1. Khác biệt so với DINHTUONG60s (KHÔNG áp máy móc)
| Luật DINHTUONG60s | Ở Dizai Serif |
|---|---|
| R5h không thu nét / monoline | **Không áp dụng.** Độ dày theo hướng bút dẹt (S3). Nét chỉ mảnh dần khi hướng nét đổi so với bút; không bao giờ mảnh tuỳ tiện |
| R4b loe F 7/8/9 trên L 120 | Loe lõm F ≈ 0.21 V mỗi bên, trên L ≈ 0.6 V (S5) |
| Chéo 0.87–0.92 thân | Chéo DÀY ≈ 0.97 thân (đo vuông góc), chéo MẢNH ≈ 0.44 thân (S2) |
| Vòng trục đứng, oval theo hộp | Vòng trục nghiêng (S4) |
| Bề ngang đều | Tỉ lệ La Mã: rộng (O Q C G D M W A V X Y), vừa (H N U K T Z R B P), hẹp (E F L S J I) |
| Tương phản 0.83 | Tương phản 0.39 |

## 2. Rule book v0.1 (Regular, UPM 1000)

- **S1 Lưới.** Cap 700 (Figma: cap line và baseline khớp với H; v0.1 có P R lệch 2 px, M Bold lệch 2 px). Overshoot: tròn +9 / −10 (đề xuất, chờ đo nguồn), đỉnh nhọn
  +12…+16. Số cao bằng cap (lining). Ascender, x-height và descender chốt khi viết
  luật chữ thường (S10).
- **S2 Bảng nét (v0.2, đã áp trong Figma — `docs/04-v0.2-thay-doi-trong-figma.md`).**

  | Ký hiệu | Phần | Regular u (Figma px) | Bold u (px) |
  |---|---|---|---|
  | V | thân đứng | 102 (36) | 139 (49) |
  | Vr | chỗ dày nhất của vòng và bụng (O Q C G D B P R) | 106 (37.5) = 1.05 V — duyệt 04/11 | 146 (51.5) |
  | D | chéo dày (nét \\ theo bút) = chéo của A | 100 (35.2); X 95 (33.5) là ngoại lệ | 146 (51.5) |
  | t | nét mảnh: chéo /, thân mảnh của M N | 44 (15.5) | 74 (26) |
  | H | ngang mảnh: thanh, tay, đỉnh/đáy bụng | 40 (14) | 68 (24) |
  | Sp | sống S / thành bụng S | 104 (36.7) / 96 (34) | 143 (50.3) / 130 (46) |
  | Vf | thân số | 102 (36) = V, giữ như bản vẽ gốc | — |
  | Hf | ngang số (2 3 4 5 nóc, 4 thanh) | 90 (32): **nét ngang dày là bản sắc của bộ số** (designer 04/11: "nét số cũ đang đẹp và đồng bộ style hơn"); 7 nóc 34 (12) | — |

  Cân bằng số ↔ chữ đo bằng MẬT ĐỘ MỰC (diện tích mực ÷ (bề ngang mực + 2 × 40 u) ÷ cap),
  không đo bằng độ dày từng nét: v0.2 số 0.344, chữ hoa 0.335 (+2.7 %, trong ngưỡng ±5 %).

  Cap = 247 px trong Figma = 700 u (1 px = 2.834 u). Số chính thức đo trên vector Figma,
  không đo trên ảnh: răng cưa của ảnh từng làm nét 14 px đọc thành 33 u.
  Mọi số trong bảng là độ dày ĐO VUÔNG GÓC NÉT.

  Mọi số khác suy ra từ bảng này. Khớp được mỏng hơn nét (~0.8). Không cố định số của
  Bold. Mỗi weight có một bảng riêng.
- **S2b Bề ngang nhóm chéo** (duyệt 04/11, "áp bản 0.96 / 0.94 cho X Y"). Mực của A = V = 237 px (667 u) làm chuẩn.
  - X = 0.96 A: 226.6 px (≈ 642 u).
  - Y = 0.94 A: 222.9 px (≈ 632 u).
  - Lý do: X và Y hở trắng ở cả hai bên đỉnh nên trông rộng hơn A, V khi cùng bề ngang.
  - Thu hẹp không làm đổi độ dày nét vuông góc. Thân Y và chỗ giao giữ nguyên. Đầu loe bám theo mép nét mới.
  - Bold dùng cùng tỉ lệ khi vẽ X, Y.
- **S3 Logic bút dẹt.** Bút nghiêng ~30°. Nét đi từ trên-trái xuống dưới-phải dùng D.
  Nét đi từ dưới-trái lên trên-phải dùng t. Thân đứng dùng V. Nét ngang dùng H.
  Ngoại lệ chủ ý (ghi tên):
  - Z: chéo dày (truyền thống La Mã).
  - U: hai thân dày (chờ duyệt).
  - 2 và 7: chéo dày.
- **S4 Vòng (chốt 04/11, designer: "nên đưa C G về như cũ").** Trục dày nghiêng: dày ở dưới-trái và trên-phải.
  - O, Q: lòng xoay 30°. Số 0, 6, 9: lòng xoay 15°.
  - **Ngoại lệ chủ ý: C, G giữ lòng đứng (0°).** Chữ hở bên phải mất vùng dày trên-phải, nên lòng nghiêng sinh ra lưỡi liềm dày ở dưới-trái và nét đỉnh rất mảnh.
  - Đã thử 30° và 15° (bảng "Xoay lòng C G theo trục O" và "Trước / sau — C G trục 15°" trên trang v0.2). Designer chọn giữ trục đứng. Đừng "sửa" C, G về trục nghiêng.
  - Thông số C, G v0.2: thành trái = Vr (Regular 37.5, Bold 51.5); đỉnh/đáy 14 / 24.
  - Lòng là elip thật, không có đoạn phẳng. 0 là oval hẹp (578 u), phân biệt với O.
- **S5 Loe.** Mọi đầu thân và đầu chéo tự do loe lõm từ V lên V + 2F, F = 21 mỗi bên,
  trên L = 60 tính từ mép. Góc cuối bo r ≈ 5. Đỉnh nhọn và vertex (A, M, N, V, W) không
  loe. Không loe vào khấc, không loe vượt đường kẻ. Chéo loe vuông góc với chéo, cùng F
  và L.
- **S6 Đầu nét hở** (C G S J 2 3 5 6 9, tay E F T Z). Một quy tắc cho mỗi loại:
  - tay ngang có mỏ (E, F, T, Z trên): một hình mỏ;
  - đầu vòng (C, G, S, 2, 3, 5, 6, 9): một kiểu cắt. Vị trí cắt tính theo tỉ lệ nét,
    không theo bề ngang. Góc gặp lòng 90–108°.
- **S7 Khớp.** Nét mảnh mọc ra khỏi nét dày với góc sắc. Bụng B D P R nối thân bằng
  nét H, chỉ mỏng ở đúng chỗ khớp. Đỉnh A M N V W là chỗ hai nét đè nhau; mép trong có
  khấc nhỏ cố định theo Regular nếu dùng.
- **S8 Thanh.** A ở 0.25 cap (La Mã, chờ kiểm lòng Bold). H và E ở 0.50 cap, đề xuất
  0.51–0.52 (tâm thị giác). Tay giữa E ngắn hơn tay trên. P và R khép bụng ở ~0.50 cap,
  bụng B trên nhỏ hơn bụng dưới.
- **S9 Đuôi bút** (Q R K J). Đuôi là một đường cong đều (G2 ở chỗ rời bụng hoặc thân).
  Độ dày theo bút (S3). Tầm vươn của Regular là mức sàn cho mọi weight.
- **S10 Chữ thường** (v0.5, `docs/10-chu-thuong.md`, nguồn Figma 2112:126):
  - x-height 495 (vượt 503.4 / −11.3); ascender d b = 698.6 ≈ cap; descender q p = −200.8.
  - **Thân chữ thường = V chữ hoa** (102 / Bold 139). Designer 04/11: "đồng bộ độ dày của các chữ thường với chữ hoa". Bỏ luật cũ 0.9 V.
  - Lòng a d b q p và vòng dưới g: elip ĐỨNG lệch về phía thân, như bụng D B (designer 04/11: "đồng bộ style với chữ hoa hơn"); e, bụng trên g lòng xoay. d b q p chung một khối bụng và một khối thân (lật). g hai tầng.
  - **Bold theo MẪU a Bold của designer** (2115:551): thân 124.5 dày ra ngoài; vòng giãn +11.3; lòng elip co −10.5 % bán trục, dời về phía thân 9.9; thanh +12.7. Đầu thân nối bụng không loe phía lòng. Mật độ B/R ≈ 1.20.
- **S11 Dấu tiếng Việt.** Dấu cùng hệ nét với chữ và có tương phản theo bút:
  - **Sắc và huyền là cặp đối xứng gương** (designer 04/11: "dấu sắc và huyền không đồng bộ"): cùng hình nêm, đầu trên dày 0.80 N, chân 0.36 N; huyền = sắc lật ngang. Dấu là nét bút, không phải tấm thép.
  - **Sừng ơ ư cắt phẳng**, không có giọt tròn (designer 04/11: "dấu ư không nên tròn"). Tâm sừng là một cung Bézier liền ("cho smooth"); Ư và Ơ có đầu sừng ngang nhau, ở Ư sừng thay loe ngoài thân phải ("dấu ư lỗi và không đồng bộ").
  - **Trăng là lưỡi liềm đối xứng**, hai đầu thon đều ("dấu ă cũng hơi lỗi").
  - **? dựng từ đầu số 2** + thân cong liền ("cho smooth hơn"); **( ) là lưỡi liềm serif** ("glyph phổ biến của dòng serif"); mọi đầu tự do của dấu câu lớn có **loe S5**.
  - **QA nét thừa**: `tools/construct/ref/tidy.py` (dọn) + `tools/construct/qa_outline.py` (kiểm) chạy sau mọi thay đổi.
  - **& dựng từ số 8** của designer theo dáng & serif cổ điển: chân dày (\\) cắt chéo tay mảnh (/) đi lên phải tới 0.52 cap ("ký tự & cũng lỗi", "không giống glyph phổ biến cùng dòng").
  - Mũ: dựng như đỉnh A thu nhỏ, lòng luôn mở.
  - Trăng: nửa elip trục nghiêng.
  - Ngã: sóng có tương phản theo bút.
  - Hỏi: móc ? thu nhỏ.
  - Nặng: cùng họ chấm với dấu chấm.
  - Dấu hoa dùng bộ `.case`. Khe dấu–dấu ≥ 30, dấu–chữ ≥ 36.
  - Sừng ơ ư dùng chung một tấm.
  - Phủ đủ 134 chữ Việt và dấu tổ hợp.
  - **v0.4 (04/11):** bộ `.case` cho 67 chữ hoa đã dựng bằng nét bút dẹt S15 (φ 20°, bút dấu N 78 / m 26, Bold 108 / 44). Số đo, vị trí và QA khe ở `docs/09-dau-tieng-viet-va-dau-cau.md`; code ở `tools/construct/ref/vn_punct.py`.
- **S15 Nét bút dẹt cho dấu và dấu câu cong.** w(θ) = √((N·sin(θ − 20°))² + m²). Bút chữ: Regular N 105 / m 26, Bold 146 / 46 (đứng = V, ngang ≈ H). Độ dày làm mượt theo chiều dài nét; phía lòng không lùi quá 0.8 bán kính cong. Dấu câu và ký hiệu: bảng ở docs/09.
- **S12 Số.** Giữ nét ngang dày (Hf 32 px) như bản vẽ gốc. Màu chữ cân bằng theo mật độ mực trung bình, không ép từng nét bằng chữ. Lining cao bằng cap. 1 có cờ, cùng góc ở mọi weight. 3 và 5 chung bụng
  dưới. 6 và 9 chung bụng (xoay 180°). 8 có vòng trên nhỏ hơn. 4 có thanh ~0.25 cap.
  Có tnum.
- **S13 Tiến triển weight.** Một khung xương; mỗi weight khác nhau ở bảng nét. Dùng
  bảng K của R2c (`type-design-principles` §3) để chia phần nét thêm vào trong và ra
  ngoài:
  - Chiều cao không đổi.
  - Bề ngang mực và advance tăng đơn điệu R ≤ M ≤ B.
  - Khoảng mở, lòng nhỏ (lòng A trên thanh, lòng B P R) và tầm vươn đuôi đo theo đơn vị
    Regular.
  - **Tương phản theo weight:** nét mảnh tăng chậm hơn nét dày. Ghi tỉ lệ t/V và H/V cho
    từng weight thành bảng, giống nhau ở mọi glyph.
- **S14 Spacing và kerning** (v0.6, `docs/11-spacing-kerning.md`, `tools/construct/spacing.py`): spacing trắng quang học độ sâu 40, chuẩn H 40/44, n 32/36; kerning class chữ gốc (Ơ Ư ơ ư class phải riêng) theo khe nhỏ nhất so với cặp chuẩn, −0.45 × phần dư, chỉ kéo vào, ≥ −150 (gạch/dấu toán ≥ −60); ngoại lệ chống va giữ khe ≥ 26 kể cả dấu/sừng.
  - Sidebearing đo theo khoảng trắng quang học so với H (hoa), sâu 40, ±6.
  - Số được dàn khoảng (spacing), không kern: mỗi bên bằng khoảng trắng của 0.
  - Mọi cặp giữ khe mực ≥ 26.
  - Chữ La Mã cần `cpsp` khi set toàn hoa.

## 3. Quy trình
Nghiên cứu → concept (đã có v0.1) → **duyệt 6 điểm** → rule book bằng số → control set
(H O A V M N C G S R Q + 0 2 5 + dấu Ấ Ặ Ở Ữ) × mọi weight, mỗi weight một hàng mực và
một hàng dựng hình → toàn bộ charset → QA (`dizai-serif-qa`) → kerning → xuất bản
(OTF/TTF/woff2, Figma, zip có version).

Mỗi góp ý mới của designer: đặt tên luật bị vi phạm → sửa trong code dựng → build lại
mọi weight → QA → ghi vào đây (kèm ngày, lời designer, số đo).

## 4. Luật bổ sung v0.6–v0.7 (05–06/11) — ghi từ góp ý designer

### 4.0 Nguyên tắc làm việc (bài học)
- **Bản vẽ designer là chuẩn.** Không tự đổi HÌNH glyph khi chưa được duyệt từng điểm (a một tầng ở Italic bị trả lại: "sao đổi glyph chữ a"). Thay đổi lớn → hỏi trước (liệt kê lựa chọn), làm sau.
- "Giữ nguyên bản các glyph" nghĩa là giữ cả chữ hoa ("bạn nên giữ lại glyph gốc cho cả chữ hoa").
- Khi designer nói "hẹp" là nói **kích thước** (bề ngang), không phải lòng chữ.
- Sửa bằng luật trong code dựng, build lại mọi weight, QA, rồi mới gửi preview. Mỗi lần gửi: commit + push + publish artifact (cùng URL).

### 4.1 Kerning (spacing.py)
- **Trắng cặp theo font tham chiếu** (ref_kern.py, phương pháp DINHTUONG60s): k = tỉ số trung vị (R + B của Liberation / DejaVu / Caladea / FreeSerif) × W(nn | HH) − W0; |k| ≤ 0.4 advance hẹp; Ư Ơ dùng cặp gốc.
- **Tròn × chéo:** D O (+ dấu) đứng trước A V W Y T, và A V W Y T đứng trước O C G Q → khe mực nhỏ nhất ≤ 1.0 × khe HH (ROUND_A, WEDGE_X).
- **Chống va** sàn 26 (sừng 14), làm tròn **1 u** (bội 5 làm R / B thừa → SemiBold nội suy thưa, "ư + i m n").
- **Variable:** chỉ có master Regular / Bold → Medium / SemiBold = ĐÚNG nội suy (dx, advance, class kern, ngoại lệ); ngoại lệ nào nội suy chặt hơn mức chống va thật thì nới cả R / B.

### 4.2 Bề ngang và độ dày
- **Thu hẹp chữ hoa X V Y:** nghiêng từng nét quanh điểm gốc (narrow_caps.shear_narrow, FRAC 0.08) — giữ loe, nhát cắt ngang, độ dày. Không thu hẹp bằng làm đậm / co cả glyph (làm méo loe).
- **S10b** nét chéo mảnh v w x y k = thân chữ thường × (nét mảnh / thân) của V hoa cùng weight (44.5 / 63.6), dời song song hai mép.
- **S10c** bề ngang mực v x w (y theo v) = 1.10 × bản trước 06/11; Bold ≥ Regular + ½ phần thân tăng × số nét dày (đơn điệu).

### 4.3 Ký hiệu
- **≤ ≥** dựng chevron cỡ 0.84 bằng ĐÚNG bút của < > (không thu nhỏ cả nét). **≈ ~** cạnh mỏng bút ≥ 0.75 H.
- **Nháy thẳng ' " ′ ″**: chân CẮT NGANG; dáng theo nháy cong — đầu = đầu giọt (chấm câu), cao = nháy cong, thon nhanh (lõm 0.45), chân 0.30 V. " và “ ” là hai ký tự Unicode khác nhau, font phải có cả hai.
- **™**: T M của master **Bold** thu 0.42; weight đậm hơn chỉ dày THEO PHƯƠNG NGANG + thanh T dày theo H — bằng **dời điểm** (không boolean) để hai master cùng cấu trúc; đáy V của M kéo nhọn lại (`sharpen` chỉ cho M).
- **{ }** mũi giữa có khối nối (hai nửa elip từng chỉ chạm một điểm); đầu mũi + khối nối dày max(0.16 thân, 0.66 H).
- **ß** chỗ thắt 0.66 H, thành đỉnh vòng trên 0.62 H. Mọi nét mảnh của ký hiệu ≥ 0.6 H (ngưỡng qa_stroke).
- **Dấu toán** + − = ≠ × ÷ ± < > ≤ ≥ ¬ ≈ cùng advance = advance của + (mực canh giữa ô); ~ giữ riêng.
- **Dấu ngã** cân độ nghiêng: đường tâm sóng nâng sang phải y += s·x, s = ½ mức cân trọng tâm hai nửa (0.118 R / 0.108 B) — bút dẹt làm nét xuống giữa dày, dấu đổ phải.
- **Dấu nặng:** MỘT đường chấm chung (đỉnh −49, tính từ đáy chuẩn −11.3, không theo đáy tràn riêng); **ỵ** cùng đường chấm, bên PHẢI đuôi y, khe GAP_ML.

### 4.4 Outline / variable
- Hai master Regular / Bold phải cùng cấu trúc (compat_masters.py): phép làm khác topology giữa hai master (boolean, Minkowski) → dùng phép **dời điểm** thay thế.
- Chiều contour theo độ lồng; so chiều bằng diện tích đường cong lấy mẫu (contour 2 đoạn cong có diện tích neo = 0).
- `tidy`: chỉ bỏ "gai" khi phần bỏ đi < 30 u² (mũi nhọn thật như chóp mỏ T phải giữ).
- Tách dấu khỏi chữ gốc theo dải cao độ; Đ / đ canh chữ gốc theo MÉP PHẢI (thanh chìa trái).

### 4.5 Italic (06/11)
- File variable: `DizaiSerif[wght].ttf`, `DizaiSerif-Italic[wght].ttf` và file gộp `DizaiSerif[slnt,wght].ttf` (wght 400–700 + slnt 0 … −10°, 4 master).
- **Italic = glyph Roman nghiêng 10°** quanh ½ x-height (quyết định designer). Spacing / kerning dùng chung Roman.
- Luật I2 (đuôi ra, f đuôi xuống, v w đáy tròn, y đuôi cong, nét vào, chân gọn, chữ hoa hẹp 0.94) nằm trong `tools/construct/italic.py` sau cờ `LOWER_I2`, `CAPS_COND` = False — chỉ bật khi designer duyệt lại. Chi tiết `docs/14-italic.md`.

### 4.6 Pipeline
`ref/narrow_caps.py` (khi đổi chữ hoa) → `ref/interp.py` → `ref/vn_punct.py` → `lower/lower.py` → `ref/make_ref.py` → `lower/derive.py` → `lower/vn_lower.py` → `ref/symbols.py` → `ref/make_ref.py` → `node export.js > out/construct/parts.json` → `build.py` (gồm compat_masters) → `spacing.py` → QA (`dizai-serif-qa`) → `italic.py` (+ chép outlines / spacing / kerning sang `out/construct_italic`) → `export_font.py` → `qa_font.py` → `preview_html.py` → commit, push, publish.
