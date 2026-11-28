# -*- coding: utf-8 -*-
"""Schnittplan im Beat-Raster (140 BPM). Jeder Schnitt faellt auf einen Schlag."""
import json, math
S='../stimme/'
Z=json.load(open(S+'zeitachse.json')); H=json.load(open(S+'huellkurven.json'))
BEAT=60/140
def zeile(text):
    for r in Z['zeilen']:
        if r['t']==text: return r
    raise KeyError(text)

CAM = {
 'PF':  dict(cx=470,cy=1010,z0=1.62,z1=1.72),
 'PF2': dict(cx=430,cy=985, z0=1.56,z1=1.48),
 'PA':  dict(cx=960,cy=1020,z0=1.62,z1=1.72),
 'REV': dict(cx=762,cy=470, z0=2.28,z1=1.96,kalt=1),
 'ZWEI':dict(cx=690,cy=1000,z0=1.32,z1=1.40),
 'KECU':dict(cx=715,cy=405, z0=2.30,z1=2.42,kalt=1),
 'STIRN':dict(cx=420,cy=830,z0=2.00,z1=2.26),
 'KEND':dict(cx=720,cy=432, z0=2.18,z1=2.40,kalt=1),
}
# (Kamera, Text der Sprachzeile oder None, Mindestschlaege, Markierung)
PLAN = [
 ('PF',   'Dreh dich nicht um.',                         3, None),
 ('PA',   'Warum denn?',                                 3, None),
 ('PF2',  'Die hinten hat neunhundertsiebzig.',          3, None),
 ('REV',  None,                                          4, 'drop'),
 ('ZWEI', 'Sie war schon da, bevor es die Zahlen gab.',  3, None),
 ('KECU', 'Bei null geht das Licht aus.',                3, None),
 ('PF',   'Pfirsich. Deine Zahl.',                       3, None),
 ('STIRN',None,                                          4, 'glitch'),
 ('KEND', 'Sieben. Und. Sechzig.',                       3, 'stille'),
 ('ENDE', None,                                          7, 'ende'),
]
VOR, NACH = 0.10, 0.34
t_beat = 0
shots, reden, marken = [], [], {}
for cam, text, mind, mark in PLAN:
    a = round(t_beat*BEAT, 4)
    n = mind
    if text:
        r = zeile(text)
        n = max(mind, math.ceil((VOR + r['dauer'] + NACH)/BEAT))
        reden.append(dict(a=round(a+VOR,4), d=r['dauer'], w=r['w'], t=text,
                          datei=S+r['datei'], env=H[str(r['i'])]))
    s = dict(a=a, b=round((t_beat+n)*BEAT,4), cam=cam)
    if cam in CAM: s.update(CAM[cam])
    shots.append(s)
    if mark: marken[mark]=a
    t_beat += n
dauer = round(t_beat*BEAT,4)
json.dump(dict(dauer=dauer, beat=BEAT, shots=shots, reden=reden, marken=marken),
          open('plan.json','w'), ensure_ascii=False, indent=1)
for s in shots: print(f"{s['a']:6.2f}–{s['b']:6.2f}s  {s['cam']}")
print('Marken:', marken, '| Gesamt:', dauer, 's')
