# 13 · Bốn weight: Regular · Medium · SemiBold · Bold (v0.5)

Yêu cầu của designer ngày 05/11: "thêm 2 weight medium và semi bold". Hai lựa chọn đã duyệt:
- **Tự sinh toàn bộ.** Designer không cần vẽ thêm.
- **Bậc đều theo độ dày nét.** Medium = 1/3 và SemiBold = 2/3 quãng Regular → Bold.

## Bảng weight (`tools/construct/weights.py`)
| Weight | t | usWeightClass | Nét thân thường |
|---|---|---|---|
| Regular | 0 | 400 | 101.8 |
| Medium | 1/3 | 500 | 109.4 |
| SemiBold | 2/3 | 600 | 116.9 |
| Bold | 1 | 700 | 124.5 |

- `lerp_w(d)` nhận bảng `{'Regular': x, 'Bold': y}` và thêm Medium / SemiBold bằng nội suy. Hàm này nội suy cả dict / tuple lồng nhau.
- Giá trị bool hoặc chuỗi lấy theo master gần hơn.

## Ba nguồn hình
1. **Chữ hoa + số (bản vẽ designer):** nội suy ĐIỂM giữa hai bản vẽ Regular / Bold (`ref/interp.py` → `ref/designer_M.json`, src `interp`).
   - Ghép contour theo tâm và kích thước hộp bao, để không nhầm lòng với viền ngoài (lỗi số 0 ở bản đầu).
   - Căn điểm neo bằng quy hoạch động vòng. Khi một bên có thừa điểm neo, chia đôi đoạn dài nhất ở bên kia. Đoạn thẳng đổi thành cubic.
   - Chỗ nối trơn ở CẢ HAI master (< 4°) được ép liền tiếp tuyến (G1), vì nội suy tuyến tính có thể sinh gãy nhỏ.
   - Glyph nội suy không qua bước tidy mạnh. Tidy mạnh từng xoá mực ở N Medium.
2. **Chữ thường, dấu, dấu câu, ký hiệu (dựng theo luật):**
   - Mọi tham số số học nội suy bằng `lerp_w`: W, N_OFF, ARCH_*, S_SX, S_D, CAP_D, LV, HOOK_S / HOOK_T / HOOK_VEC…
   - Phần "Bold thêm vào" (B_STEM, B_BAR, B_THIN, B_JOIN, B_KG…) nhân với t (`lower.set_weight(w)`).
   - Các nhánh `if w == 'Bold'` trước đây đổi thành nội suy.
3. **Ký tự ghép** (Æ œ ß £ § þ µ ð…): dựng lại từ module của chính weight đó.

## Spacing / kerning
- `spacing.py` chạy cho cả 4 weight. SB_REF và SPACE được nội suy (space: Regular 230, Bold 245).
- Kerning tính riêng từng weight bằng cùng phương pháp min-gap.

| | Regular | Medium | SemiBold | Bold |
|---|---|---|---|---|
| Class / ngoại lệ | 4270 / 1823 | 4184 / 2060 | 4103 / 2282 | 3974 / 2407 |
| A · va chạm < 26 | 0 | 0 | 0 | 0 |
| C · cặp âm tiết Việt ≤ 12 hoặc do sàn | 5202 / 5214 | 5202 / 5214 | 5202 / 5214 | 5202 / 5214 |
| E · cặp gốc quá sát | 0 | 0 | 0 | 0 |

12 cặp lệch còn lại trong mục C giống nhau ở cả 4 weight: đó là các cặp sừng ư / ơ, đã chốt "giữ ư như cũ".

## QA bổ sung
- `qa_cover.py`: đủ 312 ký tự × 4 weight, xuất không lỗi.
- `qa_weight.py`: kiểm 324 ký tự.
  - Diện tích mực tăng NGHIÊM NGẶT R < M < SB < B.
  - Bề rộng mực và advance không giảm.
  - Bước đều: tỉ lệ hai bước liền nhau trong khoảng 0.6–1.6.
  - Kết quả: 0 lỗi.
- `qa_outline.py`: với glyph nội suy, góc được chấp nhận khi nằm giữa góc của hai master (±2°). Còn lại: điểm thẳng hàng ở A Medium và V SemiBold (vô hại), cùng hai góc cắt đã biết ở c và e Bold.
- `qa_kern.py`: chạy cho 4 weight.
- Trong quá trình làm, cặp ngoặc `{ }` từng bị mất ở các bản preview trước do mất dòng gán; đã khôi phục. `qa_cover` ra đời để bắt lỗi kiểu này.

