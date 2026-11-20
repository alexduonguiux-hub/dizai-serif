# An Nam Golden

Họ chữ phát triển từ AnNam Serif (designer 19–20/11). Dựng bằng luật trên outline Regular + Bold của AnNam Serif
(`tools/construct/golden/golden.py`), Medium / SemiBold nội suy; chạy `bash tools/construct/golden/run.sh` sau pipeline AnNam Serif.
Font: `fonts/golden/` (OTF, TTF, variable, woff2), tên họ "AnNam Golden", PostScript `AnNamGolden-*`.

| Luật | Nội dung |
|---|---|
| G1 | x-height 495 → 535 (chữ thường, chữ ghép, dấu tổ hợp); bề ngang giữ; đầu thân b d h k l þ giữ 699 (chỉ đoạn thân thẳng co), đ thanh giữ dày, f móc giữ hình (cao thêm 20), ß phần trên co; dấu, chấm dời lên 40.7 |
| G5 | đầu t (và t trong ft tf tt) vát: mép phải thân thẳng lên đỉnh cao 1.03 × bề ngang thân trên mặt thanh, cạnh vát xuống mặt thanh cách mép trái thân 0.625 × phần thanh thò trái (hình phác designer) |
| G4 | v x y (ý ỳ ỷ ỹ ỵ ÿ) rộng × 1.08 quanh tâm, nét thu lại × 1/1.08 (giữ bề dày), dấu giữ hình |
| G3 | loe (chân, đỉnh thân, chéo): rộng × 1.3 theo đường chân, cao × 0.85 — vuốt nhọn; điểm nối thân trượt trên đường thân (liền tiếp tuyến) |
| G2 | nét mảnh (thanh ngang, chéo mảnh, vòng mảnh, khớp) chữ hoa + thường còn ~80 %: mép dời theo pháp tuyến 0.1 × bề dày; đoạn thẳng đo ở giữa đoạn (thanh không vát); cung dài chia đôi để đặt luật tại chỗ mảnh nhất; thân dày, dấu giữ |

Số đo (Regular, trục giữa): thanh H 40 → 32, N đứng 48 → 36, O mảnh 34 → 27, S mảnh 38 → 29; thân giữ 104.
Ảnh: `docs/img/golden-v1.png`.

## S50 — luật nét mảnh làm lại (20/11)

- Đoạn thẳng: dời song song cả đoạn; góc cung–thẳng chỉ theo phía đoạn thẳng; đoạn ngắn nối tiếp nét thẳng (≤ 20°) dời cùng nét (W giữ góc nối gốc).
- G7 s S: lòng trên / dưới kéo dãn đứng affine từ điểm chân chuỗi (không đẩy từng điểm neo → hết gãy góc).
- G10 (mới) mọi nét mảnh cong còn lại — b d p q a g c C G U J, vòm n m h u, B D P R: chuỗi cung lõm của mép lòng kéo dãn đứng, dốc tuyến tính từ giữa chuỗi (affine, tay nắm cùng phép); góc trên thân đứng trượt theo thân (cả tay nắm kề), góc khác đứng yên. δ = min((dày − chuẩn)/dốc) đo theo pháp tuyến → không điểm nào mỏng hơn chuẩn. Lòng kín: hai chiều (làm dày được); lòng hở: chỉ kéo mảnh (đầu nét / vai mảnh là chủ ý).
- Bỏ đoạn < 2 u ở cả hai master (nách K).
- Đo: Golden 32 / 44 ± 2 (trừ B D R ~40 / 52–55 — mép thẳng trên đường kẻ); AnNam Serif 42 / 62 (n m h u C G 37–38 Regular theo bản vẽ, lòng hở không làm dày).

![bảng chữ](img/s50-all.png)

## S51 — thanh ngang không dốc (designer 20/11 "nét trong của Z bị dốc", "kiểm tra z luôn")

Nguyên nhân (cả AnNam Serif lẫn Golden): (1) góc cung–thẳng (đầu thanh nối loe) giải theo tiếp tuyến cung → gần như đứng yên trong khi đầu nối thân dời; (2) khi làm DÀY (hệ số > 1) điều kiện chặn độ dời dùng max(da, db) = 0 → góc nối thân bị bỏ; (3) góc thẳng–thẳng trên đường kẻ (đỉnh chéo M W Y K) bị bỏ qua thay vì trượt dọc đường kẻ; (4) mẩu nối 2.5 u ở nách K không có tiếp tuyến.
Sửa: góc cung–thẳng dời theo pháp tuyến đoạn thẳng; chặn theo |da|, |db|; góc thẳng–thẳng trên đường kẻ trượt dọc đường kẻ; bỏ mẩu < 3 u trước mọi luật.
QA mới `tools/construct/qa_lines.py` (chạy cuối pipeline, so với v0.918): đoạn ngang / đứng giữ hướng (≤ 0.3°), mép trên đường kẻ còn trên đường kẻ, AnNam Serif mọi đoạn giữ hướng (≤ 0.5° + sai số làm tròn). Kết quả: Golden 0 · AnNam Serif 1 (Ë Bold — chủ ý: Ë = E + dấu thay cho Ë vẽ riêng ở v0.918).

## S52 — thanh T và đồng bộ mọi thanh (designer 20/11 "thanh ngang của T sao lại dày hơn của các chữ khác")

- G11 thanh T: thanh là contour riêng chồng thân, mép dưới là hai cung loe chạy vào thân → điểm nối cung–thân (tiếp tuyến ngang) dời đứng tới đúng chuẩn; đầu nhọn loe đứng yên.
- G8 tuyệt đối: mỗi đoạn thẳng nét mảnh (0.5–1.6 × chuẩn) tự về ĐÚNG chuẩn, đo riêng giữa đoạn (bỏ hệ số chung cả chữ — làm thanh P mảnh quá). Áp mọi chữ gốc, gồm thanh e f t.
- QA mới `tools/construct/qa_bars.py`: độ dày thanh ngang mọi chữ so chuẩn (lệch > 3 u = lỗi). Kết quả: AnNam Serif 42 / 62 ± 1, Golden 32 / 44 ± 1, 0 lỗi.

![bảng chữ](img/s52-all.png)
