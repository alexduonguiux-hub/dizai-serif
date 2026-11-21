# Showreel AnNam Serif (10 giây)

`AnNamSerif-Showreel.mp4`: 1920 × 1080, 30 fps, 10 giây, H.264 + AAC. Mood theo frame Home trong Figma *Đìzai Studio – Website – NEW* (`10:1457`): nền giấy, xanh emerald, chữ hoa lớn cắt sát cap, logo con dấu; thêm ảnh phong cách Indochine.

**Font:** AnNam Serif **v0.929**, file variable `AnNamSerif[XHGT,slnt,wght]` (wght 400–700 · slnt 0 → −10° · x-Height 495 → 535) + `AnNamSerif-Italic[XHGT,wght]`. Chữ ghép từng ký tự (AN NAM, tiếng việt…) đặt theo vị trí kerning thật của font, đo lại mỗi frame. Mọi chữ nằm trọn trong khung (không cắt trên dưới), không dùng chữ lật ngược.

## Kịch bản (120 BPM, mỗi chuyển cảnh rơi đúng phách)
| Thời gian | Cảnh · chuyển cảnh |
|---|---|
| 0–1 s | AN NAM ghép từng chữ (đúng kerning), đậm dần 400 → 700; chữ dần lấp đầy bằng ảnh |
| 1–1,5 s | **Ảnh nở ra từ khung chữ** thành toàn màn hình |
| 1,5–2 s | Ảnh thu vào khung bên phải; cột trái: “Phố cổ / *Hà Nội*” |
| 2–3 s | Ảnh mới đẩy lên trong khung; chữ đổi “Áo dài / *Sài Gòn*”, đoạn văn mẫu hiện theo dòng |
| 3–4 s | Khung ảnh mở lại toàn màn hình thành thẻ đầu; 8 thẻ dấu tiếng Việt **đẩy ngang** theo 1/16 nốt (ảnh / màu xen kẽ) |
| 4–6,4 s | Ba thanh kéo WEIGHT, SLANT, x-HEIGHT; chữ “tiếng việt” đổi theo, rồi cả ba cùng lùi về |
| 6,4–7,5 s | **Màn quét từ trái**: ảnh nội thất + danh sách kiểu chữ (mỗi dòng đặt bằng chính kiểu đó) |
| 7,3–8 s | Khung ảnh mở ra toàn màn hình, phủ màu emerald; chữ t lớn, x-height tăng, đúng phách đổi dạng ở 515 |
| 8–10 s | **End card trượt lên**: ảnh trong khung vòm, AN NAM / Serif / con dấu + số x-height chạy 495 → 535 |

Màu: emerald `#17503d` / `#6b9783` trên nền giấy `#f0efee`. Tên dùng duy nhất: AnNam Serif.

## Ảnh
`img/*.jpg` hiện là **ảnh tạm** (tạo bằng AI). Thay bằng ảnh chụp miễn phí (Unsplash / Pexels / Wikimedia Commons): chép đè file cùng tên, rồi chỉnh khung ảnh trong bảng `PH` đầu script `showreel.html` (`pos` = background-position). Ghi credit ảnh vào đây.

## Nhạc
Tự soạn bằng code (`music.py`), không dùng sample: jazz lounge kiểu Sài Gòn thập niên 30: piano hợp âm maj9 / m9, contrabass đi bè, trống chổi + ride; cảnh ba thanh kéo dùng tiếng đàn bầu luyến theo đúng từng lần kéo.

## Dựng lại
```bash
python3 -m http.server 8765        # chạy ở gốc repo
node showreel/render.js /tmp/frames 30
python3 showreel/music.py /tmp/music.wav
ffmpeg -framerate 30 -i /tmp/frames/f%04d.png -i /tmp/music.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest showreel/AnNamSerif-Showreel.mp4
```
Xem trực tiếp: `http://localhost:8765/showreel/showreel.html?play`. Mọi chuyển động nằm trong hàm `render(t)` của `showreel.html`.
