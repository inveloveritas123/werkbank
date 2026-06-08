# DATA-FLOW — Kontaktformular mit DSAR (GP02)

> Kein Rechtsrat — fachliche Prüfung durch DSB/Anwalt. Stand 2026-06-08.

- **Datenarten:** Name, E-Mail, Nachrichtentext, Mandant (tenant), Eingangszeitpunkt.
  Besondere Kategorien nach Art. 9: keine.
- **Quellen → Verarbeitung → Senken:**
  1. Eingang: Kunde sendet Kontaktanfrage (TLS). Der Dienst vergibt eine pseudonyme `subject_id`
     und ein Access-Token; gespeichert wird at-rest nur der SHA-256-Hash des Tokens.
  2. Verarbeitung: Speicherung in `contacts.json` (Primärspeicher), Admin-Sicht mandantengetrennt.
  3. Betroffenenrechte: Export (Art. 15/20) und Löschung (Art. 17) ausschließlich gegen gültiges Token.
  4. Senken: Primärspeicher; pseudonymes Anwendungs-Log `app.log`.
- **Beteiligte Systeme:** Web-/App-Dienst (Python stdlib), Dateispeicher, Anwendungs-Log. Kein LLM-Aufruf.
- **Wo verlässt etwas die EU?** Nirgends — Betrieb ausschließlich in der EU (Deployment-Vorgabe).
  Beleg: keine externen Endpunkte, keine Drittlandübermittlung.
- **Wo entsteht PII in Prompts/Logs?** Keine Prompts. Logs führen nur `subject_id`, `tenant`, Event und
  Zähler — niemals Name/E-Mail/Nachricht (Datenminimierung, Gate E2).
- **Restrisiko (ehrlich):** Im Primärspeicher (`contacts.json`) liegen Name/E-Mail/Nachricht im
  **Klartext** vor — gehasht wird nur das Access-Token, nicht die Kontaktdaten. Verschlüsselung
  at-rest (Datenbank/Dateisystem) ist eine Deployment-Maßnahme (siehe TOMs „Verschlüsselung").
