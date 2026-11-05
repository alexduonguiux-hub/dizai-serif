# 12 · Ký tự bổ sung — nhóm 1 + 2 (05/11)

Designer 05/11: "kiểm tra lại còn thiếu ký tự hay symbol nào không?" → "làm nhóm 1 và 2 trước".
Code: `tools/construct/ref/symbols.py` → `designer_D.json` (gộp qua `make_ref.py`). Danh sách ký tự: `SYM`, `COMB`, `LOWX` trong `glyphs.js`. Regular + Bold, dựng theo luật (chấm đỏ trong preview).

## Luật chung
- Cùng hệ nét với dấu câu đã có (`vn_punct.py`): bảng V / H, bút dẹt PHI 20°, họ chấm (Ø dot), nêm loe như ! và nháy.
- Trục toán 330 (như + = ×). Nét toán: đứng 0.62 V, ngang 0.55 V.
- Nét bút (< > « » ‹ › { } £): nét / mảnh, nét \ dày, đúng logic bút.
- Chữ dùng lại, không vẽ lại: C R T M Y hoa của designer; c s u i j thường đã dựng.

## Nhóm 1 (tối thiểu để xuất font)

| Ký tự | Dựng |
|---|---|
| `*` | 6 cánh nêm quanh tâm 0.80 cap, bán kính 150 |
| `< >` | nét bút trên trục toán, cao 400, rộng 400 |
| `\` | gương của / |
| `^` | dấu mũ × 1.35, đỉnh ở cap |
| `_` | gạch dày như gạch nối (0.58 V) ở −150 |
| `` ` `` | dấu huyền đứng riêng, đáy ở 560 |
| `{ }` | nét bút, mũi ở 355, cao −150 … 860 như ( [ |
| `\|` | thanh 0.58 V, −150 … 860 |
| `~` | dấu ngã × 1.7 trên trục toán |
| gạch mềm U+00AD | = gạch nối |
| `ı ȷ` | i, j thường bỏ chấm |
| space, nbsp | chỉ có bề ngang: 230 / Bold 245 |
| dấu tổ hợp U+0300 0301 0302 0303 0306 0308 0309 030A 030C 031B 0323 0327 | xem dưới |

**Dấu tổ hợp** (rộng 0):
- Dùng chung bộ dấu chữ (`vn_punct.marks`), đặt ở vùng dấu chữ thường (đáy 542.4), tâm dời về giữa ô n đứng trước.
- Sừng U+031B bám mép phải mực chữ trước.
- ¨ (0308): hai chấm nặng. ˚ (030A): vòng nét 0.34 V. ˇ (030C): mũ lật dọc. Móc dưới (0327): nét bút cong.
- Vị trí đúng theo từng chữ sẽ làm bằng anchor GPOS mark khi xuất font.

## Nhóm 2

| Ký tự | Dựng |
|---|---|
| `… • ·` | họ chấm: … ba chấm cách 1.8 Ø; • Ø × 1.8 ở trục toán; · chấm ở 300 |
| `« » ‹ ›` | nét bút (bút chữ × 0.62), tâm 250, cao 300, rộng 200 |
| `‚ „` | dấu phẩy ở chân dòng (một / hai) |
| `¡ ¿` | ! ? xoay 180°, đỉnh ở x-height |
| `© ®` | vòng (dày 0.62 V, mảnh 0.45 V, trục nghiêng như O) + C / R hoa × 0.44, bù nét 0.10 V |
| `™` | T M hoa × 0.42, bù nét 0.09 V, đỉnh ở cap |
| `°` | vòng nhỏ R 105, nét 0.42 V, đỉnh ở cap |
| `± ÷ −` | cùng nét + (đứng 0.62 V, ngang 0.55 V); chấm ÷ = 0.95 Ø |
| `‰` | % thêm một vòng dưới |
| `§` | hai s thường × 0.82, s dưới xoay 180°, chồng đúng một bụng → vòng kín ở giữa |
| `¶` | bụng đặc nửa elip + hai thân 0.5 V |
| `† ‡` | thân + thanh là nêm loe |
| `£` | nét bút: móc trên → thân → chân; thanh giữa và thanh đáy 0.6 H |
| `¥` | Y hoa + hai thanh 0.98 H, khe 60 (luật ¥ €) |
| `¢` | c thường + nét đứng 1.1 H xuyên qua |
| `µ` | u thường, thân trái kéo xuống descender |

## Spacing / kerning (`spacing.py`)
- Ký hiệu được spacing như dấu câu (trắng quang học, lề tối thiểu 20).
- Chỉ dấu câu đi liền chữ được kern theo class: `… ‚ „ « » ‹ › ¡ ¿ { }` và gạch mềm (gạch mềm theo giới hạn gạch −60).
- Ký hiệu toán và ký hiệu đứng riêng (`* < > \ ^ _ ` | ~ • · © ® ™ ° ± ÷ − ‰ § ¶ † ‡ £ ¥ ¢ µ`) chỉ chống va, không kern theo hình chữ. Nếu kern theo profile, ~ · − ^ sẽ trượt vào miệng C hay lòng b d (C~ −150, ^d −150).

## QA
- Va chạm: 0 / 0. Dấu tổ hợp đè lên chữ trước là chủ ý.
- Âm tiết Việt và cặp chữ gốc: không đổi so với trước.
- `qa_outline` báo gai ở ™ Bold (đỉnh M thu nhỏ) và ¢ (góc cắt của c, có từ trước).

## Chưa làm (nhóm 3)
- Latin-1 cho từ nước ngoài: Ä Å Æ Ç Ë Î Ï Ð Ñ Ö Ø Û Ü Þ ß ä å æ ç ë î ï ð ñ ö ø û ü þ ÿ, cùng Œ œ Š š Ž ž Ÿ.
- Ký hiệu toán ≠ ≤ ≥ ≈ ¬ ¦, phút / giây ′ ″.
