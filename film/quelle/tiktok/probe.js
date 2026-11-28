const { chromium } = require('playwright');
const PLAN = [
  ['a-loop',     [0.0, 2.0, 4.0, 8.0]],
  ['b-quadrate', [0.9, 4.0, 8.5, 12.4]],
  ['c-stroop',   [1.0, 3.0, 7.0, 12.4]],
  ['d-mathe',    [1.5, 5.5, 8.8, 11.5]],
  ['e-reaktion', [0.9, 3.0, 4.6, 7.5]],
  ['f-fehler',   [1.4, 4.5, 7.6, 9.5]],
];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
  let i=0;
  for (const [film, times] of PLAN) {
    await p.goto('file://' + __dirname + '/' + film + '.html');
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(250);
    console.log(film, 'Dauer', await p.evaluate(()=>window.FILM_DAUER));
    for (const t of times) {
      await p.evaluate(t => window.render(t), t);
      await p.waitForTimeout(40);
      await p.screenshot({ path:`probe/${String(++i).padStart(2,'0')}_${film}_${t}.png` });
    }
  }
  await b.close();
})();
