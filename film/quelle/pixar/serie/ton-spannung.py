# -*- coding: utf-8 -*-
"""
Spannungs-Tonbett, komplett selbst erzeugt (keine fremden Samples).
Aufruf: python3 -I ton-spannung.py '{"dauer":15.4,"cuts":[0,3.4,6.4,9.3,12.0],"out":"x.wav"}'
Die Schnitte bekommen einen Aufzieher davor und einen Schlag darauf.
"""
import numpy as np, wave, sys, json

arg  = json.loads(sys.argv[1])
SR   = 48000
LEN  = float(arg['dauer']) + 0.5
N    = int(SR*LEN); t = np.arange(N)/SR
CUTS = [float(c) for c in arg['cuts']]
OUT  = arg['out']
mix  = np.zeros((N,2))

def fenster(a, b):
    return (t >= a) & (t < b)

def tiefpass(x, a=0.02):
    y = np.zeros_like(x)
    for i in range(1, len(x)):
        y[i] = y[i-1] + a*(x[i]-y[i-1])
    return y

# --- Grundton: tiefes Brummen, das die ganze Zeit trägt ---
drone = (np.sin(2*np.pi*52.0*t) * 0.55
       + np.sin(2*np.pi*77.8*t) * 0.26
       + np.sin(2*np.pi*103.5*t) * 0.12)
atem  = 0.72 + 0.28*np.sin(2*np.pi*0.085*t)
drone *= atem * 0.38
mix[:,0] += drone; mix[:,1] += drone*0.97

# --- Herzschlag: zwei Schläge, Abstand wird zum Ende hin enger ---
def schlag(zeit, laut, frq=58.0, dauer=0.5):
    i0=int(zeit*SR); i1=min(N,i0+int(dauer*SR))
    if i0>=N or i1<=i0: return
    tt=np.arange(i1-i0)/SR
    h=np.exp(-tt*13)*(1-np.exp(-tt*900))
    w=np.sin(2*np.pi*frq*tt*(1-0.35*tt))*h*laut
    mix[i0:i1,0]+=w; mix[i0:i1,1]+=w

# Bei langen Filmen zieht der Puls langsamer an, sonst haemmert er die
# halbe Laufzeit im Anschlag.
lang   = LEN > 25
faktor = 0.985 if lang else 0.955
boden  = 0.78  if lang else 0.95
takt, zeit = 1.60, 0.35
while zeit < LEN-0.6:
    schlag(zeit, 0.30); schlag(zeit+0.21, 0.19)
    takt = max(boden, takt*faktor)
    zeit += takt

# --- Aufzieher vor jedem Schnitt + Schlag auf den Schnitt ---
def aufzieher(zeit, dauer=0.9, laut=0.22):
    i0=max(0,int((zeit-dauer)*SR)); i1=min(N,int(zeit*SR))
    if i1<=i0: return
    n=i1-i0; tt=np.arange(n)/SR
    rng=np.random.default_rng(int(zeit*1000)%99991)
    x=rng.normal(0,1,n)
    # Rauschen wird nach oben hin heller: zwei Tiefpässe überblenden
    dumpf=tiefpass(x,0.015); hell=tiefpass(x,0.12)
    k=(tt/tt[-1])**1.7
    y=dumpf*(1-k)+hell*k
    y/= (np.abs(y).max()+1e-9)
    mix[i0:i1,0]+=y*k*laut; mix[i0:i1,1]+=y*k*laut*0.93

def einschlag(zeit, laut=0.5):
    i0=int(zeit*SR); i1=min(N,i0+int(1.5*SR))
    if i0>=N or i1<=i0: return
    tt=np.arange(i1-i0)/SR
    h=np.exp(-tt*4.2)*(1-np.exp(-tt*700))
    tief=np.sin(2*np.pi*44*tt*(1-0.22*tt))*h
    rng=np.random.default_rng(int(zeit*777)%99991)
    knall=tiefpass(rng.normal(0,1,len(tt)),0.05)*np.exp(-tt*16)
    knall/=(np.abs(knall).max()+1e-9)
    w=(tief*0.8+knall*0.3)*laut
    mix[i0:i1,0]+=w; mix[i0:i1,1]+=w*0.96

for i,c in enumerate(CUTS):
    if c <= 0.05: continue
    letzter = (i == len(CUTS)-1)
    aufzieher(c, 1.0 if letzter else 0.8, 0.26 if letzter else 0.18)
    einschlag(c, 0.62 if letzter else 0.42)

# --- Hülle und Pegel ---
mix *= np.clip(t/0.35,0,1)[:,None]
mix *= np.clip((LEN-0.15-t)/1.1,0,1)[:,None]
mix /= (np.abs(mix).max()+1e-9)
mix *= 10**(-2/20)
print('Spitze %.2f dBFS, RMS %.1f dBFS' % (20*np.log10(np.abs(mix).max()),
      20*np.log10(float(np.sqrt((mix**2).mean())))))
pcm=(np.clip(mix,-1,1)*32767).astype('<i2')
with wave.open(OUT,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(OUT, round(N/SR,2),'s')
