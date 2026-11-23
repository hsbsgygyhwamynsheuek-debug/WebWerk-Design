set -e
cd "$(dirname "$0")"
node render3.js
S=../../stimme
ffmpeg -v error -y -i $S/ton-gesamt.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 out/ton-14.wav
ffmpeg -v error -y -i out/5-zwei-minuten-stumm.mp4 -i out/ton-14.wav \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart \
  out/klassenzimmer-5-zwei-minuten.mp4
echo "FERTIG"
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_type,width,height -of default=nw=1 out/klassenzimmer-5-zwei-minuten.mp4
