# -*- coding: utf-8 -*-
import json, math, wave, numpy as np
S='../stimme/'
Z=json.load(open(S+'zeitachse.json')); H=json.load(open(S+'huellkurven.json'))
BEAT=60/140
def huelle(p):
    with wave.open(p) as f: a=np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)/32768
    k=48000//25; n=len(a)//k; e=np.abs(a[:n*k]).reshape(n,k).max(1); e/=e.max()+1e-9
    return [round(float(x),3) for x in e], len(a)/48000
def zeile(text, w=None, datei=None):
    if datei:
        e,d=huelle(S+datei); return dict(w=w,t=text,datei=S+datei,dauer=d,env=e)
    for r in Z['zeilen']:
        if r['t']==text: return dict(w=r['w'],t=text,datei=S+r['datei'],dauer=r['dauer'],env=H[str(r['i'])])
    raise KeyError(text)

# Szenen: Bildgroesse 864x1536, Kameras in Bildpixeln
CAM={
 'W2':   dict(sz='s2',cx=432,cy=768, z0=1.27,z1=1.38),
 'PF2':  dict(sz='s2',cx=300,cy=860, z0=1.85,z1=1.98),
 'CU3':  dict(sz='s3',cx=432,cy=640, z0=1.30,z1=1.42),
 'STIRN3':dict(sz='s3',cx=430,cy=470,z0=1.70,z1=1.98),
 'LOW4': dict(sz='s4',cx=410,cy=560, z0=1.42,z1=1.28,kalt=1),
 'LOW4b':dict(sz='s4',cx=410,cy=600, z0=1.30,z1=1.48,kalt=1),
 'DESK': dict(sz='s5',cx=470,cy=880, z0=1.26,z1=1.40),
 'DESK2':dict(sz='s5',cx=470,cy=860, z0=1.40,z1=1.62),
}
PLAN=[
 ('W2',    zeile('Du hast meine gesagt.'),                 3, None),
 ('CU3',   zeile('Tut mir leid.'),                         3, None),
 ('LOW4',  zeile('Dreh dich um.'),                         4, 'drop'),
 ('PF2',   zeile('Nein.'),                                 3, None),
 ('LOW4b', zeile('Dreh dich um.'),                         3, None),
 ('CU3',   zeile('Pfirsich. Deine Zahl.'),                 3, None),
 ('STIRN3',None,                                           4, 'glitch'),
 ('DESK',  zeile('Wer saß hier vorher?','P','zeilen2/wer.wav'),   4, 'stille'),
 ('DESK2', zeile('Einer, der gefragt hat.','K','zeilen2/einer.wav'),5, None),
 ('ENDE',  None,                                           7, 'ende'),
]
VOR,NACH=0.10,0.34
tb=0; shots=[]; reden=[]; marken={}
for cam,r,mind,mark in PLAN:
    a=round(tb*BEAT,4); n=mind
    if r:
        n=max(mind,math.ceil((VOR+r['dauer']+NACH)/BEAT))
        reden.append(dict(a=round(a+VOR,4),d=round(r['dauer'],3),w=r['w'],t=r['t'],datei=r['datei'],env=r['env']))
    s=dict(a=a,b=round((tb+n)*BEAT,4),cam=cam); s.update(CAM.get(cam,{}))
    shots.append(s)
    if mark: marken[mark]=a
    tb+=n
dauer=round(tb*BEAT,4)
json.dump(dict(dauer=dauer,beat=BEAT,shots=shots,reden=reden,marken=marken),
          open('plan.json','w'),ensure_ascii=False,indent=1)
for s in shots: print(f"{s['a']:6.2f}–{s['b']:6.2f}s  {s['cam']}")
print('Marken:',marken,'| Gesamt:',dauer,'s')
