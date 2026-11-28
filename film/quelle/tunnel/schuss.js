const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+__dirname+'/tunnel.html'); await p.waitForTimeout(400);
  const D=await p.evaluate(()=>window.FILM_DAUER); console.log('Dauer',D);
  for(const t of process.argv.slice(2).map(Number)){
    await p.evaluate(t=>window.render(t),t); await p.waitForTimeout(50);
    await p.screenshot({path:`p_${String(t).replace('.','-')}.png`});
  }
  /* Schleifenprobe: Bild bei 0 gegen Bild bei T */
  await p.evaluate(()=>window.render(0)); const A=await p.screenshot();
  await p.evaluate(()=>window.render(1.55)); const B=await p.screenshot();
  console.log('Schleife nahtlos:', Buffer.compare(A,B)===0?'JA':'NEIN');
  await b.close();
})();
