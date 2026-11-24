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
        'atempo=1.05,highpass=f=75,lowpass=f=12000,deesser=i=0.7:m=0.5:f=0.5:s=o,'
        'equalizer=f=180:t=q:w=1:g=2,equalizer=f=2800:t=q:w=1.2:g=2,'
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
    dauer = max(1.9, d + 0.45 + sz.get('pause', 0.2))
    anzeige = re.sub(r'\[[^\]]*\]\s*', '', sz['vo']).strip()
    plan.append(dict(sz, m=phase, vo=anzeige, a=round(zeit, 3), b=round(zeit + dauer, 3),
                     vo_a=round(zeit + 0.18, 3), vo_d=round(d, 3), datei=p))
    zeit += dauer
LEN = round(zeit, 3); N = int(SR * LEN); t = np.arange(N) / SR

stim = np.zeros(N)
for s in plan:
    a = lies(s['datei']); laut = a[np.abs(a) > 0.02]; a *= 10 ** (-13 / 20) / np.sqrt((laut ** 2).mean())
    i0 = int(s['vo_a'] * SR); i1 = min(N, i0 + len(a)); stim[i0:i1] += a[:i1 - i0]

# ---------------- epische Musik (rein tonal, kein Rauschen) ----------------
STAERKE = dict(ruhig=0.45, drums=0.65, peak=1.0, drop=0.30, build=0.75, end=1.0)
TROMMEL = dict(ruhig=0, drums=2, peak=1, drop=0, build=1, end=1)      # 0 aus, 2 = auf 1+3, 1 = jeder Schlag
def phase_bei(ts):
    for s in reversed(plan):
        if ts >= s['a']: return s['m']
    return plan[0]['m']
def intensitaet(ts): return STAERKE[phase_bei(ts)]

TONARTEN = {   # MIDI-Grundtoene der Dreiklaenge
    'moll':   [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],   # Am F C G
    'dunkel': [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]],   # Dm Bb F C
    'heroisch': [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]], # Em C G D
}
AKK = TONARTEN[S.get('tonart', 'moll')]
BPM = S.get('bpm', 92); BEAT = 60 / BPM
def hz(n): return 440 * 2 ** ((n - 69) / 12)
musik = np.zeros(N)
def lege(sig, ts, g):
    i0 = int(ts * SR); i1 = min(N, i0 + len(sig))
    if 0 <= i0 < N: musik[i0:i1] += sig[:i1 - i0] * g
def q(d): return np.arange(int(SR * d)) / SR
def klavier(f, d=1.6):
    x = q(d)
    return (np.sin(2*np.pi*f*x) + 0.5*np.sin(4*np.pi*f*x)*np.exp(-x*2) + 0.2*np.sin(6*np.pi*f*x)*np.exp(-x*4)) \
        * (1 - np.exp(-x*800)) * np.exp(-x*2.2)
def taiko(f0=58):
    x = q(0.9); f = f0 * (1 + 0.9*np.exp(-x*30)); ph = 2*np.pi*np.cumsum(f)/SR
    return np.tanh(2.0 * (np.sin(ph)*np.exp(-x*5.5) + 0.25*np.sin(2*ph)*np.exp(-x*14)))
def schlag():
    x = q(2.6); f = 40 + 90*np.exp(-x*12); ph = 2*np.pi*np.cumsum(f)/SR
    b = np.sin(ph) * np.exp(-x*1.8)
    grund = AKK[0][0] - 24
    stab = sum(np.sin(2*np.pi*hz(n)*x*h)/h for n in (grund, grund+7, grund+12, grund+19) for h in (1, 2, 3)) \
        * np.exp(-x*2.4) * (1 - np.exp(-x*300))
    return np.tanh(1.3 * (b + 0.22*stab))

s = 0
while s * BEAT < LEN:
    ts = s * BEAT; akk = AKK[(s // 4) % 4]; I = intensitaet(ts); tr = TROMMEL[phase_bei(ts)]
    for h in (0, 0.5):
        ton = akk[[0, 2, 1, 2][(s*2 + int(h*2)) % 4]] + 12
        lege(klavier(hz(ton)), ts + h*BEAT, 0.13 * (0.6 + 0.4*I))
    if tr and (tr == 1 or s % 2 == 0): lege(taiko(), ts, 0.42 * I)
    if tr == 1 and s % 4 == 3: lege(taiko(84), ts + BEAT*0.5, 0.25 * I)
    s += 1
pad = np.zeros(N)
for k in range(int(LEN / (4*BEAT)) + 1):
    a0 = k*4*BEAT; akk = AKK[k % 4]; i0 = int(a0*SR); i1 = min(N, int((a0 + 4*BEAT + 0.6)*SR))
    if i0 >= N: break
    x = t[i0:i1] - a0
    w = sum(sum(np.sin(2*np.pi*hz(n-12)*h*x*(1 + 0.002*dd))/h for h in range(1, 7) for dd in (-1, 1)) for n in akk)
    pad[i0:i1] += w * np.clip(x/0.5, 0, 1) * np.clip((4*BEAT + 0.6 - x)/0.5, 0, 1)
env = np.repeat(np.array([intensitaet(v) for v in t[::480]]), 480)[:N]
c = np.concatenate([[0.0], np.cumsum(env)]); w = SR // 2
lo = np.clip(np.arange(N) - w, 0, N); hi = np.clip(np.arange(N) + w, 0, N)
musik += pad * 0.035 * (c[hi] - c[lo]) / np.maximum(1, hi - lo)
# Riser vor jedem Hoehepunkt, Einschlag auf Hoehepunkt und Schluss
for sz in plan:
    if sz['m'] in ('peak', 'end') and (sz is plan[0] or plan[plan.index(sz) - 1]['m'] != sz['m']):
        x = q(1.8); gl = 2 ** (x / 1.8)
        r = sum(np.sin(2*np.pi*np.cumsum(hz(n + 12)*gl)/SR) for n in AKK[0]) * (x/1.8)**2.2
        lege(r / np.abs(r).max(), sz['a'] - 1.8, 0.22)
        lege(schlag(), sz['a'], 0.9 if sz['m'] == 'peak' else 1.0)
# Musik geht unter der Stimme nur etwas zurueck
h = np.abs(stim); w = int(SR*0.2); c = np.concatenate([[0.0], np.cumsum(h)])
lo = np.clip(np.arange(N) - w//2, 0, N); hi = np.clip(np.arange(N) + w//2, 0, N)
g = (c[hi] - c[lo]) / np.maximum(1, hi - lo); g /= g.max() + 1e-9
musik *= 1 - 0.40*np.clip(g*3, 0, 1)
mix = stim + musik*0.85
mix *= np.clip((LEN - t)/1.0, 0, 1)
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
