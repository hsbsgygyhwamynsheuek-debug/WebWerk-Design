#!/bin/bash
# Vor JEDER Mail an einen Betrieb: Darf ich das ueberhaupt?
# Aufruf: ./scripts/darf-ich-mailen.sh "Tischlerei Krauss & Sohn GmbH"
# Rueckgabe 1 heisst: nicht mailen.
cd "$(dirname "$0")/.." || exit 2
[ -z "$1" ] && { echo "Aufruf: $0 \"<Firmenname>\""; exit 2; }

python3 - "$1" <<'PY'
import json, sys, hashlib

name = sys.argv[1].strip().lower()
liste = json.load(open('daten/anrufliste.json', encoding='utf8'))
sperre = json.load(open('daten/sperrliste.json', encoding='utf8'))
gesperrt = {e['pruefsumme']: e['grund'] for e in sperre['gesperrt']}

def h(nr):
    return hashlib.sha256(('webwerk-sperre:' + ''.join(c for c in nr if c.isdigit()))
                          .encode()).hexdigest()[:16]

treffer = [b for b in liste if name in b['firma'].lower()]
if not treffer:
    print("Betrieb nicht in der Liste. Erst recherchieren und eintragen.")
    sys.exit(1)
if len(treffer) > 1:
    print("Mehrere Treffer, bitte genauer angeben:")
    for b in treffer:
        print("  -", b['firma'])
    sys.exit(2)

b = treffer[0]
print("Betrieb:", b['firma'], "·", b['ort'])

if h(b['tel']) in gesperrt:
    print("NICHT MAILEN UND NICHT ANRUFEN.")
    print("Grund:", gesperrt[h(b['tel'])])
    sys.exit(1)

if not b.get('mail_erlaubt'):
    print("NICHT MAILEN.")
    print("Es liegt keine Erlaubnis vor. Eine Werbemail ohne vorherige")
    print("Einwilligung ist nach Paragraf 7 Abs. 2 Nr. 2 UWG unzulaessig -")
    print("auch von Betrieb zu Betrieb.")
    print()
    print("So wird eine Erlaubnis daraus:")
    print("  1. Anrufen. Telefonisch ist die Ansprache erlaubt.")
    print("  2. Fragen: \"Darf ich Ihnen das per E-Mail schicken?\"")
    print("  3. Sagt er Ja: eintragen mit")
    print("     node scripts/erlaubnis.js \"" + b['firma'] + "\" \"<E-Mail>\"")
    sys.exit(1)

if not b.get('mail'):
    print("NICHT MAILEN. Erlaubnis liegt vor, aber keine E-Mail-Adresse hinterlegt.")
    sys.exit(1)

print("Mailen ist in Ordnung.")
print("Erlaubnis erteilt am:", b.get('erlaubt_am') or 'ohne Datum')
print("Adresse:", b['mail'])
PY
