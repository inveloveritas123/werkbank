# GATE-REPORT — target=`.` — 2026-06-08T22:23:27Z

## Zusammenfassung
- **Ergebnis:** GRUEN
- **Block-Gates rot:** 0
- **Warn-Gates:** 0
- **Gates ohne Check (offen, SKIP):** 32

## Detail je Stufe
| Stufe | Gate | Flags | Ergebnis | Notiz |
|---|---|---|---|---|
| 1_spec | A1 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A2 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A3 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A4 | warn,llm | SKIP | kein Check implementiert (offen) |
| 2_static | B1 | block,deterministic | SKIP | ruff nicht installiert |
| 2_static | B2 | block,deterministic | SKIP | mypy nicht installiert |
| 2_static | B3 | block,deterministic | PASS | Build/Compile sauber (21 .py) |
| 2_static | D1 | block,deterministic | SKIP | kein Check implementiert (offen) |
| 2_static | D2 | block,deterministic | SKIP | kein Check implementiert (offen) |
| 2_static | D3 | block,deterministic | PASS | kein Secret gefunden |
| 2_static | D4 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 3_tests | C1 | block,deterministic | PASS | Tests grün (147 Tests in gates/checks/tests) |
| 3_tests | C2 | block,deterministic | SKIP | coverage nicht installiert |
| 3_tests | C3 | block,deterministic | SKIP | kein Check implementiert (offen) |
| 3_tests | C4 | block,deterministic | SKIP | kein Check implementiert (offen) |
| 3_tests | C5 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 3_tests | C6 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 4_sovereignty_dsgvo | E1 | block,deterministic | PASS | kein Non-EU-Endpunkt/Region referenziert |
| 4_sovereignty_dsgvo | E2 | block,deterministic | PASS | keine Klartext-PII in Logs/Prompts/Outputs |
| 4_sovereignty_dsgvo | E3 | block,deterministic | SKIP | kein Audit-Log (nicht anwendbar) |
| 4_sovereignty_dsgvo | E4 | block,deterministic | SKIP | kein Audit-Log (nicht anwendbar) |
| 4_sovereignty_dsgvo | E5 | block,deterministic | SKIP | kein Privacy-Kontext (nicht anwendbar) |
| 4_sovereignty_dsgvo | E6 | block,deterministic | SKIP | kein Privacy-Kontext (nicht anwendbar) |
| 4_sovereignty_dsgvo | E7 | warn,deterministic | SKIP | kein Privacy-Kontext (nicht anwendbar) |
| 4_sovereignty_dsgvo | E8 | warn,llm | SKIP | kein Check implementiert (offen) |
| 5_integrity | F1 | block,deterministic | PASS | kein 'latest' — Modelle gepinnt |
| 5_integrity | F2 | block,deterministic | SKIP | kein Check implementiert (offen) |
| 5_integrity | F3 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 6_perf | G1 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 6_perf | G2 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 6_perf | G3 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 7_maintainability | H1 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 7_maintainability | H2 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 7_maintainability | H3 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 7_maintainability | H4 | block,deterministic | PASS | CHANGELOG vorhanden, 21 Einträge, newest-top |
| 7_maintainability | H6 | block,llm | SKIP | kein Check implementiert (offen) |
| 8_judgement | I1 | block,llm | SKIP | kein Check implementiert (offen) |
| 8_judgement | I2 | block,llm | SKIP | kein Check implementiert (offen) |
| 8_judgement | I3 | block,llm | SKIP | kein Check implementiert (offen) |

## Block-Regel
Mind. 1 Block-Gate rot ⇒ kein Push, kein Abhaken. E-Gate rot ⇒ STOPP + Mensch.
