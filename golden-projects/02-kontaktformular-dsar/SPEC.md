# GP02 — Kontaktformular mit Auskunft & Löschung (DSAR)
**Ziel:** kleine Web-App mit personenbezogenen Daten + echten Betroffenenrechten.
**Feature:** Nutzer sendet Anfrage · Admin sieht sie · Nutzer kann Export anfordern · Nutzer kann Löschung anfordern · Logs ohne Klartext-E-Mail.
**Soll-Ist (alle grün):**
- Kontakt speichern OK · Export liefert eigenen Datensatz OK · Löschung entfernt Datensatz OK
- fremder Zugriff blockiert · keine PII im Log · Retention-Job vorhanden
**Soll-Outputs:** lauffähige App + Tests + DATA-FLOW.md + RETENTION-DELETION.md + DSAR-RIGHTS.md + GATE-REPORT.md
**Akzeptanz:** Score >= 85, E1/E2 grün, Regression GP01 grün.