## Việc sau
- Xuất OTF / TTF:
  - name ID 16 / 17 cho Medium và SemiBold;
  - GPOS kern và mark;
  - usWin bao Ẳ Bold 1051.
- Thêm tnum.
- Khi xuất variable font: master chữ hoa đã tương thích điểm sau bước căn của `interp.py`.

## Sửa sau khi có 4 weight (05/11)
- **ß, "vẫn dư nét dưới bụng":** lòng vòng dưới lệch trái (thành trái 0.35, thành phải 0.92 thân), nên đỉnh lòng ở `cxi = cxu − 0.285·thân`, không phải ở `cxu`. Trước đây eo và vòng dưới cắt ở `cxu`, để lại một bậc nhỏ dưới bụng. Nay cắt ở `cxi`: đáy eo chạy ngang rồi vào đúng tiếp tuyến ngang ở đỉnh lòng.
- **ß, "glyph dưới bị dính":** đầu cắt dưới-trái của vòng dưới trước chỉ cách mép loe chân thân 25 (Regular) và 8 (Bold). Nay cách đúng 50 ở mọi weight, theo luật khe nhỏ cố định theo Regular.
- **g Medium → Bold, "lỗi so với g Regular":**
  - Lòng bụng trên và lòng vòng dưới trước bị thay bằng một elip khớp gần đúng, làm mất hình lòng của bản vẽ (góc dưới-phải nặng ngay từ Medium). Nay lòng Bold = chính lòng Regular, thu nhỏ quanh tâm theo cùng hệ số `B_KG['g']`.
  - Nét nối và tai g trước được nở bằng stroke + boolean, sinh điểm thừa và bậc ở chỗ nối. Nay dùng `offset_path` (dời song song từng đoạn), giữ đúng số điểm của bản vẽ.
- **Æ, "lỗi glyph góc trái":**
  - Lỗi: đỉnh A (vượt lên 712) nhô trên thanh E, và loe trái đầu thân E chìa ra ngoài nét chéo.
  - Sửa: cắt cả khối ở mặt trên thanh E (cap 700). Phần trên 400 cắt theo mép ngoài nét chéo trái của A kéo dài, nên góc trên-trái là một góc nhọn ở đường cap.
- **Æ, "lỗi vòng khuyết":**
  - Lỗi: đỉnh lòng A nằm trái thân E, để lại một đoạn xiên ngắn từ đỉnh lòng xuống thân.
  - Sửa: lòng dựng lại thành tam giác giới hạn bởi mép trong nét chéo trái, mép trái thân E và mặt trên thanh A. Lòng có một đỉnh nhọn ở thân.

## QA độ dày nét toàn bộ glyph (designer 05/11: "đồng bộ hết độ dày các glyph", "đảm bảo không glyph nào lỗi nét")

### Công cụ: `tools/construct/qa_stroke.py`
- Đo bề dày theo trục giữa (medial axis) trên ảnh raster 0.5 px/u.
- Tỉa nhánh vào góc loe và đầu nét; bỏ vùng khớp.
- Các phép kiểm:
  - Chữ / số gốc: nét chính so với H / n / 0, lệch tối đa ±10 %.
  - Ký hiệu: trong ±10 % trung vị nhóm cùng luật. Bốn nhóm: gạch / toán, ngoặc, ký hiệu chữ, nháy thẳng.
  - Chéo weight: nét chính tăng R → M → SB → B, và tỉ lệ B/R khớp nhóm.

### Đã sửa
| Glyph | Trước | Sau |
|---|---|---|
| w | hai nét \ mảnh hơn v 11 % | dùng chung `thicken` với v x z (hàm mở rộng cho 4 mép) |
| e Medium → Bold | nhẹ hơn n tới 12 % | lòng co như o (`B_KG['e']`) |
| ~ ≈ | nét 116 / 90, gấp đôi nhóm toán (60) | cùng đường sin của dấu ngã, vẽ lại bằng bút nhóm toán, nét 0.60 V |
| – — | 0.9 × gạch nối | dày bằng gạch nối |
| { } | thân 0.70 V | 0.85 V, như ( ) [ ] |
| § | nét 66 (0.65 V) | nét 0.85 V (90), cùng nhóm ngoặc |
| vòng ̊ (Å å) | 0.34 V, mảnh hơn mọi dấu ~30 % | 0.66 N dấu, bằng đáy trăng |

