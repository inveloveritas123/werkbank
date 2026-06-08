# CHANGELOG

> Append, neuster Eintrag oben (Gate H4).

## 2026-06-09 — Budget / Kill-Switch
- `orchestrator/budget.py`: `check(spent, cap, kill)` → ok/warn/kill (0 = inert). State `.werkbank/budget.json`;
  Spend via `budget.py add <eur>` (kein Auto-Metering, ehrlich). **In den Ralph-Loop integriert:**
  Kill-Switch hält den autonomen Lauf an (HALT vor jeder Runde). Installer legt inerten State an. +7 Tests.

## 2026-06-09 — B-Gates + C2 (statisch/Coverage)
- **B3** (Build, py_compile, stdlib): kompiliert alle .py des Ziels — real (Self-Lauf: 20 .py sauber).
- **B1** (ruff) · **B2** (mypy) · **C2** (coverage.py): verdrahtet, laufen wenn das Tool da ist,
  sonst **SKIP** (ehrlich, kein Vortäuschen). +5 Tests. Alle GP-Läufe + Thin-Slice + Self-Lauf GRUEN.

## 2026-06-09 — I2 QA-Tribunal (Cross-Model) + Reconciliation
- `tribunal/reconcile.py`: deterministische, **anonymisierte** Reconciliation (nur klare Pass-Mehrheit
  besteht; `uncertain`/Gleichstand → konservativ block). `tribunal/tribunal.sh`: Fresh-Context-Fan-out,
  ruft N Reviewer (real: `claude -p --model …`), sammelt `VERDICT:`-Zeilen. +8 Tests.
- **Live bewiesen:** haiku+sonnet+opus urteilten unabhängig über den Thin-Slice → einstimmig pass →
  reconcile pass. Damit ist die früher fehlende **Cross-Model-Diversität** real.
- Verdrahtet in Workflow 03 (Meilenstein-Gate); Installer kopiert `tribunal/`. Ehrlich: LLM-Urteile
  nicht-deterministisch, Reconciliation ist es. SOLL-IST: I1/I2 als Harness ✅ (🟡 LLM-Anteil).

## 2026-06-09 — E6/E7 echt (DSFA-Erzwingung + Drittland) — 12 → 14 Gates
- **E6** (Art. 35): bei hohem Risiko im DPIA-Screening (`[x]`/`| ja |`) MUSS DPIA.md vorhanden+gefüllt sein;
  kein hohes Risiko → PASS. **E7** (Kap. V): Drittlandtransfer → Garantie (SCC/Angemessenheit/BCR) nötig; EU-only → PASS.
  Beide SKIP ohne Privacy-Kontext/Artefakt. +9 Tests.
- **Latente Regression behoben:** seit H4 (T9) als Block-Gate fehlte den per-GP-Gate-Zielen eine
  CHANGELOG.md → H4 rot. Jetzt hat jedes gegatete Bundle (GP01–06) eine CHANGELOG.md; alle GP-Läufe wieder GRUEN.
- SOLL-IST: E6/E7 ✅ (14/41 Gates). Suite + Self-Lauf + alle 6 GP-Läufe + Thin-Slice GRUEN.

## 2026-06-08 — Durchstich: Thin-Slice 01→04 LIVE (BMAD-Methode bewiesen)
- `examples/pilot-app/` „Einwilligungs-Logbuch" (Art. 7 DSGVO) durch den vollen WERKBANK-Loop:
  **01** BMAD-Templates → Brief/PRD/Architektur → `SPEC.md` (A-Gates grün) · **02** `app/consent_ledger.py`
  + 9 Tests (RED→GREEN), Ralph-Loop schließt GRUEN+promise · **03** voller Gate-Lauf GRUEN (A1/A2/A3,
  C1, D3, E1/E2, F1, H4) · **04** PR, Cross-Model-Review (opus) → keine Live-Bugs, Art.-7-Nachweis-Tests ergänzt.
- **Bug gefangen & gefixt:** C1 verdoppelte den Testpfad bei `--target <subdir>` (rel+cwd) → absoluter Pfad.
- SOLL-IST: BMAD ✅, Thin-Slice ✅. Methode→Spec→Bau→Gate→Review→PR jetzt end-to-end bewiesen.

## 2026-06-08 — T9 (Substanz): BMAD-Anbindung + A-Gates (Spec-Integrität)
- **A1/A2/A3** echt gemacht (`gates/checks/a_spec.py`, Runner-Flag `--spec-file`): A1 Pflichtfelder
  gefüllt/platzhalterfrei · A2 Akzeptanzkriterien testbar · A3 Handoff PM→Architect erfüllt.
  SKIP ohne SPEC. **9 → 12 Gates.** +6 Tests.
