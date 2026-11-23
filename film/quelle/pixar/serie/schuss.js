const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  let i=0;
  for(const [film,times] of [['1-status',[1.5,4.8,7.8,10.5,13.5]],
                             ['2-die-970',[1.5,4.9,8.0,11.0,13.8]],
                             ['3-deine-zahl',[1.3,4.0,6.4,9.0,11.6]]]){
    await p.goto('file://'+__dirname+'/'+film+'.html');
    await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(500);
    console.log(film,'Dauer',await p.evaluate(()=>window.FILM_DAUER));
    for(const t of times){ await p.evaluate(t=>window.render(t),t); await p.waitForTimeout(50);
      await p.screenshot({path:`probe/${String(++i).padStart(2,'0')}_${film}_${t}.png`}); }
  }
  await b.close();
})();
