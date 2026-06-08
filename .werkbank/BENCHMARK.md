# WERKBANK — BENCHMARK (PDCA-Messwerte je Lauf)

> Append, neuster Eintrag oben. Der Agent darf nicht „besser geworden" behaupten — nur messen.
> Volle 100-Punkte-Matrix (SCORING-MATRIX.md) ab Golden-Project-Läufen (T2+). T1 = Infrastruktur:
> gemessen an Testabdeckung der Checks + Repo-Gate-Lauf.

## 2026-06-08 — T7 · Golden Project 05 (Breach/Incident-Runbook) · Score 98/100
**Lauf:** Generator erzeugt aus einem Vorfall 4 Dokumente (BREACH-RUNBOOK, INCIDENT-TIMELINE,
NOTIFICATION-CHECKLIST, LESSONS-LEARNED) + deterministischer „Fake-Rechtsaussagen"-Linter.
GP05-GATE-REPORT grün (E1/E2/D3/E5).

**Soll-Ist (SPEC, alle grün):** 72h-Prüfung ✓ · Datenarten genannt ✓ · Meldeentscheidung begründet ✓ ·
Maßnahmenliste ✓ · KEINE Fake-Rechtsaussagen ✓.

**100-Punkte-Matrix:**
| Bereich | Pkt | Erreicht | Messung |
|---|---:|---:|---|
| Funktion erfüllt (5 Soll-Ist) | 20 | 20 | alle grün |
| Tests grün | 15 | 15 | 76/76 (GP05 13 inkl. Bald-Claim-Härtung) |
| E2E-Flow | 10 | 9 | `demo.py` läuft; Doku-Generator (−1) |
| Security/Korrektheit-Gates | 15 | 15 | Linter + Negativtest + Review-Gate (GDPR-Korrektheit PASS) |
| DSGVO-Artefakte vollständig | 15 | 15 | 4/4 E5 PASS |
| Keine PII | 10 | 10 | E2 PASS, keine PII in Dokumenten |
| Resume/State | 5 | 4 | deterministische Generierung reproduzierbar (−1 kein persistenter State) |
| Kosten/Laufzeit | 5 | 5 | stdlib, 0 LLM |
| Doku/Changelog | 5 | 5 | README+Artefakte+CHANGELOG |
| **Gesamt** | **100** | **98** | **≥ 85 ✓** |

**Produktiv-Schwelle:** 98 ≥ 85 · 0 Block rot · 0 Secrets · 0 PII · **Regression GP01–04 GRUEN**.

