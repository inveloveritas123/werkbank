"""B-Gates (B1 Lint, B2 Typecheck, B3 Build) + C2 Coverage. Tests.

B3 (py_compile) ist stdlib -> deterministisch testbar. B1/B2/C2 nutzen externe Tools, sonst SKIP.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, b_gates, c2_coverage  # noqa: E402

VALID = {PASS_OR_SKIP for PASS_OR_SKIP in (common.PASS, common.SKIP)}


def _w(d, name, content):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(content)


class B3Build(unittest.TestCase):
    def test_valid_python_compiles(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "good.py", "x = 1\ndef f():\n    return x\n")
            self.assertEqual(b_gates.run_b3(d).status, common.PASS)

    def test_syntax_error_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "bad.py", "def f(:\n  return\n")
            self.assertEqual(b_gates.run_b3(d).status, common.FAIL)


class B1B2Tolerant(unittest.TestCase):
    def test_b1_status_valid(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "ok.py", "x = 1\n")
            self.assertIn(b_gates.run_b1(d).status, VALID)   # PASS (ruff da) oder SKIP

    def test_b2_status_valid(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "ok.py", "x: int = 1\n")
            self.assertIn(b_gates.run_b2(d).status, VALID)


class C2Coverage(unittest.TestCase):
    def test_no_tests_or_no_tool_skips(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "readme.md", "x\n")
            self.assertEqual(c2_coverage.run(d).status, common.SKIP)


if __name__ == "__main__":
    unittest.main(verbosity=2)
