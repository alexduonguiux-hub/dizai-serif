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

## Sửa sau duyệt (designer 05/11: "Lỗi")
- `{ }`: mũi giữa răng cưa, đầu cắt ngang cụt. Nay chỉ dựng nửa trên rồi cắt ngang ở trục mũi 355 và lật gương, nên hai nửa trùng khít, mũi sạch. Đầu nét cắt đứng ở mép phải.
- `< > ‹ › « »`: đỉnh lởm chởm vì hai nét bút chồng mặt cắt. Nay dựng bằng đa giác (như dấu mũ): mép ngoài gặp nhau thành đỉnh nhọn, mép trong lùi đúng độ dày bút từng nhánh (nhánh / mảnh 31, nhánh \ dày 68), hai đầu cắt đứng.
- Móc dưới (Ç ç U+0327): bản đầu dài, mảnh, thả tới −230. Nay cổ ngắn, bụng móc dày, đáy khoảng −165.

## Nhóm 3 (designer 05/11: "làm tiếp nhóm 3") — `symbols.py: group3()`

| Ký tự | Dựng |
|---|---|
| Ä Ë Ï Ö Ü Ÿ ä ë ï ö ü ÿ | chữ gốc + hai chấm (chấm nặng, cách 0.75 Ø). Hoa: dấu ở đáy 750, tâm theo anchor của chữ hoa. Thường: đáy 542.4, tâm theo phần x-height. ï î dùng ı |
| Å å | vòng (nét 0.34 V); Å: vòng sát đỉnh A hơn (khe 0.6 khe dấu) |
| Î Û î û · Ñ ñ · Š Ž š ž | mũ, ngã: cùng dấu tiếng Việt; mũ ngược = mũ lật dọc |
| Ç ç | móc dưới U+0327 bám đáy giữa chữ |
| Ð | = Đ |
| Ø ø | O / o + nét / mảnh 0.42 V, dốc khoảng 60°, chìa ra ngoài vòng 30 |
| Æ | A bỏ chân phải (cắt dọc qua đỉnh) + E có thân đứng tại đỉnh A |
| Œ | O cắt ở 0.60 bề ngang + E có thân trùng chỗ cắt |
| æ œ | a + e / o + e chồng một vách |
| Þ | thân P cao trọn cap, bụng P hạ 150 |
| þ | p + đỉnh thân b (vươn lên ascender) |
| ð | o + cổ nét bút cong lên trái, mảnh dần; thanh gạch thẳng hơi chếch, cắt cổ ở khoảng 585 |
| ß | chân loe của l + MỘT nét bút liền (thân → vòm → eo → bụng dưới → đuôi dừng trước thân); bút đứng rộng đúng bằng thân chữ thường |
| ≠ | = + nét / 0.45 V |
| ≤ ≥ | < > × 0.84, nâng 85, thanh dưới 0.55 V |
| ≈ | hai ~ × 0.78, cách ±92 quanh trục toán |
| ¬ | thanh ngang + đuôi xuống bên phải |
| ¦ | thanh 0.58 V gãy (−150 … 300, 410 … 860) |
| ′ ″ | nháy thẳng ' nghiêng 14° |

- Spacing / kern: chữ có dấu (Ä Ç Ñ Š…) dùng spacing và kern của chữ gốc (canh theo phần chữ gốc). Æ Œ Ø Ð Þ ß æ œ ø ð þ tự tính spacing, kern theo class của chính chúng. Ký hiệu toán ≠ ≤ ≥ ≈ ¬ ¦ ′ ″: chỉ chống va.
- QA: va chạm 0 / 0; âm tiết Việt không đổi; `qa_outline` không có cờ mới.
- Tổng: 322 ký tự mỗi weight.
