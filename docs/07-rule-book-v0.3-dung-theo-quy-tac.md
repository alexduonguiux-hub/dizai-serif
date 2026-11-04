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


## v0.3.1 (04/11) — sửa lỗi và dựng lại theo concept của designer

Designer phản hồi: "nhiều số và chữ không giống concept", "lệch mà còn lỗi nữa", rồi gửi demo guide vẽ tay (6 7 8 9: elip trọn vòng + trục chéo).

**Nguyên nhân.** v0.3 áp luật chung trước rồi mới dựng, nên những hình đặc trưng của bản vẽ (J, K, Q, S, W, số 1 2 3 5 6 7 9…) bị thay bằng hình "suy ra từ luật". Một số phép cắt còn sinh lỗi hình học.

**Cách sửa.** Số đo lấy ngược từ chính đường cong v0.2 của designer (`tools/construct/ref/`):
- `v02_paths.json`: vector gốc lấy từ Figma.
- `ellfit.py`: nhận diện cung elip trong mỗi cubic (cubic có hai tay nắm cùng tỉ lệ ρ ⇒ cung conic, w = ρ / (4/3 − ρ)) → tâm, trục, góc của elip designer đã dùng.
- `diff.py`: % diện tích lệch so với v0.2. `scan.py`: so từng đường quét ngang.

Sau đó dựng lại từ các elip, đường thẳng và vòng compa đó (`glyphs.js`). Guide vẽ theo kiểu demo của designer: elip trọn vòng, hai trục, mép chéo kéo dài, mốc ngang cam (`guides.py`; trong Figma là các lớp "elip dựng" / "guide").

### Lỗi đã sửa
- Loe ở nét chéo (A V W X Y K R 7): phần chồng 3u đi theo pháp tuyến nên thò xuống dưới baseline thành gờ. Nay phần chồng đi dọc đường mũi.
- A: hai đầu thanh lộ bậc nhỏ ở mép trong chân. Nay thanh chạy tới đường giữa của chân.
- Z: hai mẩu thò ở đầu thanh. Nay mép chéo đi qua (W, cap − 17) và (0, 17), như v0.2.
- 4: nét chéo chỉ còn một cái nêm rời khỏi thanh. 7: mảnh vụn ở chân (còn sót khối dựng cũ). 5, 6, 9: khấc ở thành trái. 3, 5 Bold: lòng kín, sai đầu hở.

### Luật đo từ v0.2 (Regular, đơn vị font)
- **J:** thân V xuống tận baseline. Góc ngoài cung r 170, góc trong cung r 85. Đuôi là thanh Hb chạy tới x = 0, đầu có mỏ L2.
- **K:**
  - tay mảnh t: mép trên chạm thân ở 0.54 cap; mép dưới tới cap tại W − FF − 52;
  - chân dày D: mép trên mọc từ mép dưới của tay ở 0.58 cap, xuống baseline tại W − FF.
- **W:** V1 rộng 0.70 W, V2 bắt đầu ở 0.268 W. Hai đầu giữa ở đỉnh cắt phẳng, không loe. Hai nét giữa cắt nhau.
- **Y:**
  - thân lệch phải (tâm 0.509 W);
  - tay trái dày D chạm mép trái thân ở 0.464 cap; tay phải mảnh t chạm mép phải ở 0.53 cap;
  - mép ngoài hai tay chạy thẳng tới góc, không loe; chỉ loe phía trong, mũi cách mép 2·FF.
- **B, P, R:**
  - bụng có đoạn thẳng 49 %, ngoài κ (0.55, 0.70), lòng κ (0.55, 0.84);
  - P, R: bụng xuống tới 0.486 cap; R dùng đúng bụng của P; chân R nghiêng 27° so với phương đứng, mép phải ở W − 40, dày D;
  - B: thanh giữa 0.567 cap; mép ngoài hai bụng gặp nhau tại một điểm (có khấc); bụng trên rộng 0.78.
- **0:** vòng ngoài 289 × 361; lòng 187 × 322, nghiêng 15°.
- **6:**
  - bụng là vòng r 246, lòng 145 × 205, trục −60°;
  - nét lên là một phần vòng lớn 289 × 367 (≈ vòng số 0), lòng 186 × 329, nghiêng 15°;
  - đầu nét cắt theo đường qua (409, 527) và (452, 643).
