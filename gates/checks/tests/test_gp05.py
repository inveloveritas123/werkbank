"""GP05 — Breach-/Incident-Runbook. Soll-Ist-Tests.

SPEC: 72h-Prüfung enthalten · betroffene Datenarten genannt · Meldeentscheidung begründet ·
Maßnahmenliste vorhanden · KEINE Fake-Rechtsaussagen.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
APP_DIR = os.path.join(REPO_ROOT, "golden-projects", "05-breach-incident-runbook", "app")
ARTE = os.path.join(REPO_ROOT, "golden-projects", "05-breach-incident-runbook", "artefakte")
sys.path.insert(0, GATES_DIR)
sys.path.insert(0, APP_DIR)

from checks import common, e5_artefakte  # noqa: E402
import breach_runbook as br  # noqa: E402
import legal_claims as lc  # noqa: E402

INCIDENT = {
    "type": "Unbefugter Zugriff auf die Kundendatenbank",
    "systems": ["Kundendatenbank", "Web-App"],
    "data_types": ["Name", "E-Mail", "Telefon", "Auftragsdaten"],
    "detected_at": "2026-06-08T08:00:00+00:00",
    "occurred_at": "2026-06-07T22:00:00+00:00",
    "detection": "Auffaellige Login-Muster im Monitoring",
    "scope": "ca. 1.200 Kundendatensaetze potenziell betroffen",
    "special_categories": False,
}

REQUIRED = ["BREACH-RUNBOOK.md", "INCIDENT-TIMELINE.md",
            "NOTIFICATION-CHECKLIST.md", "LESSONS-LEARNED.md"]


class Generation(unittest.TestCase):
    def setUp(self):
        self.docs = br.generate(INCIDENT)

    def test_all_docs_generated(self):
        self.assertEqual(set(self.docs), set(REQUIRED))

    def test_72h_check_present(self):
        nc = self.docs["NOTIFICATION-CHECKLIST.md"]
        self.assertIn("72", nc)
        # Frist = Erkennung + 72h = 2026-06-11T08:00
        self.assertIn("2026-06-11T08:00", nc)

    def test_data_types_named(self):
        rb = self.docs["BREACH-RUNBOOK.md"]
        for dt in INCIDENT["data_types"]:
            self.assertIn(dt, rb)

    def test_decision_reasoned_not_absolute(self):
        nc = self.docs["NOTIFICATION-CHECKLIST.md"]
        self.assertIn("Art. 33", nc)
        # Begründung mit bedingter Sprache, keine Scheinsicherheit
        self.assertTrue(any(w in nc for w in ("voraussichtlich", "Einschätzung", "Risiko")))

    def test_measures_list(self):
        rb = self.docs["BREACH-RUNBOOK.md"]
        for step in ("Eindämmung", "Bewertung", "Meldung", "Dokumentation"):
            self.assertIn(step, rb)


class NoFakeLegalClaims(unittest.TestCase):
    def test_generated_docs_pass_linter(self):
        docs = br.generate(INCIDENT)
        findings = lc.lint_texts(docs)
        self.assertEqual(findings, [], "Fake-Rechtsaussage(n): %r" % findings)

    def test_linter_catches_fake_claim(self):
        bad = {"X.md": "Dieser Vorfall ist garantiert rechtssicher, eine Meldung ist "
                        "definitiv nicht erforderlich. Kein Rechtsrat."}
        self.assertTrue(lc.lint_texts(bad))

    def test_linter_requires_disclaimer(self):
        nodisc = {"BREACH-RUNBOOK.md": "Vorfall dokumentiert. Maßnahmen ergriffen."}
        self.assertTrue(lc.lint_texts(nodisc))


class BaldClaimHardening(unittest.TestCase):
    """Review-Befund: kahle unhedged Meldeaussagen müssen gefangen werden; gehedgte nicht."""

    def test_bald_not_required_caught(self):
        for bad in ("Eine Meldung ist nicht erforderlich. Kein Rechtsrat.",
                    "Der Vorfall ist nicht meldepflichtig. Kein Rechtsrat.",
                    "Sie sind auf der sicheren Seite. Kein Rechtsrat."):
            self.assertTrue(lc.lint_texts({"x.md": bad}), "nicht gefangen: %r" % bad)

    def test_hedged_not_required_ok(self):
        good = {"x.md": "Nach aktueller Einschätzung voraussichtlich nicht erforderlich "
                        "(Art. 34); Entscheidung durch DSB dokumentieren. Kein Rechtsrat."}
        self.assertEqual(lc.lint_texts(good), [])

    def test_low_risk_incident_no_overclaim(self):
        # high_risk=False-Zweig: erzeugt "nicht erforderlich" -> muss gehedgt + linter-sauber sein
        low = dict(INCIDENT, type="Verlorenes verschluesseltes Notebook",
                   special_categories=False)
        docs = br.generate(low)
        nc = docs["NOTIFICATION-CHECKLIST.md"]
        self.assertIn("nicht erforderlich", nc)            # der riskante Zweig wird wirklich erzeugt
        self.assertEqual(lc.lint_texts(docs), [])          # aber ohne Scheinsicherheit


class ArtefactsComplete(unittest.TestCase):
    def test_e5_on_generated_artefacts(self):
        res = e5_artefakte.run(ARTE, privacy_dir=ARTE, required=REQUIRED)
        self.assertEqual(res.status, common.PASS, res.summary)

    def test_artefacts_pass_legal_linter(self):
        texts = {}
        for name in REQUIRED:
            with open(os.path.join(ARTE, name), encoding="utf-8") as f:
                texts[name] = f.read()
        self.assertEqual(lc.lint_texts(texts), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
