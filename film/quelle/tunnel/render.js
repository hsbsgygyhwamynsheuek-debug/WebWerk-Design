const { chromium } = require('playwright');
const { spawn } = require('child_process');
const FPS=30;
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+__dirname+'/tunnel.html'); await p.waitForTimeout(500);
  const D=await p.evaluate(()=>window.FILM_DAUER);
  const total=Math.round(D*FPS);
  const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(FPS),'-i','-',
    '-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-profile:v','high',
    '-x264-params','keyint=30:min-keyint=15','-an','-movflags','+faststart','tunnel-stumm.mp4'],
    {stdio:['pipe','ignore','ignore']});
  const fertig=new Promise((r,j)=>ff.on('close',c=>c===0?r():j(new Error('ffmpeg '+c))));
  for(let i=0;i<total;i++){
    await p.evaluate(t=>window.render(t), i/FPS);
    const buf=await p.screenshot({type:'png'});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
  }
  ff.stdin.end(); await fertig; await b.close();
  console.log('Bilder fertig:', total, 'bei', D,'s');
})().catch(e=>{console.error('FEHLER:',e.message);process.exit(1);});
