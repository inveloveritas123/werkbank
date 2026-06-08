"""GP02 — Kontaktformular mit Auskunft & Löschung (DSAR). Soll-Ist-Tests.

Deckt die 6 Soll-Ist-Checks aus SPEC.md ab:
1. Kontakt speichern OK   2. Export liefert eigenen Datensatz OK   3. Löschung entfernt Datensatz OK
4. fremder Zugriff blockiert   5. keine PII im Log   6. Retention-Job vorhanden
Plus: DSGVO-Artefakte (DATA-FLOW/RETENTION-DELETION/DSAR-RIGHTS) vollständig (E5).
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
APP_DIR = os.path.join(REPO_ROOT, "golden-projects", "02-kontaktformular-dsar", "app")
ARTE = os.path.join(REPO_ROOT, "golden-projects", "02-kontaktformular-dsar", "artefakte")
sys.path.insert(0, GATES_DIR)
sys.path.insert(0, APP_DIR)

from checks import common, e2_pii_scan, e5_artefakte  # noqa: E402
import contact_service as cs  # noqa: E402


class _Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def _svc(d, retention_days=180, now=None):
    clock = _Clock(now or datetime(2026, 6, 8, tzinfo=timezone.utc))
    return cs.ContactService(storage_dir=d, clock=clock, retention_days=retention_days)


class StoreAndAdmin(unittest.TestCase):
    def test_submit_then_admin_sees_it(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            r = s.submit("Max Muster", "max@example.com", "Bitte Angebot", tenant="krause")
            self.assertTrue(r.subject_id and r.access_token)
            rows = s.admin_list(tenant="krause")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["subject_id"], r.subject_id)


class DsarExport(unittest.TestCase):
    def test_export_own_record(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            r = s.submit("Max", "max@example.com", "Hallo", tenant="krause")
            data = s.export(r.subject_id, r.access_token)
            self.assertEqual(data["email"], "max@example.com")
            self.assertEqual(data["message"], "Hallo")


class DsarDelete(unittest.TestCase):
    def test_delete_removes_record(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            r = s.submit("Max", "max@example.com", "Hallo")
            self.assertTrue(s.delete(r.subject_id, r.access_token))
            with self.assertRaises(cs.AccessDenied):
                s.export(r.subject_id, r.access_token)   # weg
            self.assertEqual(len(s.admin_list()), 0)


class ForeignAccessBlocked(unittest.TestCase):
    def test_wrong_token_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            a = s.submit("A", "a@example.com", "x", tenant="t1")
            b = s.submit("B", "b@example.com", "y", tenant="t2")
            with self.assertRaises(cs.AccessDenied):
                s.export(a.subject_id, b.access_token)     # fremder Token
            with self.assertRaises(cs.AccessDenied):
                s.delete(a.subject_id, "ganz-falsch")
            # Mandantentrennung im Admin-View
            self.assertEqual({r["subject_id"] for r in s.admin_list(tenant="t1")}, {a.subject_id})


class NoPiiInLog(unittest.TestCase):
    def test_log_has_no_pii(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            r = s.submit("Erika Mustermann", "erika@example.com", "Telefon 0151 23456789", tenant="t1")
            s.export(r.subject_id, r.access_token)
            s.delete(r.subject_id, r.access_token)
            with open(s.log_path, encoding="utf-8") as fh:
                log_text = fh.read()
            self.assertNotIn("erika@example.com", log_text)
            self.assertNotIn("0151 23456789", log_text)
            self.assertNotIn("Erika", log_text)
            # und der E2-Gate-Check bestaetigt es deterministisch
            self.assertEqual(e2_pii_scan.run(d).status, common.PASS)


class RetentionJob(unittest.TestCase):
    def test_purge_expired(self):
        with tempfile.TemporaryDirectory() as d:
            past = datetime(2026, 1, 1, tzinfo=timezone.utc)
            s = _svc(d, retention_days=30, now=past)
            old = s.submit("Alt", "alt@example.com", "x")
            # 200 Tage später
            s.clock.t = past + timedelta(days=200)
            fresh = s.submit("Neu", "neu@example.com", "y")
            purged = s.purge_expired()
            self.assertEqual(purged, 1)
            self.assertEqual({r["subject_id"] for r in s.admin_list()}, {fresh.subject_id})
            self.assertNotIn(old.subject_id, {r["subject_id"] for r in s.admin_list()})


class AccessControlHardening(unittest.TestCase):
    """Review-Befunde: Autorisierung muss fail-closed sein, nie mit KeyError/None brechen."""

    def test_none_and_empty_token_denied(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            r = s.submit("A", "a@example.com", "x")
            for bad in (None, "", "x"):
                with self.assertRaises(cs.AccessDenied):
                    s.export(r.subject_id, bad)

    def test_record_without_token_hash_denied_not_keyerror(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            # korrupter/handgepflegter Datensatz ohne token_hash
            s._records.append({"subject_id": "manual1", "tenant": "t", "name": "N",
                               "email": "n@example.com", "message": "m",
                               "created_at": s.clock().isoformat()})
            with self.assertRaises(cs.AccessDenied):
                s.export("manual1", "irgendwas")


class RetentionRobustness(unittest.TestCase):
    def test_purge_with_naive_now_does_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            past = datetime(2026, 1, 1, tzinfo=timezone.utc)
            s = _svc(d, retention_days=30, now=past)
            s.submit("Alt", "alt@example.com", "x")
            # Aufrufer übergibt eine naive Zeit -> darf nicht mit TypeError abbrechen
            purged = s.purge_expired(now=datetime(2026, 12, 1))
            self.assertEqual(purged, 1)


class StatePersists(unittest.TestCase):
    """Resume/State: ein neuer Service auf demselben Verzeichnis lädt die Daten (Neustart)."""
    def test_record_survives_restart(self):
        with tempfile.TemporaryDirectory() as d:
            r = _svc(d).submit("A", "a@example.com", "x", tenant="t1")
            again = _svc(d)  # frischer Service, gleicher Speicher
            self.assertEqual({x["subject_id"] for x in again.admin_list()}, {r.subject_id})
            self.assertEqual(again.export(r.subject_id, r.access_token)["email"], "a@example.com")


class ArtefactsComplete(unittest.TestCase):
    REQUIRED = ["DATA-FLOW.md", "RETENTION-DELETION.md", "DSAR-RIGHTS.md"]

    def test_e5_on_gp02_artefacts(self):
        res = e5_artefakte.run(ARTE, privacy_dir=ARTE, required=self.REQUIRED)
        self.assertEqual(res.status, common.PASS, res.summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
