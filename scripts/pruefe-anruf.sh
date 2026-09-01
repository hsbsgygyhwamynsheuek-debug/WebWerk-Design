#!/bin/bash
# Vor jedem Anruf: Darf diese Nummer angerufen werden?
# Aufruf: ./scripts/pruefe-anruf.sh "03641 123456"
cd "$(dirname "$0")/.." || exit 2
[ -z "$1" ] && { echo "Aufruf: $0 \"<Telefonnummer>\""; exit 2; }
python3 - "$1" <<'PY'
import json, sys, hashlib
nr = ''.join(c for c in sys.argv[1] if c.isdigit())
if not nr:
    print("Keine Ziffern erkannt."); sys.exit(2)
h = hashlib.sha256(('webwerk-sperre:' + nr).encode()).hexdigest()[:16]
s = json.load(open('daten/sperrliste.json', encoding='utf8'))
for e in s['gesperrt']:
    if e['pruefsumme'] == h:
        print("NICHT ANRUFEN.")
        print("Grund:", e['grund'])
        sys.exit(1)
print("Frei - diese Nummer darf angerufen werden.")
PY
