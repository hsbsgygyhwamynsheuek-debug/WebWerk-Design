#!/bin/bash
# Pflichtpruefung vor jedem Push. Rueckgabe 1 heisst: nicht pushen.
cd "$(dirname "$0")/.." || exit 2
fehler=0

echo "1) Fremde E-Mail-Adressen in docs/"
t=$(grep -rhoE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}" docs/ 2>/dev/null \
    | grep -v richardbaumgart65 | sort -u)
[ -n "$t" ] && { echo "   GEFUNDEN:"; echo "$t" | sed 's/^/     /'; fehler=1; } || echo "   in Ordnung"

echo "2) Fremde Telefonnummern in docs/"
t=$(grep -rhoE "0[0-9]{3,5}[ /-]?[0-9]{5,9}" docs/*.html 2>/dev/null \
    | tr -d ' /-' | sort -u | grep -v "015144164431")
[ -n "$t" ] && { echo "   GEFUNDEN:"; echo "$t" | sed 's/^/     /'; fehler=1; } || echo "   in Ordnung"

echo "3) Kundenentwuerfe oder Betriebsdaten im Repository"
t=$(git ls-files 2>/dev/null | grep -E "^(entwuerfe|daten|unterlagen)/|ANRUFLISTE")
[ -n "$t" ] && { echo "   GEFUNDEN:"; echo "$t" | sed 's/^/     /'; fehler=1; } || echo "   in Ordnung"

echo "4) Fremde Server eingebunden (Schriften, Zaehler, Karten)"
t=$(grep -rhoE 'src="https?://[^"]+|href="https?://[^"]+\.(css|js)' docs/*.html 2>/dev/null | sort -u)
[ -n "$t" ] && { echo "   GEFUNDEN:"; echo "$t" | sed 's/^/     /'; fehler=1; } || echo "   in Ordnung"

echo "5) Mailvorlagen: nur die mit Erlaubnispruefung erlaubt"
schlecht=$(ls scripts 2>/dev/null | grep -iE "^mail" | grep -v "^mail-nach-anruf.js$")
if [ -n "$schlecht" ]; then
  echo "   NICHT ERLAUBTE VORLAGE:"; echo "$schlecht" | sed 's/^/     /'; fehler=1
elif [ -f scripts/mail-nach-anruf.js ] && ! grep -q "mail_erlaubt" scripts/mail-nach-anruf.js; then
  echo "   mail-nach-anruf.js prueft die Erlaubnis nicht mehr"; fehler=1
else
  echo "   in Ordnung"
fi

echo
[ $fehler -eq 0 ] && echo "ALLES SAUBER - pushen ist in Ordnung." || echo "NICHT PUSHEN."
exit $fehler
