"""Autonomer 01→04-Pipeline-Runner — Orchestrierung (deterministisch, Fake-Phasen)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PIPELINE = os.path.join(REPO_ROOT, "pipeline", "run_pipeline.sh")
BENCH = os.path.join(REPO_ROOT, "benchmark", "project")
REQ = ("DATA-FLOW.md,PROCESSING-REGISTER.md,LAWFUL-BASIS.md,DPIA-SCREENING.md,"
       "TOMs.md,PROCESSORS-SUBPROCESSORS.md,RETENTION-DELETION.md")


def _copy_bench(dst):
    shutil.copytree(BENCH, dst)
    return dst


def _run(project, konz, bauen, maxit=3):
    return subprocess.run(
        ["bash", PIPELINE, "--project", project,
         "--konzipieren-cmd", konz, "--bauen-cmd", bauen, "--max-iterations", str(maxit),
         "--privacy-dir", os.path.join(project, "artefakte"), "--privacy-required", REQ,
         "--audit-log", os.path.join(project, "evidence", "audit.log")],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=180)


class HappyPath(unittest.TestCase):
    def test_all_four_phases_pass(self):
        with tempfile.TemporaryDirectory() as d:
            proj = _copy_bench(os.path.join(d, "project"))
            # SPEC existiert schon (komplett) -> konzipieren=no-op; bauen meldet promise
            r = _run(proj, "true", 'echo "<promise>GRUEN</promise>"')
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("04", r.stdout)  # Phase 4 erreicht


class HaltOnBadSpec(unittest.TestCase):
    def test_phase1_halts_on_placeholder_spec(self):
        with tempfile.TemporaryDirectory() as d:
            proj = _copy_bench(os.path.join(d, "project"))
            # konzipieren erzeugt eine kaputte SPEC (Platzhalter, fehlende Felder) -> A-Gates FAIL
            konz = "printf '# SPEC\\n\\n## 1. Ziel\\n<offen>\\n' > '%s/SPEC.md'" % proj
            r = _run(proj, konz, 'echo "<promise>GRUEN</promise>"')
            self.assertEqual(r.returncode, 3, r.stdout)  # Halt in Phase 1
            self.assertIn("01", r.stdout)


class HaltOnRedGates(unittest.TestCase):
    def test_phase3_halts_on_red(self):
        with tempfile.TemporaryDirectory() as d:
            proj = _copy_bench(os.path.join(d, "project"))
            # E5-Platzhalter in ein Artefakt: Phase 2 (ralph, ohne --privacy-dir) bleibt grün,
            # erst der volle Lauf in Phase 3 (mit --privacy-dir) fängt E5 -> Halt.
            konz = "printf '\\n- offener Punkt: <noch zu ergaenzen>\\n' >> '%s/artefakte/DATA-FLOW.md'" % proj
            r = _run(proj, konz, 'echo "<promise>GRUEN</promise>"')
            self.assertEqual(r.returncode, 3, r.stdout)
            self.assertIn("03", r.stdout)  # Halt in Phase 3 (Prüfen)


if __name__ == "__main__":
    unittest.main(verbosity=2)
