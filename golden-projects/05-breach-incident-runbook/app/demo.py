"""GP05 — lauffähige Demo: erzeugt aus einem Beispielvorfall die vier Runbook-Dokumente.

Lauf:  python3 demo.py [zielverzeichnis]
"""
import os
import sys

import breach_runbook as br
import legal_claims as lc

INCIDENT = {
    "type": "Unbefugter Zugriff auf die Kundendatenbank",
    "systems": ["Kundendatenbank", "Web-App"],
    "data_types": ["Name", "E-Mail", "Telefon", "Auftragsdaten"],
    "detected_at": "2026-06-08T08:00:00+00:00",
    "occurred_at": "2026-06-07T22:00:00+00:00",
    "detection": "Auffaellige Login-Muster im Monitoring",
    "scope": "ca. 1.200 Kundendatensaetze potenziell betroffen",
    "special_categories": False,
}


def run(out_dir=None):
    docs = br.generate(INCIDENT)
    findings = lc.lint_texts(docs)
    print("Dokumente:", ", ".join(sorted(docs)))
    print("Fake-Rechtsaussagen-Linter:", "SAUBER" if not findings else "BEFUNDE: %r" % findings)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        for name, text in docs.items():
            with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
                f.write(text)
        print("geschrieben nach", out_dir)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
