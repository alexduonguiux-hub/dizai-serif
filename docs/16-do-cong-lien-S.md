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
