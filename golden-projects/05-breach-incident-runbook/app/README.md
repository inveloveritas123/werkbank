# GP05 — Breach-/Incident-Runbook (lauffähige App)

stdlib-only (Python 3), keine externen Abhängigkeiten.

## Module
- `breach_runbook.py` — `generate(incident)` erzeugt vier Dokumente: BREACH-RUNBOOK,
  INCIDENT-TIMELINE, NOTIFICATION-CHECKLIST, LESSONS-LEARNED. 72-h-Frist (Art. 33) wird aus dem
  Erkennungszeitpunkt berechnet; die Meldeentscheidung ist eine **begründete Einschätzung** mit
  bedingter Sprache — keine verbindliche Rechtsaussage.
- `legal_claims.py` — Linter gegen **Fake-Rechtsaussagen** (absolute Konformitäts-/Haftungs-/
  Meldegarantien) und fehlenden „Kein Rechtsrat"-Disclaimer.
- `demo.py` — erzeugt die Dokumente und prüft sie mit dem Linter.

## Ausführen
```bash
python3 demo.py                 # nur Ausgabe
python3 demo.py ../artefakte    # Dokumente schreiben
```

## Wichtig
Kein Rechtsrat. Die finale Meldeentscheidung (Art. 33/34) trifft der DSB/Verantwortliche bzw.
Anwalt. Das Tool strukturiert und schätzt ein, es ersetzt keine juristische Prüfung.

## Tests
`python3 -m unittest discover -s gates/checks/tests -p "test_gp05.py"`
