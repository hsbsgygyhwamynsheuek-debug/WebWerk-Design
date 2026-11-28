# -*- coding: utf-8 -*-
import subprocess, wave, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drehbuch import STIMMEN
NEU=[('P','Wer saß hier vorher?','zeilen2/wer.wav'),
     ('K','Einer, der gefragt hat.','zeilen2/einer.wav')]
for w,text,ziel in NEU:
    st=STIMMEN[w]; roh=ziel.replace('.wav','_roh.wav')
    subprocess.run(['./venv/bin/python','-I','-m','piper','-m',f'modelle/{st["modell"]}',
        '--length-scale',str(st['laenge']*(1.08 if w=='P' else 1.10)),
        '--noise-scale','0.60','--noise-w-scale','0.80','-f',roh],
        input=text.encode(),check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    sr=wave.open(roh).getframerate(); h=st['hoehe']
    subprocess.run(['ffmpeg','-v','error','-y','-i',roh,'-af',
        f'asetrate={int(sr*h)},aresample=48000,atempo={1/h:.6f},highpass=f=70,'
        'acompressor=threshold=-18dB:ratio=3:attack=8:release=140,alimiter=limit=0.95',
        '-ar','48000','-ac','1',ziel],check=True)
    with wave.open(ziel) as f: print(f'{w} {f.getnframes()/f.getframerate():.2f}s  {text}')
