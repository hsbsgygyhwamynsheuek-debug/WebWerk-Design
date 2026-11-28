const { chromium } = require('playwright');
const PLAN = [
  ['1-kurz',     [2.6, 5.0, 9.0, 13.5]],
  ['3-schritte', [1.8, 5.0, 12.5, 18.5]],
  ['4-woche',    [1.8, 8.0, 11.5, 15.5]],
  ['7-1998',     [4.0, 8.5, 12.5, 16.5]],
  ['8-ausreden', [1.8, 7.0, 14.0, 17.5]],
];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
  let i = 0;
  for (const [film, times] of PLAN) {
    await p.goto('file://' + __dirname + '/' + film + '.html');
    await p.evaluate(() => document.getElementById('stage').className = 'port');
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(250);
    for (const t of times) {
      await p.evaluate(t => window.render(t), t);
      await p.waitForTimeout(40);
      await p.screenshot({ path: `probep/${String(++i).padStart(2,'0')}_${film}_${t}.png` });
    }
  }
  await b.close();
})();
