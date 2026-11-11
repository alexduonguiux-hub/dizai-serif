# Thương mại hoá AnNam Serif — bộ tài liệu bán hàng

Trạng thái: bản nháp v1 (06/11/2026). Các con số giá là **đề xuất**, designer quyết định.

## 1. Gói giấy phép và biến thể (variant)

Bốn gói: **Desktop · Web · App / Game · Logo / Thương hiệu**.
- **Desktop** (EULA 3.4): cài theo số máy; dùng cho in ấn, bao bì, tài liệu, hình ảnh, mạng xã hội, video, nhúng PDF. Không gồm logo, website, app.
- Web, App / Game và Logo vẫn kèm quyền **cài trên 2 máy**, nhưng chỉ để làm ra đúng sản phẩm của gói đó (EULA mục 2). Nhờ vậy người chỉ mua Logo không phải mua thêm Desktop để vẽ logo.
- Muốn bắt buộc khách mua Desktop kèm theo: bỏ câu "2 Máy trạm" ở mục 2 của EULA.

| Gói | Biến thể | Giới hạn | USD | VND (tham khảo) |
|---|---|---|---|---|
| Desktop | 1–2 máy | | 45 | 1.090.000 |
| Desktop | 3–5 máy | | 90 | 2.190.000 |
| Desktop | 6–10 máy | (hơn 10 máy: liên hệ) | 160 | 3.890.000 |
| Web | Small | ≤ 50.000 lượt xem trang / tháng | 40 | 990.000 |
| Web | Medium | ≤ 250.000 | 90 | 2.290.000 |
| Web | Large | ≤ 1.000.000 | 180 | 4.590.000 |
| App / Game | Indie | doanh thu + vốn < 100.000 USD / 12 tháng, 1 tựa | 150 | 3.790.000 |
| App / Game | Studio | không giới hạn doanh thu, 1 tựa | 450 | 11.490.000 |
| Logo / Thương hiệu | Doanh nghiệp nhỏ | < 25 nhân sự, 1 logo | 200 | 4.990.000 |
| Logo / Thương hiệu | Doanh nghiệp lớn | không giới hạn, 1 logo | 600 | 14.990.000 |

Giá đặt theo mặt bằng font indie một họ 8 kiểu có variable. Giá VND làm tròn kiểu "…90.000", không quy đổi đúng tỷ giá.

## 2. Hai loại tiền USD + VND trên Lemon Squeezy

- Một store Lemon Squeezy chỉ có **một loại tiền hiển thị**, chọn trong Settings. Store không tự đổi tiền theo quốc gia khách. Thanh toán được xử lý bằng USD.
- VND có trong danh sách tiền tệ hỗ trợ, và Việt Nam nhận payout qua ngân hàng. Kiểm tra lại trong Settings › Payouts khi mở store.

Đề xuất:
1. Đặt tiền của store là **USD**. Đây là đúng số khách quốc tế trả.
2. Trang tiếng Việt hiển thị giá VND ở bảng trên. Nút mua vẫn dẫn tới checkout USD, kèm dòng: "Thanh toán bằng thẻ quốc tế, quy đổi theo tỷ giá ngân hàng."
3. Muốn khách Việt trả đúng số VND (chuyển khoản / VietQR): tạo mã giảm giá hoặc bán tay ngoài Lemon Squeezy, rồi gửi file + EULA qua email.
   Cách thứ hai là mở store thứ hai bằng VND. Mỗi store cần cấu hình riêng.

## 3. Cài sản phẩm trên Lemon Squeezy (checklist)

1. **Store**: tên Đìzai Studio, tiền USD, payout ngân hàng Việt Nam. Thêm logo, email hỗ trợ, link EULA.
2. Tạo **4 product** (hoặc 1 product nhiều variant):

   | Product | File đính kèm (dist/commercial/) | Variant |
   |---|---|---|
   | AnNam Serif — Desktop License | AnNamSerif-Desktop-v0.910.zip | 1–2 / 3–5 / 6–10 máy |
   | AnNam Serif — Web License | AnNamSerif-Web-v0.910.zip | Small / Medium / Large |
   | AnNam Serif — App / Game License | AnNamSerif-AppGame-v0.910.zip | Indie / Studio |
   | AnNam Serif — Logo / Brand License | AnNamSerif-LogoBrand-v0.910.zip | Small Business / Enterprise |
   | (tuỳ chọn) AnNam Serif — Complete | AnNamSerif-Complete-v0.910.zip | gộp 4 gói (biến thể nhỏ nhất), giảm ~20 % |

   Nếu file chỉ gắn được ở cấp product, mọi variant cùng nhận một zip. Gói zip đã làm như vậy.
