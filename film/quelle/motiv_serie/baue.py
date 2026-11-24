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
def ton(f, d, harm=8, ein=0.004, ab=12.0):
    """Streicherartiger Ton aus Obertoenen (saegezahnaehnlich, ohne Rauschen)."""
    x = q(d)
    y = sum(np.sin(2*np.pi*f*hh*x + hh)/hh for hh in range(1, harm + 1))
    return y * (1 - np.exp(-x/ein)) * np.exp(-x*ab)
def kick():
    """Sauberer Kinoschlag: kurz, ohne Verzerrung und ohne langes Abrutschen (kein "Pfff")."""
    x = q(0.45); f = 52 + 30*np.exp(-x*30); ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph) * np.exp(-x*8) * (1 - np.exp(-x*1500))
def klavier(f, d=1.2):
    x = q(d); return np.sin(2*np.pi*f*x) * (1 - np.exp(-x*400)) * np.exp(-x*3)

# Laufende tiefe Streicher (Spiccato) auf Achteln - der Motor jeder Motivationsmusik
AKZ = [1.0, 0.55, 0.75, 0.55, 0.9, 0.55, 0.75, 0.6]
s = 0
while s * BEAT < LEN:
    ts = s * BEAT; akk = AKK[(s // 4) % 4]; ph = phase_bei(ts); I = STAERKE[ph]
    for hh in (0, 0.5):
        k8 = int(s*2 + hh*2) % 8; g = AKZ[k8] * (0.35 + 0.65*I)
        grund = akk[0] - 24 if ph not in ('ruhig', 'drop') else akk[0] - 12
        lege(ton(hz(grund), 0.3, harm=7, ab=11), ts + hh*BEAT, 0.030*g)
        lege(ton(hz(grund + 12), 0.3, harm=5, ab=13), ts + hh*BEAT, 0.018*g)
    # Klavier nur noch als leiser Glanz in den ruhigen Stellen
    if ph in ('ruhig', 'drop') and s % 2 == 0:
        lege(klavier(hz(akk[(s // 2) % 3] + 24)), ts, 0.035)
    # Schlagzeug: sauberer Kick statt Taiko
    tr = TROMMEL[ph]
    if tr and (tr == 1 or s % 2 == 0): lege(kick(), ts, 0.55 * I)
    s += 1
# Breite Streicherflaeche, weicher Einsatz
pad = np.zeros(N)
for k in range(int(LEN / (4*BEAT)) + 1):
    a0 = k*4*BEAT; akk = AKK[k % 4]; i0 = int(a0*SR); i1 = min(N, int((a0 + 4*BEAT + 0.8)*SR))
    if i0 >= N: break
    x = t[i0:i1] - a0
    w = sum(sum(np.sin(2*np.pi*hz(n)*hh*x*(1 + 0.003*dd))/hh for hh in range(1, 6) for dd in (-1, 1)) for n in akk)
    w += sum(np.sin(2*np.pi*hz(akk[0] - 24)*x) for _ in (0,))          # tiefer Bass, rein
    pad[i0:i1] += w * np.clip(x/0.8, 0, 1) * np.clip((4*BEAT + 0.8 - x)/0.8, 0, 1)
env = np.repeat(np.array([intensitaet(v) for v in t[::480]]), 480)[:N]
c = np.concatenate([[0.0], np.cumsum(env)]); w = SR // 2
lo = np.clip(np.arange(N) - w, 0, N); hi = np.clip(np.arange(N) + w, 0, N)
glatt = (c[hi] - c[lo]) / np.maximum(1, hi - lo)
musik += pad * 0.030 * glatt
# Blechblaeser-Anschwellen in Hoehepunkt und Schluss (statt Einschlag mit Abrutschen)
for sz in plan:
    if sz['m'] in ('peak', 'end'):
        d = sz['b'] - sz['a'] + 0.5; x = q(d); akk = AKK[0]
        y = sum(ton(hz(n - 12), d, harm=9, ein=0.5, ab=0.0) for n in akk)
        y *= np.clip((d - x)/0.6, 0, 1)
        lege(y, sz['a'], 0.045)
        lege(kick(), sz['a'], 0.9)
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
