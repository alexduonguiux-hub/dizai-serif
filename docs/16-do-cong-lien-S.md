# 16. Đường cong S s — S Regular + Bold vẽ lại theo vector của designer; S18 nội suy liền tiếp tuyến

## Diễn biến (06/11)

1. Designer: "Các đường cong của chữ s và S. Cảm giác không smooth lắm" (ảnh cắt cực trái bụng trên S).
2. Đo: đường liền tiếp tuyến (G1) nhưng bán kính cong nhảy ở điểm cực, ví dụ cực trái bụng trên S Regular 129 / 473 (×3.7).
   Đã thử luật **S17 độ cong liền G2** (`font/fair.py`): chỉnh độ dài tay nắm để bán kính hai bên mỗi nút bằng nhau.
3. Designer: "bây giờ bụng nó lại không cong tròn tự nhiên".
   G2 kéo dài tay nắm ở chính các góc tư bụng (cung gần elip), làm bụng phình vuông.
4. Designer tự vẽ lại S Regular + Bold trên Figma ("Đọc vector mẫu ở đây", "mình vừa chỉnh lại nét"):
   file `gGrYT5oldAplC9IedaAj7b`, node `2145:1225`.

## Kết luận

- **Bản vẽ của designer là chuẩn.** S17 **tắt**: `compat_masters.FAIR = set()`. Code `font/fair.py` giữ lại để tham khảo.
- Vector của designer **không** G2: tỉ lệ bán kính hai bên một số nút vẫn ×3–4. "Tròn tự nhiên" theo mắt quan trọng hơn chỉ số G2.
  Không dùng G2 làm luật tự động cho bụng chữ.
- `ref/figma_S.py` ghi vector vào `designer_B.json['S-Bold']`.
  - Quy đổi: x = 2.8341·X − 0.04, y = 711.34 − 2.8341·Y, giải từ 4 góc đầu nét không đổi; sai < 0.1 u.
  - S Bold trong font khớp vector: lệch 0.00 u.

## Điều designer đã đổi ở S Bold (so với bản trước)

| Chỗ | Trước | Sau |
|---|---|---|
| Nút sống (bụng trên → sống, mép trên) | (361.5, 374.5) | (321.6, 385.4), tay nắm dài theo hướng sống |
| Cực phải bụng dưới | y 170.4 | y 178.9 |
| Đáy lòng dưới | (232.4, 55) | (215.4, 56.7) |
| Lòng phải bụng dưới | cực trị (320.2, 164.7) | điểm xiên (328.7, 140.3) |
| Cực trái bụng trên | y 555.1 | y 549.4, tay nắm trên dài 87 → 107 |
| Tay nắm đáy ngoài | 101 | 126 |

Hệ quả:
- **Sống S Bold mỏng đi:** đường kính nội tiếp giữa sống 146 → 131. SemiBold 133 → 123. s Bold 118 → 106, vì s là S thu nhỏ.
  Đã bù bằng luật S19 bên dưới.
- Medium / SemiBold nội suy lại (`ref/interp.py`). s, $, Š, š, § đi theo S.
- S Regular: designer gửi tiếp (node `2145:1235` trong Frame `2145:1228`). Cùng phép quy đổi, ghi vào `designer_A.json['S-Regular']`.
  Điểm nối bụng trên → sống và cực trái bụng trên đổi như bản Bold. Lòng dưới gọn hơn: đáy lòng (181, 24), lòng phải (297.5, 164.7).

## S18 Nội suy liền tiếp tuyến (designer 06/11: "bụng s medium và semi bold lỗi")

- **Lỗi:** hai master ghép điểm neo theo thứ tự.
  - s Regular neo ở cực phải bụng dưới (349, 123). s Bold, thu nhỏ từ S Bold mới, neo ở chỗ xiên (311, 31).
  - Medium / SemiBold nội suy giữa hai hướng tiếp tuyến khác nhau nên gãy 14° / 13° ở mép ngoài bụng dưới. Đó là chỗ phồng designer thấy.
- **Sửa** (`compat_masters.reanchor`), chỉ ở nút mà bản nội suy giữa gãy > 2°:
  1. Một master neo ở cực trị, master kia neo xiên → dời nút của master kia về cực trị cùng trục, trên chính đường cong của nó.
     Cắt de Casteljau và khớp lại phần còn lại, sai số ≤ 2.5 u.
  2. Cả hai master đều xiên → đặt tỉ lệ tay nắm vào / ra của hai master bằng nhau. Chỉ nhận khi master lệch ≤ 2.5 u.
  3. Hai đoạn thẳng: một master thẳng hàng, master kia có góc (góc đầu nét dưới s Regular có bậc ngang 5 u) → đặt điểm chia theo tỉ lệ độ dài của master có góc. Hình master không đổi.
- **Kết quả:** gãy ở Medium / SemiBold về 0 ở s š ơ ư (và mọi chữ có sừng) k ç £ § ® W.
  - Master xê dịch ≤ 2–3 u. S Regular / Bold giữ đúng vector designer (S chỉ gãy 1.3° < ngưỡng).
  - Còn lại & (20°), @ (22°), Š (7°): không sửa được trong giới hạn 2.5 u, cần vẽ lại điểm neo tương ứng.

## S19 Bù đậm S Bold (designer 06/11: "đo lại cân bằng weight với các ký tự cùng weight xem cần chỉnh không")

Đo qa_stroke: T = phân vị 97 bề dày nét, chia cho nét đứng chuẩn của weight (H).

| | Regular | Bold trước | Bold sau S19 |
|---|---|---|---|
| S | 1.04 | **0.96** | **1.05** |
| C G O D B R (hoa cong) | 1.02–1.04 | 1.04–1.06 | — |
| s (S thu nhỏ) | 0.96 | 0.91 | 0.98 (o 0.96) |

