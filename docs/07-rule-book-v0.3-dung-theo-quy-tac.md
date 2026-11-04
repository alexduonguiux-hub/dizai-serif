# Dizai Serif v0.3 — Dựng lại theo quy tắc (04/11/2026)

Designer yêu cầu (04/11):
- "loe chân … vẽ lại theo guide và principle chung cho đồng bộ và có 1 quy tắc cụ thể";
- "Dựng lại bằng 1 vòng thôi";
- "cách tạo hình của các chữ bạn cũng nên tự dựng lại để có guide rõ ràng hơn là dùng vector của tôi".

Vì vậy từ v0.3, hình chữ được **sinh bằng code từ luật**, không lấy lại vector cũ:
- `tools/construct/dizai.py`: bản Python, dùng skia-pathops cho phép hợp. Dùng để QA và để xuất font sau này.
- `tools/construct/dizai_figma.js`: cùng công thức, chạy trong Figma. Mỗi glyph là một phép
  Boolean của các phần có tên (Thân, Thanh, Chéo, Loe…, Lòng), nên mở ra chỉnh từng phần được.
  Guide sinh từ chính phép dựng.
- Trang Figma: **"v0.3 — Dựng theo quy tắc (Claude)"**. Các trang v0.2 giữ nguyên để đối chiếu.

Đơn vị font: UPM 1000, cap 700, baseline 0 (1 px Figma = 2.834 u).

## Bảng nét (giữ từ v0.2, đã duyệt)
| | Thân V | Vòng Vr | Chéo dày D | Nét mảnh t | Nét ngang Hb |
|---|---|---|---|---|---|
| Regular | 102 | 106 | 100 | 44 | 40 |
| Bold | 139 | 146 | 146 | 74 | 68 |

## Luật hình học (giống nhau ở mọi weight, đo theo đơn vị Regular)
- **L1 Loe.** Mỗi phía tự do của một đầu nét (thân đứng, nét chéo) có **đúng một cung tròn r = 112**, tiếp tuyến với mép nét và kết thúc tại điểm mũi trên đường kẻ, cách mép nét f = 23 (đo ngang).
  - Không có đoạn vát, không có bo góc.
  - Với thân đứng, tiếp điểm cao 68.
  - Với nét chéo, dùng cùng công thức: tâm vòng nằm trên pháp tuyến của mép nét.
- **L2 Mỏ tay ngang** (E, F, L, T, Z…). Cùng một vòng r = 112, tiếp tuyến với mép trong của tay, mũi nằm trên đường cắt đầu tay, sâu b = 54 (tiếp điểm cách đầu tay 96).
- **J1 Đỉnh nhọn** (A, V, sau này M, W):
  - mép ngoài hai nét gặp nhau ở một đoạn cắt phẳng a = 20 trên đường overshoot (cap + 12 / baseline − 12);
  - mỗi chân được cắt theo mép ngoài của chân kia, nên đỉnh không phình ra;
  - không loe ở đỉnh.
- **J2 Nét chéo nối thân mảnh** (N, sau này M):
  - thân mảnh dừng phẳng đúng trên đường kẻ, không overshoot (chỉ đỉnh nhọn mới được vượt đường kẻ);
  - mép trên của nét chéo đi qua góc trong-trên của thân trái, mép dưới đi qua góc trong-dưới của thân phải;
  - nét chéo bị giới hạn trong khoảng giữa hai mép ngoài của thân.
- **R1 Vòng.**
  - O: vòng tròn ngoài; lòng là elip xoay 30° (dày 103 / 142 ở dưới-trái và trên-phải, mảnh 40 / 70 ở hai góc còn lại).
  - D: bụng ngoài là nửa elip κ 0.5523; lòng là nửa elip κ 0.60 (hơi vuông).
- **Thanh.** H và E ở 0.53 cap; A ở 0.255 cap. Tay giữa của E cắt xiên 26°.
- **Spacing tạm.** 40 u mỗi bên (đường chấm dọc trong ô dựng).

## Control set đã dựng
H I E T L N A V O D × Regular, Bold. Bề ngang mực giữ đúng v0.2.

Kiểm tra:
- O: đo bán kính lòng theo 4 hướng chéo cho dày 103 / 142 ở dưới-trái và trên-phải → trục đúng như O v0.2.
- N: nét chéo xuất phát đúng góc trong của thân (điểm xanh trên bản dựng).

## Chờ duyệt trước khi dựng toàn bộ
1. **Hình loe chung** (L1: r 112, f 23): có đúng tinh thần loe của bộ chữ không?
2. **Đỉnh A và V:** dùng đoạn cắt phẳng a = 20 ở overshoot, hay muốn đỉnh nhọn hẳn (a = 0)?
3. **N theo J2:** nét chéo đi qua góc thân, mặt trên thân phẳng.
4. Sau khi duyệt: viết luật cho B, P, R (bụng), C, G, S, Q, J, K, M, W, X, Y, Z và bộ số, rồi dựng tiếp.


## Cập nhật 04/11 — dựng toàn bộ chữ hoa A–Z và số 0–9 (Regular + Bold)

Designer duyệt control set: "duyệt, dựng tiếp toàn bộ chữ và số".

