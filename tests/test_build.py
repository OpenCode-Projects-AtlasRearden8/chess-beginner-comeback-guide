"""Test suite for the Chess Beginner Comeback Guide.

Covers: docs integrity, build correctness, offline/local-first guarantees,
navigation wiring, and repo hygiene (LICENSE/README). Everything runs
offline; site builds go to temp directories.
"""

from __future__ import annotations

import html.parser
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
BUILD = ROOT / "build.py"

CHAPTER_FILES = sorted(p.name for p in DOCS.glob("[0-9][0-9]-*.md"))
EXPECT_TITLES = [
    "Welcome Back to the Board",
    "Rules Refresher",
    "Opening Principles",
    "Blunder Recovery",
    "Your First Games",
    "Phase Timing",
    "Online vs. Over-the-Board",
    "Playing Calm",
    "Gentle Training Weeks",
    "The Ten-Game Starter Plan",
    "Pre-Club Checklist",
    "Glossary",
]


@pytest.fixture(scope="session")
def built(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("built") / "site"
    result = subprocess.run(
        [sys.executable, str(BUILD), "--outdir", str(out)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    return out


@pytest.fixture(scope="session")
def clean_built(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("clean") / "site"
    result = subprocess.run(
        [sys.executable, str(BUILD), "--clean", "--outdir", str(out)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    return out


# ---------------------------------------------------------------- docs ---


def test_twelve_chapters_exist():
    assert CHAPTER_FILES == [
        "01-welcome-back.md", "02-rules-refresher.md",
        "03-opening-principles.md", "04-blunder-recovery.md",
        "05-your-first-games.md", "06-phase-timing.md",
        "07-online-vs-otb.md", "08-playing-calm.md",
        "09-gentle-training.md", "10-ten-game-plan.md",
        "11-pre-club-checklist.md", "12-glossary.md",
    ]


@pytest.mark.parametrize(
    "fname,title",
    list(zip(CHAPTER_FILES, EXPECT_TITLES))
)
def test_front_matter(fname, title):
    raw = (DOCS / fname).read_text(encoding="utf-8")
    assert raw.startswith("---\n")
    assert f"title: {title}" in raw.split("---\n")[1]
    body = raw.split("---", 2)[2]
    assert len(body) > 2500, f"{fname} is suspiciously thin"
    assert "lorem" not in body.lower() and "TODO" not in body


@pytest.mark.parametrize("fname", CHAPTER_FILES)
def test_no_stray_emphasis_slash(fname):
    raw = (DOCS / fname).read_text(encoding="utf-8")
    assert "</em>" not in raw and "<code>" not in raw


def test_links_resolve_between_chapters():
    slugs = {p.stem for p in DOCS.glob("[0-9][0-9]-*.md")}
    for f in DOCS.glob("[0-9][0-9]-*.md"):
        for target in re.findall(r"\]\(([^)#\s]+\.md)\)", f.read_text(encoding="utf-8")):
            assert target[:-3] in slugs, f"{f.name} -> unknown chapter {target}"


def test_key_content_survives():
    """Content anchors that catch gutting edits of the manual's core values."""
    joined = "\n".join(
        (DOCS / f).read_text(encoding="utf-8") for f in CHAPTER_FILES
    ).lower()
    for phrase in [
        "checks, captures, threats",       # blunder scan
        "their",                            # theirs-first ordering appears
        "castle",                           # king safety
        "pre-club",                         # checklist chapter
        "ten-game",                         # starter plan
        "en passant",                       # rules
        "touch move",                       # rules/etiquette
        "chess-puzzle-drills",              # companion 1
        "scoresheet",                       # companion 2
    ]:
        assert phrase in joined, f"key phrase missing: {phrase}"


def test_checklist_chapter_has_boxes():
    raw = (DOCS / "11-pre-club-checklist.md").read_text(encoding="utf-8")
    assert raw.count("- [ ]") >= 20
    raw10 = (DOCS / "10-ten-game-plan.md").read_text(encoding="utf-8")
    assert raw10.count("- [ ]") >= 5


def test_ten_game_plan_games():
    raw = (DOCS / "10-ten-game-plan.md").read_text(encoding="utf-8")
    for marker in ["Games 1–2", "Games 3–4", "Games 5–6", "Games 7–8", "Games 9–10"]:
        assert marker in raw, f"missing {marker} in the ten-game plan"
    assert "club" in raw and "annotate" in raw


# --------------------------------------------------------------- build ---


def test_build_creates_expected_pages(built: Path):
    names = sorted(p.name for p in built.glob("*.html"))
    assert names == sorted(
        ["index.html", "manual.html"] + [f[:-3] + ".html" for f in CHAPTER_FILES]
    )
    assert (built / "assets" / "style.css").read_bytes() == (
        ROOT / "assets" / "style.css"
    ).read_bytes()


def test_pages_parse_and_have_structure(built: Path):
    for html_path in sorted(built.glob("*.html")):
        text = html_path.read_text(encoding="utf-8")
        assert '<meta charset="utf-8">' in text
        assert 'rel="stylesheet" href="assets/style.css"' in text
        parser = _Lenient()
        parser.feed(text)
        assert parser.ok(), (
            f"{html_path.name}: " + " | ".join(parser.problems or ["unbalanced stack"])
        )


class _Lenient(html.parser.HTMLParser):
    """HTML5-style lenient checker: catches unfilled placeholders and truly
    broken tag soup (e.g. a stray </h1> with no opener), while tolerating
    void elements and implicit closes."""

    VOID = {"meta", "link", "br", "img", "hr", "input", "wbr", "col"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.problems: list[str] = []

    def _template_check(self, attrs):
        for name, value in attrs:
            if value and "{" in value and "}" in value:
                self.problems.append(f"unfilled template in attr {name}={value}")

    def handle_starttag(self, tag, attrs):
        self._template_check(attrs)
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            self.problems.append(f"end tag for void element: {tag}")
            return
        if not self.stack:
            self.problems.append(f"stray </{tag}>")
        elif tag in self.stack:  # tolerate implicit closes of unclosed inline tags
            while self.stack:
                top = self.stack.pop()
                if top == tag:
                    break
        else:
            self.problems.append(f"unmatched </{tag}> (stack tail={self.stack[-3:]})")

    def handle_startendtag(self, tag, attrs):
        self._template_check(attrs)

    def handle_data(self, data):
        if "{" in data and "}" in data:
            self.problems.append(f"unfilled template in text: {data[:60]!r}")

    def ok(self) -> bool:
        return not self.problems and not self.stack


def test_no_external_network_references(built: Path):
    for html_path in built.rglob("*"):
        if html_path.suffix in {".html", ".css"}:
            text = html_path.read_text(encoding="utf-8")
            for bad in ("http://", "https://", "://"):
                assert bad not in text, f"{html_path.name} contains '{bad}'"


def test_no_unconverted_md_links(built: Path):
    for html_path in built.glob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        assert "](" not in text, f"{html_path.name}: raw markdown link survived"
        for href in re.findall(r'href="([^"]+)"', text):
            if href.endswith(".md") or ".md#" in href:
                pytest.fail(f"{html_path.name} still links a .md source: {href}")


def test_all_internal_hrefs_resolve(built: Path):
    for html_path in built.glob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', text):
            assert href.startswith("#") or href.startswith("assets/") or (
                (html_path.parent / href).exists()
            ), f"{html_path.name}: broken href {href}"


def test_navigation_wiring(built: Path):
    ch2 = (built / "02-rules-refresher.html").read_text(encoding="utf-8")
    assert 'href="01-welcome-back.html"' in ch2
    assert 'href="03-opening-principles.html"' in ch2
    assert 'href="index.html"' in ch2
    gloss = (built / "12-glossary.html").read_text(encoding="utf-8")
    assert 'href="11-pre-club-checklist.html"' in gloss
    assert "Next</span>" not in gloss or gloss.count("pagenav") == 1
    index = (built / "index.html").read_text(encoding="utf-8")
    for title in EXPECT_TITLES:
        assert title in index
    manual = (built / "manual.html").read_text(encoding="utf-8")
    for title in EXPECT_TITLES:
        assert title in manual
    assert manual.count("chapter") >= 12


def test_checklists_render_as_checkboxes(built: Path):
    club = (built / "11-pre-club-checklist.html").read_text(encoding="utf-8")
    assert club.count("class=\"todo\"") >= 20
    assert "\u2610" in club
    plan = (built / "10-ten-game-plan.html").read_text(encoding="utf-8")
    assert "\u2610" in plan


def test_built_pages_carry_chapter_titles(built: Path):
    for fname, title in zip(CHAPTER_FILES, EXPECT_TITLES):
        page = (built / (fname[:-3] + ".html")).read_text(encoding="utf-8")
        h1 = re.search(r"<h1>(.*?)</h1>", page)
        assert h1 and title in h1.group(1), f"{fname}: wrong h1"
        assert "<p class=\"summary\">" in page


# ------------------------------------------------------- build --check ---


def test_check_mode_passes(tmp_path: Path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "build.py"), "--check"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK" in result.stdout


# ---------------------------------------------------- committed site ---


def test_committed_site_matches_fresh_build(built: Path):
    committed = ROOT / "site"
    if not committed.exists():
        pytest.fail("site/ is not committed — run build.py before committing")
    for rel in ["index.html", "manual.html", "assets/style.css"] + [
        f[:-3] + ".html" for f in CHAPTER_FILES
    ]:
        assert (committed / rel).exists(), f"site/{rel} missing"
        assert (committed / rel).read_bytes() == (built / rel).read_bytes(), (
            f"site/{rel} is stale — rerun build.py"
        )


# --------------------------------------------------------- repo file ---


def test_license_exact():
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Copyright (c) 2026 Asdale Dynamics, LLC" in text
    assert text.startswith("MIT License")


def test_readme_credited():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Asdale Dynamics, LLC" in text
    assert "MIT" in text
    assert "What's in the guide" in text and "How to build" in text


def test_status_exists():
    text = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    assert "STATUS" in text and "Known gaps" in text
