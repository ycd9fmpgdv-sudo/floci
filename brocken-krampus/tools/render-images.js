// Pre-renders every painted scene of the site into img/*.webp.
// Run from this folder:  node render-images.js
// Needs Playwright with Chromium. Writes ../img/ and ../img/meta.json.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, '..', 'img');
const SCENES = [
  ['hero-l', 'hero', 1920, 1200], ['hero-p', 'hero', 900, 1950],
  ['full', 'full', 900, 1125], ['face', 'face', 900, 1125], ['horns', 'horns', 900, 1125],
  ['hands', 'hands', 1200, 800], ['trees', 'trees', 1200, 800], ['summit', 'summit', 1200, 800],
  ['gaze', 'gaze', 1920, 1080], ['gaze-p', 'gaze', 900, 1125],
  ['portrait', 'portrait', 800, 1000], ['witch', 'witch', 800, 1000], ['forester', 'forester', 800, 1000]
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
  await page.goto('file://' + path.join(__dirname, 'studio.html'));
  await page.waitForFunction(() => window.__studio);
  const save = async (name, expr, q) => {
    const data = await page.evaluate(expr);
    fs.writeFileSync(path.join(OUT, name + '.webp'), Buffer.from(data.split(',')[1], 'base64'));
  };
  const meta = { hero: {}, viewer: {} };
  for (const [name, scene, w, h] of SCENES) {
    const m = await page.evaluate(([scene, w, h]) => {
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const r = window.__studio.SCENES[scene](c.getContext('2d'), w, h);
      window.__last = c; return r || null;
    }, [scene, w, h]);
    await save(name, () => window.__last.toDataURL('image/webp', 0.8));
    if (scene === 'hero') { meta.hero[name] = { w, h, place: m.place, light: m.light, moon: m.moon }; }
    console.log('rendered', name);
  }
  for (const [v, w, h] of [['l', 1600, 1000], ['p', 900, 1125]]) {
    const m = await page.evaluate(([w, h]) => { window.__v = window.__studio.viewer(w, h); return window.__v.meta; }, [w, h]);
    meta.viewer[v] = m;
    for (const layer of ['bg', 'body', 'head', 'fore']) { await save(`viewer-${v}-${layer}`, `window.__v.${layer}.toDataURL('image/webp', ${layer === 'bg' ? 0.8 : 0.85})`); }
    console.log('rendered viewer', v);
  }
  for (const L of [0, 1, 2]) { await save('forest-' + L, `window.__studio.forest(${L}, 1600, 300).toDataURL('image/webp', 0.85)`); }
  await save('sprite-monster', `window.__studio.monster().toDataURL('image/webp', 0.85)`);
  fs.writeFileSync(path.join(OUT, 'meta.json'), JSON.stringify(meta, null, 1));
  await browser.close();
})();
