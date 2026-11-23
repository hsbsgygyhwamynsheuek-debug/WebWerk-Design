/* Dialogfassung – baut auf kino.js auf (dort stehen kamera, staub, Easing). */
function bauDialog(KONF){
  staubAn(30);
  const SH_=KONF.shots, RE=KONF.reden, DAUER=KONF.dauer;
  const FARBE={P:'#FFC48A', A:'#FF8F7A', K:'#D9C7A8'};
  const NAME={P:'Pfirsich', A:'Paprika', K:'Kartoffel'};
  const rede=document.createElement('div'); rede.id='rede';
  stage.insertBefore(rede, q('#ende'));
  RE.forEach((r,i)=>{
    const d=document.createElement('div'); d.id='r'+i; d.style.display='none';
    d.innerHTML=`<div class="tag" style="background:${FARBE[r.w]}">${NAME[r.w]}</div>`+
      `<div class="satz">${r.t.split(' ').map(x=>`<span>${x}</span>`).join('')}</div>`;
    rede.appendChild(d);
  });
  window.FILM_DAUER=DAUER;
  window.FILM_CUTS=KONF.schlaege;

  window.render=function(t){
    let akt=0; SH_.forEach((s,i)=>{ if(t>=s.a) akt=i; });
    const sh=SH_[akt], lt=t-sh.a, dauer=(SH_[akt+1]?SH_[akt+1].a:DAUER)-sh.a;
    const f=eIO(pr(lt,0,dauer));
    const z=sh.z0+(sh.z1-sh.z0)*f;
    const cx=sh.cx+((sh.cx1??sh.cx)-sh.cx)*f;
    const cy=sh.cy+((sh.cy1??sh.cy)-sh.cy)*f;
    let extra='';
    if(sh.wackel){ const w=sh.wackel*(1-pr(lt,0,1.3));
      extra=` translate(${(Math.sin(lt*31)*w).toFixed(2)}px,${(Math.cos(lt*27)*w).toFixed(2)}px)`; }
    q('#rahmen').style.transform=kamera(cx,cy,z)+extra;

    const blitz=akt>0?(1-pr(lt,0,0.08))*0.42:0;
    q('#vig').style.background=
      `radial-gradient(118% 84% at 50% 44%,rgba(255,255,255,${blitz.toFixed(3)}) 0%,transparent 44%,rgba(0,0,0,.62) 100%)`;
    /* kalter Stich, wenn die Kartoffel dran ist */
    const kalt = sh.kalt ? 0.3 : 0;
    q('#rahmen').style.filter = kalt
      ? `saturate(${(1-kalt*0.5).toFixed(2)}) brightness(${(1-kalt*0.12).toFixed(2)}) hue-rotate(-6deg)` : '';

    staubMal(t);

    /* laufende Dialogzeile */
    let aktiv=-1;
    RE.forEach((r,i)=>{ if(t>=r.a && t<r.a+r.d) aktiv=i; });
    RE.forEach((r,i)=>{ q('#r'+i).style.display = (i===aktiv)?'block':'none'; });
    if(aktiv>=0){
      const r=RE[aktiv], lt2=t-r.a, w=qa('#r'+aktiv+' .satz span');
      const proWort=Math.min(0.26,(r.d*0.62)/Math.max(1,w.length));
      w.forEach((sp,n)=>{
        const k=eOut(pr(lt2,0.06+n*proWort,0.06+n*proWort+0.2));
        sp.style.opacity=String(k);
        sp.style.transform=`translateY(${((1-k)*14).toFixed(1)}px)`;
      });
      const tag=q('#r'+aktiv+' .tag'), e=eSpr(pr(lt2,0,0.5));
      tag.style.transform=`scale(${(0.8+0.2*e).toFixed(3)})`;
      /* Die Zahl des Sprechenden pulsiert im Sprechrhythmus */
      qa('.z').forEach(z=>z.classList.remove('laut'));
      const zz={P:1,A:2,K:0}[r.w];
      const el=qa('.z')[zz];
      if(el){ el.classList.add('laut');
        el.style.filter=`brightness(${(1.1+0.22*Math.abs(Math.sin(lt2*11))).toFixed(3)})`; }
    } else {
      qa('.z').forEach(z=>{z.classList.remove('laut'); z.style.filter='';});
    }

    /* Schlusskarte */
    const e=q('#ende'), k=eOut(pr(t,KONF.ende.a,KONF.ende.a+0.5));
    e.style.opacity=String(k);
    if(k>0){
      rede.style.opacity=String(1-k);
      q('.gr',e).style.transform=`scale(${(0.84+0.16*eSpr(pr(t,KONF.ende.a+0.15,KONF.ende.a+1.05))).toFixed(3)})`;
      const pf=q('.pfeil',e); if(pf) pf.style.transform=`translateY(${(Math.sin((t-KONF.ende.a)*5)*9).toFixed(1)}px)`;
    } else rede.style.opacity='1';
  };
  window.render(0);
}
