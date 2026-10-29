#!/usr/bin/env python3
"""Build the Chess Beginner Comeback Guide: docs/*.md -> site/*.html.

Local-first by design: every output page links only to other pages in the
same folder and one local stylesheet. No network requests, no tracking.

Usage:
    python3 build.py                 # build into ./site
    python3 build.py --outdir DIR    # build somewhere else
    python3 build.py --check         # verify docs are internally consistent

Requires the Markdown package (see requirements.txt); tests live in tests/.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

try:
    import markdown as _md
except ImportError as exc:  # pragma: no cover
    sys.exit(f"build.py needs the 'markdown' package ({exc}); run: pip install markdown")

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
DEFAULT_OUT = ROOT / "site"
STYLESHEET = ROOT / "assets" / "style.css"

BOOK_TITLE = "The Chess Beginner Comeback Guide"
BOOK_SUBTITLE = "From remembered rules to your first club night"
COMPANIONS = ("chess-puzzle-drills", "free-chess-scoresheet-pack")

REQUIRED_MARKS = {  # chapter file -> phrase that must survive into the built page
    "01-welcome-back.md": "comeback guide",
    "02-rules-refresher.md": "j'adoube",
    "03-opening-principles.md": "Two starting maps",
    "04-blunder-recovery.md": "their",
    "05-your-first-games.md": "Three questions",
    "06-phase-timing.md": "budget",
    "07-online-vs-otb.md": "handshake",
    "08-playing-calm.md": "one-breath reset",
    "09-gentle-training.md": "15-minute",
    "10-ten-game-plan.md": "Ten games",
    "11-pre-club-checklist.md": "arrive 15 minutes early",
    "12-glossary.md": "tempo",
}


class Chapter:
    def __init__(self, path: Path):
        self.path = path
        self.slug = path.stem
        raw = path.read_text(encoding="utf-8")
        meta, body = split_meta(raw)
        self.meta = meta
        self.body = body
        self.title = meta.get("title", self.slug.replace("-", " ").title())
        self.summary = meta.get("summary", "")

    def render(self) -> str:
        html = _md.markdown(self.body, extensions=["tables", "sane_lists"])
        html = fix_checklists(html)
        html = rewrite_book_links(html)
        return html


def split_meta(raw: str) -> tuple[dict[str, str], str]:
    if raw.startswith("---\n"):
        end = raw.find("\n---\n", 4)
        if end != -1:
            meta = {}
            for line in raw[4:end].splitlines():
                key, _, value = line.partition(":")
                if key.strip():
                    meta[key.strip()] = value.strip()
            return meta, raw[end + 5 :].lstrip("\n")
    return {}, raw


CHECKLIST_RE = re.compile(r"<li>\[( |x)\] ")
CHECKMARK = {" ": "\u2610", "x": "\u2611"}


def fix_checklists(html: str) -> str:
    return CHECKLIST_RE.sub(
        lambda m: f'<li class="todo">{CHECKMARK[m.group(1)]} ', html
    )


HREF_MD_RE = re.compile(r'(?<=href=")([^"#]+?)\.md')
SRC_MD_RE = re.compile(r"\]\(([^ ()#]+\.md)\)")


def rewrite_book_links(html: str) -> str:
    return HREF_MD_RE.sub(lambda m: f"{m.group(1)}.html", html)


def page(ch_title: str, ch_summary: str, body: str, nav: str, footer: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape_attr(ch_summary)}">
<title>{escape_html(ch_title)} — {BOOK_TITLE}</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="wrap">
{nav}
<div class="masthead">
<p class="kicker">{BOOK_TITLE}</p>
<h1>{escape_html(ch_title)}</h1>
<p class="summary">{escape_html(ch_summary)}</p>
</div>
{body}
{footer}
</div>
</body>
</html>
"""


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_attr(text: str) -> str:
    return escape_html(text).replace('"', "&quot;")


def topnav(on_index: bool) -> str:
    home = "Back to the manual" if not on_index else "You're at the manual"
    return (
        '<nav class="topnav">'
        + (
            f"<strong>{home}</strong>"
            if on_index
            else f'<a href="index.html">&larr; {home}</a>'
        )
        + f'<span>club-night checklist below &middot; <a href="manual.html">print it all</a></span>'
        "</nav>"
    )


def pagenav(prev_ch: Chapter | None, next_ch: Chapter | None) -> str:
    parts = []
    if prev_ch:
        parts.append(
            f'<a class="prev" href="{prev_ch.slug}.html"><span class="label">Previous</span>'
            f"{escape_html(prev_ch.title)}</a>"
        )
    else:
        parts.append("<span></span>")
    if next_ch:
        parts.append(
            f'<a class="next" href="{next_ch.slug}.html"><span class="label">Next</span>'
            f"{escape_html(next_ch.title)}</a>"
        )
    else:
        parts.append('<span class="next"></span>')
    return '<nav class="pagenav">' + "".join(parts) + "</nav>"


SITEFOOTER = (
    '<footer class="sitefooter">A beginner-friendly manual by '
    "Asdale Dynamics, LLC. Local-first: no accounts, no tracking, no network "
    "calls. Companions: chess-puzzle-drills and free-chess-scoresheet-pack. "
    "MIT licensed.</footer>"
)


