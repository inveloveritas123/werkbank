"""Haerte-Test — BEWEIST, dass die Gates wirklich ROT werden.

Antwort auf den staerksten Einwand ("GRUEN, weil nichts scharf geprueft wird"): ein
absichtlich kaputtes Projekt mit SQLi, Hardcoded Secret, Klartext-PII im Log, Non-EU-
Routing und fehlenden DSGVO-Artefakten (TOMs/Loeschfrist). Jeder Gate-Fund wird EINZELN
assertiert — und ein voller Runner-Lauf liefert ROT.

Verification-first: Die Verstoesse werden zur LAUFZEIT in einem Tempdir synthetisiert
(gesplittete Literale) und NIE committet — das Repo bleibt secret-/PII-frei, der eigene
werkbank_self-Gate-Lauf bleibt gruen. Die committete Doku liegt in
golden-projects/haerte-test/README.md.
"""
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "gates"))

import runner  # noqa: E402
from checks import (  # noqa: E402
    common,
    d1_sast,
    d3_secret_scan,
    e1_eu_routing,
    e2_pii_scan,
    e5_artefakte,
)

REQUIRED_ARTEFACTS = ["DATA-FLOW.md", "PROCESSING-REGISTER.md", "TOMs.md", "RETENTION-DELETION.md"]
PFLICHT = os.path.join(HERE, "fixtures", "pflichtenheft.test.yaml")


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


def _build_broken_project(d):
    """Pflanzt fuenf reale Verstoesse (Literale gesplittet -> nie zusammenhaengend im Repo)."""
    # 1) Non-EU-Routing (E1) + 2) SQL-Injection per String-Konkatenation (D1/bandit B608)
    endpoint = "https://api.openai." + "com/v1/chat"
    _write(d, "app/service.py",
           "import sqlite3\n"
           'LLM_ENDPOINT = "%s"\n'
           "def lookup(db, uid):\n"
           "    cur = sqlite3.connect(db).cursor()\n"
           '    q = "SELECT * FROM users WHERE id = \'" + uid + "\'"\n'
           "    return cur.execute(q).fetchall()\n" % endpoint)
    # 3) Hardcoded Secret (D3)
    akia = "AKIA" + "QURTZ7XMPLE4KLMN"
    _write(d, "app/creds.env", "AWS_ACCESS_KEY_ID=%s\n" % akia)
    # 4) Klartext-PII im Log (E2)
    _write(d, "logs/app.log",
           "2026 INFO login user=max.mustermann@example.com phone=+49 151 23456789\n")
    # 5) Fehlende DSGVO-Artefakte (E5): nur DATA-FLOW vorhanden, TOMs/Loeschfrist fehlen
    arte = os.path.join(d, "artefakte")
    _write(d, "artefakte/DATA-FLOW.md", "# Datenfluss\n- A -> B\n")
    return d, arte


class GatesCatchPlantedViolations(unittest.TestCase):
    """Jeder deterministische stdlib-Gate faengt seinen gepflanzten Verstoss."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj, self.arte = _build_broken_project(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_e1_catches_non_eu_endpoint(self):
        res = e1_eu_routing.run(self.proj)
        self.assertEqual(res.status, common.FAIL)
        self.assertTrue(res.findings)

    def test_e2_catches_pii_in_log(self):
        res = e2_pii_scan.run(self.proj)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("pii:email", [f.kind for f in res.findings])

    def test_d3_catches_hardcoded_secret(self):
        res = d3_secret_scan.run(self.proj)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("aws-access-key-id", [f.kind for f in res.findings])

    def test_e5_catches_missing_dsgvo_artefacts(self):
        res = e5_artefakte.run(self.proj, privacy_dir=self.arte, required=REQUIRED_ARTEFACTS)
        self.assertEqual(res.status, common.FAIL)
        # TOMs + Loeschfrist (RETENTION-DELETION) muessen als fehlend gemeldet sein
        blob = " ".join("%s %s" % (f.file, f.evidence) for f in res.findings) + res.summary
        self.assertIn("TOMs", blob)
        self.assertIn("RETENTION-DELETION", blob)

    @unittest.skipUnless(shutil.which("bandit"), "bandit nicht installiert")
    def test_d1_catches_sql_injection(self):
        res = d1_sast.run(self.proj)
        self.assertEqual(res.status, common.FAIL)
        self.assertTrue(any("sast" in f.kind for f in res.findings))


class FullRunnerIsRed(unittest.TestCase):
    """Ein vollstaendiger Runner-Lauf auf dem kaputten Projekt liefert ROT (kein falsches Gruen)."""

    def test_overall_red_with_full_context(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as out:
            proj, arte = _build_broken_project(d)
            report = os.path.join(out, "GATE-REPORT.md")
            res = runner.run_gates(
                gates_path=os.path.join(REPO_ROOT, "gates", "gates.yaml"),
                target=proj, report_path=report,
                profile="pii_stdlib", pflichtenheft_path=PFLICHT,
                privacy_dir=arte, privacy_required=REQUIRED_ARTEFACTS,
            )
            self.assertEqual(res["overall"], "ROT")
            # mindestens ein Pflicht-Gate ist verletzt oder ungedeckt
            vd = res["verdict"]
            self.assertGreater(len(vd["violated"]) + len(vd["uncovered"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
