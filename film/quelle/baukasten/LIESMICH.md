# Episoden-Baukasten

Aus einer kurzen JSON-Beschreibung entsteht ein fertiges TikTok-Video:
Stimmen (Piper, lokal), Phonk-Beat mit Drop, Soundeffekte, Bewegung der
Figuren (WebGL), Karaoke-Untertitel, Zahlen-Glitches, Endkarte.

```bash
./baue.sh specs/v04.json          # Ton + Seite + Pruefbogen (out/<name>/bogen.png)
./baue.sh specs/v04.json render   # fertiges Video out/<name>/<name>.mp4
./schlange.sh v04 v05 v06         # mehrere nacheinander rendern
```

## Aufbau einer Beschreibung

- `szenen`: Bild, Farbstimmung (`warm`, `kalt`, `neutral`, `dunkel`),
  Figurenpositionen (`fig`: Kopf, Mund, Augen je Figur K/P/A/N) und
  Leuchtzahlen (`zahlen`, mit `wechsel` fuer Glitch-Wechsel, `spin` fuer
  den Spielautomaten, `cls: flare` fuer Aufflammen auf dem Drop).
- `shots`: Einstellungen. Jede hat Kamera (`cx`, `cy`, Zoom `z0`→`z1`),
  optional eine Sprachzeile (`rede`), Mindestlaenge in Schlaegen (`min`)
  und Marken (`drop`, `glitch`, `stille`, …). Laengen werden auf ganze
  Schlaege (140 BPM) gerundet, Schnitte fallen also auf den Beat.
- `titel`: Text oben (oder `pos: unten`), Zeiten auch als Marken
  (`"drop"`, `"drop+1.6"`).
- `ende`: Endkarte.

Sprecher: P Pfirsich, A Paprika, K Kartoffel, N der Neue (Ananas),
X Erzaehler.

## Neue Szenen

Bilder in Figma mit `gpt-image-2.5-flare` (2 Credits pro Bild, Gratis-
Kontingent). Im Prompt immer „no text, no numbers" — die Zahlen werden
darueber gelegt. Koordinaten mit einem Raster ablesen (siehe
`film/quelle/szenen/`).
