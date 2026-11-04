// node tools/construct/export.js > out/construct/parts.json
const { makeGlyph, ALL } = require('./glyphs.js');
const out = {};
for (const w of ['Regular', 'Bold']) for (const ch of ALL) { try { out[`${ch}-${w}`] = makeGlyph(ch, w); } catch (e) { out[`${ch}-${w}`] = { error: String(e.stack || e) }; } }
process.stdout.write(JSON.stringify(out));
