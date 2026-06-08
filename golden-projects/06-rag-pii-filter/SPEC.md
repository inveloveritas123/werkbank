# GP06 — RAG über interne Dokumente mit PII-Filter
**Ziel:** Mini-Wissenssystem, das interne Texte durchsucht, aber PII schützt.
**Feature:** Dokumente importieren · PII erkennen · Antworten geben · Quellen nennen · PII nicht unnötig ausgeben.
**Soll-Ist (alle grün):**
- Antwort fachlich korrekt · Quelle genannt · keine unnötige PII-Ausgabe · keine Halluzination ohne Quelle · Löschung aus Index funktioniert
**Soll-Outputs:** App + Tests + DATA-FLOW.md + RETENTION-DELETION.md (Index-Löschung) + GATE-REPORT.md
**Akzeptanz:** Score >= 85, E2 grün, Regression GP01–05 grün.
