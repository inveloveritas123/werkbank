# WERKBANK — SCORING-MATRIX (objektives Soll-Ist)

> Der Agent darf NICHT sagen „ich bin besser geworden". Er darf nur **messen**:
> `Vorher 72 → Nachher 81 · keine Regression · alle Block-Gates grün · Kosten im Limit`.
> Pro Golden-Project-Lauf ausfüllen und nach `.werkbank/BENCHMARK.md` schreiben (append, neuster oben).

## 100-Punkte-Matrix (pro Lauf)
| Bereich | Punkte | Messung |
|---|---:|---|
| Funktion erfüllt (Akzeptanzkriterien) | 20 | aus SPEC, deterministisch geprüft |
| Tests grün | 15 | Unit/Integration |
| E2E-Flow läuft | 10 | Playwright Kernflows |
| Security-Gates grün | 15 | D1–D3 + SECURITY_SEEDS gefangen |
| DSGVO-Artefakte vollständig | 15 | EXPECTED_OUTPUTS vorhanden + Pflichtfelder |
| Keine PII in Logs/Prompts/Reports | 10 | Gate E2 |
| Resume/State funktioniert | 5 | Abbruch simuliert, Wiederaufnahme ok |
| Kosten/Laufzeit im Limit | 5 | Tokens, €, Laufzeit, Tier-Verteilung |
| Doku/Changelog sauber | 5 | CHANGELOG-Eintrag, README aktuell |
| **Gesamt** | **100** | |

## Produktiv-Schwelle (ein Lauf zählt erst als „grün", wenn ALLES gilt)
```
Score >= 85
0 Block-Gates rot
0 Secrets
0 kritische Security-Funde
0 kritische DSGVO-Funde
keine Regression ggü. früheren Golden Projects
```

## Die 5 Ebenen (warum das Selbstverbesserung erst möglich macht)
1. **Orakel** — Spec + Akzeptanz + Unit/Integration/E2E + Security-Gates + DSGVO-Gates + Benchmark-Scores + Regression gegen frühere Runs. Ohne Orakel keine Selbstverbesserung.
2. **Standardisierte Prüfprojekte** — die Golden Projects (immer wieder dieselben, nicht jedes Mal neue kreative Aufgaben).
3. **Bewertungsmatrix** — diese 100 Punkte.
4. **Kontrollierte Selbstverbesserung** — nur kleine, erlaubte Änderungen (siehe `SELF-IMPROVEMENT.md`).
5. **Produktivfreigabe** — Mindestkriterien aus `BACKLOG.md` (Reifegrad-Tor) + Human-Merge.

## Regressions-Regel
Jede Verbesserung läuft gegen **alle bisher grünen** Golden Projects erneut. Sinkt dort ein Score
oder wird ein Gate rot → **zurückrollen**. „Keine Verbesserung ohne messbaren Effekt **und** ohne Regression."
