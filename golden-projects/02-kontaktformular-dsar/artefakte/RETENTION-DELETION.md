# RETENTION-DELETION — Kontaktformular mit DSAR (GP02)

| Datenart | Aufbewahrungsfrist | Rechtsgrund | Löschmechanismus |
|---|---|---|---|
| Kontaktanfragen (Name, E-Mail, Nachricht) | 180 Tage nach Eingang | Bearbeitung der Anfrage, danach kein Zweck | `purge_expired()` (Retention-Job) entfernt abgelaufene Datensätze |
| Anwendungs-Log (pseudonym) | 30 Tage | Betrieb/Sicherheit | Rotierende Logvorhaltung, automatische Löschung |

- **Löschkonzept:** Die Aufbewahrungsfrist ist im Dienst als `retention_days` konfiguriert; der
  Retention-Job `purge_expired()` löscht Datensätze, deren `created_at` älter als die Frist ist,
  und protokolliert nur die Anzahl (kein PII). Zusätzlich kann eine betroffene Person ihre Daten
  jederzeit über die Löschfunktion (Art. 17) sofort entfernen lassen.
- **Backups:** In der Beispielkonfiguration wird der Dateispeicher gesichert; gelöschte Datensätze
  fallen mit der nächsten Backup-Rotation auch dort weg.
