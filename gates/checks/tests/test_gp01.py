"""GP01 — Golden Project 01 (DSGVO-Projektstarter): Soll-Ist-Tests.

Zwei Teile:
1. Die committeten Artefakte bestehen E1/E2/D3/E5 (kein Platzhalter, EU).
2. SECURITY_SEEDS: die 3 bewusst gesetzten Verstöße werden gefangen (Catch-Rate 3/3).
   Seeds werden zur LAUFZEIT in Tempdirs erzeugt — nie committet (Repo secret-/PII-frei).
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, d3_secret_scan, e1_eu_routing, e2_pii_scan, e5_artefakte  # noqa: E402

ARTE = os.path.join(REPO_ROOT, "golden-projects", "01-dsgvo-projektstarter", "artefakte")


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class ArtefactsPassEGates(unittest.TestCase):
    def test_e5_complete(self):
        res = e5_artefakte.run(ARTE, privacy_dir=ARTE)
        self.assertEqual(res.status, common.PASS, res.summary)

    def test_e1_e2_d3_green(self):
        self.assertEqual(e1_eu_routing.run(ARTE).status, common.PASS)
        self.assertEqual(e2_pii_scan.run(ARTE).status, common.PASS)
        self.assertEqual(d3_secret_scan.run(ARTE).status, common.PASS)


class SecuritySeedsCaught(unittest.TestCase):
    """SECURITY_SEEDS.md: 3 gepflanzte Verstöße, Catch-Rate-Ziel 3/3."""

    def _seed_dir(self, d):
        # Seed 1: Klartext-E-Mail in einem Log-Statement -> E2
        _write(d, "logs/app.log", "INFO booking user=max.mustermann@example.com confirmed\n")
        # Seed 2: hartcodierter Dummy-Token im Config-Snippet -> D3 (zur Laufzeit zusammengesetzt)
        token = "tok_" + "a1b2c3d4e5f6g7h8j9"
        _write(d, "config.yaml", 'api_token: "%s"\n' % token)
        # Seed 3: LLM-Call-Stub mit US-Endpunkt -> E1 (gesplittet im Repo)
        ep = "https://bedrock." + "us-" + "east-1" + ".amazonaws.com"
        _write(d, "llm_stub.py", 'ENDPOINT = "%s"\n' % ep)

    def test_catch_rate_3_of_3(self):
        with tempfile.TemporaryDirectory() as d:
            self._seed_dir(d)
            caught = {
                "E2": e2_pii_scan.run(d).status == common.FAIL,
                "D3": d3_secret_scan.run(d).status == common.FAIL,
                "E1": e1_eu_routing.run(d).status == common.FAIL,
            }
            self.assertEqual(sum(caught.values()), 3, "Catch-Rate < 3/3: %r" % caught)


class E5Hardening(unittest.TestCase):
    """ACT-1: E5 muss Klartext-Platzhalter + Prosa-Non-EU fangen, ohne Mails/Pfeile falsch zu flaggen."""

    def _valid_set(self, d):
        import shutil
        for name in e5_artefakte.REQUIRED_DEFAULT:
            shutil.copy(os.path.join(ARTE, name), os.path.join(d, name))

    def test_underscore_placeholder_caught(self):
        with tempfile.TemporaryDirectory() as d:
            self._valid_set(d)
            with open(os.path.join(d, "TOMs.md"), "a", encoding="utf-8") as f:
                f.write("\nAufbewahrung: ____ Monate\n")
            self.assertEqual(e5_artefakte.run(d, privacy_dir=d).status, common.FAIL)

    def test_german_fill_token_caught(self):
        with tempfile.TemporaryDirectory() as d:
            self._valid_set(d)
            with open(os.path.join(d, "LAWFUL-BASIS.md"), "a", encoding="utf-8") as f:
                f.write("\nVerantwortlicher: [bitte ausfuellen]\n")
            self.assertEqual(e5_artefakte.run(d, privacy_dir=d).status, common.FAIL)

    def test_prose_usa_region_caught(self):
        with tempfile.TemporaryDirectory() as d:
            self._valid_set(d)
            with open(os.path.join(d, "PROCESSORS-SUBPROCESSORS.md"), "a", encoding="utf-8") as f:
                f.write("\nStandort: USA (United States)\n")
            self.assertEqual(e5_artefakte.run(d, privacy_dir=d).status, common.FAIL)

    def test_drittland_ja_caught(self):
        with tempfile.TemporaryDirectory() as d:
            self._valid_set(d)
            with open(os.path.join(d, "DATA-FLOW.md"), "a", encoding="utf-8") as f:
                f.write("\nDrittland: ja, mit SCC\n")
            self.assertEqual(e5_artefakte.run(d, privacy_dir=d).status, common.FAIL)

    def test_email_autolink_no_false_positive(self):
        # Mail in spitzen Klammern / Pfeil duerfen NICHT als Platzhalter gelten.
        hits = e5_artefakte._placeholders_in("Kontakt: <datenschutz@firma.de>\nFluss A <-> B\n")
        self.assertEqual(hits, [])

    def test_valid_set_still_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._valid_set(d)
            self.assertEqual(e5_artefakte.run(d, privacy_dir=d).status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
