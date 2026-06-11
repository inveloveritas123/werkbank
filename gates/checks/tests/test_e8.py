"""Gate E8 — Datenminimierung (Art. 25), deterministischer Dokumentations-Check. Tests.

Prüft DOKUMENTATION der Minimierung + Art-9-Disziplin — NICHT die materielle Angemessenheit
(die bleibt DSB/LLM). In gates.yaml als warn geführt.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, e8_minimization  # noqa: E402


def _w(d, name, content):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(content)


class E8(unittest.TestCase):
    def test_skip_without_context(self):
        res = e8_minimization.run(".")
        self.assertEqual(res.status, common.SKIP)
        self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
        self.assertIn("kein Privacy-Kontext", res.summary)

    def test_documented_minimization_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "DATA-FLOW.md", "Datenarten: Name, E-Mail. Besondere Kategorien nach Art. 9: keine.\n"
                                  "Datenminimierung: nur das für den Zweck Erforderliche wird erhoben.\n")
            self.assertEqual(e8_minimization.run(d, privacy_dir=d).status, common.PASS)

    def test_missing_minimization_doc_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "DATA-FLOW.md", "Datenarten: Name, E-Mail, Telefon, Adresse, Geburtsdatum.\n")
            self.assertEqual(e8_minimization.run(d, privacy_dir=d).status, common.FAIL)

    def test_art9_without_dpia_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "DATA-FLOW.md", "Besondere Kategorien nach Art. 9: Gesundheitsdaten werden erhoben.\n"
                                  "Datenminimierung dokumentiert.\n")
            self.assertEqual(e8_minimization.run(d, privacy_dir=d).status, common.FAIL)

    def test_art9_with_dpia_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "DATA-FLOW.md", "Besondere Kategorien nach Art. 9: Gesundheitsdaten.\nDatenminimierung dokumentiert.\n")
            _w(d, "DPIA.md", "# DSFA\nSystematische Beschreibung, Risiken, Abhilfemaßnahmen.\n")
            self.assertEqual(e8_minimization.run(d, privacy_dir=d).status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
