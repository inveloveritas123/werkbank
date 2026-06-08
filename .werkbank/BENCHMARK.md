# WERKBANK — BENCHMARK (PDCA-Messwerte je Lauf)

> Append, neuster Eintrag oben. Der Agent darf nicht „besser geworden" behaupten — nur messen.
> Volle 100-Punkte-Matrix (SCORING-MATRIX.md) ab Golden-Project-Läufen (T2+). T1 = Infrastruktur:
> gemessen an Testabdeckung der Checks + Repo-Gate-Lauf.

## 2026-06-08 — T2 · Golden Project 01 (DSGVO-Projektstarter) · Score 97/100
**Lauf:** Artefakte erzeugt (7 DSGVO-Artefakte + INPUT + GATE-REPORT), gegen E1/E2/D3/E5 gemessen.
Neuer Check **E5** (Artefakt-Vollständigkeit) implementiert.

**100-Punkte-Matrix (SCORING-MATRIX.md, GP01-SCORING.md):**
| Bereich | Pkt | Erreicht | Messung |
|---|---:|---:|---|
| Funktion erfüllt (EXPECTED_OUTPUTS vollständig, keine Platzhalter) | 20 | 20 | E5 PASS, 7/7 + GATE-REPORT |
| Tests grün | 15 | 15 | 28/28 unit/integration |
| E2E-Flow / Ersatz: Generierungs-Lauf reproduzierbar | 10 | 8 | Lauf 2× identisch; kein echtes UI-E2E (−2) |
| Security-Gates grün (D3 + SECURITY_SEEDS) | 15 | 15 | D3 PASS + **Catch-Rate 3/3** |
| DSGVO-Artefakte vollständig | 15 | 15 | 7/7 gefüllt, EU, Review-bestätigt konsistent |
| Keine PII in Logs/Prompts/Reports | 10 | 10 | E2 PASS, Report redigiert |
| Resume/State | 5 | 4 | STATE crash-sicher + deterministischer Re-run; kein Abbruch-Sim-Harness (−1) |
| Kosten/Laufzeit | 5 | 5 | Gates deterministisch, 0 LLM-Kosten, <1 s |
| Doku/Changelog | 5 | 5 | CHANGELOG+BENCHMARK+STATE+INPUT+Artefakte |
| **Gesamt** | **100** | **97** | **≥ 85 ✓** |

**Produktiv-Schwelle:** Score 97 ≥ 85 · 0 Block-Gates rot · 0 Secrets · 0 kritische DSGVO-Funde · keine Regression. **grün.**

**ACT-1 (E5 härten, erlaubt: Heuristik verbessern):** Paar-Review fand E5-False-Negatives
(Klartext-Platzhalter `____`/`[bitte ausfüllen]`, Prosa-Non-EU `USA`/`Drittland: ja`) und einen
False-Positive (Angle-Regex auf `<mail@x>`/`<->`). Behoben + 6 Tests. Artefakte bleiben grün → übernommen.
**ACT-2 (Artefakt-Ehrlichkeit):** Review-Befund Überzeichnung — TOMs-Status als Selbsteinschätzung
gekennzeichnet, Subprozessoren präzisiert (Sinch AB/Schweden statt vager „EU-Infrastruktur"). Keine Regression.
**Regression GP:** keine früheren grünen Golden Projects (GP01 ist das erste).

## 2026-06-08 — T1 ACT-1 · E1 Non-EU-Marker erweitert
- **Hebel:** Paar-Review (Reviewer ≠ Implementer) fand: E1 (Moat-Gate) übersah Azure-US-Regionen
  (`eastus`, `westus2`) und US-Cross-Region-Model-IDs (`us.anthropic.*`). Eine reale Config-Zeile
  hätte das Gate ausgehebelt (False Negative).
- **Vorher:** 16 Tests grün; E1 fängt AWS-US/GCP-non-EU/openai.com. Evasion `eastus`/`us.anthropic.*` → PASS (Lücke).
- **Erlaubt nach SELF-IMPROVEMENT.md:** „Regex/Heuristik eines Scans verbessern" + „fehlenden Testfall ergänzen".
- **Nachher:** 19/19 Tests grün (3 neue: azure-us-region, us-cross-region-model, eu-bleibt-clean).
  E1 fängt jetzt zusätzlich `eastus`/`westus2`-Azure-Regionen und `us.anthropic.*`-Model-IDs.
  Repo-Self-Lauf GRUEN, 0 Block-Gates rot. **Keine Regression.** → übernommen.
- **Nebenbefund (Self-Lauf):** Scanner flaggte seine eigene Signaturliste. Behoben: Runner schließt
  das Gate-Tooling-Verzeichnis automatisch aus, wenn es unter dem Scan-Ziel liegt (nicht bei echten Zielen).
- **Offene Lernpunkte für T3 (nicht in dieser Runde — kein endloses Wühlen):**
  - E2-Telefon nur `+49`; deutsche Nationalformate (`0151…`, `0049…`) fehlen → False-Negative-Risiko (hoch für DE-Tool).
  - D3 ohne JWT-/Stripe-(`sk_live_`)-/Hex-ohne-Keyword-Muster.
  - `test_runner_blocks_on_planted_secret` prüft nicht explizit, dass spätere Stufen durch fail-fast übersprungen werden.

## 2026-06-08 — T1 Baseline · Gate-Runner + E1/D3/E2
- Runner liest gates.yaml (38 Gates über 8 Stufen), gestaffelt, fail-fast, schreibt GATE-REPORT.md.
- Implementiert: E1 (EU-Routing), E2 (PII), D3 (Secret, gitleaks+Built-in). Rest: SKIP (ehrlich).
- **Tests:** 16/16 grün (Positiv clean-Fixture + Negativ je Verstoß zur Laufzeit synthetisiert).
- **Repo-Gate-Lauf:** GRUEN, 0 Block-Gates rot, 0 Secrets, 0 PII. E1/E2/D3 = PASS.
