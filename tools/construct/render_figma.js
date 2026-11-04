// Render glyphs.js vào Figma (nối sau glyphs.js; đặt JOBS = [[weight, gridId, [chars]]...]).
const S_ = 247 / 700, PAD_ = 60, TOP_ = 120, BOT_ = 160;
const COL = { metric: [0.70, 0.68, 0.64], sb: [0.80, 0.78, 0.75], glyph: [0.90, 0.88, 0.85], ink: [0.11, 0.11, 0.11], red: [0.86, 0.29, 0.17], blue: [0.17, 0.41, 0.86], orange: [0.93, 0.52, 0.09], mute: [0.50, 0.48, 0.45] };
const rgb = a => ({ r: a[0], g: a[1], b: a[2] });
async function buildCell(grid, W8, ch) {
  const g = makeGlyph(ch, W8);
  const ext = VN.includes(ch) || PUNCT.includes(ch); // chữ có dấu, dấu câu: ô cao hơn cho dấu (tới 1060) và phần dưới baseline (−200)
  const PADc = ext ? 120 : PAD_, TOPc = ext ? 400 : TOP_, BOTc = ext ? 260 : BOT_;
  const w = (g.W + 80 + 2 * PADc) * S_, h = (CAP + TOPc + BOTc) * S_;
  const fx = x => (x + 40 + PADc) * S_, fy = y => (TOPc + CAP - y) * S_;
  const D = cmds => cmds.map(c => c[0] === 'Z' ? 'Z' : c[0] + ' ' + c.slice(1).map(p => fx(p[0]).toFixed(2) + ' ' + fy(p[1]).toFixed(2)).join(' ')).join(' ');
  const cell = figma.createFrame(); cell.name = `${ch} ${W8}`; cell.resize(w, h); cell.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]; cell.clipsContent = true; grid.appendChild(cell);
  function vec(name, d, stroke, sw, fill, dash) {
    const v = figma.createVector(); cell.appendChild(v); v.name = name; v.x = 0; v.y = 0;
    v.vectorPaths = [{ windingRule: 'NONZERO', data: d }];
    const o = d.match(/^M\s+(-?[\d.]+)\s+(-?[\d.]+)/), q = v.vectorPaths[0].data.match(/^M\s+(-?[\d.e-]+)\s+(-?[\d.e-]+)/);
    v.relativeTransform = [[1, 0, (+o[1]) - (+q[1])], [0, 1, (+o[2]) - (+q[2])]];
    v.fills = fill ? [{ type: 'SOLID', color: rgb(fill) }] : []; v.strokes = stroke ? [{ type: 'SOLID', color: rgb(stroke) }] : []; v.strokeWeight = sw || 0.75; if (dash) v.dashPattern = dash; return v;
  }
  const line = (x1, y1, x2, y2, c, sw, dash) => vec('guide', `M ${x1.toFixed(2)} ${y1.toFixed(2)} L ${x2.toFixed(2)} ${y2.toFixed(2)}`, c, sw, null, dash);
  for (const [y, dash] of [[CAP, null], [0, null], [CAP + OVS, [2, 3]], [-OVS, [2, 3]], ...(ext ? [[750, [6, 3]], [-47.3, [6, 3]]] : [])]) line(0, fy(y), w, fy(y), COL.metric, dash ? 0.5 : 0.75, dash);
  for (const x of [-40, g.W + 40]) line(fx(x), fy(CAP + 70), fx(x), fy(-160), COL.sb, 0.75, [1, 3]);
  const BLK = [0, 0, 0];
  function partNode(s) {
    let n = vec(s.name, D(s.cmds), null, 0, BLK);
    if (s.minus) { n = figma.subtract([n, vec('lòng', D(s.minus), null, 0, BLK)], cell); }
    if (s.clip) { n = figma.intersect([n, vec('giới hạn', D(s.clip), null, 0, BLK)], cell); }
    if (s.clip2) { n = figma.intersect([n, vec('giới hạn', D(s.clip2), null, 0, BLK)], cell); }
    n.name = s.name; return n;
  }
  const adds = g.parts.filter(s => !s.counter && !s.post), ctr = g.parts.filter(s => s.counter), post = g.parts.filter(s => s.post);
  const addN = adds.map(partNode), overlay = addN.map(n => n.clone());
  let glyph = addN.length > 1 ? figma.union(addN, cell) : addN[0];
  if (ctr.length) glyph = figma.subtract([glyph, ...ctr.map(partNode)], cell);
  if (post.length) { const pn = post.map(partNode); overlay.push(...pn.map(n => n.clone())); glyph = figma.union([glyph, ...pn], cell); }
  glyph.name = `Glyph ${ch}`; glyph.fills = [{ type: 'SOLID', color: rgb(COL.glyph) }]; glyph.strokes = [{ type: 'SOLID', color: rgb(COL.ink) }]; glyph.strokeWeight = 0.6;
  const mask = glyph.clone(); cell.appendChild(mask); mask.fills = [{ type: 'SOLID', color: { r: 0, g: 0, b: 0 } }]; mask.strokes = []; mask.isMask = true; mask.name = 'mask';
  for (const o of overlay) { cell.appendChild(o); o.fills = []; o.strokes = [{ type: 'SOLID', color: rgb(COL.red) }]; o.strokeWeight = 0.8; }
  const grp = figma.group([mask, ...overlay], cell); grp.name = 'phần dựng';
  for (const s of ctr) vec(s.name, D(s.cmds), COL.blue, 0.8);
  const ol = glyph.clone(); cell.appendChild(ol); ol.fills = []; ol.name = 'viền';
  for (const q of g.guides) {
    if (q.type === 'compass') { const ext = 22 * Math.PI / 180 * (q.a1 > q.a0 ? 1 : -1);
      const cm = [['M', [q.c[0] + q.r * Math.cos(q.a0 - ext), q.c[1] + q.r * Math.sin(q.a0 - ext)]], ...arcCmds(q.c, q.r, q.a0 - ext, q.a1 + ext)];
      vec('vòng compa r ' + Math.round(q.r), D(cm), COL.orange, 0.6); line(fx(q.c[0]), fy(q.c[1]), fx(q.T[0]), fy(q.T[1]), COL.orange, 0.5, [2, 2]);
      const dt = figma.createEllipse(); cell.appendChild(dt); dt.resize(3.2, 3.2); dt.x = fx(q.c[0]) - 1.6; dt.y = fy(q.c[1]) - 1.6; dt.fills = [{ type: 'SOLID', color: rgb(COL.orange) }]; dt.name = 'tâm'; }
    else if (q.type === 'center') { const x = fx(q.c[0]), y = fy(q.c[1]); line(x - 5, y, x + 5, y, COL.blue, 0.75); line(x, y - 5, x, y + 5, COL.blue, 0.75); }
    else if (q.type === 'axis') { const c = q.c, L = q.len, a = q.rot; line(fx(c[0] + L * Math.cos(a)), fy(c[1] + L * Math.sin(a)), fx(c[0] - L * Math.cos(a)), fy(c[1] - L * Math.sin(a)), COL.blue, 0.6, [4, 3]); }
    else if (q.type === 'apex') { for (const d of [q.d1, q.d2]) line(fx(q.p[0]), fy(q.p[1]), fx(q.p[0] + d[0] * 110), fy(q.p[1] + d[1] * 110), COL.blue, 0.6, [4, 3]);
      const dt = figma.createEllipse(); cell.appendChild(dt); dt.resize(3.2, 3.2); dt.x = fx(q.p[0]) - 1.6; dt.y = fy(q.p[1]) - 1.6; dt.fills = [{ type: 'SOLID', color: rgb(COL.blue) }]; dt.name = 'điểm dựng'; }
    else if (q.type === 'cut') line(fx(q.x), fy(CAP + 50), fx(q.x), fy(-50), COL.blue, 0.6, [1, 2]);
    else if (q.type === 'ellipse') { const ca = Math.cos(q.rot), sa = Math.sin(q.rot), pts = [];
      for (let i = 0; i <= 72; i++) { const t = 2 * Math.PI * i / 72, x = q.rx * Math.cos(t), y = q.ry * Math.sin(t); pts.push([q.c[0] + x * ca - y * sa, q.c[1] + x * sa + y * ca]); }
      vec('elip dựng', 'M ' + pts.map(p => fx(p[0]).toFixed(2) + ' ' + fy(p[1]).toFixed(2)).join(' L ') + ' Z', COL.ink, 0.5);
      if (q.axes) for (const a of [q.rot, q.rot + Math.PI / 2]) { const L = 520, dx = Math.cos(a) * L, dy = Math.sin(a) * L; line(fx(q.c[0] - dx), fy(q.c[1] - dy), fx(q.c[0] + dx), fy(q.c[1] + dy), COL.ink, 0.4); } }
    else if (q.type === 'line') { const L = 900, p = q.p, d = q.d; line(fx(p[0] - d[0] * L), fy(p[1] - d[1] * L), fx(p[0] + d[0] * L), fy(p[1] + d[1] * L), COL.ink, 0.4); }
    else if (q.type === 'hline') line(0, fy(q.y), w, fy(q.y), COL.orange, 0.6);
    else if (q.type === 'circle') { const cm = [['M', [q.c[0] + q.r, q.c[1]]], ...arcCmds(q.c, q.r, 0, 2 * Math.PI)]; vec('vòng compa r ' + Math.round(q.r), D(cm), COL.orange, 0.5); }
    else if (q.type === 'handles') { const p = q.p; line(fx(p[0][0]), fy(p[0][1]), fx(p[1][0]), fy(p[1][1]), COL.mute, 0.5); line(fx(p[3][0]), fy(p[3][1]), fx(p[2][0]), fy(p[2][1]), COL.mute, 0.5); }
  }
  const lab = (s, size, style, col, x, y) => { const t = figma.createText(); t.fontName = { family: 'Inter', style }; t.fontSize = size; t.characters = s; t.fills = [{ type: 'SOLID', color: rgb(col) }]; cell.appendChild(t); t.x = x; t.y = y; return t; };
  lab(ch, 20, 'Semi Bold', COL.ink, 14, 10);
  const u = lab('U+' + ch.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0'), 11, 'Regular', COL.mute, 0, 16); u.x = w - 14 - u.width;
  lab(`mực ${g.W} u · adv ${g.W + 80} u` + (g.src === 'rule' ? (ext ? ' · TẠM (dựng theo luật S11/S15, chờ duyệt)' : ' · TẠM (chưa có bản vẽ)') : ''), 11, 'Regular', g.src === 'rule' ? COL.red : COL.mute, 14, h - 24);
  return cell;
}
for (const st of ['Regular', 'Semi Bold']) await figma.loadFontAsync({ family: 'Inter', style: st });
const pg = await figma.getNodeByIdAsync(PAGE_ID); await figma.setCurrentPageAsync(pg);
const done = [];
for (const [W8, gid, chars] of JOBS) {
  const grid = await figma.getNodeByIdAsync(gid);
  for (const ch of chars) {
    const old = grid.children.find(c => c.name === `${ch} ${W8}`); const idx = old ? grid.children.indexOf(old) : -1;
    const cell = await buildCell(grid, W8, ch); if (old) { old.remove(); grid.insertChild(idx, cell); } done.push(`${ch} ${W8}`);
  }
}
return { done: done.length };
