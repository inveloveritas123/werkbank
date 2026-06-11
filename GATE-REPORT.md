# GATE-REPORT — target=`.` — 2026-06-11T11:25:48Z

## Zusammenfassung
- **Ergebnis:** GRUEN
- **Profil (Pflichtenheft):** `werkbank_self` — WERKBANK-Repo selbst — volle statische Pflicht ohne Projekt-/Privacy-Kontext
- **Pflicht-Gates bestanden:** 9/9
- **Pflicht-Gates VERLETZT (FAIL):** 0
- **Pflicht-Gates UNGEDECKT (nicht geprueft):** 0
- **Pflicht-Gates ohne PASS:** 0
- **Optionale Befunde (warn):** 3

> **Hartes Gruen:** GRUEN gilt NUR, wenn alle 9 Pflicht-Gates aktiv bestanden sind. SKIP eines Pflicht-Gates (Tool fehlt / kein Check / kein Kontext) ⇒ UNGEDECKT ⇒ ROT.

## Detail je Stufe (Flags ★pflicht = Pflicht-Gate dieses Profils)
| Stufe | Gate | Flags | Ergebnis | Notiz |
|---|---|---|---|---|
| 1_spec | A1 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A2 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A3 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A4 | warn,llm | SKIP | kein BMAD-QA-Nachweis (.werkbank/qa-evidence.json) |
| 2_static | B1 | block,deterministic,★pflicht | PASS | ruff sauber |
| 2_static | B2 | block,deterministic,★pflicht | PASS | mypy sauber |
| 2_static | B3 | block,deterministic,★pflicht | PASS | Build/Compile sauber (29 .py) |
| 2_static | D1 | block,deterministic,★pflicht | PASS | kein High/Medium (12 Low, beraten) |
| 2_static | D2 | block,deterministic | SKIP | pip-audit/safety nicht installiert |
| 2_static | D3 | block,deterministic,★pflicht | PASS | kein Secret gefunden |
| 2_static | D4 | warn,deterministic | SKIP | pip-licenses nicht installiert |
| 3_tests | C1 | block,deterministic,★pflicht | PASS | Tests grün (313 Tests in gates/checks/tests) |
| 3_tests | C2 | block,deterministic,★pflicht | PASS | Coverage 88% >= 70% |
| 3_tests | C3 | block,deterministic | PASS | Integrationstests grün (6 in gates/checks/tests) |
| 3_tests | C4 | block,deterministic | SKIP | kein E2E konfiguriert |
| 3_tests | C5 | warn,deterministic | PASS | Concurrency-Tests grün (4 Tests) |
| 3_tests | C6 | warn,deterministic | SKIP | kein a11y/axe-Setup |
| 4_sovereignty_dsgvo | E1 | block,deterministic | PASS | kein Non-EU-Endpunkt/Region referenziert |
| 4_sovereignty_dsgvo | E2 | block,deterministic | PASS | keine Klartext-PII in Logs/Prompts/Outputs |
| 4_sovereignty_dsgvo | E3 | block,deterministic | SKIP | kein Audit-Log (nicht anwendbar) |
| 4_sovereignty_dsgvo | E4 | block,deterministic | SKIP | kein Audit-Log (nicht anwendbar) |
| 4_sovereignty_dsgvo | E5 | block,deterministic | SKIP | kein Privacy-Kontext (nicht anwendbar) |
| 4_sovereignty_dsgvo | E6 | block,deterministic | SKIP | kein Privacy-Kontext (nicht anwendbar) |
| 4_sovereignty_dsgvo | E7 | warn,deterministic | SKIP | kein Privacy-Kontext (nicht anwendbar) |
| 4_sovereignty_dsgvo | E8 | warn,llm | SKIP | kein Privacy-Kontext (nicht anwendbar) |
| 5_integrity | F1 | block,deterministic,★pflicht | PASS | kein 'latest' — Modelle gepinnt |
| 5_integrity | F2 | block,deterministic | SKIP | kein Modell gepinnt |
| 5_integrity | F3 | warn,deterministic | SKIP | kein Snapshot-Verzeichnis |
| 6_perf | G1 | warn,deterministic | SKIP | kein Lasttest konfiguriert |
| 6_perf | G2 | warn,deterministic | SKIP | kein Build-Output (dist/ oder build/) |
| 6_perf | G3 | warn,deterministic | WARN | 14 Query-in-Loop-Verdacht (N+1) |
| 7_maintainability | H1 | warn,deterministic | PASS | alle TODO/FIXME getrackt (oder keine) |
| 7_maintainability | H2 | warn,deterministic | WARN | 5 Funktion(en) ueber Komplexitaet 12 |
| 7_maintainability | H3 | warn,deterministic | WARN | README enthaelt 5 Platzhalter |
| 7_maintainability | H4 | block,deterministic,★pflicht | PASS | CHANGELOG vorhanden, 32 Einträge, newest-top |
| 7_maintainability | H5 | warn,deterministic | SKIP | keine TASKS.md (nicht anwendbar) |
| 7_maintainability | H6 | block,llm | SKIP | kein BMAD-QA-Nachweis (.werkbank/qa-evidence.json) |
| 8_judgement | I1 | block,llm | SKIP | kein BMAD-QA-Nachweis (.werkbank/qa-evidence.json) |
| 8_judgement | I2 | block,llm | SKIP | kein BMAD-QA-Nachweis (.werkbank/qa-evidence.json) |
| 8_judgement | I3 | block,llm | SKIP | kein BMAD-QA-Nachweis (.werkbank/qa-evidence.json) |

