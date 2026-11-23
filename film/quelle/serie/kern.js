/* =====================================================================
   WebWerk – gemeinsamer Zeichner. Jeder Film liefert SZ[] und malen(t).
   ===================================================================== */
const stage = document.getElementById('stage');
const q  = (s,r=document)=>r.querySelector(s);
const qa = (s,r=document)=>[...r.querySelectorAll(s)];
const K  = ()=>parseFloat(getComputedStyle(stage).getPropertyValue('--k'))||1;

const cl   = (x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const pr   = (t,a,b)=>cl((t-a)/(b-a));
const eOut = x=>1-Math.pow(1-x,3);
const eExp = x=>x>=1?1:1-Math.pow(2,-10*x);
const eIO  = x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const eSpr = x=>{ if(x>=1) return 1; const w=11,z=.74;
  return 1-Math.exp(-z*w*x)*Math.cos(w*Math.sqrt(1-z*z)*x); };

function put(el,{o=null,x=0,y=0,s=1,b=0,rot=0}={}){
  if(o!==null) el.style.opacity=o;
  el.style.transform=`translate3d(${x}px,${y}px,0)`+(s!==1?` scale(${s})`:'')+(rot?` rotate(${rot}deg)`:'');
  el.style.filter = b>0.01?`blur(${b}px)`:'';
}
function zeile(el,t,start,dauer=1.0){
  const k=eOut(pr(t,start,start+dauer)); const i=el.querySelector('i')||el;
  i.style.transform=`translate3d(0,${(1-k)*112}%,0)`; i.style.opacity=cl(k*1.6);
}
function zeilen(wrap,t,start,abstand=0.1,dauer=1.0){
  qa('.ln',wrap).forEach((l,n)=>zeile(l,t,start+n*abstand,dauer));
}
function steig(el,t,start,dauer=0.9,weg=34){
  if(!el) return;
  const k=eOut(pr(t,start,start+dauer));
  put(el,{o:cl(k*1.25),y:(1-k)*weg*K(),b:(1-k)*5});
}
function wachs(el,t,start,dauer,richtung='x'){
  const k=eOut(pr(t,start,start+dauer));
  el.style.transform = richtung==='x'?`scaleX(${k})`:`scaleY(${k})`;
  el.style.opacity=cl(k*4);
}
/* Schreibmaschine: gibt den sichtbaren Text samt Cursor zurück */
function tippe(wort,t,start,ende,cursorNachher=false){
  const n=Math.floor(pr(t,start,ende)*wort.length+1e-6);
  const blink=(Math.floor(t*1.8)%2===0)?1:0.08;
  const zeig=(t<ende)||cursorNachher;
  return wort.slice(0,n).replace(/ /g,'&nbsp;')+
    `<span class="caret" style="opacity:${zeig?blink:0}"></span>`;
}

/* ---------- Abspann ---------- */
const ABSPANN_HTML = `
<div class="scene dark" id="abspann">
  <div class="pad mitte">
    <div class="wz"><span class="w">W</span><span class="n">WebWerk Design</span></div>
    <div class="tel"><span class="ln"><i>0151 72678183</i></span></div>
    <p class="zeit">Ab 16 Uhr erreichbar — vorher Schule.</p>
  </div>
  <p class="ki">Erstellt mit KI-Unterstützung</p>
  <div class="vig"></div>
</div>`;

function malAbspann(lt){
  const s=q('#abspann'), k=K();
  const wz=q('.wz',s), e=eSpr(pr(lt,0.12,1.1));
  put(wz,{o:cl(pr(lt,0.12,0.45)),y:(1-e)*26*k});
  q('.w',s).style.transform=`scale(${0.82+0.18*eSpr(pr(lt,0.2,1.2))})`;
  zeilen(q('.tel',s),lt,0.42,0.1,1.05);
  steig(q('.zeit',s),lt,0.85,0.9,22);
  steig(q('.ki',s),lt,1.25,1.0,14);
}

/* ---------- Lauf ---------- */
function starteFilm(SZ, malen, blenden){
  blenden = blenden || {};
  window.FILM_DAUER = SZ[SZ.length-1].b;
  window.FILM_SZ = SZ;
  window.render = function(t){
    SZ.forEach(s=>{
      const el=q('#'+s.id); if(!el) return;
      const bl=blenden[s.id]||0;
      const an = t >= s.a-bl && t < s.b;
      el.style.display = an?'block':'none';
      if(!an) return;
      el.style.opacity = bl?cl(pr(t,s.a-bl,s.a)):1;
      el.style.zIndex = Math.round(s.a*10);
    });
    SZ.forEach(s=>{ if(t>=s.a-(blenden[s.id]||0) && t<s.b) malen(s.id, t-s.a, t); });
  };
  window.render(0);
}
