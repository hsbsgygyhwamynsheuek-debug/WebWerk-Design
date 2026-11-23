const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const FPS = 30;

const FILME = [
  { d:'1-kurz',     f:['quer','hoch'] },
  { d:'2-leistung', f:['quer'] },
  { d:'3-schritte', f:['quer','hoch'] },
  { d:'4-woche',    f:['quer','hoch'] },
  { d:'5-ki-bau',   f:['quer'] },
  { d:'6-strich',   f:['quer'] },
  { d:'7-1998',     f:['quer','hoch'] },
  { d:'8-ausreden', f:['quer','hoch'] },
];

async function einFilm(browser, datei, format) {
  const hoch = format === 'hoch';
  const w = hoch ? 1080 : 1920, h = hoch ? 1920 : 1080;
  const out = `out/${datei}-${hoch ? '9-16' : '16-9'}-stumm.mp4`;
  const p = await browser.newPage({ viewport:{width:w,height:h}, deviceScaleFactor:1 });
  await p.goto('file://' + __dirname + '/' + datei + '.html');
  if (hoch) await p.evaluate(() => document.getElementById('stage').className = 'port');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);

  const meta = await p.evaluate(() => ({ dauer: window.FILM_DAUER, cuts: window.FILM_SZ.map(s => s.a) }));
  const total = Math.round(meta.dauer * FPS);

  const ff = spawn('ffmpeg', ['-y','-f','image2pipe','-framerate',String(FPS),'-i','-',
    '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
    '-profile:v','high','-x264-params','keyint=60:min-keyint=30',
    '-movflags','+faststart', out], { stdio:['pipe','ignore','ignore'] });
  const fertig = new Promise((res,rej)=>ff.on('close',c=>c===0?res():rej(new Error('ffmpeg '+c))));

  for (let i = 0; i < total; i++) {
    await p.evaluate(t => window.render(t), i / FPS);
    const buf = await p.screenshot({ type:'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await fertig;
  await p.close();
  return meta;
}

(async () => {
  const b = await chromium.launch();
  const metas = {};
  for (const film of FILME) {
    for (const fmt of film.f) {
      const t0 = Date.now();
      metas[film.d] = await einFilm(b, film.d, fmt);
      console.log(`${film.d} ${fmt}: fertig (${((Date.now()-t0)/1000).toFixed(0)}s)`);
    }
  }
  await b.close();
  fs.writeFileSync('out/meta.json', JSON.stringify(metas, null, 1));
  console.log('alle Bilder fertig');
})().catch(e => { console.error('FEHLER:', e.message); process.exit(1); });
