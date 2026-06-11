"""Gate H3 — README vorhanden und ausgefuellt. Tests (hermetisch).

Deckt PASS (volle README), WARN (fehlt / zu kurz / Platzhalter) und
SKIP/NOT_APPLICABLE (Ziel ohne Dateien) ab.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from checks import common, h3_docs  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


_FULL = "\n".join("Zeile %d mit Inhalt." % i for i in range(1, 13)) + "\n"


class EmptyTargetSkips(unittest.TestCase):
    def test_no_files_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            res = h3_docs.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


class MissingOrThinWarns(unittest.TestCase):
    def test_no_readme_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "app.py", "x = 1\n")
            res = h3_docs.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(res.findings[0].kind, "docs-missing")

    def test_thin_readme_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "# Titel\n\nNur zwei Zeilen.\n")
            res = h3_docs.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(res.findings[0].kind, "docs-thin")

    def test_placeholder_readme_warns(self):
        with tempfile.TemporaryDirectory() as d:
            body = _FULL + "Install: <your-token-here>\n"
            _write(d, "README.md", body)
            res = h3_docs.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(res.findings[0].kind, "docs-placeholder")

    def test_todo_placeholder_warns(self):
        with tempfile.TemporaryDirectory() as d:
            body = _FULL + "Doku: TBD\n"
            _write(d, "README.md", body)
            res = h3_docs.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(res.findings[0].kind, "docs-placeholder")


class FullReadmePasses(unittest.TestCase):
    def test_full_readme_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", _FULL)
            res = h3_docs.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)

    def test_case_insensitive_rst_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "Readme.rst", _FULL)
            res = h3_docs.run(d)
            self.assertEqual(res.status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
