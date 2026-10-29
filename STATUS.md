# STATUS — Chess Beginner Comeback Guide

Last updated: 2026-10-29

## What was built

A beginner-friendly manual plus a static HTML site, built to the goal spec:

- **12 Markdown chapters** in `docs/`, written in the warm plain-English
  house style, each with a `title`/`summary` header:
  1. **Welcome Back to the Board** — who this is for, reading paths
  2. **Rules Refresher** — touch move/j'adoube, en passant (with a diagram
     table), stalemate, castling's fine print, threefold/50-move rounds,
     a five-minute drill
  3. **Opening Principles** — ten principles, two "setup maps" (e4 and d4)
     instead of memorized lines, the traps worth meeting on purpose, and an
     honest explanation of why engines still grade master lines higher
  4. **Blunder Recovery** — the C.C.T. pre-move scan (checks, captures,
     threats — theirs first), the receiving ritual ("fact, not story; what
     does the position punish now"), and a three-line post-game debrief
  5. **Your First Games** — getting games (slow online, casual OTB), the
     scoresheet habit, a 10-minute annotation method with real margin
     examples
  6. **Phase Timing** — opening/middlegame/endgame clock budgets (~10/60/30),
     the "obvious vs. choice" rhythm rule, increments in plain English
  7. **Online vs. Over-the-Board** — what transfers, what doesn't, full
     club etiquette, and a five-step first-night arrival script
  8. **Playing Calm** — adult-sized nerves toolkit: arrival timing, the
     one-breath reset, play-your-rating, two sentences worth memorizing
     (explicitly not medical advice)
  9. **Gentle Training Weeks** — the 15-minute session unit, a default
     week, a fallback week for broken weeks, drills sourced from your own
     game margins
  10. **The Ten-Game Starter Plan** — ten games, each with one job, ending
      with a five-mark readiness scorecard
  11. **Pre-Club Checklist** — check before you go / gear / knowledge gate /
      arrival script / at-the-board reminders / homecoming ritual (22+ ☐ items)
  12. **Glossary** — board, tactics, clock/rating/club-life terms, plus the
      two companion projects
- **Static site via `build.py`**: converts `docs/*.md` into `site/*.html`
  with a shared stylesheet (`assets/style.css`, parchment/wood theme, print
  stylesheet), cross-chapter navigation (prev/next), a front page
  (`index.html`) with three "start where you are" paths and a chapter list,
  and a single-page all-chapters `manual.html` for printing.
- **Local-first by construction**: every href in the built site is relative
  and no `http`/`https` string appears anywhere in the output (test-enforced).
  Chapter-to-chapter `.md` links are rewritten to `.html` by the build.
- **Checklist rendering**: `- [ ]` items in the markdown become real ☐
  checkbox items in the HTML.
- **build script extras**: `--clean`, `--outdir`, `--check` (verifies docs
  parse, cross-links resolve, required phrases survive).
- **serve.py**: stdlib-only preview server (`python3 serve.py` →
  http://127.0.0.1:8765), with a quiet logger and `--no-browser`.
- **Bookkeeping**: `README.md` (chapter table, build/test/run instructions,
  companion-project notes, credit to Asdale Dynamics, LLC), MIT `LICENSE`
  with the exact line `Copyright (c) 2026 Asdale Dynamics, LLC`,
  `requirements.txt` (markdown, pytest), `tests/test_build.py` (42 tests).
- **Complements, as named in the manual and README**:
  `chess-puzzle-drills` (drill puzzles for the 15-minute sessions) and
  `free-chess-scoresheet-pack` (printable scoresheets and reflection pages).
  Both are separate projects; no hard links, only by-name mentions.
- No secrets, no personal data, no network calls, nothing published.

## How to run it

```bash
pip install markdown pytest      # one-time setup
python3 build.py                 # build docs/ -> site/
python3 build.py --clean         # wipe site/ first, then build
python3 build.py --check         # verify docs parse + links resolve
python3 serve.py                 # preview at http://127.0.0.1:8765
python3 -m pytest tests/ -q      # run the test suite
```

Requirements: Python 3.10+ (tested on 3.13), `markdown` for the build,
`pytest` for tests. Or skip building entirely — `site/` is committed
prebuilt and works by double-clicking `site/index.html`.

## Verification results

- `python3 build.py --clean` → builds 14 HTML pages (12 chapters + index +
  manual) plus `assets/style.css`; exit 0.
- `python3 build.py --check` → `OK: 12 chapters parse, link, and carry their
  key phrases.`
- `python3 -m pytest tests/ -q` → all tests pass, covering:
  - 12 chapter files exist with exact expected titles and front matter,
    substantive length, no placeholder text
  - every cross-chapter link resolves (checked at source and in built HTML)
  - content anchors: C.C.T./blunder recovery, castling, en passant, touch
    move, pre-club checklist, ten-game plan, both companions present
  - build runs into temp dirs (`--outdir`, `--clean`) producing all
    expected pages with correct bytes vs. the committed `site/`
  - every built page parses with a lenient HTML parser (no tag soup, no
    unfilled template placeholders)
  - che navigation wiring: prev/next on chapters, index link everywhere,
    manual.html contains all 12 chapters
  - offline-only guarantee: no `http://`, `https://`, or any `://` in output;
    no unconverted `.md` hrefs; every href resolves to a file
  - checklists render as ☐ items (≥20 on the club-night page)
  - `--check` mode exits 0; README/LICENSE bookkeeping exact
- Link-rewriting and page templates were fixed and re-verified during
  development; the phrase-guard in the build refuses chapters that lose
  their key content phrases.

## Known gaps / possible improvements

- The site is desktop-first; mobile is usable via the viewport meta +
  fluid width but hasn't been tuned on real devices.
- No search or per-chapter table of contents sidebar; the glossary is
  browsable but not linked from a persistent nav.
- `manual.html` uses `page-break-before` CSS; some browsers print headers
  unevenly, so a PDF export path (e.g. via a print-to-PDF page) could be
  added.
- Chess diagrams are inline code spans (`d4`, `exd3`) and one table
  diagram; no SVG board graphics (the companion projects cover visual
  material).
- The `--check` mode re-parses each chapter but doesn't lint for dead
  anchors beyond chapter links (no per-chapter `#` anchors are used).
- Tests build the site into session-scoped temp dirs rather than
  parametrized per-test builds, so the full suite runs in under a second;
  no visual screenshot-diff test exists.
