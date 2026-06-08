# DATA-FLOW — Upload mit PII-Redaction (GP04)

> Kein Rechtsrat — fachliche Prüfung durch DSB/Anwalt. Stand 2026-06-08.

- **Datenarten:** Hochgeladener Freitext/Dokument, der personenbezogene Daten enthalten kann
  (E-Mail, Telefon, IBAN, Name). Besondere Kategorien nach Art. 9: nicht vorgesehen.
- **Quellen → Verarbeitung → Senken:**
  1. Eingang: Datei-Upload (TXT) über die App.
  2. Verarbeitung: PII-Erkennung (E-Mail/Telefon/IBAN/Kreditkarte/Name) und Redaction.
     Das Original wird at-rest gespeichert; für nachgelagerte Schritte (z. B. LLM) wird ein
     **PII-freier Prompt-Dump** mit Platzhaltern erzeugt.
  3. Senken: Original (`uploads/`), maskierter Report (`reports/`), Prompt-Dump (`prompts/`),
     pseudonymes Log (`app.log`).
- **Beteiligte Systeme:** Upload-/Redaction-Dienst (Python stdlib), Dateispeicher. Kein externer LLM-Aufruf im Beispiel.
- **Wo verlässt etwas die EU?** Nirgends — Betrieb EU-only (Deployment-Vorgabe), keine externen Endpunkte.
- **Wo entsteht PII in Prompts/Logs?** Nirgends im Klartext: der Prompt-Dump enthält nur Platzhalter,
  das Log nur Upload-ID, Trefferzahl und Treffer-Typen (Datenminimierung, Gate E2).
- **Restrisiko (ehrlich):** Das Original im Speicher (`uploads/`) enthält die unredigierten Daten;
  Verschlüsselung at-rest und Löschfristen sind Deployment-/Betriebsmaßnahmen. Die Löschfunktion
  entfernt Original, Report und Prompt-Dump gemeinsam.
