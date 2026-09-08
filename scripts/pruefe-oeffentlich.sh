#!/bin/bash
# Pflichtpruefung vor jedem Push. Rueckgabe 1 heisst: nicht pushen.
# Seiten von Betrieben duerfen in docs/ liegen, wenn in daten/anrufliste.json
# "seite_online_erlaubt": true eingetragen ist. Alles andere ist ein Fehler.
cd "$(dirname "$0")/.." || exit 2
fehler=0

# Erlaubte Seiten aus der Kundenliste ableiten
mapfile -t ERLAUBT < <(node -e '
const fs=require("fs");
const l=JSON.parse(fs.readFileSync("daten/anrufliste.json","utf8"));
const seiten=new Set();
for(const b of l){ if(!b.seite_online_erlaubt) continue;
  if(b.mail) seiten.add(b.mail.toLowerCase());
  if(b.tel) seiten.add(String(b.tel).replace(/\D/g,""));
}
console.log([...seiten].join("\n"));' 2>/dev/null)
ist_erlaubt(){ for e in "${ERLAUBT[@]}"; do [ "$1" = "$e" ] && return 0; done; return 1; }

echo "0) Seiten in docs/ ohne eingetragene Zustimmung"
t=""
for f in docs/*.html; do
  b=$(basename "$f")
  case "$b" in index.html|404.html|visitenkarten.html|handzettel.html|handzettel-webwerk.html|fragebogen-besuch.html) continue;; esac
  node -e '
   const fs=require("fs");
   const l=JSON.parse(fs.readFileSync("daten/anrufliste.json","utf8"));
   const html=fs.readFileSync(process.argv[1],"utf8").toLowerCase();
   const ok=l.some(b=>b.seite_online_erlaubt && b.mail && html.includes(b.mail.toLowerCase()));
   process.exit(ok?0:1);' "$f" || t="$t $b"
done
[ -n "$t" ] && { echo "   OHNE ZUSTIMMUNG:"; for x in $t; do echo "     $x"; done; fehler=1; } || echo "   in Ordnung"

echo "1) Fremde E-Mail-Adressen in docs/"
t=""
for m in $(grep -rhoE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}" docs/ 2>/dev/null | grep -v richardbaumgart65 | sort -u); do
  ist_erlaubt "$(echo "$m" | tr 'A-Z' 'a-z')" || t="$t $m"
done
[ -n "$t" ] && { echo "   OHNE ZUSTIMMUNG:"; for x in $t; do echo "     $x"; done; fehler=1; } || echo "   in Ordnung"

echo "2) Fremde Telefonnummern auf Seiten ohne Zustimmung"
t=""
for f in docs/*.html; do
  node -e '
   const fs=require("fs");
   const l=JSON.parse(fs.readFileSync("daten/anrufliste.json","utf8"));
   const html=fs.readFileSync(process.argv[1],"utf8").toLowerCase();
   const ok=l.some(b=>b.seite_online_erlaubt && b.mail && html.includes(b.mail.toLowerCase()));
   process.exit(ok?0:1);' "$f" && continue
  for n in $(grep -ohE "0[0-9]{3,5}[ /-][0-9]{5,9}" "$f" 2>/dev/null | tr -d ' /-' | sort -u | grep -v "015144164431"); do
    t="$t $(basename $f):$n"
  done
done
[ -n "$t" ] && { echo "   PRUEFEN:"; for x in $t; do echo "     $x"; done; fehler=1; } || echo "   in Ordnung"

echo "3) Kundenentwuerfe oder Betriebsdaten im Repository"
t=$(git ls-files 2>/dev/null | grep -E "^(entwuerfe|daten|unterlagen)/|ANRUFLISTE")
[ -n "$t" ] && { echo "   GEFUNDEN:"; echo "$t" | sed 's/^/     /'; fehler=1; } || echo "   in Ordnung"

echo "4) Fremde Server eingebunden (Schriften, Zaehler, Karten)"
t=$(grep -rhoE 'src="https?://[^"]+|href="https?://[^"]+\.(css|js)' docs/*.html 2>/dev/null | sort -u)
[ -n "$t" ] && { echo "   GEFUNDEN:"; echo "$t" | sed 's/^/     /'; fehler=1; } || echo "   in Ordnung"

echo "5) Impressum: auf jeder Kundenseite muss Richard stehen"
t=""
for f in docs/*.html; do
  b=$(basename "$f")
  case "$b" in 404.html|visitenkarten.html|handzettel.html|handzettel-webwerk.html|fragebogen-besuch.html) continue;; esac
  grep -q "Illmitzer Dorfstraße 9" "$f" || t="$t $b"
done
[ -n "$t" ] && { echo "   KEIN EIGENES IMPRESSUM:"; for x in $t; do echo "     $x"; done; fehler=1; } || echo "   in Ordnung"

echo "6) Mailvorlagen: nur die mit Erlaubnispruefung erlaubt"
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