- **Workflows 01–04** von Stubs zu echten Playbooks: 01 ruft BMAD-Skills (bmad-prd/-architecture/
  -epics-and-stories) und erzeugt einen A-Gate-tauglichen SPEC; 02 nutzt den Ralph-Loop + Tier-Routing;
  03 den vollen Gate-Lauf; 04 PR (kein Selbst-Merge). Agenten-Status-Zeilen ehrlich aktualisiert.
- Damit ist die „Methode→Spec→Gate"-Kette real; 1 vollständiger BMAD-Durchstich bleibt als nächster Schritt.

## 2026-06-08 — T9 (Substanz): Echter Ralph-Loop (Autonomie-Motor)
- `ralph/ralph_decide.py` — deterministische Entscheidungs-Engine (fertig/weiter/anhalten),
  inkl. **Drift-Pausegate** (rote Gates gestiegen → HALT) und max-iterations-Netz. Eine Quelle der Wahrheit.
- `ralph/ralph-loop.sh` — **Fresh-Context-Motor** (Blueprint-bevorzugt): Worker je Runde mit frischem
  Kontext, re-invoziert bis **alle Block-Gates grün UND `<promise>GRUEN</promise>`**. Exit 0/3/2.
- `ralph/stop_hook.py` (+ `settings.stop-hook.json`) — In-Session-Stop-Hook (opt-in via `--ralph-hook`).
- **10 Tests** (Engine + Bash-Motor end-to-end + Stop-Hook). Installer kopiert `ralph/`.
- Ehrlich: Stop-Hook `block` pausiert, re-invoziert interaktiv nicht garantiert — daher ist der
  Bash-Motor der vollautonome Weg (genau die Blueprint-Empfehlung). SOLL-IST: Ralph-Loop ✅.

## 2026-06-08 — T9: Drei Gates echt gemacht (C1/F1/H4) — 6 → 9 implementiert
- **C1** (Unit-Tests grün): führt die Test-Suite des Ziels als Block-Gate aus — schließt die Lücke
  „Tests existieren, aber kein Gate führt sie aus" (Repo-Self-Lauf: C1 = 102 Tests grün).
- **F1** (Modell-Pinning): FAIL bei `model: …latest` / `…-latest` — jetzt mit Tier-Routing relevant.
- **H4** (CHANGELOG): vorhanden + newest-top. Installer legt für frische Projekte eine CHANGELOG.md an.
- 9 neue Tests; clean-Fixture um CHANGELOG ergänzt; SOLL-IST-Abgleich aktualisiert. Keine Regression.

## 2026-06-08 — Modell-Tier-Routing (Kostenoptimierung der Subagenten)
- `orchestrator/tier_router.py` + `werkbank.tiers.json`: deterministische Policy Aufgabentyp→Tier→Modell
  (doku/summary→haiku · impl/test→sonnet · review/security/privacy/plan→opus), `confirm_tier_from: opus`,
  nested-merge-Override, CLI (`<label>` / `--table`). 9 Tests.
- Verdrahtet: `model:`-Tier-Frontmatter in `agents/*.md`; Regel in `CLAUDE.werkbank.md` + `workflows/02-bauen.md`;
  Installer kopiert `orchestrator/`; Kommentar in `settings.example.yaml`.
- **Ehrlichkeit:** Python erzwingt das Modell nicht — der Orchestrator setzt `model=` beim Spawn.
  Bis hierher liefen Paar-Reviews auf dem teuren Default; mit dem Router wird die Tier-Verteilung wirksam.
- Live-Beleg: 3 Subagenten parallel mit model=haiku/sonnet/opus gespawnt → gemeldete Modell-IDs
  (haiku-4-5 / sonnet-4-6 / opus-4-8) stimmen mit der Zuweisung überein. Definitiver Beweis: `/cost` je Modell.

## 2026-06-08 — Ein-Befehl-Installer (BMAD + kiln + WERKBANK als Einheit)
- `werkbank-init.sh`: richtet pro Projekt mit EINEM Befehl alles ein — kopiert gates/templates/
  agents/workflows + CI, initialisiert kiln-`STATE.md`, härtet `.gitignore`, installiert BMAD,
  legt Branch `werkbank-build` an und macht einen Gate-Baseline-Lauf. Idempotent; `--no-bmad`/`--force`.
- `templates/CLAUDE.werkbank.md`: vereinende `CLAUDE.md` — beschreibt die drei Schichten (Methode/
  Autonomie/Governance) + den Loop, damit der Agent sie als EINE Einheit behandelt.
