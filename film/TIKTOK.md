# TikTok-Formate

Sechs kurze Videos, 1080 × 1920, **ohne Ton**. Das ist Absicht: Ein
Trend-Sound aus der TikTok-Bibliothek wirkt stärker als jede eigene
Tonspur, und den legst du erst in der App drüber.

Alle halten die sicheren Zonen ein — rechts 140 px für die Knöpfe,
unten 420 px für Text, Name und Sound. Da steht nie etwas Wichtiges.

## Die sechs

| Datei | Länge | Mechanik | Vorschlag für die Beschriftung |
|---|---|---|---|
| `tiktok-a-loop` | 8 s | **Nahtlose Schleife.** Bild bei 0 s und bei 8 s sind pixelgleich — geprüft. Läuft endlos weiter, ohne dass man den Übergang sieht. | „Ich komm hier nicht raus 🌀" + ruhiger Trend-Sound |
| `tiktok-b-quadrate` | 14 s | **Kommentar-Köder.** Fast alle sagen 16. Es sind 30. | „Schreib deine Zahl, bevor du weiterschaust 👀" |
| `tiktok-c-stroop` | 13 s | **Mitmachen.** Farbe sagen, nicht das Wort. Funktioniert wirklich schlecht — darum ist es lustig. | „Wie weit kommst du ohne Fehler?" |
| `tiktok-d-mathe` | 14 s | **„Wie geht das?"** Kommt immer auf 5 raus, egal welche Zahl. | „Denk dir eine Zahl. Ich sag dir, was rauskommt." |
| `tiktok-e-reaktion` | 12 s | **Mitmachen + Vergleichen.** Leute schreiben ihre Zeit in die Kommentare. | „Wie schnell bist du? ms in die Kommentare 👇" |
| `tiktok-f-fehler` | 11 s | **Suchbild.** Einer von 42 ist anders. | „Nur mit gutem Auge. Findest du's in 5 Sekunden?" |

## Warum gerade diese Formate

TikTok misst vor allem, **wie lange** jemand schaut und **ob er
reagiert**. Darauf zielt jedes der sechs:

- Die Schleife wird mehrfach gesehen, ohne dass jemand etwas tut.
- Rätsel und Tests erzeugen Kommentare — und Kommentare zählen mehr
  als Likes.
- Alle sechs haben den Haken in der ersten halben Sekunde: Die Frage
  steht sofort im Bild, es gibt kein Intro.

## Was ehrlich dazugehört

**Niemand kann Reichweite versprechen, ich auch nicht.** Das hier sind
Formate, die die Mechanik bedienen — ob ein Video läuft, entscheiden
Timing, Sound und Glück. Rechne damit, dass fünf untergehen und eins
läuft. Dann poste von dem einen eine Variante nach.

Zweiter Punkt, unbequem: **Reichweite ohne Bezug zu deinem Geschäft
bringt dir keine Kunden.** Wer wegen eines Suchbilds folgt, will keine
Website kaufen. Deshalb ist in fünf der sechs Videos unten links ein
kleines „W" — mehr geht nicht, ohne die Formate kaputtzumachen. Wenn
dir Aufträge wichtiger sind als Zahlen, sind die Filme in `serie/` der
bessere Weg.

## Inhaltlich geprüft

Keine erfundenen Zahlen, keine falschen Behauptungen:

- **30 Quadrate** stimmt. Für Kantenlänge k passen (5−k)² Quadrate in
  ein 4×4-Netz: 16 + 9 + 4 + 1 = 30.
- **Der Mathetrick** geht immer auf: ((z·2) + 10) / 2 − z = 5.
- **Keine Statistiken** wie „99 % scheitern" — so etwas könnte ich
  nicht belegen, also steht es nicht drin.
- **Kein schnelles Blinken.** Der Wechsel Rot → Grün ist ein einzelner
  Übergang, der Punkt pulst mit 0,7 Hz. Nichts davon ist für
  lichtempfindliche Menschen riskant.

## Neu bauen

