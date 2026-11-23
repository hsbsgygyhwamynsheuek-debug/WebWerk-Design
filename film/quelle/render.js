const { chromium } = require('playwright');
const { spawn } = require('child_process');
const FPS = 30;

async function renderFormat({ name, w, h, port, out }) {
  const b = await chromium.launch({ args: ['--force-color-profile=srgb','--disable-lcd-text'] });
  const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  await p.goto('file://' + __dirname + '/film.html');
  if (port) await p.evaluate(() => document.getElementById('stage').className = 'port');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);

  const dauer = await p.evaluate(() => window.FILM_DAUER);
  const total = Math.round(dauer * FPS);

  const ff = spawn('ffmpeg', [
    '-y','-f','image2pipe','-framerate',String(FPS),'-i','-',
    '-c:v','libx264','-preset','slow','-crf','17',
    '-pix_fmt','yuv420p','-profile:v','high','-level','4.2',
    '-x264-params','keyint=60:min-keyint=30',
    '-movflags','+faststart', out
  ], { stdio: ['pipe','ignore','pipe'] });
  let ffErr = '';
  ff.stderr.on('data', d => { ffErr += d.toString(); if (ffErr.length > 8000) ffErr = ffErr.slice(-4000); });
  const done = new Promise((res, rej) =>
    ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg ' + c + '\n' + ffErr))));

  const t0 = Date.now();
  for (let f = 0; f < total; f++) {
    await p.evaluate(t => window.render(t), f / FPS);
    const buf = await p.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 120 === 0) {
      const s = (Date.now() - t0) / 1000;
      console.log(`${name}: ${f}/${total}  ${s.toFixed(0)}s`);
    }
  }
  ff.stdin.end();
  await done;
  await b.close();
  console.log(`${name}: fertig -> ${out}  (${((Date.now()-t0)/1000).toFixed(0)}s)`);
}

(async () => {
  const only = process.argv[2];
  if (only !== 'port')
    await renderFormat({ name:'quer',  w:1920, h:1080, port:false, out:'webwerk-film-16-9.mp4' });
  if (only !== 'land')
    await renderFormat({ name:'hoch',  w:1080, h:1920, port:true,  out:'webwerk-film-9-16.mp4' });
})().catch(e => { console.error('FEHLER:', e.message); process.exit(1); });
