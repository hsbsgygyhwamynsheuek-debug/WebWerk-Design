# -*- coding: utf-8 -*-
"""Serien-Baukasten fuer englische Motivationsvideos.

    python3 baue.py <skript.json> <ausgabeordner>

Pro Szene im Skript:
  typ   Bildtyp aus vorlage.html (graph, akku, uhr, kreis, ringe, gruppe, ...)
  h     Ueberschrift, pill: Etikett, vo: Sprechtext mit ElevenLabs-v3-Tags
  m     Musikphase: ruhig | drums | peak | drop | build | end  (gilt bis zur naechsten Angabe)
  pause Extra-Luft nach dem Satz (Sekunden)
Schreibt ton.wav, plan.json und seite.html in den Ausgabeordner.
Gesprochene Saetze werden zwischengespeichert: ein Neubau kostet keine Zeichen.
"""
import json, os, re, sys, wave, hashlib, subprocess, numpy as np
HIER = os.path.dirname(os.path.abspath(__file__))
SKRIPT, AUS = sys.argv[1], sys.argv[2]
CACHE = os.environ.get('EL_CACHE', os.path.join(AUS, '..', 'el-cache'))
os.makedirs(CACHE, exist_ok=True); os.makedirs(AUS, exist_ok=True)
SR = 48000
S = json.load(open(SKRIPT, encoding='utf-8'))
STIMME = S.get('stimme', 'SOYHLrjzK2X1ezoPC6cr')       # Harry (ElevenLabs, vorgefertigt)

def lies(p):
    with wave.open(p) as f:
        a = np.frombuffer(f.readframes(f.getnframes()), '<i2').astype(np.float32) / 32768
        if f.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    return a

def sprich(text):
    h = hashlib.md5((STIMME + '|v3|' + text).encode()).hexdigest()[:12]
    mp3 = os.path.join(CACHE, f'{h}.mp3'); wav = os.path.join(CACHE, f'{h}.wav')
    if not os.path.exists(mp3):
        req = os.path.join(CACHE, 'req.json')
        json.dump({'text': text, 'model_id': 'eleven_v3', 'voice_settings': {'stability': 0.0}}, open(req, 'w'))
        code = subprocess.run(['curl', '-sS', '-X', 'POST',
            f'https://api.elevenlabs.io/v1/text-to-speech/{STIMME}?output_format=mp3_44100_128',
            '-H', 'Content-Type: application/json', '--data', '@' + req, '-o', mp3, '-w', '%{http_code}'],
            capture_output=True, text=True).stdout
        if code != '200':
            msg = open(mp3, errors='replace').read()[:200]; os.remove(mp3)
            raise SystemExit(f'ElevenLabs HTTP {code}: {msg}')
    # Stimmkette ohne Rauschquellen: De-Esser gegen scharfe S-Laute, Gate fuer stille Pausen
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-af',
        'silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.12:stop_threshold=-45dB:stop_silence=0.1,'
        'atempo=1.2,highpass=f=90,lowpass=f=14000,deesser=i=0.35:m=0.5:f=0.5:s=o,'
        'equalizer=f=2800:t=q:w=1.2:g=2,highshelf=f=6000:g=3,'
        'acompressor=threshold=-22dB:ratio=3.5:attack=4:release=120:makeup=3,'
        'agate=threshold=0.012:ratio=6:attack=4:release=140,'
        'aecho=0.8:0.35:28|47:0.08|0.05,alimiter=limit=0.95',
        '-ar', str(SR), '-ac', '1', wav], check=True)
    return wav

# ---------------- Zeitplan aus den gesprochenen Saetzen ----------------
zeit = 0.25; plan = []; phase = 'ruhig'
for sz in S['szenen']:
    phase = sz.get('m', phase)
    p = sprich(sz['vo']); d = len(lies(p)) / SR
    dauer = max(1.3, d + 0.12 + sz.get('pause', 0.0))   # wie im Vorbild: Satz an Satz, kaum Luft
    anzeige = re.sub(r'\[[^\]]*\]\s*', '', sz['vo']).strip()
    plan.append(dict(sz, m=phase, vo=anzeige, a=round(zeit, 3), b=round(zeit + dauer, 3),
                     vo_a=round(zeit + 0.04, 3), vo_d=round(d, 3), datei=p))
    zeit += dauer
