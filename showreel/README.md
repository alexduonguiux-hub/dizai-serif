# Showreel AnNam Serif (10 giây)

`AnNamSerif-Showreel.mp4`: 1920 × 1080, 30 fps, 10 giây, H.264 + AAC. Mood theo frame Home trong Figma *Đìzai Studio – Website – NEW* (`10:1457`): nền giấy `#f0efee`, xanh đậm `#215028`, xanh nhạt `#749674`, chữ hoa cỡ lớn cắt sát cap, logo con dấu.

## Kịch bản (120 BPM, mỗi cú cắt rơi đúng phách)
| Thời gian | Cảnh | Chuyển động (tham khảo) |
|---|---|---|
| 0–1 s | AN NAM ghép từ từng chữ, trượt lên khỏi mặt nạ, đậm dần 400 → 700 | chữ cuộn trong khung (ref 2) |
| 1–2 s | Chữ A khổng lồ bị cắt khung, đổi độ đậm; ơ nghiêng xoay vào | một ký tự đầy khung, xoay vào (ref 1) |
| 2–3 s | 7 hàng AN NAM SERIF trôi ngang ngược chiều, hai hàng lật ngược, cuộn vào/ra kiểu máy đánh bạc | ref 2 |
| 3–4 s | 8 thẻ dấu tiếng Việt (Ắ ệ Ộ ữ Ợ ỹ Đ ẫ), cắt mỗi 1/16 nốt, Roman/Italic xen kẽ | cắt nhanh qua thẻ màu (ref 1) |
| 4–5,5 s | Chồng 7 dòng “Sài Gòn” 400 → 700, sóng độ đậm, tách khoảng chữ | chồng nhiều độ đậm, tách chữ (ref 1) |
| 5,5–7 s | Poster xoay khối lập phương 3D: AN NAM → SERIF 2026 → Việt Nam | xoay khối (ref 3) |
| 7–8 s | Lưới & nghiêng lộn vòng theo đường chéo | lưới ký tự xoay (ref 1) |
| 8–10 s | End card bố cục giống Home: AN NAM / SERIF / con dấu + 2026 (số cuộn như màn loading) | |

## Nhạc
Tự soạn bằng code (`music.py`), không dùng sample nên không vướng bản quyền: tiếng gảy kiểu đàn tranh (có luyến/nhấn) theo thang ngũ cung, mõ gỗ ở đoạn cắt nhanh, kick/hi-hat tối giản, tiếng vút khi khối xoay, tiếng cồng ở end card.

## Dựng lại
```bash
python3 -m http.server 8765        # chạy ở gốc repo
node showreel/render.js /tmp/frames 30
python3 showreel/music.py /tmp/music.wav
ffmpeg -framerate 30 -i /tmp/frames/f%04d.png -i /tmp/music.wav -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest showreel/AnNamSerif-Showreel.mp4
```
Xem trực tiếp trong trình duyệt: `http://localhost:8765/showreel/showreel.html?play`. Mọi chuyển động nằm trong hàm `render(t)` của `showreel.html`.
