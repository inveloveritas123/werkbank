"""GP02 — lauffähige End-to-End-Demo des Kontakt-/DSAR-Dienstes.

Lauf:  python3 demo.py            (nutzt ein temporäres Verzeichnis)
Zeigt: Speichern -> Admin-Sicht (mandantengetrennt) -> Export -> Fremdzugriff blockiert
       -> Löschung -> Retention-Job. Gibt nur pseudonyme IDs aus (keine PII im Output).
"""
import tempfile
from datetime import datetime, timedelta, timezone

from contact_service import ContactService, AccessDenied


class _Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def main():
    with tempfile.TemporaryDirectory() as d:
        clock = _Clock(datetime(2026, 1, 1, tzinfo=timezone.utc))
        svc = ContactService(storage_dir=d, clock=clock, retention_days=180)

        a = svc.submit("Erika Mustermann", "erika@example.com", "Bitte um Angebot", tenant="krause")
        b = svc.submit("Tom Beispiel", "tom@example.com", "Termin?", tenant="schmidt")
        print("gespeichert:", a.subject_id, "und", b.subject_id)
        print("Admin-Sicht tenant=krause:", [r["subject_id"] for r in svc.admin_list(tenant="krause")])

        exported = svc.export(a.subject_id, a.access_token)
        print("Export (eigener Datensatz) Felder:", sorted(exported.keys()))

        try:
            svc.export(a.subject_id, b.access_token)
        except AccessDenied:
            print("Fremdzugriff korrekt blockiert (AccessDenied)")

        svc.delete(a.subject_id, a.access_token)
        print("nach Löschung verbleibend:", [r["subject_id"] for r in svc.admin_list()])

        clock.t = clock.t + timedelta(days=400)
        svc.submit("Neu Kunde", "neu@example.com", "frisch", tenant="krause")
        purged = svc.purge_expired()
        print("Retention-Job entfernte:", purged, "Datensatz/Datensätze")

        log = open(svc.log_path, encoding="utf-8").read()
        print("Log-Zeilen:", log.count("\n"), "| enthält '@':", "@" in log)


if __name__ == "__main__":
    main()