- README-Quickstart ergänzt. Getestet gegen Wegwerf-Projekt (Setup + Gate-Baseline GRUEN, idempotent).

## 2026-06-08 — Freigaben erteilt (intern, ohne echte Kundendaten)
- Menschliche Freigaben durch Robert Hargesheimer in den Freigabefeldern eingetragen:
  Grenzen/Haftung akzeptiert · Security-Restrisiken akzeptiert · DSB freigegeben **mit Auflagen**.
- **Geltungsbereich: interner Einsatz OHNE echte personenbezogene Kundendaten.**
- Auflagen für echte Kundendaten (offen): D1/D2, Laufzeit-EU-Routing, manipulationssicheres Audit-Log,
  At-rest-Verschlüsselung; E6 (DSFA) + E7 (Drittland) als Gates implementieren.
- Merge von PR #1 (werkbank-build → main) durch menschliche Freigabe autorisiert.

## 2026-06-08 — Produktivfreigabe-Doku (Vorbereitung, post-Backlog)
- `docs/produktivfreigabe/`: **GRENZEN-UND-HAFTUNG.md** (Scope/Disclaimer, was WERKBANK nicht garantiert),
  **SECURITY-REVIEW.md** (Gate-Abdeckung, gefundene/gefixte Befunde, Restrisiken, Freigabefeld),
  **DATENSCHUTZ-REVIEW.md** (DSGVO-Artikel-Abdeckung, Restlücken, DSB-Freigabefeld) + README.
- Self-Assessments mit menschlichen Freigabefeldern — keine Selbst-Zertifizierung, kein Rechtsrat.
- Repo-Self-Lauf GRUEN, 84/84 Tests, keine Secrets.

## 2026-06-08 — T8 · Golden Project 06 (RAG mit PII-Filter) · Score 97/100 — Backlog vollständig
- Mini-RAG `golden-projects/06-rag-pii-filter/app/` (stdlib, kein LLM): deterministisches
  Keyword-Retrieval; Antwort = wörtlicher Satz aus belegtem Dokument (keine Halluzination);
  ohne passende Quelle wird verweigert; jede Antwort nennt die Quelle; PII-Filter auf der Ausgabe;
  `delete(doc_id)` entfernt aus dem Index.
- 2 Artefakte (DATA-FLOW, RETENTION-DELETION); GP06-Gate-Lauf GRUEN (E1/E2/D3/E5).
- **ACT/Paar-Review:** 3 SPEC-Verstöße gefixt — Namen ohne Anrede (Klartext-Leck), Quelle nicht
  redigiert, Halluzination bei 1-Token-Überlappung (Schwelle jetzt Token-Anteil ≥ 50 %). +3 Tests.
- **Tests 84/84 grün; Regression GP01–05 GRUEN; Repo-Self-Lauf GRUEN.** Score 97/100.
- **Reifegrad: 6/6 Golden Projects grün — Sprint-Backlog (T0–T8) vollständig abgearbeitet.**

## 2026-06-08 — T7 · Golden Project 05 (Breach/Incident-Runbook) · Score 98/100
- Breach-Runbook-Generator `golden-projects/05-breach-incident-runbook/app/`: aus einem Vorfall
  werden 4 Dokumente (BREACH-RUNBOOK, INCIDENT-TIMELINE, NOTIFICATION-CHECKLIST, LESSONS-LEARNED)
  erzeugt — 72h-Frist (Art. 33) berechnet, Meldeentscheidung als begründete Einschätzung (kein Rechtsrat).
- Deterministischer **„Fake-Rechtsaussagen"-Linter** (`legal_claims.py`): flaggt absolute Rechts-/
  Meldegarantien, Haftungsausschlüsse, fehlenden Disclaimer — und (nach Review) **kahle unhedged
  Meldeaussagen** („nicht meldepflichtig"/„nicht erforderlich") hedge-bewusst.
- GP05-Gate-Lauf GRUEN (E1/E2/D3/E5). Review-Gate: GDPR-Korrektheit unabhängig bestätigt.
- **Tests 76/76 grün; Regression GP01–04 GRUEN; Repo-Self-Lauf GRUEN.** Score 98/100. Reifegrad: **5 GP grün**.

## 2026-06-08 — T6 · Golden Project 04 (Upload PII-Redaction) · Score 98/100
- Upload-Dienst mit PII-Erkennung & Redaction `golden-projects/04-upload-pii-redaction/app/`
  (`pii_redactor.py` + `upload_service.py` + Demo): erkennt E-Mail/Telefon/IBAN/Kreditkarte/Name,
  maskiert im Report, erzeugt PII-freien Prompt-Dump (Platzhalter), PII-freies Log, Löschung.