### Móc dưới (U+0327, Ç ç) vẽ lại
Designer: "đuôi móc không giống các font cùng dòng".
- Cổ đứng mảnh.
- ¾ vòng elip (ering4): cong sang phải rồi về trái, mở hẳn về trái.
- Thành phải 0.62 thân thường; trên / đáy là nét mảnh.
- Đuôi phẳng mặt trên, cắt đứng thẳng hàng mép trái cổ.

### Còn lại, đã kiểm tay (không phải lỗi)
- 2 3 5 8: tương phản theo bản vẽ / luật số của designer. Đo trực tiếp thì thành bụng 3 5 Bold vẫn dày lên.
- Æ Bold, ‹ › Bold, ! ¡ ' “ ;: lệch do thước đo trên glyph nhỏ hoặc hình giọt. Đo trực tiếp thì thân / diện tích tăng đều.

## w vẽ lại từ module v (designer 05/11: "cân nhắc làm lại chữ w thường khác")
- **Bản cũ:** W hoa thu nhỏ, hai nét giữa bắt chéo. Ở x-height thành một cụm mực đặc với lòng tam giác nhỏ, nên w tối hơn các chữ thường khác.
- **Bản mới:** `derive.w_from_v`, hai module v ghép lại.
  - Mỗi v dựng như v (`shrink_caps`; nét \ dày = thân, qua `thicken`) nhưng hẹp hơn, `W_SX = 0.47` (v là 0.55).
  - Hai nét ngoài giữ loe của v. Hai nét trong bỏ loe, kéo thẳng theo mép nét.
  - Đỉnh giữa cắt phẳng ở x-height, rộng đúng bằng đáy nhọn của v.
- **Bề ngang:** w = 1.45 × v. Medium / SemiBold / Bold rộng hơn Regular đúng phần B_STEM (hai nét dày).

## Module loe đầu nét chéo, X V Y hẹp lại, k (05/11)

### Module loe đầu nét chéo
Designer: "đỉnh loe không nhọn như các module khác"; tham khảo module ở Figma 2138:1189.

- **Vector của designer** (đơn vị module cao 29, đo theo mép nét kéo dài):

  | Module | Mũi chìa | Điểm điều khiển gần mũi | Điểm điều khiển gần mép |
  |---|---|---|---|
  | Thân đứng | 8 | (1.5, t 8) | (0, t 13.5) |
  | Nét xiên 15°, phía góc tù | 10.2 | (1.45, t 6) | (0, t 13.5) |
  | Nét xiên 15°, phía góc nhọn | 5.8 | (−2.9, t 8): lấn vào mép, tạo đoạn lồi nhỏ rồi mũi nhọn | (0, t 14) |

- **`derive.flare_ends`:**
  - Một cubic từ mép tới mũi; nội suy theo độ ngả λ = ngả / 0.268.
  - Phía tù: mũi 8 + 2.2λ. Phía nhọn: mũi 8 − 2.2λ, điểm điều khiển 1.5 − 4.4λ.
  - Quy ra font: t × 69.8/29 (bằng chiều cao loe thân H), u × 22.7/8 (bằng độ chìa loe H).
  - Cắt từ chỗ mép thẳng của bản vẽ dừng, nên không sót bướu của loe cũ.
- **Áp cho:** đầu trên V Y, đầu trên + chân X, chân A, đầu tay (/) + chân (\) K. Chạy ở cả hai master Regular / Bold (`ref/narrow_caps.py`); Medium / SemiBold nội suy lại.
  - Trước đây K Regular có móc loe ở chân còn K Bold cắt nhọn, nên Medium / SemiBold nội suy ra vát xiên ("lỗi nét chân chữ k").
- **Chữ thường v x y w k:** dựng từ chữ hoa nên tự theo module.

### X V Y hoa hẹp lại
Designer: "giảm bề ngang chữ X hoa 1 chút", "các chữ XVY hoa giảm bề ngang lại".

