"""GP03 — lauffähige Demo des Mini-CRM mit Mandantentrennung.

Lauf:  python3 demo.py [audit_log_pfad]
Zeigt: A liest A (ok) · A liest B (denied) · B liest B (ok) · manipulierte tenant_id (denied) ·
       Liste je Mandant. Schreibt ein schema-konformes, PII-freies Audit-Log.
Mit Argument wird das Audit-Log an den angegebenen Pfad geschrieben (reproduzierbare Evidence,
fester Zeitstempel); Kundendaten liegen nur in einem temporären Verzeichnis.
"""
import os
import sys
import tempfile
from datetime import datetime, timezone

from crm_service import CrmService, Principal, AccessDenied


class _Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def run(audit_path=None):
    clock = _Clock(datetime(2026, 6, 8, 9, 0, 0, tzinfo=timezone.utc))
    with tempfile.TemporaryDirectory() as d:
        svc = CrmService(storage_dir=d, clock=clock,
                         audit_path=audit_path or os.path.join(d, "audit.log"))
        a = Principal("u-a", "tenantA")
        b = Principal("u-b", "tenantB")
        ca = svc.create_customer(a, "Kunde A", "a@example.com")
        cb = svc.create_customer(b, "Kunde B", "b@example.com")

        print("A liest A:", svc.get_customer(a, ca)["customer_id"] == ca)
        for label, p, cid, claimed in [("A liest B", a, cb, None),
                                       ("manipulierte tenant_id", a, ca, "tenantB")]:
            try:
                svc.get_customer(p, cid, claimed_tenant=claimed)
                print(label, "-> UNERWARTET erlaubt")
            except AccessDenied:
                print(label, "-> korrekt blockiert")
        print("B liest B:", svc.get_customer(b, cb)["customer_id"] == cb)
        print("Liste A:", [r["customer_id"] for r in svc.list_customers(a)] == [ca])
        print("Audit-Log:", svc.audit_path)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
