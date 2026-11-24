/* node dreh.js <Ordner> probe 1.0 3.2 ...   |   node dreh.js <Ordner> render */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs=require('fs'), path=require('path');
const [ordner, modus, ...zeiten] = process.argv.slice(2);
(async()=>{
  const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  p.on('pageerror',e=>console.log('SEITENFEHLER:',e.message));
  await p.goto('file://'+path.resolve(ordner,'seite.html'));
  await p.waitForFunction(()=>window.bereit===true,{timeout:90000});
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(500);
  const D=await p.evaluate(()=>window.FILM_DAUER);
  if(modus==='probe'){
    fs.mkdirSync(path.join(ordner,'probe'),{recursive:true});
    const T = zeiten.length? zeiten.map(Number) : [0.6,D*0.2,D*0.35,D*0.5,D*0.65,D*0.8,D-1.0];
    let i=0; for(const t of T){ await p.evaluate(t=>window.render(t),t); await p.waitForTimeout(50);
      await p.screenshot({path:path.join(ordner,'probe',`${String(++i).padStart(2,'0')}.png`)}); }
    console.log('Proben', i, 'Dauer', D);
  } else {
    const FPS=30,total=Math.round(D*FPS), stumm=path.join(ordner,'stumm.mp4');
    const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(FPS),'-i','-','-vf','unsharp=5:5:0.40:5:5:0.0',
      '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-profile:v','high',
      '-x264-params','keyint=60:min-keyint=30','-an','-movflags','+faststart',stumm],{stdio:['pipe','ignore','ignore']});
    const fertig=new Promise((r,j)=>ff.on('close',c=>c===0?r():j(new Error('ffmpeg '+c))));
    for(let i=0;i<total;i++){ await p.evaluate(t=>window.render(t),i/FPS);
      const buf=await p.screenshot({type:'png'}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); }
    ff.stdin.end(); await fertig; console.log('Bilder', total);
  }
  await b.close();
})().catch(e=>{console.error('FEHLER:',e.message);process.exit(1);});
