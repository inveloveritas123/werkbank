# WERKBANK — BENCHMARK (PDCA-Messwerte je Lauf)

> Append, neuster Eintrag oben. Der Agent darf nicht „besser geworden" behaupten — nur messen.
> Volle 100-Punkte-Matrix (SCORING-MATRIX.md) ab Golden-Project-Läufen (T2+). T1 = Infrastruktur:
> gemessen an Testabdeckung der Checks + Repo-Gate-Lauf.

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
