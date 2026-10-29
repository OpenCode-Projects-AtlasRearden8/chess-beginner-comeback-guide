# Chess Beginner Comeback Guide

A warm manual for grown-up beginners going from *I know how the pieces move*
to *I played at a club and it went fine*. Twelve chapters of plain English:
opening **principles** instead of memorized lines, a blunder-recovery
ritual, annotating your own first games, clock-time basics for each phase,
online-vs-over-the-board etiquette, playing calm, gentle training weeks that
fit adult life — plus a **ten-game starter plan**, a **pre-club checklist**,
and a **glossary**. Ships as Markdown chapters plus a small static site the
local build script generates. No accounts, no signsups, no tracking —
open the pages in any browser and read.

## What's in the guide

| # | Chapter | What it covers |
|---|---------|----------------|
| 1 | Welcome Back to the Board | who this is for, how to use the book |
| 2 | Rules Refresher | touch move, en passant, stalemate, castling's fine print, scoring habits |
| 3 | Opening Principles | ten principles + two setup "maps", not memorized lines |
| 4 | Blunder Recovery | the C.C.T. pre-move scan and the receiving ritual |
| 5 | Your First Games | slow games, scoresheet habit, 10-minute annotation method |
| 6 | Phase Timing | opening/middlegame/endgame clock budgets, increments |
| 7 | Online vs. Over-the-Board | what transfers, what doesn't, club-night etiquette |
| 8 | Playing Calm | adult-sized nerves toolkit and arrival scripts |
| 9 | Gentle Training Weeks | 15-minute sessions, fallback weeks, light tracking |
| 10 | The Ten-Game Starter Plan | your first ten games, each with one job |
| 11 | Pre-Club Checklist | gear, knowledge gate, arrival script, homecoming |
| 12 | Glossary | every term used in the book, translated plainly |

The manual is written to be read in any order; the site's front page offers
three "start where you are" paths.

It's a companion to two sibling beginner-chess projects:
**chess-puzzle-drills** (a local drill-puzzle site) and the
**free-chess-scoresheet-pack** (printable scoresheets, a post-game
reflection page, and lesson-notes pages). Both are referenced by name in the
manual's reading tips and glossary; each is its own folder/repo.

## How to build the site

Requirements: Python 3.10+ and the `markdown` package (`pip install markdown`).

```bash
python3 build.py            # build docs/ -> site/
python3 build.py --clean    # wipe site/ first, then build
python3 build.py --outdir /tmp/other
python3 build.py --check    # verify docs parse and cross-links resolve
python3 serve.py            # preview at http://127.0.0.1:8765
```

Every chapter is a plain Markdown file in `docs/` with a small `title`/`summary`
header at the top. Edit, rebuild, refresh. The build rewrites chapter-to-chapter
`.md` links into `.html`, renders tables and checklists, and emits
`index.html` (front page + chapter list) and `manual.html` (all twelve
chapters on one printable page). The shared stylesheet is `assets/style.css`.

`site/` is committed prebuilt, so you can also just open `site/index.html`
in a browser straight from a checkout — nothing external is ever fetched.

## Running the tests

```bash
pip install pytest
python3 -m pytest tests/ -q
```

The suite verifies the twelve chapter files (front matter, cross-links,
content anchors), runs the build into temp directories, checks every built
page parses cleanly and navigates correctly, guarantees the site stays
offline-only (no URLs anywhere in the output), confirms the prebuilt
`site/` matches a fresh build, and checks LICENSE/README bookkeeping.

## License

MIT — see [LICENSE](LICENSE).

Copyright (c) 2026 Asdale Dynamics, LLC. This guide is a free, beginner-friendly
manual published by Asdale Dynamics, LLC, which makes plain-English AI books,
guides, and practical open-source tools.