- Co ngang × 0.92 quanh tâm. Y chỉ co phần tay; góc tay gặp thân là giao của mép tay mới với mép thân đứng.
- Nét chéo dốc hơn thì mỏng đi, nên dời song song hai mép (`thicken`) để bề dày vuông góc bằng bản gốc.
- Bề ngang mới: V 672 → 624, X 642 → 597, Y 632 → 586 (Regular).
- Bản vẽ gốc giữ ở `designer_AB_orig.json`; chạy lại script luôn đi từ bản gốc.
- v x w thường giữ bề ngang cũ: sx được giải theo bề ngang đích 411 / 423 / 596.

### k
- **Kerning:** designer thấy "kerning chữ k và i hơi xa".
  - Lề phải k chỉ còn 14, nhưng giữa đầu tay và chân là khe chữ V sâu (khoảng trắng trung bình của ki là 218, so với ni 116).
  - Rút lề phải k thêm 12 (`spacing.NOTCH_RS`).


## Cập nhật sau phản hồi (05/11, muộn)

### Bỏ module loe dựng lại và phép thu hẹp X V Y
Designer: "hư hết rồi — coi lại bản gốc", "bản của bạn lỗi quá".

- Loe đầu nét chéo của bản vẽ gốc (Figma 2138:1200) đã đúng module 2138:1189: phía góc tù loe dài, phía góc nhọn lồi nhỏ rồi mũi nhọn. Bản dựng lại loe theo module (mục "Module loe đầu nét chéo" ở trên) đã bỏ; A K trở về bản vẽ.
- Phép thu hẹp X V Y (dời song song mép nét) làm méo loe, nên đã tắt (`narrow_caps.NARROW = {}`). V X Y giữ đúng bản vẽ gốc.
- **V Bold** lấy bản designer vừa vẽ (Figma 2138:1203): xoay 180°, x = (w − x)·k, y = y·k − 11.3 với k = 711.3/251. Cùng cách quy đổi này cho ra V Regular (6:646) trùng từng điểm với dữ liệu hiện có.

### Chân K / k đồng bộ 4 weight
Designer: "chân các chữ k và K các weight không đồng bộ", "chân góc nghiêng nó phải cong như này".

- Phía góc nhọn của chân (bên trái nét \): mép đi theo nét xuống tới khoảng 45 u trên đường chân, gù nhẹ rồi vòng về mũi. Mũi chìa 23 u ra ngoài đầu mép kéo dài, bằng độ chìa loe thân H.
- Cùng số đo ở K Regular và K Bold. Medium / SemiBold nội suy theo; k thường dựng từ K nên theo luôn.
- Đầu tay k = đầu nét / của v (`derive.graft_top`), cùng module loe nét xiên.
- `interp.lerp`: điểm nằm trên đường chân / cap ở một master và sát đường đó (< 20) ở master kia thì đặt lên đường đó, để không nội suy ra vát xiên.

### R, M
- **R "hở bụng":** đường cong đáy bụng dừng ở x 293 (Bold 337), rồi đi ngược tới đầu chân ở 311 (Bold 366), để lại khe nêm. Đã lấp bằng tam giác nằm trong mực.
- **M Bold "chân lỗi":** mép trong thân phải thiếu loe (`L487.4 0 L487.4 547`). Đã thêm loe như M Regular: chìa 22.6, cao 69.8.
- **Kiểm toàn bộ chân / đỉnh thân 26 chữ hoa:** loe khớp giữa Regular và Bold. Các khác biệt còn lại (C E F G L T Z) là mép cắt đầu tay / thanh, do designer vẽ Bold cao hơn, không phải loe thiếu.

### @
Designer: "kiểm tra lại vòng khuyết trong của chữ @".

- Elip lòng xoay vượt qua mép thân, cắt vào đoạn thân đang uốn, làm mép lòng gãy.
- Nay lòng giữ trọn một hình, chỉ bóp phẳng theo mép trái thẳng của thân (đo ở cao 400), như lòng a thường.

### Đơn giản hoá outline cho variable (`compat_masters.py`, gọi cuối `build.py`)
Designer: "Simplify lại để dễ làm variables".

1. Đơn giản hoá từng master:
   - bỏ điểm thẳng hàng (lệch < 0.35 u) và đoạn < 1.2 u;
   - gộp hai đoạn cong (hoặc thẳng + cong) nối trơn (gãy < 10°) khi một cubic khớp sai số < 1.5 u.
2. Ghép cặp Regular ↔ Bold: cùng số contour, cùng chuỗi đoạn.
3. Đơn giản hoá đồng thời hai master: chỉ bỏ điểm bỏ được ở cả hai.
4. Medium / SemiBold = nội suy đúng 1/3, 2/3. Cả 4 weight cùng cấu trúc điểm.

