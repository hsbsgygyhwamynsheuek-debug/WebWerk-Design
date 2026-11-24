# -*- coding: utf-8 -*-
"""Englisches Motivationsvideo: ElevenLabs-Stimme (Harry, Eleven v3), epische Musik, Mischung."""
import json, os, re, wave, hashlib, subprocess, numpy as np
HIER=os.path.dirname(os.path.abspath(__file__)); CACHE=os.path.join(HIER,'el','cache'); os.makedirs(CACHE,exist_ok=True)
SR=48000
S=json.load(open(os.path.join(HIER,'skript.json'),encoding='utf-8'))
def lies(p):
    with wave.open(p) as f:
        a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(np.float32)/32768
        if f.getnchannels()==2: a=a.reshape(-1,2).mean(1)
    return a
def sprich(text):
    h=hashlib.md5((S['stimme']+'|v3|'+text).encode()).hexdigest()[:12]
    mp3=os.path.join(CACHE,f'{h}.mp3'); wav=os.path.join(CACHE,f'{h}.wav')
    if not os.path.exists(mp3):
        req=os.path.join(CACHE,'req.json')
        json.dump({'text':text,'model_id':'eleven_v3','voice_settings':{'stability':0.0}},open(req,'w'))
        code=subprocess.run(['curl','-sS','-X','POST',f'https://api.elevenlabs.io/v1/text-to-speech/{S["stimme"]}?output_format=mp3_44100_128',
            '-H','Content-Type: application/json','--data','@'+req,'-o',mp3,'-w','%{http_code}'],capture_output=True,text=True).stdout
        if code!='200': raise SystemExit(f'ElevenLabs HTTP {code}: {open(mp3).read()[:200]}')
    # Stimme verdichten, Praesenz, leichte Saettigung, kurzer Raum, minimal schneller
    subprocess.run(['ffmpeg','-v','error','-y','-i',mp3,'-af',
        'atempo=1.05,highpass=f=75,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3200:t=q:w=1.2:g=3.5,'
        'acompressor=threshold=-22dB:ratio=4:attack=4:release=120:makeup=4,'
        'asoftclip=type=tanh,aecho=0.8:0.4:28|47:0.10|0.06,alimiter=limit=0.95',
        '-ar',str(SR),'-ac','1',wav],check=True)
    return wav
zeit=0.25; plan=[]
for sz in S['szenen']:
    p=sprich(sz['vo']); a=lies(p); d=len(a)/SR
    k=SR//25; n=len(a)//k; e=np.abs(a[:n*k]).reshape(n,k).max(1); e/=e.max()+1e-9
    dauer=max(1.9, d+0.45+sz.get('pause',0.2))
    anzeige=re.sub(r'\[[^\]]*\]\s*','',sz['vo']).strip()
    plan.append(dict(sz, vo=anzeige, a=round(zeit,3), b=round(zeit+dauer,3), vo_a=round(zeit+0.18,3), vo_d=round(d,3), datei=p))
    zeit+=dauer
LEN=round(zeit,3); N=int(SR*LEN); t=np.arange(N)/SR
stim=np.zeros(N)
for s in plan:
    a=lies(s['datei']); laut=a[np.abs(a)>0.02]; a*=10**(-13/20)/np.sqrt((laut**2).mean())
    i0=int(s['vo_a']*SR); i1=min(N,i0+len(a)); stim[i0:i1]+=a[:i1-i0]
# ---------------- epische Musik ----------------
idx={s['typ']:s for s in plan}
T_DRUM=idx['prozent']['a']; T_HOCH=idx['hoch']['a']; T_TAL=idx['talent']['a']; T_HEUTE=idx['heute']['a']; T_END=idx['ende']['a']
BPM=92; BEAT=60/BPM
def hz(n): return 440*2**((n-69)/12)
AKK=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]          # Am F C G
musik=np.zeros(N); rng=np.random.default_rng(9)
def lege(sig,ts,g):
    i0=int(ts*SR); i1=min(N,i0+len(sig))
    if 0<=i0<N: musik[i0:i1]+=sig[:i1-i0]*g
def q(d): return np.arange(int(SR*d))/SR
def klavier(f,d=1.6):
    x=q(d); return (np.sin(2*np.pi*f*x)+0.5*np.sin(4*np.pi*f*x)*np.exp(-x*2)+0.2*np.sin(6*np.pi*f*x)*np.exp(-x*4))*(1-np.exp(-x*800))*np.exp(-x*2.2)
