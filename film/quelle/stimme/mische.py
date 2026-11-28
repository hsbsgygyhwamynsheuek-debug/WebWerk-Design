# -*- coding: utf-8 -*-
"""Legt alle Sprachzeilen auf die Zeitachse, mischt das Spannungsbett
darunter und senkt es ab, solange jemand spricht."""
import json, wave, subprocess, numpy as np

SR = 48000
Z  = json.load(open('zeitachse.json'))
LEN = Z['dauer']; N = int(SR*LEN)
stimmen = np.zeros(N)
huell   = np.zeros(N)          # wo gesprochen wird

def lies(p):
    with wave.open(p) as f:
        a = np.frombuffer(f.readframes(f.getnframes()), '<i2').astype(np.float32)/32768
        if f.getnchannels()==2: a = a.reshape(-1,2).mean(1)
        assert f.getframerate()==SR, (p, f.getframerate())
    return a

ENVS = {}
for r in Z['zeilen']:
    a = lies(r['datei'])
    i0 = int(r['a']*SR); i1 = min(N, i0+len(a)); a = a[:i1-i0]
    stimmen[i0:i1] += a
    huell[i0:i1] = np.maximum(huell[i0:i1], np.abs(a))
    # Lautstärkeverlauf der Zeile, 25 Werte je Sekunde, für die Zahl-Pulsierung
    k = max(1, SR//25)
    n = len(a)//k
    e = np.abs(a[:n*k]).reshape(n,k).max(1)
    e = e/(e.max()+1e-9)
    ENVS[r['i']] = [round(float(x),3) for x in e]

# Spannungsbett bauen
wendepunkte = []
for r in Z['zeilen']:
    if any(s in r['t'] for s in ['neunhundertsiebzig','Licht aus','Sie steht auf',
                                 'Sieben. Und. Sechzig.','Dreh dich um.','achtundsechzig']):
        wendepunkte.append(round(r['a'],2))
wendepunkte = sorted(set(wendepunkte))[:8] + [Z['ende']]
subprocess.run(['python3','-I','ton-spannung.py',
    json.dumps({'dauer':LEN,'cuts':wendepunkte,'out':'bett.wav'})], check=True)
bett = lies('bett.wav')[:N]
if len(bett) < N: bett = np.pad(bett,(0,N-len(bett)))

# Bett absenken, solange gesprochen wird (einfacher Ducker mit weicher Flanke)
w = int(SR*0.18)
glatt = np.convolve(huell, np.ones(w)/w, mode='same')
glatt = glatt/(glatt.max()+1e-9)
duck  = 1.0 - 0.72*np.clip(glatt*3.2, 0, 1)

stimmen /= (np.abs(stimmen).max()+1e-9)
mix = stimmen*0.82 + bett*duck*0.42
mix /= (np.abs(mix).max()+1e-9); mix *= 10**(-1.5/20)
st = np.stack([mix, mix],1)
pcm = (np.clip(st,-1,1)*32767).astype('<i2')
with wave.open('ton-gesamt.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(pcm.tobytes())
json.dump(ENVS, open('huellkurven.json','w'))
print('ton-gesamt.wav', round(N/SR,2),'s | Wendepunkte:', wendepunkte)
