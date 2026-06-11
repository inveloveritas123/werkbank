"""Gate C3 — Integrationstests (deterministisch). Tests.

Pure Python + unittest: SKIP-NOT_APPLICABLE bei leerem Projekt, und echte
PASS-/FAIL-Läufe mit winzigen Integrationstests in einem Tempdir (kein externes Tool nötig).
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import c3_integration, common  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p) or d, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


_PASS_TEST = (
    "import unittest\n"
    "class T(unittest.TestCase):\n"
    "    def test_ok(self):\n"
    "        self.assertEqual(1 + 1, 2)\n"
)
_FAIL_TEST = (
    "import unittest\n"
    "class T(unittest.TestCase):\n"
    "    def test_bad(self):\n"
    "        self.assertEqual(1 + 1, 3)\n"
)


class NoIntegrationSkips(unittest.TestCase):
    def test_empty_project_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "nix\n")
            res = c3_integration.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertIn("Integrationstests", res.summary)


class IntegrationDirRuns(unittest.TestCase):
    def test_passing_integration_dir_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "tests/integration/test_ok.py", _PASS_TEST)
            res = c3_integration.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertIn("1", res.summary)

    def test_failing_integration_dir_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "tests/integration/test_bad.py", _FAIL_TEST)
            res = c3_integration.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)


class IntegrationFilePatternRuns(unittest.TestCase):
    def test_named_integration_file_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "test_login_integration.py", _PASS_TEST)
            res = c3_integration.run(d)
            self.assertEqual(res.status, common.PASS)

    def test_suffix_integration_file_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "login_integration_test.py", _FAIL_TEST)
            res = c3_integration.run(d)
            self.assertEqual(res.status, common.FAIL)


class EmptyIntegrationDirSkips(unittest.TestCase):
    def test_dir_without_collected_tests_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "tests", "integration"))
            res = c3_integration.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
