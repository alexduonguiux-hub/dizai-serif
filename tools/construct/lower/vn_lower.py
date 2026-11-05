#!/usr/bin/env python3
"""Dấu tiếng Việt cho chữ thường (67 chữ + đ + ₫), Regular + Bold — TẠM, dựng theo luật S11 như chữ hoa.
    python3 tools/construct/lower/vn_lower.py   → lower/lower_vn.json (make_ref.py gộp vào ref_glyphs.json)

- Dấu: CÙNG bộ dấu của chữ hoa (vn_punct.marks: sắc/huyền gương, mũ, trăng lưỡi liềm, ngã, hỏi, nặng, sừng) — cùng nét bút.
- Đáy dấu thấp nhất: MARK_YL = x-height 495 + vượt 8.4 + khe 36 + 3 = 542.4 (cách tính như chữ hoa: 700 + 11.3 + 36 + 3).
- Tâm ngang dấu: tâm hộp mực PHẦN x-height của chữ (y, ư, ơ: bỏ đuôi / sừng).
- Mũ + sắc/huyền/hỏi: dấu thanh bên phải mũ (place_right); mọi dấu khác chồng lên, khe ≥ 30.
- i có dấu trên: i không chấm (ị giữ chấm). Nặng: dưới đáy thật, khe 36 (ỵ: dưới đỉnh nhọn, dời trái tới khi cách đuôi 36).
- Sừng ơ: bám vai vòng o ở góc 48° (Ơ hoa 38°: vòng thường nhỏ, sừng 38° chỉ nhô 33 u khỏi x-height, ơ đọc thành σ); ư: mép ngoài thân phải ở CÙNG cao độ, sừng thay loe ngoài đỉnh thân phải (như Ư).
- đ: thanh ngang H cắt qua thân d ở 600 (giữa x-height và đỉnh thân), vươn ra ngoài thân 0.62 V, vào trong 0.9 V (như Đ).
- ₫: đ + gạch dưới dày H ở −160.
"""
import sys, os, json, math, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'ref'))
import vn_punct as V
from make_ref import outline

XH, OVT = 495.0, 8.4
MARK_YL = XH + OVT + V.GAP_ML + 3
HORN_A = 48.0          # góc bám sừng trên vòng o (Ơ hoa 38°): vòng thường nhỏ, bám cao hơn để đầu sừng vươn rõ khỏi x-height (≈ +70)
LV = {'Regular': dict(V=36*700/247.5, H=39.6), 'Bold': dict(V=44*700/247.5, H=52.3)}
VN_LOWER = 'àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ'
MODS = {'̆': 'breve', '̂': 'circumflex', '̛': 'horn'}
TONE = {'́': 'acute', '̀': 'grave', '̉': 'hook', '̃': 'tilde', '̣': 'dotbelow'}

def load():
    S = {}
    for f in ('lower.json', 'lower_derived.json'): S.update(json.load(open(os.path.join(HERE, f))))
    return S

def xpart(p):
    """phần x-height (0 … 520) để lấy tâm dấu"""
    return V.I(p, V.rect(-50, -5, 2000, XH + 25))
def cxof(p): b = V.bounds(xpart(p)); return (b[0] + b[2])/2

def horn_anchor(ch, base, ref_o):
    if ch == 'u':
        x0, y0, x1, y1 = V.bounds(ref_o); y = (y0 + y1)/2 + (y1 - y0)/2*math.sin(math.radians(HORN_A))
        s = V.I(base, V.rect(-50, y - 0.05, 2000, y + 0.05)); return (V.bounds(s)[2], y)
    x0, y0, x1, y1 = V.bounds(base); a = math.radians(HORN_A)
    return ((x0 + x1)/2 + (x1 - x0)/2*math.cos(a), (y0 + y1)/2 + (y1 - y0)/2*math.sin(a))

def place_clear(obstacles, q, step=2):
    """đẩy dấu q lên tới khi cách mọi vật cản ≥ 30"""
    while any(V.gap(o, q) < V.GAP_MM + 2 for o in obstacles): q = V.move(q, 0, step)
    return q

def compose(S, M, ch, w):
    nfd = unicodedata.normalize('NFD', ch); b = nfd[0]; mod = next((MODS[c] for c in nfd[1:] if c in MODS), None)
    tone = next((TONE[c] for c in nfd[1:] if c in TONE), None)
    base = outline(S[f'{b}-{w}']); o_ref = outline(S[f'o-{w}'])
    if b == 'i' and tone != 'dotbelow': base = V.I(base, V.halfplane(XH + 20, above=False))   # i không chấm
    cx = cxof(base); parts = [base]; above = []; horn = None
    if mod == 'horn':
        ax, ay = horn_anchor(b, base, o_ref)
        if b == 'u': parts[0] = V.D(base, V.rect(ax, ay, ax + 300, XH + 60))       # sừng thay loe ngoài đỉnh thân phải
        horn = V.move(M['horn'], ax, ay); parts.append(horn)
    elif mod:
        above.append(V.move(M[mod], cx, MARK_YL))
    if tone and tone != 'dotbelow':
        m = M[tone]
        if mod == 'circumflex' and tone in ('acute', 'grave', 'hook'): q = V.place_right(above[0], m, w)
        elif above: q = V.place_above(above[-1], m, cx)
        else: q = V.move(m, cx, MARK_YL)
        if horn is not None: q = place_clear([horn], q)
        above.append(q)
    if tone == 'dotbelow':
        d = M['dotbelow']; db = V.bounds(d)
        q = V.move(d, cx, min(-11.3, V.bounds(V.I(base, V.halfplane(-60)))[1]) - V.GAP_ML - (db[3] - db[1]) - 2)
        while V.gap(base, q) < V.GAP_ML + 2: q = V.move(q, -2, 0)                     # ỵ: tránh đuôi
        parts.append(q)
    return V.U(*parts, *above)

def dstroke(S, w):
    base = outline(S[f'd-{w}']); y = 600.0
    s = V.I(base, V.rect(-50, y - 0.05, 2000, y + 0.05)); x0, x1 = V.bounds(s)[0], V.bounds(s)[2]
    v, H = LV[w]['V'], LV[w]['H']
    return V.U(base, V.rect(x0 - 0.9*v, y - H/2, x1 + 0.62*v, y + H/2))

def build():
    S = load(); out = {}; Wover = {}
    for w in ('Regular', 'Bold'):
        M = V.marks(w)
        for ch in VN_LOWER:
            if ch == 'đ': p = dstroke(S, w)
            else: p = compose(S, M, ch, w)
            b = 'd' if ch == 'đ' else unicodedata.normalize('NFD', ch)[0]; bb = V.bounds(outline(S[f'{b}-{w}']))
            out[f'{ch}-{w}'] = [V.to_d(p)]; Wover[f'{ch}-{w}'] = round(bb[2])
        dd = dstroke(S, w); x0, _, x1, _ = V.bounds(dd); H = LV[w]['H']
        out[f'₫-{w}'] = [V.to_d(V.U(dd, V.rect(x0 + 20, -160, x1, -160 + H)))]
    out['_W'] = Wover
    json.dump(out, open(os.path.join(HERE, 'lower_vn.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print('ok', len(out) - 1)

if __name__ == '__main__':
    build()