- **Sửa** (`ref/figma_S.py`, `S19_DELTA = 6`): giữ dáng vector của designer, làm đậm đều bằng offset song song Tiller–Hanson.
  - Dời từng cạnh đa giác điều khiển ra ngoài 6 u rồi giao lại. Không thêm điểm neo, nên Medium / SemiBold vẫn nội suy.
  - Mặt cắt đầu nét giữ nguyên đường. Góc = giao của đường cong đã dời với mặt cắt.
  - Co dọc về đúng cao cũ (−14.2 … 711.3). Bề ngang tăng 12 u (bụng dày ra hai phía; co ngang làm đầu cắt lệch so với bụng).
- **Kết quả:** S tăng đều 1.04 / 1.03 / 1.03 / 1.05 qua 4 weight. qa_stroke 0 lệch chéo weight.

## S18b–c Ghép cặp nội suy (designer 06/11: "&, @ và Š vẫn còn gãy ở Medium/SemiBold" → "bạn đề xuất")

- **Š:** phép hợp S ∪ dấu móc chia lại / xấp xỉ lại đường cong S (Š Bold lệch S Bold 3.5 u, thừa một điểm neo).
  - Sửa: `vn_punct.U` ghép contour, không hợp, khi hai hình rời nhau. Chữ có dấu giữ đúng hình chữ gốc.
  - `compat_masters`: contour trùng hình chữ gốc dùng lại cặp đã ghép của chữ gốc (S18b).
- **@ (chân thân a):** góc nằm cùng chỗ ở hai master, nhưng Regular đặt ở điểm 1, Bold ở điểm 2. Ghép cặp chỉ so vị trí + tiếp tuyến nên lệch một bậc; SemiBold gãy 55°.
  - Sửa: `interp.align` phạt 0.12 khi ghép neo góc với neo trơn (S18c). Lệch cấu trúc góc↔trơn toàn font 27 → 17. @ Ç Œ ß hết lệch.
- **Nút trơn kề nhau:** dời một nút làm nút kề gãy thêm (s 1° → 4.6°). `reanchor` chạy lặp tới khi ổn định.
  - Cả hai master neo xiên nhưng cùng cung có cực trị → dời cả hai về cực trị. Sai số khớp ≤ 3.6 u.
- **ß:** Regular có đoạn cong 4 u ở mũi đuôi mà Bold không có. Gộp đoạn tí hon (< 5 u) sát góc vào đoạn sau (`drop_stub`).
- Ghép contour (U không hợp) phải chuẩn hoá chiều theo độ lồng (`vn_punct.orient`). S18b dùng lại cặp chữ gốc thì đảo theo chiều contour của chữ. Nếu không, QA diện tích Ấ Ơ À báo không đơn điệu.
- Nét thẳng chia hai đoạn ở hai master với tỉ lệ khác nhau → cùng tỉ lệ (điểm trượt trên đường).
- **Còn lại** (khác thiết kế giữa hai master, chờ designer): & nách bụng – chân (Regular khấc sắc, Bold bo tròn), 5, M, N, g, x, ®, s (bậc 5 u ở góc đầu nét dưới Regular).

## Đ mất phần thanh trong lòng (designer 06/11: "Chữ Đ bị mất nét trong" — "nét này có 1 bên")

- **Lỗi do S18b:** hàm so khớp hình chỉ kiểm tra một chiều (mọi điểm lòng D nằm trên lòng Đ). Lòng Đ = lòng D + khuyết do thanh ngang ăn vào, nhưng vẫn bị coi là "trùng" và bị thay bằng lòng D, nên thanh chỉ còn bên ngoài thân.
- **Sửa:** `_same` so HAI CHIỀU (Hausdorff, < 1.5 u). Đ / Ð có lại thanh vào trong lòng 0.9 V như luật.
- **Kiểm tra:** so ảnh mọi glyph với bản trước S18b. Chỉ các chữ cố ý đổi khác nhiều (£, nhóm S); không chữ nào mất chi tiết.

## & — hai master cùng cấu trúc (designer 06/11 duyệt đề xuất)

- Các "khấc" 3–5 u ở nách bụng – chân thật ra là **bậc thừa** của phép hợp: mép tay gặp mép bụng lệch 3 u.
  - Regular có 3 bậc, Bold có 2, nên ghép cặp lệch.
- **Sửa** (`compat_masters.dejog`): bỏ đoạn bậc < 6 u nằm giữa hai góc ~vuông khi hướng vào / ra lệch < 50°; nối hai mép ở trung điểm (dời ≤ 3 u).
- **Kết quả:** & hết lệch cấu trúc. Đổi kèm g, Œ (bậc cùng loại, ≤ 3 u). Lệch cấu trúc toàn font 17 → 13.

## S20 Đồng bộ cấu trúc Regular ↔ Bold cho các chữ còn lại (designer 07/11 duyệt đề xuất)

| Chữ | Trước | Sửa | Ở đâu |
|---|---|---|---|
| 5 | Regular khấc vát 13.4 × 15.5 u chỗ chân thân gặp vai bụng; Bold phẳng | Bold có cùng khấc: mép phẳng dừng 73.1, vát lên (86.5, 414.7) | `ref/fix_struct_bold.py` |
| M | Bold loe đỉnh thân trái ngắn (từ 665.6), gãy 18° | Bold dùng module loe chuẩn (630.2 → 7.7 686.5 → 0 700) như Regular | `ref/fix_struct_bold.py` |
| N, Ñ | Regular khấc V 14 u ở hai đỉnh chéo; Bold bậc 5.8 u | Bold khấc 14 u, chân lệch 5.6 u; cạnh chéo xoay ~0.8° | `ref/fix_struct_bold.py` |
| g | Bold gai 8 u (quay 149° / 153°) ở cổ nối vòng dưới | bỏ gai, nối trơn; chia đôi đoạn trước để giữ số đoạn | `compat_masters.sync_struct` |
| s, š | Regular bậc ngang 5 u sau góc đầu nét dưới | góc về cuối cạnh đứng, đoạn cong bắt đầu tại góc | `compat_masters.sync_struct` |
| x | Regular nách là một đỉnh; Bold mặt nách 7.5 u | Regular có mặt nách cùng hướng, cùng dài, trên hai cạnh | `compat_masters.sync_struct` |

