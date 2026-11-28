const stage=document.getElementById('stage');
const q=(s,r=document)=>r.querySelector(s);
const qa=(s,r=document)=>[...r.querySelectorAll(s)];
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const pr=(t,a,b)=>cl((t-a)/(b-a));
const eOut=x=>1-Math.pow(1-x,3);
const eIO=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const eSpr=x=>{if(x>=1)return 1;const w=13,z=.62;
  return 1-Math.exp(-z*w*x)*Math.cos(w*Math.sqrt(1-z*z)*x);};

const BW=1360, BH=1712, SW=1080, SH=1920;
/* Hält den Bildausschnitt im Bild – nie schwarze Ränder. */
function kamera(cx,cy,z){
  const hw=SW/2/z, hh=SH/2/z;
  cx=cl(cx,hw,BW-hw); cy=cl(cy,hh,BH-hh);
  return `translate(${(SW/2-cx*z).toFixed(2)}px,${(SH/2-cy*z).toFixed(2)}px) scale(${z.toFixed(4)})`;
}

/* Staub */
let ST=[];
function staubAn(n){
  let seed=11; const zuf=()=>{seed=(seed*1103515245+12345)%2147483648; return seed/2147483648;};
  const h=q('#staub');
  for(let i=0;i<n;i++){
    const d=document.createElement('i'); const g=1.6+zuf()*4.2;
    d.style.width=g+'px'; d.style.height=g+'px';
    ST.push({el:d,x:zuf()*SW,y:zuf()*SH,v:9+zuf()*22,a:zuf()*6.28,sw:18+zuf()*46,o:.18+zuf()*.5});
    h.appendChild(d);
  }
}
function staubMal(t){
  ST.forEach(d=>{
    const y=((d.y-t*d.v)%1980+1980)%1980-30;
    const x=d.x+Math.sin(t*0.5+d.a)*d.sw;
    d.el.style.transform=`translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0)`;
    d.el.style.opacity=(d.o*(0.55+0.45*Math.sin(t*0.9+d.a))).toFixed(3);
  });
}

/* Text Wort für Wort */
function textAn(sh,i){
  if(!sh.text) return null;
  const d=document.createElement('div');
  d.className='tx '+(sh.pos||'oben'); d.id='tx'+i;
  d.innerHTML=sh.text.split(' ').map(w=>`<span>${w}</span>`).join('');
  stage.insertBefore(d, q('#ende')); return d;
}
function textMal(el,lt,start){
  if(!el) return;
  qa('span',el).forEach((sp,n)=>{
    const st=start+n*0.115, k=eOut(pr(lt,st,st+0.26));
    sp.style.opacity=String(k);
    sp.style.transform=`translateY(${((1-k)*16).toFixed(1)}px)`;
  });
}

function bauFilm(KONF){
  staubAn(34);
  const SH_=KONF.shots;
  const texte=SH_.map((sh,i)=>textAn(sh,i));
  const DAUER=KONF.dauer;
  window.FILM_DAUER=DAUER;
  window.FILM_CUTS=SH_.map(s=>s.a).concat(KONF.ende? [KONF.ende.a] : []);

  window.render=function(t){
    /* laufende Einstellung finden */
    let akt=0; SH_.forEach((s,i)=>{ if(t>=s.a) akt=i; });
    const sh=SH_[akt], lt=t-sh.a, dauer=(SH_[akt+1]?SH_[akt+1].a:DAUER)-sh.a;
    const f=eIO(pr(lt,0,dauer));
    const z=sh.z0+(sh.z1-sh.z0)*f;
    const cx=sh.cx+((sh.cx1??sh.cx)-sh.cx)*f;
    const cy=sh.cy+((sh.cy1??sh.cy)-sh.cy)*f;
    let extra='';
    if(sh.wackel){ const w=sh.wackel*(1-pr(lt,0,1.2));
      extra=` translate(${(Math.sin(lt*31)*w).toFixed(2)}px,${(Math.cos(lt*27)*w).toFixed(2)}px)`; }
    q('#rahmen').style.transform=kamera(cx,cy,z)+extra;

    /* kurzer Aufblitz direkt nach einem harten Schnitt */
    const blitz=akt>0 ? (1-pr(lt,0,0.09))*0.5 : 0;
    q('#vig').style.background=
      `radial-gradient(118% 84% at 50% 44%,rgba(255,255,255,${blitz.toFixed(3)}) 0%,transparent 44%,rgba(0,0,0,.6) 100%)`;

    staubMal(t);
    texte.forEach((el,i)=>{ if(!el) return;
      const s=SH_[i];
      el.style.display=(t>=s.a&&t<(SH_[i+1]?SH_[i+1].a:DAUER))?'block':'none';
      textMal(el,t-s.a,s.tStart??0.25);
    });

    /* Schlusskarte */
    if(KONF.ende){
      const e=q('#ende'), k=eOut(pr(t,KONF.ende.a,KONF.ende.a+0.45));
      e.style.opacity=String(k);
      const gr=q('.gr',e), sp=eSpr(pr(t,KONF.ende.a+0.15,KONF.ende.a+1.0));
      gr.style.transform=`scale(${(0.84+0.16*sp).toFixed(3)})`;
      const pf=q('.pfeil',e);
      if(pf) pf.style.transform=`translateY(${(Math.sin((t-KONF.ende.a)*5)*9).toFixed(1)}px)`;
    }
  };
  window.render(0);
}
