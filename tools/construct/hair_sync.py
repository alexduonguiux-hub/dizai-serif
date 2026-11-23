#!/usr/bin/env python3
"""S49 đồng bộ nét mảnh AnNam Serif (designer 20/11: "đồng bộ nét mảnh cho cả Serif" — cả chữ hoa, cả b d p q a: "đồng bộ tất cả").
    python3 tools/construct/hair_sync.py      (sau build.py, trước spacing.py) → ghi lại out/construct/outlines.json

Chuẩn: nét mảnh 42 (Regular) / 56.5 (Bold, = 42 × thân 140/104 — tương phản cố định như Golden) cho mọi chữ có nét mảnh; Medium / SemiBold = nội suy đúng (1/3, 2/3).
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
T = {'Regular': 42.0, 'Bold': 56.5}           # designer 20/11 "đồng bộ weight của serif giống golden": nét mảnh tăng theo tỉ lệ thân (42 × 140/104) — tương phản 0.40 cố định
XTOP = 503.4

def main():
    GD.RING_T.update(T); GD.ARCH_T.update(T); GD.BAR_K = 1.0     # AnNam Serif: không hiệu chỉnh nét ngang (chỉ Golden)
    GD.ARM_D.update({'Regular': 94.0, 'Bold': 122.0})        # G13: tay loe đầu thanh = độ sâu bản vẽ gốc v0.918 (mọi tay bằng nhau)
    O = json.load(open(os.path.join(OUT, 'outlines.json'))); SRC = dict(O); SP = json.load(open(os.path.join(OUT, 'spacing.json')))
    chars = [c for c in SP['Regular'] if f'{c}-Regular' in O]
    for c in chars:                                               # mẩu nối < 3 u (nách K): bỏ trước mọi luật — không có tiếp tuyến
        O[f'{c}-Regular'], O[f'{c}-Bold'], _ = GD.drop_tiny(O[f'{c}-Regular'], O[f'{c}-Bold'], 3.0)
        for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    SRC = dict(O)
    low = set(GD.lower_set(chars)); K = {}
    order = sorted(chars, key=lambda c: (unicodedata.normalize('NFD', c) != c or len(c) > 1 or not c.isascii(), c))   # chữ gốc trước
    for c in order:
        b = unicodedata.normalize('NFD', c)[0]
        if b in GD.TBAR and c == b:                                 # G11 thanh T (mép dưới là cung loe chạy vào thân)
            for w in ('Regular', 'Bold'): O[f'{c}-{w}'] = GD.bar_thin(O[f'{c}-{w}'], w)[0]
            for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
        if not b.isalpha() or not b.isascii() or c != b: continue    # chữ có dấu: ghép lại từ chữ gốc ở vòng sau
        for w in ('Regular', 'Bold'):
            d = O[f'{c}-{w}']
            if b in GD.RING:
                tl = b == 'Q'
                if (b, w, 'k') not in K: K[(b, w, 'k')] = GD.solve_ring(d, d, w, tl)
                d = GD.ring_scale(d, K[(b, w, 'k')], tl)
            elif b in GD.EFAM: d = GD.e_top(d, T[w])
            elif b in GD.SFAM: d = GD.s_thin(d, w)
            if b not in GD.G10_SKIP: d = GD.g10(d, w)                    # G10 nét mảnh cong: kéo dãn lòng theo chiều đứng
            d, _ = GD.g8_solve(d, c, w, low, XTOP)                      # G8 tuyệt đối: đoạn thẳng nét mảnh = chuẩn (gồm thanh e f t)
            O[f'{c}-{w}'] = d
        for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    if 'l-Regular' in O and 't-Regular' in O:                     # G14 chân l = chân t (designer 21/11: "chân chữ l và t … như golden cho serif")
        for w in ('Regular', 'Bold'): O[f'l-{w}'] = GD.l_from_t(O[f'l-{w}'], O[f't-{w}'])
        for w, t in GD.TW.items(): O[f'l-{w}'] = GD.lerp_d(O['l-Regular'], O['l-Bold'], t)
    for c in order:                                               # G13 tay loe đầu thanh dài bằng nhau (E F L T Z Æ Œ)
        if c in GD.ARMD and f'{c}-Regular' in O:
            for w in ('Regular', 'Bold'): O[f'{c}-{w}'] = GD.arm_depth(O[f'{c}-{w}'], w)[0]
            for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    for c in order:                                               # S76 G16 mặt cắt đỉnh A mọi weight = APEX_W (designer 23/11)
        if c in GD.APEX_KEEP and f'{c}-Regular' in O:
            for w in ('Regular', 'Bold'): O[f'{c}-{w}'] = GD.apex_set(O[f'{c}-{w}'], GD.APEX_W)
            for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    for c in order:                                               # G20 nét mảnh bụng D P B R giữ mảnh như O (designer 23/11)
        if c in GD.STEMBOWL and f'{c}-Regular' in O:
            for w in ('Regular', 'Bold'): O[f'{c}-{w}'] = GD.stem_bowl(O[f'{c}-{w}'], T[w])[0]
            for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    for c in order:                                               # thân chữ có dấu = chữ gốc đã đồng bộ (không lệch như ệ)
        b = unicodedata.normalize('NFD', c)[0]
        if c == b or f'{b}-Regular' not in O: continue
        for w in ('Regular', 'Bold'):
            O[f'{c}-{w}'] = (GD.compose(O[f'{b}-{w}'], O[f'{c}-{w}']) if GD.composable(c)          # chữ có dấu = chữ gốc + dấu
                             else GD.rebase(SRC[f'{c}-{w}'], SRC[f'{b}-{w}'], O[f'{b}-{w}'], O[f'{c}-{w}']))
        for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    if 'B-Regular' in O:                                          # G18 eo B = chuẩn nét mảnh (designer 23/11)
        for w in ('Regular', 'Bold'): O[f'B-{w}'] = GD.b_waist(O[f'B-{w}'], T[w])
        for w, t in GD.TW.items(): O[f'B-{w}'] = GD.lerp_d(O['B-Regular'], O['B-Bold'], t)
        for c in order:                                           # chữ có dấu gốc B (nếu có): dựng lại theo B
            b = unicodedata.normalize('NFD', c)[0]
            if c != b and b == 'B' and f'{c}-Regular' in O and GD.composable(c):
                for w in ('Regular', 'Bold'): O[f'{c}-{w}'] = GD.compose(O[f'B-{w}'], O[f'{c}-{w}'])
                for w, t in GD.TW.items(): O[f'{c}-{w}'] = GD.lerp_d(O[f'{c}-Regular'], O[f'{c}-Bold'], t)
    nh = 0
    for c in order:                                               # G17 chữ có sừng = chữ không sừng đã đồng bộ + sừng (designer 23/11)
        b2 = GD.no_horn(c)
        if not b2 or f'{c}-Regular' not in O or f'{b2}-Regular' not in O: continue
        WS_ = [w for w in ('Regular', 'Medium', 'SemiBold', 'Bold') if f'{c}-{w}' in SRC and f'{b2}-{w}' in SRC]
        rr = {w: GD.horn_compose(SRC[f'{c}-{w}'], SRC[f'{b2}-{w}'], O[f'{b2}-{w}']) for w in WS_}   # từng weight; compat_masters ghép R / B
        if rr and all(rr.values()):
            for w in WS_: O[f'{c}-{w}'] = rr[w]
            nh += 1
    print('G17 chữ có sừng:', nh)
    json.dump(O, open(os.path.join(OUT, 'outlines.json'), 'w'))
    print('hair_sync:', ' '.join(f'{b}{w[0]}{k}{v:.2f}' for (b, w, k), v in sorted(K.items()) if abs(v - 1) > 0.02))

if __name__ == '__main__':
    main()