## Funde (redigiert — keine Klartext-Secrets/PII)
- **G3** — WARN — 14 Query-in-Loop-Verdacht (N+1)
    - `gates/runner.py:140` [n+1-query] {'meta': 'meta', 'stages': 'stages', 'branch_mod…{'meta': 'meta', 'stages': 'stages', 'branch_modules': 'branch'}.get
    - `gates/runner.py:270` [n+1-query] ****************************
    - `gates/verdict.py:113` [n+1-query] ***********
    - `gates/verdict.py:114` [n+1-query] *****
    - `gates/verdict.py:118` [n+1-query] *************
    - `gates/verdict.py:123` [n+1-query] *****
    - `gates/verdict.py:124` [n+1-query] *****
    - `ralph/stop_hook.py:39` [n+1-query] ******
    - `ralph/stop_hook.py:40` [n+1-query] ******
    - `ralph/stop_hook.py:40` [n+1-query] ******
    - `feedback/feedback.py:184` [n+1-query] *****
    - `feedback/feedback.py:188` [n+1-query] *****
    - `golden-projects/04-upload-pii-redaction/app/pii_redactor.py:110` [n+1-query] ***************
    - `golden-projects/02-kontaktformular-dsar/app/contact_service.py:101` [n+1-query] *******
- **H2** — WARN — 5 Funktion(en) ueber Komplexitaet 12
    - `gates/runner.py:130` [complexity] load_gates() = 16
    - `gates/runner.py:238` [complexity] _write_report() = 19
    - `gates/verdict.py:37` [complexity] load_pflichtenheft() = 16
    - `feedback/feedback.py:196` [complexity] main() = 13
    - `golden-projects/04-upload-pii-redaction/app/pii_redactor.py:75` [complexity] _collect() = 13
- **H3** — WARN — README enthaelt 5 Platzhalter
    - `README.md:22` [docs-placeholder] `curl … | bash` führt fremden Co…`curl … | bash` führt fremden Code ungeprüft aus. Ehrlich: für Wegwerf-/Testsysteme ist die Pipe oben in Ordnung.
    - `README.md:33` [docs-placeholder] `WERKBANK_EXPECT_SHA=<commit>`: …`WERKBANK_EXPECT_SHA=<commit>`: weicht der ausgecheckte Commit ab, bricht der Installer ab.
    - `README.md:34` [docs-placeholder] Der Installer gibt den aufgelöst…Der Installer gibt den aufgelösten Commit aus (`▶ WERKBANK @ <sha> (ref=<ref>)`) — du siehst genau, was installiert wurde.
    - `README.md:75` [docs-placeholder] | `make cover` | `coverage run ……| `make cover` | `coverage run … && coverage report` |
    - `README.md:105` [docs-placeholder] | `privacy/DSGVO-ARTEFAKTE.md` |…| `privacy/DSGVO-ARTEFAKTE.md` | DSGVO-Vorlagen (Art. 6/25/28/30/32/35 …) |

## Block-Regel
Mind. 1 Block-Gate rot ⇒ kein Push, kein Abhaken. E-Gate rot ⇒ STOPP + Mensch.
