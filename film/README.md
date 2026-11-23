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
