// Render showreel.html frame by frame to PNG.
// Usage: node render.js <outDir> [fps=30] [onlyTimes comma list]
// Requires a static server at http://localhost:8765 serving the repo root.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const out = process.argv[2] || 'frames';
  const fps = +(process.argv[3] || 30);
  const only = process.argv[4] ? process.argv[4].split(',').map(Number) : null;
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto('http://localhost:8765/showreel/showreel.html');
  await page.evaluate(() => window.ready);
  const stage = await page.$('#stage');
  const times = only || Array.from({ length: Math.round(10 * fps) }, (_, i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(t => window.render(t), times[i]);
    const name = only ? `t${times[i].toFixed(2)}.png` : `f${String(i).padStart(4, '0')}.png`;
    await stage.screenshot({ path: `${out}/${name}` });
  }
  await browser.close();
})();