Kết quả: 6 691 → 5 723 đoạn mỗi weight. Ví dụ o: 4 + 4 đoạn; n: 17; H: 20.

### Kerning (QA theo skill dizai-serif-qa)
- **Khe ≥ 26:** đạt mọi cặp, 4 weight.
- **Âm tiết Việt (5 214 cặp × 3 kiểu viết):** 12 cặp lệch > 12, đều là ơ + t / y (sừng chạm).
- **Cặp có dấu lệch cặp gốc:** chỉ còn chữ có sừng đứng trước chữ hoa có nét chéo (ơY, ờV…), tổ hợp hiếm trong tiếng Việt. Sừng chặn.
- **ƯA "hơi xa":** khe chân U / Ư + A là 134, gấp đôi HA (67). Kéo thêm 20 (`spacing.KADJ`), ƯA = UA giữ luật ơn = on.

### Kerning theo skill DINHTUONG60s (type-qa-qc §3.1, S1c)
Designer: "hãy dùng skill kerning của Dinh Tuong đã đo sẵn". Thay cho các chỉnh tay ở trên: lề A, lề k, UA / AU / ƯA.

- **Đo trắng cặp W(a, b)** (`ref_kern.white`): khe giữa hai mép mực ngoài cùng, cộng trắng mỗi phía đo từ mép mực ngoài cùng của chính chữ đó. Mỗi phía chặn ở D = 0.12 × x-height. Lấy trung bình theo cao độ: vùng x-height nếu cặp có chữ thường, vùng cap nếu không.
- **Tỉ số:** W(a, b) / W(n, n) hoặc / W(H, H).
- **Tham chiếu** (`ref_kern.py`): 4 font serif có sẵn (Liberation Serif, DejaVu Serif, Caladea, FreeSerif), Regular + Bold, tính cả kerning GPOS của chúng. Đo cho 3 844 cặp A–Z a–z 0–9 → `out/construct/ref_ratios.json`.
- **Kern Đìzai** (`spacing.py`):
  - Mọi cặp chữ / số: kern = tỉ số tham chiếu × W(n n | H H) − W(a, b, kern 0).
  - Tỉ số dùng trung bình Regular + Bold cho cả hai master; Medium / SemiBold nội suy.
  - Ư Ơ ư ơ dùng cặp gốc.
  - |k| ≤ 0.4 advance của chữ hẹp hơn; làm tròn về phía rộng; va chạm ≥ 26 (sừng 14) chặn ở bước sau.
- **Kiểm** (`pair_white.py`): Regular 3 580 / 3 844 cặp trong dải tham chiếu, 0 cặp chật đáng kể; Bold 3 589.
  - Còn thưa: chéo × chéo (vv yy RA KA XA AA WW rv…). Loe chân hai chữ chạm sàn 26 trước khi phần trên khít như tham chiếu (serif tham chiếu cho chân gần chồng nhau). Đây là giới hạn của sàn.
  - Ví dụ Regular: AT / TA 0.90 → 0.25 / 0.29 (tham chiếu 0.24 / 0.26); OO 1.11 → 0.90 (0.86); ki 0.92 (0.86).
- **qa_kern:**
  - va chạm 0;
  - âm tiết Việt: 0 cặp lệch > 12 ngoài sàn (trước 12 cặp ơt / ơy);
  - cặp có dấu lệch cặp gốc: 402 → 138 (Regular);
  - kern giữa 4 weight nhất quán.

### g, £ (05/11)
- **Vòng dưới g:** designer thấy "hông bụng dưới chữ g hơi nhọn cho độ cong lài hơn".
  - Elip 144 × 88 px với κ 0.552 cho bán kính cong ở hông chỉ ≈ 27 px.
  - Đổi sang siêu elip: tay nắm đứng ở hông κ 0.68, tay nắm ngang ở đỉnh / đáy 0.58. Lòng 0.62 / 0.56 để thành vòng vẫn đều.
- **£ vẽ lại lần 2:** designer muốn "giống các font khác nhưng đồng bộ concept". Lấy cấu trúc £ của font serif, dựng bằng module Đìzai:
  - móc trên: nửa trên vòng elip, cắt đứng như đầu nét trên C;
  - thân 0.9 V; chân là ¼ vòng elip đồng tâm cong sang trái, liền tiếp tuyến vào đáy;
  - thanh đáy dày bằng nét mảnh; đầu phải đúng hai cubic đầu tay dưới E (Figma 6:924);
  - thanh giữa ở 300, đầu phải cắt xiên như thanh giữa E.

