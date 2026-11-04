// Đìzai Serif v0.3 — bộ hình học theo quy tắc (nguồn chính). Chạy được trong Figma và Node.
// Luật: docs/07-rule-book-v0.3-dung-theo-quy-tac.md. Đơn vị font, cap 700, y hướng lên.
// Part: {name, cmds, clip?, minus?, counter?, post?}
//   cmds/clip/minus: [['M',p],['L',p],['C',c1,c2,p],['Z']]
//   minus: trừ riêng khỏi part này (vòng = ngoài − lòng);  clip: giao với vùng;  counter: trừ khỏi cả glyph;
//   post: cộng sau khi trừ counter (ví dụ đuôi Q đi qua lòng).
const CAP = 700, OVS = 12;
const RULES = { Regular: { V: 102, Vr: 106, D: 100, t: 44, Hb: 40, Hf: 90 }, Bold: { V: 139, Vr: 146, D: 146, t: 74, Hb: 68, Hf: 120 } };
const WIDTH = {
  Regular: { A: 672, B: 473, C: 537, D: 558, E: 374, F: 374, G: 537, H: 499, I: 148, J: 303, K: 503, L: 408, M: 643, N: 499, O: 723, P: 473, Q: 757, R: 527, S: 394, T: 397, U: 499, V: 672, W: 780, X: 642, Y: 632, Z: 465,
    '0': 578, '1': 201, '2': 448, '3': 449, '4': 530, '5': 449, '6': 527, '7': 445, '8': 521, '9': 527 },
  Bold: { A: 695, B: 504, C: 574, D: 609, E: 422, F: 422, G: 574, H: 541, I: 185, J: 340, K: 560, L: 456, M: 649, N: 555, O: 723, P: 502, Q: 768, R: 584, S: 451, T: 445, U: 541, V: 695, W: 805, X: 665, Y: 655, Z: 513,
    '0': 608, '1': 238, '2': 478, '3': 479, '4': 567, '5': 479, '6': 557, '7': 475, '8': 551, '9': 557 } };