LEN = round(zeit, 3); N = int(SR * LEN); t = np.arange(N) / SR

stim = np.zeros(N)
for s in plan:
    a = lies(s['datei']); laut = a[np.abs(a) > 0.02]; a *= 10 ** (-13 / 20) / np.sqrt((laut ** 2).mean())
    i0 = int(s['vo_a'] * SR); i1 = min(N, i0 + len(a)); stim[i0:i1] += a[:i1 - i0]

# ---------------- Motivationsmusik, gebaut nach dem 1,5-Mio-Vorbild ----------------
# Gemessen am Vorbild: ~96 BPM, Cis-Moll/E-Dur, Sub-Bass auf E1 (41 Hz), 86 % der Energie unter 250 Hz,
# Pegel durchgehend gleich. Die Musik traegt von unten und laesst den Sprachbereich frei.
STAERKE = dict(ruhig=0.80, drums=0.90, peak=1.0, drop=0.65, build=0.92, end=1.0)
TROMMEL = dict(ruhig=2, drums=2, peak=1, drop=0, build=1, end=1)      # 0 aus, 2 = auf 1+3, 1 = jeder Schlag
def phase_bei(ts):
    for s in reversed(plan):
        if ts >= s['a']: return s['m']
    return plan[0]['m']
def intensitaet(ts): return STAERKE[phase_bei(ts)]
# Cis-Moll – A – E – H (vi–IV–I–V in E): die klassische emotionale Motivations-Folge, je Video transponiert
VERSATZ = dict(moll=0, dunkel=-2, heroisch=3).get(S.get('tonart', 'moll'), 0)
AKK = [[n + VERSATZ for n in a] for a in ([61, 64, 68], [57, 61, 64], [52, 56, 59], [59, 63, 66])]
BPM = S.get('bpm', 96); BEAT = 60 / BPM; TAKT = 4 * BEAT
def hz(n): return 440 * 2 ** ((n - 69) / 12)
def q(d): return np.arange(int(SR * d)) / SR
unten = np.zeros(N); oben = np.zeros(N)
def lege(ziel, sig, ts, g):
    i0 = int(ts * SR); i1 = min(N, i0 + len(sig))
    if 0 <= i0 < N: ziel[i0:i1] += sig[:i1 - i0] * g
def basston(n):                      # Grundton in die Lage 38-76 Hz legen (wie E1 im Vorbild)
    f = hz(n)
    while f > 76: f /= 2
    while f < 38: f *= 2
    return f
def sub808(f, d):
    x = q(d); ff = f * (1 + 0.05*np.exp(-x*40)); ph = 2*np.pi*np.cumsum(ff)/SR
    y = np.sin(ph) + 0.35*np.sin(2*ph) + 0.12*np.sin(3*ph)       # Obertoene: auch auf Handys hoerbar
    return y * (1 - np.exp(-x*200)) * np.exp(-x*0.9) * np.clip((d - x)/0.05, 0, 1)
def kick():
    x = q(0.35); f = 55 + 35*np.exp(-x*35); ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph) * np.exp(-x*9) * (1 - np.exp(-x*1500))
def glocke(f):
    x = q(1.4); return (np.sin(2*np.pi*f*x) + 0.25*np.sin(4*np.pi*f*x)*np.exp(-x*3)) * (1 - np.exp(-x*600)) * np.exp(-x*2.6)
MOTIV = [(0, 0), (0.75, 1), (1.5, 2), (2.5, 1), (3.0, 2), (3.5, 0)]   # (Schlag im Takt, Akkordton)
k = 0
while k * TAKT < LEN:
    t0 = k * TAKT; akk = AKK[k % 4]; f = basston(akk[0])
    for hh in range(4):
        ts = t0 + hh*BEAT; ph = phase_bei(ts); I = STAERKE[ph]; tr = TROMMEL[ph]
        if tr and (tr == 1 or hh % 2 == 0): lege(unten, kick(), ts, 0.8 * I)
    I = intensitaet(t0)
    if phase_bei(t0) != 'drop':
        lege(unten, sub808(f, 2.5*BEAT), t0, I)
        lege(unten, sub808(f, 1.5*BEAT), t0 + 2.5*BEAT, 0.85 * I)
    else:
        lege(unten, sub808(f, TAKT), t0, 0.6)
    for sch, ti in MOTIV:
        lege(oben, glocke(hz(akk[ti] + 12)), t0 + sch*BEAT, 0.5 if sch == 0 else 0.35)
    k += 1
