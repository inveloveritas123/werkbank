"""Benchmark-App — Multi-Tenant Einwilligungs-Portal (stdlib).

Vereint die Eigenschaften, die möglichst viele Gates ansprechen: Mandantentrennung (E3) mit
schema-konformem Audit-Log (E4), PII-armes Logging (E2), Einwilligung (Art. 7), Zugriffsschutz,
Persistenz. EU-only (E1), keine Secrets (D3), kein 'latest' (F1).
"""
import hashlib
import hmac
import json
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


class AccessDenied(Exception):
    pass


@dataclass
class Principal:
    user_id: str
    tenant: str


def _utcnow():
    return datetime.now(timezone.utc)


class Portal:
    def __init__(self, storage_dir, clock=_utcnow, audit_path=None):
        self.dir = storage_dir
        os.makedirs(self.dir, exist_ok=True)
        self.clock = clock
        self.store_path = os.path.join(self.dir, "contacts.json")
        self.log_path = os.path.join(self.dir, "app.log")
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

    def _log(self, event, contact_id, tenant):
        ts = self.clock().isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write("%s INFO %s id=%s tenant=%s\n" % (ts, event, contact_id, tenant))

    def _audit(self, actor_tenant, user_id, action, owner_tenant, contact_id, result):
        entry = {
            "timestamp": self.clock().isoformat(), "actor": "user:%s" % user_id,
            "action": action, "resource": "tenant:%s/contact:%s" % (owner_tenant, contact_id),
            "tenant_id": actor_tenant, "result": result, "routing_region": "EU", "pii_present": False,
        }
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def add_contact(self, principal, name, email):
        cid = uuid.uuid4().hex
        token = secrets.token_urlsafe(24)
        self._records.append({
            "contact_id": cid, "tenant": principal.tenant, "name": name, "email": email,
            "created_at": self.clock().isoformat(), "consents": {},
            "token_hash": hashlib.sha256(token.encode()).hexdigest(),
        })
        self._save()
        self._log("contact_added", cid, principal.tenant)
        self._audit(principal.tenant, principal.user_id, "create", principal.tenant, cid, "success")
        return cid

    def _owned(self, principal, contact_id, action):
        rec = next((r for r in self._records if r["contact_id"] == contact_id), None)
        if rec is None:
            self._audit(principal.tenant, principal.user_id, action, "unknown", contact_id, "denied")
            raise AccessDenied("nicht gefunden")
        if rec["tenant"] != principal.tenant:
            self._audit(principal.tenant, principal.user_id, action, rec["tenant"], contact_id, "denied")
            raise AccessDenied("tenant-übergreifend")
        return rec

    def get_contact(self, principal, contact_id):
        rec = self._owned(principal, contact_id, "read")
        self._audit(principal.tenant, principal.user_id, "read", rec["tenant"], contact_id, "success")
        return {k: rec[k] for k in ("contact_id", "tenant", "name", "email", "created_at", "consents")}

    def grant_consent(self, principal, contact_id, purpose):
        rec = self._owned(principal, contact_id, "update")
        rec["consents"][purpose] = True
        self._save()
        self._log("consent_granted", contact_id, principal.tenant)
        self._audit(principal.tenant, principal.user_id, "update", rec["tenant"], contact_id, "success")

    def withdraw_consent(self, principal, contact_id, purpose):
        rec = self._owned(principal, contact_id, "update")
        rec["consents"][purpose] = False
        self._save()
        self._log("consent_withdrawn", contact_id, principal.tenant)
        self._audit(principal.tenant, principal.user_id, "update", rec["tenant"], contact_id, "success")

    def is_consented(self, principal, contact_id, purpose):
        return bool(self._owned(principal, contact_id, "read")["consents"].get(purpose))

    def list_contacts(self, principal):
        return [{"contact_id": r["contact_id"], "tenant": r["tenant"]}
                for r in self._records if r["tenant"] == principal.tenant]
