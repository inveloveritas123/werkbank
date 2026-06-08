# TOMs — Technische & organisatorische Maßnahmen (Art. 32)

| Bereich | Maßnahme (Soll) | Status |
|---|---|---|
| Vertraulichkeit | Rollen-/Rechtemodell (Inhaber/Mitarbeiter/System), Zugriff nur nach Authentifizierung | umgesetzt |
| Integrität | Audit-Log für schreibende Zugriffe (unveränderlich), Vier-Augen-Gate für KI-generierten Code | umgesetzt |
| Verfügbarkeit | Tägliches verschlüsseltes Backup, dokumentierter Wiederherstellungsprozess | umgesetzt |
| Belastbarkeit | Last-/Concurrency-Test der Buchungs-Endpunkte vor Release | umgesetzt |
| Verschlüsselung | TLS im Transit, Verschlüsselung at-rest (DB und Backups) | umgesetzt |
| Pseudonym./Minimierung | Server-Logs nur mit pseudonymer Vorgangs-ID; Prompts ohne Kontaktdaten (Gate E2) | umgesetzt |
| EU-Datenresidenz | Ausschließlich EU-Endpunkte: Hosting DE, Bedrock eu-central-1, Mailversand EU (Gate E1) | umgesetzt |
| Wiederherstellbarkeit | Restore vierteljährlich getestet und protokolliert | geplant Q3-2026 |

> **Status = Selbsteinschätzung des Verantwortlichen.** „umgesetzt" verweist auf die jeweilige
> Maßnahme im Maßnahmen-/Audit-Register; im Rahmen der DSB-Prüfung wird der Nachweis geführt.
> Diese Tabelle ist eine Vorlage und kein Nachweis für sich.
