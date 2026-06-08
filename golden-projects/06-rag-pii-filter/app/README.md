# GP06 — RAG mit PII-Filter (lauffähige App)

stdlib-only (Python 3), keine externen Abhängigkeiten, kein LLM.

## Module
- `rag_index.py` — `RagIndex` mit `add`, `answer`, `delete`. Deterministisches Keyword-Retrieval;
  die Antwort ist ein **wörtlicher Satz aus dem belegten Dokument** (keine Halluzination); ohne
  passende Quelle wird die Antwort verweigert. Jede Antwort nennt die Quelle.
- `pii_filter.py` — maskiert E-Mail/Telefon/IBAN/Name in der Ausgabe (keine unnötige PII-Ausgabe).
- `demo.py` — End-to-End-Durchlauf inkl. Anti-Halluzination und Index-Löschung.

## Ausführen
```bash
python3 demo.py                 # nur Ausgabe
python3 demo.py ../evidence     # PII-freies Antwort-Log als Gate-Evidence
```

## DSGVO-Eigenschaften
- Quellenangabe je Antwort (Nachvollziehbarkeit, Anti-Halluzination).
- PII in Antworten standardmäßig maskiert; Logs ohne Klartext-PII (Gate E2).
- `delete(doc_id)` entfernt Dokumente aus dem Index (Art. 17, Index-Löschung).

## Tests
`python3 -m unittest discover -s gates/checks/tests -p "test_gp06.py"`
