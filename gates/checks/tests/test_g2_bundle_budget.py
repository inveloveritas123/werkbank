"""Gate G2 — Bundle-/Ressourcen-Budget (deterministisch). Tests.

Reale Tempdirs: kleiner dist/ -> PASS; dist/ über Budget (via G2_MAX_KB-Env klein gesetzt
oder reale große Datei) -> WARN; kein Build-Output -> SKIP/NOT_APPLICABLE.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, g2_bundle_budget  # noqa: E402


def _write_bytes(d, rel, nbytes):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(b"x" * nbytes)
    return p


class NoBuildDirSkips(unittest.TestCase):
    def test_no_build_dir_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "src"))
            res = g2_bundle_budget.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


class WithinBudgetPasses(unittest.TestCase):
    def test_small_dist_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "dist/app.js", 2048)
            res = g2_bundle_budget.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)


class OverBudgetWarns(unittest.TestCase):
    def setUp(self):
        self._orig = os.environ.get("G2_MAX_KB")

    def tearDown(self):
        if self._orig is None:
            os.environ.pop("G2_MAX_KB", None)
        else:
            os.environ["G2_MAX_KB"] = self._orig

    def test_over_budget_via_env_warns_with_finding(self):
        os.environ["G2_MAX_KB"] = "1"
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "dist/bundle.js", 4096)  # 4 KB > 1 KB
            res = g2_bundle_budget.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(len(res.findings), 1)
            self.assertEqual(res.findings[0].kind, "bundle-budget")
            self.assertIn("KB", res.findings[0].evidence)

    def test_over_budget_via_many_bytes_warns(self):
        os.environ.pop("G2_MAX_KB", None)  # Default 5000 KB
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "build/huge.bin", (5000 + 10) * 1024)
            res = g2_bundle_budget.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(len(res.findings), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
