# GP04 — Upload mit PII-Redaction (lauffähige App)

stdlib-only (Python 3), keine externen Abhängigkeiten.

## Module
- `pii_redactor.py` — erkennt E-Mail/Telefon/IBAN/Kreditkarte/Name und ersetzt sie durch
  Platzhalter ([EMAIL]/[PHONE]/[IBAN]/[CARD]/[NAME]). Liefert maskierte Befunde (kein Klartext).
- `upload_service.py` — `upload` (Original speichern, maskierter Report, PII-freier Prompt-Dump,
  pseudonymes Log), `get_report`, `get_prompt_dump`, `delete`.
- `demo.py` — End-to-End-Durchlauf; schreibt optional PII-freie Evidence.

## Ausführen
```bash
python3 demo.py                 # Demo im Temp-Verzeichnis
python3 demo.py ../evidence     # PII-freie Ergebnisse als Gate-Evidence
```

## DSGVO-Eigenschaften
- Original nicht ins Log; Log nur mit Upload-ID/Trefferzahl/Typen.
- Prompt-Dump ausschließlich mit Platzhaltern → kein PII-Leck Richtung LLM (Gate E2).
- Löschung entfernt Original, Report und Prompt-Dump gemeinsam.

## Tests
`python3 -m unittest discover -s gates/checks/tests -p "test_gp04.py"`
