"""GP03 — Mini-CRM mit harter Mandantentrennung. Kern-Service (stdlib-only).

Prinzip: Der Mandant (tenant) wird IMMER aus dem authentifizierten Principal abgeleitet,
niemals aus einem Client-Parameter. Jeder Zugriff auf eine fremde tenant wird abgewiesen
(AccessDenied) und im Audit-Log als `denied` festgehalten. Das Audit-Log ist schema-konform
(templates/AUDIT-LOG.schema.json) und enthält keine unnötige PII (nur IDs/Mandant/Event).
"""
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


class AccessDenied(Exception):
    """Tenant-übergreifender oder manipulierter Zugriff."""


@dataclass
class Principal:
    user_id: str
    tenant: str
    role: str = "user"


def _utcnow():
    return datetime.now(timezone.utc)


class CrmService:
    def __init__(self, storage_dir, clock=_utcnow, audit_path=None):
        self.dir = storage_dir
        os.makedirs(self.dir, exist_ok=True)
        self.clock = clock
        self.store_path = os.path.join(self.dir, "customers.json")
        self.audit_path = audit_path or os.path.join(self.dir, "audit.log")
        self._records = self._load()

    def _load(self):
        if os.path.isfile(self.store_path):
            with open(self.store_path, encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        tmp = self.store_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._records, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.store_path)

    def _audit(self, actor_tenant, user_id, action, owner_tenant, customer_id, result):
        # Nur IDs/Mandant/Event — keine PII. Schema-konform (AUDIT-LOG.schema.json).
        entry = {
            "timestamp": self.clock().isoformat(),
            "actor": "user:%s" % user_id,
            "action": action,
            "resource": "tenant:%s/customer:%s" % (owner_tenant, customer_id),
            "tenant_id": actor_tenant,
            "result": result,
            "routing_region": "EU",
            "pii_present": False,
        }
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ---------- Schreiben ----------
    def create_customer(self, principal, name, email):
        customer_id = uuid.uuid4().hex
        self._records.append({
            "customer_id": customer_id,
            "tenant": principal.tenant,
            "name": name,
            "email": email,
            "created_at": self.clock().isoformat(),
        })
        self._save()
        self._audit(principal.tenant, principal.user_id, "create", principal.tenant, customer_id, "success")
        return customer_id

    # ---------- Lesen (mandantengeprüft) ----------
    def get_customer(self, principal, customer_id, claimed_tenant=None):
        # Manipulierte tenant_id: Client behauptet einen anderen Mandanten als der Principal -> denied.
        if claimed_tenant is not None and claimed_tenant != principal.tenant:
            self._audit(principal.tenant, principal.user_id, "read", claimed_tenant, customer_id, "denied")
            raise AccessDenied("tenant_id-Manipulation")
        rec = next((r for r in self._records if r["customer_id"] == customer_id), None)
        if rec is None:
            self._audit(principal.tenant, principal.user_id, "read", "unknown", customer_id, "denied")
            raise AccessDenied("nicht gefunden")
        if rec["tenant"] != principal.tenant:
            # Cross-Tenant-Zugriff: NICHT die Daten zurückgeben, als denied protokollieren.
            self._audit(principal.tenant, principal.user_id, "read", rec["tenant"], customer_id, "denied")
            raise AccessDenied("tenant-übergreifend")
        self._audit(principal.tenant, principal.user_id, "read", rec["tenant"], customer_id, "success")
        return {k: rec[k] for k in ("customer_id", "tenant", "name", "email", "created_at")}

    # ---------- Liste (auf eigenen Mandanten beschränkt) ----------
    def list_customers(self, principal):
        rows = [
            {k: r[k] for k in ("customer_id", "tenant", "name", "email", "created_at")}
            for r in self._records if r["tenant"] == principal.tenant
        ]
        self._audit(principal.tenant, principal.user_id, "read", principal.tenant, "*", "success")
        return rows
