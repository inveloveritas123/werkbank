"""Gate H2 — zyklomatische Komplexitaet (stdlib ast). Tests (hermetisch).

Deckt PASS (alle unter Schwelle), WARN (Funktion ueber Schwelle, via env H2_MAX
gesteuert) und SKIP/NOT_APPLICABLE (kein .py) ab.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from checks import common, h2_complexity  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


_SIMPLE = "def f(a):\n    return a + 1\n"

# 4 if-Zweige + Basis 1 = Komplexitaet 5.
_BRANCHY = (
    "def g(a):\n"
    "    if a == 1:\n"
    "        return 1\n"
    "    if a == 2:\n"
    "        return 2\n"
    "    if a == 3:\n"
    "        return 3\n"
    "    if a == 4:\n"
    "        return 4\n"
    "    return 0\n"
)


class NoPythonSkips(unittest.TestCase):
    def test_no_python_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "no python here\n")
            res = h2_complexity.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


class BelowThresholdPasses(unittest.TestCase):
    def test_simple_function_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.py", _SIMPLE)
            res = h2_complexity.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)


class OverThresholdWarns(unittest.TestCase):
    def setUp(self):
        self._orig = os.environ.get("H2_MAX")
        # Schwelle bewusst niedrig -> _BRANCHY (Komplexitaet 5) loest WARN aus.
        os.environ["H2_MAX"] = "3"

    def tearDown(self):
        if self._orig is None:
            os.environ.pop("H2_MAX", None)
        else:
            os.environ["H2_MAX"] = self._orig

    def test_branchy_function_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "b.py", _BRANCHY)
            res = h2_complexity.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(len(res.findings), 1)
            self.assertEqual(res.findings[0].kind, "complexity")
            self.assertIn("g() = 5", res.findings[0].evidence)

    def test_default_threshold_does_not_warn(self):
        # Ohne env-Override (Default 12) ist Komplexitaet 5 unkritisch.
        os.environ.pop("H2_MAX", None)
        with tempfile.TemporaryDirectory() as d:
            _write(d, "b.py", _BRANCHY)
            res = h2_complexity.run(d)
            self.assertEqual(res.status, common.PASS)


class CountsConstructs(unittest.TestCase):
    def test_boolop_and_comprehension_if_count(self):
        with tempfile.TemporaryDirectory() as d:
            # 1 (base) + 2 (a and b and c => 2 extra operands) + 1 (comprehension if) = 4
            src = (
                "def h(a, b, c, xs):\n"
                "    ok = a and b and c\n"
                "    ys = [x for x in xs if x > 0]\n"
                "    return ok, ys\n"
            )
            _write(d, "c.py", src)
            os.environ["H2_MAX"] = "3"
            try:
                res = h2_complexity.run(d)
            finally:
                os.environ.pop("H2_MAX", None)
            self.assertEqual(res.status, common.WARN)
            self.assertIn("h() = 4", res.findings[0].evidence)


if __name__ == "__main__":
    unittest.main(verbosity=2)