- **Kết quả:** lệch cấu trúc góc ↔ trơn toàn font **0** (trước 27).
- **Ghi chú:**
  - N Bold: hai đầu cạnh chéo dày hơn ~5 u do cạnh xoay để có khấc V (qa_stroke B/R 1.52).
  - 5 Medium và 3 Medium: nét chính thấp hơn chuẩn ~10% (cờ có từ trước).
- Ảnh: `docs/img/structure-fixed.png`.

## S21 Cân nét chéo chữ hoa Bold (designer 07/11: "N hơi nặng … kiểm tra lại các độ dày của các chữ bold khác")

**Đo**: mép thẳng song song, khoảng cách vuông góc; chỉ nhận cặp có mực ở giữa.
- Chữ hoa Regular: nét chéo dày đều 0.97–1.00 × thân (chân R 0.89).
- Chữ hoa Bold lệch tới ±10%. Thân Bold là 140.

| Nét "\" dày Bold | A | K | M | N | R chân | V | W | X | Y |
|---|---|---|---|---|---|---|---|---|---|
| trước | 146 | 146 | 146 | 152 | 141 | 129 | 146 | 137 | 151 |
| sau (= Regular × 140/102) | 137 | 137 | 135 | 137 | 124 | 138 | 140 | 135 | 142 |

- Nét chéo mảnh chữ hoa Bold trước 65–80, sau 70 (0.5 thân = nét ngang Bold).
- Chữ thường Bold đã đều (k v w x y z: dày 124–125, mảnh 63–64), không đổi.
- Thân, nét ngang, chữ tròn đều sẵn.

**Cách làm** (`ref/balance_diag.py`, đi từ bản lưu `designer_B_prediag.json`):
- Dời song song HAI mép của nét, mỗi mép ½ lượng chênh, giữ trục nét.
- Mép gồm nhiều đoạn thẳng hàng thì dời cả nhóm. Đoạn thẳng hàng kề và loe nối trơn đi theo mép.
- Đầu mép trên đường chân / đỉnh trượt ngang. Giao vọt xa thì chỉ tịnh tiến. Lặp 6 lượt cho các nét chung đỉnh.
- N riêng: hai khấc V (14 u) cố định chân khấc dưới (453.5, −11.3) và trên (102, 711.3). Nét chéo xoay ~1° quanh hai điểm đó để dày 137.

**Ghép cặp chữ có dấu** (S18b), sửa kèm:
- So khớp với cặp GỐC của chữ gốc (trước khi dời neo), dùng lại cặp ĐÃ dời. Ngưỡng 3 u, vì đơn giản hoá mỗi bên lệch ≤ 1.5 u.
- Chỉ áp cho chữ ngoài ASCII. Trước đó A Bold dời neo nhiều hơn nên À … Ặ không khớp, nội suy gãy.

**Kết quả:**
- Lệch cấu trúc 0. qa_font 0 lệch, qa_weight 0, kerning va chạm 0.
- Đổi: A K M N R V W X Y Bold + chữ có dấu + ¥ Æ ® ™.
- Ảnh: `docs/img/bold-diagonal-balance.png`.

## S22 Các chỗ còn lại (designer 07/11: "sửa luôn các chỗ còn lại")

| Chữ | Đo | Sửa |
|---|---|---|
| 3, 5 | thành bụng dưới (đo ngang tại cực phải) 95 → 93 u (R → B) — KHÔNG dày lên; 6: 92 → 130 | `ref/fix_fig_bowl.py`: giữ mép ngoài, dời mép lòng thành phải vào (d·min(0, nx)); thành bụng Bold = 130 như 6 |
| J | nét đáy móc 40 u ở cả 4 weight (U: 40 → 79) | `ref/fix_struct_bold.py`: mép lòng đáy móc + đầu cắt trái nâng 28.3 u → đáy 68 = nét ngang Bold |
| W | mặt đáy đỉnh nhọn Bold 12.5 < Regular 20 (V 24 → 34) | `balance_diag.fix_flats`: mặt đỉnh Bold ≥ Regular × 140/102 → 27.5 |
| a | qa_stroke "nét chính −10 %" | **báo nhầm**: thân a = thân n ở mọi weight (102 / 109 / 117 / 124); bụng a tăng × 1.29 như o, d — không sửa |

- Kết quả: chỉ 3, 5, J, W đổi (Medium + Bold). Lệch cấu trúc 0. qa_font 0 lệch, qa_weight 0, kerning va chạm 0.
- Ảnh: `docs/img/bold-3-5-J-W.png`.
- Cờ qa_stroke CÓ TỪ BẢN VẼ Regular, chưa sửa (chờ designer):
  - 2 Regular nét chính 96 so với 0 111 (−13 %);
  - 8 Regular 97 so với 111 (−12 %);
  - 4 tỉ lệ Bold / Regular 1.38 (chuẩn số 1.24).

## S23 Cân độ đậm số 2, 8, 4 (designer 07/11: "cân lại 2, 8, 4 luôn")

Đo độ dày lớn nhất từng nét (Regular → Bold): bụng 0 / 3 / 6 = 111 / 107 / 102 → 139 / 143 / 136.

| Số | Trước | Sửa (`ref/fix_fig_weight.py`, từ bản lưu `designer_B_prefig2.json`) | Sau |
|---|---|---|---|
| 2 | bụng 97 → 130 (nhẹ ~9 % ở cả hai master) | làm đậm NGANG Tiller–Hanson (`symbols.hdilate`, chỉ nét đứng): Regular +10, Bold +9; chiều cao, đường chân, đỉnh giữ nguyên; góc chân trái tay nắm suy biến như Regular (móc 3 u của bản vẽ Bold sinh gai khi nội suy) | 106 → 138 |
| 8 | bụng dưới 98 → 132, bụng trên 86 → 106: tỉ lệ trên / dưới Regular 0.88, Bold tụt còn 0.80 | làm đậm ngang Regular +9, Bold +7; Bold: lòng trên (lòng GỐC, thay sau khi làm đậm) thu quanh tâm −20 ngang / −10 dọc | trên / dưới: R 96 / 107, B 122 / 139 (0.90 / 0.88) |
| 4 | qa_stroke "B/R 1.38" | **báo nhầm**: qa_stroke so 4 với 0 (nét tròn); thân 4 = thân 1 (104 → 143 ≈ 102 → 140) — sửa qa_stroke (`STEMFIG`: 4 so với 1), không sửa hình | — |

