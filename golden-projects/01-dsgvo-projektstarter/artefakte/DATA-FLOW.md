# DATA-FLOW — Terminbuchung & Anfragen, Elektro Krause GmbH

> Kein Rechtsrat — fachliche Prüfung durch DSB/Anwalt. Stand 2026-06-08.

- **Datenarten:** Name, Anschrift, E-Mail, Telefon, gewünschter Termin, Freitext-Anliegen, Auftragsbezug.
  Besondere Kategorien nach Art. 9: keine.
- **Quellen → Verarbeitung → Senken:**
  1. Eingang: Kunde füllt Web-Formular (TLS) aus.
  2. Verarbeitung: Validierung in der Web-App; Speicherung in PostgreSQL; optionale Vorklassifizierung
     des Freitext-Anliegens durch den LLM-Assistenten (nur Anliegen-Text, keine Kontaktdaten im Prompt).
  3. Senken: PostgreSQL (Primärspeicher), verschlüsselte Backups im Objektspeicher, E-Mail-Bestätigung via mailjet (EU).
- **Beteiligte Systeme:** Web-App (Next.js), PostgreSQL, Objektspeicher (Backups), Bedrock (eu-central-1)
  als LLM-Endpunkt, Server-Logs, mailjet (EU-Region) für Transaktionsmails.
- **Wo verlässt etwas die EU?** Nirgends. Hosting Deutschland (Hetzner, Falkenstein/Nürnberg),
  LLM über Bedrock Frankfurt (eu-central-1), Mailversand EU-Region. Beleg: THIRD-COUNTRY-TRANSFERS = „nein".
- **Wo entsteht PII in Prompts/Logs?** Prompts enthalten nur den Anliegen-Freitext ohne Kontaktdaten
  (Datenminimierung). Server-Logs führen nur pseudonyme Vorgangs-IDs, keine Klartext-PII (Maßnahme in TOMs, Gate E2).
