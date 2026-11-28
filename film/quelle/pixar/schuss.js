const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+__dirname+'/clip.html');
  await p.waitForTimeout(700);
  for(const t of process.argv.slice(2).map(Number)){
    await p.evaluate(t=>window.render(t),t); await p.waitForTimeout(60);
    await p.screenshot({path:`probe_${String(t).replace('.','-')}.png`});
  }
  await b.close();
})();
