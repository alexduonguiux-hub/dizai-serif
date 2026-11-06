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

NÊN CÀI BẢN NÀO
  • Thiết kế in ấn, Adobe, Figma, Office: cài 8 file otf/ (hoặc ttf/). Không cài cùng lúc otf/ và ttf/ trên một máy.
  • Web và ứng dụng hỗ trợ variable: dùng variable/. Cần nút in nghiêng (I) hoạt động trong Word / Office thì cài
    cả AnNam[wght].ttf và AnNam-Italic[wght].ttf; file gộp [slnt,wght] dành cho web / Figma / ứng dụng hỗ trợ trục nghiêng.

Web (CSS):
  @font-face { font-family: "AnNam"; src: url("AnNam[wght].ttf") format("truetype"); font-weight: 400 700; font-style: normal; }
  @font-face { font-family: "AnNam"; src: url("AnNam-Italic[wght].ttf") format("truetype"); font-weight: 400 700; font-style: italic; }
