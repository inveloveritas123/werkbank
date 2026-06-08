# GP04 — Upload mit PII-Erkennung & Redaction
**Ziel:** Datei-Upload erkennt personenbezogene Daten und behandelt sie sauber.
**Feature:** PDF/TXT hochladen · System erkennt E-Mail/Telefon/IBAN/Name-Muster · Report maskiert Fundstellen · Original nicht ins Log.
**Soll-Ist (alle grün):**
- PII erkannt · PII im Report maskiert · keine PII im Log · keine PII im Prompt-Dump · Datei-Löschung OK
**Soll-Outputs:** App + Tests (mit PII-Testdaten) + DATA-FLOW.md + GATE-REPORT.md
**Akzeptanz:** Score >= 85, E2 grün (hart), Regression GP01–03 grün.
