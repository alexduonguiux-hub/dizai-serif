"""Đóng gói file tải về theo gói giấy phép (mỗi gói = 1 file đính kèm cho mọi biến thể trên Lemon Squeezy).

  Desktop     OTF + TTF tĩnh + TTF variable (cài máy: in ấn, tài liệu, hình ảnh, video)
  Web         woff2 (variable + tĩnh) + OTF để thiết kế trên 2 máy
  App / Game  TTF tĩnh + TTF variable + OTF
  Logo        OTF + TTF tĩnh + TTF variable (cài máy để thiết kế logo)
Mỗi gói kèm README, EULA tiếng Anh + tiếng Việt. Ra dist/commercial/.
"""
import os, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
FONTS = os.path.join(ROOT, 'fonts'); OUT = os.path.join(ROOT, 'dist', 'commercial'); C = os.path.join(ROOT, 'commercial')
V = '0.916'
TIERS = {
    'Desktop':  ['otf', 'ttf', 'variable'],
    'Web':      ['woff2/variable', 'woff2/ttf', 'otf'],
    'AppGame':  ['ttf', 'variable', 'otf'],
    'LogoBrand': ['otf', 'ttf', 'variable'],
    'Complete': ['variable', 'otf', 'ttf', 'woff2/variable', 'woff2/ttf'],   # gói trọn bộ (mua cả 4 giấy phép)
}
NOTE = {
    'Desktop': 'DESKTOP LICENSE — install otf/ (or ttf/, not both; variable/ for apps that support it) on the number of computers on your order.',
    'Web': 'WEB LICENSE — self-host the files in woff2/ (see CSS in README). The otf/ fonts are for designing the site on up to 2 computers.',
    'AppGame': 'APP / GAME LICENSE — embed the ttf/ or variable/ fonts in one app or game title. Do not ship them as loose installable files.',
    'LogoBrand': 'LOGO / BRAND LICENSE — install otf/ (or ttf/, not both) on up to 2 computers to create one logo or brand identity.',
    'Complete': 'COMPLETE PACKAGE — all formats. What you may do with them is set by the license tier(s) on your order (see EULA).',
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    readme = open(os.path.join(ROOT, 'dist', 'README-AnNamSerif.txt'), encoding='utf-8').read()
    for tier, dirs in TIERS.items():
        top = f'AnNamSerif-{tier}-v{V}'; zp = os.path.join(OUT, top + '.zip'); n = 0
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            for d in dirs:
                src = os.path.join(FONTS, d)
                for f in sorted(os.listdir(src)):
                    if os.path.isfile(os.path.join(src, f)):
                        z.write(os.path.join(src, f), f'{top}/{d}/{f}'); n += 1
            z.writestr(f'{top}/README.txt', NOTE[tier] + '\n\n' + readme)
            for e in ('EULA-en.txt', 'EULA-vi.txt'): z.write(os.path.join(C, e), f'{top}/{e}')
        print(f'{tier:10} {n:2d} font  {os.path.getsize(zp)//1024:5d} KB  → {os.path.relpath(zp, ROOT)}')
