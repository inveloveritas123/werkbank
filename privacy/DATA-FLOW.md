# DATA-FLOW — Datenflussdiagramm (Grundlage für alles)

> Vorlage. Pro Projekt ausfüllen. **Kein Rechtsrat** — fachliche Prüfung durch DSB/Anwalt.

- **Datenarten:** <welche personenbezogenen Daten? Kategorien nach Art. 9?>
- **Quellen → Verarbeitung → Senken:** <Eingang | Schritte | Speicherorte | Ausgänge>
- **Beteiligte Systeme:** <App, DB, LLM-Endpunkt(e), Logs, Backups, Drittdienste>
- **Wo verlässt etwas die EU?** <jeden Punkt markieren → THIRD-COUNTRY-TRANSFERS> (Default: nein, Gate E1)
- **Wo entsteht PII in Prompts/Logs?** <→ TOMs „PII-Minimierung", Gate E2>
