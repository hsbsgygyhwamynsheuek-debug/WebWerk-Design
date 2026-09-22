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

## Design-Skills (ab 15.09.2026)

Bei allem Gestalterischen – Websites, Präsentationen, Handouts, E-Mail-Layouts –
gelten immer diese Skills, ohne dass sie extra angefordert werden müssen:

Von Emil Kowalski (`npx skills@latest add emilkowalski/skills`, liegt in
`.agents/skills/`, verlinkt nach `.claude/skills/`):

- `emil-design-eng` – UI-Politur, Komponenten, die unsichtbaren Details
- `animate`, `review-animations`, `improve-animations`, `animation-vocabulary`
- `apple-design`, `pick-ui-library`, `prototype`

Eigene:

- `impeccable-design` – Abstände, Typografie, Farbe, Kontrast, nichts überlappt
- `taste` – was weggelassen wird, kein KI-Ton, konkret statt Werbesprache

## oh-my-claude-code (ab 20.09.2026)

Die Skills und Agenten aus `Yeachan-Heo/oh-my-claudecode` (MIT) liegen fest im
Repo: 40 Skills in `.claude/skills/`, 19 Agenten in `.claude/agents/`. Sie sind
damit in jeder Sitzung hier verfuegbar, ohne dass etwas installiert werden muss.

Nuetzlich sind vor allem `review`, `verify`, `research`, `plan` und
`minimal-code-discipline`.

Nicht automatisch starten: `autopilot`, `ralph`, `self-improve`, `team`. Die
arbeiten ohne Rueckfrage weiter. In diesem Projekt haengen Kundendaten, Mails
und oeffentliche Seiten dran - hier wird nichts vollautomatisch veroeffentlicht
oder verschickt. Nur auf ausdrueckliche Ansage von Richard.

## Abmahn-Checkliste (ab 21.09.2026)

Gilt fuer jede Seite, die ich baue - eigene wie Kundenseiten. Vor dem
Veroeffentlichen jeden Punkt pruefen.

1. **Datenschutzerklaerung** vorhanden, mit Verantwortlichem und Rechtsgrundlage.
2. **Keine Google Fonts** und keine anderen Schriften, Karten, Videos oder
   Zaehler von fremden Servern. Alles liegt lokal. (LG Muenchen 3 O 17493/20)
3. **Jedes Bild hat ein alt-Attribut**, das beschreibt, was zu sehen ist.
4. **Impressum** nach Paragraph 5 DDG: Richard Baumgart, Illmitzer Dorfstrasse 9,
   07751 Jena, Telefon, E-Mail. Nie der Betrieb.
5. **Widerrufsbelehrung**, sobald ueber die Seite etwas bestellt oder gebucht
   werden kann und der Kunde Verbraucher ist. Reine Visitenkartenseiten
   brauchen keine.
6. **Kein Analytics, keine Cookies.** Wenn doch, erst nach Einwilligung laden -
   nie vorher. (Paragraph 25 TDDG)
7. **Bilder nur mit Lizenz.** Pexels, Unsplash oder eigene Fotos des Betriebs.
   Lizenz und Quelle notieren. Nie ein Bild aus der Google-Suche.
8. **Keine Behauptungen ohne Beleg**: kein "Testsieger", kein "Nummer 1",
   keine erfundenen Jahreszahlen, keine erfundene Mitarbeiterzahl.
9. **Keine erfundenen Bewertungen.** Nur echte, und nur mit Erlaubnis.
10. **Keine offenen Verzeichnisse.** Was hochgeladen wird, darf nicht per
    Direktlink fuer jeden erreichbar sein.

Zusaetzlich immer: Hinweis auf den Einsatz kuenstlicher Intelligenz
(Artikel 50 der Verordnung (EU) 2024/1689).

## hyperpowers (ab 22.09.2026)

Aus `withzombies/hyperpowers` (MIT) liegen 24 Skills in `.claude/skills/` und
5 Agenten in `.claude/agents/`. Der gleichnamige Agent des anderen Plugins
heisst hier `hyper-code-reviewer.md`, damit sich nichts ueberschreibt.

Nuetzlich: `writing-plans`, `verification-before-completion`,
`root-cause-tracing`, `debugging-with-tools`, `review-implementation`.

Nicht installiert: `adkaushik/hyperpowers-claude`. Dieser Installer
entschluesselt ein mitgeliefertes Paket und richtet daraus eine lokale
Quelle ein. Was da entschluesselt wird, laesst sich vorher nicht lesen -
deshalb nicht angefasst.
