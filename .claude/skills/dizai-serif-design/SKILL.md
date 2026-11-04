---
name: dizai-serif-design
description: Rule book và nguyên tắc dựng chữ của Dizai Serif (chữ glyphic loe nét, logic bút dẹt, tương phản cao). Dùng trước khi vẽ, sửa hoặc review bất kỳ glyph, weight, dấu, spacing nào của Dizai Serif. Dùng kèm dizai-serif-qa.
---

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
- **S10 Chữ thường** (chưa có, viết luật TRƯỚC khi vẽ):
  - x/cap khoảng 0.66–0.70 (glyphic);
  - v ≈ 0.9 V, h ≈ 0.9 H;
  - loe giống S5 nhưng tỉ lệ theo v;
  - a và g chọn theo concept (đề xuất: a hai tầng, g hai tầng kiểu La Mã, kiểm
    lòng ở Bold).
- **S11 Dấu tiếng Việt.** Dấu cùng hệ nét với chữ và có tương phản theo bút:
  - **Sắc và huyền là cặp đối xứng gương** (designer 04/11: "dấu sắc và huyền không đồng bộ"): cùng hình nêm, đầu trên dày 0.80 N, chân 0.36 N; huyền = sắc lật ngang. Dấu là nét bút, không phải tấm thép.
  - **Sừng ơ ư cắt phẳng**, không có giọt tròn (designer 04/11: "dấu ư không nên tròn"). Tâm sừng là một cung Bézier liền ("cho smooth"); Ư và Ơ có đầu sừng ngang nhau, ở Ư sừng thay loe ngoài thân phải ("dấu ư lỗi và không đồng bộ").
  - **Trăng là lưỡi liềm đối xứng**, hai đầu thon đều ("dấu ă cũng hơi lỗi").
  - **& dựng từ số 8** của designer + chân chéo D ("ký tự & cũng lỗi").
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
- **S14 Spacing và kerning.**
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