## Thu hẹp X V Y hoa (05/11)

Designer: "giảm bề ngang X, Y, V hoa". Không làm đậm / co cả glyph (làm méo loe). Dùng **nghiêng từng nét** (`ref/narrow_caps.py · shear_narrow`, FRAC 0.08 bề ngang):
- mỗi nét chéo = dải giữa hai mép thẳng của nó (kéo dài, nới 6 u) + vùng đầu nét (loe) → nghiêng một chiều quanh điểm gốc: V quanh đáy, X quanh tâm giao, Y quanh đỉnh thân (cột thân + chân giữ nguyên);
- V / Y: dưới nách chia theo đường từ đáy lòng tới điểm gốc; X: chỉ nới dải xa tâm giao (> 120 u) để không khấc;
- sau phép hợp, bỏ gai mảnh (hai đoạn thẳng gần trùng hướng < 4°) — X Regular từng có gai sợi ở nách phải.
Loe, nhát cắt ngang, độ dày nét giữ nguyên. Bề ngang: V 672→618 / 683→628 · X 642→591 / 665→612 · Y 632→584 / 655→605 (Regular / Bold); Medium, SemiBold nội suy. v x y w thường không đổi.

## Cặp tròn × A (05/11)

Designer: "ĐÂ, ĐĂ và ĐA kerning vẫn hơi xa". Trắng cặp theo tham chiếu cho DA / OA / AO khe mực nhỏ nhất 128–136 u ≈ 1.5 × khe HH (86): nêm trắng của A cộng bụng tròn thành lỗ. Luật mới (`spacing.py`, ROUND_A = 1.0): cặp D O (Đ Ð Ơ… theo chữ gốc) + A và A + O C G Q kéo vào tới khi khe mực nhỏ nhất ≤ khe HH. Kết quả DA −55 → −95 (Bold −100), OA −105, AO AC AG AQ −95 (Bold −100); áp cho mọi biến thể dấu (ĐÂ ĐĂ ĐẠ ĐÀ ĐOÀN…). Va chạm 0, âm tiết Việt không đổi, 4 weight nhất quán.
Mở rộng (designer: "siết luôn các cặp OV DY theo luật đó"): luật áp cho mọi chữ chéo / tay vươn WEDGE_X = A V W Y T, hai phía. Regular / Bold: OV −90/−100 · DV −85/−95 · OW −85/−90 · DY −110/−115 · OY −125/−120 · OT −80/−50 · VO −95/−80 · WO −90/−95 · YO −130 · TO −80/−55 (Bold T đã sát do tay T dày). Va chạm 0, âm tiết Việt không đổi.

## Bản variable + Italic (05/11)

Designer: "làm bản variable luôn nhé, thêm cả Italic". `tools/construct/export_font.py` (sau `spacing.py`) → `fonts/`:

| Thư mục | Nội dung |
|---|---|
| `fonts/variable/` | `DizaiSerif[wght].ttf`, `DizaiSerif-Italic[wght].ttf` — trục wght 400–700, instance Regular 400 · Medium 500 · SemiBold 600 · Bold 700; STAT có trục `ital` (Roman ↔ Italic liên kết) |
| `fonts/otf/`, `fonts/ttf/` | 8 bản tĩnh `DizaiSerif-{Regular, Medium, SemiBold, Bold}[Italic]` |

- **Master**: Regular + Bold (outlines.json sau `compat_masters.py`, cùng cấu trúc ở cả 324 glyph). Medium / SemiBold không là master: outline, dịch outline, advance và kerning của chúng = ĐÚNG nội suy hai master (spacing.py) → bản tĩnh trùng khít bản variable.
- **Chiều contour** chuẩn PostScript theo độ lồng (58 contour ở 44 glyph do designer vẽ chiều kim đồng hồ được đảo cùng chỉ số ở hai master).
- **Kerning**: class → groups `public.kern1/2`; 5 287 ngoại lệ chống va ghi tường minh ở cả hai master. Ngoại lệ tương thích variable: cặp nào nội suy ở M / SB chặt hơn mức chống va thật thì nới cả R / B (59 cặp, theo đơn vị 1 u). Hệ quả nhỏ: Tĩ / Vĩ Regular, ư + i m n SemiBold thưa hơn cặp gốc 17–33 u.
- **ccmp**: chuỗi NFD (gốc + dấu tổ hợp, kể cả hai dấu như ấ = a + ̂ + ́, ợ = o + ̛ + ̣) → chữ dựng sẵn.
- **Vertical metrics** một bộ: typo = hhea 960 / −240 (dòng 1.2 em, USE_TYPO_METRICS), usWin 1070 / 246 bao chồng dấu cao nhất (1060) và đuôi thấp nhất (−236).

