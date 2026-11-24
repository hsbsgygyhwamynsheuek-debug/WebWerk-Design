/* Kurzformat: eine durchgehende Kamerafahrt, Figuren leben, Text in Beats. */
function bauKurz(KONF){
  staubAn(26);
  const DAUER=KONF.dauer; window.FILM_DAUER=DAUER;
  const FIG=['K','P','A'];
  const RUHE={K:{t:3.9,p:0.0,amp:3.4}, P:{t:3.2,p:1.7,amp:2.8}, A:{t:3.6,p:3.1,amp:2.6}};
  const BLINZEL={};
  FIG.forEach((k,n)=>{ const l=[]; let z=1.1+n*0.9, s=(KONF.samen||13)+n*17;
    while(z<DAUER){ l.push(z); s=(s*1103515245+12345)%2147483648; z+=2.2+(s/2147483648)*3.4; }
    BLINZEL[k]=l; });
  const blz=(k,t)=>{ let m=0; for(const z of BLINZEL[k]){ const d=t-z;
    if(d>=0&&d<0.17) m=Math.max(m,Math.sin(Math.PI*d/0.17)); } return m; };

  /* Texte anlegen */
  const TXT=KONF.texte.map((x,i)=>{
    const d=document.createElement('div');
    d.className='tx '+(x.pos||'oben'); d.style.display='none';
    d.innerHTML=x.t.split(' ').map(w=>`<span>${w}</span>`).join('');
    stage.insertBefore(d, q('#vig')); return d;
  });

  let zeichne=null;
  window.setzeZeichner = f => zeichne = f;

  window.render=function(t){
    /* Kamera: weiche Fahrt ueber die ganze Laufzeit */
    const f=eIO(cl(t/DAUER));
    const K0=KONF.von, K1=KONF.bis;
    const z  = K0.z  + (K1.z - K0.z )*f;
    const cx = K0.cx + (K1.cx- K0.cx)*f;
    const cy = K0.cy + (K1.cy- K0.cy)*f;
    let extra='';
    if(KONF.wackel){ const w=KONF.wackel;
      extra=` translate(${(Math.sin(t*7.3)*w).toFixed(2)}px,${(Math.cos(t*5.9)*w).toFixed(2)}px)`; }
    q('#rahmen').style.transform=kamera(cx,cy,z)+extra;
    if(KONF.kalt) q('#rahmen').style.filter='saturate(.86) brightness(.94) hue-rotate(-5deg)';

    /* Figuren leben */
    const zu={};
    FIG.forEach(k=>{ const r=RUHE[k], w=2*Math.PI/r.t;
      const fl=(KONF.fluestern||[]).includes(k)
        ? Math.max(0, Math.sin(t*9.1 + (k==='P'?0:1.7)))*0.55 : 0;
      zu[k]={ dx:Math.sin(w*0.63*t+r.p*1.7)*r.amp*1.5,
              dy:Math.sin(w*t+r.p)*r.amp - fl*4,
              rot:Math.sin(w*0.47*t+r.p*0.8)*0.012,
              sc:Math.sin(w*t+r.p)*0.005,
              mund:fl, blinzel:blz(k,t) }; });
    if(zeichne) zeichne(zu);

    /* Zahlen wippen mit */
    qa('.z').forEach(el=>{
      const [px,py]=el.dataset.p.split(',').map(Number);
      const [ox,oy]=versatz(px,py,zu);
      let s=1;
      if(KONF.pochen && el.dataset.p===KONF.pochen) s=1+0.05*Math.abs(Math.sin(t*2.6));
      el.style.transform=`translate(-50%,-50%) translate(${ox.toFixed(2)}px,${oy.toFixed(2)}px) scale(${s.toFixed(3)})`;
      /* Zahlenwechsel mit Bildfehler */
      if(KONF.wechsel && el.dataset.p===KONF.wechsel.p){
        const W=KONF.wechsel;
        if(t>=W.a){ const g=cl((t-W.a)/0.45);
          el.textContent = (Math.floor(t*22)%2===0 && g<1) ? W.alt : W.neu;
          el.style.filter=`brightness(${(1+1.4*(1-g)).toFixed(2)})`;
        } else { el.textContent=W.alt; el.style.filter=''; }
      }
    });

    staubMal(t);
    KONF.texte.forEach((x,i)=>{
      const el=TXT[i], an = t>=x.a && t<(x.b||DAUER);
      el.style.display = an?'block':'none';
      if(!an) return;
      qa('span',el).forEach((sp,n)=>{
        const st=x.a+n*0.075, k=eOut(pr(t,st,st+0.22));
        sp.style.opacity=String(k);
        sp.style.transform=`translateY(${((1-k)*16).toFixed(1)}px)`;
      });
    });
  };
}
