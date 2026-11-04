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
