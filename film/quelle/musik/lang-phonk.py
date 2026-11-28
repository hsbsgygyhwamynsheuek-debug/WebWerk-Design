# -*- coding: utf-8 -*-
"""Stimmen + Phonk fuer den Zwei-Minuten-Film. Vor dem Auftritt der Kartoffel
laeuft der Beat gedaempft; wenn sie spricht, kommt der Drop. Unter den Stimmen
wird die Musik abgesenkt."""
import json, wave, subprocess, numpy as np
SR=48000
S='../stimme/'
Z=json.load(open(S+'zeitachse.json'))
LEN=Z['dauer']; N=int(SR*LEN)
def lies(p):
    with wave.open(p) as f:
        a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(np.float32)/32768
        if f.getnchannels()==2: a=a.reshape(-1,2).mean(1)
    return a
stimmen=np.zeros(N); huell=np.zeros(N)
for r in Z['zeilen']:
    a=lies(S+r['datei']); i0=int(r['a']*SR); i1=min(N,i0+len(a)); a=a[:i1-i0]
    stimmen[i0:i1]+=a; huell[i0:i1]=np.maximum(huell[i0:i1],np.abs(a))
drop=[r['a'] for r in Z['zeilen'] if r['w']=='K'][0]
print('Drop auf dem ersten Wort der Kartoffel:', drop,'s')
import os
if not os.path.exists('lang-beat.wav'):
  subprocess.run(['python3','-I','phonk.py',json.dumps(
    {'dauer':LEN,'drop':drop,'samen':5,'leise_intro':True,'out':'lang-beat.wav'})],check=True)
beat=lies('lang-beat.wav')[:N]
w=int(SR*0.22)
c=np.concatenate([[0.0],np.cumsum(huell)])
lo=np.clip(np.arange(N)-w//2,0,N); hi=np.clip(np.arange(N)+w//2,0,N)
glatt=(c[hi]-c[lo])/np.maximum(1,hi-lo); glatt/=glatt.max()+1e-9
duck=1.0-0.80*np.clip(glatt*3.5,0,1)          # unter Sprache bis -14 dB
stimmen/=np.abs(stimmen).max()+1e-9
mix=stimmen*0.86 + beat*duck*0.34
mix/=np.abs(mix).max()+1e-9; mix*=10**(-1.5/20)
st=np.stack([mix,mix],1)
with wave.open('lang-phonk-roh.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i','lang-phonk-roh.wav','-af',
  'loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','lang-phonk.wav'],check=True)
print('lang-phonk.wav fertig')
