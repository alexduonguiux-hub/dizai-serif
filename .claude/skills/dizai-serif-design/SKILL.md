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
| Chéo 0.87–0.92 thân | Chéo DÀY 1.06–1.10 thân, chéo MẢNH ≈ 0.45 thân (S2) |
| Vòng trục đứng, oval theo hộp | Vòng trục nghiêng (S4) |
| Bề ngang đều | Tỉ lệ La Mã: rộng (O Q C G D M W A V X Y), vừa (H N U K T Z R B P), hẹp (E F L S J I) |
| Tương phản 0.83 | Tương phản 0.39 |

## 2. Rule book v0.1 (Regular, UPM 1000)

- **S1 Lưới.** Cap 700. Overshoot: tròn +9 / −10 (đề xuất, chờ đo nguồn), đỉnh nhọn
  +12…+16. Số cao bằng cap (lining). Ascender, x-height và descender chốt khi viết
  luật chữ thường (S10).
- **S2 Bảng nét (Regular).**

  | Ký hiệu | Phần | Giá trị |
  |---|---|---|
  | V | thân đứng dày | 101 |
  | D | chéo dày (nét \ theo bút) | 108 (1.07 V) |
  | t | nét mảnh: chéo /, thân mảnh của M N | 46 (0.45 V) |
  | H | ngang mảnh: thanh, tay, đỉnh/đáy bụng | 39 (0.39 V) |
  | Vf | nét số | 0.95 × nét hoa (đang chờ duyệt) |

  Mọi số khác suy ra từ bảng này. Khớp được mỏng hơn nét (~0.8). Không cố định số của
  Bold. Mỗi weight có một bảng riêng.
- **S3 Logic bút dẹt.** Bút nghiêng ~30°. Nét đi từ trên-trái xuống dưới-phải dùng D.
  Nét đi từ dưới-trái lên trên-phải dùng t. Thân đứng dùng V. Nét ngang dùng H.
  Ngoại lệ chủ ý (ghi tên):
  - Z: chéo dày (truyền thống La Mã).
  - U: hai thân dày (chờ duyệt).
  - 2 và 7: chéo dày.
- **S4 Vòng.** O và Q chung một vòng (rộng 726). Trục dày nghiêng: dày ở dưới-trái và
  trên-phải. Mọi chữ tròn (C G D Q 0 6 9 8 3 5) dùng cùng một góc trục. Lòng là elip
  thật, không có đoạn phẳng. 0 là oval hẹp (578), phân biệt với O.
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
  - sắc đi từ dưới-trái lên trên-phải nên là nét mảnh (t, đầu trên có thể đậm hơn
    theo vết bút); huyền đi xuống-phải nên là nét dày (D thu nhỏ). Dấu là nét bút,
    không phải tấm thép.
  - Mũ: dựng như đỉnh A thu nhỏ, lòng luôn mở.
  - Trăng: nửa elip trục nghiêng.
  - Ngã: sóng có tương phản theo bút.
  - Hỏi: móc ? thu nhỏ.
  - Nặng: cùng họ chấm với dấu chấm.
  - Dấu hoa dùng bộ `.case`. Khe dấu–dấu ≥ 30, dấu–chữ ≥ 36.
  - Sừng ơ ư dùng chung một tấm.
  - Phủ đủ 134 chữ Việt và dấu tổ hợp.
- **S12 Số.** Lining cao bằng cap. 1 có cờ, cùng góc ở mọi weight. 3 và 5 chung bụng
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