**Review-Gate (inhaltliche Korrektheit):** Unabhängiger Reviewer bestätigte GDPR-Korrektheit
(72h ab Erkennung Art. 33(1); Art. 33 Behörde/„Risiko" vs. Art. 34 Betroffene/„hohes Risiko" korrekt;
keine rechtlich falsche Aussage). **ACT:** Linter-Lücke gefunden & gefixt (RED→GREEN) — er übersah
KAHLE unhedged Aussagen („nicht meldepflichtig", „nicht erforderlich", „auf der sicheren Seite");
jetzt hedge-bewusst (flaggt nur ohne Bedingungswörter). +3 Tests, inkl. bislang ungetestetem
high_risk=False-Zweig. Generierte Dokumente bleiben sauber. Keine Regression.

## 2026-06-08 — T6 · Golden Project 04 (Upload PII-Redaction) · Score 98/100
**Lauf:** Upload-Dienst mit PII-Erkennung & Redaction (`pii_redactor.py` + `upload_service.py`) +
Demo + DATA-FLOW. E2 ist hier HART. GP04-GATE-REPORT grün (E1/E2/D3/E5).

**Soll-Ist (SPEC, alle grün):** PII erkannt ✓ · im Report maskiert ✓ · keine PII im Log ✓ ·
keine PII im Prompt-Dump ✓ (Platzhalter) · Datei-Löschung ✓.

**100-Punkte-Matrix:**
| Bereich | Pkt | Erreicht | Messung |
|---|---:|---:|---|
| Funktion erfüllt (5 Soll-Ist) | 20 | 20 | alle grün |
| Tests grün | 15 | 15 | 63/63 (GP04 6 + T6-Härtung 3) |
| E2E-Flow | 10 | 9 | `demo.py` läuft; kein Browser (−1) |
| Security-Gates grün | 15 | 15 | D3 + E2 hart (Redaction unabhängig per E2 verifiziert) |
| DSGVO-Artefakte vollständig | 15 | 15 | DATA-FLOW E5 PASS |
| Keine PII (Logs/Prompts/Reports) | 10 | 10 | E2 PASS auf echten Outputs (Evidence) |
| Resume/State | 5 | 4 | Datei-Persistenz; nicht separat getestet (−1) |
| Kosten/Laufzeit | 5 | 5 | stdlib, 0 LLM |
| Doku/Changelog | 5 | 5 | README+DATA-FLOW+CHANGELOG |
| **Gesamt** | **100** | **98** | **≥ 85 ✓** |

**Produktiv-Schwelle:** 98 ≥ 85 · 0 Block rot · 0 Secrets · 0 PII · **Regression GP01–03 GRUEN**.

**ACT/Paar-Review (Reviewer ≠ Implementer) — kritische False-Negatives gefunden & gefixt (RED→GREEN):**
Für ein Redaction-Tool sind verpasste PII das Kernrisiko. Behoben in **Redactor UND E2** (Defense-in-Depth):
(1) Telefon `+49 (0)151 …` rutschte durch → `(0)` im Muster erlaubt; (2) Namen ohne Anrede
(„Mit freundlichen Grüßen, Anna Schmidt", „Mein Name ist …") leckten → Grußformel-/Selbstnennungs-Heuristik,
**und E2 erkennt jetzt Namen** (vorher gar nicht — „falsches Grün"); (3) Auslands-IBAN (AT…) → IBAN beliebiges
Land mit mod-97. Adversariales Korpus-Testset prüft, dass der Prompt-Dump per UNABHÄNGIGEM E2-Scan sauber ist.
**Cross-cutting:** E2 wurde damit für ALLE Golden Projects breiter; FP-frei (GP01–04 + Repo grün). Keine Regression.

## 2026-06-08 — T5 · Golden Project 03 (Mini-CRM Mandantentrennung) · Score 98/100
**Lauf:** Multi-Tenant Mini-CRM (stdlib) + Demo + TOMs. Zwei neue Gate-Checks: **E3**
(Tenant-Isolation aus Audit-Log) und **E4** (Audit-Log schema-konform). GP03-GATE-REPORT grün.

**Soll-Ist (SPEC, alle grün):** A liest A ✓ · A liest B NICHT ✓ · B liest B ✓ · B liest A NICHT ✓ ·
manipulierte tenant_id schlägt fehl ✓ · Audit-Log ohne unnötige PII ✓.

**100-Punkte-Matrix:**
| Bereich | Pkt | Erreicht | Messung |
|---|---:|---:|---|
| Funktion erfüllt (Soll-Ist) | 20 | 20 | alle Checks grün |
| Tests grün | 15 | 15 | 54/54 (GP03: 13 inkl. Gate-Härtung + forge) |
| E2E-Flow | 10 | 9 | `demo.py` läuft end-to-end; kein Browser (−1) |
| Security-Gates grün | 15 | 15 | D3 + E3 (Isolation) + Cross-Tenant-Negativtest + gehärtete E3/E4 |
| DSGVO-Artefakte vollständig | 15 | 15 | TOMs E5 PASS |
| Keine PII (Logs/Audit) | 10 | 10 | E2 PASS; Audit-Log nur IDs/Mandant/Event |
| Resume/State | 5 | 4 | Datenspeicher persistent (wie GP02); für GP03 nicht separat getestet (−1) |
| Kosten/Laufzeit | 5 | 5 | stdlib, 0 LLM |
| Doku/Changelog | 5 | 5 | README+TOMs+CHANGELOG |
| **Gesamt** | **100** | **98** | **≥ 85 ✓** |

**Produktiv-Schwelle:** 98 ≥ 85 · 0 Block rot · 0 Secrets · 0 PII · **Regression GP01–02 GRUEN**.

**Neue Gates:** E3 prüft das Audit-Log auf Tenant-übergreifende ERFOLGE (denied-Versuche erlaubt);
E4 validiert jede Zeile gegen `templates/AUDIT-LOG.schema.json`. Runner-Flags `--audit-log`/`--audit-schema`.

**ACT/Paar-Review (Reviewer ≠ Implementer):** App selbst leckfrei. Aber 2 Härtungs-Bugs in den
**Gates** gefunden & gefixt (RED→GREEN): (1) E3-Regex verlangte `/` nach Mandant und nahm `*`/`unknown`
aus → verkürzte Ressource/Wildcard hätten ein Cross-Tenant-Leck durchgelassen; jetzt jeder Cross-Tenant-
Erfolg fängt. (2) E4 prüfte keine Typen → `pii_present:0` / falsche Typen rutschten durch; jetzt strikte
Typprüfung (boolean ≠ 0/1). +6 Tests. Keine Regression.

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
