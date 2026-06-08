"""I3 — Deployment-Validierung (Argus-Stil): alle kritischen User-Flows müssen bestehen."""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEPLOY = os.path.join(REPO_ROOT, "deploy")
sys.path.insert(0, DEPLOY)

from deploy_validate import validate  # noqa: E402

SH = os.path.join(DEPLOY, "deploy_validate.sh")


class Engine(unittest.TestCase):
    def test_all_pass_deploys(self):
        self.assertEqual(validate([{"flow": "buchen", "verdict": "pass"},
                                   {"flow": "stornieren", "verdict": "pass"}])["decision"], "deploy")

    def test_any_fail_blocks(self):
        self.assertEqual(validate([{"flow": "buchen", "verdict": "pass"},
                                   {"flow": "stornieren", "verdict": "fail"}])["decision"], "block")

    def test_uncertain_blocks(self):
        self.assertEqual(validate([{"flow": "buchen", "verdict": "uncertain"}])["decision"], "block")

    def test_empty_blocks(self):
        self.assertEqual(validate([])["decision"], "block")


class Harness(unittest.TestCase):
    def _run(self, *flows):
        args = ["bash", SH]
        for f in flows:
            args += ["--flow", f]
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)

    def test_deploys_when_all_flows_pass(self):
        r = self._run('buchen=echo "VERDICT: pass"', 'stornieren=echo "VERDICT: pass"')
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_blocks_when_a_flow_fails(self):
        r = self._run('buchen=echo "VERDICT: pass"', 'stornieren=echo "VERDICT: fail"')
        self.assertEqual(r.returncode, 3, r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
