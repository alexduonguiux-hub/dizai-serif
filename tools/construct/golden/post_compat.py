"""Sau compat_masters (Golden): đoạn siêu ngắn (< 1 u) ở MỘT master (sừng Ơ ghép boolean: cung suy biến ở Regular) — export bỏ đoạn
suy biến riêng từng master → lệch số điểm, fontmake từ chối. Bỏ ở CẢ HAI master (drop_tiny), M / SB nội suy lại."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import golden as GD
OUT = os.environ.get('DIZAI_OUT', os.path.join(HERE, '..', '..', '..', 'out', 'golden'))
p = os.path.join(OUT, 'outlines.json'); O = json.load(open(p)); fixed = []
for k in [k for k in O if k.endswith('-Regular')]:
    c = k[:-8]
    if f'{c}-Bold' not in O: continue
    r, b, n = GD.drop_tiny(O[f'{c}-Regular'], O[f'{c}-Bold'], 1.0)
    if n:
        O[f'{c}-Regular'], O[f'{c}-Bold'] = r, b
        for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(r, b, t)
        fixed.append(c)
hn = []
for k in [k for k in O if k.endswith('-Regular')]:                   # chữ có sừng: Medium / SemiBold = nội suy đúng R / B
    c = k[:-8]
    if GD.no_horn(c) and f'{c}-Bold' in O and GD.horn_compat(O[k], O[f'{c}-Bold']):
        for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[k], O[f'{c}-Bold'], t)
        hn.append(c)
print('post_compat: chữ có sừng nội suy lại:', len(hn))
json.dump(O, open(p, 'w'))
print('post_compat: bỏ đoạn siêu ngắn ở cả hai master:', ''.join(fixed))
