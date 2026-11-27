# -*- coding: utf-8 -*-
"""Ton fuer das Ring-Video: jeder Aufprall am Ring spielt den naechsten Ton einer Melodie,
Zusammenstoesse der Baelle einen tiefen Ton, der Sieg einen Akkord. Rein tonal, kein Rauschen.
python3 ring_ton.py <stoesse.json> <ausgabe.wav>"""
import json, sys, wave, numpy as np
SR = 48000
E = json.load(open(sys.argv[1])); DAUER = E['dauer']; N = int(SR * DAUER); t = np.arange(N) / SR
def hz(n): return 440 * 2 ** ((n - 69) / 12)
def q(d): return np.arange(int(SR * d)) / SR
def glocke(f, d=1.1, hell=1.0):
    x = q(d)
    y = np.sin(2*np.pi*f*x) + 0.35*hell*np.sin(2*np.pi*2*f*x)*np.exp(-x*6) + 0.12*hell*np.sin(2*np.pi*3.01*f*x)*np.exp(-x*9)
    return y * (1 - np.exp(-x*900)) * np.exp(-x*3.2)
spur = np.zeros(N)
def lege(sig, ts, g):
    i0 = int(ts*SR); i1 = min(N, i0+len(sig))
    if 0 <= i0 < N: spur[i0:i1] += sig[:i1-i0]*g
# eigene Melodie in a-Moll-Pentatonik, steigt im Verlauf des Videos eine Oktave an (Spannung)
MEL = [69, 72, 76, 74, 72, 76, 79, 76, 74, 72, 69, 72, 74, 76, 81, 79, 76, 74, 76, 72]
k = 0
for s in E['stoesse']:
    if s['art'] == 'ring':
        hoch = 12 if s['t'] > E['tGewinn'] * 0.7 else 0
        lege(glocke(hz(MEL[k % len(MEL)] + hoch), hell=0.6+0.6*s.get('staerke', .5)), s['t'], 0.16 + 0.16*s.get('staerke', .5)); k += 1
    elif s['art'] == 'ball':
        lege(glocke(hz(57), 0.6, 0.4), s['t'], 0.12)
    elif s['art'] == 'sieg':
        for j, n in enumerate([69, 73, 76, 81, 85, 88]):
            lege(glocke(hz(n), 2.4, 1.0), s['t'] + 0.06*j, 0.22)
# leise Flaeche als Boden (a-Moll), steigert sich bis zum Sieg
pad = sum(np.sin(2*np.pi*hz(n)*t) for n in (45, 52, 57, 60, 64)) / 5
pad *= 0.05 + 0.07*np.clip(t / E['tGewinn'], 0, 1)
# Start-Synthhit und Pop beim Siegertext (Sounddesign-Vorbild)
x = q(0.9); hit = sum(np.sin(2*np.pi*hz(n)*x*hh)/hh for n in (45,52,57) for hh in range(1,6))/3*(1-np.exp(-x*800))*np.exp(-x*4.5)
lege(hit, 0.02, 0.35)
xp = q(0.08); lege(np.sin(2*np.pi*np.cumsum(1500*np.exp(-xp*30)+500)/SR)*np.exp(-xp*45), E['tGewinn']+0.15, 0.3)
mix = spur + pad
mix *= np.clip(t/0.3, 0, 1) * np.clip((DAUER - t)/1.2, 0, 1)
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * 0.89
with wave.open(sys.argv[2], 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.stack([mix, mix], 1)*32767).astype('<i2').tobytes())
print('Ring-Toene:', k, '| Dauer', round(DAUER, 2))
