"""Test: .werkbank/framework-dirs schliesst kopiertes WERKBANK-Framework vom Scan aus.

Verhindert Falsch-Positive/Rauschen, wenn werkbank-init das Framework ins Projekt kopiert
(Projekt bleibt standalone, Audit bleibt sauber).
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
sys.path.insert(0, GATES_DIR)

import runner  # noqa: E402
from checks import common  # noqa: E402

GATES_YAML = os.path.join(REPO_ROOT, "gates", "gates.yaml")


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


def _marker(d, *names):
    os.makedirs(os.path.join(d, ".werkbank"), exist_ok=True)
    with open(os.path.join(d, ".werkbank", "framework-dirs"), "w", encoding="utf-8") as f:
        f.write("\n".join(names) + "\n")


class FrameworkExclude(unittest.TestCase):
    def test_reader_parses_marker(self):
        with tempfile.TemporaryDirectory() as d:
            _marker(d, "gates", "deploy", "# kommentar")
            got = runner._framework_exclude(d)
            self.assertIn("gates", got)
            self.assertIn("deploy", got)
            self.assertNotIn("# kommentar", got)   # Kommentarzeilen ignoriert

    def test_no_marker_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(runner._framework_exclude(d), set())

    def _run_d3(self, d):
        with tempfile.TemporaryDirectory() as out:
            res = runner.run_gates(GATES_YAML, d, os.path.join(out, "r.md"), profile="static_min")
            return res["results"]["D3"]["status"]

    def test_secret_in_framework_dir_is_excluded(self):
        # Gepflanztes Secret in einem "Framework"-Verzeichnis -> mit Marker NICHT geflaggt.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "app.py", "x = 1\n")
            _write(d, "deploy/cfg.py", 'KEY = "AKIA' + 'QURTZ7XMPLE4KLMN"\n')
            self.assertEqual(self._run_d3(d), common.FAIL)     # ohne Marker: rot
            _marker(d, "deploy")
            self.assertEqual(self._run_d3(d), common.PASS)     # mit Marker: deploy/ uebersprungen

    def test_app_code_still_scanned_with_marker(self):
        # Der Marker darf NICHT den App-Code ausblenden — nur die gelisteten Framework-Dirs.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "app.py", 'KEY = "AKIA' + 'QURTZ7XMPLE4KLMN"\n')   # Secret im App-Code
            _marker(d, "deploy")
            self.assertEqual(self._run_d3(d), common.FAIL)     # App-Secret bleibt rot


if __name__ == "__main__":
    unittest.main(verbosity=2)
