"""GP04 — Upload-Service mit PII-Redaction (stdlib-only).

upload() speichert das Original (mit PII) im Speicher, erzeugt einen maskierten Report und
einen PII-freien Prompt-Dump (Platzhalter) und protokolliert NUR id + Trefferzahl (keine PII).
delete() entfernt Original, Report und Prompt-Dump.
"""
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

import pii_redactor as red


class NotFound(Exception):
    pass


@dataclass
class UploadResult:
    upload_id: str
    finding_count: int
    finding_types: List[str] = field(default_factory=list)


def _utcnow():
    return datetime.now(timezone.utc)


class UploadService:
    def __init__(self, storage_dir, clock=_utcnow):
        self.dir = storage_dir
        self.clock = clock
        self.uploads = os.path.join(self.dir, "uploads")
        self.reports = os.path.join(self.dir, "reports")
        self.prompts = os.path.join(self.dir, "prompts")
        for p in (self.uploads, self.reports, self.prompts):
            os.makedirs(p, exist_ok=True)
        self.log_path = os.path.join(self.dir, "app.log")

    def _log(self, event, upload_id, **kv):
        parts = ["%s INFO %s id=%s" % (self.clock().isoformat(), event, upload_id)]
        parts += ["%s=%s" % (k, v) for k, v in kv.items()]
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(" ".join(parts) + "\n")

    def _p(self, base, upload_id, suffix):
        return os.path.join(base, "%s%s" % (upload_id, suffix))

    def upload(self, filename, content_text):
        upload_id = uuid.uuid4().hex
        # Original (mit PII) at-rest speichern — nicht ins Log.
        with open(self._p(self.uploads, upload_id, ".raw"), "w", encoding="utf-8") as f:
            f.write(content_text)
        redacted, findings = red.redact(content_text)
        kinds = sorted({f.kind for f in findings})
        # maskierter Report (kein Klartext-PII)
        lines = ["# PII-Redaction-Report", "", "Datei: %s" % os.path.basename(filename),
                 "Treffer: %d" % len(findings), ""]
        for f in findings:
            lines.append("- %s maskiert: `%s` (Position %d)" % (f.kind, f.masked, f.start))
        with open(self._p(self.reports, upload_id, ".report.md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        # PII-freier Prompt-Dump (Platzhalter statt PII)
        with open(self._p(self.prompts, upload_id, ".prompt"), "w", encoding="utf-8") as fh:
            fh.write(redacted)
        self._log("upload_processed", upload_id, pii_found=len(findings), types="|".join(kinds))
        return UploadResult(upload_id, len(findings), kinds)

    def exists(self, upload_id):
        return os.path.isfile(self._p(self.uploads, upload_id, ".raw"))

    def get_report(self, upload_id):
        p = self._p(self.reports, upload_id, ".report.md")
        if not os.path.isfile(p):
            raise NotFound(upload_id)
        with open(p, encoding="utf-8") as f:
            return f.read()

    def get_prompt_dump(self, upload_id):
        p = self._p(self.prompts, upload_id, ".prompt")
        if not os.path.isfile(p):
            raise NotFound(upload_id)
        with open(p, encoding="utf-8") as f:
            return f.read()

    def delete(self, upload_id):
        removed = False
        for base, suffix in ((self.uploads, ".raw"), (self.reports, ".report.md"),
                             (self.prompts, ".prompt")):
            p = self._p(base, upload_id, suffix)
            if os.path.isfile(p):
                os.remove(p)
                removed = True
        if removed:
            self._log("upload_deleted", upload_id)
        return removed
