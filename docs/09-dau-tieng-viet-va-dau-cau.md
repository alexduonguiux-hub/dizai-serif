# 09 — Dấu tiếng Việt (chữ hoa) và dấu câu, ký hiệu (v0.4)

Phạm vi: 67 chữ hoa tiếng Việt và 29 dấu câu, ký hiệu, cho cả Regular và Bold.
- Code dựng: `tools/construct/ref/vn_punct.py`, xuất ra `designer_C.json`.
- `make_ref.py` gộp file này vào `ref_glyphs.json` với `src: "rule"`.
- Trong Figma, các glyph này mang nhãn **TẠM** đến khi designer duyệt hoặc vẽ lại.

## S15 — Nét bút dẹt cho dấu và dấu câu cong

Mọi nét cong hoặc xiên của dấu là **một nét bút dẹt** (luật S3).
- Bút nghiêng φ = 20°.
- Độ dày đo vuông góc với nét: `w(θ) = √((N·sin(θ − φ))² + m²)`, với θ là hướng nét.
- Hai mép nét lấy mẫu dày trên **toàn nét liền một mạch**, không ghép mảnh, nên mối nối không có gờ. Code khớp lại bằng chuỗi Bézier (least-squares) và chia đôi cho tới khi sai số dưới 0.6 u. Hai đầu nét khép bằng hai nắp.
- Độ dày được làm mượt theo chiều dài nét (Gauss, σ = 22 u). Lý do: các mối nối Hermite có độ cong nhảy bậc.
- Phía lòng không kẹp. Chỗ mép trong gập lại (đuôi én), pathops gộp thành góc trong như vết bút thật; lỗ dưới 400 u² bị bỏ.
- Ở Bold, các khung cong gắt được nới ra để góc trong không thành khấc: `?` × 1.15, `&` × 1.18, vòng dấu hỏi r 60.

| | N | m | Nét đứng | Nét ngang |
|---|---|---|---|---|
| Bút chữ Regular (? & ( ) @) | 105 | 26 | 102 = V | 44 ≈ H |
| Bút chữ Bold | 146 | 46 | 139 = V | 68 = H |
| Bút dấu Regular (0.74 N) | 78 | 26 | 77 | 37 |
| Bút dấu Bold | 108 | 44 | 109 | 57 |

## S11 — Dấu (bộ `.case` cho chữ hoa), số đo Regular

Bold giãn ngang × 1.08. Mọi số ở dưới tính theo đơn vị u.

| Dấu | Dựng | Số đo |
|---|---|---|
| sắc | nét thẳng đi lên-phải, hình nêm: đầu trên dày 0.80 N, chân 0.36 N | rộng 96, cao 122 |
| huyền | **sắc lật ngang** (đối xứng gương: cùng dài, cùng góc, cùng hình nêm). Designer 04/11: "dấu sắc và huyền không đồng bộ" → bỏ chênh mảnh/dày theo bút giữa hai dấu | như sắc |
| mũ | dựng như đỉnh A: hai cạnh ngoài, hai cạnh trong song song; chân trái mảnh, chân phải dày (× 0.85 để lòng mở ở Bold); chân cắt ngang; đỉnh cắt phẳng 0.2 N | rộng 300, cao 142 |
| trăng | **lưỡi liềm đối xứng** (designer 04/11: "dấu ă cũng hơi lỗi"): nửa elip ngoài trừ lòng elip có tâm nâng 0.5 rv; đáy dày 0.66 N, hai đầu thon 0.42 N, cắt ngang | rx 112, ry 90 (Bold 100) |
| ngã | tâm nét là một chu kỳ sin: biên độ 32, bước sóng 260; đoạn đi lên mảnh, đoạn đi xuống dày. Bold: biên độ 28, giãn ngang 1.14 (bán kính đỉnh lớn hơn nửa nét) | rộng 260 |
| hỏi | ? thu nhỏ: vòng là cung tròn r 52 (Bold 60), quét 168° → −40°, đuôi về giữa; bút 0.8 bút dấu | cao 170 |
| nặng | chấm tròn, cùng họ với dấu chấm | Ø 100 / Bold 138 |
| sừng ơ ư | **một tấm chung**, tâm nét là **một cung Bézier liền** (designer 04/11: "điều chỉnh nét cong của dấu ư lại cho smooth"); dày 0.34 V → 0.64 V theo smoothstep; đầu cắt phẳng ngang (bỏ giọt tròn) | Ơ bám vai vòng O ở góc 38°; **Ư bám mép ngoài thân phải ở cùng cao độ** nên đầu sừng hai chữ ngang nhau, và ở Ư sừng thay cho loe ngoài của thân phải (designer 04/11: "dấu ư lỗi và không đồng bộ") |

