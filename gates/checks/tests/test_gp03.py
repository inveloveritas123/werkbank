"""GP03 — Mini-CRM mit Mandantentrennung. Soll-Ist-Tests.

SPEC: A liest A · A liest B NICHT · B liest B · B liest A NICHT ·
manipulierte tenant_id schlägt fehl · Audit-Log ohne unnötige PII.
Plus: E3 (keine Cross-Tenant-Erfolge) und E4 (Audit-Log schema-valid) grün.
"""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
APP_DIR = os.path.join(REPO_ROOT, "golden-projects", "03-mini-crm-mandantentrennung", "app")
ARTE = os.path.join(REPO_ROOT, "golden-projects", "03-mini-crm-mandantentrennung", "artefakte")
SCHEMA = os.path.join(REPO_ROOT, "templates", "AUDIT-LOG.schema.json")
sys.path.insert(0, GATES_DIR)
sys.path.insert(0, APP_DIR)

import crm_service as crm  # noqa: E402

from checks import common, e2_pii_scan, e3_tenant_isolation, e4_audit_log, e5_artefakte  # noqa: E402


class _Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def _svc(d):
    return crm.CrmService(storage_dir=d, clock=_Clock(datetime(2026, 6, 8, tzinfo=timezone.utc)),
                          audit_path=os.path.join(d, "audit.log"))


def _seed(s):
    pa = crm.Principal("u-a", "tenantA")
    pb = crm.Principal("u-b", "tenantB")
    ca = s.create_customer(pa, "Kunde A", "a@example.com")
    cb = s.create_customer(pb, "Kunde B", "b@example.com")
    return pa, pb, ca, cb


class TenantIsolation(unittest.TestCase):
    def test_own_tenant_reads(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            pa, pb, ca, cb = _seed(s)
            self.assertEqual(s.get_customer(pa, ca)["email"], "a@example.com")
            self.assertEqual(s.get_customer(pb, cb)["email"], "b@example.com")

    def test_cross_tenant_read_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            pa, pb, ca, cb = _seed(s)
            with self.assertRaises(crm.AccessDenied):
                s.get_customer(pa, cb)   # A liest B NICHT
            with self.assertRaises(crm.AccessDenied):
                s.get_customer(pb, ca)   # B liest A NICHT

    def test_list_scoped_to_tenant(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            pa, pb, ca, cb = _seed(s)
            self.assertEqual({r["customer_id"] for r in s.list_customers(pa)}, {ca})
            self.assertEqual({r["customer_id"] for r in s.list_customers(pb)}, {cb})


class ManipulatedTenantId(unittest.TestCase):
    def test_forged_tenant_id_denied(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            pa, pb, ca, cb = _seed(s)
            # Principal A behauptet, Mandant B zu sein -> muss scheitern (Tenant kommt vom Principal)
            with self.assertRaises(crm.AccessDenied):
                s.get_customer(pa, ca, claimed_tenant="tenantB")


class AuditLog(unittest.TestCase):
    def test_audit_has_no_pii_and_is_schema_valid(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            pa, pb, ca, cb = _seed(s)
            try:
                s.get_customer(pa, cb)
            except crm.AccessDenied:
                pass
            with open(s.audit_path, encoding="utf-8") as fh:
                text = fh.read()
            self.assertNotIn("a@example.com", text)
            self.assertNotIn("Kunde A", text)
            # E2 (keine PII) + E4 (Schema) + E3 (kein Cross-Tenant-Erfolg)
            self.assertEqual(e2_pii_scan.run(d).status, common.PASS)
            self.assertEqual(e4_audit_log.run(d, audit_log=s.audit_path, schema_path=SCHEMA).status, common.PASS)
            self.assertEqual(e3_tenant_isolation.run(d, audit_log=s.audit_path).status, common.PASS)

    def test_e3_fails_on_cross_tenant_success(self):
        # Negativtest des Gates selbst: ein manipuliertes Audit-Log mit Cross-Tenant-Erfolg -> E3 FAIL
        with tempfile.TemporaryDirectory() as d:
            ap = os.path.join(d, "audit.log")
            entry = {"timestamp": "2026-06-08T00:00:00+00:00", "actor": "user:u-a",
                     "action": "read", "resource": "tenant:tenantB/customer:x",
                     "tenant_id": "tenantA", "result": "success",
                     "routing_region": "EU", "pii_present": False}
            with open(ap, "w", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            self.assertEqual(e3_tenant_isolation.run(d, audit_log=ap).status, common.FAIL)


class GateHardening(unittest.TestCase):
    """Review-Befunde: E3/E4 dürfen Cross-Tenant-Lecks / Schema-Verstöße nicht durchlassen."""

    def _write_audit(self, d, entries):
        ap = os.path.join(d, "audit.log")
        with open(ap, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        return ap

    def _ok(self, **over):
        e = {"timestamp": "2026-06-08T00:00:00+00:00", "actor": "user:u-a", "action": "read",
             "resource": "tenant:tenantA/customer:x", "tenant_id": "tenantA",
             "result": "success", "routing_region": "EU", "pii_present": False}
        e.update(over)
        return e

    def test_e3_catches_slashless_resource(self):
        with tempfile.TemporaryDirectory() as d:
            ap = self._write_audit(d, [self._ok(resource="tenant:tenantB", result="success")])
            self.assertEqual(e3_tenant_isolation.run(d, audit_log=ap).status, common.FAIL)

    def test_e3_catches_wildcard_owner(self):
        with tempfile.TemporaryDirectory() as d:
            ap = self._write_audit(d, [self._ok(resource="tenant:*/customer:x", result="success")])
            self.assertEqual(e3_tenant_isolation.run(d, audit_log=ap).status, common.FAIL)

    def test_e4_rejects_nonbool_pii(self):
        with tempfile.TemporaryDirectory() as d:
            ap = self._write_audit(d, [self._ok(pii_present=0)])
            self.assertEqual(e4_audit_log.run(d, audit_log=ap, schema_path=SCHEMA).status, common.FAIL)

    def test_e4_rejects_wrong_type(self):
        with tempfile.TemporaryDirectory() as d:
            ap = self._write_audit(d, [self._ok(tenant_id=123)])
            self.assertEqual(e4_audit_log.run(d, audit_log=ap, schema_path=SCHEMA).status, common.FAIL)

    def test_e3_e4_still_pass_on_valid(self):
        with tempfile.TemporaryDirectory() as d:
            ap = self._write_audit(d, [self._ok(), self._ok(resource="tenant:tenantB/customer:y",
                                                            tenant_id="tenantA", result="denied")])
            self.assertEqual(e3_tenant_isolation.run(d, audit_log=ap).status, common.PASS)
            self.assertEqual(e4_audit_log.run(d, audit_log=ap, schema_path=SCHEMA).status, common.PASS)


class ForgedTenantOnRealRecord(unittest.TestCase):
    def test_forge_tenant_against_other_record(self):
        with tempfile.TemporaryDirectory() as d:
            s = _svc(d)
            pa, pb, ca, cb = _seed(s)
            # A behauptet tenantB UND zielt auf B's echten Datensatz -> muss scheitern
            with self.assertRaises(crm.AccessDenied):
                s.get_customer(pa, cb, claimed_tenant="tenantB")


class ArtefactsComplete(unittest.TestCase):
    def test_toms_complete(self):
        res = e5_artefakte.run(ARTE, privacy_dir=ARTE, required=["TOMs.md"])
        self.assertEqual(res.status, common.PASS, res.summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
