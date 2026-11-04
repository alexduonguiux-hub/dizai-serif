// Đìzai Serif v0.3 — bộ dựng hình theo quy tắc, chạy trong Figma (use_figma).
// Cùng công thức với tools/construct/dizai.py. Glyph = Boolean của các phần có tên.
// Đặt WEIGHT, LIST, GRID_ID ở đầu khi chạy.
const CAP = 700, OVS = 12, S = 247 / 700, PAD = 60, TOP = 120, BOT = 140;
const RULES = { Regular: { V: 102, Vr: 106, D: 100, t: 44, Hb: 40 }, Bold: { V: 139, Vr: 146, D: 146, t: 74, Hb: 68 } };
const WIDTH = {
  Regular: { H: 499, I: 148, E: 374, T: 397, L: 408, N: 499, A: 672, V: 672, O: 723, D: 558 },
  Bold: { H: 541, I: 185, E: 422, T: 445, L: 456, N: 555, A: 695, V: 695, O: 723, D: 609 } };
const FR = 112, FF = 23, BEAK = 54, APEX = 20, SLANT = 26 * Math.PI / 180, BAR_H = 0.53, BAR_A = 0.255, KAP = 0.5523, KIN = 0.60;
const add = (a, b) => [a[0] + b[0], a[1] + b[1]], sub = (a, b) => [a[0] - b[0], a[1] - b[1]], mul = (a, k) => [a[0] * k, a[1] * k];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1], nrm = a => mul(a, 1 / Math.hypot(a[0], a[1])), perp = a => [-a[1], a[0]];
const xAt = (p, d, y) => p[0] + d[0] * (y - p[1]) / d[1];
const poly = (name, pts, o = {}) => Object.assign({ name, cmds: [['M', pts[0]], ...pts.slice(1).map(p => ['L', p]), ['Z']] }, o);
const rect = (name, x0, y0, x1, y1, o) => poly(name, [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], o);
function arcCmds(c, r, a0, a1) {
  const n = Math.max(1, Math.ceil(Math.abs(a1 - a0) / (Math.PI / 2))), da = (a1 - a0) / n, out = [];
  for (let i = 0; i < n; i++) {
    const s = a0 + i * da, e = s + da, k = 4 / 3 * Math.tan(da / 4) * r;
    const p0 = [c[0] + r * Math.cos(s), c[1] + r * Math.sin(s)], p3 = [c[0] + r * Math.cos(e), c[1] + r * Math.sin(e)];
    out.push(['C', [p0[0] - k * Math.sin(s), p0[1] + k * Math.cos(s)], [p3[0] + k * Math.sin(e), p3[1] - k * Math.cos(e)], p3]);
  }
  return out;
}
function ellipse(name, c, rx, ry, rot, kappa, o) {
  const ca = Math.cos(rot), sa = Math.sin(rot), tf = (x, y) => [c[0] + x * ca - y * sa, c[1] + x * sa + y * ca], kx = kappa * rx, ky = kappa * ry;
  return Object.assign({ name, cmds: [['M', tf(rx, 0)], ['C', tf(rx, ky), tf(kx, ry), tf(0, ry)], ['C', tf(-kx, ry), tf(-rx, ky), tf(-rx, 0)],
    ['C', tf(-rx, -ky), tf(-kx, -ry), tf(0, -ry)], ['C', tf(kx, -ry), tf(rx, -ky), tf(rx, 0)], ['Z']] }, o || {});
}
function halfRight(name, cx, cy, rx, ry, kappa, ext, o) {
  const kx = kappa * rx, ky = kappa * ry;
  return Object.assign({ name, cmds: [['M', [cx - ext, cy - ry]], ['L', [cx, cy - ry]], ['C', [cx + kx, cy - ry], [cx + rx, cy - ky], [cx + rx, cy]],
    ['C', [cx + rx, cy + ky], [cx + kx, cy + ry], [cx, cy + ry]], ['L', [cx - ext, cy + ry]], ['Z']] }, o || {});
}
function makeGlyph(ch, W8) {
  const r = RULES[W8], W = WIDTH[W8][ch], parts = [], guides = [];
  const P = s => (parts.push(s), s);
  function flare(name, Eg, u, n, Pt, rad = FR) {
    const w = sub(Pt, Eg), uw = dot(u, w), nw = dot(n, w), s = uw + Math.sqrt(uw * uw - dot(w, w) + 2 * rad * nw);
    const T = add(Eg, mul(u, s)), C = add(T, mul(n, rad));
    const a0 = Math.atan2(Pt[1] - C[1], Pt[0] - C[0]); let d = Math.atan2(T[1] - C[1], T[0] - C[0]) - a0;
    while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI;
    P({ name, cmds: [['M', add(Eg, mul(n, -3))], ['L', Pt], ...arcCmds(C, rad, a0, a0 + d), ['L', add(T, mul(n, -3))], ['Z']] });
    guides.push({ type: 'compass', c: C, r: rad, a0, a1: a0 + d, T, tip: Pt });
  }
  const stem = (x0, y0 = 0, y1 = CAP, name, w) => P(rect(name || 'Thân', x0, y0, x0 + (w || r.V), y1));
  function stemFlares(x0, x1, y, L = true, R = true) {
    const u = y === 0 ? [0, 1] : [0, -1], tag = y === 0 ? 'chân' : 'đỉnh';
    if (L) flare(`Loe ${tag} trái`, [x0, y], u, [-1, 0], [x0 - FF, y]);
    if (R) flare(`Loe ${tag} phải`, [x1, y], u, [1, 0], [x1 + FF, y]);
  }
  function diagFlares(pa, pb, d, y, name) {
    const u = (d[1] > 0) === (y === 0) ? d : mul(d, -1);
    let ea = [xAt(pa, d, y), y], eb = [xAt(pb, d, y), y]; if (ea[0] > eb[0]) [ea, eb] = [eb, ea];
    const nl = perp(u)[0] < 0 ? perp(u) : mul(perp(u), -1);
    flare(`Loe ${name} trái`, ea, u, nl, [ea[0] - FF, y]); flare(`Loe ${name} phải`, eb, u, mul(nl, -1), [eb[0] + FF, y]);
  }
  function beak(name, xEnd, yEdge, down) {
    const n = down ? [0, -1] : [0, 1], side = xEnd > W / 2 ? -1 : 1;
    flare(name, [xEnd, yEdge], [side, 0], n, [xEnd, yEdge + n[1] * BEAK]);
  }
  const yc = BAR_H * CAP;
  const G = {
    I() { const x = FF; stem(x); stemFlares(x, x + r.V, 0); stemFlares(x, x + r.V, CAP); },
    H() { const xl = FF, xr = W - FF - r.V; stem(xl, 0, CAP, 'Thân trái'); stem(xr, 0, CAP, 'Thân phải');
      P(rect('Thanh', xl + r.V - 3, yc - r.Hb / 2, xr + 3, yc + r.Hb / 2)); for (const x of [xl, xr]) { stemFlares(x, x + r.V, 0); stemFlares(x, x + r.V, CAP); } },
    E() { const x = FF, a = x + r.V - 3; stem(x); stemFlares(x, x + r.V, 0, true, false); stemFlares(x, x + r.V, CAP, true, false);
      P(rect('Tay trên', a, CAP - r.Hb, W, CAP)); P(rect('Tay dưới', a, 0, W, r.Hb));
      P(poly('Tay giữa', [[a, yc - r.Hb / 2], [W, yc - r.Hb / 2], [W - r.Hb * Math.tan(SLANT), yc + r.Hb / 2], [a, yc + r.Hb / 2]]));
      beak('Mỏ tay trên', W, CAP - r.Hb, true); beak('Mỏ tay dưới', W, r.Hb, false); },
    L() { const x = FF; stem(x); stemFlares(x, x + r.V, CAP); stemFlares(x, x + r.V, 0, true, false);
      P(rect('Tay dưới', x + r.V - 3, 0, W, r.Hb)); beak('Mỏ tay dưới', W, r.Hb, false); },
    T() { P(rect('Thanh trên', 0, CAP - r.Hb, W, CAP)); const x = W / 2 - r.V / 2; stem(x, 0, CAP - r.Hb + 3); stemFlares(x, x + r.V, 0);
      beak('Mỏ trái', 0, CAP - r.Hb, true); beak('Mỏ phải', W, CAP - r.Hb, true); },
    A(flip) { const xc = W / 2, yt = CAP + OVS, tl = [xc - APEX / 2, yt], tr = [xc + APEX / 2, yt], fl = [FF, 0], fr = [W - FF, 0];
      const [wl, wr] = flip ? [r.D, r.t] : [r.t, r.D];
      const leg = (name, foot, top, th, inward) => { const d = nrm(sub(top, foot)); const ni = (perp(d)[0] > 0) === (inward > 0) ? perp(d) : mul(perp(d), -1);
        const ip = add(foot, mul(ni, th)); return { name, d, foot, ip, pts: [[xAt(foot, d, 0), 0], [xAt(foot, d, yt), yt], [xAt(ip, d, yt), yt], [xAt(ip, d, 0), 0]] }; };
      const L = leg('Chân trái', fl, tl, wl, 1), R = leg('Chân phải', fr, tr, wr, -1);
      const hull = [[xAt(fl, L.d, -60), -60], tl, tr, [xAt(fr, R.d, -60), -60]];
      for (const g of [L, R]) P(Object.assign(poly(g.name, g.pts), { clip: poly('hull', hull).cmds }));
      diagFlares(L.foot, L.ip, L.d, 0, 'chân trái'); diagFlares(R.foot, R.ip, R.d, 0, 'chân phải');
      guides.push({ type: 'apex', p: [xc, yt], d1: mul(L.d, -1), d2: mul(R.d, -1) });
      if (!flip) { const y = BAR_A * CAP; P(rect('Thanh', xAt(L.ip, L.d, y) - 3, y - r.Hb / 2, xAt(R.ip, R.d, y) + 3, y + r.Hb / 2)); } },
    V() { G.A(true); const f = p => [p[0], CAP - p[1]];
      for (const s of parts) { s.cmds = s.cmds.map(c => [c[0], ...c.slice(1).map(f)]); if (s.clip) s.clip = s.clip.map(c => [c[0], ...c.slice(1).map(f)]); }
      for (const g of guides) { for (const k of ['c', 'T', 'tip', 'p']) if (g[k]) g[k] = f(g[k]);
        if (g.type === 'compass') { g.a0 = -g.a0; g.a1 = -g.a1; } if (g.type === 'apex') { g.d1 = [g.d1[0], -g.d1[1]]; g.d2 = [g.d2[0], -g.d2[1]]; } } },
    N() { // J2: thân mảnh phẳng trên đường kẻ; mép chéo đi qua góc trong của thân
      const s0 = FF, sR = W - FF; stem(s0, 0, CAP, 'Thân trái', r.t); stem(sR - r.t, 0, CAP, 'Thân phải', r.t);
      stemFlares(s0, s0 + r.t, 0); stemFlares(sR - r.t, sR, CAP);
      const P1 = [s0 + r.t, CAP], P2 = [sR - r.t, 0], v = sub(P2, P1), Lv = Math.hypot(v[0], v[1]);
      const ang = Math.atan2(v[1], v[0]) + Math.asin(r.D / Lv), d = [Math.cos(ang), Math.sin(ang)];
      let n = perp(d); if (dot(n, v) < 0) n = mul(n, -1); const bot = add(P1, mul(n, r.D));
      const pts = [[xAt(P1, d, CAP), CAP], [xAt(P1, d, 0), 0], [xAt(bot, d, 0), 0], [xAt(bot, d, CAP), CAP]];
      P(Object.assign(poly('Chéo', pts), { clip: rect('', s0, 0, sR, CAP).cmds }));
      guides.push({ type: 'apex', p: P1, d1: [0, -1], d2: d }); guides.push({ type: 'apex', p: P2, d1: [0, 1], d2: mul(d, -1) }); },
    O() { const R = W / 2, c = [W / 2, CAP / 2], rx = R - r.Vr, ry = CAP / 2 + OVS - (r.Hb - 6), rot = 30 * Math.PI / 180;
      P(ellipse('Vòng ngoài', c, R, R, 0, KAP)); P(ellipse('Lòng', c, rx, ry, rot, KAP, { counter: true }));
      guides.push({ type: 'center', c }); guides.push({ type: 'axis', c, len: ry * 1.1, rot: rot + Math.PI / 2 }); },
    D() { const x = FF; stem(x); stemFlares(x, x + r.V, 0, true, false); stemFlares(x, x + r.V, CAP, true, false);
      const xm = x + r.V + (W - x - r.V) * 0.25, xi = x + r.V;
      P(halfRight('Bụng ngoài', xm, CAP / 2, W - xm, CAP / 2, KAP, xm - xi + 3));
      P(halfRight('Lòng', xi, CAP / 2, W - r.Vr - xi, CAP / 2 - r.Hb, KIN, 0, { counter: true }));
      guides.push({ type: 'center', c: [xm, CAP / 2] }); guides.push({ type: 'center', c: [xi, CAP / 2] }); },
  };
  G[ch]();
  return { ch, W, parts, guides };
}
// ------------------------------------------------------------ Figma
const COL = { metric: [0.70, 0.68, 0.64], sb: [0.80, 0.78, 0.75], glyph: [0.90, 0.88, 0.85], ink: [0.11, 0.11, 0.11], red: [0.86, 0.29, 0.17], blue: [0.17, 0.41, 0.86], orange: [0.93, 0.52, 0.09], mute: [0.50, 0.48, 0.45] };
const rgb = a => ({ r: a[0], g: a[1], b: a[2] });
async function buildCell(grid, W8, ch) {
  const g = makeGlyph(ch, W8);
  const w = (g.W + 80 + 2 * PAD) * S, h = (CAP + TOP + BOT) * S;
  const fx = x => (x + 40 + PAD) * S, fy = y => (TOP + CAP - y) * S;
  const D = cmds => cmds.map(c => c[0] === 'Z' ? 'Z' : c[0] + ' ' + c.slice(1).map(p => fx(p[0]).toFixed(2) + ' ' + fy(p[1]).toFixed(2)).join(' ')).join(' ');
  const cell = figma.createFrame(); cell.name = `${ch} ${W8}`; cell.resize(w, h); cell.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]; cell.clipsContent = true; grid.appendChild(cell);
  function vec(name, d, par, stroke, sw, fill, dash) {
    const v = figma.createVector(); (par || cell).appendChild(v); v.name = name; v.x = 0; v.y = 0;
    v.vectorPaths = [{ windingRule: 'NONZERO', data: d }];
    const o = d.match(/^M\s+(-?[\d.]+)\s+(-?[\d.]+)/), q = v.vectorPaths[0].data.match(/^M\s+(-?[\d.e-]+)\s+(-?[\d.e-]+)/);
    v.relativeTransform = [[1, 0, (+o[1]) - (+q[1])], [0, 1, (+o[2]) - (+q[2])]];
    v.fills = fill ? [{ type: 'SOLID', color: rgb(fill) }] : []; v.strokes = stroke ? [{ type: 'SOLID', color: rgb(stroke) }] : []; v.strokeWeight = sw || 0.75; if (dash) v.dashPattern = dash; return v;
  }
  const line = (x1, y1, x2, y2, c, sw, dash) => vec('guide', `M ${x1.toFixed(2)} ${y1.toFixed(2)} L ${x2.toFixed(2)} ${y2.toFixed(2)}`, cell, c, sw, null, dash);
  for (const [y, dash] of [[CAP, null], [0, null], [CAP + OVS, [2, 3]], [-OVS, [2, 3]]]) line(0, fy(y), w, fy(y), COL.metric, dash ? 0.5 : 0.75, dash);
  for (const x of [-40, g.W + 40]) line(fx(x), fy(CAP + 70), fx(x), fy(-70), COL.sb, 0.75, [1, 3]);
  // --- glyph = boolean of named parts
  const addNodes = [];
  for (const s of g.parts.filter(s => !s.counter)) {
    let n = vec(s.name, D(s.cmds), cell, null, 0, [0, 0, 0]);
    if (s.clip) { const k = vec('giới hạn', D(s.clip), cell, null, 0, [0, 0, 0]); n = figma.intersect([n, k], cell); n.name = s.name; }
    addNodes.push(n);
  }
  let glyph = figma.union(addNodes, cell); glyph.name = 'cộng';
  const ctr = g.parts.filter(s => s.counter);
  if (ctr.length) { const cn = ctr.map(s => vec(s.name, D(s.cmds), cell, null, 0, [0, 0, 0])); glyph = figma.subtract([glyph, ...cn], cell); }
  glyph.name = `Glyph ${ch} (dựng)`; glyph.fills = [{ type: 'SOLID', color: rgb(COL.glyph) }]; glyph.strokes = [{ type: 'SOLID', color: rgb(COL.ink) }]; glyph.strokeWeight = 0.6;
  // --- red part outlines masked by the glyph
  const mask = glyph.clone(); cell.appendChild(mask); mask.fills = [{ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }]; mask.strokes = []; mask.isMask = true; mask.name = 'mask';
  const outl = g.parts.filter(s => !s.counter).map(s => vec(s.name, D(s.cmds), cell, COL.red, 0.8));
  const grp = figma.group([mask, ...outl], cell); grp.name = 'phần dựng';
  for (const s of ctr) vec(s.name, D(s.cmds), cell, COL.blue, 0.8);
  const ol = glyph.clone(); cell.appendChild(ol); ol.fills = []; ol.name = 'viền';
  // --- guides
  for (const q of g.guides) {
    if (q.type === 'compass') { const ext = 22 * Math.PI / 180 * (q.a1 > q.a0 ? 1 : -1);
      const cm = [['M', [q.c[0] + q.r * Math.cos(q.a0 - ext), q.c[1] + q.r * Math.sin(q.a0 - ext)]], ...arcCmds(q.c, q.r, q.a0 - ext, q.a1 + ext)];
      vec('vòng compa r ' + q.r, D(cm), cell, COL.orange, 0.6); line(fx(q.c[0]), fy(q.c[1]), fx(q.T[0]), fy(q.T[1]), COL.orange, 0.5, [2, 2]);
      const dt = figma.createEllipse(); cell.appendChild(dt); dt.resize(3.2, 3.2); dt.x = fx(q.c[0]) - 1.6; dt.y = fy(q.c[1]) - 1.6; dt.fills = [{ type: 'SOLID', color: rgb(COL.orange) }]; dt.name = 'tâm'; }
    else if (q.type === 'center') { const x = fx(q.c[0]), y = fy(q.c[1]); line(x - 5, y, x + 5, y, COL.blue, 0.75); line(x, y - 5, x, y + 5, COL.blue, 0.75); }
    else if (q.type === 'axis') { const c = q.c, L = q.len, a = q.rot; line(fx(c[0] + L * Math.cos(a)), fy(c[1] + L * Math.sin(a)), fx(c[0] - L * Math.cos(a)), fy(c[1] - L * Math.sin(a)), COL.blue, 0.6, [4, 3]); }
    else if (q.type === 'apex') { for (const d of [q.d1, q.d2]) line(fx(q.p[0]), fy(q.p[1]), fx(q.p[0] + d[0] * 110), fy(q.p[1] + d[1] * 110), COL.blue, 0.6, [4, 3]); }
  }
  const lab = (s, size, style, col, x, y) => { const t = figma.createText(); t.fontName = { family: 'Inter', style }; t.fontSize = size; t.characters = s; t.fills = [{ type: 'SOLID', color: rgb(col) }]; cell.appendChild(t); t.x = x; t.y = y; return t; };
  lab(ch, 20, 'Semi Bold', COL.ink, 14, 10);
  const u = lab('U+' + ch.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0'), 11, 'Regular', COL.mute, 0, 16); u.x = w - 14 - u.width;
  lab(`mực ${g.W} u · adv ${g.W + 80} u`, 11, 'Regular', COL.mute, 14, h - 24);
  return cell;
}
const pg = await figma.getNodeByIdAsync('2048:2'); await figma.setCurrentPageAsync(pg);
for (const st of ['Regular', 'Semi Bold']) await figma.loadFontAsync({ family: 'Inter', style: st });
const grid = await figma.getNodeByIdAsync(GRID_ID);
for (const ch of LIST) {
  const old = grid.children.find(c => c.name === `${ch} ${WEIGHT}`); const idx = old ? grid.children.indexOf(old) : -1;
  const cell = await buildCell(grid, WEIGHT, ch); if (old) { old.remove(); grid.insertChild(idx, cell); }
}
return { built: grid.children.length };
