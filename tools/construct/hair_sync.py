#!/usr/bin/env python3
"""S49 đồng bộ nét mảnh AnNam Serif (designer 20/11: "đồng bộ nét mảnh cho cả Serif" — cả chữ hoa, cả b d p q a: "đồng bộ tất cả").
    python3 tools/construct/hair_sync.py      (sau build.py, trước spacing.py) → ghi lại out/construct/outlines.json

Chuẩn: nét mảnh 42 (Regular) / 62 (Bold) cho mọi chữ có nét mảnh; Medium / SemiBold = nội suy đúng (1/3, 2/3).
Dùng lại luật của An Nam Golden (golden/golden.py), đo bằng trục giữa (stroke_balance.measure):
  - vòm n m h u: lòng vòm / lòng đáy u dịch nguyên khối tới đỉnh vòm = chuẩn (giữ dáng cung);
  - vòng o O ơ Ơ Q: lòng giãn / co theo trục dài của chính nó (Q: vùng đuôi giữ);
  - nét mảnh cong còn lại (b d p q a g c C G B D P R U J …): G10 kéo dãn chuỗi cung lõm của mép lòng theo chiều đứng (affine);
  - s S: lòng trên / dưới kéo dãn đứng affine; e: lòng mắt kéo đứng tới đỉnh cung = chuẩn;
  - chữ khác: nét mảnh (≤ 1.4 × chuẩn) nhân hệ số r = chuẩn / đo (mép lòng của cung, hai mép đoạn thẳng), tổng r trong 0.7–1.3.
Chữ có dấu dùng hệ số của chữ gốc. Bỏ qua chữ không có nét mảnh (i j l f r t I T).
"""
import json, os, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, 'golden')]
import golden as GD
OUT = os.path.join(HERE, '..', '..', 'out', 'construct')
T = {'Regular': 42.0, 'Bold': 62.0}
XTOP = 503.4

def main():
    GD.RING_T.update(T); GD.ARCH_T.update(T)
    O = json.load(open(os.path.join(OUT, 'outlines.json'))); SRC = dict(O); SP = json.load(open(os.path.join(OUT, 'spacing.json')))
    chars = [c for c in SP['Regular'] if f'{c}-Regular' in O]
    low = set(GD.lower_set(chars)); K = {}
    order = sorted(chars, key=lambda c: (unicodedata.normalize('NFD', c) != c or len(c) > 1 or not c.isascii(), c))   # chữ gốc trước
    for c in order:
        b = unicodedata.normalize('NFD', c)[0]
        if not b.isalpha() or not b.isascii() or b in GD.NOHAIR: continue
        for w in ('Regular', 'Bold'):
            d = O[f'{c}-{w}']
            if b in GD.ARCH:
                cs = GD.parse(d); GD.arch_thin(cs, w); d = GD.fmt(cs)
            if b in GD.RING:
                tl = b == 'Q'
                if (b, w, 'k') not in K: K[(b, w, 'k')] = GD.solve_ring(d, d, w, tl)
                d = GD.ring_scale(d, K[(b, w, 'k')], tl)
            elif b in GD.EFAM:
                d = GD.e_top(d, T[w])
            elif b in GD.SFAM:
                d = GD.s_thin(d, w)
            elif b not in GD.ARCH:
                if c == b and b not in GD.G10_SKIP: d = GD.g10(d, w)          # G10 nét mảnh cong: kéo dãn lòng theo chiều đứng
                if c == b: d, K[(b, w, 'r')] = GD.g8_solve(d, c, w, low, XTOP)
                elif abs(K.get((b, w, 'r'), 1.0) - 1) > 0.01: d = GD.g8_apply(d, c, w, K[(b, w, 'r')], low, XTOP)
            O[f'{c}-{w}'] = d
        for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    for c in order:                                               # thân chữ có dấu = chữ gốc đã đồng bộ (không lệch như ệ)
        b = unicodedata.normalize('NFD', c)[0]
        if c == b or f'{b}-Regular' not in O: continue
        for w in ('Regular', 'Bold'):
            O[f'{c}-{w}'] = (GD.compose(O[f'{b}-{w}'], O[f'{c}-{w}']) if GD.composable(c)          # chữ có dấu = chữ gốc + dấu
                             else GD.rebase(SRC[f'{c}-{w}'], SRC[f'{b}-{w}'], O[f'{b}-{w}'], O[f'{c}-{w}']))
        for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    json.dump(O, open(os.path.join(OUT, 'outlines.json'), 'w'))
    print('hair_sync:', ' '.join(f'{b}{w[0]}{k}{v:.2f}' for (b, w, k), v in sorted(K.items()) if abs(v - 1) > 0.02))

if __name__ == '__main__':
    main()
