---
name: impeccable-design
description: Handwerkliche Sauberkeit bei allem Visuellen – Abstände, Typografie, Farbe, Raster, Kontrast. Verwenden bei jeder Website, Präsentation, jedem Handout, Artifact oder Mockup, bevor es rausgeht.
---

# Sauberes Design

Die meisten Entwürfe sehen nicht schlecht aus, weil die Idee schlecht ist,
sondern weil die Ausführung schlampig ist. Ungleiche Abstände, sieben
Schriftgrößen, Text der über Bilder rutscht. Das hier ist die Checkliste.

## Abstände aus einem System

Nur diese Werte, nichts dazwischen:

`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96`

Kein `padding: 13px`. Kein `margin-top: 37px`. Wenn 24 zu wenig ist, nimm 32.

**Nähe zeigt Zusammengehörigkeit.** Die Überschrift gehört zu ihrem Absatz –
also 8 px darunter und 48 px darüber, nicht 24/24. Der Abstand *zwischen*
Gruppen ist immer größer als der *innerhalb* einer Gruppe. Wenn das nicht
stimmt, liest niemand die Struktur.

## Typografie

- **Höchstens drei Größen** pro Seite. Vier ist schon Unruhe.
- Skala mit Sprüngen, nicht in Ein-Pixel-Schritten: 14 · 16 · 20 · 28 · 40 · 56.
- **Zeilenhöhe** umgekehrt zur Größe: Fließtext 1.5–1.6, große Überschriften
  1.1–1.2. Eine 40-px-Überschrift mit `line-height: 1.6` zerfällt.
- **Zeilenlänge** 60–75 Zeichen (`max-width: 65ch`). Volle Bildschirmbreite
  ist unlesbar.
- Höchstens **zwei Schriftschnitte** (z.B. Regular + Bold). Kein Kursiv-Bold-
  Unterstrichen gleichzeitig.
- Überschriften in Versalien nur kurz und mit `letter-spacing: .08em`.
- Zahlen in Tabellen: `font-variant-numeric: tabular-nums`.

## Farbe

- **Ein** Akzentfarbton. Der markiert das Wichtigste – und sonst nichts.
- Der Rest: eine Hintergrundfarbe, eine Textfarbe, eine gedämpfte Textfarbe,
  eine Linienfarbe. Fünf Werte reichen für fast jede Seite.
- Reines Schwarz auf reinem Weiß ist hart. `#1A1A1B` auf `#FAF9F6` ist besser.
- **Kontrast prüfen**: Fließtext mindestens 4.5:1, große Schrift 3:1. Grauer
  Text auf hellgrauem Grund ist kein Stil, sondern unlesbar.
- Farbe darf nie die einzige Information sein (Rot/Grün).

## Ausrichtung

Alles richtet sich an einer gemeinsamen Kante aus. Eine unsichtbare Linie
links, an der Überschrift, Text und Button hängen. Wenn ein Element 3 px
daneben steht, sieht man es – auch wenn man nicht sagen kann, warum es
komisch aussieht.

Zentrieren nur bei kurzen, einzelnen Elementen. Nie ganze Textblöcke.

## Nichts überlappt

Text steht nie über einem Bild, es sei denn, das Bild hat darunter eine
Abdunklung von mindestens 50 %. Besser: Text neben das Bild, in eine eigene
Spalte.

Bei fester Größe (Slides, PDF): **jede Seite nachmessen**, nicht schätzen.
Läuft Inhalt über den Rand, wird gekürzt – nicht die Schrift verkleinert.

## Bilder

Alle Bilder auf einer Seite im gleichen Seitenverhältnis. `object-fit: cover`,
nie verzerren. Gleiche Behandlung (alle mit Rundung oder alle ohne, nicht
gemischt).

## Ränder

Innen mindestens 16 px zum Rand, auf Desktop eher 24–32. Nichts klebt an der
Kante. Eine Karte hat innen ringsum den gleichen Abstand – oben 20 und unten
14 sieht man sofort.

## Zustände

Jedes klickbare Element braucht: Normal, Hover, Fokus (sichtbarer Ring –
`outline` niemals einfach entfernen), Aktiv, Deaktiviert. Klickflächen
mindestens 44 × 44 px, sonst trifft man sie am Handy nicht.

## Vor der Abgabe

1. Bei 400 px Breite ansehen – keine Seitwärtsscrollleiste.
2. Alle Abstände aus der Skala?
3. Mehr als drei Schriftgrößen? Dann eine raus.
4. Überlappt irgendwo etwas?
5. Kontrast überall ausreichend?
6. Hell- und Dunkelmodus beide geprüft?
