"""Bốn weight của Dìzai Serif (designer 05/11: "thêm 2 weight medium và semi bold" — tự sinh toàn bộ, bậc ĐỀU theo độ dày nét).
Regular / Bold là hai master (bản vẽ designer + luật); Medium = 1/3, SemiBold = 2/3 quãng Regular → Bold.
    - bản vẽ chữ hoa + số: nội suy điểm (ref/interp.py → designer_M.json)
    - dựng theo luật: mọi tham số số học nội suy bằng lerp_w(); phần "Bold thêm vào" (B_STEM, B_BAR…) nhân TW[w]
"""
WEIGHTS = ('Regular', 'Medium', 'SemiBold', 'Bold')
TW = {'Regular': 0.0, 'Medium': 1/3, 'SemiBold': 2/3, 'Bold': 1.0}
WCLASS = {'Regular': 400, 'Medium': 500, 'SemiBold': 600, 'Bold': 700}

def lerp(a, b, t):
    if isinstance(a, dict): return {k: lerp(a[k], b[k], t) for k in a}
    if isinstance(a, (tuple, list)): return type(a)(lerp(x, y, t) for x, y in zip(a, b))
    if isinstance(a, bool) or not isinstance(a, (int, float)): return a if t < 0.5 else b
    return a + (b - a)*t

def lerp_w(d):
    """bảng theo weight {'Regular': x, 'Bold': y} → thêm Medium / SemiBold (nội suy, kể cả dict / tuple lồng nhau); trả về chính d"""
    for w in WEIGHTS:
        if w not in d: d[w] = lerp(d['Regular'], d['Bold'], TW[w])
    return d

def at(a, b, w):
    """giá trị tại weight w giữa a (Regular) và b (Bold)"""
    return lerp(a, b, TW[w])
