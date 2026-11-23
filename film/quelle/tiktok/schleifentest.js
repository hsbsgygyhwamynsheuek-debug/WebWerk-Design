const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  await p.goto('file://'+__dirname+'/a-loop.html'); await p.waitForTimeout(300);
  await p.evaluate(()=>window.render(0));          const A=await p.screenshot();
  await p.evaluate(()=>window.render(7.9999999));  const B=await p.screenshot();
  console.log('Bild bei 0 s und bei 8 s identisch:', Buffer.compare(A,B)===0 ? 'JA – Schleife ist nahtlos' : 'NEIN');
  await b.close();
})();
