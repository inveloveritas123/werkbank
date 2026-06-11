"""GP04 — Upload mit PII-Erkennung & Redaction. Soll-Ist-Tests.

SPEC: PII erkannt · PII im Report maskiert · keine PII im Log · keine PII im Prompt-Dump ·
Datei-Löschung OK.  PII-Testdaten werden zur LAUFZEIT erzeugt (nichts committet).
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
APP_DIR = os.path.join(REPO_ROOT, "golden-projects", "04-upload-pii-redaction", "app")
ARTE = os.path.join(REPO_ROOT, "golden-projects", "04-upload-pii-redaction", "artefakte")
sys.path.insert(0, GATES_DIR)
sys.path.insert(0, APP_DIR)

import pii_redactor as red  # noqa: E402
import upload_service as up  # noqa: E402

from checks import common, e2_pii_scan, e5_artefakte  # noqa: E402


class _Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def _svc(d):
    return up.UploadService(storage_dir=d, clock=_Clock(datetime(2026, 6, 8, tzinfo=timezone.utc)))


# Reale Klartext-PII nur zur Laufzeit (zusammengesetzt, damit der Repo-Self-Scan nichts findet).
def _pii_text():
    email = "max.mustermann" + "@example.com"
    phone = "0151 " + "23456789"
    iban = "DE89" + "370400440532013000"
    return ("Sehr geehrte Damen und Herren,\n"
            "ich bin Herr Max Mustermann. Kontakt: %s, Telefon %s.\n"
            "Meine IBAN lautet %s.\n" % (email, phone, iban)), email, phone, iban


class Detection(unittest.TestCase):
    def test_pii_types_detected(self):
        text, _, _, _ = _pii_text()
        _, findings = red.redact(text)
        kinds = {f.kind for f in findings}
        for expected in ("email", "iban"):
            self.assertIn(expected, kinds)
        self.assertTrue(any(k.startswith("phone") for k in kinds))
        self.assertTrue(any(k == "name" for k in kinds))


class ReportMasked(unittest.TestCase):
    def test_report_has_no_cleartext_pii(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            text, email, phone, iban = _pii_text()
            r = s.upload("brief.txt", text)
            self.assertGreaterEqual(r.finding_count, 4)
            report = s.get_report(r.upload_id)
            for raw in (email, phone, iban, "Max Mustermann"):
                self.assertNotIn(raw, report)
            self.assertIn("[EMAIL]", s.get_prompt_dump(r.upload_id))


class NoPiiInLogOrPrompt(unittest.TestCase):
    def test_log_and_prompt_pii_free(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            text, email, phone, iban = _pii_text()
            s.upload("brief.txt", text)
            with open(s.log_path, encoding="utf-8") as f:
                log = f.read()
            for raw in (email, phone, iban):
                self.assertNotIn(raw, log)
            # E2-Gate ueber Log+Prompt-Verzeichnisse: keine Klartext-PII
            self.assertEqual(e2_pii_scan.run(d).status, common.PASS)


class DeleteFile(unittest.TestCase):
    def test_delete_removes_all_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            text, _, _, _ = _pii_text()
            r = s.upload("brief.txt", text)
            self.assertTrue(s.delete(r.upload_id))
            self.assertFalse(s.exists(r.upload_id))
            with self.assertRaises(up.NotFound):
                s.get_report(r.upload_id)


class RedactorPrecision(unittest.TestCase):
    def test_no_false_positive_on_clean_text(self):
        clean = "Bestellung 12345 wurde am Montag versandt. Status 200. Vielen Dank."
        _, findings = red.redact(clean)
        self.assertEqual(findings, [])


class ArtefactsComplete(unittest.TestCase):
    def test_data_flow_complete(self):
        res = e5_artefakte.run(ARTE, privacy_dir=ARTE, required=["DATA-FLOW.md"])
        self.assertEqual(res.status, common.PASS, res.summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
