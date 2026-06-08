"""GP04 — lauffähige Demo der Upload-PII-Redaction.

Lauf:  python3 demo.py [evidence_dir]
Verarbeitet einen Beispieltext mit PII. Original bleibt im Temp-Verzeichnis; nach evidence_dir
werden NUR die PII-freien Ergebnisse kopiert (maskierter Report, Prompt-Dump, Log).
"""
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone

from upload_service import UploadService


class _Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


SAMPLE = (
    "Sehr geehrte Damen und Herren,\n"
    "ich bin Herr Max Mustermann und bitte um Rückruf.\n"
    "Erreichbar unter max.mustermann@example.com oder 0151 23456789.\n"
    "Zur Erstattung: IBAN DE89 3704 0044 0532 0130 00.\n"
)


def run(evidence_dir=None):
    clock = _Clock(datetime(2026, 6, 8, 9, 0, 0, tzinfo=timezone.utc))
    with tempfile.TemporaryDirectory() as d:
        svc = UploadService(storage_dir=d, clock=clock)
        r = svc.upload("anfrage.txt", SAMPLE)
        print("Upload:", r.upload_id)
        print("PII-Treffer:", r.finding_count, "Typen:", r.finding_types)
        print("Prompt-Dump (PII-frei):")
        print(svc.get_prompt_dump(r.upload_id).strip())
        if evidence_dir:
            os.makedirs(evidence_dir, exist_ok=True)
            for sub in ("reports", "prompts"):
                dst = os.path.join(evidence_dir, sub)
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(os.path.join(d, sub), dst)
            shutil.copy(svc.log_path, os.path.join(evidence_dir, "app.log"))
            print("Evidence (PII-frei) ->", evidence_dir)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
