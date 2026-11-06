AnNam — Version 0.900 (06/11/2026)
Thiết kế: Dizai Studio

Bộ chữ glyphic loe nét, tương phản theo bút dẹt, đủ tiếng Việt (134 chữ có dấu, ghép dấu NFD).
4 độ đậm: Regular 400 · Medium 500 · SemiBold 600 · Bold 700, mỗi độ đậm có Roman và Italic (nghiêng 10°).

THƯ MỤC
  variable/
    AnNam[wght].ttf           Roman, trục độ đậm wght 400–700
    AnNam-Italic[wght].ttf    Italic, trục độ đậm wght 400–700
    AnNam[slnt,wght].ttf      Gộp Roman + Italic: wght 400–700 + nghiêng slnt 0 … −10°
  otf/   8 bản tĩnh OpenType (CFF): AnNam-Regular … AnNam-BoldItalic
  ttf/   8 bản tĩnh TrueType:       AnNam-Regular … AnNam-BoldItalic
  woff2/ bản web (nén Brotli, nhẹ hơn TTF ~4 lần)
    variable/  AnNam[wght].woff2 · AnNam-Italic[wght].woff2 · AnNam[slnt,wght].woff2
    ttf/       8 bản tĩnh AnNam-Regular.woff2 … AnNam-BoldItalic.woff2

NÊN CÀI BẢN NÀO
  • Thiết kế in ấn, Adobe, Figma, Office: cài 8 file otf/ (hoặc ttf/). Không cài cùng lúc otf/ và ttf/ trên một máy.
  • Web và ứng dụng hỗ trợ variable: dùng variable/. Cần nút in nghiêng (I) hoạt động trong Word / Office thì cài
    cả AnNam[wght].ttf và AnNam-Italic[wght].ttf; file gộp [slnt,wght] dành cho web / Figma / ứng dụng hỗ trợ trục nghiêng.

Web (CSS) — dùng woff2:
  /* variable: 2 file cho mọi độ đậm 400–700, nút in nghiêng hoạt động đúng */
  @font-face { font-family: "AnNam"; src: url("AnNam[wght].woff2") format("woff2"); font-weight: 400 700; font-style: normal; font-display: swap; }
  @font-face { font-family: "AnNam"; src: url("AnNam-Italic[wght].woff2") format("woff2"); font-weight: 400 700; font-style: italic; font-display: swap; }
  body { font-family: "AnNam", serif; }   /* font-weight: 400 … 700 tuỳ ý, ví dụ 450 */

  /* hoặc một file gộp: nghiêng tuỳ ý 0 … −10° */
  @font-face { font-family: "AnNam"; src: url("AnNam[slnt,wght].woff2") format("woff2"); font-weight: 400 700; font-style: oblique 0deg 10deg; }

  /* hoặc bản tĩnh (trình duyệt cũ): mỗi kiểu một @font-face, ví dụ */
  @font-face { font-family: "AnNam"; src: url("AnNam-Regular.woff2") format("woff2"); font-weight: 400; font-style: normal; }
  @font-face { font-family: "AnNam"; src: url("AnNam-BoldItalic.woff2") format("woff2"); font-weight: 700; font-style: italic; }
