# DATA-FLOW — Einwilligungs-Portal
- Datenarten: Name, E-Mail, Mandant, Einwilligungszwecke. Besondere Kategorien nach Art. 9: keine.
- Fluss: Eingang (TLS) → Speicherung pro Mandant → Audit-Log (PII-arm) → Senke Dateispeicher.
- Wo verlässt etwas die EU? Nirgends (EU-only). Beleg: THIRD-COUNTRY-TRANSFERS = nein.
- Datenminimierung: nur das für den Zweck Erforderliche wird erhoben; Logs ohne Klartext-PII (Art. 5/25).
