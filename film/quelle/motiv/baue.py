# -*- coding: utf-8 -*-
"""Motivationsvideo: Sprecher, Zeitachse, Klaviermusik, Mischung."""
import json, os, wave, hashlib, subprocess, numpy as np
HIER=os.path.dirname(os.path.abspath(__file__)); ST=os.path.join(HIER,'..','stimme')
SR=48000
S=json.load(open(os.path.join(HIER,'skript.json'),encoding='utf-8'))
def lies(p):
    with wave.open(p) as f:
        a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(np.float32)/32768
        if f.getnchannels()==2: a=a.reshape(-1,2).mean(1)
    return a
def sprich(text):
    """Ruhige, tiefe Sprecherstimme (Thorsten, tiefer und langsamer)."""
    h=hashlib.md5(('M|'+text).encode()).hexdigest()[:12]
    ziel=os.path.join(ST,'cache',f'M_{h}.wav')
    if not os.path.exists(ziel):
        roh=ziel.replace('.wav','_roh.wav')
        subprocess.run([os.path.join(ST,'venv','bin','python'),'-I','-m','piper','-m',
            os.path.join(ST,'modelle','de_DE-thorsten-medium.onnx'),'--length-scale','1.10',
            '--noise-scale','0.55','--noise-w-scale','0.75','--sentence-silence','0.25','-f',roh],
            input=text.encode(),check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        sr=wave.open(roh).getframerate(); hoch=0.88
        subprocess.run(['ffmpeg','-v','error','-y','-i',roh,'-af',
            f'asetrate={int(sr*hoch)},aresample=48000,atempo={1/hoch:.6f},highpass=f=60,'
            'lowshelf=f=180:g=3,equalizer=f=3000:t=q:w=1.3:g=2,'
            'acompressor=threshold=-20dB:ratio=3:attack=6:release=160,alimiter=limit=0.95',
            '-ar','48000','-ac','1',ziel],check=True)
    return ziel
os.makedirs(os.path.join(ST,'cache'),exist_ok=True)
zeit=0.35; plan=[]
for sz in S['szenen']:
    p=sprich(sz['vo']); a=lies(p); d=len(a)/SR
    k=SR//25; n=len(a)//k; e=np.abs(a[:n*k]).reshape(n,k).max(1); e/=e.max()+1e-9
    dauer=max(2.2, d+0.55+sz.get('pause',0.35))
    plan.append(dict(sz, a=round(zeit,3), b=round(zeit+dauer,3), vo_a=round(zeit+0.25,3), vo_d=round(d,3),
                     datei=p, env=[round(float(x),3) for x in e]))
    zeit+=dauer
LEN=round(zeit,3); N=int(SR*LEN); t=np.arange(N)/SR
# ---- Stimme ----
stim=np.zeros(N)
for s in plan:
    a=lies(s['datei']); laut=a[np.abs(a)>0.02]; a*=10**(-14/20)/np.sqrt((laut**2).mean())
    i0=int(s['vo_a']*SR); i1=min(N,i0+len(a)); stim[i0:i1]+=a[:i1-i0]
# ---- Klavier: Am – F – C – G, Arpeggios, zum Hoehepunkt hin voller ----
def hz(n): return 440*2**((n-69)/12)
AKK=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]        # Am F C G (MIDI)
BPM=76; BEAT=60/BPM
musik=np.zeros(N)
def klavier(f,dauer,laut):
    q=np.arange(int(SR*dauer))/SR
    x=(np.sin(2*np.pi*f*q)+0.42*np.sin(2*np.pi*2*f*q)*np.exp(-q*1.5)
       +0.18*np.sin(2*np.pi*3*f*q)*np.exp(-q*3)+0.06*np.sin(2*np.pi*4.02*f*q)*np.exp(-q*5))
    env=(1-np.exp(-q*600))*np.exp(-q*(1.1+f/900))
    return x*env*laut
idx={s['typ']:s for s in plan}
hoch_a=idx['hoch']['a']; talent_a=idx['talent']['a']; heute_a=idx['heute']['a']; ende_a=idx['ende']['a']
schlag=0
while schlag*BEAT < LEN:
    tz=schlag*BEAT; akk=AKK[(schlag//8)%4]
    # Lautstaerke folgt der Geschichte
    if tz<hoch_a: l=0.16
    elif tz<talent_a: l=0.30
    elif tz<heute_a: l=0.10
    else: l=0.26
    ton=akk[[0,1,2,1][schlag%4]]+12
    s=klavier(hz(ton),2.4,l); i0=int(tz*SR); i1=min(N,i0+len(s)); musik[i0:i1]+=s[:i1-i0]
    if schlag%8==0:          # Bass auf jedem Akkordwechsel
        s=klavier(hz(akk[0]-12),4.5,l*1.25); i1=min(N,i0+len(s)); musik[i0:i1]+=s[:i1-i0]
    schlag+=1
# Flaeche, die ab dem Hoehepunkt aufgeht
pad=np.zeros(N)
for k,akk in enumerate(AKK*20):
    a0=k*8*BEAT
    if a0>LEN: break
    i0=int(a0*SR); i1=min(N,int((a0+8*BEAT+1)*SR)); q=t[i0:i1]-a0
    w=sum(np.sin(2*np.pi*hz(n)*q)*0.33 + np.sin(2*np.pi*hz(n)*1.003*q)*0.2 for n in akk)
    pad[i0:i1]+=w*np.clip(q/1.5,0,1)*np.clip((8*BEAT+1-q)/1.5,0,1)
pg=np.clip((t-hoch_a)/1.5,0,1)*0.10*(1-np.clip((t-talent_a)/0.6,0,1)*0.85)+np.clip((t-heute_a)/1.5,0,1)*0.09
musik+=pad*pg
# Sub-Schwellung auf "37×"
q=t-hoch_a; m=(q>0)&(q<3)
musik[m]+=np.sin(2*np.pi*41*q[m])*np.exp(-q[m]*1.4)*0.45
# Unter der Stimme etwas leiser
huell=np.abs(stim); w=int(SR*0.25); c=np.concatenate([[0.0],np.cumsum(huell)])
lo=np.clip(np.arange(N)-w//2,0,N); hi=np.clip(np.arange(N)+w//2,0,N)
gl=(c[hi]-c[lo])/np.maximum(1,hi-lo); gl/=gl.max()+1e-9
musik*=1-0.45*np.clip(gl*3,0,1)
mix=stim*0.9+musik*0.8
mix*=np.clip((LEN-t)/1.2,0,1)
mix/=np.abs(mix).max()+1e-9; mix*=10**(-1/20)
with wave.open(os.path.join(HIER,'mix.wav'),'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(np.stack([mix,mix],1),-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',os.path.join(HIER,'mix.wav'),'-af','loudnorm=I=-14:TP=-1.2:LRA=11',
                '-ar','48000',os.path.join(HIER,'ton.wav')],check=True)
json.dump(dict(dauer=LEN,szenen=[{k:v for k,v in s.items() if k!='datei'} for s in plan]),
          open(os.path.join(HIER,'plan.json'),'w'),ensure_ascii=False)
for s in plan: print(f"{s['a']:6.2f}–{s['b']:6.2f}  {s['typ']:9s} {s['vo']}")
print('Gesamt', LEN, 's')
