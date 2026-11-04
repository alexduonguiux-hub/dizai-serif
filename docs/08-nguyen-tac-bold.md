# Đìzai Serif — Nguyên tắc vẽ Bold (rút ra từ bản Bold của designer)

Nguồn đo: Bold A–T và số 0–9 do designer vẽ, so với Regular.
- Đo tự động: `tools/construct/ref/` (đường quét ngang/dọc trên raster 1u, mật độ mực).
- Đơn vị font: UPM 1000, cap 700.

## 1. Bảng nét

| | Regular | Bold | Δ |
|---|---|---|---|
| Thân đứng V | 102 | 139 | +37 |
| Thân mảnh t (N, M) | 44–46 | 74 | +28–30 |
| Thanh / tay Hb (E, F, H, Z) | 40 | 68 | +28 |
| Nét chéo dày D (A, M, N) | 100 | 146 | +46 |
| Nét chéo mảnh (A, V, W, X, Y) | 44–47 | 74–77 | +30 |
| Vòng (O, Q): chỗ dày / chỗ mảnh | 93 / 58 | 132 / 96 | +38 mỗi phía |
| C, G: thành trái / đỉnh | 107 / 41 | 147 / 68 | +40 / +27 |

## 2. Nguyên tắc dày lên

1. **Mép ngoài giữ nguyên, nét dày vào phía lòng.**
   - Thân trái: mép trái đứng yên, mép phải lùi vào lòng (H, E, B, D, P, R, K: 22.7–124.7 → 22.7–161.5).
   - Thân phải: dịch ra ngoài, nên chữ rộng thêm. H: thân phải 374–476 → 380–519; lòng chỉ hẹp đi ~31.
2. **Thanh giữa nở đều hai phía** (E, H: 351–391 → 337–405).
   - Tay trên dày xuống (660 → 632); tay dưới dày lên (40 → 68).
   - Ngoại lệ có chủ ý: tay dưới của L giữ 40.
3. **Vòng:** mép ngoài giữ nguyên (O, Q vẫn rộng 723). Lòng co đều ~38 mỗi phía, kể cả chỗ mảnh. Trục nghiêng của lòng giữ nguyên.
4. **Nét chéo (A):**
   - Chân ngoài cố định trên baseline; nửa phải dịch theo phần tăng bề rộng (A +23).
   - Đỉnh dịch theo nửa phần tăng bề rộng; mặt cắt đỉnh 24 → 20.
   - Mép trong lùi vào; chạc tự hạ xuống khi nét dày.
5. **Loe và mỏ giữ nguyên hình** (vòng r ≈ 114.5), chỉ trượt theo mép nét chúng gắn vào.
   - Mỏ của E: x trượt theo bề rộng (+48), y theo tay (−28).
6. **Bề rộng tăng** theo số thân phải dịch ra:

   | Chữ | Δ bề rộng |
   |---|---|
   | I, J | +37 |
   | H | +43 |
   | E, F, L, T | +48 |
   | D | +51 |
   | K, N, R, S | +57 |
   | C, G | +36 |
   | B | +31 |
   | P | +28 |
   | A | +23 |
   | Q | +12 |
   | M | +6 |
   | O | 0 |

7. **Mật độ mực** (mực ÷ ((rộng + 80) × 700)), tỉ lệ Bold/Regular:
   - trung bình A–T: 1.29;
   - chữ thân đứng (H, T, K, R): 1.26–1.27;
   - chữ chéo (A, M, N): 1.32–1.36.

## 3. Áp dụng cho U V W X Y Z (chưa có bản vẽ Bold)

Dựng bằng `tools/construct/ref/bold_UZ.py`.

| Chữ | Cách dựng | Bề rộng | Tỉ lệ mật độ |
|---|---|---|---|
| U | Thân lấy y nguyên H Bold (kèm loe). Bụng: mép ngoài là nửa vòng nối hai mép ngoài thân; lòng là nửa vòng nối hai mép trong thân, đáy dày 40 + 38 | 541 | 1.28 |
| V | A Bold của designer xoay 180°, bỏ thanh; hai mép trong gặp ở chạc (Regular: V ≡ A xoay 180°) | 695 | 1.37 |
| W | 4 nét (hai V lồng nhau). Mép ngoài từng nét giữ, giãn theo bề rộng +25; đáy nhọn phẳng 20; dày 146 / mảnh 74 vào trong; đỉnh giữa cắt phẳng; loe ngoài của designer trượt theo mép | 801 | 1.30 |
| X | Góc ngoài giữ (phải +23). Dày 132, mảnh 72, chỉnh cho mật độ ≈ nhóm chữ chéo. Loe trong của designer trượt theo mép | 665 | 1.33 |
| Y | Rộng +23, tâm thân dịch +11.5 (như T); thân 139. Mép ngoài hai tay giữ độ dốc; tay trái dày 146, tay phải mảnh 77; loe trong và loe chân thân trượt theo mép | 655 | 1.35 |
| Z | Rộng +48 (như E). Thanh 68; mỏ trượt theo thanh. Chéo 134 qua góc (W, 683) và (0, 17) như Regular; mép ngoài chéo cắt vát đầu thanh (mặt cắt đứng 683–700 ở góc trên-phải, 0–17 ở góc dưới-trái) | 513 | 1.32 |

Đây là bản dựng theo nguyên tắc, chưa phải bản vẽ tay. Cần designer duyệt, đặc biệt W và X.
