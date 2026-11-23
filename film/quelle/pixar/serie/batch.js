const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const FPS=30;
const FILME=['1-status','2-die-970','3-deine-zahl'];
(async()=>{
  const b=await chromium.launch(); const meta={};
  for(const f of FILME){
    const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
    await p.goto('file://'+__dirname+'/'+f+'.html');
    await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(800);
    const m=await p.evaluate(()=>({dauer:window.FILM_DAUER,cuts:window.FILM_CUTS}));
    meta[f]=m;
    const total=Math.round(m.dauer*FPS);
    const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(FPS),'-i','-',
      '-vf','unsharp=5:5:0.45:5:5:0.0',
      '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-profile:v','high',
      '-x264-params','keyint=60:min-keyint=30','-an','-movflags','+faststart',
      `out/${f}-stumm.mp4`],{stdio:['pipe','ignore','ignore']});
    const fertig=new Promise((r,j)=>ff.on('close',c=>c===0?r():j(new Error('ffmpeg '+c))));
    const t0=Date.now();
    for(let i=0;i<total;i++){
      await p.evaluate(t=>window.render(t), i/FPS);
      const buf=await p.screenshot({type:'png'});
      if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    }
    ff.stdin.end(); await fertig; await p.close();
    console.log(`${f}: ${m.dauer}s, Schnitte ${m.cuts.join(', ')} (${((Date.now()-t0)/1000).toFixed(0)}s)`);
  }
  await b.close();
  fs.writeFileSync('out/meta.json', JSON.stringify(meta,null,1));
})().catch(e=>{console.error('FEHLER:',e.message);process.exit(1);});
