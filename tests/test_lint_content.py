"""Tests for scripts/lint_content.py. Run with:  python -m unittest discover -s tests"""

from __future__ import annotations

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import lint_content  # noqa: E402

DOMAINS = ["gov.qa", "hamad.qa"]
TODAY = dt.date(2026, 10, 30)

FRONT = "---\ntitle: Test\ndescription: A test page.\nlastChecked: 2026-10\n---\n\n# Test\n\n"
MOI = "[^moi]: Ministry of Interior, [Visas](https://portal.moi.gov.qa/visas). Last checked: 2026-10.\n"
MOI_AR = "[^moi]: وزارة الداخلية، [التأشيرات](https://portal.moi.gov.qa/visas). آخر تحقق: 2026-10.\n"


class LintTestCase(unittest.TestCase):
    def lint(self, english: str, arabic: str | None = None, stale_after: int | None = None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "guide").mkdir()
            (root / "ar" / "guide").mkdir(parents=True)
            (root / "guide" / "page.md").write_text(english, encoding="utf-8")
            if arabic is not None:
                (root / "ar" / "guide" / "page.md").write_text(arabic, encoding="utf-8")
            problems = lint_content.lint(root, DOMAINS, today=TODAY, stale_after=stale_after)
        return [p for p in problems if p.level == "error"], [p for p in problems if p.level == "warning"]

    def good_arabic(self, body: str = "فقرة.[^moi]\n\n") -> str:
        return FRONT + body + "## المصادر\n\n" + MOI_AR

    def test_clean_page_passes(self):
        english = FRONT + "A sourced paragraph.[^moi]\n\n- A sourced item.[^moi]\n\n## Sources\n\n" + MOI
        errors, warnings = self.lint(english, self.good_arabic())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_paragraph_without_source_fails(self):
        english = FRONT + "Sourced.[^moi]\n\nNo source in this one,\nover two lines.\n\n## Sources\n\n" + MOI
        errors, _ = self.lint(english, self.good_arabic())
        self.assertEqual(len(errors), 1)
        self.assertIn("paragraph has no official source", errors[0].message)
        self.assertEqual(errors[0].line, 11)

    def test_list_item_without_source_fails(self):
        english = FRONT + "- Sourced.[^moi]\n- Not sourced.\n\n## Sources\n\n" + MOI
        errors, _ = self.lint(english, self.good_arabic())
        self.assertEqual([e.message.split(":")[0] for e in errors], ["item has no official source"])

    def test_inline_official_link_counts_as_source(self):
        english = FRONT + "See [the HMC page](https://www.hamad.qa/page).[^moi]\n\nOnly inline [HMC](https://www.hamad.qa/x).\n\n## Sources\n\n" + MOI
        errors, _ = self.lint(english, self.good_arabic())
        self.assertEqual(errors, [])

    def test_unofficial_link_is_rejected(self):
        english = FRONT + "Claim.[^blog]\n\n## Sources\n\n[^blog]: Some blog, [Post](https://blog.example.com/x). Last checked: 2026-10.\n"
        arabic = FRONT + "ادعاء.[^blog]\n\n[^blog]: مدونة، [منشور](https://blog.example.com/x). آخر تحقق: 2026-10.\n"
        errors, _ = self.lint(english, arabic)
        messages = " ".join(e.message for e in errors)
        self.assertIn("not in official_domains.txt", messages)
        self.assertIn("paragraph has no official source", messages)

    def test_lookalike_domain_is_not_official(self):
        self.assertFalse(lint_content.is_official("https://notgov.qa/x", DOMAINS))
        self.assertFalse(lint_content.is_official("https://gov.qa.example.com/x", DOMAINS))
        self.assertTrue(lint_content.is_official("https://portal.moi.gov.qa/x", DOMAINS))

    def test_footnote_needs_last_checked_date(self):
        english = FRONT + "Claim.[^moi]\n\n## Sources\n\n[^moi]: MOI, [Visas](https://portal.moi.gov.qa/visas).\n"
        errors, _ = self.lint(english, self.good_arabic())
        self.assertTrue(any("Last checked" in e.message for e in errors))

    def test_undefined_and_unused_footnotes(self):
        english = FRONT + "Claim.[^missing]\n\nOther.[^moi]\n\n## Sources\n\n" + MOI + "[^spare]: MOI, [X](https://portal.moi.gov.qa/x). Last checked: 2026-10.\n"
        errors, _ = self.lint(english, self.good_arabic())
        messages = " ".join(e.message for e in errors)
        self.assertIn("[^missing] is used but never defined", messages)
        self.assertIn("[^spare] is defined but never used", messages)

    def test_table_rows_need_sources_but_header_does_not(self):
        english = FRONT + "| Number | Use |\n| --- | --- |\n| 999 | Emergencies[^moi] |\n| 123 | Something |\n\n## Sources\n\n" + MOI
        errors, _ = self.lint(english, self.good_arabic())
        self.assertEqual(len(errors), 1)
        self.assertIn("123", errors[0].message)

    def test_see_also_with_internal_links_is_allowed(self):
        english = FRONT + "Claim.[^moi]\n\nSee also: [Metrash](./metrash.md).\n\n## Sources\n\n" + MOI
        arabic = self.good_arabic("فقرة.[^moi]\n\nانظر أيضًا: [مطراش](./metrash.md).\n\n")
        errors, _ = self.lint(english, arabic)
        self.assertEqual(errors, [])

    def test_code_blocks_and_comments_are_skipped(self):
        english = FRONT + "Claim.[^moi]\n\n```\nno source here\n```\n\n<!-- a note for editors -->\n\n## Sources\n\n" + MOI
        errors, _ = self.lint(english, self.good_arabic())
        self.assertEqual(errors, [])

    def test_long_dashes_and_emoji_are_style_errors(self):
        english = FRONT + "Claim — with a dash.[^moi]\n\nAnd a smiley \U0001F600.[^moi]\n\n## Sources\n\n" + MOI
        errors, _ = self.lint(english, self.good_arabic())
        self.assertEqual(len([e for e in errors if e.message.startswith("style")]), 2)

    def test_front_matter_is_required(self):
        english = "# No front matter\n\nClaim.[^moi]\n\n## Sources\n\n" + MOI
        errors, _ = self.lint(english, self.good_arabic())
        missing = [e for e in errors if "front matter" in e.message]
        self.assertEqual(len(missing), 3)

    def test_arabic_twin_must_exist(self):
        english = FRONT + "Claim.[^moi]\n\n## Sources\n\n" + MOI
        errors, _ = self.lint(english, None)
        self.assertTrue(any("no Arabic version" in e.message for e in errors))

    def test_arabic_twin_must_cite_the_same_sources(self):
        english = FRONT + "Claim.[^moi]\n\nOther.[^hmc]\n\n## Sources\n\n" + MOI + "[^hmc]: HMC, [Card](https://www.hamad.qa/card). Last checked: 2026-10.\n"
        errors, _ = self.lint(english, self.good_arabic())
        self.assertTrue(any("missing sources: hmc" in e.message for e in errors))

    def test_old_sources_give_a_warning(self):
        english = FRONT + "Claim.[^moi]\n\n## Sources\n\n[^moi]: MOI, [Visas](https://portal.moi.gov.qa/visas). Last checked: 2025-01.\n"
        errors, warnings = self.lint(english, self.good_arabic(), stale_after=12)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("21 months", warnings[0].message)

    def test_real_domain_file_loads(self):
        domains = lint_content.load_domains(lint_content.DEFAULT_DOMAINS)
        self.assertIn("gov.qa", domains)
        self.assertTrue(all(" " not in d and not d.startswith("#") for d in domains))


if __name__ == "__main__":
    unittest.main()