def index_body(chapters: list[Chapter]) -> str:
    return f"""<p>This is a warm, plain-English manual for grown-ups who know how the
pieces move and want everything else: opening <em>principles</em> instead of
memorized lines, a blunder-recovery ritual, annotating your own games,
clock-time basics, real-room etiquette, calmer nerves, and training weeks
sized for adult life. It ends with a pre-club checklist and a ten-game
starter plan — everything between &ldquo;I know the rules&rdquo; and
&ldquo;I played at a club and it was fine.&rdquo;</p>
<div class="paths">
<h2>Start where you are</h2>
<ul>
<li><strong>Starting fresh tonight?</strong> Read the <a href="01-welcome-back.html">welcome</a>, then the <a href="02-rules-refresher.html">rules refresher</a>.</li>
<li><strong>Games already on your mind?</strong> Go straight to the <a href="10-ten-game-plan.html">ten-game starter plan</a> and work backward.</li>
<li><strong>Club night is this week?</strong> Skim the <a href="11-pre-club-checklist.html">pre-club checklist</a>, then fill your gaps chapters first.</li>
</ul>
</div>
<h2>The chapters</h2>
<ol class="chapter-list">
{"".join(f"<li><span class='cnum'>Chapter {n:02d}</span>" + f"<a class=\"ctitle\" href=\"{ch.slug}.html\">{escape_html(ch.title)}</a>" f"<p class=\"csummary\">{escape_html(ch.summary)}</p></li>" for n, ch in enumerate(chapters, 1))}
</ol>
<h2>Alongside this guide</h2>
<p>Two companions carry the practice side. <em>{COMPANIONS[0]}</em> is a small
local puzzle site for the 15-minute drill sessions, and
<em>{COMPANIONS[1]}</em> is a free printable pack: regulation scoresheets,
a post-game reflection page, and lesson-notes sheets. Both are separate,
self-contained projects — grab, print, or open them offline whenever.</p>
"""


def manual_body(chapters: list[Chapter], toc: str) -> str:
    parts = []
    for n, ch in enumerate(chapters, 1):
        parts.append(
            f'<section class="chapter"><h1 id="ch{n:02d}">{n:02d}. {escape_html(ch.title)}</h1>'
            f"<p><em>{escape_html(ch.summary)}</em></p>{ch.render()}</section>"
        )
    return f'<nav class="paths"><h2>In this manual</h2><ul>{toc}</ul></nav>' + "".join(parts)


def build(outdir: Path) -> None:
    chapters = load_chapters()
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "assets").mkdir(exist_ok=True)
    shutil.copyfile(STYLESHEET, outdir / "assets" / "style.css")

    nav = topnav(on_index=True)
    (outdir / "index.html").write_text(
        page(BOOK_TITLE, BOOK_SUBTITLE, index_body(chapters), nav, SITEFOOTER),
        encoding="utf-8",
    )

    toc = "".join(
        f'<li><a href="#ch{n:02d}">{n:02d}. {escape_html(ch.title)}</a></li>'
        for n, ch in enumerate(chapters, 1)
    )
    body = manual_body(chapters, toc)
    (outdir / "manual.html").write_text(
        page(f"{BOOK_TITLE} — all chapters", BOOK_SUBTITLE, body, nav, SITEFOOTER),
        encoding="utf-8",
    )

    for i, ch in enumerate(chapters):
        nav = topnav(on_index=False)
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i + 1 < len(chapters) else None
        html = page(ch.title, ch.summary, ch.render(), nav, pagenav(prev_ch, next_ch))
        (outdir / f"{ch.slug}.html").write_text(html, encoding="utf-8")


def load_chapters() -> list[Chapter]:
    files = sorted(DOCS.glob("[0-9][0-9]-*.md"))
    if not files:
        sys.exit(f"No chapters found in {DOCS}")
    chapters = []
    for f in files:
        ch = Chapter(f)
        flat = re.sub(r"\s+", " ", ch.body + " " + ch.summary).lower()
        missing = [k for k, v in REQUIRED_MARKS.items() if k == ch.path.name and v.lower() not in flat]
        if missing:
            sys.exit(f"Chapter {ch.path.name} lost its required phrase "
                     f"'{REQUIRED_MARKS[missing[0]]}' — refusing to build.")
        chapters.append(ch)
    for f in DOCS.glob("*.md"):
        if f.name not in {c.path.name for c in chapters}:
            sys.exit(f"{f.name} doesn't match the NN-name.md chapter pattern.")
    return chapters


def check() -> int:
    """Verify docs parse, link targets exist, and key phrases survive."""
    problems = []
    chapters = load_chapters()
    slugs = {c.slug for c in chapters}
    for ch in chapters:
        stripped = re.sub(r"```.*?```", "", ch.body, flags=re.S)
        if not ch.title:
            problems.append(f"{ch.path.name}: missing title")
        if len(stripped) < 1200:
            problems.append(f"{ch.path.name}: suspiciously short ({len(stripped)} chars)")
        for target in SRC_MD_RE.findall(ch.body):
            page = target[:-3]
            if page not in slugs:
                problems.append(f"{ch.path.name}: link to unknown chapter '{target}'")
        if ch.slug != ch.path.stem:
            problems.append(f"{ch.path.name}: slug mismatch")
    if problems:
        print("FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"OK: {len(chapters)} chapters parse, link, and carry their key phrases.")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outdir", type=Path, default=None, help="build directory (default: ./site)")
    ap.add_argument("--check", action="store_true", help="verify docs, then exit")
    ap.add_argument("--clean", action="store_true", help="wipe the build directory first")
    args = ap.parse_args()

    if args.clean:
        out = args.outdir or DEFAULT_OUT
        if out.exists():
            shutil.rmtree(out)
        build(out)
        print(f"Clean build written to {out}")
        return
    if args.check:
        sys.exit(check())
    out = args.outdir or DEFAULT_OUT
    build(out)
    print(f"Built {len(list((out).glob('*.html')))} pages into {out}")


if __name__ == "__main__":
    main()
