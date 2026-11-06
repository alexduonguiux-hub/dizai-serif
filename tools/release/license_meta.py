"""Thông tin giấy phép trong font (name ID 13 mô tả giấy phép, 14 URL giấy phép).

Dùng chung cho export_font.py (mỗi lần build) và package_tiers.py / make_trial.py.
Khi website có tên miền: điền LICENSE_URL, chạy lại `python3 tools/release/license_meta.py` (ghi lại vào fonts/).
"""
import os, sys

LICENSE_URL = ''          # ví dụ 'https://annamserif.com/license' — để trống thì không ghi name ID 14
LICENSE_DESC = ('This font software is commercial. Use requires a license from Đìzai Studio '
                '(Web, App / Game or Logo / Brand). See the EULA included with the font.')
TRIAL_DESC = ('Trial version for personal, non-commercial testing only. '
              'Any commercial use requires a license from Đìzai Studio.')


def apply(t, desc=LICENSE_DESC, url=LICENSE_URL):
    """t: TTFont đã mở. Ghi name ID 13 (+14) cho Windows (3, 1, 0x409)."""
    nm = t['name']
    nm.removeNames(nameID=13); nm.removeNames(nameID=14)
    nm.setName(desc, 13, 3, 1, 0x409)
    if url: nm.setName(url, 14, 3, 1, 0x409)


if __name__ == '__main__':
    from fontTools.ttLib import TTFont
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'fonts')
    n = 0
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(('.ttf', '.otf', '.woff2')):
                p = os.path.join(dp, f); t = TTFont(p)
                if f.endswith('.woff2'): t.flavor = 'woff2'
                apply(t); t.save(p); n += 1
    print('ghi thông tin giấy phép vào', n, 'file')
