"""Tests for scripts/check_links.py.

A small local web server plays the part of the official sites, so the tests
never touch the internet. Run with:  python -m unittest discover -s tests
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check_links  # noqa: E402


def page(title: str, body: str = "") -> bytes:
    return f"<!doctype html><html><head><title>{title}</title></head><body>{body}</body></html>".encode()


class FakeSite(BaseHTTPRequestHandler):
    routes = {
        "/ok": (200, {}, page("Residence permit services")),
        "/ok-arabic": (200, {}, page("خدمات الإقامة")),
        "/old-address": (301, {"Location": "/new-address"}, b""),
        "/new-address": (200, {}, page("New address")),
        "/with-slash": (301, {"Location": "/with-slash/"}, b""),
        "/with-slash/": (200, {}, page("Same page")),
        "/gone": (404, {}, page("Not here")),
        "/removed": (410, {}, b""),
        "/forbidden": (403, {}, page("Forbidden")),
        "/challenge": (403, {}, page("Just a moment...", "<div id='cf-chl-widget'></div>")),
        "/captcha": (200, {}, page("", "What code is in the image? Your support ID is: 123.")),
        "/soft-404": (302, {"Location": "/page-not-found?initialRequestUrl=x"}, b""),
        "/page-not-found": (200, {}, page("Page not found")),
        "/broken": (500, {}, page("Server error")),
        "/too-many": (429, {}, b""),
    }

    flaky_hits = 0

    def do_GET(self):  # noqa: N802 - name required by BaseHTTPRequestHandler
        path = self.path.split("?")[0]
        code, headers, body = self.routes.get(path, (404, {}, page("Not found")))
        if path == "/flaky":
            # a 404 on the first visit, then the real page
            FakeSite.flaky_hits += 1
            code, body = (404, page("Not found")) if FakeSite.flaky_hits == 1 else (200, page("Back again"))
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # keep test output clean
        pass


class ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeSite)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def check(self, path: str, **kwargs) -> check_links.Result:
        return check_links.check_url(self.base + path, timeout=5, retries=0, **kwargs)


class CheckUrlTests(ServerTestCase):
    def test_ok_page_and_title(self):
        result = self.check("/ok")
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.code, 200)
        self.assertEqual(result.title, "Residence permit services")

    def test_arabic_title_is_read(self):
        self.assertEqual(self.check("/ok-arabic").title, "خدمات الإقامة")

    def test_redirect_to_another_page_is_moved(self):
        result = self.check("/old-address")
        self.assertEqual(result.status, "moved")
        self.assertTrue(result.final_url.endswith("/new-address"))

    def test_trailing_slash_redirect_is_still_ok(self):
        self.assertEqual(self.check("/with-slash").status, "ok")

    def test_404_and_410_are_dead(self):
        self.assertEqual(self.check("/gone").status, "dead")
        self.assertEqual(self.check("/removed").status, "dead")

    def test_a_passing_404_gets_a_second_chance(self):
        FakeSite.flaky_hits = 0
        original = check_links.time.sleep
        check_links.time.sleep = lambda seconds: None
        try:
            result = check_links.check_url(self.base + "/flaky", timeout=5, retries=1)
        finally:
            check_links.time.sleep = original
        self.assertEqual(result.status, "ok")
        self.assertEqual(FakeSite.flaky_hits, 2)

    def test_redirect_to_not_found_page_is_dead(self):
        result = self.check("/soft-404")
        self.assertEqual(result.status, "dead")
        self.assertIn("not found", result.detail)

    def test_forbidden_and_rate_limited_are_blocked_not_dead(self):
        self.assertEqual(self.check("/forbidden").status, "blocked")
        self.assertEqual(self.check("/too-many").status, "blocked")

    def test_bot_check_pages_are_blocked(self):
        self.assertEqual(self.check("/challenge").status, "blocked")
        self.assertEqual(self.check("/captcha").status, "blocked")

    def test_server_error_is_unreachable(self):
        self.assertEqual(self.check("/broken").status, "unreachable")

    def test_connection_refused_is_unreachable(self):
        result = check_links.check_url("http://127.0.0.1:9/nothing", timeout=3, retries=0)
        self.assertEqual(result.status, "unreachable")
        self.assertTrue(result.detail)

    def test_title_change_against_baseline(self):
        url = self.base + "/ok"
        baseline = {url: {"title": "Visa services"}}
        result = check_links.check_url(url, timeout=5, retries=0, baseline=baseline)
        self.assertEqual(result.status, "changed")
        self.assertIn("Visa services", result.detail)

    def test_same_title_in_baseline_is_ok(self):
        url = self.base + "/ok"
        baseline = {url: {"title": "residence permit services"}}
        result = check_links.check_url(url, timeout=5, retries=0, baseline=baseline)
        self.assertEqual(result.status, "ok")


class CollectAndReportTests(ServerTestCase):
    def make_docs(self, folder: Path) -> Path:
        docs = folder / "docs"
        (docs / "guide").mkdir(parents=True)
        (docs / "ar" / "guide").mkdir(parents=True)
        (docs / ".vitepress").mkdir()
        (docs / "guide" / "visas.md").write_text(
            "---\ntitle: Visas\n---\n\n"
            "Entry rules.[^moi]\n\n"
            "```\nhttps://in-a-code-block.example/ignored\n```\n\n"
            f"Inline [link]({self.base}/gone).\n\n"
            "## Sources\n\n"
            f"[^moi]: Ministry of Interior, [Visas]({self.base}/ok). Last checked: 2026-10.\n",
            encoding="utf-8",
        )
        (docs / "ar" / "guide" / "visas.md").write_text(
            f"قواعد الدخول.[^moi]\n\n[^moi]: وزارة الداخلية، [التأشيرات]({self.base}/ok). آخر تحقق: 2026-09.\n",
            encoding="utf-8",
        )
        (docs / ".vitepress" / "notes.md").write_text(f"[skip]({self.base}/broken)\n", encoding="utf-8")
        return docs

    def test_collect_links_with_locations(self):
        with tempfile.TemporaryDirectory() as tmp:
            links = check_links.collect_links(self.make_docs(Path(tmp)))
        self.assertEqual(set(links), {self.base + "/ok", self.base + "/gone"})
        self.assertEqual(len(links[self.base + "/ok"]), 2)
        files = {loc.file for loc in links[self.base + "/ok"]}
        self.assertEqual(files, {"guide/visas.md", "ar/guide/visas.md"})

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            stats = check_links.guide_stats(self.make_docs(Path(tmp)))
        self.assertEqual(stats["topics"], 1)
        self.assertEqual(stats["arabic_pages"], 1)
        self.assertEqual(stats["sources"], 1)
        self.assertEqual(stats["footnotes"], 2)
        self.assertEqual(stats["oldest_check"], "2026-09")

    def test_main_fails_on_dead_link_and_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = self.make_docs(Path(tmp))
            report_json = Path(tmp) / "report.json"
            report_md = Path(tmp) / "report.md"
            baseline = Path(tmp) / "baseline.json"
            out = io.StringIO()
            with redirect_stdout(out):
                code = check_links.main([
                    "--docs", str(docs), "--quiet", "--delay", "0", "--retries", "0",
                    "--json", str(report_json), "--markdown", str(report_md),
                    "--baseline", str(baseline), "--update-baseline",
                ])
            self.assertEqual(code, 1)
            data = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual(data["summary"]["dead"], 1)
            self.assertEqual(data["summary"]["ok"], 1)
            self.assertIn("guide/visas.md", report_md.read_text(encoding="utf-8"))
            saved = json.loads(baseline.read_text(encoding="utf-8"))
            self.assertEqual(saved[self.base + "/ok"]["title"], "Residence permit services")
            self.assertIn("DEAD (1)", out.getvalue())

    def test_main_passes_when_links_are_fine(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = self.make_docs(Path(tmp))
            with redirect_stdout(io.StringIO()):
                code = check_links.main(["--docs", str(docs), "--quiet", "--delay", "0", "--only", "/ok",
                                         "--baseline", str(Path(tmp) / "none.json")])
            self.assertEqual(code, 0)


class NormaliseTests(unittest.TestCase):
    def test_ignores_scheme_www_case_and_trailing_slash(self):
        self.assertEqual(
            check_links.normalise("http://WWW.Example.qa/Path/"),
            check_links.normalise("https://example.qa/Path"),
        )

    def test_keeps_query(self):
        self.assertNotEqual(
            check_links.normalise("https://example.qa/page?id=1"),
            check_links.normalise("https://example.qa/page?id=2"),
        )


if __name__ == "__main__":
    unittest.main()
