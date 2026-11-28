#!/bin/bash
# Fuehrt fertig gerenderte stumme Videos mit der Phonk-Musik zusammen.
set -e
cd "$(dirname "$0")"
V=../pixar/serie/out
mkdir -p fertig
for n in k1-reveal k2-starren k3-runter k4-pov k5-frage; do
  [ -f "$V/$n-stumm.mp4" ] || { echo "fehlt noch: $n"; continue; }
  ffmpeg -v error -y -i "$V/$n-stumm.mp4" -i "$n.wav" -c:v copy -c:a aac -b:a 192k \
    -ar 48000 -ac 2 -shortest -movflags +faststart "fertig/970-$n.mp4"
  cp "$V/$n-stumm.mp4" "fertig/970-$n-stumm.mp4"
  echo "fertig: 970-$n.mp4"
done
if [ -f "$V/6-bewegt-stumm.mp4" ] && [ -s "$V/6-bewegt-stumm.mp4" ]; then
  ffmpeg -v error -y -i "$V/6-bewegt-stumm.mp4" -i lang-phonk.wav -c:v copy -c:a aac -b:a 192k \
    -ar 48000 -ac 2 -shortest -movflags +faststart "fertig/970-zwei-minuten-bewegt.mp4" && echo "fertig: langer Film"
fi
