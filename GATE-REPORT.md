# GATE-REPORT — target=`.` — 2026-06-11T05:38:30Z

## Zusammenfassung
- **Ergebnis:** GRUEN
- **Profil (Pflichtenheft):** `werkbank_self` — WERKBANK-Repo selbst — volle statische Pflicht ohne Projekt-/Privacy-Kontext
- **Pflicht-Gates bestanden:** 9/9
- **Pflicht-Gates VERLETZT (FAIL):** 0
- **Pflicht-Gates UNGEDECKT (nicht geprueft):** 0
- **Pflicht-Gates ohne PASS:** 0
- **Optionale Befunde (warn):** 0

> **Hartes Gruen:** GRUEN gilt NUR, wenn alle 9 Pflicht-Gates aktiv bestanden sind. SKIP eines Pflicht-Gates (Tool fehlt / kein Check / kein Kontext) ⇒ UNGEDECKT ⇒ ROT.

## Detail je Stufe (Flags ★pflicht = Pflicht-Gate dieses Profils)
| Stufe | Gate | Flags | Ergebnis | Notiz |
|---|---|---|---|---|
| 1_spec | A1 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A2 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A3 | block,deterministic | SKIP | kein SPEC (nicht anwendbar) |
| 1_spec | A4 | warn,llm | SKIP | kein Check implementiert (offen) |
| 2_static | B1 | block,deterministic,★pflicht | PASS | ruff sauber |
| 2_static | B2 | block,deterministic,★pflicht | PASS | mypy sauber |
| 2_static | B3 | block,deterministic,★pflicht | PASS | Build/Compile sauber (29 .py) |
| 2_static | D1 | block,deterministic,★pflicht | PASS | kein High/Medium (45 Low, beraten) |
| 2_static | D2 | block,deterministic | SKIP | kein Check implementiert (offen) |
| 2_static | D3 | block,deterministic,★pflicht | PASS | kein Secret gefunden |
| 2_static | D4 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 3_tests | C1 | block,deterministic,★pflicht | PASS | Tests grün (217 Tests in gates/checks/tests) |
| 3_tests | C2 | block,deterministic,★pflicht | PASS | Coverage 86% >= 70% |
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
| 4_sovereignty_dsgvo | E8 | warn,llm | SKIP | kein Privacy-Kontext (nicht anwendbar) |
| 5_integrity | F1 | block,deterministic,★pflicht | PASS | kein 'latest' — Modelle gepinnt |
| 5_integrity | F2 | block,deterministic | SKIP | kein Check implementiert (offen) |
| 5_integrity | F3 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 6_perf | G1 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 6_perf | G2 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 6_perf | G3 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 7_maintainability | H1 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 7_maintainability | H2 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 7_maintainability | H3 | warn,deterministic | SKIP | kein Check implementiert (offen) |
| 7_maintainability | H4 | block,deterministic,★pflicht | PASS | CHANGELOG vorhanden, 29 Einträge, newest-top |
| 7_maintainability | H6 | block,llm | SKIP | kein Check implementiert (offen) |
| 8_judgement | I1 | block,llm | SKIP | kein Check implementiert (offen) |
| 8_judgement | I2 | block,llm | SKIP | kein Check implementiert (offen) |
| 8_judgement | I3 | block,llm | SKIP | kein Check implementiert (offen) |

## Block-Regel
Mind. 1 Block-Gate rot ⇒ kein Push, kein Abhaken. E-Gate rot ⇒ STOPP + Mensch.
