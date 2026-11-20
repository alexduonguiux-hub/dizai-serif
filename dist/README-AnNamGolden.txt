AnNam Golden — Version 0.921 (20 November 2026)
Design: Đìzai Studio · Vendor ID: DZAI

A display companion to AnNam Serif: taller x-height (535), larger flares,
finer hairlines (32 / 44 units), wider v x y, and the same broad-nib contrast and full Vietnamese support
(all 134 precomposed Vietnamese letters; decomposed input — base letter + combining marks — is composed automatically).
4 weights: Regular 400 · Medium 500 · SemiBold 600 · Bold 700, each in Roman and Italic (10° slant).

CONTENTS
  variable/
    AnNamGolden[wght].ttf            Roman, weight axis wght 400–700
    AnNamGolden-Italic[wght].ttf     Italic, weight axis wght 400–700
    AnNamGolden[slnt,wght].ttf       Roman + Italic in one file: wght 400–700 + slant slnt 0 to −10°
  otf/    8 static OpenType (CFF) fonts: AnNamGolden-Regular … AnNamGolden-BoldItalic
  ttf/    8 static TrueType fonts:       AnNamGolden-Regular … AnNamGolden-BoldItalic
  woff2/  web fonts (Brotli-compressed, about 4× smaller than TTF)
    variable/  AnNamGolden[wght].woff2 · AnNamGolden-Italic[wght].woff2 · AnNamGolden[slnt,wght].woff2
    ttf/       8 static fonts AnNamGolden-Regular.woff2 … AnNamGolden-BoldItalic.woff2

WHICH FILES TO INSTALL
  • Print and desktop design (Adobe, Figma, Microsoft Office): install the 8 fonts in otf/ (or ttf/).
    Do not install otf/ and ttf/ on the same computer — they share names and will conflict.
  • Apps that support variable fonts: use variable/. Choose ONE option:
      – the pair AnNamGolden[wght].ttf + AnNamGolden-Italic[wght].ttf (needed for the Italic button in Word / Office), or
      – the single file AnNamGolden[slnt,wght].ttf (web, Figma and apps that support a slant axis).
    Installing both options shows "AnNam Golden Regular" twice in the Windows font menu.

WEB (CSS) — use the woff2 files
  /* Variable pair: any weight from 400 to 700, real italic */
  @font-face { font-family: "AnNam Golden"; src: url("AnNamGolden[wght].woff2") format("woff2");
               font-weight: 400 700; font-style: normal; font-display: swap; }
  @font-face { font-family: "AnNam Golden"; src: url("AnNamGolden-Italic[wght].woff2") format("woff2");
               font-weight: 400 700; font-style: italic; font-display: swap; }
  body { font-family: "AnNam Golden", serif; }   /* any font-weight from 400 to 700, e.g. 450 */

  /* Or the single combined file: any slant from 0 to 10° */
  @font-face { font-family: "AnNam Golden"; src: url("AnNamGolden[slnt,wght].woff2") format("woff2");
               font-weight: 400 700; font-style: oblique 0deg 10deg; }

  /* Or static fonts (older browsers): one @font-face per style, for example */
  @font-face { font-family: "AnNam Golden"; src: url("AnNamGolden-Regular.woff2") format("woff2"); font-weight: 400; font-style: normal; }
  @font-face { font-family: "AnNam Golden"; src: url("AnNamGolden-BoldItalic.woff2") format("woff2"); font-weight: 700; font-style: italic; }

LICENSE
  AnNam Golden is commercial software. Your rights depend on the license on your order
  (Desktop, Web, App / Game or Logo / Brand) — read EULA-en.txt (English) or EULA-vi.txt (Tiếng Việt).
  Desktop: install on the number of computers on your order. Web, App / Game and Logo / Brand
  include installing on up to 2 computers only to create the licensed work.

© 2026 Đìzai Studio
