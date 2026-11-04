// Đìzai Serif v0.3 — bộ hình học theo quy tắc (nguồn chính). Chạy được trong Figma và Node.
// Luật: docs/07-rule-book-v0.3-dung-theo-quy-tac.md. Đơn vị font, cap 700, y hướng lên.
// Part: {name, cmds, clip?, minus?, counter?, post?}
//   cmds/clip/minus: [['M',p],['L',p],['C',c1,c2,p],['Z']]
//   minus: trừ riêng khỏi part này (vòng = ngoài − lòng);  clip: giao với vùng;  counter: trừ khỏi cả glyph;
//   post: cộng sau khi trừ counter (ví dụ đuôi Q đi qua lòng).
const CAP = 700, OVS = 12;
// Đường viền giữ từ bản vẽ v0.2 cho các glyph có đường cong tự do (S, Q, 2, 3, 5, 6, 9): ref_glyphs.json (ref/make_ref.py)
const REF = typeof REF_DATA !== 'undefined' ? REF_DATA : (typeof require !== 'undefined' ? require('./ref_glyphs.json') : {});
let VOPT = null; // tuỳ chọn cho V con trong W
let NO_REF = false; // true: bỏ qua bản vẽ, dựng hoàn toàn theo luật (để so sánh)
const RULES = { Regular: { V: 102, Vr: 106, D: 100, t: 44, Hb: 40, Hf: 90 }, Bold: { V: 139, Vr: 146, D: 146, t: 74, Hb: 68, Hf: 120 } };
const WIDTH = {
  Regular: { A: 672, B: 473, C: 537, D: 558, E: 374, F: 374, G: 537, H: 499, I: 148, J: 303, K: 503, L: 408, M: 643, N: 499, O: 723, P: 473, Q: 757, R: 527, S: 394, T: 397, U: 499, V: 672, W: 780, X: 642, Y: 632, Z: 465,
    '0': 578, '1': 201, '2': 448, '3': 449, '4': 530, '5': 449, '6': 527, '7': 445, '8': 521, '9': 527 },
  Bold: { A: 695, B: 504, C: 574, D: 609, E: 422, F: 422, G: 574, H: 541, I: 185, J: 340, K: 560, L: 456, M: 649, N: 555, O: 723, P: 502, Q: 768, R: 584, S: 451, T: 445, U: 541, V: 695, W: 805, X: 665, Y: 655, Z: 513,
    '0': 608, '1': 238, '2': 485, '3': 479, '4': 567, '5': 479, '6': 557, '7': 475, '8': 551, '9': 557 } };
const FR = 112, FF = 23, BEAK = 54, APEX = 20, SLANT = 26 * Math.PI / 180, BAR_H = 0.53, BAR_A = 0.255, KAP = 0.5523, KIN = 0.60, DEG = Math.PI / 180;
const BOWL0 = { flat: 0.35, ky: KAP, kyIn: KIN }; let BOWL = BOWL0;
const BOWL_BPR = { flat: 0.49, ky: 0.70, kyIn: 0.84 }; // B1: đo từ B, P, R v0.2
const add = (a, b) => [a[0] + b[0], a[1] + b[1]], sub = (a, b) => [a[0] - b[0], a[1] - b[1]], mul = (a, k) => [a[0] * k, a[1] * k];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1], nrm = a => mul(a, 1 / Math.hypot(a[0], a[1])), perp = a => [-a[1], a[0]];
const xAt = (p, d, y) => p[0] + d[0] * (y - p[1]) / d[1];
const polyC = pts => [['M', pts[0]], ...pts.slice(1).map(p => ['L', p]), ['Z']];
const poly = (name, pts, o) => Object.assign({ name, cmds: polyC(pts) }, o || {});
const rectC = (x0, y0, x1, y1) => polyC([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]);
const rect = (name, x0, y0, x1, y1, o) => Object.assign({ name, cmds: rectC(x0, y0, x1, y1) }, o || {});
function arcCmds(c, r, a0, a1) {
  const n = Math.max(1, Math.ceil(Math.abs(a1 - a0) / (Math.PI / 2))), da = (a1 - a0) / n, out = [];
  for (let i = 0; i < n; i++) {
    const s = a0 + i * da, e = s + da, k = 4 / 3 * Math.tan(da / 4) * r;
    const p0 = [c[0] + r * Math.cos(s), c[1] + r * Math.sin(s)], p3 = [c[0] + r * Math.cos(e), c[1] + r * Math.sin(e)];
    out.push(['C', [p0[0] - k * Math.sin(s), p0[1] + k * Math.cos(s)], [p3[0] + k * Math.sin(e), p3[1] - k * Math.cos(e)], p3]);
  }
  return out;
}
function ellC(c, rx, ry, rot = 0, kappa = KAP) {
  const ca = Math.cos(rot), sa = Math.sin(rot), tf = (x, y) => [c[0] + x * ca - y * sa, c[1] + x * sa + y * ca], kx = kappa * rx, ky = kappa * ry;
  return [['M', tf(rx, 0)], ['C', tf(rx, ky), tf(kx, ry), tf(0, ry)], ['C', tf(-kx, ry), tf(-rx, ky), tf(-rx, 0)],
    ['C', tf(-rx, -ky), tf(-kx, -ry), tf(0, -ry)], ['C', tf(kx, -ry), tf(rx, -ky), tf(rx, 0)], ['Z']];
}
function halfRightC(cx, cy, rx, ry, kappa, ext, kappaY = kappa) {
  const kx = kappa * rx, ky = kappaY * ry;
  return [['M', [cx - ext, cy - ry]], ['L', [cx, cy - ry]], ['C', [cx + kx, cy - ry], [cx + rx, cy - ky], [cx + rx, cy]],
    ['C', [cx + rx, cy + ky], [cx + kx, cy + ry], [cx, cy + ry]], ['L', [cx - ext, cy + ry]], ['Z']];
}
// two parallel lines, one through P1, the other through P2, perpendicular distance w. sgn picks the rotation.
function band2(P1, P2, w, sgn = 1) {
  const v = sub(P2, P1), L = Math.hypot(v[0], v[1]), ang = Math.atan2(v[1], v[0]) + sgn * Math.asin(Math.min(1, w / L));
  return [Math.cos(ang), Math.sin(ang)];
}
const bandPts = (p, q, d, y0, y1) => [[xAt(p, d, y0), y0], [xAt(p, d, y1), y1], [xAt(q, d, y1), y1], [xAt(q, d, y0), y0]];
const halfPlane = (Pt, n) => { const t = perp(n); return polyC([add(Pt, mul(t, 3000)), add(add(Pt, mul(t, 3000)), mul(n, 3000)), add(add(Pt, mul(t, -3000)), mul(n, 3000)), add(Pt, mul(t, -3000))]); };
// tiếp điểm trên elip (trục ngang/dọc) của tiếp tuyến từ điểm ngoài Pe; pick chọn nghiệm
function tangentPt(Pe, c, rx, ry, pick) { const bx = (Pe[0] - c[0]) / rx, by = (Pe[1] - c[1]) / ry, L = Math.hypot(bx, by), a = Math.atan2(by, bx), b = Math.acos(1 / L);
  const s1 = [c[0] + rx * Math.cos(a + b), c[1] + ry * Math.sin(a + b)], s2 = [c[0] + rx * Math.cos(a - b), c[1] + ry * Math.sin(a - b)]; return pick(s1, s2) ? s1 : s2; }