```bash
cd film/quelle/tiktok
node probe.js          # Stichproben
node schleifentest.js  # prüft, ob die Schleife wirklich nahtlos ist
node batch.js          # alle sechs rendern (~2 Minuten)
```

---

## Klassenzimmer 67 (23.11.2026)

`tiktok/klassenzimmer-67.mp4` — 8,6 s, 1080 × 1920, ohne Ton.

### Wie es entstanden ist, und was dabei schiefging

Ziel war ein echtes 3D-Video im Pixar-Stil. Hier ist kein Videomodell
angebunden, deshalb der Umweg über Gamma mit dem Modell `veo-3.1-fast`.

Ergebnis: **Gamma hat ein Standbild geliefert, kein Video.** Dabei sind
**28 Gamma-Credits verbraucht worden, danach standen 0 übrig.** Außerdem
hat Gamma die leuchtenden Stirnzahlen weggelassen und die Zuordnung im
eigenen Bildprompt vertauscht.

Gerettet wurde das so, ohne weitere Kosten:

- Das erzeugte Standbild (`quelle/pixar/szene.jpg`, 1360 × 1712) ist gut.
- Die Zahlen 67, 88 und 970 sind in `quelle/pixar/clip.html` als
  leuchtende Elemente über die Stirnen gelegt — mit Aufpopp-Animation
  und leichtem Pulsieren.
- Dazu eine langsame Kamerafahrt (Maßstab 1,132 → 1,277), ein minimaler
  Seitwärtsdrift und 34 Staubpartikel, die im Gegenlicht aufsteigen.
  Das ist der Unterschied zwischen „Standbild" und „wirkt wie gefilmt".
- Untertitel Wort für Wort, über der TikTok-Beschriftungszone.

### Grenze, die bleibt

Die Figuren bewegen sich nicht und sprechen nicht. Wer genau hinsieht,
erkennt ein animiertes Standbild. Für echte Bewegung bräuchte es ein
Videomodell (Sora, Veo direkt, Runway) — das ist hier nicht erreichbar.

### Beschriftung zum Kopieren

```
die 970 hat einfach andere regeln 💀 #67 #sixseven #fyp #foryou #fürdich #viral #ai #aivideo #brainrot #schule
```

Beim Hochladen in TikTok den Schalter **„KI-generierte Inhalte"**
einschalten. Kostet nichts, dauert einen Tipp, und erspart Ärger.

---

## Klassenzimmer-Reihe, Teil 1 bis 3 (23.11.2026)

Drei Clips aus **einem einzigen bezahlten Bild**. Keine weiteren
Credits verbraucht.

| Datei | Länge | Erzählung |
|---|---|---|
| `klassenzimmer-1-status.mp4` | 15,4 s | Regel erklären → 67 und 88 → 970 → die Zeile |
| `klassenzimmer-2-die-970.mp4` | 15,6 s | Legende um die 970, endet mit „Sie schaut gerade dich an" |
| `klassenzimmer-3-deine-zahl.mp4` | 13,6 s | Rangordnung, endet mit „Und du? Schreib deine Zahl" |

Alle drei enden mit **„Wollt ihr Part 2?"** und der Aufforderung,
„Part 2" zu kommentieren.

### Der Trick: ein Bild, vier Einstellungen

`quelle/pixar/serie/kino.js` schneidet aus dem Standbild echte
Kameraeinstellungen — Totale, Tuschel-Nahaufnahme, Kartoffel von
unten. Die Funktion `kamera(cx, cy, z)` setzt einen Punkt des Bildes
in die Bildmitte und hält den Ausschnitt dabei immer innerhalb des
Bildes, damit nie schwarze Ränder entstehen.

Jede Einstellung hat eine eigene langsame Fahrt, harte Schnitte
dazwischen, ein kurzer Aufblitz auf dem Schnitt, bei der Kartoffel
ein leichtes Kamerazittern. Dazu durchgehend aufsteigender Staub und
Untertitel Wort für Wort.

Die Zahlen 67, 88 und 970 liegen im selben Rahmen wie das Bild —
dadurch wachsen sie bei einer Nahaufnahme automatisch mit.

