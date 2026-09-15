---
name: emil-kowalski
description: Animationen und Übergänge im Web. Verwenden, sobald etwas sich bewegt, ein- oder ausblendet, aufklappt, hovert, lädt oder den Zustand wechselt – in Websites, Slides, Artifacts und UI-Mockups.
---

# Animation

Eine Animation ist gelungen, wenn niemand sie bemerkt. Sie erklärt, wo etwas
herkommt und wohin es geht. Alles andere ist Dekoration und stört.

## Dauer

| Was | Dauer |
|---|---|
| Hover, Farbwechsel, kleine Buttons | 100–150 ms |
| Ein-/Ausblenden, Dropdown, Tooltip | 150–250 ms |
| Panel, Modal, Sheet | 250–400 ms |
| Ganzseitiger Wechsel | 400–600 ms |

Über 600 ms wirkt träge. Unter 100 ms sieht man nichts. Große Elemente
brauchen länger als kleine – gleiche Dauer für alles sieht falsch aus.

## Easing

Nie `linear` (außer bei Endlos-Spinnern) und nie das Default-`ease`.

- **Erscheinen** (Element kommt rein): `cubic-bezier(0.16, 1, 0.3, 1)` – schnell
  los, weich aus.
- **Verschwinden**: `cubic-bezier(0.4, 0, 1, 1)` – langsam los, schnell weg.
  Weggehen darf kürzer sein als Kommen.
- **Beides** (Umpositionieren): `cubic-bezier(0.4, 0, 0.2, 1)`.

Spring statt Bezier nur, wenn etwas gezogen oder geworfen wird.

## Nur zwei Eigenschaften animieren

`transform` und `opacity`. Die laufen auf der GPU. Alles andere – `width`,
`height`, `top`, `left`, `margin`, `box-shadow` – lässt den Browser das Layout
neu rechnen und ruckelt auf älteren Handys.

Höhe animieren: `grid-template-rows: 0fr → 1fr`, oder `scaleY` mit
gegen-skaliertem Inhalt. Schatten animieren: zweites Pseudoelement mit dem
Schatten über `opacity` einblenden.

## Ursprung

Bewegung startet dort, wo geklickt wurde. Ein Menü, das am Button hängt,
klappt vom Button auf (`transform-origin: top right`), nicht aus der
Bildschirmmitte. Ein Sheet von unten kommt von unten.

## Distanz

Klein. 4–12 px Versatz reichen, `scale` zwischen 0.96 und 1. Wer 50 px
schiebt, macht eine Show daraus.

## Staffelung

Mehrere Elemente nacheinander: 20–40 ms Abstand, maximal 5–6 Stück. Bei
längeren Listen nur die erste Bildschirmhöhe staffeln.

## Unterbrechbar

Wer zweimal klickt, wartet nicht auf das Ende. Animationen müssen aus dem
aktuellen Zustand heraus umkehren können, nicht erst zurückspringen.

## Pflicht

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    transition-duration: .01ms !important;
  }
}
```

Manche Menschen wird von Bewegung schlecht. Das ist keine Einstellungssache.

## Nicht machen

Bounce bei normalen UI-Elementen. Etwas, das dauernd wackelt, um Aufmerksamkeit
zu holen. Ladeanimationen, die länger dauern als das Laden. Animation beim
ersten Seitenaufbau über dem Falz – der Inhalt soll sofort da sein.
