const stage=document.getElementById('stage');
const q=(s,r=document)=>r.querySelector(s);
const qa=(s,r=document)=>[...r.querySelectorAll(s)];
const cl=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const pr=(t,a,b)=>cl((t-a)/(b-a));
const eOut=x=>1-Math.pow(1-x,3);
const eIO=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const eSpr=x=>{if(x>=1)return 1;const w=12,z=.7;
  return 1-Math.exp(-z*w*x)*Math.cos(w*Math.sqrt(1-z*z)*x);};
function put(el,{o=null,x=0,y=0,s=1,rot=0}={}){
  if(o!==null) el.style.opacity=o;
  el.style.transform=`translate3d(${x}px,${y}px,0)`+(s!==1?` scale(${s})`:'')+(rot?` rotate(${rot}deg)`:'');
}
function steig(el,t,start,dauer=.6,weg=40){
  if(!el) return; const k=eOut(pr(t,start,start+dauer));
  put(el,{o:cl(k*1.4),y:(1-k)*weg});
}
function zeilen(wrap,t,start,ab=.09,d=.7){
  qa('.ln',wrap).forEach((l,n)=>{
    const k=eOut(pr(t,start+n*ab,start+n*ab+d)); const i=l.querySelector('i')||l;
    i.style.transform=`translate3d(0,${(1-k)*112}%,0)`; i.style.opacity=cl(k*1.6);
  });
}
const WM = `<div class="wm"><span class="w">W</span><span class="n">WebWerk Design</span></div>`;
function starte(SZ, malen){
  window.FILM_DAUER = SZ[SZ.length-1].b;
  window.render=function(t){
    SZ.forEach(s=>{const el=q('#'+s.id); if(!el) return;
      const an=t>=s.a&&t<s.b; el.style.display=an?'block':'none';});
    SZ.forEach(s=>{ if(t>=s.a&&t<s.b) malen(s.id,t-s.a,t); });
  };
  window.render(0);
}
