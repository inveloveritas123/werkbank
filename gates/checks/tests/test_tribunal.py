"""I2 — QA-Tribunal: anonymisierte Reconciliation (deterministisch) + Fan-out-Harness."""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TRIB = os.path.join(REPO_ROOT, "tribunal")
sys.path.insert(0, TRIB)

from reconcile import reconcile  # noqa: E402

SH = os.path.join(TRIB, "tribunal.sh")


class Reconcile(unittest.TestCase):
    def test_clear_pass(self):
        self.assertEqual(reconcile([{"verdict": "pass"}] * 3)["decision"], "pass")

    def test_majority_fail_blocks(self):
        self.assertEqual(reconcile([{"verdict": "fail"}, {"verdict": "fail"}, {"verdict": "pass"}])["decision"], "block")

    def test_minority_fail_passes(self):
        self.assertEqual(reconcile([{"verdict": "fail"}, {"verdict": "pass"}, {"verdict": "pass"}])["decision"], "pass")

    def test_tie_is_conservative_block(self):
        self.assertEqual(reconcile([{"verdict": "fail"}, {"verdict": "pass"}])["decision"], "block")

    def test_uncertain_counts_as_not_pass(self):
        self.assertEqual(reconcile([{"verdict": "uncertain"}, {"verdict": "uncertain"}, {"verdict": "pass"}])["decision"], "block")

    def test_empty_blocks(self):
        self.assertEqual(reconcile([])["decision"], "block")


class Harness(unittest.TestCase):
    def _run(self, *reviewer_cmds):
        args = ["bash", SH]
        for c in reviewer_cmds:
            args += ["--reviewer", c]
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)

    def test_harness_passes_on_majority_pass(self):
        r = self._run('echo "VERDICT: pass"', 'echo "VERDICT: pass"', 'echo "VERDICT: fail"')
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_harness_blocks_on_majority_fail(self):
        r = self._run('echo "VERDICT: fail"', 'echo "VERDICT: fail"', 'echo "VERDICT: pass"')
        self.assertEqual(r.returncode, 3, r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
