const { chromium } = require('playwright');
(async () => {
  const times = process.argv.slice(3).map(Number);
  const port = process.argv[2] === 'port';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: port ? {width:1080,height:1920} : {width:1920,height:1080}, deviceScaleFactor: 1 });
  await p.goto('file://' + __dirname + '/film.html');
  if (port) await p.evaluate(() => document.getElementById('stage').className = 'port');
  await p.waitForTimeout(400);
  for (const t of times) {
    await p.evaluate(t => window.render(t), t);
    await p.waitForTimeout(60);
    const f = `probe/${port?'p':'l'}_${String(t).replace('.','-')}.png`;
    await p.screenshot({ path: f });
    console.log(f);
  }
  console.log('Dauer:', await p.evaluate(() => window.FILM_DAUER));
  await b.close();
})();