**Nguồn chính:** `tools/construct/glyphs.js` (hình học), dùng cho cả Figma và Node.
- `render_figma.js`: dựng ô trong Figma. `mkrun.py` ghép và rút gọn mã để chạy trong `use_figma`; đã kiểm bản rút gọn cho kết quả giống hệt ở cả 72 glyph.
- `export.js`: xuất dữ liệu các phần dựng ra `parts.json`.
- `build.py`: phép hợp chính xác bằng skia-pathops và bảng kiểm tra.
- `preview.py`: ảnh lớn kèm các phần dựng.
- Bản Python cũ `dizai.py` chỉ còn giá trị tham khảo cho control set.

### Luật bổ sung
- **T1 Đầu nét hở** (C G S J 2 3 5 6 9): cắt dọc, không loe.
- **B1 Bụng** (B D P R): thân + nửa elip κ 0.5523 có đoạn thẳng (35 % bề rộng); lòng là nửa elip κ 0.60, nối mép trong của thân.
  - B: hai bụng gặp nhau ở 0.56 cap; bụng trên rộng 80 % bụng dưới.
  - P, R: bụng xuống tới 0.47 cap.
  - Chân R: dải chéo dày D, mọc từ 62 % bụng, có loe L1 ở chân.
- **C, G:** vòng tròn của O cắt dọc tại bề ngang chữ. Lòng đứng (ngoại lệ đã chốt): thành trái = Vr, đỉnh/đáy = Hb. G thêm thân phải V, tay ngang ở 0.48 cap với mỏ L2.
- **U, J:** thân V + nửa vòng dưới (U ở 0.33 cap, J ở 0.30 cap). Móc J cắt dọc.
- **K:** tay mảnh t đi từ thân (0.30 cap) lên cap, có loe. Chân dày D đi từ giữa tay xuống baseline, có loe; chân bị cắt theo mép trên của tay.
- **M:** J2 ở hai góc trên (thân trái mảnh, thân phải dày). Đỉnh dưới theo J1 ở cao 175. Nét chéo giới hạn giữa hai thân.
- **W:** hai V (rộng 62 %) chồng nhau. **X:** chéo dày \\ và chéo mảnh / giao nhau, loe cả 4 đầu. **Y:** hai tay gặp thân ở 0.47 cap.
- **Z:** thanh trên có mỏ trái, thanh dưới có mỏ phải (L2); chéo dày D đi qua góc trên-phải và góc dưới-trái.
- **Q1 Đuôi Q:** hình trăng khuyết giữa hai cung tròn đi qua cùng hai điểm (sagitta 100 và 44 / 22), cộng sau khi trừ lòng.
- **S1 Chữ S:** hai đường tâm là hai vòng tròn tiếp xúc tại T (đường nối tâm nghiêng −68°), sau đó nén ngang hệ số k cho vừa bề ngang.
  - Lòng mỗi vòng lệch tâm, sao cho thành tại T đúng Sp/2; nhờ vậy sống liền một nét và dày Sp.
  - Đỉnh và đáy dày Hb. Mỗi vòng chỉ giữ phần thuộc đường S. Hai đầu cắt dọc.
- **Số:** thân và vòng = V; nét ngang dày Hf (90 / 120); vòng của số nghiêng 15°.
  - 0: oval.
  - 1: cờ là một cung tròn L1 nối từ đỉnh thân tới mũi (mũi đặt tại bề ngang chữ, cách cap 120).
  - 2: cung trên + nét chéo tiếp tuyến với cung + thanh đáy có mỏ L2.
  - 3: thanh trên có mỏ + nét chéo tiếp tuyến với bụng dưới; bụng mở ở trái.
  - 5: thanh trên có mỏ + thân mảnh cắm vào vai bụng (140°); 3 và 5 dùng chung bụng.
  - 4: thân phải V, thanh Hf ở 0.30 cap có mỏ; nét chéo mảnh đi qua góc trong của thân (J2).
  - 6, 9: bụng + nét lên là phần của vòng lớn; hai lòng đứng để thành trái liền một mạch; 9 = 6 xoay 180°.
  - 7: thanh trên có mỏ trái + nét chéo dày có loe ở chân.
  - 8: hai vòng chồng nhau, vòng trên hẹp hơn (thành 0.9 V).
- **Nối tiếp tuyến:** nét chéo của 2 và 3 có mép là tiếp tuyến của vòng (tính chính xác), đầu nét cắt vuông góc tại tiếp điểm. Không cắt ngang tuỳ ý.

### Kiểm tra
- 72 glyph đều dựng được. Phép hợp trong Figma (Boolean) và trong Python (skia-pathops) xuất phát từ cùng dữ liệu.
- Từng nhóm đã xem ở cỡ lớn. Các lỗi gặp khi dựng và đã sửa:
  - M: chọn sai nghiệm khi đặt nét chéo;
  - S: sống mảnh, rồi có bậc ở sống;
  - 2: nét chéo nằm sai phía, rồi không liền với cung;
  - 3, 5: mẩu nét thò ra khỏi bụng;
  - 4: đỉnh thân phẳng vượt cap;
  - 6, 9: gờ ở thành trái.

### Còn mở (cần designer xem)
- **S:** đã liền và đúng luật, nhưng dáng còn "cuộn" (bụng trên nhỏ, sống ngắn). Có thể chỉnh góc nối tâm (−68°) hoặc tỉ lệ hai vòng (46/54).
- **Q:** độ dài và độ cong của đuôi.
- **Spacing / kerning:** chưa làm. Preview đang dùng 40 u mỗi bên.
