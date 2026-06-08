# WERKBANK — DSGVO-Artefakte (Vorlagen)

> Ausfüllbare Vorlagen, die WERKBANK von „EU-Routing" zu echter DSGVO-Substanz heben.
> Pro Projekt ausfüllen; Gate **E5** prüft Vorhandensein, **E6** erzwingt DSFA bei hohem Risiko.
> **Kein Rechtsrat** — fachliche Prüfung durch Carsten [Anwalt/DSB] / DSB. Vorlagen, kein Ersatz für Beratung.

---

## DATA-FLOW.md — Datenflussdiagramm (Grundlage für alles)
- **Datenarten:** [welche personenbezogenen Daten? Kategorien nach Art. 9 (besondere Kategorien)?]
- **Quellen → Verarbeitung → Senken:** [Eingang | Verarbeitungsschritte | Speicherorte | Ausgänge]
- **Beteiligte Systeme:** [App, DB, LLM-Endpunkt(e), Logs, Backups, Drittdienste]
- **Wo verlässt etwas die EU?** [jeden Punkt markieren → THIRD-COUNTRY-TRANSFERS]
- **Wo entsteht PII in Prompts/Logs?** [→ TOMs Maßnahme „PII-Minimierung", Gate E2]

## PROCESSING-REGISTER.md — Verzeichnis von Verarbeitungstätigkeiten (Art. 30)
| Feld | Inhalt |
|---|---|
| Verantwortlicher | [Firma, Anschrift, Vertretung] |
| DSB / Kontakt | [Name oder „kein DSB bestellt, da …"] |
| Zweck der Verarbeitung | [konkret] |
| Kategorien betroffener Personen | [Kunden, Mitarbeiter, …] |
| Kategorien personenbezogener Daten | [Stammdaten, Nutzungsdaten, …] |
| Empfänger | [intern/extern, Auftragsverarbeiter] |
| Drittlandübermittlung | [ja/nein → Kap. V] |
| Löschfristen | [→ RETENTION-DELETION] |
| TOMs (Verweis) | [→ TOMs.md] |

## LAWFUL-BASIS.md — Rechtsgrundlage (Art. 6)
- **Gewählte Grundlage:** [a) Einwilligung · b) Vertrag · c) rechtl. Pflicht · f) berechtigtes Interesse]
- **Begründung:** [warum tragfähig]
- **Bei f) — Interessenabwägung:** [Zweck vs. Betroffenenrechte, Ergebnis]
- **Bei a) — Einwilligung:** [wie eingeholt, wie widerrufbar, Nachweis]

## DPIA-SCREENING.md — Schwellwertprüfung (Art. 35 Abs. 1)
Hohe-Risiko-Indikatoren (ankreuzen):
- [ ] Systematische umfangreiche Bewertung / Profiling
- [ ] Verarbeitung besonderer Kategorien (Art. 9) in großem Umfang
- [ ] Systematische Überwachung öffentlich zugänglicher Bereiche
- [ ] Neue Technologie / KI mit unklaren Risiken
- [ ] Automatisierte Entscheidungen mit Rechtswirkung
**Ergebnis:** [≥1 angekreuzt → DSFA (DPIA.md) Pflicht; sonst dokumentierte Verneinung]

## DPIA.md — Datenschutz-Folgenabschätzung (Art. 35) — nur falls Screening positiv
- **Systematische Beschreibung** der Verarbeitung [+ Verweis DATA-FLOW]
- **Notwendigkeit & Verhältnismäßigkeit** [Datenminimierung Art. 25]
- **Risiken für Betroffene** [Eintritt × Schwere, je Risiko]
- **Abhilfemaßnahmen** [→ TOMs, Restrisiko]
- **Konsultation DSB / ggf. Aufsichtsbehörde (Art. 36)** [Ergebnis]

## TOMs.md — Technische & organisatorische Maßnahmen (Art. 32)
| Bereich | Maßnahme (Soll) | Status |
|---|---|---|
| Vertraulichkeit | Zugriffskontrolle, Rollen/Capability-Modell, Mandantentrennung | [ ] |
| Integrität | Audit-Log (unveränderlich), Vier-Augen-Gate für AI-Code | [ ] |
| Verfügbarkeit | Backup, DR/Break-Glass, Kill-Switch | [ ] |
| Belastbarkeit | Last-/Concurrency-Tests | [ ] |
| Verschlüsselung | Transit (TLS), at-rest | [ ] |
| Pseudonym./Minimierung | PII-Minimierung in Prompts/Logs (Gate E2) | [ ] |
| EU-Datenresidenz | nur EU-Endpunkte (Gate E1) | [ ] |
| Wiederherstellbarkeit | Restore getestet | [ ] |

## RETENTION-DELETION.md — Aufbewahrung & Löschung
| Datenart | Aufbewahrungsfrist | Rechtsgrund | Löschmechanismus |
|---|---|---|---|
| [z. B. Logs mit PII] | [z. B. 30 Tage] | [Zweck/Recht] | [automatisiert? wie?] |
- **Löschkonzept:** [wie wird fristgerechtes Löschen technisch erzwungen? Backups?]

## DSAR-RIGHTS.md — Betroffenenrechte (Art. 12–22)
- **Auskunft (15) / Berichtigung (16) / Löschung (17) / Einschränkung (18) / Portabilität (20) / Widerspruch (21)**
- **Prozess:** [Eingang → Identitätsprüfung → Frist 1 Monat → Antwort/Umsetzung → Protokoll]
- **Technische Umsetzbarkeit:** [kann das System Daten einer Person finden/exportieren/löschen?]

## PROCESSORS-SUBPROCESSORS.md — Auftragsverarbeitung (Art. 28)
| Dienst | Rolle | AVV vorhanden | Subunternehmer | Standort |
|---|---|---|---|---|
| [z. B. EU-Region (z. B. Frankfurt)] | Auftragsverarbeiter | [ja/nein] | [Liste] | [EU] |
| [z. B. EU-Router] | Auftragsverarbeiter | [ja/nein] | [Liste] | [EU] |
- **Prüfung:** [AVV nach Art. 28 für jeden Verarbeiter? Subunternehmer freigegeben?]

## THIRD-COUNTRY-TRANSFERS.md — Drittlandübermittlung (Kap. V, Art. 44 ff.)
- **Findet eine Übermittlung außerhalb der EU/EWR statt?** [ja/nein — aus DATA-FLOW]
- **Falls ja — Garantie:** [Angemessenheitsbeschluss · SCC (Standardvertragsklauseln) · sonstige]
- **Transfer-Impact-Assessment:** [Risiko im Zielland, ergänzende Maßnahmen]
- **WERKBANK-Default:** EU-Routing erzwingt „nein" (Gate E1) — dieses Artefakt belegt das.

## BREACH-RUNBOOK.md — Meldekette bei Datenpanne (Art. 33/34)
1. **Erkennung & Eindämmung** [wer, wie, Logfreeze]
2. **Bewertung des Risikos** für Betroffene
3. **Meldung an Aufsichtsbehörde binnen 72 h** (Art. 33) — [Vorlage-Inhalt: Art, Umfang, Folgen, Maßnahmen]
4. **Benachrichtigung Betroffener** bei hohem Risiko (Art. 34)
5. **Dokumentation** jeder Panne (auch nicht-meldepflichtiger)
- **Kontakte:** [DSB, GF, [Anwalt/DSB], Aufsichtsbehörde Sachsen]
