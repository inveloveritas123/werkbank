"""GP02 — Kontaktformular mit Betroffenenrechten (DSAR). Kern-Service.

stdlib-only, lauffähig. Eigenschaften (DSGVO-relevant):
- Betroffenenrechte: Export (Art. 15/20) und Löschung (Art. 17) — nur für den EIGENEN Datensatz.
- Zugriffsschutz: pro Anfrage ein Access-Token; at-rest nur der SHA-256-Hash (kein Klartext-Token).
- Mandantentrennung: Admin-Sicht je tenant gefiltert.
- Datenminimierung in Logs: Logs enthalten nur pseudonyme subject_id + Event, NIE Name/E-Mail/Nachricht.
- Aufbewahrung: purge_expired() löscht Datensätze nach Ablauf der Frist (Retention-Job).
"""
import hashlib
import hmac
import json
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


class AccessDenied(Exception):
    """Fremder oder ungültiger Zugriff auf einen Datensatz."""


@dataclass
class Receipt:
    subject_id: str
    access_token: str


def _utcnow():
    return datetime.now(timezone.utc)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _as_utc(dt: datetime) -> datetime:
    """Normalisiert naive Zeiten auf UTC -> robuster Retention-Vergleich (kein TypeError)."""
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


class ContactService:
    def __init__(self, storage_dir, clock=_utcnow, retention_days=180):
        self.dir = storage_dir
        os.makedirs(self.dir, exist_ok=True)
        self.clock = clock
        self.retention_days = retention_days
        self.store_path = os.path.join(self.dir, "contacts.json")
        self.log_path = os.path.join(self.dir, "app.log")
        self._records = self._load()

    # ---------- Persistenz ----------
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

    # ---------- PII-sicheres Logging (Gate E2) ----------
    def _log(self, event, subject_id=None, tenant=None, count=None):
        ts = self.clock().isoformat()
        parts = ["%s INFO %s" % (ts, event)]
        if subject_id is not None:
            parts.append("subject=%s" % subject_id)
        if tenant is not None:
            parts.append("tenant=%s" % tenant)
        if count is not None:
            parts.append("count=%d" % count)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(" ".join(parts) + "\n")

    # ---------- Anfrage speichern ----------
    def submit(self, name, email, message, tenant="default"):
        subject_id = uuid.uuid4().hex
        access_token = secrets.token_urlsafe(24)
        self._records.append({
            "subject_id": subject_id,
            "tenant": tenant,
            "name": name,
            "email": email,
            "message": message,
            "created_at": self.clock().isoformat(),
            "token_hash": _hash_token(access_token),
        })
        self._save()
        self._log("contact_submitted", subject_id=subject_id, tenant=tenant)
        return Receipt(subject_id=subject_id, access_token=access_token)

    # ---------- Zugriffsprüfung ----------
    def _authorized_record(self, subject_id, access_token):
        for rec in self._records:
            if rec["subject_id"] == subject_id:
                # fail-closed: fehlender/leerer Hash oder Token -> Zugriff verweigert (kein KeyError)
                stored = rec.get("token_hash") or ""
                if stored and hmac.compare_digest(stored, _hash_token(access_token or "")):
                    return rec
                raise AccessDenied("Token stimmt nicht")
        raise AccessDenied("Datensatz nicht gefunden")

    # ---------- Auskunft / Export (Art. 15/20) ----------
    def export(self, subject_id, access_token):
        rec = self._authorized_record(subject_id, access_token)
        self._log("dsar_export", subject_id=subject_id, tenant=rec["tenant"])
        return {k: rec[k] for k in ("subject_id", "tenant", "name", "email", "message", "created_at")}

    # ---------- Löschung (Art. 17) ----------
    def delete(self, subject_id, access_token):
        rec = self._authorized_record(subject_id, access_token)
        self._records = [r for r in self._records if r["subject_id"] != subject_id]
        self._save()
        self._log("dsar_delete", subject_id=subject_id, tenant=rec["tenant"])
        return True

    # ---------- Admin-Sicht (mandantengetrennt) ----------
    def admin_list(self, tenant=None):
        return [
            {"subject_id": r["subject_id"], "tenant": r["tenant"], "created_at": r["created_at"]}
            for r in self._records
            if tenant is None or r["tenant"] == tenant
        ]

    # ---------- Retention-Job ----------
    def purge_expired(self, now=None):
        now = _as_utc(now or self.clock())
        cutoff = now - timedelta(days=self.retention_days)
        keep, removed = [], 0
        for r in self._records:
            created = _as_utc(datetime.fromisoformat(r["created_at"]))
            if created < cutoff:
                removed += 1
            else:
                keep.append(r)
        if removed:
            self._records = keep
            self._save()
            self._log("retention_purge", count=removed)
        return removed
