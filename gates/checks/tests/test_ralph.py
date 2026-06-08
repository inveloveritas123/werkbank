"""Ralph-Loop — Tests: Entscheidungs-Engine, Bash-Motor (end-to-end), Stop-Hook."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RALPH = os.path.join(REPO_ROOT, "ralph")
sys.path.insert(0, RALPH)

from ralph_decide import decide  # noqa: E402

LOOP = os.path.join(RALPH, "ralph-loop.sh")
HOOK = os.path.join(RALPH, "stop_hook.py")


def _clean_target(d):
    # Gate-sauberes Mini-Projekt: CHANGELOG (H4), keine Secrets/PII, keine Tests (C1 SKIP).
    with open(os.path.join(d, "CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write("# CHANGELOG\n\n## 2026-06-08 — init\n- x\n")


class Engine(unittest.TestCase):
    def test_done_when_green_and_promise(self):
        self.assertEqual(decide(True, True, 1, 15, -1, 0)[0], "stop")

    def test_continue_when_no_promise(self):
        self.assertEqual(decide(True, False, 1, 15, -1, 0)[0], "continue")

    def test_continue_when_gates_red(self):
        self.assertEqual(decide(False, True, 1, 15, -1, 0)[0], "continue")

    def test_halt_on_max_iter(self):
        self.assertEqual(decide(False, False, 15, 15, -1, 5)[0], "halt")

    def test_drift_halts_even_if_would_continue(self):
        # rote Gates gestiegen (1 -> 3) -> Drift-Pausegate vor allem anderen
        self.assertEqual(decide(False, True, 2, 15, 1, 3)[0], "halt")


class BashMotor(unittest.TestCase):
    def _run(self, target, build_cmd, maxit):
        return subprocess.run(
            ["bash", LOOP, "--target", target, "--build-cmd", build_cmd,
             "--max-iterations", str(maxit), "--report", os.path.join(target, "GATE-REPORT.md")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)

    def test_stops_on_green_plus_promise(self):
        with tempfile.TemporaryDirectory() as d:
            _clean_target(d)
            r = self._run(d, 'echo "<promise>GRUEN</promise>"', 5)
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_halts_on_max_iter_without_promise(self):
        with tempfile.TemporaryDirectory() as d:
            _clean_target(d)
            r = self._run(d, 'echo "noch nicht fertig"', 3)
            self.assertEqual(r.returncode, 3, r.stdout)

    def test_halts_when_gates_red_despite_promise(self):
        with tempfile.TemporaryDirectory() as d:
            _clean_target(d)
            tok = "tok_" + "a1b2c3d4e5f6g7h8j9"   # zur Laufzeit, nie committet
            with open(os.path.join(d, "config.yaml"), "w", encoding="utf-8") as f:
                f.write('api_token: "%s"\n' % tok)   # D3 -> rot
            r = self._run(d, 'echo "<promise>GRUEN</promise>"', 2)
            self.assertEqual(r.returncode, 3, r.stdout)


class StopHook(unittest.TestCase):
    def _hook(self, payload):
        return subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)

    def test_allows_stop_when_green_and_promise(self):
        with tempfile.TemporaryDirectory() as d:
            _clean_target(d)
            r = self._hook({"cwd": d, "assistant_message": "fertig <promise>GRUEN</promise>"})
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), "")   # kein block -> Stop erlaubt

    def test_blocks_when_promise_missing(self):
        with tempfile.TemporaryDirectory() as d:
            _clean_target(d)
            r = self._hook({"cwd": d, "assistant_message": "bin noch dran"})
            self.assertIn('"decision": "block"', r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
