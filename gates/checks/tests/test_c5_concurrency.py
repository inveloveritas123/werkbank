"""Gate C5 — Concurrency-/Race-Tests (deterministisch). Tests.

Pure Python + unittest: SKIP-NOT_APPLICABLE bei leerem Projekt, plus echte PASS-/FAIL-Läufe
mit winzigen Concurrency-Tests in einem Tempdir (kein externes Tool nötig).
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import c5_concurrency, common  # noqa: E402


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
    "        self.assertTrue(True)\n"
)
_FAIL_TEST = (
    "import unittest\n"
    "class T(unittest.TestCase):\n"
    "    def test_bad(self):\n"
    "        self.assertTrue(False)\n"
)


class NoConcurrencySkips(unittest.TestCase):
    def test_empty_project_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "test_plain.py", _PASS_TEST)
            res = c5_concurrency.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


class ConcurrencyRuns(unittest.TestCase):
    def test_passing_concurrency_test_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "test_worker_concurrency.py", _PASS_TEST)
            res = c5_concurrency.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertIn("1", res.summary)

    def test_failing_race_test_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "test_data_race.py", _FAIL_TEST)
            res = c5_concurrency.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)

    def test_suffix_concurrency_file_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "queue_concurrency_test.py", _PASS_TEST)
            res = c5_concurrency.run(d)
            self.assertEqual(res.status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
