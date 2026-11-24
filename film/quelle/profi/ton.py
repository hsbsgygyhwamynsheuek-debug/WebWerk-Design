# -*- coding: utf-8 -*-
import json, wave, subprocess, numpy as np
SR=48000
P=json.load(open('plan.json')); M=P['marken']; LEN=P['dauer']; N=int(SR*LEN)
rng=np.random.default_rng(3)
def lies(p):
    with wave.open(p) as f:
        a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(np.float32)/32768
        if f.getnchannels()==2: a=a.reshape(-1,2).mean(1)
    return a
def lege(buf,t,sig,g=1.0):
    i0=int(round(t*SR)); i1=min(N,i0+len(sig))
    if i0<N and i1>i0: buf[i0:i1]+=sig[:i1-i0]*g
def tp(x,a):
    y=np.empty_like(x); v=0.0
    for i in range(len(x)): v+=a*(x[i]-v); y[i]=v
    return y

# ---- Stimmen: Raumklang und Praesenz, Kartoffel mit mehr Tiefe ----
stimme=np.zeros(N); huell=np.zeros(N)
for k,r in enumerate(P['reden']):
    fx='highpass=f=85,equalizer=f=3200:t=q:w=1.2:g=3,aecho=0.8:0.55:38|67:0.16|0.09'
    if r['w']=='K': fx='lowshelf=f=160:g=5,'+fx
    subprocess.run(['ffmpeg','-v','error','-y','-i',r['datei'],'-af',fx,'-ar',str(SR),'-ac','1',
                    f'v{k}.wav'],check=True)
    a=lies(f'v{k}.wav')
    # jede Zeile auf dieselbe Lautheit (nur ueber die hoerbaren Teile gemessen)
    laut=a[np.abs(a)>0.02]
    rms=np.sqrt((laut**2).mean()) if len(laut) else 1e-3
    a=a*(10**(-15/20)/rms)
    lege(stimme,r['a'],a)
    i0=int(r['a']*SR); i1=min(N,i0+len(a)); huell[i0:i1]=np.maximum(huell[i0:i1],np.abs(a[:i1-i0]))

# ---- Musik ----
subprocess.run(['python3','-I','../musik/phonk.py',json.dumps(
  {'dauer':LEN,'drop':M['drop'],'samen':17,'out':'beat.wav'})],check=True,stdout=subprocess.DEVNULL)
beat=lies('beat.wav')[:N]
# Musik bricht weg, wenn die Kartoffel spricht – und kommt auf der Endkarte zurueck
t=np.arange(N)/SR
gain=np.ones(N)
s0,s1=M['stille'],M['ende']
gain[(t>=s0)&(t<s1)]=0.06
ramp=int(0.05*SR); i0=int(s0*SR)
gain[i0:i0+ramp]=np.linspace(1,0.06,ramp)
beat*=gain
# Ducking unter den Stimmen
w=int(SR*0.2); c=np.concatenate([[0.0],np.cumsum(huell)])
lo=np.clip(np.arange(N)-w//2,0,N); hi=np.clip(np.arange(N)+w//2,0,N)
gl=(c[hi]-c[lo])/np.maximum(1,hi-lo); gl/=gl.max()+1e-9
beat*=1-0.62*np.clip(gl*3,0,1)

# ---- Effekte ----
sfx=np.zeros(N)
def tt(d): return np.arange(int(SR*d))/SR
# Whoosh in den Drop
d=0.42; x=rng.normal(0,1,int(SR*d)); u=tt(d)/d
y=np.empty_like(x); v=0.0
for i in range(len(x)):
    a=0.02+0.55*np.sin(np.pi*u[i])**2; v+=a*(x[i]-v); y[i]=v
y*=np.sin(np.pi*u)**1.5; y/=np.abs(y).max()+1e-9
lege(sfx,M['drop']-0.30,y,0.55)
# Sub-Schlag auf dem Drop und auf der Endkarte
def boom(f0=48,lang=1.6):
    q=tt(lang); f=f0+70*np.exp(-q*14); ph=2*np.pi*np.cumsum(f)/SR
    return np.tanh(1.8*np.sin(ph)*np.exp(-q*2.6))
lege(sfx,M['drop'],boom(),0.75)
lege(sfx,M['ende'],boom(42,2.2),0.95)
# Digitaler Glitch beim Zahlenwechsel: zerhacktes Rauschen + Piepser
q=tt(0.34); g=np.zeros(len(q))
for k in range(9):
    s=int(k*0.034*SR); e=min(len(q),s+int(0.02*SR))
    f=900+300*k%1800
    g[s:e]=np.sign(np.sin(2*np.pi*f*q[s:e]))*0.6 + rng.normal(0,0.5,e-s)
g=np.round(g*6)/6                                  # Bitreduktion
lege(sfx,M['glitch'],g,0.28)

mix=stimme*0.92 + beat*0.55 + sfx*0.6
mix/=np.abs(mix).max()+1e-9; mix*=10**(-1.0/20)
st=np.stack([mix,mix],1)
with wave.open('mix-roh.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i','mix-roh.wav','-af','loudnorm=I=-14:TP=-1.2:LRA=10',
                '-ar',str(SR),'ton.wav'],check=True)
print('ton.wav', LEN,'s')