# warme Flaeche, wenige Obertoene, weicher Einsatz
for k in range(int(LEN / TAKT) + 1):
    a0 = k*TAKT; akk = AKK[k % 4]; i0 = int(a0*SR); i1 = min(N, int((a0 + TAKT + 0.8)*SR))
    if i0 >= N: break
    x = t[i0:i1] - a0
    w = sum(sum(np.sin(2*np.pi*hz(n)*hh*x*(1 + 0.003*dd))*(1, 0.25, 0.08)[hh-1] for hh in (1, 2, 3) for dd in (-1, 1)) for n in akk)
    oben[i0:i1] += 0.5 * w * np.clip(x/0.9, 0, 1) * np.clip((TAKT + 0.8 - x)/0.8, 0, 1)
env = np.repeat(np.array([intensitaet(v) for v in t[::480]]), 480)[:N]
c = np.concatenate([[0.0], np.cumsum(env)]); w = SR // 2
lo = np.clip(np.arange(N) - w, 0, N); hi = np.clip(np.arange(N) + w, 0, N)
oben *= (c[hi] - c[lo]) / np.maximum(1, hi - lo)
# ---- Pegel exakt auf das Vorbild einstellen (Messung in Frequenzbaendern) ----
def band(x, lo_, hi_):
    X = np.abs(np.fft.rfft(x))**2; f = np.fft.rfftfreq(len(x), 1/SR)
    return 10*np.log10(X[(f >= lo_) & (f < hi_)].sum() + 1e-12)
aktiv = np.abs(stim) > 1e-4
STIMME_MITTE = band(stim, 250, 4000) - 10*np.log10(aktiv.mean())
UNTEN_ZIEL = S.get('bass_db', -1.0)        # Vorbild: Musik-Bass +0,7 dB gegenueber Sprach-Mitten
OBEN_ZIEL = S.get('mitte_db', -11.0)       # Mitten der Musik deutlich unter der Stimme
unten *= 10**((STIMME_MITTE + UNTEN_ZIEL - band(unten, 30, 250))/20)
oben *= 10**((STIMME_MITTE + OBEN_ZIEL - band(oben, 250, 4000))/20)
musik = unten + oben
# nur sanft unter der Stimme zurueck - das Vorbild hat einen gleichmaessigen Pegel
h = np.abs(stim); w = int(SR*0.2); c = np.concatenate([[0.0], np.cumsum(h)])
lo = np.clip(np.arange(N) - w//2, 0, N); hi = np.clip(np.arange(N) + w//2, 0, N)
g = (c[hi] - c[lo]) / np.maximum(1, hi - lo); g /= g.max() + 1e-9
musik *= 1 - 0.20*np.clip(g*3, 0, 1)
mix = stim + musik
mix *= np.clip((LEN - t)/1.2, 0, 1)
mix = mix / np.abs(mix).max() * 10**(-1/20)
mixp = os.path.join(AUS, 'mix.wav')
with wave.open(mixp, 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(np.stack([mix, mix], 1), -1, 1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mixp, '-af', 'loudnorm=I=-13:TP=-1.0:LRA=8',
                '-ar', '48000', os.path.join(AUS, 'ton.wav')], check=True)
P = dict(dauer=LEN, titel=S.get('titel', ''), szenen=[{k: v for k, v in s.items() if k != 'datei'} for s in plan])
json.dump(P, open(os.path.join(AUS, 'plan.json'), 'w'), ensure_ascii=False)
html = open(os.path.join(HIER, 'vorlage.html'), encoding='utf-8').read().replace('__PLAN__', json.dumps(P, ensure_ascii=False))
open(os.path.join(AUS, 'seite.html'), 'w', encoding='utf-8').write(html)
zeichen = sum(len(sz['vo']) for sz in S['szenen'])
for s in plan: print(f"{s['a']:6.2f}–{s['b']:6.2f} {s['m']:6s} {s['typ']:8s} {s['vo']}")
print('Gesamt', LEN, 's |', zeichen, 'Zeichen im Skript')
