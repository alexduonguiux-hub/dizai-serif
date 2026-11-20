"""Đóng gói AnNam Golden (bản duyệt, chưa có giấy phép thương mại riêng): mọi định dạng + README.
    python3 tools/release/package_golden.py   → dist/AnNamGolden-v<V>.zip"""
import os, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
FONTS = os.path.join(ROOT, 'fonts', 'golden'); V = '0.924'
DIRS = ['otf', 'ttf', 'variable', 'woff2/variable', 'woff2/ttf']
NOTE = ('AnNam Golden — review build. A separate commercial license for AnNam Golden is not yet published;\n'
        'please do not redistribute these files.\n\n')
if __name__ == '__main__':
    top = f'AnNamGolden-v{V}'; zp = os.path.join(ROOT, 'dist', top + '.zip'); n = 0
    readme = open(os.path.join(ROOT, 'dist', 'README-AnNamGolden.txt'), encoding='utf-8').read()
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for d in DIRS:
            src = os.path.join(FONTS, d)
            for f in sorted(os.listdir(src)):
                if os.path.isfile(os.path.join(src, f)): z.write(os.path.join(src, f), f'{top}/{d}/{f}'); n += 1
        z.writestr(f'{top}/README.txt', NOTE + readme)
    print(f'Golden {n} font {os.path.getsize(zp)//1024} KB → {os.path.relpath(zp, ROOT)}')
