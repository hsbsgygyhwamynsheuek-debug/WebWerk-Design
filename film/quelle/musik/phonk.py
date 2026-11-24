# -*- coding: utf-8 -*-
"""
Phonk-Beat, komplett selbst synthetisiert – keine Samples, keine Lizenzfrage.
Kuhglocken-Melodie (wie die 808-Cowbell), uebersteuerter 808-Bass, harter Kick,
Clap, Hi-Hats. Vor dem Drop laeuft alles gedaempft hinter einem Tiefpass, der
sich langsam oeffnet; der Drop landet sample-genau auf der Zeit 'drop'.

Aufruf: python3 -I phonk.py '{"dauer":9.2,"drop":4.9,"out":"x.wav"}'
"""
import numpy as np, wave, sys, json, math

A    = json.loads(sys.argv[1])
SR   = 48000
BPM  = 140.0
BEAT = 60.0/BPM; S16 = BEAT/4; BAR = BEAT*4
DAUER, DROP, OUT = float(A['dauer']), float(A['drop']), A['out']
LEISE_INTRO = bool(A.get('leise_intro', False))   # fuer lange Dialogfilme
rng = np.random.default_rng(int(A.get('samen', 7)))

# Musikzeit: so viele Intro-Takte, dass der Drop auf einen Taktanfang faellt
N_INTRO = max(1, math.ceil(DROP/BAR))
M_DROP  = N_INTRO*BAR
M0      = M_DROP - DROP                  # Musikzeit am Clipanfang (0 .. 1 Takt)
N       = int(SR*DAUER)
intro   = np.zeros(N)   # wird gefiltert
trocken = np.zeros(N)   # nach dem Drop, ungefiltert

def lege(buf, m, sig, g=1.0):
    """Signal zur Musikzeit m einlegen (abgeschnitten am Rand)."""
    i0 = int(round((m - M0)*SR))
    if i0 >= N or i0 + len(sig) <= 0: return
    a = max(0, -i0); b = min(len(sig), N - i0)
    buf[i0+a:i0+b] += sig[a:b]*g

def tp(x, a):
    """Einpoliger Tiefpass (Schleife, aber nur auf kurzen Puffern)."""
    y = np.empty_like(x); v = 0.0
    for i in range(len(x)):
        v += a*(x[i]-v); y[i] = v
    return y
def hp(x):  # Hochpass durch Differenzbildung
    return np.diff(x, prepend=x[:1])

# ---------------- Klangerzeuger ----------------
def tt(dauer): return np.arange(int(SR*dauer))/SR

_glocke = {}
def glocke(semi):
    """808-Cowbell: zwei Rechtecke im Verhaeltnis 1:1,48, bandbegrenzt."""
    if semi in _glocke: return _glocke[semi]
    t = tt(0.34); f = 545.0*2**(semi/12)
    x = np.sign(np.sin(2*np.pi*f*t)) + 0.8*np.sign(np.sin(2*np.pi*f*1.4815*t))
    x = tp(hp(x), 0.32)
    env = (1-np.exp(-t*900))*np.exp(-t*13.5)
    x = x*env; x /= np.abs(x).max()+1e-9
    _glocke[semi] = x; return x

def kick():
    t = tt(0.46)
    f = 44 + 120*np.exp(-t*30)
    ph = 2*np.pi*np.cumsum(f)/SR
    x = np.sin(ph)*np.exp(-t*7.0)
    klick = rng.normal(0,1,len(t))*np.exp(-t*900)*0.35
    return np.tanh(1.6*(x+klick))/np.tanh(1.6)

def bass(semi, lang=0.95):
    t = tt(lang); f0 = 43.65*2**(semi/12)
    f = f0*(1 + 0.55*np.exp(-t*32))
    ph = 2*np.pi*np.cumsum(f)/SR
    env = (1-np.exp(-t*400))*np.exp(-t*2.1)
    x = np.sin(ph)*env
    return np.tanh(2.4*x)/np.tanh(2.4)        # Uebersteuerung -> hoerbar auf Handys

def clap():
    t = tt(0.26); n = rng.normal(0,1,len(t)); env = np.zeros(len(t))
    for d in (0.0, 0.009, 0.018):
        m = t >= d; env[m] += np.exp(-(t[m]-d)*70)
    env += np.exp(-t*17)*0.6
    x = tp(hp(n*env), 0.42)
    return x/(np.abs(x).max()+1e-9)

def hat(offen=False):
    t = tt(0.22 if offen else 0.06)
    x = hp(hp(rng.normal(0,1,len(t))))*np.exp(-t*(14 if offen else 70))
    return x/(np.abs(x).max()+1e-9)

