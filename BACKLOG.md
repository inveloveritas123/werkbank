# WERKBANK — BACKLOG (Aufgaben, die der Agent abarbeitet)

> **Single Source of Truth für offene Arbeit.** Der Bootstrap-Agent liest diese Datei aus dem
> Repo, nimmt die **oberste offene Aufgabe** (`[ ]`), arbeitet sie ab, misst gegen
> `SCORING-MATRIX.md`, verbessert sich gegen `SELF-IMPROVEMENT.md` — und hakt erst ab (`[x]`),
> wenn die Akzeptanz erfüllt ist. Reihenfolge ist verbindlich. Status pro Aufgabe pflegen.

## Status-Legende
`[ ]` offen · `[~]` in Arbeit · `[x]` fertig (Akzeptanz erfüllt) · `[!]` blockiert (Grund nennen)

---

## Sprint-Reihenfolge (nicht mit 62 Gates anfangen)

- [x] **T0 · Fundament** — BMAD installieren, Ziel-Struktur anlegen, `STATE.md` initialisieren.
  - Akzeptanz: Struktur aus Blueprint §3 existiert; `npx bmad-method install` gelaufen; STOPP vor T1.

- [x] **T1 · Gate-Runner + 3 deterministische Gates** — `gates/runner` + Checks `E1` (EU-Routing), `D3` (Secret-Scan), `E2` (PII-Scan). Kein LLM.
  - Akzeptanz: `runner` läuft über `gates/gates.yaml`, schreibt `GATE-REPORT.md`; E1/D3/E2 erkennen je einen bewusst gesetzten Verstoß (Negativtest grün).

- [x] **T2 · Golden Project 01 — DSGVO-Projektstarter** (`golden-projects/01-...`).
  - Akzeptanz: alle Soll-Artefakte erzeugt, Pflichtfelder gefüllt, keine TODO/TBD-Platzhalter, E-Gates grün, Score ≥ 85.

- [x] **T3 · Benchmark + erste kontrollierte Selbstverbesserung (PDCA)**.
  - Akzeptanz: `BENCHMARK.md` mit Vorher/Nachher; mindestens 1 Verbesserung aus `SELF-IMPROVEMENT.md` (erlaubte Liste) angewandt; **keine Regression**; alle Block-Gates grün.

- [x] **T4 · Golden Project 02 — Kontaktformular mit Auskunft & Löschung** (DSAR).
  - Akzeptanz: Speichern/Export/Löschung/Fremdzugriff-Block/keine-PII-im-Log/Retention-Job — alle Soll-Ist-Checks grün; Score ≥ 85; Regression über GP01 weiterhin grün.

- [x] **T5 · Golden Project 03 — Mini-CRM mit Mandantentrennung**.
  - Akzeptanz: A↔B-Isolation, manipulierte `tenant_id` schlägt fehl, Audit-Log ohne unnötige PII; Score ≥ 85; Regression GP01–02 grün.

- [ ] **T6 · Golden Project 04 — Upload mit PII-Redaction**.
  - Akzeptanz: PII erkannt & maskiert, keine PII in Log/Prompt-Dump, Löschung funktioniert; Score ≥ 85; Regression GP01–03 grün.

- [ ] **T7 · Golden Project 05 — Breach/Incident-Runbook**.
  - Akzeptanz: 72h-Prüfung, betroffene Datenarten, begründete Meldeentscheidung, Maßnahmenliste, **keine Fake-Rechtsaussagen**; Score ≥ 85.

- [ ] **T8 · Golden Project 06 — RAG mit PII-Filter**.
  - Akzeptanz: korrekte Antwort + Quelle, keine unnötige PII-Ausgabe, keine Halluzination ohne Quelle, Löschung aus Index; Score ≥ 85; Regression GP01–05 grün.

---

## Reifegrad-Tor (wann WERKBANK wofür nutzbar ist)
- **Interne Spielprojekte:** ab **1** Golden Project grün.
- **Interne interne Projekte (keine echten Kundendaten):** ab **3** Golden Projects grün.
- **Echte Kundenprojekte mit personenbezogenen Daten:** ab **5** Golden Projects grün **+** Security-Review **+** Datenschutz-Review **+** menschliche Merge-Freigabe **+** Grenzen-/Haftungsdoku.

## Regeln fürs Abhaken
- Eine Aufgabe gilt erst als `[x]`, wenn ihre Akzeptanz **gemessen** erfüllt ist (Score + grüne Gates), nicht wenn der Agent es „glaubt".
- Pro fertiger Aufgabe: CHANGELOG-Eintrag (neuster oben) + BENCHMARK-Eintrag + PR (kein Selbst-Merge).
- Verschlechtert eine Änderung eine frühere Aufgabe (Regression) → zurückrollen, Aufgabe bleibt `[~]`.
