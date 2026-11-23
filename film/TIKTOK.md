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
