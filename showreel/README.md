# Showreel AnNam Serif (12 giây)

`AnNamSerif-Showreel.mp4`: 2034 × 1270 (khung storyboard), 30 fps, 12 giây, H.264 + AAC.

Dựng theo storyboard Figma **Đìzai Serif – WIP · Storyboard** (Story-01 … 09, gồm hai khung mới: câu tục ngữ "Sự học…" + ảnh thuyền, và đoạn tiếng Pháp "Enfin, la guerre d'Indochine…"). Nền giấy `#eae9e6`, chữ `#0e0e0e`, ảnh sepia xuất từ chính file Figma (`img_sb/`); ảnh thuyền được chuyển về cùng bảng màu sepia của ảnh nền.

**Font:** AnNam Serif **v0.934** — `AnNamSerif[XHGT,slnt,wght]` (XHGT 0 = AnNam Serif) + `AnNamSerif-Italic[XHGT,wght]`. Chữ ghép từng ký tự theo kerning thật của font.

**Chuyển động:** theo hướng các mẫu tham khảo (Pinterest 409053578674372562, 957366833301398698): cắt cứng đúng phách 120 BPM, zoom giật nấc, vòng quay glyph, gõ chữ / hiện ký tự ngẫu nhiên, echo, sóng trục variable, xoay theo bước. Không dùng trượt mượt, màn quét, mở tròn, cửa chớp.

## Kịch bản
| Thời gian | Storyboard | Chuyển động |
|---|---|---|
| 0–0,25 s | 01 | Giấy trống |
| 0,25–1,5 s | 02 | Dòng chữ trên cùng gõ ra; cắt vào cận cảnh chữ A khổng lồ, zoom lùi mượt (nhanh rồi chậm dần) ra toàn AN NAM; symbol cắt vào |
| 1,5–2,25 s | 03 | Hai cặp cung xoay mượt thành bông hoa; sóng weight chạy qua AN NAM |
| 2,25–3 s | 04 | Cắt cứng: mọi nét thành cửa sổ nhìn ra ảnh Huế (nháy 1 khung hình) |
| 3–4,5 s | 05–06 | Cắt sang ảnh; A–Z hiện từ chiều sâu (mờ → rõ), rồi lùi về nhường a–z |
| 4,5–6,25 s | 07 | Đường kẻ; A đẩy weight 400 → 700 → 400; dấu mũ, dấu hỏi bật vào → Ẩ; cắt qua Ở Ữ Đ Ặ ặ ơ đ ỹ |
| 6,25–7,5 s | 08 | Địa danh xưa của An Nam hiện từng ký tự ngẫu nhiên, các dòng trôi ngang (kín hai đầu) |
| 7,5–8,75 s | 08b | "Sự học cũng như việc chèo thuyền ngược nước, không *tiến* ắt sẽ *lùi*" hiện từng chữ theo nhịp (chữ bật vào ở Bold rồi lắng về Regular); thuyền cắt vào, bập bềnh |
| 8,75–9,75 s | 08c | "Enfin, la guerre d'Indochine se termine. Le Vietnam est devenu une nation indépendante." — vòng quay glyph: mỗi ký tự lướt qua các chữ hoa tiếng Việt cùng độ rộng rồi khóa vào chữ thật |
| 9,75–12 s | 09 | Cắt sang ảnh Nhà hát Lớn Hà Nội (đã xoá chữ ký trên ảnh); AN NAM / SERIF hiện bằng vòng quay glyph, khóa từ trái sang; VARIABLE · ITALIC · REGULAR ✱ MEDIUM ✱ SEMIBOLD ✱ BOLD gõ ra |

## Nhạc
Giai điệu liên khúc Nhã nhạc cung đình Huế **Lưu thủy – Kim tiền – Xuân phong – Long hổ** (nhạc cổ truyền), ký âm lại từ một bản hòa tấu tham khảo (dò cao độ + nghe), rồi chơi lại bằng nhạc cụ tổng hợp trong `music.py`. Không dùng âm thanh của bản thu gốc; file tham khảo không lưu trong repo.

- Thang: điệu Bắc, Hò = C (Hò C · Xự D · Xang ≈ F♯ (lên dây cao) · Xê G · Cống A).
- 0,25–6,4 s: câu mở **Lưu thủy** — C A C D Xang · G G · C B A C D Xang G.
- 6,25–11,5 s: đoạn nhanh **Long hổ** — A G C A C G D C · A G C A G Xang A C G …; kết về Hò.
- Đàn nhị + sáo chơi giai điệu (liền, có luyến), đàn nguyệt gảy từng nốt, đàn tranh vuốt vào Long hổ; phách, sênh tiền, trống bản giữ nhịp; trống đại, chuông, khánh nhấn các cú cắt hình.

## Bản dùng nhạc thu sẵn (đồng bộ phách)
`beatmap.py` dò phách bản thu, cho hiệu ứng mỗi màn chạy một phách video (0,5 s) trên một phách nhạc, giữ màn ≥ 2 phách (~1,2 s) rồi cắt ở phách mạnh kế tiếp, và xuất thời điểm từng khung hình: `python3 showreel/beatmap.py nhac.wav 37 times.json` rồi `TIMES=times.json node showreel/render.js <thư-mục> 30`. Bản dùng liên khúc Lưu thủy – Long hổ (từ giây 37 của bản hòa tấu tham khảo): ~30 s, nhạc nhỏ dần 2,6 s cuối. **Bản thu đó có bản quyền của người biểu diễn / kênh đăng — không đưa vào repo; cần xin phép hoặc mua quyền trước khi đăng công khai.**

## Dựng lại
```bash
python3 -m http.server 8765        # chạy ở gốc repo
node showreel/render.js /tmp/frames 30
python3 showreel/music.py /tmp/music.wav
ffmpeg -framerate 30 -i /tmp/frames/f%04d.png -i /tmp/music.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest showreel/AnNamSerif-Showreel.mp4
```
Xem trực tiếp: `http://localhost:8765/showreel/showreel.html?play`.
