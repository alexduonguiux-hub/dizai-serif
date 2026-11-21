# Showreel AnNam Serif (10 giây)

`AnNamSerif-Showreel.mp4`: 1920 × 1080, 30 fps, 10 giây, H.264 + AAC. Mood theo frame Home trong Figma *Đìzai Studio – Website – NEW* (`10:1457`): nền giấy `#f0efee`, xanh đậm `#215028`, xanh nhạt `#749674`, chữ hoa lớn cắt sát cap, logo con dấu; thêm ảnh phong cách Indochine.

**Font:** AnNam Serif **v0.929**, file variable `AnNamSerif[XHGT,slnt,wght]` (wght 400–700 · slnt 0 → −10° · x-Height 495 Serif → 535 Golden) + `AnNamSerif-Italic[XHGT,wght]`. Chữ ghép từng ký tự (AN NAM, tiếng việt…) đặt theo vị trí kerning thật của font, đo lại mỗi frame. Mọi chữ nằm trọn trong khung (không cắt trên dưới), không dùng chữ lật ngược.

## Kịch bản (120 BPM, mỗi cú cắt rơi đúng phách)
| Thời gian | Cảnh |
|---|---|
| 0–1 s | AN NAM ghép từng chữ (đúng kerning), đậm dần 400 → 700 |
| 1–1,5 s | Ảnh mặt tiền phố cổ Hà Nội nằm trong chữ AN NAM |
| 1,5–2 s | Ảnh áo dài, nón lá, tường vàng cửa chớp xanh; chữ nghiêng “Sài Gòn” cuộn vào |
| 2–3 s | 5 hàng AN NAM SERIF trôi ngang ngược chiều, cuộn vào/ra |
| 3–4 s | 8 thẻ dấu tiếng Việt cắt theo 1/16 nốt, xen thẻ màu và thẻ ảnh (gạch bông, sen, nội thất, mặt tiền) |
| 4–6,5 s | **Ba thanh kéo:** con trỏ kéo lần lượt WEIGHT 400 → 700, SLANT 0 → −10°, x-HEIGHT 495 → 535 (tên đổi AnNam Serif → AnNam Golden, chữ t đổi dạng ở 515), rồi cả ba cùng lùi về |
| 6,5–7,5 s | Ảnh nội thất Indochine + danh sách kiểu chữ, mỗi dòng đặt bằng chính kiểu đó (Regular, Medium Slant, Bold Italic, Golden …) |
| 7,5–8 s | Chữ t khổng lồ trên nền hồ sen, x-height tăng, đúng phách bật sang t Golden |
| 8–10 s | End card: ảnh áo dài trong khung vòm cửa, AN NAM / Serif → Golden / con dấu + số x-height chạy 495 → 535 |

## Ảnh
`img/*.jpg`: 5 ảnh tạo bằng AI trong Figma (file *AnNam Serif Showreel – Indochine images*, team Đìzai Studio Official): mặt tiền phố cổ, gạch bông, áo dài, hồ sen, nội thất. Ảnh minh hoạ, không phải ảnh chụp thật.

## Nhạc
Tự soạn bằng code (`music.py`), không dùng sample: tiếng gảy kiểu đàn tranh theo thang ngũ cung, mõ gỗ, kick/hi-hat tối giản, tiếng cồng ở end card. Ở cảnh ba thanh kéo, mỗi lần kéo là một tiếng nhấn luyến theo đúng thanh kéo (weight lên, slant xuống, x-height lên một quãng bốn).

## Dựng lại
```bash
python3 -m http.server 8765        # chạy ở gốc repo
node showreel/render.js /tmp/frames 30
python3 showreel/music.py /tmp/music.wav
ffmpeg -framerate 30 -i /tmp/frames/f%04d.png -i /tmp/music.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest showreel/AnNamSerif-Showreel.mp4
```
Xem trực tiếp: `http://localhost:8765/showreel/showreel.html?play`. Mọi chuyển động nằm trong hàm `render(t)` của `showreel.html`.
