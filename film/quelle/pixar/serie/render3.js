const { chromium } = require('playwright');
const { spawn } = require('child_process');
const FPS=30;
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+__dirname+'/5-zwei-minuten.html');
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(1000);
  const D=await p.evaluate(()=>window.FILM_DAUER);
  const total=Math.round(D*FPS);
  const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(FPS),'-i','-',
    '-vf','unsharp=5:5:0.42:5:5:0.0',
    '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-profile:v','high',
    '-x264-params','keyint=60:min-keyint=30','-an','-movflags','+faststart',
    'out/5-zwei-minuten-stumm.mp4'],{stdio:['pipe','ignore','ignore']});
  const fertig=new Promise((r,j)=>ff.on('close',c=>c===0?r():j(new Error('ffmpeg '+c))));
  const t0=Date.now();
  for(let i=0;i<total;i++){
    await p.evaluate(t=>window.render(t), i/FPS);
    const buf=await p.screenshot({type:'png'});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(i%600===0) console.log(`${i}/${total}  ${((Date.now()-t0)/1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await fertig; await b.close();
  console.log('Bilder fertig:', total);
})().catch(e=>{console.error('FEHLER:',e.message);process.exit(1);});
