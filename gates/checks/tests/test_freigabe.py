"""Tests fuer J1/J2 — Produktivfreigabe (menschliche Security-/Datenschutz-Abnahme)."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from checks import common, freigabe  # noqa: E402

_FULL = """security:
  freigegeben: true
  von: "Max Mustermann (Security Lead)"
  datum: "2026-06-11"
  referenz: "docs/produktivfreigabe/SECURITY-REVIEW.md"
datenschutz:
  freigegeben: true
  von: "Erika Musterfrau (DSB)"
  datum: "2026-06-11"
"""


def _freigabe(d, text):
    p = os.path.join(d, "docs", "produktivfreigabe")
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, "FREIGABE.yaml"), "w", encoding="utf-8") as f:
        f.write(text)
    return d


class Freigabe(unittest.TestCase):
    def test_no_file_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            for run in (freigabe.run_j1, freigabe.run_j2):
                res = run(d)
                self.assertEqual(res.status, common.SKIP)
                self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)

    def test_both_granted_pass(self):
        with tempfile.TemporaryDirectory() as d:
            _freigabe(d, _FULL)
            self.assertEqual(freigabe.run_j1(d).status, common.PASS)
            self.assertEqual(freigabe.run_j2(d).status, common.PASS)
            self.assertIn("Mustermann", freigabe.run_j1(d).summary)

    def test_not_granted_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _freigabe(d, _FULL.replace("freigegeben: true", "freigegeben: false", 1))  # security false
            self.assertEqual(freigabe.run_j1(d).status, common.FAIL)
            self.assertEqual(freigabe.run_j2(d).status, common.PASS)  # datenschutz weiter ok

    def test_granted_but_unsigned_fails(self):
        # freigegeben true, aber von/datum noch Platzhalter -> unvollstaendig -> FAIL
        text = ("security:\n  freigegeben: true\n  von: \"<Name>\"\n  datum: \"<YYYY-MM-DD>\"\n"
                "datenschutz:\n  freigegeben: true\n  von: \"DSB\"\n  datum: \"2026-06-11\"\n")
        with tempfile.TemporaryDirectory() as d:
            _freigabe(d, text)
            self.assertEqual(freigabe.run_j1(d).status, common.FAIL)
            self.assertIn("unvollstaendig", freigabe.run_j1(d).summary)

    def test_missing_section_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            _freigabe(d, "security:\n  freigegeben: true\n  von: \"X\"\n  datum: \"2026-06-11\"\n")
            self.assertEqual(freigabe.run_j2(d).status, common.SKIP)   # datenschutz-Abschnitt fehlt

    def test_truthy_variants(self):
        for word in ("ja", "JA", "erteilt", "x", "1"):
            with self.subTest(word=word):
                with tempfile.TemporaryDirectory() as d:
                    _freigabe(d, "security:\n  freigegeben: %s\n  von: \"A\"\n  datum: \"2026-06-11\"\n" % word)
                    self.assertEqual(freigabe.run_j1(d).status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
