#!/bin/bash
# Rendert mehrere Videos nacheinander: ./schlange.sh v02 v03 ...
cd "$(dirname "$0")"
for v in "$@"; do
  f=$(ls specs/$v.json); n=$(python3 -c "import json;print(json.load(open('$f'))['name'])")
  ./baue.sh $f render > out/$n/render.log 2>&1 && echo "FERTIG $n" || echo "FEHLER $n"
done