- **9:** là 6 xoay 180°.
- **8:**
  - vòng dưới 261 × 221, lòng 159 × 181, trục −60°;
  - vòng trên 204 × 159, lòng 116 × 122, trục −60°.
- **3, 5:**
  - bụng là elip 258 × 244 tâm (190, 235); lòng 157 × 220, nghiêng 40°;
  - mở ở trái, cắt dọc x = 0 tới cao 241;
  - 3: chéo mảnh t, mép trái qua (145, 475);
  - 5: thân mảnh t nghiêng 9°, chân thân cắt ngang ở 397.
- **4:**
  - thân ở 0.62 W, đỉnh vượt cap 9;
  - thanh 0.24–0.33 cap, mỏ hướng lên;
  - chéo mảnh t, mép ngoài từ (0, 0.316 cap) tới đỉnh thân.
- **7:** thanh Hb, mỏ trái. Chéo dày D, mép phải qua (W, cap − 15) và (0.433 W, 0). Chân chỉ loe phía phải.
- **1:** đỉnh thân vượt cap 11. Mép trên cờ là đường thẳng từ đỉnh thân tới mũi (0, cap − 100); mép dưới là cung L1.
- **S, Q, 2** (đường cong tự do): giữ nguyên đường cong của designer (`ref_glyphs.json`). Guide gồm elip nhận diện được và tay nắm Bézier.
- **Bold:**
  - cùng các luật trên; lòng co lại 0.7 × (V_Bold − V_Regular);
  - 3, 5: lòng co về phía dưới-phải, giữ mép trên-trái để đầu hở vẫn mở.

### Độ lệch so với v0.2 (`docs/img/v0.3.1-lech-so-voi-v0.2.txt`)
- Các glyph đã dựng lại lệch 0–6 % diện tích.
- W lệch 8 %: đỉnh dưới V2 lệch 12u.
- 7 lệch 11 %: thanh theo bảng nét Hb 40 (bản vẽ 34) và mỏ L2 sâu 54 (bản vẽ 28).

### Còn mở
- **2 Bold:** chưa có bản Bold v0.2. Bản tạm suy ra từ 2 Regular (tổng Minkowski với chữ nhật 37 × 30 rồi nén về cap). Dáng đúng nhưng có bậc nhỏ ở ba mũi nhọn và quá nhiều điểm. Cần designer vẽ.
- Bold U V W X Y Z và các số Bold khác cũng chưa có bản v0.2 để đối chiếu; đang dựng theo luật đo từ Regular.
- Mỏ L2 (54) sâu hơn mỏ trên 3, 5, 7 trong bản vẽ (28): cần designer chọn một giá trị chung.

Ảnh: `docs/img/v0.3.1-Regular.png`, `v0.3.1-Bold.png`, `v0.3.1-dung-elip-Regular.png` (xanh đứt = v0.2), `v0.3.1-dung-elip-Bold.png`.


## v0.3.2 (04/11) — hình gốc của designer là chuẩn

Designer phản hồi: "số 1, 2, 3 lỗi không giống tôi vẽ. Bản bold bị làm sai glyph ban đầu."

**Quyết định.** Không dựng lại hình bằng luật nữa. Glyph = đúng bản vẽ của designer. Guide = hình học nhận diện từ chính đường cong đó, vẽ đè lên như demo của designer (6 7 8 9).
- **Nguồn** (`tools/construct/ref/`):
  - `designer_A.json`: Regular A–Z, trang "Design v0.2 — cân bằng".
  - `designer_B.json`: Bold A–T và bộ số mới nhất (khung `2059:2`, có 6 và 9 vẽ lại, 2 chỉnh).
- **Guide tự nhận diện** (`make_ref.py`):
  - elip (vẽ trọn vòng + 2 trục);
  - vòng compa của loe, mỏ, móc;
  - mép chéo kéo dài;
  - mốc ngang của thanh và tay;
  - tay nắm Bézier cho đường cong tự do dài.
- `glyphs.js` dùng bản vẽ khi có. Phần dựng theo luật chỉ còn cho các glyph **chưa có bản vẽ**: Bold U V W X Y Z và số Bold. Các ô này ghi nhãn đỏ "TẠM (chưa có bản vẽ)". `NO_REF = true` để xem lại bản dựng theo luật nếu cần so sánh.
- Các mục "Luật đo từ v0.2" ở v0.3.1 chỉ còn là số đo tham khảo, không dùng để thay hình.

**Cần designer:** bản vẽ Bold U–Z và bộ số Bold.
