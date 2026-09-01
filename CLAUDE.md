# WebWerk Design – Projekt-Regeln

Richard Baumgart, 14 Jahre, Jena. Baut kostenlose Websites für kleine
Handwerks- und Gewerbebetriebe, um Erfahrung zu sammeln.

## Stand: 01.09.2026 – Telefon zuerst, Mail nur mit Erlaubnis

Nach einem Widerspruch nach Art. 21 DSGVO wurde die Arbeitsweise umgestellt.
**Der erste Kontakt läuft immer über das Telefon.** Eine E-Mail folgt nur,
wenn der Betrieb sie am Telefon ausdrücklich erlaubt hat.

Das ist keine Schikane, sondern schlicht die Rechtslage: Kaltakquise per
Telefon ist gegenüber Gewerbebetrieben zulässig, per E-Mail nicht. Mit einer
Erlaubnis aus dem Telefonat ist die Mail dann völlig in Ordnung – und wird
sogar gelesen, weil man schon miteinander gesprochen hat.

## Die vier Regeln

### 1. Eine Mail nur, wenn der Betrieb sie erlaubt hat
Eine Werbemail ohne vorherige Einwilligung ist nach § 7 Abs. 2 Nr. 2 UWG
unzulässig – auch von Betrieb zu Betrieb. Das ist kein Formulierungsproblem
und lässt sich durch keinen noch so guten Text heilen.

Der erlaubte Weg ist immer derselbe:

1. **Anrufen.** Telefonisch ist die Ansprache von Gewerbebetrieben zulässig
   (§ 7 Abs. 2 Nr. 1 UWG, mutmaßliche Einwilligung).
2. **Fragen:** „Darf ich Ihnen das per E-Mail schicken?"
3. **Ja eintragen:** `node scripts/erlaubnis.js "<Firma>" "<E-Mail>"`
4. **Erst dann mailen:** `node scripts/mail-nach-anruf.js "<Firma>"`

`scripts/darf-ich-mailen.sh "<Firma>"` sagt vor jeder Mail, ob es erlaubt ist.
Rückgabe 1 heißt: nicht mailen. Es gibt keinen Schalter, der das überspringt.

Antwortmails an Betriebe, die sich von sich aus gemeldet haben, und Mails an
bestehende Kunden sind etwas anderes und jederzeit in Ordnung.

### 2. Nichts wird veröffentlicht, bevor der Betrieb zustimmt
Kundenseiten liegen in `entwuerfe/` – das ist nicht öffentlich und steht in
`.gitignore`. Erst wenn ein Betrieb am Telefon ausdrücklich zugestimmt hat,
darf seine Seite nach `docs/`.

### 3. Im Impressum steht immer Richard
Solange die Seite Richard gehört, ist **er** der Diensteanbieter nach § 5 DDG
– niemals der Betrieb. Sonst haftet jemand für Inhalte, die er nicht kennt.

### 4. Ein Nein wird sofort umgesetzt
Sagt jemand Nein oder will nicht wieder angerufen werden: Nummer sofort in
`daten/sperrliste.json`, ohne Rückfrage, ohne Überredungsversuch.

## Vor jedem Anruf

```
./scripts/pruefe-anruf.sh "03641 123456"
```
Meldet, ob die Nummer gesperrt ist. Rückgabe 1 heißt: nicht anrufen.

Die Sperrliste enthält **keine Namen und keine lesbaren Nummern**, nur
Prüfsummen. So lässt sich prüfen, ohne die Personen zu speichern.

## Anrufliste erzeugen

```
node scripts/anrufliste.js          # alle
node scripts/anrufliste.js jena     # nur ein Ort
```
Ergebnis: `ANRUFLISTE.md`. In `daten/anrufliste.json` stehen bewusst **keine
E-Mail-Adressen**. Was nicht da ist, kann auch nicht versehentlich
angeschrieben werden.

## Wann eine Seite online gehen darf

Erst wenn der Betrieb ausdrücklich zugestimmt hat. Eintragen mit
`node scripts/erlaubnis.js "<Firma>" "<E-Mail>" --seite-online`.
Ohne dieses Flag bleibt die Seite in `entwuerfe/` und geht nicht nach `docs/`.

Im Impressum steht dann trotzdem Richard, nicht der Betrieb.

## Was am Telefon gesagt wird

Ehrlich und kurz:

> „Guten Tag, mein Name ist Richard Baumgart, ich bin 14 und aus Jena.
> Ich baue kostenlos Websites für Handwerksbetriebe, weil ich Erfahrung
> sammeln möchte. Ich habe gesehen, dass Sie noch keine Seite haben –
> darf ich Ihnen einen Entwurf bauen und zeigen? Das kostet nichts und
> Sie gehen keine Verpflichtung ein."

Nicht sagen: dass schon etwas im Internet steht. Es steht nichts im Internet,
solange der Betrieb nicht zugestimmt hat.

## Was früher falsch war

1. Entwürfe standen **öffentlich** im Netz, mit Name, Anschrift und Telefon –
   ohne Zustimmung des Betriebs.
2. Im Impressum stand **der Betrieb** als Diensteanbieter statt Richard.
3. Es wurde nicht mitgeteilt, woher die Kontaktdaten stammten (Art. 14 DSGVO).
4. Die Mails behaupteten, die Website sei fertig und abrufbar.

## Grundsatz

Keine personenbezogenen Daten Dritter in ein öffentliches Repository.
Weder in `docs/`, noch sonst wo, noch in der Versionsgeschichte.
