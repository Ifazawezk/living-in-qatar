#!/usr/bin/env python3
"""Check that every paragraph in the guide points to an official source.

For each Markdown page under docs/guide (English) and docs/ar/guide (Arabic):

* the front matter has a title, a description and lastChecked (YYYY-MM)
* every paragraph, list item, quote and table row cites a source, either a
  footnote such as [^moi-visas] or an inline link to an official domain
* every footnote links to an official domain and says when it was last
  checked: "Last checked: 2026-10" or, in Arabic, "آخر تحقق: 2026-10"
* every footnote is used, and every footnote reference is defined
* each English page has an Arabic twin with the same footnote names, so the
  two versions cite the same sources
* style: no em or en dashes, no emoji

Official domains live in scripts/official_domains.txt.

Usage:
    python scripts/lint_content.py
    python scripts/lint_content.py --root docs --stale-after 12

Exit code 0 when the guide is clean, 1 when there are errors.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = REPO_ROOT / "docs"
DEFAULT_DOMAINS = REPO_ROOT / "scripts" / "official_domains.txt"
GUIDE_DIRS = ("guide", "ar/guide")

FOOTNOTE_DEF = re.compile(r"^\[\^([^\]\s]+)\]:\s*(.*)$")
FOOTNOTE_REF = re.compile(r"\[\^([^\]\s]+)\](?!:)")
INLINE_URL = re.compile(r"\]\((https?://[^)\s]+)\)|<(https?://[^>\s]+)>")
ANY_URL = re.compile(r"https?://[^\s)>\]]+")
LAST_CHECKED = re.compile(r"(?:Last checked|آخر تحقق):\s*(\d{4})-(\d{2})")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
HEADING = re.compile(r"^#{1,6}\s")
FENCE = re.compile(r"^\s*(```|~~~)")
CONTAINER = re.compile(r"^\s*:::")
HTML_ONLY = re.compile(r"^\s*(?:<[^>]+>\s*)+$")
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
SEE_ALSO = re.compile(r"^(?:See also|انظر أيضًا|انظر أيضا)", re.IGNORECASE)
DASHES = re.compile("[–—]")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
REQUIRED_FRONT_MATTER = ("title", "description", "lastChecked")


@dataclass
class Problem:
    path: Path
    line: int
    message: str
    level: str = "error"

    def format(self, base: Path | None = None) -> str:
        shown = self.path
        if base is not None:
            try:
                shown = self.path.relative_to(base)
            except ValueError:
                pass
        return f"{shown.as_posix()}:{self.line}: {self.level}: {self.message}"


@dataclass
class Block:
    kind: str  # paragraph, item, quote, row
    line: int
    text: str


@dataclass
class Page:
    path: Path
    front_matter: dict[str, str] = field(default_factory=dict)
    blocks: list[Block] = field(default_factory=list)
    footnotes: dict[str, tuple[int, str]] = field(default_factory=dict)
    problems: list[Problem] = field(default_factory=list)


def load_domains(path: Path) -> list[str]:
    domains = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip().lower()
        if line:
            domains.append(line)
    return domains


def is_official(url: str, domains: list[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in domains)


def split_front_matter(lines: list[str]) -> tuple[dict[str, str], int]:
    """Return the front matter keys and the index of the first body line."""
    if not lines or lines[0].strip() != "---":
        return {}, 0
    data: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return data, i + 1
        if ":" in lines[i] and not lines[i].startswith((" ", "\t")):
            key, value = lines[i].split(":", 1)
            data[key.strip()] = value.strip().strip("'\"")
    return data, 0


def parse_page(path: Path, text: str) -> Page:
    page = Page(path=path)
    lines = text.splitlines()
    page.front_matter, start = split_front_matter(lines)

    current: Block | None = None
    in_fence = False
    in_comment = False
    in_footnote: str | None = None
    previous_row: Block | None = None

    def close() -> None:
        nonlocal current
        if current is not None and current.text.strip():
            page.blocks.append(current)
        current = None

    for index in range(start, len(lines)):
        number = index + 1
        line = lines[index]
        stripped = line.strip()

        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if stripped.startswith("<!--"):
            close()
            in_comment = "-->" not in stripped
            continue
        if FENCE.match(line):
            close()
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if DASHES.search(line):
            page.problems.append(Problem(path, number, "style: use a comma, colon or full stop instead of a long dash"))
        if EMOJI.search(line):
            page.problems.append(Problem(path, number, "style: no emoji in the guide"))

        match = FOOTNOTE_DEF.match(line)
        if match:
            close()
            in_footnote = match.group(1)
            if in_footnote in page.footnotes:
                page.problems.append(Problem(path, number, f"footnote [^{in_footnote}] is defined twice"))
            page.footnotes[in_footnote] = (number, match.group(2))
            continue
        if in_footnote is not None:
            if stripped and line.startswith(("    ", "\t")):
                first_line, body = page.footnotes[in_footnote]
                page.footnotes[in_footnote] = (first_line, body + " " + stripped)
                continue
            in_footnote = None

        if not stripped:
            close()
            previous_row = None
            continue
        if HEADING.match(line) or CONTAINER.match(line) or HTML_ONLY.match(line):
            close()
            continue

        if stripped.startswith("|"):
            close()
            if TABLE_SEPARATOR.match(stripped):
                # the row above the separator is the header, which holds no claim
                if previous_row is not None and page.blocks and page.blocks[-1] is previous_row:
                    page.blocks.pop()
                continue
            previous_row = Block("row", number, stripped)
            page.blocks.append(previous_row)
            continue

        if stripped.startswith(">"):
            content = stripped.lstrip(">").strip()
            if current is None or current.kind != "quote":
                close()
                current = Block("quote", number, "")
            current.text += " " + content
            continue

        if LIST_ITEM.match(line):
            close()
            current = Block("item", number, LIST_ITEM.sub("", line, count=1))
            continue

        if current is None:
            current = Block("paragraph", number, stripped)
        else:
            current.text += " " + stripped
    close()
    return page


def check_page(page: Page, domains: list[str], today: dt.date, stale_after: int | None) -> list[Problem]:
    problems = list(page.problems)
    path = page.path

    for key in REQUIRED_FRONT_MATTER:
        if not page.front_matter.get(key):
            problems.append(Problem(path, 1, f"front matter is missing '{key}'"))
    checked = page.front_matter.get("lastChecked", "")
    if checked and not re.fullmatch(r"\d{4}-\d{2}", checked):
        problems.append(Problem(path, 1, "lastChecked must look like 2026-10"))

    used: set[str] = set()
    for block in page.blocks:
        refs = FOOTNOTE_REF.findall(block.text)
        used.update(refs)
        if SEE_ALSO.match(block.text.strip()) and not ANY_URL.search(block.text):
            continue
        official = False
        for ref in refs:
            if ref not in page.footnotes:
                problems.append(Problem(path, block.line, f"footnote [^{ref}] is used but never defined"))
                continue
            if any(is_official(u, domains) for u in ANY_URL.findall(page.footnotes[ref][1])):
                official = True
        for a, b in INLINE_URL.findall(block.text):
            if is_official(a or b, domains):
                official = True
        if not official:
            preview = re.sub(r"\s+", " ", block.text.strip())[:70]
            problems.append(Problem(path, block.line, f"{block.kind} has no official source: \"{preview}\""))

    for name, (line, body) in page.footnotes.items():
        urls = ANY_URL.findall(body)
        if not urls:
            problems.append(Problem(path, line, f"footnote [^{name}] has no link"))
        for url in urls:
            if not is_official(url, domains):
                host = urlparse(url).hostname
                problems.append(Problem(path, line, f"footnote [^{name}] links to {host}, which is not in official_domains.txt"))
        stamp = LAST_CHECKED.search(body)
        if not stamp:
            problems.append(Problem(path, line, f"footnote [^{name}] has no 'Last checked: YYYY-MM' date"))
        elif stale_after is not None:
            year, month = int(stamp.group(1)), int(stamp.group(2))
            age = (today.year - year) * 12 + (today.month - month)
            if age > stale_after:
                problems.append(Problem(path, line, f"footnote [^{name}] was last checked {age} months ago", "warning"))
        if name not in used:
            problems.append(Problem(path, line, f"footnote [^{name}] is defined but never used"))
    return problems


def check_twins(root: Path, pages: dict[Path, Page]) -> list[Problem]:
    problems = []
    english = root / "guide"
    arabic = root / "ar" / "guide"
    for path, page in pages.items():
        if path.parent != english:
            continue
        twin = arabic / path.name
        if twin not in pages:
            problems.append(Problem(path, 1, f"no Arabic version at {twin.relative_to(root).as_posix()}"))
            continue
        missing = set(page.footnotes) - set(pages[twin].footnotes)
        extra = set(pages[twin].footnotes) - set(page.footnotes)
        if missing:
            problems.append(Problem(twin, 1, "Arabic page is missing sources: " + ", ".join(sorted(missing))))
        if extra:
            problems.append(Problem(twin, 1, "Arabic page has sources the English page lacks: " + ", ".join(sorted(extra))))
    for path in pages:
        if path.parent == arabic and not (english / path.name).exists():
            problems.append(Problem(path, 1, f"no English version at guide/{path.name}"))
    return problems


def lint(root: Path, domains: list[str], today: dt.date | None = None, stale_after: int | None = None) -> list[Problem]:
    today = today or dt.date.today()
    pages: dict[Path, Page] = {}
    for sub in GUIDE_DIRS:
        folder = root / sub
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.md")):
            if path.name.lower() == "index.md":
                continue
            pages[path] = parse_page(path, path.read_text(encoding="utf-8"))
    problems: list[Problem] = []
    for page in pages.values():
        problems.extend(check_page(page, domains, today, stale_after))
    problems.extend(check_twins(root, pages))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="docs folder (default: docs)")
    parser.add_argument("--domains", type=Path, default=DEFAULT_DOMAINS, help="file with official domains")
    parser.add_argument("--stale-after", type=int, default=None, metavar="MONTHS",
                        help="warn about sources not checked for this many months")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = args.root.resolve()
    problems = lint(root, load_domains(args.domains), stale_after=args.stale_after)
    errors = [p for p in problems if p.level == "error"]
    for problem in problems:
        print(problem.format(root))
    pages = sum(len(list((root / sub).glob("*.md"))) for sub in GUIDE_DIRS if (root / sub).is_dir())
    print(f"checked {pages} pages: {len(errors)} errors, {len(problems) - len(errors)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
