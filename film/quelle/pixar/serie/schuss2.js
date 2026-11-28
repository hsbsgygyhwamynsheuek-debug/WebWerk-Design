const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+__dirname+'/4-lang.html');
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(600);
  console.log('Dauer', await p.evaluate(()=>window.FILM_DAUER));
  let i=0;
  for(const t of process.argv.slice(2).map(Number)){
    await p.evaluate(t=>window.render(t),t); await p.waitForTimeout(50);
    await p.screenshot({path:`p2/${String(++i).padStart(2,'0')}_${t}.png`});
  }
  await b.close();
})();