def crash():
    """Tonaler Einschlag statt Becken-Rauschen: tiefer Schlag plus Akkord."""
    t = tt(1.8); f = 42 + 80*np.exp(-t*12); ph = 2*np.pi*np.cumsum(f)/SR
    stab = sum(np.sin(2*np.pi*f0*h*t)/h for f0 in (87.3, 130.8, 174.6) for h in (1,2,3))
    x = np.sin(ph)*np.exp(-t*2.0) + 0.18*stab*np.exp(-t*2.6)*(1-np.exp(-t*300))
    return x/(np.abs(x).max()+1e-9)

def riser(dauer):
    """Ansteigender Akkord statt Rauschfahne."""
    t = tt(dauer); gl = 2**(t/dauer)
    y = sum(np.sin(2*np.pi*np.cumsum(f0*gl)/SR) for f0 in (349.2, 523.3, 698.5))*(t/dauer)**2.2
    return y/(np.abs(y).max()+1e-9)

# ---------------- Muster ----------------
# Kuhglocken-Melodie ueber zwei Takte, in Halbtoenen um F (Moll/phrygisch)
MEL = [0,None,0,None, 3,None,0,None, 7,None,5,None, 3,None,0,1,
       0,None,0,None, 3,None,0,None, 8,None,7,None, 5,None,3,None]
BASS_POS = [0, 6, 10]
BASS_TON = [[0,0,3],[0,0,-2]]

letzter_takt = int(math.ceil((M0+DAUER)/BAR))+1
for takt in range(-1, letzter_takt):
    m_takt = takt*BAR
    vor_drop = takt < N_INTRO
    ziel = intro if vor_drop else trocken
    # Kuhglocke (laeuft durch – das ist der Wiedererkennungswert)
    for s in range(16):
        n = MEL[(takt % 2)*16 + s]
        if n is not None:
            g = 0.30 if not (vor_drop and LEISE_INTRO) else 0.16
            lege(ziel, m_takt + s*S16, glocke(n), g)
    # Hi-Hats auf Achteln, Wirbel am Taktende jedes zweiten Takts
    for s in range(0,16,2):
        lege(ziel, m_takt + s*S16, hat(), 0.16 if vor_drop else 0.20)
    if takt % 2 == 1:
        for k in range(4):
            lege(ziel, m_takt + 14*S16 + k*S16/2, hat(), 0.12)
    if vor_drop:
        # Im Intro schon ein gedaempfter Bass auf der Eins – der Track lebt sofort
        lege(intro, m_takt, bass(BASS_TON[takt%2][0], 1.4), 0.42 if not LEISE_INTRO else 0.24)
        lege(intro, m_takt + 8*S16, bass(BASS_TON[takt%2][2], 0.8), 0.30 if not LEISE_INTRO else 0.18)
    if not vor_drop:
        # voller Beat nach dem Drop
        for i,s in enumerate(BASS_POS):
            lege(trocken, m_takt + s*S16, kick(), 0.95)
            lege(trocken, m_takt + s*S16, bass(BASS_TON[takt%2][i]), 0.78)
        for s in (4,12):
            lege(trocken, m_takt + s*S16, clap(), 0.55)
        lege(trocken, m_takt + 2*S16, hat(True), 0.10)
    if takt == N_INTRO-1:
        # Aufbau im letzten Takt vor dem Drop: Wirbel wird dichter, Rauschen steigt
        for s in range(8):  lege(trocken, m_takt + s*S16, clap(), 0.10 + 0.03*s)
        for k in range(16): lege(trocken, m_takt + BAR/2 + k*S16/2, clap(), 0.30 + 0.025*k)
        lege(trocken, m_takt, riser(BAR), 0.30)
    if takt == N_INTRO:
        lege(trocken, m_takt, crash(), 0.32)

# Tiefpass vor dem Drop oeffnet sich langsam: dumpf -> klar
gefiltert = np.empty_like(intro); v = 0.0
grenze = int(round((M_DROP - M0)*SR))
for i in range(N):
    if i < grenze:
        f = i/max(1,grenze)
        # schon am Anfang klar hoerbar ("Telefon-Klang"), dann voll offen
        a = 0.17 + (0.60 if not LEISE_INTRO else 0.25)*f**1.4
    else:
        a = 1.0
    v += a*(intro[i]-v); gefiltert[i] = v

mix = gefiltert*1.15 + trocken   # Intro deutlich anheben – die erste Sekunde zaehlt
mix = np.tanh(1.25*mix/ (np.abs(mix).max()+1e-9) * 1.6)/np.tanh(1.25*1.6)
# ganz kurzes Einblenden, damit der erste Sample nicht knackt
mix[:240] *= np.linspace(0,1,240)
mix[-2400:] *= np.linspace(1,0,2400)
mix /= np.abs(mix).max()+1e-9; mix *= 10**(-1.5/20)
st = np.stack([mix, mix],1)
with wave.open(OUT,'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
print(f'{OUT}: {DAUER}s, Drop bei {DROP}s, {N_INTRO} Intro-Takte, 140 BPM')