def taiko(f0=58):
    x=q(0.9); f=f0*(1+0.9*np.exp(-x*30)); ph=2*np.pi*np.cumsum(f)/SR
    k=np.sin(ph)*np.exp(-x*5.5); n=rng.normal(0,1,len(x))*np.exp(-x*40)*0.35
    return np.tanh(2.2*(k+n))
def schlag():   # grosser Einschlag
    x=q(2.6); f=40+90*np.exp(-x*12); ph=2*np.pi*np.cumsum(f)/SR
    b=np.sin(ph)*np.exp(-x*1.8); c=np.diff(rng.normal(0,1,len(x)+1))*np.exp(-x*1.6)*0.5
    return np.tanh(1.6*(b+c))
def intensitaet(ts):
    if ts<T_DRUM: return 0.45
    if ts<T_HOCH: return 0.65
    if ts<T_TAL: return 1.0
    if ts<T_HEUTE: return 0.30
    if ts<T_END: return 0.75
    return 1.0
s=0
while s*BEAT<LEN:
    ts=s*BEAT; akk=AKK[(s//4)%4]; I=intensitaet(ts)
    # Klavier-Ostinato auf Achteln
    for h in (0,0.5):
        ton=akk[[0,2,1,2][(s*2+int(h*2))%4]]+12
        lege(klavier(hz(ton)),ts+h*BEAT,0.13*(0.6+0.4*I))
    # Trommeln: ab "One percent" auf 1 und 3, ab "37x" auf jedem Schlag, Pause im Einbruch
    if ts>=T_DRUM and not (T_TAL<=ts<T_HEUTE):
        if (s%2==0) or ts>=T_HOCH: lege(taiko(), ts, 0.42*I)
        if ts>=T_HOCH and s%4==3: lege(taiko(84), ts+BEAT*0.5, 0.25*I)
    s+=1
# Streicherflaeche: saegezahnartig, schwillt mit der Intensitaet
pad=np.zeros(N)
for k in range(int(LEN/(4*BEAT))+1):
    a0=k*4*BEAT; akk=AKK[k%4]; i0=int(a0*SR); i1=min(N,int((a0+4*BEAT+0.6)*SR))
    if i0>=N: break
    x=t[i0:i1]-a0
    w=sum(sum(np.sin(2*np.pi*hz(n-12)*h*x*(1+0.002*dd))/h for h in range(1,7) for dd in (-1,1)) for n in akk)
    pad[i0:i1]+=w*np.clip(x/0.5,0,1)*np.clip((4*BEAT+0.6-x)/0.5,0,1)
env=np.array([intensitaet(v) for v in t[::480]]); env=np.repeat(env,480)[:N]
c=np.concatenate([[0.0],np.cumsum(env)]); w=SR//2; lo=np.clip(np.arange(N)-w,0,N); hi=np.clip(np.arange(N)+w,0,N)
env=(c[hi]-c[lo])/np.maximum(1,hi-lo)
musik+=pad*0.035*env
# Riser in den Hoehepunkt, Einschlaege auf "37x" und "START NOW"
x=q(1.8); r=np.cumsum(rng.normal(0,1,len(x))); r=np.diff(r,prepend=0)*(x/1.8)**2.5
lege(r/np.abs(r).max(), T_HOCH-1.8, 0.35)
lege(schlag(), T_HOCH, 0.9); lege(schlag(), T_END, 1.0)
# Musik bleibt praesent, geht unter der Stimme nur etwas zurueck (wie im Vorbild)
h=np.abs(stim); w=int(SR*0.2); c=np.concatenate([[0.0],np.cumsum(h)])
lo=np.clip(np.arange(N)-w//2,0,N); hi=np.clip(np.arange(N)+w//2,0,N); g=(c[hi]-c[lo])/np.maximum(1,hi-lo); g/=g.max()+1e-9
musik*=1-0.40*np.clip(g*3,0,1)
mix=stim*1.0+musik*0.85
mix*=np.clip((LEN-t)/1.0,0,1)
mix=np.tanh(1.2*mix/np.abs(mix).max())/np.tanh(1.2)
mix*=10**(-1/20)
with wave.open(os.path.join(HIER,'mix.wav'),'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(np.stack([mix,mix],1),-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',os.path.join(HIER,'mix.wav'),'-af','loudnorm=I=-13:TP=-1.0:LRA=8',
                '-ar','48000',os.path.join(HIER,'ton.wav')],check=True)
json.dump(dict(dauer=LEN,szenen=[{k:v for k,v in s.items() if k!='datei'} for s in plan]),open(os.path.join(HIER,'plan.json'),'w'),ensure_ascii=False)
for s in plan: print(f"{s['a']:6.2f}–{s['b']:6.2f} {s['typ']:9s} {s['vo']}")
print('Gesamt',LEN,'s')
