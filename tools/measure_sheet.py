#!/usr/bin/env python3
"""Đo ảnh bảng chữ (specimen sheet) của Dizai Serif.

Chỉ dùng để chẩn đoán từ ảnh khi chưa có file nguồn (.glyphs / .ufo / Figma).
Mọi số đo quy về đơn vị font với cap height = 700 (UPM 1000).
Độ chính xác: ±1 px ảnh ≈ ±3 u. Số đo ngang trên nét chéo / nét tròn là
bề ngang cắt ngang, KHÔNG phải độ dày vuông góc nét.

Cách dùng:
    python3 tools/measure_sheet.py reference/regular/caps-A-K.webp \
        --cap-top 126 --baseline 362 --names "A B C D E F G H I J K"

    # Profile loe chân của một thân (cột x0..x1 tính bằng px ảnh):
    python3 tools/measure_sheet.py reference/regular/caps-A-K.webp \
        --cap-top 126 --baseline 362 --profile 1595 1643
"""
import argparse

import numpy as np
from PIL import Image


def load_ink(path):
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    return (r < 110) & (g < 110) & (b < 110)


def runs(line):
    out, s = [], None
    for i, v in enumerate(line):
        if v and s is None:
            s = i
        if not v and s is not None:
            out.append((s, i - s))
            s = None
    if s is not None:
        out.append((s, len(line) - s))
    return out


def glyph_columns(ink):
    return runs(ink.any(0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--cap-top", type=int, required=True, help="y px của cap line (nét thẳng)")
    ap.add_argument("--baseline", type=int, required=True, help="y px của baseline")
    ap.add_argument("--names", default="", help="tên glyph theo thứ tự trái → phải")
    ap.add_argument("--profile", nargs=2, type=int, metavar=("X0", "X1"))
    a = ap.parse_args()

    ink = load_ink(a.image)
    k = 700 / (a.baseline - a.cap_top)
    print(f"scale {k:.3f} u/px")

    if a.profile:
        x0, x1 = a.profile
        for u in [0, 5, 10, 20, 30, 40, 60, 80, 100, 200, 350, 500, 600, 640, 660, 680, 690, 695, 700]:
            y = int(round(a.baseline - u / k))
            xs = np.where(ink[y, x0:x1 + 1])[0]
            if len(xs):
                print(f"  h={u:3d}  L={xs[0]*k:5.0f}  R={xs[-1]*k:5.0f}  w={(xs[-1]-xs[0]+1)*k:4.0f}")
        return

    names = a.names.split()
    cols = glyph_columns(ink)
    gaps = [cols[i + 1][0] - (cols[i][0] + cols[i][1]) for i in range(len(cols) - 1)]
    for i, (x0, w) in enumerate(cols):
        g = ink[:, x0:x0 + w]
        ys = np.where(g.any(1))[0]
        name = names[i] if i < len(names) else f"#{i}"
        print(f"{name:>3} ink_w={w*k:4.0f} top={(a.baseline-ys.min())*k:4.0f} "
              f"bottom={(ys.max()-a.baseline)*k:4.0f}"
              + (f"  gap→next={gaps[i]*k:4.0f}" if i < len(gaps) else ""))
        for frac in (0.25, 0.5, 0.75):
            y = int(a.baseline - (a.baseline - a.cap_top) * frac)
            print(f"      ngang @{int(frac*100)}%: " + ", ".join(
                f"x{round(s*k)} w{round(n*k)}" for s, n in runs(g[y])))
        for fx in (0.3, 0.5, 0.7):
            x = int(w * fx)
            print(f"      dọc  @{int(fx*100)}%: " + ", ".join(
                f"y{round((a.baseline-s)*k)-round(n*k)} h{round(n*k)}" for s, n in runs(g[:, x])))


if __name__ == "__main__":
    main()
