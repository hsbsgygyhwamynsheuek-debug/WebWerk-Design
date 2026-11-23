# -*- coding: utf-8 -*-
"""
Tonbett für den WebWerk-Film – komplett selbst erzeugt (Sinus-Synthese).
Keine fremden Samples, keine Lizenzfrage. 48 kHz, Stereo.
"""
import numpy as np, wave, struct

SR   = 48000
LEN  = 42.0
N    = int(SR*LEN)
t    = np.arange(N)/SR

def hz(note):
    """Notenname -> Frequenz (A4 = 440)."""
    n = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[note[0]]
    i = 1
    if note[1] in '#b':
        n += 1 if note[1]=='#' else -1; i = 2
    okt = int(note[i:])
    return 440.0*2**((n-9)/12 + (okt-4))

# Szenenwechsel – daran hängen Akkorde und Akzente
CUTS = [0.0, 7.2, 11.8, 17.6, 25.2, 31.4, 35.8]
AKKORDE = [
    ['A2','A3','C4','E4'],   # Am  – Frage
    ['F2','F3','A3','C4'],   # F   – Problem
    ['C3','C4','E4','G4'],   # C   – Preis, hell
    ['A2','A3','C4','E4'],   # Am  – Ablauf
    ['F2','F3','A3','C4'],   # F   – Demo
    ['G2','G3','B3','D4'],   # G   – Person, Spannung
    ['C3','E3','G3','C5'],   # C   – Auflösung
]

mix = np.zeros((N,2))

def pad(noten, ein, aus, lautst):
    """Warmer Flächenklang mit weichem Ein- und Ausblenden."""
    freqs = [hz(n) for n in noten]
    seg = np.zeros((N,2))
    hull = np.clip((t-ein)/1.3,0,1) * np.clip((aus-t)/1.6,0,1)
    hull = np.where((t>ein-1.4)&(t<aus+1.7), hull, 0.0)
    if hull.max() <= 0: return
    # langsames Atmen, damit die Fläche nicht steht
    atem = 1 + 0.09*np.sin(2*np.pi*0.075*t + (freqs[0] % 3.0))
    for k,f in enumerate(freqs):
        amp = [1.0, 0.55, 0.42, 0.30][k]
        for h,ha in ((1,1.0),(2,0.30),(3,0.13),(4,0.055)):
            # minimale Verstimmung links/rechts = Breite
            l = np.sin(2*np.pi*f*h*0.9988*t + h*0.7)
            r = np.sin(2*np.pi*f*h*1.0012*t + h*1.9)
            seg[:,0] += l*amp*ha
            seg[:,1] += r*amp*ha
    mix[:] += seg * (hull*atem*lautst)[:,None]

def sub(f, ein, aus, lautst=0.26):
    hull = np.clip((t-ein)/1.0,0,1)*np.clip((aus-t)/1.2,0,1)
    hull = np.where((t>ein-1.1)&(t<aus+1.3), hull, 0.0)
    w = np.sin(2*np.pi*f*t)*hull*lautst
    mix[:,0] += w; mix[:,1] += w

def zupf(f, zeit, lautst=0.13, dauer=1.4):
    """Weicher Anschlag – markiert einen Schnitt, ohne zu klickern."""
    i0 = int(zeit*SR); i1 = min(N, i0+int(dauer*SR))
    if i0>=N: return
    tt = np.arange(i1-i0)/SR
    hull = np.exp(-tt*3.2) * (1-np.exp(-tt*420))     # kein Knacken am Anfang
    w = (np.sin(2*np.pi*f*tt) + 0.33*np.sin(2*np.pi*f*2*tt)
         + 0.10*np.sin(2*np.pi*f*3*tt)) * hull * lautst
    mix[i0:i1,0] += w*0.96; mix[i0:i1,1] += w

def luft(zeit, lautst=0.05, dauer=0.75):
    """Leiser Luftzug am Schnitt – gefiltertes Rauschen."""
    i0 = max(0,int((zeit-dauer*0.7)*SR)); i1 = min(N, i0+int(dauer*SR))
    if i1<=i0: return
    n = i1-i0
    tt = np.arange(n)/SR
    rng = np.random.default_rng(int(zeit*100))
    x = rng.normal(0,1,n)
    y = np.zeros(n); a = 0.02                         # Tiefpass, nimmt die Schärfe
    for i in range(1,n): y[i] = y[i-1] + a*(x[i]-y[i-1])
    y /= (np.abs(y).max()+1e-9)
    hull = np.sin(np.pi*np.clip(tt/ (dauer),0,1))**2
    w = y*hull*lautst
    mix[i0:i1,0] += w; mix[i0:i1,1] += w*0.9

# --- Akkorde legen ---
for i,ak in enumerate(AKKORDE):
    ein = CUTS[i]
    aus = CUTS[i+1] if i+1 < len(CUTS) else LEN-0.4
    pad(ak, ein, aus, 0.055)
    sub(hz(ak[0])/2, ein, aus, 0.20)
    # Akzent auf dem Schnitt (der allererste leiser, der Film soll ruhig anfangen)
    zupf(hz(ak[-1]), ein+0.02, 0.10 if i==0 else 0.14)
    if i>0: luft(ein)

# --- Zusätzliche Akzente: Zahl, Ablaufschritte, Telefonnummer ---
for z,f,l in [(12.10,'C5',0.10),(13.0,'E5',0.09),      # 250 zählt hoch
              (18.55,'A4',0.075),(19.17,'C5',0.075),
              (19.79,'E5',0.075),(20.41,'A5',0.075),    # vier Schritte
              (36.36,'G4',0.11),(36.9,'C5',0.12)]:      # Rufnummer
    zupf(hz(f), z, l)

# --- Gesamthülle: sanft rein, sauber raus ---
mix *= np.clip(t/1.1,0,1)[:,None]
mix *= np.clip((LEN-0.3-t)/2.2,0,1)[:,None]

# --- Pegel: Spitze auf -2 dBFS, dezent unter dem Bild ---
mix /= (np.abs(mix).max()+1e-9)
mix *= 10**(-2/20)
rms = float(np.sqrt((mix**2).mean()))
print('Spitze %.2f dBFS   RMS %.1f dBFS' % (20*np.log10(np.abs(mix).max()), 20*np.log10(rms)))

pcm = (np.clip(mix,-1,1)*32767).astype('<i2')
with wave.open('ton.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('ton.wav geschrieben,', round(N/SR,2), 's')