const FR = 112, FF = 23, BEAK = 54, APEX = 20, SLANT = 26 * Math.PI / 180, BAR_H = 0.53, BAR_A = 0.255, KAP = 0.5523, KIN = 0.60, DEG = Math.PI / 180;
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
function halfRightC(cx, cy, rx, ry, kappa, ext) {
  const kx = kappa * rx, ky = kappa * ry;
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
  const r = RULES[W8], W = WIDTH[W8][ch], parts = [], guides = [];
  const P = s => (parts.push(s), s);
  const G = (o) => guides.push(o);
  // L1 / L2 — one circle r tangent to the stroke edge through the tip
  function flare(name, Eg, u, n, Pt, rad = FR) {
    const w = sub(Pt, Eg), uw = dot(u, w), nw = dot(n, w), s = uw + Math.sqrt(Math.max(0, uw * uw - dot(w, w) + 2 * rad * nw));
    const T = add(Eg, mul(u, s)), C = add(T, mul(n, rad));
    const a0 = Math.atan2(Pt[1] - C[1], Pt[0] - C[0]); let d = Math.atan2(T[1] - C[1], T[0] - C[0]) - a0;
    while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI;
    P({ name, cmds: [['M', add(Eg, mul(n, -3))], ['L', Pt], ...arcCmds(C, rad, a0, a0 + d), ['L', add(T, mul(n, -3))], ['Z']] });
    G({ type: 'compass', c: C, r: rad, a0, a1: a0 + d, T, tip: Pt });
  }
  const stem = (x0, y0 = 0, y1 = CAP, name = 'Thân', w = r.V) => P(rect(name, x0, y0, x0 + w, y1));
  function stemFlares(x0, x1, y, L = true, R = true) {
    const u = y === 0 ? [0, 1] : [0, -1], tag = y === 0 ? 'chân' : 'đỉnh';
    if (L) flare(`Loe ${tag} trái`, [x0, y], u, [-1, 0], [x0 - FF, y]);
    if (R) flare(`Loe ${tag} phải`, [x1, y], u, [1, 0], [x1 + FF, y]);
  }
  function diagFlares(pa, pb, d, y, name, L = true, R = true) {
    const u = (d[1] > 0) === (y === 0) ? d : mul(d, -1);
    let ea = [xAt(pa, d, y), y], eb = [xAt(pb, d, y), y]; if (ea[0] > eb[0]) [ea, eb] = [eb, ea];
    const nl = perp(u)[0] < 0 ? perp(u) : mul(perp(u), -1);
    if (L) flare(`Loe ${name} trái`, ea, u, nl, [ea[0] - FF, y]);
    if (R) flare(`Loe ${name} phải`, eb, u, mul(nl, -1), [eb[0] + FF, y]);
  }
  function beak(name, xEnd, yEdge, down, side) {
    const n = down ? [0, -1] : [0, 1]; side = side || (xEnd > W / 2 ? -1 : 1);
    flare(name, [xEnd, yEdge], [side, 0], n, [xEnd, yEdge + n[1] * BEAK]);
  }
  const yc = BAR_H * CAP, x0 = FF;
  // ring helpers (R1): outer ellipse minus counter, optionally clipped
  function ring(name, c, rxo, ryo, rxi, ryi, rot, clip, o) {
    P(Object.assign({ name, cmds: ellC(c, rxo, ryo), minus: ellC(c, rxi, ryi, rot), clip }, o || {}));
    G({ type: 'center', c }); if (rot) G({ type: 'axis', c, len: ryi * 1.1, rot: rot + Math.PI / 2 });
  }
  // bowl attached to a stem (B1)
  function bowl(name, xs, yb, yt, xr, wall = r.Vr, hb = r.Hb) {
    const cy = (yb + yt) / 2, ry = (yt - yb) / 2, xm = xs + (xr - xs) * 0.35;
    P({ name: name, cmds: halfRightC(xm, cy, xr - xm, ry, KAP, xm - xs + 3), minus: halfRightC(xs, cy, xr - wall - xs, ry - hb, KIN, 3) });
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
    A(flip) { const xc = W / 2, yt = CAP + OVS, tl = [xc - APEX / 2, yt], tr = [xc + APEX / 2, yt], fl = [FF, 0], fr = [W - FF, 0];
      const [wl, wr] = flip ? [r.D, r.t] : [r.t, r.D];
      const leg = (name, foot, top, th, inward) => { const d = nrm(sub(top, foot)); const ni = (perp(d)[0] > 0) === (inward > 0) ? perp(d) : mul(perp(d), -1);
        const ip = add(foot, mul(ni, th)); return { name, d, foot, ip, pts: [[xAt(foot, d, 0), 0], [xAt(foot, d, yt), yt], [xAt(ip, d, yt), yt], [xAt(ip, d, 0), 0]] }; };
      const L = leg('Chân trái', fl, tl, wl, 1), R = leg('Chân phải', fr, tr, wr, -1);
      const hull = polyC([[xAt(fl, L.d, -60), -60], tl, tr, [xAt(fr, R.d, -60), -60]]);
      for (const g of [L, R]) P(poly(g.name, g.pts, { clip: hull }));
      diagFlares(L.foot, L.ip, L.d, 0, 'chân trái'); diagFlares(R.foot, R.ip, R.d, 0, 'chân phải');
      G({ type: 'apex', p: [xc, yt], d1: mul(L.d, -1), d2: mul(R.d, -1) });
      if (!flip) { const y = BAR_A * CAP; P(rect('Thanh', xAt(L.ip, L.d, y) - 3, y - r.Hb / 2, xAt(R.ip, R.d, y) + 3, y + r.Hb / 2)); } },
    V() { B.A(true); flipAll(); },
    N() { const s0 = FF, sR = W - FF; stem(s0, 0, CAP, 'Thân trái', r.t); stem(sR - r.t, 0, CAP, 'Thân phải', r.t);
      stemFlares(s0, s0 + r.t, 0); stemFlares(sR - r.t, sR, CAP);
      const P1 = [s0 + r.t, CAP], P2 = [sR - r.t, 0], d = band2(P1, P2, r.D, 1);
      P(poly('Chéo', bandPts(P1, P2, d, CAP, 0), { clip: rectC(s0, 0, sR, CAP) }));
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
      P(poly('Chéo mảnh', bandPts(P2, V2, d2, yv - 50, CAP), { clip: hull, clip2: rectC(s0, 0, sR, CAP) }));
      G({ type: 'apex', p: [xv, yv], d1: d1[1] > 0 ? d1 : mul(d1, -1), d2: d2[1] > 0 ? d2 : mul(d2, -1) }); },
    W() { // hai V chồng nhau (W La Mã)
      const Wv = Math.round(W * 0.62), sub1 = makeGlyphV(Wv, 0), sub2 = makeGlyphV(Wv, W - Wv);
      for (const s of [...sub1.parts, ...sub2.parts]) parts.push(s); for (const g of [...sub1.guides, ...sub2.guides]) guides.push(g); },
    X() { // chéo dày \ và chéo mảnh / giao nhau
      const A1 = [FF, CAP], B1 = [W - FF, 0], dT = band2(A1, B1, r.D, -1);
      const A2 = [FF, 0], B2 = [W - FF, CAP], dt = band2(A2, B2, r.t, 1);
      P(poly('Chéo dày', bandPts(A1, B1, dT, 0, CAP))); P(poly('Chéo mảnh', bandPts(A2, B2, dt, 0, CAP)));
      diagFlares(A1, B1, dT, CAP, 'đỉnh trái'); diagFlares(A1, B1, dT, 0, 'chân phải');
      diagFlares(A2, B2, dt, 0, 'chân trái'); diagFlares(A2, B2, dt, CAP, 'đỉnh phải'); },
    Y() { const yj = 0.47 * CAP, xs = W / 2 - r.V / 2;
      stem(xs, 0, yj + 3); stemFlares(xs, xs + r.V, 0);
      const dl = nrm(sub([xs, yj], [FF, CAP])), dr = nrm(sub([xs + r.V, yj], [W - FF, CAP]));
      const il = add([FF, CAP], mul(perp(dl)[0] > 0 ? perp(dl) : mul(perp(dl), -1), r.D));
      const ir = add([W - FF, CAP], mul(perp(dr)[0] < 0 ? perp(dr) : mul(perp(dr), -1), r.t));
      const hull = polyC([[FF, CAP], [xs, yj], [xs, yj - 80], [xs + r.V, yj - 80], [xs + r.V, yj], [W - FF, CAP]]);
      P(poly('Tay trái', bandPts([FF, CAP], il, dl, yj - 80, CAP), { clip: hull }));
      P(poly('Tay phải', bandPts([W - FF, CAP], ir, dr, yj - 80, CAP), { clip: hull }));
      diagFlares([FF, CAP], il, dl, CAP, 'tay trái'); diagFlares([W - FF, CAP], ir, dr, CAP, 'tay phải'); },
    K() { const xs = x0 + r.V, yk = 0.30 * CAP;
      stem(x0); stemFlares(x0, x0 + r.V, 0); stemFlares(x0, x0 + r.V, CAP);
      const Ta = [W - FF - 30, CAP], da = nrm(sub(Ta, [xs, yk])); const ia = add([xs, yk], mul(perp(da)[0] > 0 ? perp(da) : mul(perp(da), -1), r.t));
      // tay mảnh: mép trên đi qua (xs, yk) và mũi trên cap
      P(poly('Tay', bandPts([xs, yk], ia, da, yk - 60, CAP), { clip: rectC(xs - 3, 0, W, CAP) }));
      diagFlares([xs, yk], ia, da, CAP, 'tay');
      // chân dày: mép phải qua chân (W−FF, 0) và mọc từ tâm tay
      const am = [xAt(add([xs, yk], mul(sub(ia, [xs, yk]), 0.5)), da, 0.52 * CAP), 0.52 * CAP];
      const dl = band2([W - FF, 0], am, r.D / 2, 1);
      const Lr = [W - FF, 0], Ll = add(Lr, mul(perp(dl)[0] < 0 ? perp(dl) : mul(perp(dl), -1), r.D));
      const armUpper = polyC([[xs - 3, 0], [W, 0], [W, CAP], [xAt([xs, yk], da, CAP), CAP], [xs - 3, yk]]);
      P(poly('Chân', bandPts(Lr, Ll, dl, 0, 0.6 * CAP), { clip: armUpper }));
      diagFlares(Lr, Ll, dl, 0, 'chân'); },
    O() { const R = W / 2, c = [W / 2, CAP / 2]; ring('Vòng', c, R, R, R - r.Vr, CAP / 2 + OVS - (r.Hb - 6), 30 * DEG); },
    Q() { const R = 723 / 2, c = [R, CAP / 2]; ring('Vòng', c, R, R, R - r.Vr, CAP / 2 + OVS - (r.Hb - 6), 30 * DEG);
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
    B() { stem(x0); stemFlares(x0, x0 + r.V, 0, true, false); stemFlares(x0, x0 + r.V, CAP, true, false);
      const yj = 0.56 * CAP; bowl('Bụng dưới', x0 + r.V, 0, yj + r.Hb / 2, W); bowl('Bụng trên', x0 + r.V, yj - r.Hb / 2, CAP, x0 + r.V + 0.80 * (W - x0 - r.V)); },
    P(isR) { stem(x0); stemFlares(x0, x0 + r.V, CAP, true, false); stemFlares(x0, x0 + r.V, 0);
      const yb = 0.47 * CAP, xr = isR ? x0 + r.V + 0.82 * (W - x0 - r.V - FF) : W; bowl('Bụng', x0 + r.V, yb, CAP, xr);
      if (isR) { const Fr = [W - FF, 0], Tq = [x0 + r.V + 0.62 * (xr - x0 - r.V), yb + r.Hb], dl = nrm(sub(Tq, Fr));
        const Fl = add(Fr, mul(perp(dl)[0] < 0 ? perp(dl) : mul(perp(dl), -1), r.D));
        P(poly('Chân', bandPts(Fr, Fl, dl, 0, yb + r.Hb), { clip: rectC(x0 + r.V - 3, 0, W, yb + r.Hb / 2) })); diagFlares(Fr, Fl, dl, 0, 'chân'); } },
    R() { B.P(true); },
    U() { const xr = W - FF - r.V, yu = 0.33 * CAP, cx = W / 2, rxo = cx - FF, ryo = yu + OVS;
      stem(x0, yu - 3, CAP, 'Thân trái'); stem(xr, yu - 3, CAP, 'Thân phải'); stemFlares(x0, x0 + r.V, CAP); stemFlares(xr, xr + r.V, CAP);
      P({ name: 'Bụng U', cmds: ellC([cx, yu], rxo, ryo), minus: ellC([cx, yu], rxo - r.V, yu - r.Hb), clip: rectC(0, -100, W, yu) }); G({ type: 'center', c: [cx, yu] }); },
    J() { const xs = W - FF - r.V, yu = 0.30 * CAP, rxo = (W - FF - FF) / 2, cx = FF + rxo;
      stem(xs, yu - 3, CAP); stemFlares(xs, xs + r.V, CAP);
      P({ name: 'Móc J', cmds: ellC([cx, yu], rxo, yu + OVS), minus: ellC([cx + 0.12 * r.V, yu], rxo - 0.70 * r.V, yu - r.Hb), clip: polyC([[FF + 0.12 * rxo, yu], [W, yu], [W, -100], [FF + 0.12 * rxo, -100]]) });
      G({ type: 'center', c: [cx, yu] }); G({ type: 'cut', x: FF + 0.12 * rxo }); },
    S() { // S1: hai vòng (đường tâm) tiếp xúc tại T; thành phía T dày Sp/2 → sống = Sp; đỉnh/đáy = Hb; nén ngang hệ số k
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
    Z() { const A1 = [W, CAP], B1 = [0, 0], d = band2(A1, B1, r.D, 1);
      P(rect('Thanh trên', 12, CAP - r.Hb, W, CAP)); beak('Mỏ trái', 12, CAP - r.Hb, true, 1);
      P(rect('Thanh dưới', 0, 0, W - 12, r.Hb)); beak('Mỏ phải', W - 12, r.Hb, false, -1);
      P(poly('Chéo', bandPts(A1, B1, d, 0, CAP), { clip: rectC(0, 0, W, CAP) })); G({ type: 'apex', p: A1, d1: [0, -1], d2: mul(d, d[1] < 0 ? 1 : -1) }); },
    // ---------------- bộ số (F1)
    '0'() { const c = [W / 2, CAP / 2]; ring('Vòng', c, W / 2, CAP / 2 + OVS, W / 2 - r.V, CAP / 2 + OVS - r.Hb - 4, 15 * DEG); },
    '1'() { const xs = W - FF - r.V; stem(xs, 0, CAP); stemFlares(xs, xs + r.V, 0);
      flare('Cờ', [xs, CAP], [0, -1], [-1, 0], [0, CAP - 120]); },
    '8'() { const cU = [W / 2, CAP + OVS - 0.235 * (CAP + 2 * OVS)], cL = [W / 2, -OVS + 0.285 * (CAP + 2 * OVS)];
      const ryU = 0.235 * (CAP + 2 * OVS), ryL = 0.285 * (CAP + 2 * OVS);
      ring('Vòng trên', cU, 0.42 * W, ryU, 0.42 * W - 0.9 * r.V, ryU - r.Hb, 15 * DEG);
      ring('Vòng dưới', cL, 0.5 * W, ryL, 0.5 * W - r.V, ryL - r.Hb, 15 * DEG); },
    '6'() { // bụng (vòng đủ) + nét lên = vòng lớn cắt; hai lòng đứng để thành trái liền một mạch
      const ryL = 0.31 * (CAP + 2 * OVS), cL = [W / 2, -OVS + ryL], c = [W / 2, CAP / 2];
      ring('Bụng', cL, W / 2, ryL, W / 2 - r.V, ryL - r.Hb, 0);
      const xt = W / 2 + 0.55 * (W / 2);
      P({ name: 'Nét lên', cmds: ellC(c, W / 2, CAP / 2 + OVS), minus: ellC(c, W / 2 - r.V, CAP / 2 + OVS - r.Hb),
        clip: polyC([[-100, cL[1]], [W / 2, cL[1]], [W / 2, c[1]], [xt, c[1]], [xt, CAP + 100], [-100, CAP + 100]]) });
      G({ type: 'center', c }); G({ type: 'cut', x: xt }); },
    '9'() { B['6'](); for (const s of parts) for (const k of ['cmds', 'minus', 'clip']) if (s[k]) s[k] = rot180(s[k], W);
      for (const g of guides) { for (const k of ['c', 'T', 'tip', 'p']) if (g[k]) g[k] = [W - g[k][0], CAP - g[k][1]]; if (g.type === 'cut') g.x = W - g.x; if (g.type === 'axis') g.rot += Math.PI; } },
    '3'(five) { const ryL = 0.36 * (CAP + 2 * OVS), cL = [W / 2, -OVS + ryL], rx = W / 2, xt = cL[0] - 0.80 * rx;
      const open = five ? 150 * DEG : 140 * DEG, inner = ellC(cL, rx - r.V, ryL - r.Hb, 15 * DEG);
      P({ name: 'Bụng', cmds: ellC(cL, rx, ryL), minus: inner,
        clip: polyC([[xt, cL[1]], [xt, cL[1] - 1000], [2000, cL[1] - 1000], [2000, cL[1] + 1000], add(cL, [1000 * Math.cos(open), 1000 * Math.sin(open)]), cL]) });
      G({ type: 'center', c: cL }); G({ type: 'cut', x: xt });
      const onB = a => [cL[0] + rx * Math.cos(a * DEG), cL[1] + ryL * Math.sin(a * DEG)], left = (p, q) => p[0] < q[0];
      if (!five) { P(rect('Thanh trên', 30, CAP - r.Hf, W - 8, CAP)); beak('Mỏ trái', 30, CAP - r.Hf, true, 1);
        const X = [0.55 * W, CAP - r.Hf], Tp = tangentPt(X, cL, rx, ryL, left), d = nrm(sub(X, Tp));
        const nq = perp(d)[0] > 0 ? perp(d) : mul(perp(d), -1), Q = add(Tp, mul(nq, 0.9 * r.D));
        P(poly('Chéo', bandPts(Tp, Q, d, cL[1], CAP - r.Hf + 3), { clip: rectC(0, 0, W - 8, CAP), clip2: halfPlane(Tp, d), minus: inner }));
        G({ type: 'apex', p: Tp, d1: d, d2: mul(d, -1) }); }
      else { P(rect('Thanh trên', 34, CAP - r.Hf, W - 8, CAP)); beak('Mỏ phải', W - 8, CAP - r.Hf, true, -1);
        const top = [34, CAP], Bj = onB(140), d = nrm(sub(top, Bj)), q = add(Bj, mul(perp(d)[0] > 0 ? perp(d) : mul(perp(d), -1), r.t));
        const keep = polyC([[-1000, Bj[1]], [-1000, 2000], [2000, 2000], [2000, -1000], [Bj[0], -1000], [Bj[0], Bj[1]]]);
        P(poly('Thân 5', bandPts(Bj, q, d, Bj[1] - 60, CAP), { clip: rectC(0, 0, W, CAP), clip2: keep, minus: inner }));
        G({ type: 'apex', p: Bj, d1: d, d2: [Math.cos(140 * DEG), Math.sin(140 * DEG)] }); } },
    '5'() { B['3'](true); },
    '2'() { // cung trên + chéo tiếp tuyến với cung + thanh đáy
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
    '4'() { const yb = 0.30 * CAP, xs = W - 0.30 * W, d = nrm(sub([xs, CAP], [0, yb + r.Hf / 2]));
      const q = add([xs, CAP], mul(perp(d)[0] > 0 ? perp(d) : mul(perp(d), -1), r.t));
      const hull = polyC([[0, yb - r.Hf / 2 - 1], [xs, CAP], [W + 100, CAP], [W + 100, -100], [0, -100]]);
      stem(xs, 0, CAP); P(rect('Thanh', 0, yb - r.Hf / 2, W, yb + r.Hf / 2, { clip: hull })); parts[parts.length - 2].clip = hull;
      P(poly('Chéo', bandPts([xs, CAP], q, d, yb - r.Hf / 2, CAP), { clip: hull }));
      stemFlares(xs, xs + r.V, 0); beak('Mỏ phải', W, yb + r.Hf / 2, false, -1); },
    '7'() { P(rect('Thanh trên', 0, CAP - r.Hf, W, CAP)); beak('Mỏ trái', 0, CAP - r.Hf, true, 1);
      const A1 = [W, CAP], B1 = [0.18 * W, 0], d = band2(A1, B1, r.D, -1);
      P(poly('Chéo', bandPts(A1, B1, d, 0, CAP), { clip: rectC(0, 0, W, CAP) })); diagFlares(A1, B1, d, 0, 'chân'); },
  };
  function flipAll() { for (const s of parts) for (const k of ['cmds', 'minus', 'clip']) if (s[k]) s[k] = flipY(s[k]);
    for (const g of guides) { for (const k of ['c', 'T', 'tip', 'p']) if (g[k]) g[k] = [g[k][0], CAP - g[k][1]];
      if (g.type === 'compass') { g.a0 = -g.a0; g.a1 = -g.a1; } if (g.type === 'apex') { g.d1 = [g.d1[0], -g.d1[1]]; g.d2 = [g.d2[0], -g.d2[1]]; } } }
  function makeGlyphV(Wv, ox) { // V con cho W
    const sub = makeGlyphRaw('V', W8, Wv); for (const s of sub.parts) for (const k of ['cmds', 'minus', 'clip']) if (s[k]) s[k] = s[k].map(c => [c[0], ...c.slice(1).map(p => [p[0] + ox, p[1]])]);
    for (const g of sub.guides) for (const k of ['c', 'T', 'tip', 'p']) if (g[k]) g[k] = [g[k][0] + ox, g[k][1]]; return sub; }
  B[ch]();
  return { ch, W, parts, guides };
}
function makeGlyphRaw(ch, W8, Wover) { const save = WIDTH[W8][ch]; WIDTH[W8][ch] = Wover; const g = makeGlyph(ch, W8); WIDTH[W8][ch] = save; return g; }
const ALL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'.split('');
if (typeof module !== 'undefined') module.exports = { makeGlyph, ALL, RULES, WIDTH, CAP, OVS, arcCmds };