- DATA-FLOW-Artefakt; GP04-Gate-Lauf GRUEN (E1/E2/D3/E5), E2 hart über echte Outputs.
- **Cross-cutting Gate-Härtung (Paar-Review):** Redactor UND E2 gegen reale False-Negatives gehärtet —
  Telefon `+49 (0)…`, Namen ohne Anrede (Grußformel/Selbstnennung; **E2 erkennt jetzt Namen**),
  Auslands-IBAN (beliebiges Land + mod-97). Defense-in-Depth: E2 unabhängig breiter als der Redactor.
  Adversariales Korpus-Testset (Prompt-Dump per unabhängigem E2-Scan sauber).
- **Tests 63/63 grün; Regression GP01–03 GRUEN; Repo-Self-Lauf GRUEN.** Score 98/100. Reifegrad: 4 GP grün.

## 2026-06-08 — T5 · Golden Project 03 (Mini-CRM Mandantentrennung) · Score 98/100
- Multi-Tenant Mini-CRM `golden-projects/03-mini-crm-mandantentrennung/app/` (stdlib): Mandant kommt
  aus dem Principal, nie vom Client; Cross-Tenant- und manipulierte-`tenant_id`-Zugriffe → `AccessDenied`.
- Schema-konformes, PII-freies Audit-Log (`templates/AUDIT-LOG.schema.json`); Demo + Evidence.
- **Zwei neue deterministische Gates:** **E3** (Tenant-Isolation aus Audit-Log: kein Cross-Tenant-Erfolg)
  und **E4** (Audit-Log schema-valide, strikte Typprüfung). Runner-Flags `--audit-log`/`--audit-schema`.
- Soll-Ist 6/6 grün (A↔B-Isolation, manipulierte tenant_id scheitert, Audit ohne PII).
- **ACT/Paar-Review:** 2 Härtungs-Bugs in E3/E4 gefixt (E3-Regex-Evasion via verkürzter Ressource/`*`;
  E4 ohne Typprüfung ließ `pii_present:0` durch). +6 Tests.
- **Tests 54/54 grün; Regression GP01–02 GRUEN; Repo-Self-Lauf GRUEN.** Score 98/100. Reifegrad: 3 GP grün.

## 2026-06-08 — T4 · Golden Project 02 (Kontaktformular DSAR) · Score 99/100
- Erstes Golden Project mit echtem Code: `golden-projects/02-kontaktformular-dsar/app/`
  (stdlib-only Kontakt-/DSAR-Dienst + `demo.py`). Betroffenenrechte Export (Art. 15/20) & Löschung
  (Art. 17) nur für eigenen Datensatz (Access-Token, at-rest nur SHA-256-Hash), Mandantentrennung,
  Retention-Job, PII-freie Logs.
- 3 DSGVO-Artefakte (DATA-FLOW, RETENTION-DELETION, DSAR-RIGHTS); GP02-Gate-Lauf GRUEN (E1/E2/D3/E5).
- Runner-Flag `--privacy-required` (E5 mit projektspezifischer Soll-Artefaktliste).
- **Soll-Ist 6/6 grün** (Speichern/Export/Löschung/Fremdzugriff-Block/keine-PII-Log/Retention).
- **ACT/Paar-Review:** 2 echte Bugs gefixt (Autorisierung fail-closed statt KeyError; Retention-Job
  datetime-robust) + Anti-Overclaim (Klartext-at-rest dokumentiert). +3 Tests.
- **Tests 41/41 grün; Regression GP01 GRUEN; Repo-Self-Lauf GRUEN.** Score 99/100. Details: `.werkbank/BENCHMARK.md`.

## 2026-06-08 — T3 · PDCA-Zyklus 1 (E2-Telefonerkennung)
- Kontrollierte Selbstverbesserung gegen die BENCHMARK-Historie: E2 erkennt jetzt deutsche
  Telefon-Nationalformate (`0151…`, `0351-…`) und `0049` zusätzlich zu `+49`.
- **Metrik Vorher→Nachher: 2/5 → 5/5** Telefonformate. False-Positive-Schutz (National-Muster
  verlangt Trenner nach Vorwahl → keine Treffer auf `status=200`, Zeitstempel, IBAN-Fragmente).
- 2 neue Tests (Coverage + FP). **Tests 30/30 grün; GP01 bleibt GRUEN (Regression frei); Block-Gates grün.**
- Vollständige Vorher/Nachher-Messung: `.werkbank/BENCHMARK.md`.