**Vị trí dấu:**
- Đáy dấu thấp nhất ở y = 750, tức cap + overshoot 11.3 + khe 36.
- Tâm ngang của dấu đặt ở tâm hộp mực của chữ. Riêng E đặt ở 0.44 bề ngang, tâm thị giác lệch về phía thân.
- Mũ đi với sắc, huyền hoặc hỏi: dấu thanh nằm **bên phải** mũ. Đáy dấu thanh ngang 0.45 chiều cao mũ, rồi đẩy sang phải tới khi khe với mũ đạt 30.
- Ngã đi với mũ, và mọi dấu thanh đi với trăng: dấu thanh chồng lên trên, cách 30.
- Nặng nằm dưới đáy thật của chữ (U ở −14.2), cách 36.
- Chữ có dấu giữ bề ngang của chữ gốc; dấu được phép tràn ra ngoài.

**Đ:** thanh ngang dày H cắt qua thân trái của D, tâm ở 350. Thanh vươn ra ngoài thân 0.62 V và vào trong thân 0.9 V.

**QA (máy đo, 120 chữ × 2 weight):**
- Không có vi phạm.
- Khe dấu–chữ nhỏ nhất là 39 (luật ≥ 36). Khe dấu–dấu nhỏ nhất là 32.1 (luật ≥ 30). Khe dấu nặng–chữ nhỏ nhất là 38.
- Chữ cao nhất là Ằ Bold, đỉnh ở 1054.

## Dấu câu và ký hiệu

