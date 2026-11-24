# -*- coding: utf-8 -*-
"""
Episoden-Baukasten. Aus einer JSON-Beschreibung entstehen Stimmen, Ton und
eine Seite, die Bild fuer Bild gerendert wird.
  python3 -I ep.py spec.json          -> baut alles, rendert Pruefbilder
  python3 -I ep.py spec.json render   -> zusaetzlich fertiges Video
"""
import json, sys, os, math, wave, hashlib, subprocess, base64
import numpy as np
HIER = os.path.dirname(os.path.abspath(__file__))
ST   = os.path.join(HIER, '..', 'stimme')
SR, BEAT = 48000, 60/140
SPEC = json.load(open(sys.argv[1], encoding='utf-8'))
NAME = SPEC['name']; OUT = os.path.join(HIER, 'out', NAME); os.makedirs(OUT, exist_ok=True)
RENDER = len(sys.argv) > 2 and sys.argv[2] == 'render'

STIMMEN = {
 'P': ('de_DE-thorsten-medium.onnx', 1.16, 0.96),
 'A': ('de_DE-karlsson-low.onnx',    1.09, 1.00),
 'K': ('de_DE-pavoque-low.onnx',     0.74, 1.26),
 'N': ('de_DE-thorsten-medium.onnx', 0.92, 1.06),   # der Neue: ruhig, selbstsicher
 'X': ('de_DE-karlsson-low.onnx',    0.97, 1.02),   # Erzaehler aus dem Off
}
def lies(p):
    with wave.open(p) as f:
        a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(np.float32)/32768
        if f.getnchannels()==2: a=a.reshape(-1,2).mean(1)
    return a
