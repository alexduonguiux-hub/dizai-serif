# 09 — Dấu tiếng Việt (chữ hoa) và dấu câu, ký hiệu (v0.4)

Phạm vi: 67 chữ hoa tiếng Việt và 29 dấu câu, ký hiệu, cho cả Regular và Bold.
- Code dựng: `tools/construct/ref/vn_punct.py`, xuất ra `designer_C.json`.
- `make_ref.py` gộp file này vào `ref_glyphs.json` với `src: "rule"`.
- Trong Figma, các glyph này mang nhãn **TẠM** đến khi designer duyệt hoặc vẽ lại.

## S15 — Nét bút dẹt cho dấu và dấu câu cong

Mọi nét cong hoặc xiên của dấu là **một nét bút dẹt** (luật S3).
- Bút nghiêng φ = 20°.
- Độ dày đo vuông góc với nét: `w(θ) = √((N·sin(θ − φ))² + m²)`, với θ là hướng nét.
- Hai mép nét là hai đường song song biến thiên. Code khớp lại bằng Bézier (least-squares) và chia đôi đoạn cho tới khi sai số dưới 0.6 u.
- Độ dày được làm mượt theo chiều dài nét (Gauss, σ = 14 u). Nhờ vậy mối nối giữa các đoạn cong không tạo gờ.
- Ở phía lòng của chỗ cong gắt, mép nét không lùi quá 0.8 lần bán kính cong. Code dùng min mềm nên không sinh nút thắt.

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
| sắc | nét thẳng đi lên-phải nên là nét mảnh; đầu trên đậm hơn (taper 0.72 → 1.27) | rộng 96, cao 122 |
| huyền | nét thẳng đi xuống-phải nên là nét dày (D thu nhỏ); mảnh dần về chân (1.08 → 0.66) | như sắc |
| mũ | dựng như đỉnh A: hai cạnh ngoài, hai cạnh trong song song; chân trái mảnh, chân phải dày (× 0.85 để lòng mở ở Bold); chân cắt ngang; đỉnh cắt phẳng 0.2 N | rộng 300, cao 142 |
| trăng | nửa elip ngoài trừ lòng elip xoay 12° (trục nghiêng như lòng O): đáy dày 0.72 N, hai đầu ≈ 0.4 N, cắt ngang | rx 118, ry 96 |
| ngã | tâm nét là một chu kỳ sin: biên độ 32, bước sóng 260; đoạn đi lên mảnh, đoạn đi xuống dày. Bold: biên độ 28, giãn ngang 1.14 (bán kính đỉnh lớn hơn nửa nét) | rộng 260 |
| hỏi | ? thu nhỏ: vòng là cung tròn r 52 (168° → −40°), đuôi về giữa; bút 0.8 bút dấu | cao 170 |
| nặng | chấm tròn, cùng họ với dấu chấm | Ø 100 / Bold 138 |
| sừng ơ ư | **một tấm chung**: nét ra phải rồi vút lên; dày 0.34 V → 0.62 V; kết bằng giọt Ø 0.62 V | bám Ư ở mép ngoài thân phải, cao 0.9 cap; bám Ơ ở vai vòng O, góc 38° |

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
- Khe dấu–chữ nhỏ nhất là 39 (luật ≥ 36). Khe dấu–dấu nhỏ nhất là 32 (luật ≥ 30).
- Chữ cao nhất là Ằ Bold, đỉnh ở 1054.

## Dấu câu và ký hiệu

| Ký tự | Dựng |
|---|---|
| `.` | chấm tròn, Ø 120 (1.18 V); Bold Ø 164 |
| `,` | chấm và đuôi thon cong xuống-trái tới −1.25 Ø |
| `: ;` | chấm trên có đỉnh ở 480 (x-height tạm, chờ luật S10) |
| `!` | nét thon, đỉnh cắt ngang rộng 0.98 V, chân rộng 0.42 V, hai cạnh lõm nhẹ như loe |
| `?` | một nét bút chữ: đầu trái dày, vòng phải, thân đứng xuống |
| `' "` | nét thon từ 711 xuống 455, rộng 0.86 V → 0.34 V |
| `’ ‘ ” “` | dấu phẩy nâng lên (‘ là ’ xoay 180°) |
| `- – —` | dày 0.58 V (giữa H và V), tâm ở 330; `-` dài 250, `–` dài 420, `—` dài 920 |
| `( )` | một nét bút cong: dày ở giữa, mảnh ở hai đầu; từ −150 tới 860 |
| `[ ]` | thân 0.86 V, tay 1.15 H dài 150 |
| `/` | dày 0.58 V, từ −130 tới 830 |
| `+ = ×` | nét đứng 0.62 V, nét ngang 0.55 V (ngang dày như bộ số, Hf); `×` dày 0.6 V; tâm ở 330 |
| `#` | hai nét đứng nghiêng 10°, dày 0.66 V; hai nét ngang 0.5 V |
| `%` | hai vòng kiểu O (lòng xoay 30°) và nét chéo 0.6 V |
| `$` | S của designer và nét đứng dày 1.1 H, vươn từ −100 tới 800 |
| `€` | C của designer và hai thanh dày 1.05 H, ở 300 và 430 |
| `&` | một nét bút liền: chân phải đi lên-trái (dày), vòng trên là oval đứng với nét nhẹ 0.78, bụng dưới, tay phải vút lên |
| `@` | vòng ngoài là nét bút từ 0° tới 300°; bên trong là a một tầng, thân a cong chữ U nhập vào vòng ngoài |

**Chưa làm:**
- `₫` cần đ thường, chờ luật chữ thường S10.

**Cần designer xem kỹ:**
- `&` Bold: lòng vòng trên nhỏ.
- `@` và `?`: là hình dựng theo luật, chưa có bản vẽ.

Ảnh:
- `img/v0.4-chu-hoa-viet.png`
- `img/v0.4-dau-cau.png`
- `img/v0.4-van-ban.png`