### Italic I1 — roman nghiêng có hệ thống

Chữ glyphic loe nét có tiền lệ italic là **roman nghiêng** (Optima Italic, Palatino Sans Italic), không phải chữ viết tay. I1: mọi glyph nghiêng 10° quanh đường y = ½ x-height (247.5). Vì mọi glyph nghiêng như nhau quanh cùng một đường, khe giữa hai chữ ở mọi cao độ giữ nguyên → spacing / kerning / chống va của Roman đúng tuyệt đối cho Italic. post.italicAngle −10, caret slope 1000 / 176.

Cần designer duyệt cho I2 (italic thật): a một tầng, e / c thu hẹp, f có đuôi xuống, nét nối ra ở chân n m h u, góc nghiêng 10° hay 12°.

### QA trên chính file font (`qa_font.py`, HarfBuzz)

Variable ở wght 400 / 500 / 600 / 700 và 16 bản tĩnh: advance khớp spacing.json, kerning mọi cặp khớp kerning.json (lệch ≤ 1 u), NFD = NFC, hộp bao glyph của instance = outlines.json (≤ 1.6 u, Italic so với Roman nghiêng 10°).

## ™ dựng lại (05/11)

Designer: "kiểm tra lỗi của glyph này" (™). Lỗi: T M thu 0.42 rồi làm đậm ĐỀU mọi phía 0.09 V → nét mảnh dày gấp đôi, chéo mảnh của M nặng gần bằng thân, mép chéo hết song song. Dựng lại: T M của master **Bold** thu 0.42 (thân 0.42 × V_B ≈ 0.57 V Regular, giữ tương phản bút dẹt); weight đậm hơn chỉ làm dày **theo phương ngang** (cộng Minkowski với đoạn ngang, `xdilate`), thân tăng theo V_w / V_R; đáy nhọn của M bị cộng thành đoạn phẳng thì kéo dài hai mép chéo tới giao điểm (`sharpen`). Nét ngang, loe và mép chéo song song giữ nguyên.

Designer: "Module T trong cụm TM vẫn lỗi mà". Lỗi thứ hai nằm ở bước dọn outline `ref/tidy.py` (glyph dựng theo luật): luật "gai = mẩu < 12 u quay ngược > 150°" xoá mất chóp mỏ tay phải của T trong ™ Regular (đoạn cong 11.5 u gãy gắt vào mép đứng) → tay phải T vát xiên. Sửa luật: chỉ xoá khi phần bỏ đi gần như không có diện tích (tam giác < 30 u², sợi thật); mũi nhọn có diện tích giữ nguyên. Build lại: chỉ ™ đổi (so outlines.json trước / sau), không glyph nào khác bị ảnh hưởng.

Trang preview có thêm mục **Font variable** (hai file woff2 nhúng trong trang): thanh trượt wght 400–700, Roman / Italic, ô chữ sửa được, bảng 8 kiểu.

Designer: "Medium vẫn lỗi module T", "Semi bold và bold module T bị kéo dài quá". Lỗi thứ ba: cộng Minkowski ngang biến chóp mỏ T thành đoạn phẳng 2dx, bước `sharpen` (chỉ dành cho đáy chữ V của M) bắt nhầm và kéo mép đứng đầu tay xuống thêm ~50 u ở SemiBold / Bold; Medium là nội suy nên méo theo. Sửa: T không dùng boolean nữa — **dời điểm** thân + loe chân (dưới mặt thanh, trong cột thân ± 14 u) sang hai phía ±dx; tay, mỏ, thanh giữ nguyên module T hoa; cùng cấu trúc điểm ở mọi weight nên Medium / SemiBold nội suy thẳng thân. `sharpen` chỉ áp cho M (Regular M cũng qua cùng phép 0.3 u để hai master cùng cấu trúc).
