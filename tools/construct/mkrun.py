#!/usr/bin/env python3
"""Ghép glyphs.js + render_figma.js thành code chạy trong use_figma (đã rút gọn)."""
import re, sys
def mini(src):
    src = re.sub(r'^\s*//.*$', '', src, flags=re.M)          # dòng chú thích
    src = re.sub(r'\s+//[^\n\'"`]*$', '', src, flags=re.M)     # chú thích cuối dòng (không chứa dấu nháy)
    src = re.sub(r'^\s+', '', src, flags=re.M)
    src = re.sub(r'\n+', '\n', src)
    return src
if __name__ == "__main__":
  g = open('glyphs.js').read().split("if (typeof module")[0]
  r = open('render_figma.js').read()
  import json
  head = sys.argv[1]
  # chỉ nhúng REF của các glyph có trong JOBS (giới hạn kích thước mã)
  ref = json.load(open('ref_glyphs.json'))
  jobs = re.search(r"JOBS\s*=\s*(\[.*\])", head).group(1)
  need = {f"{ch}-{w}" for w, _, chars in json.loads(jobs.replace("'", '"')) for ch in chars}
  sub = {k: v for k, v in ref.items() if k in need}
  print(head + "\nconst REF_DATA=" + json.dumps(sub, separators=(",", ":")) + ";\n" + mini(g) + "\n" + mini(r))