const flipY = cmds => cmds.map(c => [c[0], ...c.slice(1).map(p => [p[0], CAP - p[1]])]);
const rot180 = (cmds, W) => cmds.map(c => [c[0], ...c.slice(1).map(p => [W - p[0], CAP - p[1]])]);

function makeGlyph(ch, W8) {
  // Hình gốc của designer là chuẩn: nếu có bản vẽ thì glyph = bản vẽ, guide = hình học nhận diện từ chính đường cong.
  // Chỉ những glyph chưa có bản vẽ (Bold U–Z, số Bold) mới dựng tạm theo luật bên dưới.
  const ref = REF[`${ch}-${W8}`];
  if (ref && !NO_REF) return { ch, W: ref.W, src: ref.src || 'designer', parts: [{ name: ref.src === 'rule' ? 'Hình dựng theo luật (vn_punct.py)' : 'Hình gốc (bản vẽ designer)', cmds: ref.cmds }], guides: ref.guides.map(g => Object.assign({}, g)) };
  const r = RULES[W8], W = WIDTH[W8][ch], parts = [], guides = [];
  const P = s => (parts.push(s), s);
  const G = (o) => guides.push(o);
  // L1 / L2 — one circle r tangent to the stroke edge through the tip
  function flare(name, Eg, u, n, Pt, rad = FR) {
    const w = sub(Pt, Eg), uw = dot(u, w), nw = dot(n, w), s = uw + Math.sqrt(Math.max(0, uw * uw - dot(w, w) + 2 * rad * nw));
    const T = add(Eg, mul(u, s)), C = add(T, mul(n, rad));
    const a0 = Math.atan2(Pt[1] - C[1], Pt[0] - C[0]); let d = Math.atan2(T[1] - C[1], T[0] - C[0]) - a0;
    while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI;
    P({ name, cmds: [['M', add(Eg, mul(nrm(sub(Eg, Pt)), 3))], ['L', Pt], ...arcCmds(C, rad, a0, a0 + d), ['L', add(T, mul(n, -3))], ['Z']] });
    G({ type: 'compass', c: C, r: rad, a0, a1: a0 + d, T, tip: Pt });
  }
  const edges = (p, q, d) => { G({ type: 'line', p, d }); G({ type: 'line', p: q, d }); };
  const stem = (x0, y0 = 0, y1 = CAP, name = 'Thân', w = r.V) => P(rect(name, x0, y0, x0 + w, y1));
  function stemFlares(x0, x1, y, L = true, R = true) {
    const u = y === 0 ? [0, 1] : [0, -1], tag = y === 0 ? 'chân' : 'đỉnh';
    if (L) flare(`Loe ${tag} trái`, [x0, y], u, [-1, 0], [x0 - FF, y]);
    if (R) flare(`Loe ${tag} phải`, [x1, y], u, [1, 0], [x1 + FF, y]);
  }
  function diagFlares(pa, pb, d, y, name, L = true, R = true, fL = FF, fR = FF) {
    const u = (d[1] > 0) === (y === 0) ? d : mul(d, -1);
    let ea = [xAt(pa, d, y), y], eb = [xAt(pb, d, y), y]; if (ea[0] > eb[0]) [ea, eb] = [eb, ea];
    const nl = perp(u)[0] < 0 ? perp(u) : mul(perp(u), -1);
    if (L) flare(`Loe ${name} trái`, ea, u, nl, [ea[0] - fL, y]);
    if (R) flare(`Loe ${name} phải`, eb, u, mul(nl, -1), [eb[0] + fR, y]);
  }
  function beak(name, xEnd, yEdge, down, side) {
    const n = down ? [0, -1] : [0, 1]; side = side || (xEnd > W / 2 ? -1 : 1);
    flare(name, [xEnd, yEdge], [side, 0], n, [xEnd, yEdge + n[1] * BEAK]);
  }
  const yc = BAR_H * CAP, x0 = FF;
  // giữ đường cong tự do từ bản vẽ v0.2; guide: cung tròn khớp hoặc tay nắm Bézier
  function refGlyph(c) { const e = REF[`${c}-${W8}`]; if (!e) return false; P({ name: 'Hình (đường cong từ bản vẽ)', cmds: e.cmds });
    for (const q of e.guides) guides.push(q); return true; }
  // ring helpers (R1): outer ellipse minus counter, optionally clipped
  function ring(name, c, rxo, ryo, rxi, ryi, rot, clip, o) {
    const ci = (o && o.ci) || c; P(Object.assign({ name, cmds: ellC(c, rxo, ryo), minus: ellC(ci, rxi, ryi, rot), clip }, o && o.post ? { post: true } : {}));
    G({ type: 'ellipse', c, rx: rxo, ry: ryo, rot: 0 }); G({ type: 'ellipse', c: (o && o.ci) || c, rx: rxi, ry: ryi, rot: rot || 0, axes: true });
  }
  // bowl attached to a stem (B1)
  function bowl(name, xs, yb, yt, xr, wall = r.Vr, hb = r.Hb, cb = yb + hb, ct = yt - hb) { // cb, ct: đáy/đỉnh lòng
    const cy = (yb + yt) / 2, ry = (yt - yb) / 2, xm = xs + (xr - xs) * BOWL.flat;
    P({ name: name, cmds: halfRightC(xm, cy, xr - xm, ry, KAP, xm - xs + 3, BOWL.ky), minus: halfRightC(xs, (cb + ct) / 2, xr - wall - xs, (ct - cb) / 2, KAP, 3, BOWL.kyIn) });
    G({ type: 'center', c: [xm, cy] }); G({ type: 'center', c: [xs, cy] });
  }
  const B = {
    I() { stem(x0); stemFlares(x0, x0 + r.V, 0); stemFlares(x0, x0 + r.V, CAP); },
    H() { const xr = W - FF - r.V; stem(x0, 0, CAP, 'Thân trái'); stem(xr, 0, CAP, 'Thân phải');
      P(rect('Thanh', x0 + r.V - 3, yc - r.Hb / 2, xr + 3, yc + r.Hb / 2)); for (const x of [x0, xr]) { stemFlares(x, x + r.V, 0); stemFlares(x, x + r.V, CAP); } },
    E(noBottom) { const a = x0 + r.V - 3; stem(x0); stemFlares(x0, x0 + r.V, CAP, true, false);
      if (noBottom) stemFlares(x0, x0 + r.V, 0); else stemFlares(x0, x0 + r.V, 0, true, false);
      P(rect('Tay trên', a, CAP - r.Hb, W, CAP)); beak('Mỏ tay trên', W, CAP - r.Hb, true);
      const ym = noBottom ? yc - r.Hb / 4 : yc, xm = noBottom ? W - 0.05 * W : W;
      P(poly('Tay giữa', [[a, ym - r.Hb / 2], [xm, ym - r.Hb / 2], [xm - r.Hb * Math.tan(SLANT), ym + r.Hb / 2], [a, ym + r.Hb / 2]]));
      if (!noBottom) { P(rect('Tay dưới', a, 0, W, r.Hb)); beak('Mỏ tay dưới', W, r.Hb, false); } },
    F() { B.E(true); },
    L() { stem(x0); stemFlares(x0, x0 + r.V, CAP); stemFlares(x0, x0 + r.V, 0, true, false);
      P(rect('Tay dưới', x0 + r.V - 3, 0, W, r.Hb)); beak('Mỏ tay dưới', W, r.Hb, false); },
    T() { P(rect('Thanh trên', 0, CAP - r.Hb, W, CAP)); const x = W / 2 - r.V / 2; stem(x, 0, CAP - r.Hb + 3); stemFlares(x, x + r.V, 0);
      beak('Mỏ trái', 0, CAP - r.Hb, true); beak('Mỏ phải', W, CAP - r.Hb, true); },
    A(flip) { const xc = W / 2, yt = CAP + OVS, tl = [xc - APEX / 2, yt], tr = [xc + APEX / 2, yt], fl = [FF, 0], fr = [(VOPT && VOPT.noR) ? W : W - FF, 0];
      const [wl, wr] = flip ? [r.D, r.t] : [r.t, r.D];
      const leg = (name, foot, top, th, inward) => { const d = nrm(sub(top, foot)); const ni = (perp(d)[0] > 0) === (inward > 0) ? perp(d) : mul(perp(d), -1);
        const ip = add(foot, mul(ni, th)); return { name, d, foot, ip, pts: [[xAt(foot, d, 0), 0], [xAt(foot, d, yt), yt], [xAt(ip, d, yt), yt], [xAt(ip, d, 0), 0]] }; };
      const L = leg('Chân trái', fl, tl, wl, 1), R = leg('Chân phải', fr, tr, wr, -1);
      const hull = polyC([[xAt(fl, L.d, -60), -60], tl, tr, [xAt(fr, R.d, -60), -60]]);
      for (const g of [L, R]) { P(poly(g.name, g.pts, { clip: hull })); edges(g.foot, g.ip, g.d); }
      const vo = VOPT || {}; if (!vo.noL) diagFlares(L.foot, L.ip, L.d, 0, 'chân trái'); if (!vo.noR) diagFlares(R.foot, R.ip, R.d, 0, 'chân phải');
      G({ type: 'apex', p: [xc, yt], d1: mul(L.d, -1), d2: mul(R.d, -1) });
      if (!flip) { const y = BAR_A * CAP, mL = mul(add(L.foot, L.ip), 0.5), mR = mul(add(R.foot, R.ip), 0.5); // thanh chạy tới đường giữa chân → không lộ bậc
        P(rect('Thanh', Math.max(xAt(mL, L.d, y - r.Hb / 2), xAt(mL, L.d, y + r.Hb / 2)), y - r.Hb / 2, Math.min(xAt(mR, R.d, y - r.Hb / 2), xAt(mR, R.d, y + r.Hb / 2)), y + r.Hb / 2)); } },
    V() { B.A(true); flipAll(); },
    N() { const s0 = FF, sR = W - FF; stem(s0, 0, CAP, 'Thân trái', r.t); stem(sR - r.t, 0, CAP, 'Thân phải', r.t);
      stemFlares(s0, s0 + r.t, 0); stemFlares(sR - r.t, sR, CAP);
      const P1 = [s0 + r.t, CAP], P2 = [sR - r.t, 0], d = band2(P1, P2, r.D, 1);
      P(poly('Chéo', bandPts(P1, P2, d, CAP, 0), { clip: rectC(s0, 0, sR, CAP) })); edges(P1, P2, d);
      G({ type: 'apex', p: P1, d1: [0, -1], d2: d }); G({ type: 'apex', p: P2, d1: [0, 1], d2: mul(d, -1) }); },
    M() { // J2 ở hai góc trên, J1 ở đỉnh dưới (cao 175)
      const s0 = FF, sR = W - FF, yv = 175, xv = (s0 + r.t + sR - r.V) / 2;
      stem(s0, 0, CAP, 'Thân trái', r.t); stem(sR - r.V, 0, CAP, 'Thân phải', r.V);
      stemFlares(s0, s0 + r.t, 0); stemFlares(sR - r.V, sR, 0); stemFlares(s0, s0 + r.t, CAP, true, false); stemFlares(sR - r.V, sR, CAP, false, true);
      const P1 = [s0 + r.t, CAP], V1 = [xv - APEX / 2, yv], d1 = band2(P1, V1, r.D, 1);
      const P2 = [sR - r.V, CAP], V2 = [xv + APEX / 2, yv], d2 = band2(P2, V2, r.t, -1);
      const o1top = [xAt(V1, d1, CAP), CAP], o2top = [xAt(V2, d2, CAP), CAP];
      const hull = polyC([V1, o1top, o2top, V2]);
      P(poly('Chéo dày', bandPts(P1, V1, d1, yv - 50, CAP), { clip: hull, clip2: rectC(s0, 0, sR, CAP) }));
      P(poly('Chéo mảnh', bandPts(P2, V2, d2, yv - 50, CAP), { clip: hull, clip2: rectC(s0, 0, sR, CAP) })); edges(P1, V1, d1); edges(P2, V2, d2);
      G({ type: 'apex', p: [xv, yv], d1: d1[1] > 0 ? d1 : mul(d1, -1), d2: d2[1] > 0 ? d2 : mul(d2, -1) }); },
    W() { // hai V chồng nhau (đo v0.2): V1 rộng 0.70 W, đầu phải ở đỉnh không loe, mép chạm x = 0.70 W;
      // V2 bắt đầu ở 0.268 W, đầu trái không loe. Hai nét giữa cắt nhau.
      const W1 = Math.round(W * 0.70), o2 = Math.round(W * 0.268); VOPT = { noR: true }; const sub1 = makeGlyphV(W1, 0);
      VOPT = { noL: true }; const sub2 = makeGlyphV(W - o2, o2); VOPT = null;
      for (const s of [...sub1.parts, ...sub2.parts]) parts.push(s); for (const g of [...sub1.guides, ...sub2.guides]) guides.push(g); },
    X() { // chéo dày \ và chéo mảnh / giao nhau
      const A1 = [FF, CAP], B1 = [W - FF, 0], dT = band2(A1, B1, r.D, -1);
      const A2 = [FF, 0], B2 = [W - FF, CAP], dt = band2(A2, B2, r.t, 1);
      P(poly('Chéo dày', bandPts(A1, B1, dT, 0, CAP))); P(poly('Chéo mảnh', bandPts(A2, B2, dt, 0, CAP))); edges(A1, B1, dT); edges(A2, B2, dt);
      diagFlares(A1, B1, dT, CAP, 'đỉnh trái'); diagFlares(A1, B1, dT, 0, 'chân phải');
      diagFlares(A2, B2, dt, 0, 'chân trái'); diagFlares(A2, B2, dt, CAP, 'đỉnh phải'); },
    Y() { // đo v0.2: thân lệch phải (tâm 0.509 W); tay trái dày D chạm mép trái thân ở 0.464 cap, tay phải mảnh t chạm mép phải ở 0.53 cap
      // mép ngoài hai tay đi thẳng tới góc (0, cap) và (W, cap): chỉ loe phía trong, mũi cách mép 2·FF
      const yl = 0.464 * CAP, yr = 0.53 * CAP, xs = 0.509 * W - r.V / 2;
      stem(xs, 0, yr); stemFlares(xs, xs + r.V, 0);
      const dl = nrm(sub([xs, yl], [0, CAP])), dr = nrm(sub([xs + r.V, yr], [W, CAP]));
      const il = add([0, CAP], mul(perp(dl)[0] > 0 ? perp(dl) : mul(perp(dl), -1), r.D));
      const ir = add([W, CAP], mul(perp(dr)[0] < 0 ? perp(dr) : mul(perp(dr), -1), r.t));
      const hull = polyC([[0, CAP], [xs, yl], [xs, yl - 120], [xs + r.V, yr - 120], [xs + r.V, yr], [W, CAP]]);
      P(poly('Tay trái', bandPts([0, CAP], il, dl, yl - 120, CAP), { clip: hull }));
      P(poly('Tay phải', bandPts([W, CAP], ir, dr, yr - 120, CAP), { clip: hull })); edges([0, CAP], il, dl); edges([W, CAP], ir, dr);
      diagFlares([0, CAP], il, dl, CAP, 'tay trái', false, true, FF, 2 * FF); diagFlares([W, CAP], ir, dr, CAP, 'tay phải', true, false, 2 * FF, FF);
      G({ type: 'apex', p: [xs, yl], d1: mul(dl, -1), d2: [0, -1] }); G({ type: 'apex', p: [xs + r.V, yr], d1: mul(dr, -1), d2: [0, -1] }); },
    K() { // đo v0.2: tay mảnh t, mép trên chạm thân ở 0.54 cap, mép dưới tới cap tại W − FF − 52;
      // chân dày D: mép trên mọc từ mép dưới của tay ở 0.58 cap và xuống baseline tại W − FF
      const xs = x0 + r.V, ya = 0.54 * CAP, yj = 0.58 * CAP;
      stem(x0); stemFlares(x0, x0 + r.V, 0); stemFlares(x0, x0 + r.V, CAP);
      const Pa = [xs, ya], Ta = [W - FF - 52, CAP], da = band2(Pa, Ta, r.t, 1), dA = da[1] > 0 ? da : mul(da, -1);
      const na = perp(dA)[0] > 0 ? perp(dA) : mul(perp(dA), -1), qa = add(Pa, mul(na, r.t)); // qa: một điểm trên mép dưới-phải của tay
      P(poly('Tay', bandPts(Pa, qa, dA, ya - 80, CAP), { clip: rectC(xs - 3, 0, W, CAP) }));
      diagFlares(Pa, qa, dA, CAP, 'tay');
      const Pj = [xAt(qa, dA, yj), yj], Fr = [W - FF, 0], dl = nrm(sub(Pj, Fr)), nl = perp(dl)[0] < 0 ? perp(dl) : mul(perp(dl), -1);
      const Fl = add(Fr, mul(nl, r.D)), armLow = halfPlane(Pa, perp(dA)[1] < 0 ? perp(dA) : mul(perp(dA), -1));
      P(poly('Chân', bandPts(Fr, Fl, dl, 0, yj + 60), { clip: rectC(xs - 3, 0, W, CAP), clip2: armLow }));
      diagFlares(Fr, Fl, dl, 0, 'chân'); edges(Pa, qa, dA); edges(Fr, Fl, dl);
      G({ type: 'apex', p: Pa, d1: dA, d2: [0, -1] }); G({ type: 'apex', p: Pj, d1: mul(dl, -1), d2: dA }); },
    O() { const R = W / 2, c = [W / 2, CAP / 2]; ring('Vòng', c, R, R, R - r.Vr, CAP / 2 + OVS - (r.Hb - 6), 30 * DEG); },
    Q() { if (refGlyph('Q')) return; const R = 723 / 2, c = [R, CAP / 2]; ring('Vòng', c, R, R, R - r.Vr, CAP / 2 + OVS - (r.Hb - 6), 30 * DEG);
      // Q1: đuôi = trăng khuyết giữa hai cung tròn đi qua cùng hai điểm S0, E0
      const S0 = [0.47 * 2 * R, 60], E0 = [W, -150], u = nrm(sub(E0, S0)), n = [u[1], -u[0]], L = Math.hypot(...sub(E0, S0)), mid = mul(add(S0, E0), 0.5);
      const arc = sag => { const rr = (L * L / 4 + sag * sag) / (2 * sag), c0 = add(mid, mul(n, -(rr - sag)));
        const a0 = Math.atan2(S0[1] - c0[1], S0[0] - c0[0]); let a1 = Math.atan2(E0[1] - c0[1], E0[0] - c0[0]);
        while (a1 - a0 > Math.PI) a1 -= 2 * Math.PI; while (a1 - a0 < -Math.PI) a1 += 2 * Math.PI; return { c0, rr, a0, a1 }; };
      const o = arc(100), i = arc(100 - (W8 === 'Bold' ? 78 : 56));
      P({ name: 'Đuôi', post: true, cmds: [['M', S0], ...arcCmds(o.c0, o.rr, o.a0, o.a1), ...arcCmds(i.c0, i.rr, i.a1, i.a0), ['Z']] });
      G({ type: 'compass', c: o.c0, r: o.rr, a0: o.a0, a1: o.a1, T: S0, tip: E0 }); G({ type: 'compass', c: i.c0, r: i.rr, a0: i.a0, a1: i.a1, T: E0, tip: S0 }); },
    C(gee) { // lòng đứng (ngoại lệ C, G): thành trái = Vr, đỉnh/đáy = Hb; cắt dọc tại x = W
      const R = 723 / 2, c = [R, CAP / 2], rxi = 0.64 * R, ryi = R - r.Hb - (gee ? 15 : 0);
      P({ name: 'Vòng', cmds: ellC(c, R, R), minus: ellC([r.Vr + rxi, CAP / 2], rxi, ryi), clip: rectC(-10, -100, W, CAP + 100) });
      G({ type: 'center', c }); G({ type: 'center', c: [r.Vr + rxi, CAP / 2] }); G({ type: 'cut', x: W });
      if (gee) { const yg = 0.48 * CAP, xa = W - r.V - 70;
        P(rect('Thân G', W - r.V, r.Hb, W, yg)); P(rect('Tay G', xa, yg - r.Hb, W, yg)); beak('Mỏ tay G', xa, yg - r.Hb, true, 1); } },
    G() { B.C(true); },
    D() { stem(x0); stemFlares(x0, x0 + r.V, 0, true, false); stemFlares(x0, x0 + r.V, CAP, true, false); bowl('Bụng', x0 + r.V, 0, CAP, W); },
    B() { BOWL = BOWL_BPR; stem(x0); stemFlares(x0, x0 + r.V, 0, true, false); stemFlares(x0, x0 + r.V, CAP, true, false);
      // đo v0.2: thanh giữa tâm 0.567 cap; mép ngoài hai bụng gặp nhau tại một điểm (cao yj + 4) → có khấc; bụng trên rộng 0.78
      const yj = 0.567 * CAP, yo = yj + 4, xs = x0 + r.V;
      bowl('Bụng dưới', xs, 0, yo, W, r.Vr, r.Hb, r.Hb, yj - r.Hb / 2); bowl('Bụng trên', xs, yo, CAP, xs + 0.78 * (W - xs), r.Vr, r.Hb, yj + r.Hb / 2, CAP - r.Hb); BOWL = BOWL0; },
    P(isR) { BOWL = BOWL_BPR; stem(x0); stemFlares(x0, x0 + r.V, CAP, true, false); stemFlares(x0, x0 + r.V, 0);
      const yb = 0.486 * CAP, xr = isR ? WIDTH[W8].P : W; bowl('Bụng', x0 + r.V, yb, CAP, xr); BOWL = BOWL0; // R dùng đúng bụng của P
      if (isR) { // đo v0.2: chân nghiêng 27° so với phương đứng, mép phải chạm baseline ở W − 40, dày D
        const Fr = [W - 40, 0], dl = nrm([-Math.sin(27.2 * DEG), Math.cos(27.2 * DEG)]), Fl = add(Fr, mul(perp(dl)[0] < 0 ? perp(dl) : mul(perp(dl), -1), r.D));
        P(poly('Chân', bandPts(Fr, Fl, dl, 0, yb + 3), { clip: rectC(x0 + r.V - 3, 0, W, yb + 3) })); diagFlares(Fr, Fl, dl, 0, 'chân', true, true, FF, 40); edges(Fr, Fl, dl); } },
    R() { B.P(true); },
    U() { const xr = W - FF - r.V, yu = 0.33 * CAP, cx = W / 2, rxo = cx - FF, ryo = yu + OVS;
      stem(x0, yu - 3, CAP, 'Thân trái'); stem(xr, yu - 3, CAP, 'Thân phải'); stemFlares(x0, x0 + r.V, CAP); stemFlares(xr, xr + r.V, CAP);
      P({ name: 'Bụng U', cmds: ellC([cx, yu], rxo, ryo), minus: ellC([cx, yu], rxo - r.V, yu - r.Hb), clip: rectC(0, -100, W, yu) }); G({ type: 'center', c: [cx, yu] }); },
    J() { // đo v0.2: thân V xuống baseline, góc ngoài cung r 170, góc trong cung r 85; đuôi là thanh Hb chạy tới x = 0, đầu có mỏ L2
      const xe = W - FF, xs = xe - r.V, Ro = 170, ri = 85, co = [xe - Ro, Ro], ci = [xs - ri, r.Hb + ri];
      stem(xs, Ro - 3, CAP); stemFlares(xs, xe, CAP);
      const hook = [['M', [0, 0]], ['L', [co[0], 0]], ...arcCmds(co, Ro, -Math.PI / 2, 0), ['L', [xs, Ro]], ['L', [xs, ci[1]]], ...arcCmds(ci, ri, 0, -Math.PI / 2), ['L', [0, r.Hb]], ['Z']];
      P({ name: 'Móc J', cmds: hook }); beak('Mỏ đuôi J', 0, r.Hb, false, 1);
      G({ type: 'compass', c: co, r: Ro, a0: -Math.PI / 2, a1: 0, T: [xe, Ro], tip: [co[0], 0] });
      G({ type: 'compass', c: ci, r: ri, a0: -Math.PI / 2, a1: 0, T: [xs, ci[1]], tip: [ci[0], r.Hb] }); },
    S() { if (refGlyph('S')) return;
 // (dự phòng) S1: hai vòng (đường tâm) tiếp xúc tại T; thành phía T dày Sp/2 → sống = Sp; đỉnh/đáy = Hb; nén ngang hệ số k
      const H = CAP + 2 * OVS, Sp = r.V * 1.02, phi = -68 * DEG, s1 = Math.abs(Math.sin(phi));
      const rsum = (H - Sp) / (1 + s1), rhoU = 0.46 * rsum, rhoL = rsum - rhoU, RoU = rhoU + Sp / 2, RoL = rhoL + Sp / 2;
      const off = rsum * Math.cos(phi), k = W / (off + RoU + RoL);
      const cU = [k * RoU, CAP + OVS - RoU], cL = [cU[0] + k * off, cU[1] - rsum * s1];
      const dir = [Math.cos(phi), Math.sin(phi)];
      const inner = (c, rho, Ro, sgn) => { const RiY = rho - r.Hb / 2, ax = Math.min(Ro - 0.72 * r.V / k, RiY);
        const Rdir = 1 / Math.hypot(dir[0] / ax, dir[1] / RiY), del = Rdir - rho + Sp / 2; // thành tại T đúng Sp/2
        const ci = [c[0] - sgn * k * dir[0] * del, c[1] - sgn * dir[1] * del]; return ellC(ci, k * ax, RiY); };
      const far = (c, a) => add(c, [1500 * k * Math.cos(a), 1500 * Math.sin(a)]);
      const xtU = cU[0] + 0.80 * k * RoU, xtL = cL[0] - 0.80 * k * RoL;
      const keepU = polyC([[xtU, cU[1]], [xtU, cU[1] + 1500], [-1500, cU[1] + 1500], [-1500, cU[1] - 1500], far(cU, phi), cU]);
      const keepL = polyC([[xtL, cL[1]], [xtL, cL[1] - 1500], [1500, cL[1] - 1500], [1500, cL[1] + 1500], far(cL, phi + Math.PI), cL]);
      P({ name: 'Vòng trên', cmds: ellC(cU, k * RoU, RoU), minus: inner(cU, rhoU, RoU, 1), clip: keepU });
      P({ name: 'Vòng dưới', cmds: ellC(cL, k * RoL, RoL), minus: inner(cL, rhoL, RoL, -1), clip: keepL });
      const T = [cU[0] + k * rhoU * dir[0], cU[1] + rhoU * dir[1]];
      G({ type: 'center', c: cU }); G({ type: 'center', c: cL }); G({ type: 'apex', p: T, d1: [k * dir[0], dir[1]], d2: [-k * dir[0], -dir[1]] });
      G({ type: 'cut', x: xtU }); G({ type: 'cut', x: xtL }); },
    Z() { // đo v0.2: mép chéo đi qua (W, cap − 17) và (0, 17) → đầu chéo cắt dọc trùng mép thanh, không có bậc
      const A1 = [W, CAP - 17], B1 = [0, 17], d = band2(A1, B1, r.D, 1);
      P(rect('Thanh trên', 11, CAP - r.Hb, W, CAP)); beak('Mỏ trái', 11, CAP - r.Hb, true, 1);
      P(rect('Thanh dưới', 0, 0, W - 11, r.Hb)); beak('Mỏ phải', W - 11, r.Hb, false, -1);
      P(poly('Chéo', bandPts(A1, B1, d, -50, CAP + 50), { clip: rectC(0, 0, W, CAP) })); edges(A1, B1, d); G({ type: 'apex', p: A1, d1: [0, -1], d2: mul(d, d[1] < 0 ? 1 : -1) }); G({ type: 'apex', p: B1, d1: [0, 1], d2: mul(d, d[1] < 0 ? -1 : 1) }); },
    // ---------------- bộ số (F1)
    '0'() { const c = [W / 2, CAP / 2]; ring('Vòng', c, W / 2, CAP / 2 + OVS, W / 2 - r.V, CAP / 2 + OVS - r.Hb - 4, 15 * DEG); },
    '1'() { // đo v0.2: đỉnh thân vượt cap 11; mép trên cờ là đường thẳng từ đỉnh thân tới mũi (0, cap − 100); mép dưới là cung L1
      const xs = W - FF - r.V, yt = CAP + 11, tip = [0, CAP - 100];
      stem(xs, 0, yt); stemFlares(xs, xs + r.V, 0);
      P(poly('Cờ', [tip, [xs + r.V - 9, yt], [xs + 3, yt], [xs + 3, tip[1]]]));
      flare('Loe cờ', [xs, tip[1]], [0, -1], [-1, 0], tip); },
    '8'() { // hai vòng elip chồng nhau, lòng nghiêng trục −60° (đo v0.2)
      const k = W / 521, dB = (r.V - 102) * 0.7;
      ring('Vòng dưới', [W / 2, 210], 261 * k, 221, 159 - dB, 181 - dB, 30 * DEG);
      ring('Vòng trên', [W / 2, 550], 204 * k, 159, 116 - dB * 0.8, 122 - dB * 0.8, 30 * DEG, undefined, { ci: [W / 2, 553] });
      G({ type: 'hline', y: 210 }); G({ type: 'hline', y: 550 }); },
    '6'() { // bụng = vòng r 246, lòng elip 145×205 trục −60°; nét lên = phần của vòng lớn 289×367 (≈ vòng số 0), lòng 186×329 nghiêng 15°
      const k = W / 527, dB = (r.V - 102) * 0.7, bR = 246 + (W - 527) / 2, bc = [W - bR, 234];
      const Bc = [289 * k, 344], Ic = [288 * k, 342], Tin = [409 * k, 527], Tout = [452 * k, 643], dT = nrm(sub(Tout, Tin));
      ring('Bụng', bc, bR, 246, 145 - dB, 205 - dB, 30 * DEG);
      const clip = polyC([[-100, 78], [bc[0], 78], bc, Tin, add(Tin, mul(dT, 800)), [-100, 1000]]);
      P({ name: 'Nét lên (vòng lớn)', cmds: ellC(Bc, 289 * k, 367), minus: ellC(Ic, 186 - dB, 329 - dB, 14.5 * DEG), clip });
      G({ type: 'ellipse', c: Bc, rx: 289 * k, ry: 367, rot: 0 }); G({ type: 'ellipse', c: Ic, rx: 186 - dB, ry: 329 - dB, rot: 14.5 * DEG, axes: true });
      G({ type: 'line', p: Tin, d: dT }); G({ type: 'hline', y: 78 }); G({ type: 'hline', y: bc[1] + 246 }); },
    '9'() { B['6'](); for (const s of parts) for (const k of ['cmds', 'minus', 'clip']) if (s[k]) s[k] = rot180(s[k], W);
      for (const g of guides) { for (const k of ['c', 'T', 'tip', 'p']) if (g[k]) g[k] = [W - g[k][0], CAP - g[k][1]];
        if (g.d) g.d = mul(g.d, -1); if (g.type === 'hline') g.y = CAP - g.y; if (g.type === 'cut') g.x = W - g.x; if (g.type === 'axis') g.rot += Math.PI; } },
    '3'(five) { // đo v0.2: bụng = elip 258×244 tâm (190, 235); lòng = elip 157×220 nghiêng 40°; mở ở trái, cắt dọc x = 0 tới cao 241
      const k = W / 449, dB = (r.V - 102) * 0.7, c = [190 * k, 235], ci = add([178 * k, 234], mul([Math.cos(130 * DEG), Math.sin(130 * DEG)], dB)); // đậm: lòng co về phía dưới-phải, giữ mép trên-trái
      const rxI = 157 * k - dB, ryI = 220 - dB, inE = p => { const x = p[0] - ci[0], y = p[1] - ci[1], ca = Math.cos(40 * DEG), sa = Math.sin(40 * DEG); return ((x * ca + y * sa) / rxI) ** 2 + ((-x * sa + y * ca) / ryI) ** 2 < 1; };
      let yo = 241.3; for (let y = 241; y < 420; y++) if (inE([0.5, y])) { yo = y; break; } // đầu hở cắt đúng chỗ lòng chạm x = 0
      if (yo === 241.3 && W8 !== 'Regular') { let bx = 1e9; for (let i = 0; i < 360; i++) { const t = i * DEG, x = ci[0] + rxI * Math.cos(t) * Math.cos(40 * DEG) - ryI * Math.sin(t) * Math.sin(40 * DEG), y = ci[1] + rxI * Math.cos(t) * Math.sin(40 * DEG) + ryI * Math.sin(t) * Math.cos(40 * DEG); if (x < bx && y > 200) { bx = x; yo = y; } } } // lòng không chạm x = 0: cắt ở điểm lòng gần mép nhất
      const inner = ellC(ci, 157 * k - dB, 220 - dB, 40 * DEG);
      G({ type: 'ellipse', c, rx: 258 * k, ry: 244, rot: 0 }); G({ type: 'ellipse', c: ci, rx: 157 * k - dB, ry: 220 - dB, rot: 40 * DEG, axes: true }); G({ type: 'hline', y: yo });
      if (!five) { // thanh trên Hf rộng 405, mỏ trái; chéo mảnh t: mép phải qua (W − 44, cap − 13) và đỉnh bụng (207, 478)
        // mép trái chéo cố định qua (145, 475) (đo v0.2), nét dày thêm về phía phải khi đậm
        const xb = 405 * k, d = nrm(sub([418 * k, CAP - 13], [207 * k, 478])), nl = perp(d)[0] < 0 ? perp(d) : mul(perp(d), -1), L1 = [145.4 * k, 475.4], Bt = add(L1, mul(nl, -r.t));
        let yc = 478; while (yc > 300 && !inE([xAt(L1, d, yc), yc])) yc -= 1; // điểm mép trái chéo chạm lòng
        const xc = xAt(L1, d, yc), Q = polyC([[-100, -100], [2000, -100], [2000, 2000], [xAt(L1, d, 2000), 2000], [xAt(L1, d, yc), yc], [xc, yc], [xc, yo], [-100, yo]]); // giữ: bỏ phần bụng phía trên-trái (mở)
        P(rect('Thanh trên', 0, CAP - r.Hf, xb, CAP)); beak('Mỏ trái', 0, CAP - r.Hf, true, 1);
        P(poly('Chéo', bandPts(Bt, L1, d, 300, CAP + 50), { clip: rectC(xc, 300, xb, CAP), minus: inner }));
        P({ name: 'Bụng', cmds: ellC(c, 258 * k, 244), minus: inner, clip: rectC(0, -100, W + 10, 800), clip2: Q }); edges(Bt, L1, d); }
      else { // thanh trên từ 49 tới 395, mỏ phải; thân mảnh t nghiêng 9°, mép trái qua (49, cap); chân thân cắt ngang ở 397
        const x1 = 49 * k, xb = 395 * k, ys = 396.7, d = nrm([0.156, 1]), T = [x1, CAP], nr = [d[1], -d[0]], Rr = add(T, mul(nr, r.t));
        P(rect('Thanh trên', x1 - 10, CAP - r.Hf, xb, CAP)); beak('Mỏ phải', xb, CAP - r.Hf, true, -1);
        P(poly('Thân 5', bandPts(T, Rr, d, ys, CAP), { clip: rectC(0, ys, W, CAP) }));
        const Q = polyC([[-100, yo], [xAt(Rr, d, yo), yo], [xAt(Rr, d, 1200), 1200], [-100, 1200]]);
        P({ name: 'Bụng', cmds: ellC(c, 258 * k, 244), minus: inner, clip: rectC(0, -100, W + 10, 800), clip2: polyC([[-100, -100], [2000, -100], [2000, 2000], [xAt(Rr, d, 2000), 2000], [xAt(Rr, d, yo), yo], [-100, yo]]) });
        edges(T, Rr, d); } },
    '5'() { B['3'](true); },
    '2'() { if (refGlyph('2')) return; // cung trên + chéo tiếp tuyến với cung + thanh đáy
      const ryU = 0.30 * (CAP + 2 * OVS), cU = [W / 2, CAP + OVS - ryU], rx = W / 2, xt = cU[0] - 0.86 * rx;
      const Bp = [0.30 * W, r.Hf]; const bx = (Bp[0] - cU[0]) / rx, by = (Bp[1] - cU[1]) / ryU, Lb = Math.hypot(bx, by);
      const th = Math.atan2(by, bx) + Math.acos(1 / Lb); // tiếp điểm phía phải-dưới
      const A1 = [cU[0] + rx * Math.cos(th), cU[1] + ryU * Math.sin(th)], d = nrm(sub(A1, Bp));
      const nq = perp(d)[0] < 0 ? perp(d) : mul(perp(d), -1), Q = add(Bp, mul(nq, r.D));
      P({ name: 'Cung trên', cmds: ellC(cU, rx, ryU), minus: ellC(cU, rx - r.V, ryU - r.Hb, 15 * DEG),
        clip: polyC([[xt, cU[1]], [xt, cU[1] + 1000], [2000, cU[1] + 1000], [2000, cU[1] - 1000], add(cU, [1000 * Math.cos(th - 3 * DEG), 1000 * Math.sin(th - 3 * DEG)]), cU]) });
      G({ type: 'center', c: cU }); G({ type: 'cut', x: xt }); G({ type: 'apex', p: A1, d1: d, d2: mul(d, -1) });
      P(rect('Thanh đáy', 0, 0, W, r.Hf)); beak('Mỏ phải', W, r.Hf, false, -1);
      P(poly('Chéo', bandPts(A1, Q, d, r.Hf - 3, cU[1]), { clip: rectC(0, 0, W, CAP), clip2: halfPlane(A1, mul(d, -1)), minus: ellC(cU, rx - r.V, ryU - r.Hb, 15 * DEG) })); },
    '4'() { // đo v0.2: thân ở 0.62 W, đỉnh vượt cap 9; thanh 0.24–0.33 cap có mỏ hướng lên; chéo mảnh t, mép ngoài từ (0, 0.316 cap) tới đỉnh thân
      const xs = 0.62 * W, yt = CAP + 9, yb0 = 0.238 * CAP, yb1 = yb0 + 0.70 * r.Hf, O1 = [0, 0.316 * CAP], O2 = [xs + r.V - 14, yt];
      const d = nrm(sub(O2, O1)), ni = perp(d)[0] > 0 ? perp(d) : mul(perp(d), -1), I1 = add(O1, mul(ni, r.t));
      const under = halfPlane(O1, perp(d)[1] < 0 ? perp(d) : mul(perp(d), -1));
      stem(xs, 0, yt); parts[parts.length - 1].clip = under; stemFlares(xs, xs + r.V, 0);
      P(rect('Thanh', 0, yb0, W, yb1)); beak('Mỏ phải', W, yb1, true, -1);
      P(poly('Chéo', bandPts(O1, I1, d, yb0, yt), { clip: rectC(0, yb0, xs + r.V, yt) })); edges(O1, I1, d);
      G({ type: 'apex', p: O2, d1: mul(d, -1), d2: [0, -1] }); },
    '7'() { // đo v0.2: thanh Hb, mỏ trái; chéo dày D, mép phải qua (W, cap − 15) và (0.433 W, 0); chân chỉ loe phía phải (mũi cách 2·FF)
      P(rect('Thanh trên', 0, CAP - r.Hb, W, CAP)); beak('Mỏ trái', 0, CAP - r.Hb, true, 1);
      const A1 = [W, CAP - 15], F1 = [0.433 * W, 0], d = nrm(sub(A1, F1)), nl = perp(d)[0] < 0 ? perp(d) : mul(perp(d), -1), F2 = add(F1, mul(nl, r.D));
      P(poly('Chéo', bandPts(F1, F2, d, 0, CAP + 50), { clip: rectC(0, 0, W, CAP) })); diagFlares(F1, F2, d, 0, 'chân', false, true, FF, 2 * FF); edges(F1, F2, d);
      G({ type: 'apex', p: A1, d1: [0, 1], d2: mul(d, -1) }); },
  };
  function flipAll() { for (const s of parts) for (const k of ['cmds', 'minus', 'clip']) if (s[k]) s[k] = flipY(s[k]);
    for (const g of guides) { for (const k of ['c', 'T', 'tip', 'p']) if (g[k]) g[k] = [g[k][0], CAP - g[k][1]];
      if (g.type === 'compass') { g.a0 = -g.a0; g.a1 = -g.a1; } if (g.type === 'apex') { g.d1 = [g.d1[0], -g.d1[1]]; g.d2 = [g.d2[0], -g.d2[1]]; } } }
  function makeGlyphV(Wv, ox) { // V con cho W
    const sub = makeGlyphRaw('V', W8, Wv); for (const s of sub.parts) for (const k of ['cmds', 'minus', 'clip']) if (s[k]) s[k] = s[k].map(c => [c[0], ...c.slice(1).map(p => [p[0] + ox, p[1]])]);
    for (const g of sub.guides) for (const k of ['c', 'T', 'tip', 'p']) if (g[k]) g[k] = [g[k][0] + ox, g[k][1]]; return sub; }
  B[ch]();
  return { ch, W, parts, guides, src: 'rule' };
}
function makeGlyphRaw(ch, W8, Wover) { const save = WIDTH[W8][ch]; WIDTH[W8][ch] = Wover; const g = makeGlyph(ch, W8); WIDTH[W8][ch] = save; return g; }
const VN = 'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ';
const PUNCT = '.,:;!?\'"’‘”“-–—()[]/+=×#%$€&@';
const LOWER = 'abdegpq';
const ALL = [...'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', ...VN, ...PUNCT, ...LOWER];
if (typeof module !== 'undefined') module.exports = { makeGlyph, ALL, VN, PUNCT, LOWER, RULES, WIDTH, CAP, OVS, arcCmds };
