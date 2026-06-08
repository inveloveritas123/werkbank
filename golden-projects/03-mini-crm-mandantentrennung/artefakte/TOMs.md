# TOMs — Mini-CRM mit Mandantentrennung (GP03), Art. 32

| Bereich | Maßnahme (Soll) | Status |
|---|---|---|
| Mandantentrennung | tenant wird aus dem authentifizierten Principal abgeleitet, nie aus Client-Parametern | umgesetzt |
| Zugriffskontrolle | Jeder Lese-/Schreibzugriff gegen den Principal-Mandanten geprüft; Cross-Tenant → AccessDenied | umgesetzt |
| Manipulationsschutz | Behauptete (claimed) tenant_id ≠ Principal-Mandant → Zugriff verweigert | umgesetzt |
| Nachvollziehbarkeit | Unveränderliches Audit-Log je Zugriff (success/denied), schema-konform | umgesetzt |
| Datenminimierung | Audit-Log nur mit IDs/Mandant/Event — keine Klartext-PII (Gate E2) | umgesetzt |
| EU-Datenresidenz | routing_region=EU in jedem Audit-Eintrag; Betrieb EU-only (Gate E1) | umgesetzt |
| Integrität | Atomare Schreibvorgänge (replace) für den Datenspeicher | umgesetzt |
| Prüfbarkeit | Cross-Tenant-Negativtest in der Test-Suite; Gate E3 prüft Audit-Log auf Tenant-Lecks | umgesetzt |

> Status = Selbsteinschätzung des Verantwortlichen; Nachweis im Maßnahmen-/Audit-Register.
> Vorlage, kein Rechtsnachweis. Verschlüsselung at-rest des Datenspeichers ist Deployment-Maßnahme.
