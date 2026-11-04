#!/usr/bin/env python3
"""Ghép glyphs.js + render_figma.js thành code chạy trong use_figma (đã rút gọn)."""
import re, sys
def mini(src):
    src = re.sub(r'^\s*//.*$', '', src, flags=re.M)          # dòng chú thích
    src = re.sub(r'\s+//[^\n\'"`]*$', '', src, flags=re.M)     # chú thích cuối dòng (không chứa dấu nháy)
    src = re.sub(r'^\s+', '', src, flags=re.M)
    src = re.sub(r'\n+', '\n', src)
    return src
g = open('glyphs.js').read().split("if (typeof module")[0]
r = open('render_figma.js').read()
head = sys.argv[1]
print(head + "\n" + mini(g) + "\n" + mini(r))