| Ký tự | Dựng |
|---|---|
| `.` | chấm tròn, Ø 120 (1.18 V); Bold Ø 164 |
| `,` | chấm tròn và đuôi thon cong xuống-trái tới −1.25 Ø; **đuôi rời chấm tiếp tuyến** ở điểm phải nhất của chấm (mép phải đuôi trùng mép chấm, không còn mép thẳng thò ra — designer 04/11: "vẫn lỗi nét thừa ở các glyph"); dùng chung cho `; ’ ‘ ” “`. **Đuôi không vuốt nhọn**: kéo quá rồi cắt ngang ở −1.12 Ø, mặt cắt 27 u / 35 u (designer 04/11: "đuôi nhọn … nên cắt ngang phần nhọn 1 tí") |
| `: ;` | chấm trên có đỉnh ở 480 (x-height tạm, chờ luật S10) |
| `!` | nét thon, đỉnh cắt ngang rộng 0.98 V, chân rộng 0.42 V, hai cạnh lõm nhẹ như loe |
| `?` | **lấy phần đầu số 2 của designer** (vòng móc + đầu nét trái), cắt ở y 400; thân là một cung Hermite liền tiếp tuyến với sống 2, thon về 0.78 V, cắt ngang; chấm cùng họ dấu chấm (designer 04/11: "điều chỉnh nét của dấu ? cho smooth hơn") |
| `' "` | nét thon từ 711 xuống 455, rộng 0.86 V → 0.34 V |
| `’ ‘ ” “` | dấu phẩy nâng lên (‘ là ’ xoay 180°) |
| `- – —` | dày 0.58 V (giữa H và V), tâm ở 330; `-` dài 250, `–` dài 420, `—` dài 920 |
| `( )` | **lưỡi liềm serif**: hai elip đồng tâm, dày nhất ở giữa 0.85 V, thon về hai đầu ≈ 0.55 H, hai đầu cong vào (ry ngoài chỉ hơn nửa chiều cao 8 %), cắt ngang ở −150 và 860 (designer 04/11: "( ) nên có glyph phổ biến của dòng serif") |
| `[ ]` | thân 0.86 V, tay 1.15 H dài 150 |
| `/` | dày 0.58 V, từ −130 tới 830 |
| `+ = ×` | nét đứng 0.62 V, nét ngang 0.55 V (ngang dày như bộ số, Hf); `×` dày 0.6 V; tâm ở 330. `×` là hai thanh xoay ±45°, dài 430, **đầu cắt vuông góc với nét** (designer 04/11: "các góc cắt hơi kỳ") |
| `#` | hai nét đứng nghiêng 10°, dày 0.66 V; hai nét ngang 0.5 V |
| `%` | hai vòng kiểu O (lòng xoay 30°) và nét chéo 0.6 V |
| `$` | S của designer và nét đứng dày 1.1 H, vươn từ −100 tới 800 |
| `€` | C của designer và hai thanh dày 1.05 H, ở 300 và 430 |
| `&` | **dựng từ số 8 của designer, theo dáng & serif cổ điển** (designer 04/11: "ký tự & cũng lỗi", "không giống glyph phổ biến cùng dòng"): vòng trên chảy thành **chân dày (\\)** D 100 / 146 xuống chân phải; bụng dưới cắt ở góc −40° rồi đi tiếp thành **tay mảnh (/)** t 44 / 74 lên tới 0.52 cap bên phải, cắt chéo qua chân thành chữ X (đúng logic bút: / mảnh, \\ dày). Tay đi trùng nét bụng từ −62° tới −40° nên mối nối liền. **Loe S5** ở hai góc chân và hai góc đầu tay (compa r 112, chìa 23 u), như chân K, X (designer 04/11: "& thiếu module loe như glyph chữ"). Đầu tay **cắt ngang ở 0.52 cap** và loe theo phương ngang, như đầu tay K ở cap |
| `@` | vòng ngoài là nét bút từ 0° tới 300°; bên trong là a một tầng, thân a cong chữ U nhập vào vòng ngoài |

## QA nét thừa và lỗi (designer 04/11: "QA/QC lại hết các nét thừa và lỗi")

- **Dọn tự động** (`tools/construct/ref/tidy.py`, chạy trong `make_ref.py`):
  - Gộp mẩu thừa và khấc dưới 2.5 u; độ lệch hình dưới 1.3 u.
  - Bỏ điểm trùng và điểm thừa nằm thẳng hàng.
  - Bỏ gai do mẩu ngắn quay ngược.
  - Nắn gãy dưới 20° giữa hai đoạn cong cho liền mạch G1, kể cả tay nắm suy biến.
  - Bỏ vòng kín dưới 400 u².
  - Với bản vẽ designer: chỉ dọn nút thừa và nắn gãy nhỏ; giữ mọi mũi nhọn chủ ý (mỏ E, đầu S và C, mũi loe).
- **Kiểm tra** (`python3 tools/construct/qa_outline.py`):
  - Quét đoạn ngắn, gai, gãy, điểm trùng, điểm thẳng hàng, vòng li ti.
  - Bỏ qua lỗi kế thừa nguyên vẹn từ bản vẽ designer.
  - Kết quả: trước khi dọn có **239** lỗi trên 101 glyph dựng theo luật. Sau khi dọn còn đúng các chỗ chủ ý: hai đầu nhọn của C trong €, chỗ giao bụng a với thân trong @, mũi loe chân &, chỗ thân ? gặp vòng số 2.
  - Bản vẽ designer: dọn 12 mẩu thừa dưới 2.5 u (A Bold, K, M, J Bold, 3, 5, 6 Bold, 9 Bold, V Bold) và các gãy G1 ở A Bold, V Bold, J, 8 Bold.

**Chưa làm:**
- `₫` cần đ thường, chờ luật chữ thường S10.

**Cần designer xem kỹ:**
- `@`: là hình dựng theo luật, chưa có bản vẽ.

Ảnh:
- `img/v0.4-chu-hoa-viet.png`
- `img/v0.4-dau-cau.png`
- `img/v0.4-van-ban.png`
