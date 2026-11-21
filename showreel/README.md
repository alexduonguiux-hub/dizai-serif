# Showreel AnNam Serif (12 giây)

`AnNamSerif-Showreel.mp4`: 2034 × 1270 (khung storyboard), 30 fps, 12 giây, H.264 + AAC.

Dựng theo storyboard Figma **Đìzai Serif – WIP · Storyboard** (Story-01 … 09, gồm hai khung mới: câu tục ngữ "Sự học…" + ảnh thuyền, và đoạn tiếng Pháp "Enfin, la guerre d'Indochine…"). Nền giấy `#f3f3f1`, chữ `#0e0e0e`, ảnh sepia xuất từ chính file Figma (`img_sb/`).

**Font:** AnNam Serif **v0.933** — `AnNamSerif[XHGT,slnt,wght]` (XHGT 0 = AnNam Serif) + `AnNamSerif-Italic[XHGT,wght]`. Chữ ghép từng ký tự theo kerning thật của font.

**Chuyển động:** theo hướng các mẫu tham khảo (Pinterest 409053578674372562, 957366833301398698): cắt cứng đúng phách 120 BPM, chữ rải rác rồi "khớp" vào hàng, gõ chữ / hiện ký tự ngẫu nhiên, sóng trục variable, xoay theo bước. Không dùng trượt mượt, màn quét, mở tròn, cửa chớp.

## Kịch bản
| Thời gian | Storyboard | Chuyển động |
|---|---|---|
| 0–0,25 s | 01 | Giấy trống |
| 0,25–1,5 s | 02 | Dòng chữ trên cùng gõ ra; symbol cắt vào; AN NAM hiện từng chữ (lệch cao, lệch weight) rồi khớp vào hàng ở 1,25 s |
| 1,5–2,25 s | 03 | Hai cặp cung xoay thành bông hoa theo 4 nấc; sóng weight chạy qua AN NAM |
| 2,25–3 s | 04 | Cắt cứng: mọi nét thành cửa sổ nhìn ra ảnh Huế (nháy 1 khung hình) |
| 3–4,5 s | 05–06 | Cắt sang ảnh; A–Z hiện từ chiều sâu (mờ → rõ), rồi lùi về nhường a–z |
| 4,5–6,25 s | 07 | Đường kẻ; A đẩy weight 400 → 700 → 400; dấu mũ, dấu hỏi bật vào → Ẩ; cắt qua Ở Ữ Đ Ặ ặ ơ đ ỹ |
| 6,25–7,5 s | 08 | Địa danh xưa của An Nam hiện từng ký tự ngẫu nhiên, các dòng trôi ngang (kín hai đầu) |
| 7,5–8,75 s | 08b | "Sự học cũng như việc chèo thuyền ngược nước, không *tiến* ắt sẽ *lùi*" hiện từng chữ theo nhịp; thuyền cắt vào, bập bềnh |
| 8,75–9,75 s | 08c | "Enfin, la guerre d'Indochine se termine. Le Vietnam est devenu une nation indépendante." gõ ra từng ký tự |
| 9,75–12 s | 09 | Cắt sang ảnh chợ; AN NAM gom lại như mở đầu; VARIABLE · ITALIC · REGULAR ✱ MEDIUM ✱ SEMIBOLD ✱ BOLD gõ ra |

## Nhạc
Giai điệu liên khúc Nhã nhạc cung đình Huế **Lưu thủy – Kim tiền – Xuân phong – Long hổ** (nhạc cổ truyền), ký âm lại từ một bản hòa tấu tham khảo (dò cao độ + nghe), rồi chơi lại bằng nhạc cụ tổng hợp trong `music.py`. Không dùng âm thanh của bản thu gốc; file tham khảo không lưu trong repo.

- Thang: điệu Bắc, Hò = C (Hò C · Xự D · Xang ≈ F♯ (lên dây cao) · Xê G · Cống A).
- 0,25–6,4 s: câu mở **Lưu thủy** — C A C D Xang · G G · C B A C D Xang G.
- 6,25–11,5 s: đoạn nhanh **Long hổ** — A G C A C G D C · A G C A G Xang A C G …; kết về Hò.
- Đàn nhị + sáo chơi giai điệu (liền, có luyến), đàn nguyệt gảy từng nốt, đàn tranh vuốt vào Long hổ; phách, sênh tiền, trống bản giữ nhịp; trống đại, chuông, khánh nhấn các cú cắt hình.

## Dựng lại
```bash
python3 -m http.server 8765        # chạy ở gốc repo
node showreel/render.js /tmp/frames 30
python3 showreel/music.py /tmp/music.wav
ffmpeg -framerate 30 -i /tmp/frames/f%04d.png -i /tmp/music.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest showreel/AnNamSerif-Showreel.mp4
```
Xem trực tiếp: `http://localhost:8765/showreel/showreel.html?play`.
