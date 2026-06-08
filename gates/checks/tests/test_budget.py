"""Budget/Kill-Switch — Engine + CLI + Ralph-Loop-Integration."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ORCH = os.path.join(REPO_ROOT, "orchestrator")
sys.path.insert(0, ORCH)

import budget  # noqa: E402

BUDGET_PY = os.path.join(ORCH, "budget.py")
LOOP = os.path.join(REPO_ROOT, "ralph", "ralph-loop.sh")


class Engine(unittest.TestCase):
    def test_ok_below_cap(self):
        self.assertEqual(budget.check(10, 100, 200)[0], "ok")

    def test_warn_at_cap(self):
        self.assertEqual(budget.check(100, 100, 200)[0], "warn")

    def test_kill_at_killswitch(self):
        self.assertEqual(budget.check(200, 100, 200)[0], "kill")

    def test_zero_limits_never_trigger(self):
        self.assertEqual(budget.check(9999, 0, 0)[0], "ok")  # 0 = nicht gesetzt


class StateAndCli(unittest.TestCase):
    def test_add_spend_persists(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "budget.json")
            with open(p, "w") as f:
                json.dump({"spent_eur": 0, "period_cap_eur": 100, "kill_switch_eur": 200}, f)
            budget.add_spend(p, 30)
            budget.add_spend(p, 5)
            with open(p) as f:
                self.assertEqual(json.load(f)["spent_eur"], 35)

    def test_cli_check_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "budget.json")
            with open(p, "w") as f:
                json.dump({"spent_eur": 300, "period_cap_eur": 100, "kill_switch_eur": 200}, f)
            r = subprocess.run([sys.executable, BUDGET_PY, "check", p], stdout=subprocess.PIPE, text=True)
            self.assertEqual(r.returncode, 4)  # kill -> 4


class RalphIntegration(unittest.TestCase):
    def test_loop_halts_on_killswitch_despite_promise(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".werkbank"))
            with open(os.path.join(d, "CHANGELOG.md"), "w") as f:
                f.write("# CHANGELOG\n\n## 2026-06-09 — x\n- y\n")
            with open(os.path.join(d, ".werkbank", "budget.json"), "w") as f:
                json.dump({"spent_eur": 999, "period_cap_eur": 100, "kill_switch_eur": 500}, f)
            r = subprocess.run(
                ["bash", LOOP, "--target", d, "--build-cmd", 'echo "<promise>GRUEN</promise>"',
                 "--max-iterations", "5", "--report", os.path.join(d, "GATE-REPORT.md")],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
            self.assertEqual(r.returncode, 3, r.stdout)   # Kill-Switch -> HALT, nicht stop
            self.assertIn("Budget", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
