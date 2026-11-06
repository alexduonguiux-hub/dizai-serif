#!/usr/bin/env python3
"""QA tiến triển weight (typeface-construction §13): mọi ký tự — diện tích mực R < M < SB < B (tăng thật), bề ngang mực và
advance không giảm; bước diện tích đều (bước giữa / bước đầu trong 0.6 … 1.6). In các ký tự vi phạm."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'ref'))
from weights import WEIGHTS
from make_ref import outline
import vn_punct as V
O = json.load(open(os.path.join(os.environ.get('DIZAI_OUT') or os.path.join(HERE, '..', '..', 'out', 'construct'), 'outlines.json')))
SP = json.load(open(os.path.join(os.environ.get('DIZAI_OUT') or os.path.join(HERE, '..', '..', 'out', 'construct'), 'spacing.json')))
def area(p):
    tot = 0; cur = []; pt = None
    for v, ps in p.segments:
        if v == 'moveTo': cur = [ps[0]]; pt = ps[0]
        elif v == 'lineTo': cur.append(ps[0]); pt = ps[0]
        elif v == 'curveTo': c = (pt, *ps); cur += [V.bez(c, k/12) for k in range(1, 13)]; pt = ps[2]
        elif v == 'closePath': tot += sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(cur, cur[1:] + cur[:1]))/2
    return abs(tot)
chars = sorted({k.rsplit('-', 1)[0] for k in O})
bad = []; uneven = []
for c in chars:
    if not all(f'{c}-{w}' in O for w in WEIGHTS): continue
    ps = [outline([O[f'{c}-{w}']]) for w in WEIGHTS]; A = [area(p) for p in ps]; Wd = [p.bounds[2] - p.bounds[0] for p in ps]
    adv = [SP[w].get(c, {}).get('adv', 0) for w in WEIGHTS]
    if not (all(A[i] < A[i + 1] for i in range(3)) and all(Wd[i] <= Wd[i + 1] + 0.5 for i in range(3)) and all(adv[i] <= adv[i + 1] for i in range(3))):
        bad.append((c, [round(a/1000, 1) for a in A], [round(x) for x in Wd], adv))
    st = [A[i + 1] - A[i] for i in range(3)]
    if st[0] > 0 and not all(0.6 <= s/st[0] <= 1.6 for s in st[1:]): uneven.append((c, [round(s/1000, 1) for s in st]))
print(f'{len(chars)} ký tự · không đơn điệu: {len(bad)}', bad[:30]); print(f'bước không đều: {len(uneven)}', uneven[:30])
