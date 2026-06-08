"""Thin-Slice — Einwilligungs-Logbuch (Art. 7 DSGVO). stdlib-only.

grant/withdraw/is_active/list_active mit dateibasierter Persistenz. Das Audit-Log enthält NUR
consent_id, purpose und Event — niemals den (pseudonymen) subject_ref im Klartext (Art. 5,
Datenminimierung; Gate E2). Widerruf so einfach wie die Erteilung (Art. 7 Abs. 3); der Datensatz
bleibt als Nachweis erhalten (Art. 7 Abs. 1).
"""
import json
import os
import uuid
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc)


class ConsentLedger:
    def __init__(self, storage_dir, clock=_utcnow):
        self.dir = storage_dir
        os.makedirs(self.dir, exist_ok=True)
        self.clock = clock
        self.store_path = os.path.join(self.dir, "consents.json")
        self.log_path = os.path.join(self.dir, "app.log")
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

    def _log(self, event, consent_id, purpose):
        # Datenminimierung: kein subject_ref im Log.
        line = "%s INFO %s id=%s purpose=%s\n" % (self.clock().isoformat(), event, consent_id, purpose)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)

    def grant(self, subject_ref, purpose):
        # Contract: `purpose` ist ein nicht-personenbezogenes Zweck-Label (z. B. "newsletter").
        # Klartext-PII in purpose würde im Log landen — Gate E2 fängt das als Schutznetz.
        consent_id = uuid.uuid4().hex
        self._records.append({
            "consent_id": consent_id,
            "subject_ref": subject_ref,
            "purpose": purpose,
            "granted_at": self.clock().isoformat(),
            "active": True,
            "withdrawn_at": None,
        })
        self._save()
        self._log("consent_granted", consent_id, purpose)
        return consent_id

    def withdraw(self, consent_id):
        for r in self._records:
            if r["consent_id"] == consent_id:
                if r["active"]:
                    r["active"] = False
                    r["withdrawn_at"] = self.clock().isoformat()
                    self._save()
                    self._log("consent_withdrawn", consent_id, r["purpose"])
                return True
        return False

    def is_active(self, subject_ref, purpose):
        return any(r["active"] and r["subject_ref"] == subject_ref and r["purpose"] == purpose
                   for r in self._records)

    def list_active(self, subject_ref):
        return [{"consent_id": r["consent_id"], "purpose": r["purpose"], "granted_at": r["granted_at"]}
                for r in self._records if r["active"] and r["subject_ref"] == subject_ref]
