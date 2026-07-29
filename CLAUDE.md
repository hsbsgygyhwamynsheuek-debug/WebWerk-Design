# CLAUDE.md

Guidance for AI assistants working in this repository.

## What this is

A small, static marketing website (a **draft / Entwurf**) for **Maler Menzel**,
a painting/decorating business (Malerbetrieb) in Jena-Zwätzen, Germany. There is
no build system, no framework, no JavaScript, and no dependencies — it's plain
HTML and CSS meant to be opened directly in a browser.

The site is explicitly labelled an unofficial, non-binding draft (see the
`.notice` banner and footer text). Several sections contain `[Platzhalter: …]`
placeholder text and dashed-border image placeholders awaiting real content.

## Layout

```
maler-menzel/
  index.html    Single-page site, German (lang="de"), semantic sections
  styles.css    All styling; no external stylesheets or fonts
```

The page is one HTML file with anchor-linked sections, navigated via the sticky
header. Section `id`s and their nav order:

`#start` (hero) · `#leistungen` (services) · `#ablauf` (process steps) ·
`#ueber` (about) · `#zeiten` (opening hours) · `#kontakt` (contact + form)

## Working on it

- **No build/tooling.** Edit the files and open `maler-menzel/index.html` in a
  browser to preview. There is nothing to compile, install, or run.
- **Language is German.** All user-facing copy is German; keep it that way and
  match the existing calm, professional, tradesman tone. `lang="de"` must stay.
- **Placeholders** use the `[Platzhalter: …]` convention for text and the
  `.placeholder` dashed boxes for images. Don't invent real business details
  (email, Impressum, owner bio, photos) — leave placeholders until the owner
  provides real content.

## Conventions

- **Styling lives entirely in `styles.css`.** Avoid inline styles and adding
  `<style>` blocks. Design tokens are CSS custom properties in `:root`
  (`--ink`, `--accent` = brick red `#a23b1e`, `--bg-alt`, `--maxw`, etc.) — reuse
  them rather than hardcoding new colors.
- **Typography:** serif (Georgia) for body/headings; Arial for nav, buttons,
  labels, and UI accents. Large font sizes and high contrast are intentional
  (readability for an older/local audience).
- **Layout** uses CSS Grid with a `.container` (max-width `--maxw`, 1080px).
  Responsive breakpoints at `860px` and `560px` collapse grids to single column.
- **Accessibility matters here:** semantic elements, `aria-label`s on nav and
  image placeholders, `scope` on table headers, visible `:focus-visible`
  outlines, and `role="alert"` on the notice. Preserve these when editing.
- The contact `<form>` is not wired to any backend — the hint text directs users
  to call. Don't claim it submits anywhere.

## Git

- Active development branch: `claude/claude-md-docs-g2uj9p`.
- Commit messages in this repo are in German (e.g. "Entwurf: Website Maler
  Menzel Jena"); follow that style. Push with `git push -u origin <branch>`.
