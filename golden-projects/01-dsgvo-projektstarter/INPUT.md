# GP01 — Eingabe (strukturierte Projektangaben)

> Diese Angaben verarbeitet der Lauf zu den DSGVO-Artefakten in `artefakte/`.
> Beispielprojekt; fiktiver Mittelständler, alle Werte EU.

| Feld | Wert |
|---|---|
| Projektname | Terminbuchung & Anfragen — Elektro Krause GmbH |
| Zweck | Online-Terminvereinbarung und Angebotsanfragen für Privat- und Gewerbekunden |
| Datenarten | Name, Anschrift, E-Mail, Telefon, gewünschter Termin, Freitext-Anliegen, Auftragsbezug |
| Besondere Kategorien (Art. 9) | keine |
| Betroffenengruppen | Kunden, Interessenten |
| Systeme | Web-App (Next.js), PostgreSQL, Objektspeicher (Backups), LLM-Assistent für Anliegen-Vorklassifizierung |
| Hosting-Region | EU — Deutschland (Rechenzentrum Falkenstein/Nürnberg) |
| LLM-Endpunkt | Amazon Bedrock, Region eu-central-1 (Frankfurt) |
| Subdienstleister | Hetzner Online GmbH (Hosting, DE) · AWS EMEA SARL (Bedrock, eu-central-1) · mailjet (Smtp, EU-Region) |
| Speicherdauer | Termin-/Auftragsdaten 24 Monate; Anfragen ohne Auftrag 6 Monate; Server-Logs 30 Tage |
| Zugriffsrollen | Inhaber (Admin) · Mitarbeiter (Termine lesen/schreiben) · System (technisch) |
| Verantwortlicher | Elektro Krause GmbH, Musterstraße 12, 01067 Dresden; GF: Petra Krause |
| DSB | kein DSB bestellt (Schwellen Art. 37 nicht erreicht; jährliche Prüfung dokumentiert) |
| Rechtsgrundlage | Art. 6 Abs. 1 lit. b (Vertrag/Anbahnung) |
