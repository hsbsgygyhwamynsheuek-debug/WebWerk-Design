const { chromium } = require('playwright');
const { spawn } = require('child_process');
const FPS = 30;
const FILME = ['a-loop','b-quadrate','c-stroop','d-mathe','e-reaktion','f-fehler'];

(async () => {
  const b = await chromium.launch();
  for (const datei of FILME) {
    const p = await b.newPage({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 });
    await p.goto('file://' + __dirname + '/' + datei + '.html');
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);
    const dauer = await p.evaluate(() => window.FILM_DAUER);
    const total = Math.round(dauer * FPS);
    const out = `out/tiktok-${datei}.mp4`;
    const ff = spawn('ffmpeg', ['-y','-f','image2pipe','-framerate',String(FPS),'-i','-',
      '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-profile:v','high',
      '-x264-params','keyint=60:min-keyint=30','-an','-movflags','+faststart', out],
      { stdio:['pipe','ignore','ignore'] });
    const fertig = new Promise((r,j)=>ff.on('close',c=>c===0?r():j(new Error('ffmpeg '+c))));
    const t0 = Date.now();
    for (let i = 0; i < total; i++) {
      await p.evaluate(t => window.render(t), i / FPS);
      const buf = await p.screenshot({ type:'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await fertig; await p.close();
    console.log(`${datei}: ${dauer}s, ${total} Bilder (${((Date.now()-t0)/1000).toFixed(0)}s)`);
  }
  await b.close();
})().catch(e=>{console.error('FEHLER:',e.message);process.exit(1);});
