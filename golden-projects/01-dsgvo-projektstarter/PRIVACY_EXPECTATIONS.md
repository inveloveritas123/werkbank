# GP01 — DSGVO-Soll
- E1 EU-Routing: jeder LLM-Call über EU-Endpunkt → grün.
- E2 PII-Scan: keine Klartext-PII in Logs/Prompts/Reports → grün.
- E5 Artefakt-Vollständigkeit: alle EXPECTED_OUTPUTS vorhanden & gefüllt → grün.
- E6 DPIA: falls Screening „hohes Risiko" → DPIA.md vorhanden.
- Drittland (E7): wenn Region=EU und keine US-Subdienstleister → THIRD-COUNTRY = „nein", belegt.
