#!/usr/bin/env python3
"""Visit every source link in the guide and report the ones that need a look.

Each link ends up in one of these groups:

  ok           the page loaded at the same address
  moved        the page loaded, but only after redirecting to another address
  changed      the page loaded, but its title is not the one in the baseline
  blocked      the site turned away an automated visitor (401, 403, 429 or a
               bot check page); open it in a browser and check it by hand
  dead         404, 410, or a "page not found" page
  unreachable  timeouts, DNS failures, refused connections and server errors

Usage:
  python scripts/check_links.py                  check every link under docs/
  python scripts/check_links.py --stats          count topics and sources (no network)
  python scripts/check_links.py --list           print every link and where it is used
  python scripts/check_links.py --json report.json --markdown report.md
  python scripts/check_links.py --update-baseline

The exit code is 1 when a link is dead, or also unreachable with --strict.
Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import datetime as dt
import html
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DOCS = REPO_ROOT / "docs"
DEFAULT_BASELINE = REPO_ROOT / "scripts" / "link_baseline.json"
USER_AGENT = "Mozilla/5.0 (compatible; living-in-qatar-linkcheck/1.0; +https://github.com/Ifazawezk/living-in-qatar)"
MAX_BYTES = 512 * 1024
# Links to this repository are not sources and may not exist before a push
SKIP_PREFIXES = ("https://github.com/Ifazawezk/living-in-qatar",)

STATUSES = ("dead", "unreachable", "moved", "changed", "blocked", "ok")

LINK = re.compile(r"\]\((https?://[^)\s]+)\)|<(https?://[^>\s]+)>")
FOOTNOTE_DEF = re.compile(r"^\[\^([^\]\s]+)\]:\s*(.*)$")
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)

# Pages that bot protection serves instead of the real content
CHALLENGE_TITLES = ("just a moment", "attention required", "access denied", "request rejected", "web page blocked")
CHALLENGE_BODY = (
    "cf-chl-",
    "what code is in the image",
    "your support id is",
    "incapsula incident",
    "the url you requested has been blocked",
)
NOT_FOUND_MARKERS = ("page not found", "page-not-found", "404 not found", "الصفحة غير موجودة", "الصفحة المطلوبة غير موجودة")


@dataclass
class Location:
    file: str
    line: int


@dataclass
class Result:
    url: str
    status: str
    code: int | None = None
    final_url: str | None = None
    title: str | None = None
    detail: str = ""
    seconds: float = 0.0
    locations: list[Location] = field(default_factory=list)


# ---------------------------------------------------------------- collecting


def markdown_files(docs: Path) -> list[Path]:
    return sorted(p for p in docs.rglob("*.md") if ".vitepress" not in p.parts and "node_modules" not in p.parts)


def collect_links(docs: Path) -> dict[str, list[Location]]:
    """Map every external link in the Markdown files to the places that use it."""
    links: dict[str, list[Location]] = defaultdict(list)
    for path in markdown_files(docs):
        in_fence = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for a, b in LINK.findall(line):
                url = (a or b).rstrip(".,;")
                if url.startswith(SKIP_PREFIXES):
                    continue
                links[url].append(Location(path.relative_to(docs).as_posix(), number))
    return dict(links)


def guide_stats(docs: Path) -> dict[str, object]:
    """Numbers for the README badges: topics, languages and official sources."""
    english = sorted(p for p in (docs / "guide").glob("*.md") if p.name != "index.md")
    arabic = sorted(p for p in (docs / "ar" / "guide").glob("*.md") if p.name != "index.md")
    sources: set[str] = set()
    footnotes = 0
    oldest = None
    for path in english + arabic:
        for line in path.read_text(encoding="utf-8").splitlines():
            match = FOOTNOTE_DEF.match(line)
            if not match:
                continue
            footnotes += 1
            for a, b in LINK.findall(match.group(2)):
                sources.add(normalise(a or b))
            stamp = re.search(r"(\d{4}-\d{2})\.?\s*$", match.group(2))
            if stamp and (oldest is None or stamp.group(1) < oldest):
                oldest = stamp.group(1)
    hosts = sorted({urlsplit(u).hostname or "" for u in sources})
    return {
        "topics": len(english),
        "arabic_pages": len(arabic),
        "sources": len(sources),
        "footnotes": footnotes,
        "domains": len(hosts),
        "oldest_check": oldest,
        "hosts": hosts,
    }


# ------------------------------------------------------------------ checking


def normalise(url: str) -> str:
    """Drop differences that do not matter: scheme, www, case of host, trailing slash."""
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    path = parts.path.rstrip("/") or ""
    return urlunsplit(("https", host, path, parts.query, ""))


def page_title(body: str) -> str | None:
    match = TITLE.search(body)
    if not match:
        return None
    title = re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()
    return title or None


def looks_like_challenge(body: str) -> bool:
    title = (page_title(body) or "").lower()
    if any(marker in title for marker in CHALLENGE_TITLES):
        return True
    lowered = body[:20000].lower()
    return any(marker in lowered for marker in CHALLENGE_BODY)


def looks_not_found(final_url: str, title: str | None) -> bool:
    text = f"{final_url} {title or ''}".lower()
    return any(marker in text for marker in NOT_FOUND_MARKERS)


class _Redirects(urllib.request.HTTPRedirectHandler):
    max_redirections = 10


def fetch(url: str, timeout: float) -> tuple[int, str, str]:
    """Return (status code, final url, start of the body)."""
    opener = urllib.request.build_opener(_Redirects())
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8", "Accept-Language": "en,ar;q=0.8"},
    )
    with opener.open(request, timeout=timeout) as response:
        body = response.read(MAX_BYTES)
        charset = response.headers.get_content_charset() or "utf-8"
        return response.status, response.geturl(), body.decode(charset, errors="replace")


def classify(url: str, code: int, final_url: str, body: str, baseline: dict[str, dict] | None = None) -> Result:
    title = page_title(body)
    result = Result(url=url, status="ok", code=code, final_url=final_url, title=title)
    if looks_like_challenge(body) and (code in (401, 403, 429, 503) or code < 400):
        result.status = "blocked"
        result.detail = "bot check page instead of content"
    elif code in (401, 403, 429):
        result.status = "blocked"
        result.detail = f"HTTP {code}"
    elif code in (404, 410):
        result.status = "dead"
        result.detail = f"HTTP {code}"
    elif code >= 500:
        result.status = "unreachable"
        result.detail = f"HTTP {code}"
    elif code >= 400:
        result.status = "dead"
        result.detail = f"HTTP {code}"
    elif looks_not_found(final_url, title):
        result.status = "dead"
        result.detail = "loads a 'page not found' page"
    elif normalise(final_url) != normalise(url):
        result.status = "moved"
        result.detail = f"now at {final_url}"
    elif baseline and url in baseline:
        before = (baseline[url].get("title") or "").strip()
        if before and title and before.casefold() != title.casefold():
            result.status = "changed"
            result.detail = f"title was '{before}', now '{title}'"
    return result


def check_url(url: str, timeout: float = 25, retries: int = 1, baseline: dict[str, dict] | None = None) -> Result:
    started = time.monotonic()
    attempt = 0
    while True:
        try:
            code, final_url, body = fetch(url, timeout)
            result = classify(url, code, final_url, body, baseline)
        except urllib.error.HTTPError as error:
            try:
                body = error.read(MAX_BYTES).decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001 - the body is only a hint
                body = ""
            result = classify(url, error.code, error.geturl() or url, body, baseline)
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, ssl.SSLError) as error:
            reason = getattr(error, "reason", error)
            result = Result(url=url, status="unreachable", detail=type(reason).__name__ + ": " + str(reason))
        # Government servers sometimes answer 404 for a page that is fine a
        # moment later, so a link gets a second chance before it counts as dead.
        if result.status not in ("dead", "unreachable") or attempt >= retries:
            break
        attempt += 1
        time.sleep(2)
    result.seconds = round(time.monotonic() - started, 2)
    return result


def check_all(
    links: dict[str, list[Location]],
    workers: int = 8,
    timeout: float = 25,
    retries: int = 1,
    delay: float = 1.0,
    baseline: dict[str, dict] | None = None,
    progress=None,
) -> list[Result]:
    """Check links in parallel across sites, but one at a time per site."""
    by_host: dict[str, list[str]] = defaultdict(list)
    for url in links:
        by_host[urlsplit(url).hostname or ""].append(url)

    def run_host(urls: list[str]) -> list[Result]:
        results = []
        for index, url in enumerate(urls):
            if index:
                time.sleep(delay)
            result = check_url(url, timeout=timeout, retries=retries, baseline=baseline)
            result.locations = links[url]
            if progress:
                progress(result)
            results.append(result)
        return results

    results: list[Result] = []
    with futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for batch in pool.map(run_host, by_host.values()):
            results.extend(batch)
    order = {status: i for i, status in enumerate(STATUSES)}
    return sorted(results, key=lambda r: (order[r.status], r.url))


# ------------------------------------------------------------------- reports


def summary(results: list[Result]) -> dict[str, int]:
    counts = {status: 0 for status in STATUSES}
    for result in results:
        counts[result.status] += 1
    return counts


def text_report(results: list[Result]) -> str:
    lines = []
    for status in STATUSES:
        group = [r for r in results if r.status == status]
        if not group or status == "ok":
            continue
        lines.append(f"\n{status.upper()} ({len(group)})")
        for result in group:
            used = ", ".join(f"{loc.file}:{loc.line}" for loc in result.locations[:3])
            more = f" and {len(result.locations) - 3} more" if len(result.locations) > 3 else ""
            lines.append(f"  {result.url}")
            if result.detail:
                lines.append(f"    {result.detail}")
            if used:
                lines.append(f"    used in {used}{more}")
    counts = summary(results)
    lines.append("\n" + ", ".join(f"{counts[s]} {s}" for s in STATUSES) + f" ({len(results)} links)")
    return "\n".join(lines).lstrip("\n")


def markdown_report(results: list[Result], when: str) -> str:
    counts = summary(results)
    out = [f"# Source link report, {when}", "", "| Status | Links |", "| --- | --- |"]
    out += [f"| {s} | {counts[s]} |" for s in STATUSES]
    for status in STATUSES:
        group = [r for r in results if r.status == status]
        if not group or status == "ok":
            continue
        out += ["", f"## {status.capitalize()}", ""]
        for result in group:
            where = ", ".join(f"`{loc.file}:{loc.line}`" for loc in result.locations[:3])
            detail = f" ({result.detail})" if result.detail else ""
            out.append(f"- {result.url}{detail}, used in {where}")
    return "\n".join(out) + "\n"


def load_baseline(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_baseline(path: Path, results: list[Result], old: dict[str, dict]) -> None:
    data = dict(old)
    for result in results:
        if result.status in ("ok", "moved", "changed") and result.title:
            data[result.url] = {"title": result.title, "final_url": result.final_url}
    path.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the source links in the guide.")
    parser.add_argument("--docs", type=Path, default=DEFAULT_DOCS, help="docs folder (default: docs)")
    parser.add_argument("--stats", action="store_true", help="print topic and source counts, no network")
    parser.add_argument("--list", action="store_true", help="print every link and where it is used, no network")
    parser.add_argument("--only", metavar="TEXT", help="only check links that contain TEXT")
    parser.add_argument("--workers", type=int, default=8, help="sites checked at the same time (default: 8)")
    parser.add_argument("--timeout", type=float, default=25, help="seconds per request (default: 25)")
    parser.add_argument("--delay", type=float, default=1.0, help="pause between requests to one site (default: 1)")
    parser.add_argument("--retries", type=int, default=1, help="retries for dead or unreachable links (default: 1)")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE, help="saved page titles")
    parser.add_argument("--update-baseline", action="store_true", help="save the titles seen in this run")
    parser.add_argument("--json", type=Path, help="write the full results as JSON")
    parser.add_argument("--markdown", type=Path, help="write a Markdown report, handy for an issue")
    parser.add_argument("--strict", action="store_true", help="also fail on unreachable links")
    parser.add_argument("--quiet", action="store_true", help="no progress lines")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    docs = args.docs.resolve()
    if args.stats:
        stats = guide_stats(docs)
        for key, value in stats.items():
            print(f"{key}: {', '.join(value) if isinstance(value, list) else value}")
        return 0

    links = collect_links(docs)
    if args.only:
        links = {url: locs for url, locs in links.items() if args.only in url}
    if args.list:
        for url, locations in sorted(links.items()):
            print(f"{url}  ({len(locations)} uses)")
        print(f"{len(links)} links")
        return 0
    if not links:
        print("no links found")
        return 0

    baseline = load_baseline(args.baseline)

    def progress(result: Result) -> None:
        if not args.quiet:
            print(f"  {result.status:<11} {result.url}", flush=True)

    print(f"checking {len(links)} links on {len({urlsplit(u).hostname for u in links})} sites")
    results = check_all(
        links,
        workers=args.workers,
        timeout=args.timeout,
        retries=args.retries,
        delay=args.delay,
        baseline=baseline,
        progress=progress,
    )
    print()
    print(text_report(results))

    when = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    if args.json:
        payload = {"checked_at": when, "summary": summary(results), "results": [asdict(r) for r in results]}
        args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown_report(results, when), encoding="utf-8")
    if args.update_baseline:
        save_baseline(args.baseline, results, baseline)

    counts = summary(results)
    failed = counts["dead"] + (counts["unreachable"] if args.strict else 0)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
