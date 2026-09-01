# WebWerk Design – Projekt-Regeln

Richard Baumgart, 14 Jahre, Jena. Baut kostenlose Websites für kleine
Handwerks- und Gewerbebetriebe, um Erfahrung zu sammeln.

## Stand: 01.09.2026 – nur noch Telefon

Nach einem Widerspruch nach Art. 21 DSGVO wurde die Arbeitsweise umgestellt.
Richards Entscheidung: **Es werden keine Verkaufsmails mehr geschrieben.**
Kontakt zu Betrieben ausschließlich per Telefon.

Das ist keine Einschränkung, sondern der sichere Weg. Am Telefon merkt man
sofort, ob jemand will oder nicht, und es entsteht nichts Schriftliches, das
falsch verstanden werden kann.

## Die vier Regeln

### 1. Keine Verkaufsmails. Nie.
Es gibt keine Mailvorlage mehr, und es wird keine gebaut. Wer nach einer
fragt, bekommt diesen Hinweis. Antwortmails an Betriebe, die sich von sich
aus gemeldet haben, sind etwas anderes und in Ordnung.

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