def stimme(w, text):
    """Sprachzeile erzeugen (zwischengespeichert)."""
    os.makedirs(os.path.join(ST,'cache'), exist_ok=True)
    h = hashlib.md5((w+'|'+text).encode()).hexdigest()[:12]
    ziel = os.path.join(ST,'cache',f'{w}_{h}.wav')
    if not os.path.exists(ziel):
        mod,hoch,lang = STIMMEN[w]; roh = ziel.replace('.wav','_roh.wav')
        subprocess.run([os.path.join(ST,'venv','bin','python'),'-I','-m','piper',
            '-m',os.path.join(ST,'modelle',mod),'--length-scale',str(lang),
            '--noise-scale','0.60','--noise-w-scale','0.80','-f',roh],
            input=text.encode(),check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        sr=wave.open(roh).getframerate()
        subprocess.run(['ffmpeg','-v','error','-y','-i',roh,'-af',
            f'asetrate={int(sr*hoch)},aresample=48000,atempo={1/hoch:.6f},highpass=f=70,'
            'acompressor=threshold=-18dB:ratio=3:attack=8:release=140,alimiter=limit=0.95',
            '-ar','48000','-ac','1',ziel],check=True)
    a = lies(ziel); k=SR//25; n=len(a)//k
    e = np.abs(a[:n*k]).reshape(n,k).max(1); e/=e.max()+1e-9
    return ziel, len(a)/SR, [round(float(x),3) for x in e]

# ---------- Schnittplan ----------
VOR, NACH = 0.10, 0.34
tb=0; shots=[]; reden=[]; marken={}
for s in SPEC['shots']:
    a = round(tb*BEAT,4); n = s.get('min',3)
    r = s.get('rede')
    if r:
        datei,d,env = stimme(r['w'], r['t'])
        n = max(n, math.ceil((VOR+d+NACH)/BEAT))
        reden.append(dict(a=round(a+VOR,4), d=round(d,3), w=r['w'], t=r['t'],
                          datei=datei, env=env, hall=r.get('hall',False)))
    sh = {k:v for k,v in s.items() if k not in ('rede','min','mark')}
    sh.update(a=a, b=round((tb+n)*BEAT,4)); shots.append(sh)
    if s.get('mark'): marken[s['mark']] = a
    tb += n
if SPEC.get('ende'):
    shots.append(dict(a=round(tb*BEAT,4), b=round((tb+7)*BEAT,4), cam='ENDE')); marken['ende']=round(tb*BEAT,4); tb+=7
DAUER = round(tb*BEAT,4)
def zeit(x):
    if isinstance(x,(int,float)): return float(x)
    if isinstance(x,str) and '+' in x:
        m,o = x.split('+'); return marken[m]+float(o)
    return marken[x]

# Zahlenwechsel in Sekunden aufloesen
wechselzeiten=[]; spinfenster=[]
for sz in SPEC['szenen'].values():
    for z in sz.get('zahlen',[]):
        if 'wechsel' in z:
            z['wechsel']=[[zeit(t),txt] for t,txt in z['wechsel']]; wechselzeiten += [w[0] for w in z['wechsel']]
        if 'spin' in z:
            z['spin']['von']=zeit(z['spin']['von']); z['spin']['bis']=zeit(z['spin']['bis']); spinfenster.append((z['spin']['von'],z['spin']['bis']))
titel=[dict(t=x['t'], von=zeit(x['von']), bis=zeit(x['bis']), pos=x.get('pos','oben')) for x in SPEC.get('titel',[])]

# ---------- Ton ----------
N=int(SR*DAUER); t=np.arange(N)/SR; rng=np.random.default_rng(len(NAME))
def lege(buf,ts,sig,g=1.0):
    i0=int(round(ts*SR)); i1=min(N,i0+len(sig))
    if 0<=i0<N and i1>i0: buf[i0:i1]+=sig[:i1-i0]*g
stim=np.zeros(N); huell=np.zeros(N)
for k,r in enumerate(reden):
    fx='highpass=f=85,equalizer=f=3200:t=q:w=1.2:g=3,aecho=0.8:0.55:38|67:0.16|0.09'
    if r['hall']: fx='highpass=f=95,equalizer=f=3000:t=q:w=1.2:g=2,aecho=0.8:0.72:90|170|260:0.34|0.22|0.12'
    if r['w']=='K': fx='lowshelf=f=160:g=5,'+fx
    v=os.path.join(OUT,f'v{k}.wav')
    subprocess.run(['ffmpeg','-v','error','-y','-i',r['datei'],'-af',fx,'-ar',str(SR),'-ac','1',v],check=True)
    a=lies(v); laut=a[np.abs(a)>0.02]; a*= (10**(-15/20))/(np.sqrt((laut**2).mean()) if len(laut) else 1e-3)
    lege(stim,r['a'],a); i0=int(r['a']*SR); i1=min(N,i0+len(a)); huell[i0:i1]=np.maximum(huell[i0:i1],np.abs(a[:i1-i0]))
drop = marken.get('drop', SPEC.get('drop_zeit', 0.0))
subprocess.run(['python3','-I',os.path.join(HIER,'..','musik','phonk.py'),json.dumps(
    {'dauer':DAUER,'drop':max(drop,BEAT),'samen':len(NAME)*7,'out':os.path.join(OUT,'beat.wav')})],
    check=True,stdout=subprocess.DEVNULL)
beat=lies(os.path.join(OUT,'beat.wav'))[:N]
if len(beat)<N: beat=np.pad(beat,(0,N-len(beat)))
if 'stille' in marken:
    s0=marken['stille']; s1=marken.get('ende',DAUER)
    g=np.ones(N); g[(t>=s0)&(t<s1)]=0.06; beat*=g
w=int(SR*0.2); c=np.concatenate([[0.0],np.cumsum(huell)])
lo=np.clip(np.arange(N)-w//2,0,N); hi=np.clip(np.arange(N)+w//2,0,N)
gl=(c[hi]-c[lo])/np.maximum(1,hi-lo); gl/=gl.max()+1e-9; beat*=1-0.62*np.clip(gl*3,0,1)
sfx=np.zeros(N)
def tt(d): return np.arange(int(SR*d))/SR
def tp(x,a):
    y=np.empty_like(x); v=0.0
    for i in range(len(x)): v+=a*(x[i]-v); y[i]=v
    return y
def boom(f0=48,lang=1.6):
    q=tt(lang); f=f0+70*np.exp(-q*14); ph=2*np.pi*np.cumsum(f)/SR
    return np.tanh(1.8*np.sin(ph)*np.exp(-q*2.6))
if 'drop' in marken:
    d=0.42; x=rng.normal(0,1,int(SR*d)); u=tt(d)/d; y=np.empty_like(x); v=0.0
    for i in range(len(x)): a=0.02+0.55*np.sin(np.pi*u[i])**2; v+=a*(x[i]-v); y[i]=v
    y*=np.sin(np.pi*u)**1.5; y/=np.abs(y).max()+1e-9; lege(sfx,marken['drop']-0.30,y,0.55)
    lege(sfx,marken['drop'],boom(),0.75)
if 'ende' in marken: lege(sfx,marken['ende'],boom(42,2.2),0.95)
def glitch():
    q=tt(0.34); g=np.zeros(len(q))
    for k in range(9):
        s=int(k*0.034*SR); e=min(len(q),s+int(0.02*SR)); f=900+(300*k)%1800
        g[s:e]=np.sign(np.sin(2*np.pi*f*q[s:e]))*0.6+rng.normal(0,0.5,e-s)
    return np.round(g*6)/6
for wz in wechselzeiten: lege(sfx,wz,glitch(),0.28)
for (a0,a1) in spinfenster:
    tick=np.sin(2*np.pi*2400*tt(0.012))*np.exp(-tt(0.012)*300)
    x=a0
    while x<a1: lege(sfx,x,tick,0.35); x+=0.055
    lege(sfx,a1,glitch(),0.30)
mix=stim*0.92+beat*0.55+sfx*0.6
mix/=np.abs(mix).max()+1e-9; mix*=10**(-1.0/20)
with wave.open(os.path.join(OUT,'mix.wav'),'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(np.stack([mix,mix],1),-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',os.path.join(OUT,'mix.wav'),'-af','loudnorm=I=-14:TP=-1.2:LRA=10',
                '-ar',str(SR),os.path.join(OUT,'ton.wav')],check=True)

# ---------- Seite ----------
bilder={}
for sid,sz in SPEC['szenen'].items():
    p=os.path.join(OUT,f'{sid}.jpg')
    subprocess.run(['ffmpeg','-v','error','-y','-i',sz['bild'],'-q:v','2',p],check=True)
    bilder[sid]='data:image/jpeg;base64,'+base64.b64encode(open(p,'rb').read()).decode()
    sz['w'],sz['h']=[int(v) for v in subprocess.run(['ffprobe','-v','error','-show_entries','stream=width,height',
        '-of','csv=p=0',p],capture_output=True,text=True).stdout.strip().split(',')]
DATA=dict(dauer=DAUER,beat=BEAT,shots=shots,marken=marken,titel=titel,ende=SPEC.get('ende'),
          reden=[{k:v for k,v in r.items() if k!='datei'} for r in reden],
          szenen={k:{kk:vv for kk,vv in v.items() if kk!='bild'} for k,v in SPEC['szenen'].items()})
vorlage=open(os.path.join(HIER,'vorlage.html'),encoding='utf-8').read()
open(os.path.join(OUT,'bilder.js'),'w').write('window.SZENEN='+json.dumps(bilder)+';')
for f in ('warp3.js','kino.js','kino.css','profi.css'):
    subprocess.run(['cp',os.path.join(HIER,f),OUT],check=True)
open(os.path.join(OUT,'seite.html'),'w',encoding='utf-8').write(vorlage.replace('__DATA__',json.dumps(DATA,ensure_ascii=False)))
print(f'{NAME}: {DAUER:.1f}s, {len(shots)} Einstellungen, {len(reden)} Zeilen, Marken {marken}')