- ? ¿, dấu hỏi dựng từ số 2 GỐC, & dựng từ số 8 GỐC (`ref/designer_Q.json`) — giữ hình đã duyệt.
- Kết quả: so từng glyph với bản trước, chỉ `two`, `eight` đổi (4 weight). Lệch cấu trúc 0; qa_outline 2, 8 sạch; qa_font 0 lệch, qa_weight 0, kerning va chạm 0; qa_stroke chỉ còn cờ báo nhầm của a.
- Ảnh: `docs/img/s23-so-2-8.png`.
- Ghi chú: từ S21, `lower/derive.py` dừng ở x → chữ thường chưa theo chữ hoa S21 — sửa ở S24.

## S24 Chữ thường k v w x y theo chữ hoa S21 (designer 07/11: "sửa luôn x thường theo X Bold mới")

Từ S21 (cân nét chéo chữ hoa Bold), `lower/derive.py` dừng ở x nên chữ thường dựng từ chữ hoa (k v w x y ý ỳ ỷ ỹ ỵ) vẫn là bản trước S21. Hai lỗi trong bộ dựng:

| Lỗi | Nguyên nhân | Sửa (`lower/derive.py`) |
|---|---|---|
| x Bold: lòng bít, chương trình dừng | S10b làm dày nét mảnh theo bước → khoảng trắng lòng không đơn điệu quanh sx 0.565; secant nhảy về 0.46 | `_solve` / `_widen`: secant có chặn khoảng; lệch → chia đôi trong khoảng kẹp; bỏ outline hỏng |
| x Medium: outline văng xuống −400 | sau S21, mép `\` của X Medium (nội suy) chia thành mảnh gần thẳng hàng lệch ~1 u → `thicken` lấy giao mép mới với mảnh gần song song | `thicken`: không lấy giao khi hai đoạn lệch hướng < 8° (mảnh cùng mép → tịnh tiến) |

- Kết quả (Medium / SemiBold / Bold): nét `\` = thân, `/` theo tỉ lệ mảnh của V hoa — như trước (±0.3 u); lòng v y lớn thêm 1–4 u, x SemiBold −3 u; bề ngang giữ nguyên. Hình đầu nét / loe theo chữ hoa S21, điểm dời tối đa 11 u. x Regular lệch 1 u (ghép cặp nội suy S20).
- So từng glyph với bản trước: chỉ k v w x y ý ỳ ỷ ỹ ỵ đổi. Lệch cấu trúc 0, qa_font 0 lệch, qa_weight 0, kerning va chạm 0.
- Ảnh: `docs/img/s24-chu-thuong-kvwxy.png`.

## S25 Các cờ QA còn lại (designer 07/11: "OK duyệt, sửa luôn các cờ còn lại")

| Cờ | Kết luận | Xử lý |
|---|---|---|
| qa_stroke "không tăng" (! ¡ Æ ‹ › a â ã ả ấ ầ ậ ắ ằ, dấu tổ hợp) | **báo nhầm**: đo lát cắt / vuông góc đều tăng (thân a = n: 102 / 109 / 117 / 125; ! 90 → 122; ‹ › 59 → 97 & 30 → 49) — phân vị 97 trên trục giữa bỏ gần hết thân ngắn khi loại vùng khớp | qa_stroke: kiểm chéo weight dùng E (phân vị 99 bản đồ khoảng cách); cờ độ dày chỉ tính khi CẢ T và E cùng lệch |
| $ & ¥ +12 %, € @ −12 %, ≠ −11 % (nhóm) | **báo nhầm**: $ = S, ¥ = Y, € = C (thân 106 → 146), ≠ = thanh của = | ký hiệu so với chữ gốc (`SYMBASE`), æ œ so với o |
| @ nhẹ hơn o 13 %, đáy vòng mảnh | thật: ngòi bút @ 0.8 N / 0.85 m | ngòi 0.88 N / 0.9 m |
| * đầu cánh, ¶ thanh trên mảnh | thật (dưới nét mảnh chung) | * đầu trong 0.20 → 0.24 V; ¶ thanh 0.55 → 0.75 H |
| A Bold chân phải bậc 3.5 u | thật: S21 dời mép chéo +4.6 u, đầu loe không theo | `fix_struct_bold.py`: đoạn loe dịch theo mép (x += 4.6·y/80.7) |
| nút gãy nhỏ 3–10° (chân loe A, g, &, V, Y, ~ …); nội suy M / SB gãy > 2° ($ S Š s j ȷ ~) | thật | `compat_masters.smooth_pair` (S25): nút gãy < 12° ở cả hai master → xoay tay nắm về một tiếp tuyến (cạnh thẳng giữ hướng; hai cong → trung bình theo độ dài tay; cạnh "thẳng" có thể uốn đầu nếu dời ít hơn); tỉ lệ tay nắm hai master đồng bộ khi bản nội suy gãy (chỉnh MỘT tay, dời ít nhất). Dời hình học > 3.5 u → giữ bản vẽ. Thẳng hàng ở cả hai master → gộp |
| @ gãy 22° | **cố ý**: lòng elip của a bên trong bị mép thân cắt dọc (designer 07/11 "bụng @ nên cắt ngang như này") | không làm liền (`KINK_CH['@'] = 0`) |
| Å å ̊ "contour rỗng" | báo nhầm: lỗ vòng là tròn 2 đoạn cong, diện tích tính từ điểm neo = 0 | qa_outline lấy mẫu đường cong |
| gai 150–166° (mỏ E C G T Z, đầu S 3 5, nách B N &) | cố ý | qa_outline: gai > 170°; thêm phần quét OUTLINE XUẤT FONT |

- Kết quả: qa_stroke 0 cờ (chéo weight 0), qa_outline 0 (bản dựng + outline xuất font), nút trơn gãy M / SB 0, lệch cấu trúc 0, qa_font 0, qa_weight 0, kerning va chạm 0.
- Dời hình học do làm liền: phần lớn ≤ 1.5 u; lớn nhất ~3.4 u (S, Y, g, ~).

## S26 Italic: bù quang học trước khi nghiêng (designer 07/11 duyệt đề xuất)

Italic = Roman nghiêng 10° (trượt ngang) giữ lượng mực nhưng đổi độ dày VUÔNG GÓC theo hướng nét: hướng u dày × 1/|S·u|
(thân đứng × 0.985, "\" 45° × 1.09, "/" × 0.92). Đo trước S26: o O s S x X nét chính +7…+9 %, nét mảnh vòng −8 %, n H −3 % → chữ
tròn / chéo đậm hơn chữ thân đứng ~11 %, màu chữ lốm đốm.

- `tools/construct/ital_comp.py` (gọi trong `export_font.master` khi nghiêng): mỗi cạnh đa giác điều khiển dời song song
  (Tiller–Hanson, `symbols.hdilate(dist=…)`) k = t·(|S·u| − 1)/2; t = độ dày tại chỗ (bắn tia vào trong tới mép đối diện, chặn
  ≤ 1.15 × thân H cùng weight). Không đổi số điểm → variable tương thích; Roman không đổi.
- Sau S26 (Italic so với Roman, 4 weight): nét chính n H o O v e A V x X s S a trong ±3 %; trung vị / phân vị 10–20 độ dày ±3 %.
- Ảnh: `docs/img/s26-italic-bu-quang-hoc.png`.

## S27 X x R: nách chéo + đoạn loe cong đều (designer 07/11 "vẫn lỗi glyph ở bụng chỗ nối chéo x", "đường cong phải smooth")

- Nách X Bold: S21 dời mép chéo → nách thành mặt phẳng 5.2 / 4.8 u; S20 ép x (cả Regular) theo → bậc ở nách. `fix_struct_bold.py`:
  nách = giao hai mép chéo. Quét mọi glyph: không còn mặt nách ngắn (trừ mặt cắt cố ý: cờ 1, đỉnh w, nách tối thiểu ®).
- Đoạn loe X x R nhập mép chéo gãy 15–25° (K A V liền). `compat_masters`: KINK_CH X x R = 30°; rồi S27 `_fair_flare`: trượt điểm
  nhập dọc mép chéo (±40 u, mép giữ hướng) + chọn hai tay nắm cho độ cong ĐỀU (lược độ cong như module loe V) — chỉ đoạn loe
  (đầu kia trên đường chân / x-height / cap, dây cung < 110 u); bụng, đuôi R giữ nguyên.
- QA: nút cong ↔ thẳng gãy (mới thêm vào kiểm): X x R 0; lệch cấu trúc 0, nội suy gãy 0, qa_outline 0, qa_stroke 0.
- Ảnh: `docs/img/s27-loe-X-x-R.png`.

### S27b Quét lại mọi đoạn loe (designer 10/11: "kiểm tra lại các chữ có loe khác xem có gãy không")

Quét outline xuất font, 4 weight: đoạn cong nhập một mép thẳng, đầu kia trên đường chân / x-height / cap, dây cung < 110 u.
Độ đều = độ lệch chuẩn / trung bình của độ cong (0 = cung tròn đều).

| Loại | Trước | Sau |
|---|---|---|
| Gãy ở chỗ nhập mép | 0 (sau S27) | 0 |
| Module loe chéo V (chuẩn) | 0.04–0.18 | — |
| K chân dưới | 0.35–0.53 (độ cong dồn về chân, như X x trước S27) | ≤ 0.23 |
| Y 7 v w y | 0.20–0.47 | ≤ 0.2 |
| Loe chân thân đứng (H I E L K R n m h …) — module chung | 0.36–0.39 | giữ nguyên |
| A V chân ngoài, k tay trên, 2 góc chân | đều; một điểm uốn nhỏ ở mũi vuốt nhọn (hình loe ngoài) | giữ |

- `compat_masters.FLARE_FAIR` = X x R K Y 7 v w y; `_fair_flare` chỉ xử lý mép CHÉO — S27 trước lỡ làm đều cả loe chân thân R
  (thân thẳng) → nay trả về module loe thân chung (0.36–0.39 như H, K).
- QA: lệch cấu trúc 0, nội suy gãy 0, qa_outline 0, qa_stroke 0, qa_font 0, kerning va chạm 0.
- Ảnh: `docs/img/s27b-loe-cong-deu.png` (lược độ cong K w 7 Y trước / sau).

## S28 Italic: đoạn loe (designer 10/11: "kiểm tra lại italic các chữ có loe luôn")

Quét outline font Italic (4 weight) so với chính đoạn loe đó ở Roman. Trước S28: 178 cờ.

| Lỗi | Nguyên nhân | Sửa |
|---|---|---|
| Đổi chiều cong (gợn) ở loe chân thân H I E L n m … | S26 dời từng cạnh điều khiển theo độ dày đo ở chỗ khác nhau → điểm chân và điểm nhập dời lệch nhau (phép nghiêng KHÔNG tạo điểm uốn — affine) | `ital_comp`: đoạn loe KHÔNG dời từng cạnh — tịnh tiến NGANG nguyên đoạn loe Roman cho điểm nhập nằm trên mép đã bù (hình module giữ, liền tiếp tuyến, chân trên đường chân) |
| Loe chéo K Italic dồn độ cong (0.35 → 1.5) | như trên (điểm chân dời 6.4 u, điểm nhập 3 u) | như trên |
| Gãy 2–18° ở chỗ nhập mép | làm tròn toạ độ NGUYÊN sau khi nghiêng: tay nắm loe ngắn (3–22 u) lệch hướng | `export_font._snap_smooth`: ở nút liền, tay nắm (và điểm nối ±1 u trên mép) đặt vào điểm nguyên thẳng hàng nhất; S27 tay nắm ở chỗ nối liền ≥ 16 u (đầu góc chân tự do); `ital_comp` cứu tay quá ngắn (< 8 u / < ½ Roman) |
| (S26) nét chính o O lại +5 % | kéo dài mọi tay nắm về độ dài Roman làm mất phần bù | chỉ cứu tay quá ngắn |

- Áp `_snap_smooth` cho cả Roman (cùng làm tròn → Roman / Italic cùng số điểm → variable dựng được).
- Sau S28: Italic so với Roman nghiêng thuần — độ đều loe chéo chênh trung vị 0.05, loe thân 0.08; không đổi chiều cong; gãy còn
  x Medium / SemiBold 2.1°, x ¥ Medium Italic 2.0–2.4° (sai số làm tròn khi nội suy hai master nguyên — không thấy bằng mắt).
- Độ dày Italic (S26) giữ: E (bản đồ khoảng cách) n H o O v V x X s S K e trong ±3 % so với Roman, 4 weight.
- QA Roman: lệch cấu trúc 0, nội suy gãy 0, qa_outline 0, qa_stroke 0, qa_font 0, kerning va chạm 0; loe chéo K ≤ 0.24.
- Ảnh: `docs/img/s28-italic-loe.png` (lược độ cong H K x n Italic trước / sau).

## S29 N đóng khấc + nút gãy do làm tròn / nội suy (designer 10/11: "Hở mối nối N", "sửa luôn mấy chỗ gãy x ¥ còn lại")

**N:** bản vẽ N Regular (và Bold theo S20) có khấc nêm ở đỉnh dưới phải và đỉnh trên trái — mép thân đi 14 u rồi mặt cắt dốc
lệch 5.6 u → khe 5.6 × 14 u đọc thành VẾT HỞ. `ref/fix_N_notch.py`: mép đáy / đỉnh chạy thẳng tới chân / đỉnh nét chéo (một điểm),
Regular (designer_A) + Bold (designer_B); Medium / SemiBold nội suy lại. Ảnh: `docs/img/s29-N-dong-khac.png`.

**Nút gãy trong font** (quét mọi nút cong ↔ cong / cong ↔ thẳng 2–12°, 312 ký tự × 8 style): 674 → 5.

| Nguồn | Sửa |
|---|---|
| Bản tĩnh Medium / SemiBold = instance NỘI SUY từ hai master đã làm tròn rồi làm tròn lần nữa → tay nắm ngắn lệch hướng (113 / 131 nút, j Medium 11°) | `export_font`: instance UFO (tên, kerning, feature của fontmake) nhưng OUTLINE thay bằng bản dựng thẳng từ toạ độ số thực cùng weight qua `_snap_smooth` (bản variable giữ nguyên; lệch ≤ 1 u do làm tròn) |
| Hai master nguyên: tỉ lệ tay nắm / cạnh lệch sau làm tròn → nội suy gãy (x, ¥ 2–2.4°) | `pair_fix`: ở mỗi nút liền, dò CẶP điểm nguyên cho tay nắm ở hai master (±2 u), min góc gãy lớn nhất tại t = 0, ⅓, ⅔, 1 |
| Làm tròn tay nắm cong ↔ cong rất ngắn (3 u → lệch tới 10°) | `_snap_smooth`: bộ ba (tay vào, neo, tay ra) nguyên thẳng hàng nhất (neo ±1, tay dài ±1); tay < 5 u kéo dài 7 u |
| Bước chống "đổi chiều cong" nhích tay nắm ở nút liền / đoạn gần thẳng (A Medium 5°) | không đụng tay ở nút liền; bỏ qua đoạn gần thẳng |
| S26 bù Italic: neo dời tới giao điểm mới, tay ngắn quay hướng → góc nhọn z 153° → 27° | `ital_comp`: hướng mọi tay nắm = Roman (dời song song không đổi hướng cạnh điều khiển) — 0 nút đổi góc > 1° |
| S25 đồng bộ tỉ lệ phóng tay 0.1 → 16 u trên đoạn 10 u → vòng xoắn (A Bold chân trong) | `_sync_ratio`: tay ≤ 0.9 dây cung, đoạn không tự quay ngược |
| ® loe chân R bên trong gãy 16° (hdilate) | `KINK_CH['®'] = 20` |

- Còn lại (cố ý): 5 Medium Italic 11.6° = góc khấc vát S20 (18° ở Roman, nghiêng làm hẹp lại); @ Italic = đoạn tí hon 7 u trong góc
  cắt lòng cố ý; 7 Medium Italic 2.2°.
- QA: lệch cấu trúc 0, nội suy gãy 0, qa_outline 0, qa_stroke 0, qa_font 0, kerning va chạm 0; Italic độ dày ±3 %; loe Italic 0 gợn
  (trừ y SemiBold Italic: điểm uốn sát 0 ở mũi đuôi).

## S30 Hết các chỗ gãy còn lại (designer 10/11: "sửa luôn 7 Medium Italic còn gãy", "xử hết 1 lần nhé")

| Chỗ | Nguyên nhân | Sửa |
|---|---|---|
| 7 Medium Italic 2.2°, Medium 1.6° | contour đảo chiều khi xuất khép bằng cạnh NGẦM (closePath) → nút đoạn cuối ↔ cạnh khép không qua bước đặt điểm nguyên | `export_font.draw`: cạnh khép tường minh trước `_snap_smooth` (mọi contour) |
| @ Italic / Medium Italic 8–10° | đoạn cong tí hon (7 u) tay zigzag ở góc cắt lòng; sau bù co ≤ 3 u → làm tròn xoắn | `compat_masters._fix_tiny` (S30): đoạn < 12 u tay ngược / dài quá dây cung → tay Hermite theo tiếp tuyến hai bên; @ vẫn đồng bộ độ dài tay ở nút LIỀN (không đổi hướng — góc cắt giữ); khi xuất đoạn ≤ 3 u: tay về hai đầu |
| đuôi y (mọi weight) đổi chiều cong ở mũi | đoạn loe đuôi có chân trên mặt cắt NGANG y −201 — S27 / S28 chỉ nhận đường chân / x-height / cap | đoạn loe nhận theo cạnh ngang ở đầu chân (S27 compat + S28 ital_comp) |
| ý ỳ ỷ ỹ ỵ ÿ Ý Ỳ Ỷ Ỹ Ỵ Ÿ | dùng lại cặp outline chữ gốc từ TRƯỚC S27 → loe chưa làm đều từ S27b | S27 xét theo chữ gốc (NFD); thêm ¥ |

- Quét nút gãy 2–12° trên file font, 312 ký tự × 8 style: còn 1 — 5 Medium Italic 11.6° = góc khấc vát cố ý (S20; 18° ở Roman,
  nghiêng làm hẹp lại). Loe chéo Roman mọi ký tự (kể cả có dấu) độ đều ≤ 0.25; loe Italic: 0 gãy, 0 đổi chiều cong.
- QA: lệch cấu trúc 0, nội suy gãy 0, qa_outline 0, qa_stroke 0, qa_font 0, kerning va chạm 0; Italic độ dày ±3 %.
- Ảnh: `docs/img/s30-gay-con-lai.png` (lược độ cong 7 Medium Italic, y SemiBold Italic, ý Regular, @ Medium Italic — trước / sau).

## S31 Kiểm tra các chữ có khấc khác (designer 10/11: "kiểm tra lại các chữ có khấc khác xem có hở không")

- Quét 1: khe trắng hẹp < 8 u (đóng hình thái bằng đĩa r 4 u) ở mọi ký tự × 4 weight → 42 ký tự có vùng bị lấp, phóng to từng chỗ:
  tất cả là NÁCH NHỌN tự nhiên (vai n m h – thân, nách b d p q, đỉnh trong V v W w, nách K k M, bụng B gặp nhau tại một điểm,
  khấc vát 5 liền mực, mũi giữa { }) — không có khe cắt vào mực.
- Quét 2: dấu hiệu khấc nêm như N cũ (hai cạnh ngắn < 30 u liền nhau, quay > 120°, miệng < 10 u, lõm vào mực): 0 ký tự.
- Phóng to mọi đỉnh nhọn A V v W w M N Y y K k X x Z z 7 4 Æ æ & (Regular, Bold): liền một khối.
- `qa_outline.py`: thêm kiểm "khe" (khe nêm hẹp) vào phần quét outline xuất font — bắt đúng hai khấc của N trước S29.

## S32 Italic: kiểm tra các chữ có khấc (designer 10/11: "kiểm tra lại italic các chữ có khấc luôn")

- Quét file font Italic (4 weight): khe nêm hẹp 0; khe trắng < 8 u trùng nhóm nách nhọn tự nhiên của Roman.
- Tìm thấy: **W Italic loe ngoài trên phải** — sau bù S26 tay nắm dài 110 u (Roman 12 u) → vòng xoắn, Medium Italic thêm hai đoạn tí hon
  quay ngược (miệng 0 u) → vết trắng mảnh cắt vào loe. Nguyên nhân: giao cạnh dời gần song song vọt xa, bước "giữ hướng tay như
  Roman" giữ nguyên độ dài vọt. `ital_comp`: độ dài tay sau bù ≤ 1.5 × Roman + 2 u.
- @ Medium: tay nắm kéo dài khi làm tròn vượt dây cung đoạn 5.8 u → `_snap_smooth` kéo dài tay ≤ 0.9 dây cung đoạn.
- Sau S32 (8 style): khe nêm 0, tay nắm dài quá dây cung 0, nút gãy 2–12° 0, loe Italic 0 gãy / 0 đổi chiều cong; qa_font 0.
- Ảnh: `docs/img/s32-italic-khac.png` (W loe trên phải Italic 4 weight trước / sau; đỉnh nhọn N A V v w K M Italic / Bold Italic).

## S33 QA đường cong số 2 và S (designer 11/11: "QA/QA lại đường curve của các glyph số 2, và chữ S")

Đo trên file font, 8 style: gãy ở nút, bước nhảy độ cong (G2) tại nút liền, điểm uốn từng đoạn, lược độ cong toàn glyph.

- **Roman:** đường cong = bản vẽ designer (2: designer_B sau S23; S: vector Figma) — pipeline không đổi profile độ cong. Các bước
  nhảy G2 có sẵn trong bản vẽ: 2 bụng phải −8.2 → −5.9 ×10⁻³ (bụng "chụm" nhẹ ở cực phải), 2 nách trong đầu nét; S Bold đáy lòng
  dưới 15.5 → 5.3, lòng trên 17.5 / 10.4 → 6.9 (đã có trong Figma). Không sửa — đề xuất G2 cục bộ (chỉ độ dài tay nắm ở nút, giữ neo
  + hướng) ở `docs/img/s33-de-xuat-g2-2-S.png`: lược đều hơn nhưng đổi hình thấy được ở mép ngoài S → chờ designer.
- **Italic (lỗi do S26 bù quang học):** bụng phải 2 Italic nhảy 4.5 → 22; đuôi S Italic có điểm uốn (tay suy biến Roman thành tay
  thật sau bù). `ital_comp`: tay suy biến ở Roman giữ suy biến; độ dài tay = Roman × tỉ lệ dây cung, kẹp ±8 % quanh độ dài bước dời
  (giữ phần bù o O e). Sau: profile Italic bám Roman, đuôi S hết uốn, bụng phải 2 hết nhảy; độ dày Italic ±3 %; nút gãy 2–12° chỉ còn
  góc khấc vát cố ý 5 Medium Italic; loe Italic 0 gãy / 0 đổi chiều cong. Ảnh: `docs/img/s33-italic-2-S.png`.

## S34 S liền độ cong có ràng buộc (designer 11/11: "tôi cảm giác S glyph các đường cong vẫn hơi gãy")

Góc ở mọi nút S đã liền; cái "gãy" mắt thấy là BƯỚC NHẢY ĐỘ CONG tại nút (bụng ngoài trái −1.9 → −7.8 ×10⁻³ Regular, đáy lòng dưới
Bold 15.5 → 5.0, lòng trên 17.5 / 10.4 → 6.9, đỉnh −4.6 → −1.4). S17 (ép G2 toàn bộ) làm bụng mất tròn → lần này có ràng buộc:

- `ref/fix_S_g2.py` (từ bản lưu `designer_{A,B}_preS34.json`): giữ HƯỚNG tiếp tuyến mọi nút; chỉ đổi độ dài tay nắm (× 0.75 … 1.35) và
  cho nút trượt DỌC tiếp tuyến của nó (± 12 u); mỗi đoạn lệch ≤ 3 u so với vector Figma; không thêm điểm uốn; nút có độ cong đổi dấu
  (điểm uốn sống) bỏ qua; dò từng nút nhiều lượt giảm Σ (κ trái − κ phải)² / κ².
- Kết quả (tỉ lệ độ cong hai bên nút, 1.0 = liền): đỉnh 3.2 → 1.1, đáy lòng dưới Bold 3.1 → 1.4 / Regular 2.0 → 1.2, lòng trên
  1.5–1.9 → 1.0–1.6, bụng ngoài trái 4.2 → 2.6 (Regular), 3.5 → 2.0 (Bold), bụng phải dưới 2.7 → 2.3 / 2.3 → 1.6 — phần còn lại là dáng
  bụng của bản vẽ (nửa dưới phía sống phẳng hơn), gỡ hết phải sửa dáng > 3 u.
- Lệch hình (Hausdorff) S 2.65–2.8 u; s thường (dựng từ S) 3.0–3.4 u; $ Š theo S.
- QA: lệch cấu trúc 0, nội suy gãy 0, qa_outline 0, qa_stroke 0, qa_font 0, kerning va chạm 0; Italic độ dày ±3 %.
- Ảnh: `docs/img/s34-S-lien-do-cong.png` (lược độ cong S Regular / Bold, s Regular, S Italic — trước / sau).

## S35 S bụng dưới phải tròn hơn (designer 11/11: "đường cong bụng chỗ này của S regular chưa tròn trịa và mềm mại")

- Đo hệ số tay nắm (so với hộp tiếp tuyến; cung tròn: 0.552 cho đoạn quay 90°, 0.62 cho 60°): mép ngoài bụng dưới, hai đoạn hai bên
  cực phải có tay phía cực phải 0.81 (đoạn 60°) và 0.62 (90°) → mép đứng thẳng một đoạn rồi bẻ gắt ("vuông"). Bold 0.79.
- `ref/fix_S_g2.py` (`round_bowl`, trước bước liền độ cong S34): tay phía cực phải MÉP NGOÀI bụng dưới về hệ số cung tròn × 1.05;
  cực phải (bề ngang, độ dày tại đó) giữ. Lòng KHÔNG đổi (thử rút cả lòng → lòng nhọn ở cực phải).
- Sau: Regular 0.81 / 0.62 → 0.65 / 0.58; nút cực phải ngoài: tỉ lệ độ cong hai bên 2.3 → 1.9 (Bold 1.6 → 1.2). s $ § Š š theo S.
- qa_stroke: kiểm chéo weight cho ký hiệu dựng thẳng từ chữ (¢ € $ ¥) so với chữ gốc (`XBASE`) — ¢ bị báo vì trung vị nhóm dịch
  khi $ đổi theo S.
- QA: lệch cấu trúc 0, nội suy gãy 0, qa_outline 0, qa_stroke 0, qa_font 0, kerning va chạm 0; Italic độ dày ±3 %.
- Ảnh: `docs/img/s35-S-bung-duoi-tron.png` (bụng dưới phải Regular / Bold — trước / sau).

## S37 Số 2 theo mẫu gốc Figma + cân độ dày bộ số (designer 11/11: "tham khảo đường cong số 2 từ mẫu gốc", "cân lại độ dày số cho đồng bộ")

- Bỏ đề xuất S36 (ép vai phải bụng ngoài số 2 về cung tròn, chưa phát hành): làm mất vai phải "vuông" của bản vẽ.
- Mẫu gốc Figma `2168:109`. Regular trùng bản vẽ cũ (`designer_Q`) → giữ đường cong gốc và phần đậm ngang +10 của S23. Bold là bản vẽ
  MỚI: vai phải phẳng hơn, thanh chân 131, đầu nét trái hạ xuống 480, bụng 142. Bản này đã đậm hơn bản làm đậm S23 (139) nên dùng
  nguyên hình, chỉ đổi đơn vị (× 711.3 / 251, lật trục y) và cho tay nắm góc chân trái suy biến (`ref/fix_fig_weight.py`, `FIG2_BOLD`).
- Cân độ dày bộ số: đo nét dày nhất của từng nét chính (đường kính hình tròn nội tiếp lớn nhất, bỏ vùng khớp), Regular / Bold:
  0 111/139 · 1 103/139 · 2 106/142 · 3 107/144 · 4 106/145 · 5 107/143 · 7 108/137 · 8 107/139. Riêng bụng 6 và 9 nhẹ hơn
  (102/136, −4 %) → làm đậm ngang +4 (Regular) / +5 (Bold), cùng cách S23 → 105/140. Thứ tự này giữ nguyên: 8 trên nhẹ hơn 8 dưới
  (luật), 3 trên nhẹ hơn 3 dưới.
- ? ¿ và dấu hỏi vẫn dựng từ số 2 gốc (`designer_Q`), không đổi.
- Ảnh: `docs/img/s37-so-2-figma.png` (Figma gốc / v0.910 / S37, Regular và Bold).
