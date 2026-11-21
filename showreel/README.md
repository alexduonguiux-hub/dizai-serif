# Showreel AnNam Serif (10 giây)

`AnNamSerif-Showreel.mp4`: 2034 × 1270 (đúng khung storyboard), 30 fps, 10 giây, H.264 + AAC.

Dựng theo storyboard Figma **Đìzai Serif – WIP · Storyboard** (Story-01 … 09): nền giấy `#f3f3f1`, chữ đen `#0e0e0e`, ảnh sepia. Ảnh lấy từ chính file Figma (đã chỉnh màu, xuất đúng khung): `img_sb/hue.jpg`, `img_sb/hue_s04.jpg` (Huế), `img_sb/market.jpg` (chợ Đồng Xuân xưa).

**Font:** AnNam Serif **v0.931**, file `AnNamSerifVF[XHGT,slnt,wght]` (họ "AnNam Serif VF", XHGT 0 = AnNam Serif) + `AnNamSerif-Italic[XHGT,wght]`. Chữ ghép từng ký tự đặt theo kerning thật của font.

## Kịch bản
| Thời gian | Storyboard | Chuyển động |
|---|---|---|
| 0–0,3 s | 01 | Giấy trống |
| 0,3–1,6 s | 02 | Dòng chữ trên cùng cuộn lên; symbol hai cặp cung hiện; AN NAM cuộn lên từng chữ |
| 1,6–2,4 s | 03 | Hai cặp cung xoay ngược chiều ±67,5° thành bông hoa |
| 2,4–3,1 s | 04 | Mọi nét chữ + symbol thành cửa sổ nhìn ra ảnh Huế |
| 3,1–4,2 s | 05 | Ảnh mở tròn từ tâm bông hoa; bảng A–Z trắng **hiện từ chiều sâu: mờ → rõ** (lan từ giữa dòng) |
| 4,2–5 s | 06 | Chữ hoa lùi về sau, mờ đi; chữ thường a–z tiến lên rõ dần |
| 5–6,4 s | 07 | Giấy kéo lên; đường kẻ chạy ra; A, rồi dấu mũ, rồi dấu hỏi rơi vào → Ẩ |
| 6,4–8 s | 08 | Đẩy lên: 5 dòng địa danh đứng / nghiêng, trôi ngang ngược chiều |
| 8–10 s | 09 | Ảnh chợ mở như cửa chớp từ giữa; AN NAM trắng hạ xuống; VARIABLE · ITALIC · REGULAR ✱ MEDIUM ✱ SEMIBOLD ✱ BOLD |

## Nhạc
Tự soạn bằng code (`music.py`), không dùng sample: jazz lounge kiểu Sài Gòn thập niên 30 (piano maj9, contrabass, trống chổi, ride) + đàn bầu; nốt nhạc bám theo từng mốc storyboard (đàn bầu luyến khi bông hoa xoay, luyến kiểu thanh hỏi khi dấu hỏi rơi xuống).

## Dựng lại
```bash
python3 -m http.server 8765        # chạy ở gốc repo
node showreel/render.js /tmp/frames 30
python3 showreel/music.py /tmp/music.wav
ffmpeg -framerate 30 -i /tmp/frames/f%04d.png -i /tmp/music.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest showreel/AnNamSerif-Showreel.mp4
```
Xem trực tiếp: `http://localhost:8765/showreel/showreel.html?play`.
