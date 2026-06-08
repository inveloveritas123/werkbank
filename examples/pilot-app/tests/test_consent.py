"""Thin-Slice — Einwilligungs-Logbuch. Akzeptanztests (aus SPEC §4)."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
import consent_ledger as cl  # noqa: E402


class _Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def _led(d):
    return cl.ConsentLedger(d, clock=_Clock(datetime(2026, 6, 8, tzinfo=timezone.utc)))


class GrantAndStatus(unittest.TestCase):
    def test_grant_then_active(self):
        with tempfile.TemporaryDirectory() as d:
            led = _led(d)
            cid = led.grant("user-7f3a", "newsletter")
            self.assertTrue(cid)
            self.assertTrue(led.is_active("user-7f3a", "newsletter"))


class Withdraw(unittest.TestCase):
    def test_withdraw_deactivates(self):
        with tempfile.TemporaryDirectory() as d:
            led = _led(d)
            cid = led.grant("user-7f3a", "newsletter")
            self.assertTrue(led.withdraw(cid))
            self.assertFalse(led.is_active("user-7f3a", "newsletter"))

    def test_withdraw_unknown_is_false(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(_led(d).withdraw("gibt-es-nicht"))


class ListActive(unittest.TestCase):
    def test_only_active_of_subject(self):
        with tempfile.TemporaryDirectory() as d:
            led = _led(d)
            a = led.grant("user-a", "newsletter")
            led.grant("user-a", "analytics")
            led.grant("user-b", "newsletter")
            led.withdraw(a)
            purposes = {r["purpose"] for r in led.list_active("user-a")}
            self.assertEqual(purposes, {"analytics"})


class NoPiiInLogAndPersistence(unittest.TestCase):
    def test_log_has_no_pii(self):
        with tempfile.TemporaryDirectory() as d:
            led = _led(d)
            led.grant("max.mustermann@example.com", "newsletter")  # Aufrufer-Fehler simuliert
            with open(led.log_path, encoding="utf-8") as f:
                log = f.read()
            self.assertNotIn("max.mustermann@example.com", log)  # subject_ref wird NICHT geloggt

    def test_persistence_across_restart(self):
        with tempfile.TemporaryDirectory() as d:
            cid = _led(d).grant("user-7f3a", "newsletter")
            again = _led(d)  # frischer Service, gleicher Speicher
            self.assertTrue(again.is_active("user-7f3a", "newsletter"))
            self.assertTrue(again.withdraw(cid))


class Art7Proof(unittest.TestCase):
    """Review-Befund: die Nachweis-Garantie (Art. 7) muss explizit geprüft sein."""

    def test_withdrawn_record_retained_as_proof(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            cid = _led(d).grant("user-7f3a", "newsletter")
            _led(d).withdraw(cid)
            with open(os.path.join(d, "consents.json"), encoding="utf-8") as f:
                recs = json.load(f)
            rec = next(r for r in recs if r["consent_id"] == cid)
            self.assertFalse(rec["active"])
            self.assertIsNotNone(rec["withdrawn_at"])   # Nachweis bleibt erhalten

    def test_log_positively_records_event(self):
        with tempfile.TemporaryDirectory() as d:
            led = _led(d)
            cid = led.grant("user-7f3a", "newsletter")
            with open(led.log_path, encoding="utf-8") as f:
                log = f.read()
            self.assertIn("consent_granted", log)
            self.assertIn("purpose=newsletter", log)
            self.assertIn(cid, log)

    def test_is_active_isolated_per_subject(self):
        with tempfile.TemporaryDirectory() as d:
            led = _led(d)
            led.grant("user-a", "newsletter")
            self.assertFalse(led.is_active("user-b", "newsletter"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
