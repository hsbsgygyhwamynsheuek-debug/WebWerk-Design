# WebWerk-Film

Werbefilm für WebWerk Design. 41,6 Sekunden, 30 Bilder/Sekunde.
Komplett im Browser gebaut und Bild für Bild gerendert – keine
Videoschnitt-Software, keine fremden Clips, keine fremde Musik.

## Die fertigen Dateien

| Datei | Format | Wofür |
|---|---|---|
| `webwerk-film-16-9.mp4` | 1920 × 1080 | YouTube, Website, Laptop, E-Mail-Link |
| `webwerk-film-9-16.mp4` | 1080 × 1920 | Instagram Reel, TikTok, WhatsApp-Status |
| `…-ohne-ton.mp4` | beide | falls eigene Musik drunter soll |
| `webwerk-vorschaubild.png` | 1920 × 1080 | Titelbild / Thumbnail |

## Was drinsteht

Nur Aussagen, die auch auf `docs/index.html` stehen und stimmen:
250 € einmalig, keine monatlichen Kosten, fertig in einer Woche,
bezahlt wird erst wenn die Seite online ist, Änderungen im ersten
Monat kostenlos, Telefon 0151 72678183, erreichbar ab 16 Uhr.

Keine erfundenen Zahlen, keine Kundennamen, keine fremden Logos.
Die gezeigte „Beispielseite" ist eine abstrakte Nachbildung aus
Balken – kein echter Betrieb, keine fremden Fotos.

Der Hinweis auf den Einsatz künstlicher Intelligenz steht im Abspann
(Artikel 50 der Verordnung (EU) 2024/1689).

## Ton

`quelle/ton.py` erzeugt die Tonspur selbst aus Sinustönen
(Akkorde Am – F – C – Am – F – G – C, dazu leise Akzente auf den
Schnitten). Dadurch gibt es keine Musiklizenz-Frage. Lautheit
normalisiert auf −17 LUFS, Spitze −1,5 dBTP.

## Ändern und neu rendern

Texte, Farben und Zeiten stehen alle in `quelle/film.html`.
Die Zeitachse ist die Liste `SZ` ganz unten im `<script>`.

```bash
cd film/quelle
node probe.js land 14.5        # Einzelbild zum Prüfen
node render.js                 # beide Formate neu bauen (~3 Minuten)
python3 ton.py                 # Tonspur neu bauen
```

Gebraucht werden: Node mit Playwright, Chromium, ffmpeg, Python mit numpy.
Die Schrift ist Inter, lokal installiert – nichts wird nachgeladen.

---

# Die Filmreihe (ab 23.11.2026)

Acht weitere Filme, alle aus demselben Baukasten: `quelle/serie/kern.css`
und `quelle/serie/kern.js` geben Farben, Schrift, Bewegungen und den
Abspann vor. Jeder Film ist eine eigene HTML-Datei mit seinen Szenen.
Dadurch sehen alle zusammengehörig aus, und Ändern geht an einer Stelle.

| Nr. | Datei | Länge | Art | Wofür |
|---|---|---|---|---|
| 1 | `1-kurz` | 16 s | sachlich | Kurzfassung. Reel, Status, erster Kontakt |
| 2 | `2-leistung` | 22 s | sachlich | Was in den 250 € steckt |
| 3 | `3-schritte` | 22 s | sachlich | Ablauf, jeder Schritt ein Bild |
| 4 | `4-woche` | 18 s | sachlich | Montag angerufen, Freitag online |
| 5 | `5-ki-bau` | 28 s | KI sichtbar | Prompt links, Seite entsteht rechts |
| 6 | `6-strich` | 24 s | KI sichtbar | Drahtgitter wird zur fertigen Seite |
| 7 | `7-1998` | 20 s | lustig | Website von früher, dann heute |
| 8 | `8-ausreden` | 24 s | lustig | Vier Ausreden, vier Antworten |

`-16-9` ist Querformat (Website, YouTube, Laptop),
`-9-16` Hochformat (Reel, TikTok, WhatsApp-Status).
Hochformat gibt es für 1, 3, 4, 7 und 8 — die anderen leben vom
breiten Bild.

## Ton

`quelle/serie/ton-gen.py` baut zu jedem Film eine eigene Tonspur: Die
Akkorde wechseln genau dort, wo der Film schneidet. Aufruf:

```bash
python3 -I ton-gen.py '{"dauer":16.4,"cuts":[0,3.7,7.2,11.4],"out":"ton.wav"}'
```

Die Schnittzeiten gibt jeder Film selbst aus (`window.FILM_SZ`), der
Stapellauf `batch.js` schreibt sie nach `out/meta.json`.

## Alles neu bauen

```bash
cd film/quelle/serie
node probe-alle.js     # Stichproben als Einzelbilder
node batch.js          # alle Filme rendern (~8 Minuten)
```

## Grenzen, ehrlich gesagt

Echte KI-Filmaufnahmen (fotorealistische Menschen, bewegte Szenen) sind
hier nicht dabei — dafür bräuchte es ein Videomodell. Die beiden
„KI-Filme" zeigen stattdessen das echte Arbeiten: Prompt, Entwurf,
fertige Seite. Das ist ehrlicher und passt zum Hinweis im Abspann.

Der Ton ist gemessen, nicht gehört: −17 LUFS, Spitze −1,5 dBTP.
