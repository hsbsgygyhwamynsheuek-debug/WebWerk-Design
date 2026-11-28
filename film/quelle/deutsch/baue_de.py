# -*- coding: utf-8 -*-
"""Deutsches Psychologie-Format: Piper-Stimme (kostenlos), Wort-fuer-Wort-Text, S/W-Autobilder, leise Musik.
python3 baue_de.py <video.json> <ausgabeordner>   ->  seite.html + ton.wav (danach mit dreh.js rendern)
Regeln gegen die Viral-Fehler: erstes Wort ab Bild 1, 12-16 s, Frage am Ende."""
import json, os, sys, subprocess
V = json.load(open(sys.argv[1], encoding='utf-8')); A = sys.argv[2]; os.makedirs(A, exist_ok=True)
F = '/tmp/claude-0/-home-user-WebWerk-Design/21ce08ea-274b-522f-8718-d96f1cd65571/scratchpad/film'
BILDER = F + '/deutsch/bilder'
def sh(c): subprocess.run(c, shell=True, check=True)
# Stimme: schneller als normal, praesent
open(A+'/text.txt','w').write(V['text'])
sh(f"{F}/stimme/venv/bin/piper --model {F}/stimme/modelle/de_DE-thorsten-medium.onnx --length_scale {V.get('tempo',0.8)} --sentence_silence 0.1 --output_file {A}/roh.wav < {A}/text.txt 2>/dev/null")
sh(f"ffmpeg -v error -y -i {A}/roh.wav -af 'silenceremove=start_periods=1:start_threshold=-45dB,highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3,aecho=0.8:0.3:25:0.06,loudnorm=I=-15:TP=-1.5' -ar 48000 {A}/stimme.wav")
dauer = float(subprocess.run(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {A}/stimme.wav", shell=True, capture_output=True, text=True).stdout) + 1.0
# Wortzeiten per Spracherkennung
sh(f"ffmpeg -v error -y -i {A}/stimme.wav -ac 1 -ar 16000 -b:a 64k {A}/st.mp3")
sh(f"curl -sS -X POST https://api.elevenlabs.io/v1/speech-to-text -F model_id=scribe_v1 -F language_code=de -F file=@{A}/st.mp3 -o {A}/stt.json")
w = [x for x in json.load(open(A+'/stt.json'))['words'] if x['type'] == 'word']
pink = {p.lower() for p in V['pink']}
W = [{'t': round(x['start']+0.05, 3), 'e': round(x['end']+0.05, 3), 'w': x['text'], 'p': x['text'].strip(',.?!:').lower() in pink} for x in w]
W[0]['t'] = 0.0   # Hook: erstes Wort steht sofort
# leise Musik darunter
m = {"titel":"bett","tonart":V.get('tonart','dunkel'),"bpm":V.get('bpm',92),"drop_stil":True,"laut_db":-14,"stumm_bass":2.0,"sfx":False,
     "marken":[[0,"drums"],[dauer*0.7,"peak"],[dauer-1.5,"end"]],"szenen":[{"typ":"punkt","h":"","pill":"","m":"drums","dauer":dauer}]}
json.dump(m, open(A+'/musik.json','w'))
sh(f"python3 /home/user/WebWerk-Design/film/quelle/motiv_serie/baue.py {A}/musik.json {A}/musik >/dev/null")
sh(f"ffmpeg -v error -y -i {A}/stimme.wav -i {A}/musik/ton.wav -filter_complex \"[0:a]adelay=50|50,apad[v];[1:a]volume=-17dB[m];[v][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{dauer:.2f},afade=t=out:st={dauer-0.8:.2f}:d=0.8,loudnorm=I=-14:TP=-1.0\" -ar 48000 -ac 2 {A}/ton.wav")
sh(f"rm -rf {A}/bilder && ln -s {BILDER} {A}/bilder")
reihe = V.get('bilder', [1,2,3,4])
html = open('/home/user/WebWerk-Design/film/quelle/drei/spotlight_de.html', encoding='utf-8').read()
import re
html = re.sub(r'const W=\[.*?\], D=19;', 'const W=__W__, D=__D__;', html, flags=re.S)
html = html.replace('__W__', json.dumps(W, ensure_ascii=False)).replace('__D__', f'{dauer:.2f}')
for i, b in enumerate(reihe, 1): html = html.replace(f'bilder/b{i}.png)', f'bilder/X{b}.png)')
html = html.replace('bilder/X', 'bilder/b')
open(A+'/seite.html','w',encoding='utf-8').write(html)
print(f"{len(W)} Woerter, {dauer:.1f} s")
