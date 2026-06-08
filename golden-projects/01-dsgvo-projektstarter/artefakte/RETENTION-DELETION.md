# RETENTION-DELETION — Aufbewahrung & Löschung

| Datenart | Aufbewahrungsfrist | Rechtsgrund | Löschmechanismus |
|---|---|---|---|
| Termin-/Auftragsdaten | 24 Monate nach letzter Leistung | Vertragsabwicklung, Gewährleistung | Nächtlicher Lösch-Job nach Fristablauf (DB + Backup-Rotation) |
| Anfragen ohne Auftrag | 6 Monate nach Eingang | Anbahnung, danach kein Zweck | Automatischer Lösch-Job |
| Server-Logs (pseudonym) | 30 Tage | Betrieb/Sicherheit | Rotierende Logvorhaltung, automatische Löschung |

- **Löschkonzept:** Fristen sind je Datenart als Job konfiguriert; Backups folgen einer 30-Tage-Rotation,
  sodass gelöschte Datensätze spätestens mit Ablauf der Rotation auch aus Backups entfernt sind.
  Steuerlich aufbewahrungspflichtige Belege (z. B. Rechnungen) werden separat nach HGB/AO behandelt
  und sind nicht Teil dieses Buchungsdatenbestands.
