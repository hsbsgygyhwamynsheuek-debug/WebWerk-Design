# -*- coding: utf-8 -*-
"""
Hypnotischer Ton, der exakt genauso schleift wie das Bild.
Trick: Jede Frequenz ist ein ganzzahliges Vielfaches von 1/T.
Dadurch ist die Welle nach T Sekunden exakt wieder am selben Punkt --
die Schleife hat keinen hoerbaren Uebergang.
"""
import numpy as np, wave

SR, T, RUNDEN = 48000, 1.55, 6
LEN = T*RUNDEN
N   = int(round(SR*LEN)); t = np.arange(N)/SR
f0  = 1.0/T                      # 0.645 Hz -- alles ist ein Vielfaches davon
mix = np.zeros((N,2))

def ton(m, amp, phase=0.0, schwebe=0):
    f = m*f0
    w = np.sin(2*np.pi*f*t + phase)
    if schwebe:                  # Schwebung, ebenfalls ein Vielfaches von f0
        w = w*(1 + 0.25*np.sin(2*np.pi*schwebe*f0*t))
    mix[:,0] += w*amp
    mix[:,1] += np.sin(2*np.pi*f*t + phase + 0.12)*amp

# Grundakkord: Grundton, Quinte, Oktave -- tief und ruhig
ton(100, 0.50, 0.0, 1)           # 64.5 Hz
ton(150, 0.26, 0.7, 1)           # 96.8 Hz
ton(200, 0.20, 1.4, 2)           # 129.0 Hz
ton(300, 0.10, 2.1, 2)           # 193.5 Hz
# Schimmer oben drueber
ton(600, 0.045, 0.3, 3)
ton(900, 0.028, 1.1, 3)

# Ein weicher Puls pro Ringschritt -- Funktion von (t mod T), also periodisch
ph = (t % T)/T
huelle = np.exp(-ph*5.5)*(1-np.exp(-ph*140))
puls = np.sin(2*np.pi*(200*f0)*t)*huelle*0.30
mix[:,0] += puls; mix[:,1] += puls*0.97

# Langsames Atmen, Periode genau T
mix *= (0.82 + 0.18*np.sin(2*np.pi*f0*t))[:,None]

mix /= (np.abs(mix).max()+1e-9); mix *= 10**(-2.0/20)
print('Spitze %.2f dBFS' % (20*np.log10(np.abs(mix).max())))
# Beweis: erste und letzte Periode muessen identisch sein
p = int(round(SR*T))
print('Schleife sauber:', 'JA' if np.allclose(mix[:p], mix[-p:], atol=2e-4) else 'NEIN')
pcm=(np.clip(mix,-1,1)*32767).astype('<i2')
with wave.open('ton.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ton.wav', round(N/SR,3),'s')
