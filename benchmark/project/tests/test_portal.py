"""Benchmark-App Akzeptanztests (aus SPEC)."""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
import portal as p  # noqa: E402


class _Clock:
    def __init__(self, t): self.t = t
    def __call__(self): return self.t


def _portal(d):
    return p.Portal(d, clock=_Clock(datetime(2026, 6, 9, tzinfo=timezone.utc)),
                    audit_path=os.path.join(d, "audit.log"))


class TenantIsolation(unittest.TestCase):
    def test_cross_tenant_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            s = _portal(d)
            a = p.Principal("u-a", "tenantA"); b = p.Principal("u-b", "tenantB")
            ca = s.add_contact(a, "Kunde A", "a@example.com")
            with self.assertRaises(p.AccessDenied):
                s.get_contact(b, ca)
            self.assertEqual({r["contact_id"] for r in s.list_contacts(a)}, {ca})
            self.assertEqual(s.list_contacts(b), [])


class Consent(unittest.TestCase):
    def test_grant_withdraw(self):
        with tempfile.TemporaryDirectory() as d:
            s = _portal(d); a = p.Principal("u-a", "t1")
            c = s.add_contact(a, "N", "n@example.com")
            s.grant_consent(a, c, "newsletter")
            self.assertTrue(s.is_consented(a, c, "newsletter"))
            s.withdraw_consent(a, c, "newsletter")
            self.assertFalse(s.is_consented(a, c, "newsletter"))


class NoPiiInLog(unittest.TestCase):
    def test_log_pii_free(self):
        with tempfile.TemporaryDirectory() as d:
            s = _portal(d); a = p.Principal("u-a", "t1")
            s.add_contact(a, "Erika Mustermann", "erika@example.com")
            with open(s.log_path, encoding="utf-8") as f:
                log = f.read()
            self.assertNotIn("erika@example.com", log)
            self.assertNotIn("Erika", log)


class Persistence(unittest.TestCase):
    def test_survives_restart(self):
        with tempfile.TemporaryDirectory() as d:
            a = p.Principal("u-a", "t1")
            cid = _portal(d).add_contact(a, "N", "n@example.com")
            self.assertEqual({r["contact_id"] for r in _portal(d).list_contacts(a)}, {cid})


if __name__ == "__main__":
    unittest.main(verbosity=2)