3. Mô tả product: dán phần "Giới hạn" của biến thể và link EULA (EN/VI).
4. **Checkout**: bật trường "Company / licensee name" (custom field), vì EULA ghi giấy phép theo tên trên đơn. Bật hoá đơn (invoice) cho doanh nghiệp.
5. **Email sau mua** (receipt): thêm link EULA, hướng dẫn cài, email liên hệ nâng cấp.
6. **Thuế**: Lemon Squeezy là merchant of record, tự thu VAT/GST quốc tế. Thuế thu nhập tại Việt Nam vẫn cần hỏi kế toán.
7. Gắn nút mua trên website: dùng **Checkout overlay** (lemon.js) hoặc link checkout của từng variant. Không cần backend.
8. Mua thử ở **test mode** trước khi bật live. Kiểm tra zip tải về có đủ 19–30 file và EULA.

## 4. Bản dùng thử (Trial)

`dist/AnNamSerif-Trial-v0.910.zip` (40 KB): Regular, Bold, Italic; chỉ Latin cơ bản (96 ký tự, **không có tiếng Việt**).
- Tên họ "AnNam Serif Trial", PS `AnNamSerifTrial-*`, nên không đụng bản thương mại khi cài cùng máy.
- fsType 2 (không cho nhúng vào PDF/ứng dụng).
- Kèm EULA-Trial (song ngữ).
- Trên Lemon Squeezy có thể tạo product giá 0 USD để thu email người tải.

## 5. Thông tin giấy phép trong font

Mọi file trong `fonts/` có **name ID 13** (mô tả giấy phép thương mại). Khi có tên miền:
1. Điền `LICENSE_URL` trong `tools/release/license_meta.py` (vd. `https://<tên-miền>/license`).
2. Chạy:
   ```bash
   python3 tools/release/license_meta.py
   ```
3. Chạy:
   ```bash
   python3 tools/release/package_tiers.py
   ```
4. Chạy:
   ```bash
   python3 tools/release/make_trial.py
   ```

`export_font.py` cũng tự ghi name ID 13/14 mỗi lần build.

## 6. Nội dung cho website (designer tự thiết kế)

**Tagline**
- EN: A glyphic, flared serif with broad-nib contrast — built for Vietnamese.
- VI: Serif khắc loe nét, tương phản ngòi dẹt — dựng cho tiếng Việt.

**Thông số**
- 8 kiểu: Regular, Medium, SemiBold, Bold × Roman / Italic (nghiêng 10°).
- 3 file variable: wght 400–700, slnt 0 → −10°.
- 134 chữ Việt dựng sẵn; gõ tổ hợp (NFD/VNI) tự ghép.
- Kerning theo âm tiết tiếng Việt.
- Định dạng: OTF, TTF, WOFF2. Vendor DZAI.

**Câu mẫu (specimen)**
- VI: "Trăm năm trong cõi người ta, chữ tài chữ mệnh khéo là ghét nhau." · "Sài Gòn — Hà Nội — Huế — Hội An" · "Ẩm thực đường phố, phở bò, bún chả, cà phê sữa đá"
- EN: "The quick brown fox jumps over the lazy dog" · "Glyphic letters cut with a broad nib"
- Pangram tiếng Việt: "Tôi yêu tiếng nước tôi từ khi mới ra đời, người ơi."

**Font cho chính website**: dùng `fonts/woff2/variable/AnNamSerif[slnt,wght].woff2` với CSS trong `dist/README-AnNamSerif.txt`. Website của chính Đìzai Studio không cần mua giấy phép.

**Trang nên có**
- Specimen: chữ lớn, thanh trượt wght/slnt, ô gõ thử.
- Bảng glyph.
- Giấy phép: so sánh 4 gói + FAQ.
- Bảng giá với nút mua Lemon Squeezy.
- Tải bản Trial.
- EULA EN/VI.
- Liên hệ.

**FAQ gợi ý**
- "Tôi thiết kế logo cho khách thì mua gói nào?" → Logo / Thương hiệu, đứng tên khách.
- "Làm poster, bao bì, bài đăng mạng xã hội?" → Desktop.
- "Agency 8 người cùng dùng?" → Desktop 6–10 máy.
- "Website và app cùng dùng?" → mua cả Web và App / Game, hoặc gói Complete.
- "Vượt lượt xem?" → nâng cấp, trả phần chênh lệch.

## 7. Trước khi bán

- [ ] Nhờ luật sư rà EULA (EN + VI). File hiện là bản nháp.
- [ ] Đăng ký vendor ID DZAI với Microsoft (email đã soạn).
- [ ] Cân nhắc đăng ký nhãn hiệu "AnNam Serif" / "Đìzai" tại Cục Sở hữu trí tuệ.
- [ ] Điền LICENSE_URL khi có tên miền rồi đóng gói lại.
- [ ] Nâng version lên 1.000 khi phát hành chính thức (VERSION trong export_font.py).
