# WERKBANK — BENCHMARK (PDCA-Messwerte je Lauf)

> Append, neuster Eintrag oben. Der Agent darf nicht „besser geworden" behaupten — nur messen.
> Volle 100-Punkte-Matrix (SCORING-MATRIX.md) ab Golden-Project-Läufen (T2+). T1 = Infrastruktur:
> gemessen an Testabdeckung der Checks + Repo-Gate-Lauf.

## 2026-06-08 — T4 · Golden Project 02 (Kontaktformular DSAR) · Score 99/100
**Lauf:** Erstes Golden Project mit echtem Code. App `app/contact_service.py` (stdlib) +
Demo + 3 DSGVO-Artefakte. Gegen E1/E2/D3/E5 gemessen, GP02-GATE-REPORT grün.

**Soll-Ist (SPEC.md, alle grün):** Kontakt speichern ✓ · Export eigener Datensatz ✓ · Löschung ✓ ·
Fremdzugriff blockiert ✓ · keine PII im Log ✓ (E2 PASS) · Retention-Job ✓.

**100-Punkte-Matrix:**
| Bereich | Pkt | Erreicht | Messung |
|---|---:|---:|---|
| Funktion erfüllt (6 Soll-Ist) | 20 | 20 | alle 6 Checks grün |
| Tests grün | 15 | 15 | 41/41 (GP02: 11 inkl. Hardening + Persistenz) |
| E2E-Flow | 10 | 9 | `demo.py` läuft end-to-end; kein Browser-Playwright (−1) |
| Security-Gates grün | 15 | 15 | D3 PASS + fail-closed Zugriffskontrolle + Fremdzugriff-Block |
| DSGVO-Artefakte vollständig | 15 | 15 | 3/3 (E5 PASS), Restrisiko ehrlich dokumentiert |
| Keine PII in Logs/Prompts/Reports | 10 | 10 | E2 PASS, Log-Inhalt verifiziert |
| Resume/State | 5 | 5 | Persistenz getestet (Neustart lädt Daten) |
| Kosten/Laufzeit | 5 | 5 | stdlib, 0 LLM, <1 s |
| Doku/Changelog | 5 | 5 | README+Artefakte+CHANGELOG |
| **Gesamt** | **100** | **99** | **≥ 85 ✓** |

**Produktiv-Schwelle:** 99 ≥ 85 · 0 Block rot · 0 Secrets · 0 kritische DSGVO-Funde · **Regression GP01 GRUEN**.

**ACT/Paar-Review (Reviewer ≠ Implementer):** fand 2 echte Bugs in sicherheitskritischem Code →
behoben (RED→GREEN): (1) `_authorized_record` warf KeyError statt AccessDenied bei fehlendem
token_hash → jetzt fail-closed; (2) `purge_expired` crashte bei naive/aware-datetime → UTC-Normalisierung
(sonst würde der Retention-Job werfen und PII nie löschen, Art. 17). +3 Tests. Plus Anti-Overclaim:
Klartext-PII at-rest im DATA-FLOW als Restrisiko dokumentiert. Keine Regression.

## 2026-06-08 — T3 · PDCA-Zyklus 1 · E2-Telefonerkennung (DE-Nationalformate)
**Plan:** Höchster offener Hebel aus der Lernpunkt-Historie: E2 fing nur `+49`; deutsche
Nationalformate (`0151…`, `0351-…`) und `0049` fehlten → hohes False-Negative-Risiko für ein
DE-DSGVO-Tool. Erlaubt nach SELF-IMPROVEMENT.md: „Regex/Heuristik eines PII-Scans verbessern".

**Metrik (Telefon-Format-Abdeckung, 5 repräsentative Formate):**
| | Vorher | Nachher |
|---|---:|---:|
| `+49 151 23456789` (intl) | ✅ | ✅ |
| `+4915123456789` (intl kompakt) | ✅ | ✅ |
| `0151 23456789` (national mobil) | ❌ | ✅ |
| `0351-1234567` (national fest) | ❌ | ✅ |
| `0049 151 23456789` (intl alt) | ❌ | ✅ |
| **Catch-Rate** | **2/5** | **5/5** |

**Check/Act:** National-Muster verlangt einen Trenner nach der Vorwahl → False-Positive-Schutz
gegen Log-Zahlen (`status=200`, `id=req-001`, Zeitstempel, IBAN-Fragmente). 2 neue Tests (Coverage + FP).
**Regression:** Tests 30/30 grün · **GP01 bleibt GRUEN** (E2/E5 PASS, Seeds 3/3) · Repo-Self-Lauf GRUEN.
→ **besser (2/5→5/5) + keine Regression + Block-Gates grün → übernommen.**
**Stop-Kriterium:** weitere Lernpunkte (D3 JWT/Stripe) für künftige Zyklen vermerkt — ein
gemessener, regressionsfreier Zyklus erfüllt T3; kein endloses Wühlen.

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