## 2026-06-08 — T2 · Golden Project 01 (DSGVO-Projektstarter) · Score 97/100
- Beispielprojekt `golden-projects/01-dsgvo-projektstarter/INPUT.md` → 7 gefüllte DSGVO-Artefakte
  in `artefakte/` (DATA-FLOW, PROCESSING-REGISTER, LAWFUL-BASIS, DPIA-SCREENING, TOMs,
  PROCESSORS-SUBPROCESSORS, RETENTION-DELETION) — keine Platzhalter, EU-only, intern konsistent.
- Neuer Check **E5** (Artefakt-Vollständigkeit): prüft Vorhandensein/Füllung/Platzhalterfreiheit/EU-Region;
  „nicht anwendbar → SKIP", damit Läufe ohne DSGVO-Kontext grün bleiben. Runner-Flag `--privacy-dir`.
- GP01-Gate-Lauf: **GRUEN** (E1/E2/D3/E5 PASS), `golden-projects/01-.../GATE-REPORT.md`.
- **SECURITY_SEEDS Catch-Rate 3/3** (E-Mail→E2, Dummy-Token→D3, US-Endpunkt→E1; zur Laufzeit synthetisiert).
- **Tests:** 28/28 grün (T1 19 + GP01 9).
- **ACT/PDCA:** Paar-Review → E5-Erkennung gehärtet (Klartext-Platzhalter, Prosa-Non-EU, FP-Fix) +
  Artefakt-Überzeichnung entfernt (TOMs-Selbsteinschätzung, Subprozessor-Präzision). Keine Regression.
- **Score 97/100** (≥85), 0 Block-Gates rot, 0 Secrets, 0 kritische DSGVO-Funde. Details: `.werkbank/BENCHMARK.md`.

## 2026-06-08 — T1 · Gate-Runner + 3 deterministische Gates (E1/D3/E2)
- `gates/runner.py` (+ `gates/runner`-Shim): liest `gates.yaml` (eigener YAML-Subset-Parser, kein Dependency),
  führt Gates gestaffelt aus (fail-fast bei Block-FAIL), schreibt `GATE-REPORT.md`. Nicht-implementierte Gates → SKIP (ehrlich).
- Checks (stdlib, kein LLM): **E1** EU-Routing (AWS/GCP/Azure-non-EU-Regionen, `us.*`-Model-IDs, openai.com),
  **E2** PII in Logs/Prompts/Outputs (Mail, +49-Tel, DE-IBAN, Kreditkarte+Luhn), **D3** Secret-Scan (Built-in-Regex + optional gitleaks).
- Redaction: GATE-REPORT enthält nie Klartext-Secrets/PII (per Test abgesichert).
- Self-Lauf-Schutz: Runner schließt das Gate-Tooling-Verzeichnis automatisch aus, wenn es unter dem Scan-Ziel liegt.
- **Tests:** 19/19 grün; Negativtests synthetisieren je einen Verstoß zur Laufzeit (Repo bleibt secret-/PII-frei).
- **ACT (PDCA):** Paar-Review (Reviewer ≠ Implementer) → E1-Marker erweitert (Azure-US, `us.anthropic.*`), keine Regression. Siehe `.werkbank/BENCHMARK.md`.
- Repo-Self-Gate-Lauf: **GRUEN**, 0 Block-Gates rot, 0 Secrets, 0 PII.

## 2026-06-08 — T0 · Fundament
- Ziel-Struktur aus Blueprint §3 angelegt: `agents/` (junge, waechter, kanzler[disabled], privacy-analyst),
  `workflows/` (01-konzipieren … 04-uebergeben), `gates/checks/`, `templates/`
  (SPEC, ARCHITECTURE, TASKS, GATE-REPORT, AUDIT-LOG.schema.json), `examples/pilot-app/`,
  `.github/workflows/werkbank-gates.yml` (CI-Stub).
- `privacy/`: 11 DSGVO-Artefakt-Vorlagen aus `DSGVO-ARTEFAKTE.md` als einzeln befüllbare Dateien.
- BMAD installiert ins `examples/pilot-app/` (core + bmm v6.8.0, 44 Skills, 6 Rollen) — Methoden-/Rollenschicht.
  Install-Artefakte gitignored (reinstallierbar, Blueprint §1 "installieren, nicht nachbauen").
- `.werkbank/STATE.md` initialisiert (crash-sicherer Pipeline-State; lokal/gitignored).
- Branch `werkbank-build` von GitHub-`main` (@9807fa7).