Grenze: Der Zoom bleibt unter 2,3-fach. Darüber wird das Bild
sichtbar matschig, weil die Vorlage nur 1360 × 1712 Pixel hat. Ein
leichtes Nachschärfen (`unsharp`) beim Rendern fängt den Rest ab.

### Ton

`quelle/pixar/serie/ton-spannung.py` baut pro Clip ein Spannungsbett:
tiefes Brummen, Herzschlag, dessen Takt zum Ende hin anzieht, vor
jedem Schnitt ein Aufzieher und auf dem Schnitt ein Einschlag. Alles
aus Sinus und gefiltertem Rauschen erzeugt, also keine Musiklizenz.
Normalisiert auf −16 LUFS.

Wer einen Trend-Sound drüberlegen will, nimmt `out/*-stumm.mp4` aus
dem Build oder stellt die Lautstärke in der App herunter.

### Beschriftungen zum Kopieren

Teil 1:
```
in dieser klasse hat jeder eine zahl 💀 part 2? #67 #sixseven #fyp #foryou #fürdich #viral #ai #brainrot
```
Teil 2:
```
keiner weiß woher die 970 kommt 😳 #67 #sixseven #fyp #foryou #fürdich #viral #ai #brainrot
```
Teil 3:
```
welche zahl hättest du? 👀 schreib sie in die kommentare #67 #sixseven #fyp #foryou #fürdich #viral #ai
```

Beim Hochladen den Schalter **„KI-generierte Inhalte"** einschalten.

---

## Die 970 — die lange Fassung, 62 Sekunden (23.11.2026)

`tiktok/klassenzimmer-4-die-970-lang.mp4` — 1080 × 1920, 62 s, mit Ton.

Eine durchgehende Szene mit **19 Dialogzeilen** zwischen Pfirsich (67),
Paprika (88) und der Kartoffel (970), geschnitten als Schuss und
Gegenschuss über **21 Einstellungen** — alle aus demselben einen Bild.

### Wie der Dialog funktioniert

`quelle/pixar/serie/kino2.js`: Jede Zeile hat Anfang, Dauer, Sprecher
und Text. Die Kamera folgt dem Sprecher (Pfirsich links, Paprika
rechts, Kartoffel in der Mitte von unten), die Zeile erscheint Wort
für Wort, darüber ein farbiges Namensschild, und **die Zahl des
Sprechenden pulsiert im Sprechrhythmus** — so sieht man ohne Ton
sofort, wer gerade redet.

Bei den Kartoffel-Einstellungen liegt ein kalter Farbstich über dem
Bild (weniger Sättigung, leichter Blaustich). Das trennt sie von den
warmen Einstellungen der beiden vorne.

### Ton

Dasselbe Spannungsbett wie bei den kurzen Clips, aber mit angepasstem
Puls: Bei Filmen über 25 Sekunden zieht der Herzschlag langsamer an
(Faktor 0,985 statt 0,955) und geht bis 0,78 Sekunden Abstand
herunter. Sonst hämmert er die halbe Laufzeit im Anschlag.
Einschläge liegen auf den sechs Wendepunkten der Geschichte.

### Was NICHT drin ist, und warum

**Die Figuren sprechen nicht mit Stimme.** Für den Versuch wurde ein
ElevenLabs-Schlüssel eingetragen, die API antwortet aber dreimal mit
`401 Invalid API key`. Solange das nicht stimmt, gibt es keine
Sprachaufnahme.

**Die Münder bewegen sich nicht.** Das ginge auch mit funktionierendem
ElevenLabs-Schlüssel nicht — der Dienst macht Stimmen, keine
Animation. Dafür bräuchte es einen Dienst für sprechende Bilder
(Hedra, D-ID) oder Bild-zu-Video (Kling, Runway).

### Beschriftung zum Kopieren

```
teil 1 von der 970 😨 wollt ihr part 2? #67 #sixseven #fyp #foryou #fürdich #viral #ai #brainrot #story
```
