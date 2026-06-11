"""T9 — drei bisher fehlende Gates echt machen: C1 (Tests), H4 (CHANGELOG), F1 (Modell-Pinning)."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import c1_tests, common, f1_model_pinning, h4_changelog  # noqa: E402


def _w(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class C1Tests(unittest.TestCase):
    def test_passing_suite_is_green(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "tests/test_ok.py",
               "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.assertEqual(1,1)\n")
            self.assertEqual(c1_tests.run(d).status, common.PASS)

    def test_failing_suite_is_red(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "tests/test_bad.py",
               "import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.assertEqual(1,2)\n")
            self.assertEqual(c1_tests.run(d).status, common.FAIL)

    def test_no_tests_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "readme.md", "nix\n")
            res = c1_tests.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertIn("kein Testverzeichnis", res.summary)


class H4Changelog(unittest.TestCase):
    def test_dated_changelog_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "CHANGELOG.md", "# CHANGELOG\n\n## 2026-06-08 — A\n- x\n\n## 2026-06-01 — B\n- y\n")
            self.assertEqual(h4_changelog.run(d).status, common.PASS)

    def test_missing_changelog_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "readme.md", "x\n")
            self.assertEqual(h4_changelog.run(d).status, common.FAIL)

    def test_not_newest_top_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "CHANGELOG.md", "# CHANGELOG\n\n## 2026-06-01 — alt\n\n## 2026-06-08 — neu\n")
            self.assertEqual(h4_changelog.run(d).status, common.FAIL)


class F1ModelPinning(unittest.TestCase):
    def test_latest_tag_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "cfg.yaml", "model: claude-3-5-sonnet-latest\n")
            self.assertEqual(f1_model_pinning.run(d).status, common.FAIL)

    def test_model_latest_kv_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "cfg.json", '{"model": "latest"}\n')
            self.assertEqual(f1_model_pinning.run(d).status, common.FAIL)

    def test_pinned_model_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "cfg.yaml", "model: opus\nmodel2: claude-opus-4-8\n")
            self.assertEqual(f1_model_pinning.run(d).status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
