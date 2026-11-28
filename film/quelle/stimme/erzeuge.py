# -*- coding: utf-8 -*-
"""Synthetisiert jede Zeile, verschiebt die Tonhöhe und misst die Dauer."""
import subprocess, json, os, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drehbuch import ZEILEN, STIMMEN

PY_ENV = './venv/bin/python'
erg = []
for i,(w, text, pause) in enumerate(ZEILEN):
    st = STIMMEN[w]
    roh  = f'zeilen/{i:02d}_roh.wav'
    fert = f'zeilen/{i:02d}.wav'
    subprocess.run([PY_ENV,'-I','-m','piper','-m',f'modelle/{st["modell"]}',
                    '--length-scale',str(st['laenge']),
                    '--noise-scale','0.60','--noise-w-scale','0.80',
                    '-f',roh], input=text.encode('utf-8'), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(roh) as f: sr = f.getframerate()
    h = st['hoehe']
    # Tonhöhe verschieben, Länge dabei beibehalten
    filt = (f'asetrate={int(sr*h)},aresample=48000,'
            f'atempo={1/h:.6f},'
            f'highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=8:release=140,'
            f'alimiter=limit=0.95')
    subprocess.run(['ffmpeg','-v','error','-y','-i',roh,'-af',filt,
                    '-ar','48000','-ac','1',fert], check=True)
    with wave.open(fert) as f: d = f.getnframes()/f.getframerate()
    erg.append(dict(i=i, w=w, t=text, datei=fert, dauer=round(d,3), pause=pause))
    print(f'{i:02d} {w} {d:5.2f}s  {text}')

# Zeitachse: Zeile, Pause, Zeile ...
zeit = 1.2        # ruhiger Vorlauf
for r in erg:
    r['a'] = round(zeit,3)
    zeit += r['dauer'] + r['pause']
gesamt = round(zeit + 4.6, 2)      # Platz für die Schlusskarte
json.dump(dict(zeilen=erg, dauer=gesamt, ende=round(zeit+0.3,2)),
          open('zeitachse.json','w'), ensure_ascii=False, indent=1)
print(f'\nGesamtlänge: {gesamt} s, Schlusskarte ab {round(zeit+0.3,2)} s')
