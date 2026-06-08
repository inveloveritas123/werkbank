# DATA-FLOW — RAG mit PII-Filter (GP06)

> Kein Rechtsrat — fachliche Prüfung durch DSB/Anwalt. Stand 2026-06-08.

- **Datenarten:** Interne Dokumente/FAQ, die personenbezogene Daten enthalten können
  (z. B. Ansprechpartner-Name, E-Mail). Besondere Kategorien nach Art. 9: nicht vorgesehen.
- **Quellen → Verarbeitung → Senken:**
  1. Import: interne Texte werden mit Quelle (source) in den Index aufgenommen.
  2. Retrieval: zu einer Frage wird das belegende Dokument per Schlüsselwort-Überlappung bestimmt.
  3. Antwort: ein WÖRTLICHER Satz aus dem belegten Dokument wird zurückgegeben (keine Generierung,
     keine Halluzination); ohne passende Quelle wird die Antwort verweigert.
  4. PII-Filter: vor der Ausgabe werden E-Mail/Telefon/IBAN/Name maskiert (keine unnötige PII-Ausgabe).
- **Beteiligte Systeme:** RAG-Index (In-Memory), PII-Filter. Kein externer LLM-Aufruf im Beispiel.
- **Wo verlässt etwas die EU?** Nirgends — Betrieb EU-only, keine externen Endpunkte.
- **Wo entsteht PII in Prompts/Logs?** Antworten sind PII-maskiert; eine autorisierte Klartext-Ausgabe
  wäre ein separater, gesondert zu berechtigender Vorgang. Logs führen keine Klartext-PII (Gate E2).
- **Quellenangabe:** Jede belegte Antwort nennt die Quelle (Nachvollziehbarkeit, Anti-Halluzination).
