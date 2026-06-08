# GP02 — Kontaktformular mit DSAR (lauffähige App)

stdlib-only (Python 3), keine externen Abhängigkeiten.

## Module
- `contact_service.py` — Kern: `submit`, `export` (Art. 15/20), `delete` (Art. 17),
  `admin_list` (mandantengetrennt), `purge_expired` (Retention-Job). PII-sicheres Logging.
- `demo.py` — End-to-End-Durchlauf.

## Ausführen
```bash
python3 demo.py
```

## DSGVO-Eigenschaften
- Betroffenenrechte nur für den **eigenen** Datensatz (Access-Token; at-rest nur SHA-256-Hash).
- Mandantentrennung in der Admin-Sicht.
- Logs ohne Klartext-PII (nur `subject_id`/`tenant`/Event) → Gate **E2** grün.
- Aufbewahrung über `retention_days`; `purge_expired()` löscht abgelaufene Datensätze.

## Tests
Aus dem Repo-Root: `python3 -m unittest discover -s gates/checks/tests -p "test_gp02.py"`

## Artefakte
DSGVO-Artefakte in `../artefakte/` (DATA-FLOW, RETENTION-DELETION, DSAR-RIGHTS); Gate-Ergebnis in `../GATE-REPORT.md`.
