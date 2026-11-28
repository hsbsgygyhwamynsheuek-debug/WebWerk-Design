#!/bin/bash
# baue.sh <spec.json> [render]   -> Ton + Seite, Pruefbogen; mit "render" das fertige Video
set -e
cd "$(dirname "$0")"
N=$(python3 -c "import json,sys;print(json.load(open('$1'))['name'])")
python3 -I ep.py "$1"
O=out/$N
if [ "$2" = "render" ]; then
  node dreh.js $O render
  ffmpeg -v error -y -i $O/stumm.mp4 -i $O/ton.wav -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart $O/$N.mp4
  echo "FERTIG: $O/$N.mp4"
else
  rm -rf $O/probe; node dreh.js $O probe
  ffmpeg -v error -y -pattern_type glob -i "$O/probe/*.png" -filter_complex "scale=250:444,tile=7x1:margin=6:padding=6:color=0x444444" -frames:v 1 $O/bogen.png
  echo "BOGEN: $O/bogen.png"
fi
