# KOLONIE × BMAD — Das optimale System

**Architektur-Entscheidungsdokument** · Mapping · Schwächen-Ausgleich · Hardening-Pipeline · Skill-Sync

> Kernthese: Das bessere System ist **die Vereinigung**. BMAD liefert die überlegene **Workflow- und Dokumentenschicht** (Spec → PRD → Architektur → Stories → Dev → QA). KOLONIE liefert die Schicht **nach dem Test** (Deploy, Souveränität, Routing, Budget, Multi-Tenant) — und füllt damit genau die Lücken, die BMAD selbst als ungelöst benennt.

---

## 1 · Mapping: Meine 6 Subagents ↔ BMAD-Rollen

| BMAD-Rolle | Aufgabe | Mein Pendant | Tier | Verdikt |
|---|---|---|---|---|
| **Analyst / PM** | Brief, PRD, Requirements, Markt-/Branchen-Research | `researcher` (nur teilweise) | Haiku | **BMAD übernehmen.** PRD-Autor als erste Klasse fehlt mir. `researcher` bleibt als Haiku-Vorstufe (Quellen sammeln). |
| **Architect** | Technisches Design-Dokument, Integrationspunkte | `architect` | Opus | **BMAD-Workflow übernehmen**, Opus-Tier behalten. BMAD produziert das Design als persistentes Artefakt. |
| **Scrum Master** | Story-Zerlegung, Done-Kriterien, Story-Dateien | — *(fehlt)* | — | **BMAD übernehmen.** Echte Lücke bei mir — heute mache ich das ad hoc. |
| **Developer** | Implementierung **gegen Spec**, nicht gegen Prompt | `implementer` | Sonnet | **BMAD-Dev-Workflow ersetzt** meinen Ad-hoc-Implementer, Sonnet-Tier behalten. |
| **QA / Test Architect (TEA)** | Validierung gegen Akzeptanzkriterien, risikobasierte Teststrategie | `tester` | Sonnet | **TEA übernehmen** (umfassender als mein Tester), Sonnet, für Urteils-Gates ggf. hochstufen. |
| *(kein BMAD-Pendant)* | Billige Codebase-Recon, Kontext-Vorbereitung | `explorer` | Haiku | **Behalten.** BMAD hat keine billige Recon-Rolle — spart Tokens vor teuren Phasen. |
| *(kein BMAD-Pendant)* | Vier-Augen-Review, **Haftungs-Gate** für AI-Code | `reviewer` | Sonnet | **Behalten + als hartes Gate.** Deckt direkt BMADs Schwäche „Haftung". Muss auf **anderem Modell** laufen als der Implementer. |
| *(kein BMAD-Pendant)* | Orchestrierung, EU-Routing, Budget, Multi-Tenant, PDCA | `Junge` + KOLONIE | — | **Mein Moat.** BMAD endet beim Test — alles danach bleibt hier. |

**Konsequenz:** Kein „Umstieg". Du ersetzt 3 deiner Agenten durch BMADs strukturierte Workflows, schließt 2 Lücken (PM, SM), behältst 3 Stärken (Explorer, Reviewer-als-Gate, Orchestrierung). Eine Quelle der Wahrheit: kein zweites `CLAUDE.md` neben BMADs Config — Konventionen wandern in BMADs Agenten-Config.

---

## 2 · Wo BMAD stark ist — und wo schwierig (Folien-Auswertung)

### Stärken (übernehmen)
- **Spec als Quelle der Wahrheit** killt den Context-Drift über Sessions — der mit Abstand größte Hebel.
- **Vertraute SDLC-Rollen** → kein neuer Prozess, nur andere Teammitglieder.
- **Persistente Artefakte** (PRD, Architektur, Stories als Markdown) → Refactoring mit dokumentiertem *Intent*, nicht nur Ist-Code.
- **TEA-Testarchitektur** und **scale-adaptive** Planungstiefe.
- **Modell-agnostisch:** die Agenten sind nur Markdown — laufen gegen *jedes* Backend, also auch gegen dein EU-Routing.

### Schwächen → konzeptioneller Ausgleich
Die Folie „Was wir noch nicht gelöst haben" + der ehrliche Retro-Slide, jeweils mit KOLONIE-Antwort:

| # | BMAD-Schwäche (Folie) | Konzeptioneller Ausgleich | Quelle des Ausgleichs |
|---|---|---|---|
| 1 | **Doku-Drift** — PRD ≠ Realität nach vielen Epics | **Drift-Audit-Gate**: difft PRD ↔ implementierte Architektur pro Epic; Specs **shardden** (klein halten); INDEX-first + append-only CHANGELOG; periodisches Re-Grounding | Gate G‑H6 + deine Konventionen |
| 2 | **Team-Skalierung** — mehrere Devs = Sync-Problem | **Branch-per-Story** + **Merge-Queue** + `Junge`-Orchestrierung + git-worktrees pro Story | Gitea + Orchestrator |
| 3 | **Haftung für AI-Code** (DSGVO-Vorfall) | **Hartes Vier-Augen-Gate mit Modell-Diversität** (Reviewer ≠ Implementer-Modell) + **unveränderliches Audit-Log** + AVV (Lexa) + EU-Routing → **deine Stärke** | Reviewer-Gate + KOLONIE |
| 4 | **Edge Cases** — Race Conditions, Mandanten-Interferenz | **Concurrency-Gate** + **Tenant-Isolation** (`vmbr2` ohne Internet, Single-Tenant-LXC) + **Canary/Pilot-Deploy** statt Big-Bang | Gates G‑C5/G‑E3 + Netz-Topologie |
| 5 | **Modell-Drift** — neues Release, neuer Output | **Modell-Pinning** + **Eval-on-Bump-Gate** (bei jedem Modellwechsel Regressions-Eval) + **Golden-Output-Snapshots** | Gates G‑F1…F3 + Routing |
| 6 | **Kosten** — linear mit Projektgröße | **Budget-API** + **Tier-Routing** (Haiku 80 / Sonnet 15 / Opus 5) + **deterministische Gates statt LLM-Gates** → **deine Stärke**, billiger als Copilot-Sub | LLM-Proxy + Gate-Strategie §3 |
| 7 | **Disziplin-Erosion** (Retro: Follow-Through fiel auf 55–58 %, Tech-Debt bis Aufräum-Sprint) | **Gates blockierend statt beratend** (kein Merge ohne grün) + **PDCA-Kadenz** erzwingt Follow-Through | Blocking-Integration §3 + PDCA |
| 8 | **Raue Agent-Handoffs** (Architect nimmt an, was PM nicht spezifizierte) | **Handoff-Checklisten als Gate** zwischen Phasen + **schema-validierte Artefakte** (PRD/Design/Story haben Pflichtfelder) | Gate G‑A1/A2 |
| 9 | **Context-Window-Druck** bei großen Projekten | **Spec-Sharding** + **MCP-Wissens-Layer** statt „alles im Kontext" + Subagent-Isolation | dein MCP+LLM-as-Knowledge-Layer |

**Fazit der Auswertung:** 6 von 9 genannten Schwächen beantwortet deine Infrastruktur direkt. Das ist der eigentliche Beweis, dass die Vereinigung das bessere System ist — nicht BMAD pur.

---

## 3 · Output-Hardening: 62-Gate-Pipeline + Wächter-Agent

> Anforderung: „beim Output nachsteuern — Pipeline mit 50+ Funktions-/Sicherheits-Gates, branchentypische Best-Cases, dedizierter optimierter Agent."

**Legende:** `[BLOCK]` blockiert Merge/Deploy · `[WARN]` beratend · `[LLM]` braucht Modell-Urteil (alle anderen sind deterministische Tools) · `[BRANCHE]` pro Kunde zuschaltbar.

**Designprinzip (löst zugleich die Kosten-Schwäche):** Gates laufen **gestaffelt** — erst die billigen deterministischen Tools (fail fast), LLM-Urteils-Gates **nur** auf dem, was deterministisch durchkommt. So bleibt der Token-Verbrauch sublinear.

### A · Spezifikations-Konformität
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| A1 | Artefakt-Schema | PRD/Design/Story haben alle Pflichtfelder | JSON-Schema/Linter | `[BLOCK]` |
| A2 | Handoff-Checkliste | Architect-Annahmen ⊆ PM-Spec | Custom-Check | `[BLOCK][LLM]` |
| A3 | Akzeptanzkriterien vorhanden | jede Story testbar formuliert | Linter | `[BLOCK]` |
| A4 | Story ↔ Code-Traceability | jeder Commit referenziert Story-ID | Git-Hook | `[BLOCK]` |
| A5 | Scope-Grenze | kein Code außerhalb der Story-Scope-Datei | Diff-Check | `[WARN]` |
| A6 | Spec-Aktualität | PRD-Hash seit Story-Start unverändert oder bewusst versioniert | Git-Check | `[WARN]` |

### B · Funktionale Korrektheit
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| B1 | Build grün | kompiliert/transpiliert fehlerfrei | tsc/vite build | `[BLOCK]` |
| B2 | Typprüfung | keine Typfehler | TypeScript/mypy | `[BLOCK]` |
| B3 | Akzeptanz-Match | Output erfüllt Akzeptanzkriterien der Story | TEA/Custom | `[BLOCK][LLM]` |
| B4 | Edge-Cases | leere Eingaben, Null, Timeouts behandelt | Test + Review | `[BLOCK]` |
| B5 | Fehlerpfade | definierte Fehlerbehandlung, kein Silent-Fail | SAST/Review | `[WARN]` |
| B6 | Idempotenz | Scripts/Deployments wiederholbar | Test | `[WARN]` |

### C · Test-Pyramide
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| C1 | Unit/Integration | je Story eigene Tests | Vitest | `[BLOCK]` |
| C2 | Coverage-Schwelle | ≥ definierter Coverage (z. B. 75 %) | Vitest --coverage | `[BLOCK]` |
| C3 | E2E User-Journeys | Kern-Flows gegen echten Browser | Playwright | `[BLOCK]` |
| C4 | Accessibility | BITV 2.0 / WCAG 2.1 AA auf öffentl. Seiten | axe-core | `[BLOCK][BRANCHE]` |
| C5 | Concurrency | Race Conditions, Doppel-Submit, Session-Konflikte | Custom-Last/Test | `[BLOCK]` |
| C6 | Smoke (Staging) | Health, Login, Kern-Submission | Playwright-Smoke | `[BLOCK]` |
| C7 | Mutation-Tests | Testsuite fängt eingebaute Defekte | Stryker | `[WARN]` |
| C8 | Contract-Tests | API-Verträge stabil | Pact/Schemathesis | `[WARN]` |
| C9 | Golden-Output-Snapshot | Output-Diff zu Referenz (gegen Halluzination) | Snapshot-Test | `[BLOCK]` |

### D · Security
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| D1 | SAST | statische Code-Schwachstellen | Semgrep/CodeQL | `[BLOCK]` |
| D2 | Dependency/SCA | bekannte CVEs in Abhängigkeiten | Trivy/osv-scanner | `[BLOCK]` |
| D3 | Secret-Scanning | keine Keys/Tokens im Code/Repo | gitleaks | `[BLOCK]` |
| D4 | AuthN/AuthZ | geschützte Routen wirklich geschützt | Test + Review | `[BLOCK]` |
| D5 | Input-Validierung | serverseitig, nicht nur Client | Review/SAST | `[BLOCK]` |
| D6 | Injection (SQL/XSS) | parametrisiert, escaped | Semgrep | `[BLOCK]` |
| D7 | **Prompt-Injection** | LLM-Pfade gegen Injection/Leak gehärtet | Custom + Red-Team-Prompts | `[BLOCK][LLM]` |
| D8 | Security-Header/CORS | CSP, HSTS, restriktives CORS | header-check | `[WARN]` |
| D9 | Rate-Limiting | Abuse-/Brute-Force-Schutz an Endpunkten | Config-Check | `[WARN]` |

### E · DSGVO & Compliance *(branchenkritisch)*
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| E1 | **Daten-Residenz** | jeder Modell-Call/Storage über EU-Endpunkt | Routing-/Egress-Check | `[BLOCK]` |
| E2 | PII-Erkennung | keine personenbezogenen Daten in Logs/Prompts | Presidio/Regex | `[BLOCK]` |
| E3 | **Mandantentrennung** | kein Tenant-übergreifender Datenzugriff | Isolation-Test | `[BLOCK][BRANCHE]` |
| E4 | Vier-Augen für AI-Code | Reviewer-Sign-off (anderes Modell) liegt vor | Gate-Check | `[BLOCK][LLM]` |
| E5 | AVV-Abdeckung | jeder Sub-Dienstleister AVV-gedeckt (Lexa-Liste) | Manifest-Check | `[BLOCK]` |
| E6 | Löschkonzept/Retention | Aufbewahrungs-/Löschfristen implementiert | Config-Check | `[WARN][BRANCHE]` |
| E7 | Consent/Logging | Einwilligungen erfasst, Audit-Log unveränderlich | Test | `[WARN]` |
| E8 | Daten-Minimierung | nur notwendige Felder erhoben/verarbeitet | Review | `[WARN]` |

### F · Daten- & Modell-Integrität
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| F1 | Modell-Pinning | Produktiv-Modellversionen gepinnt | Config-Check | `[BLOCK]` |
| F2 | Eval-on-Bump | Regressions-Eval bei Modellwechsel bestanden | Eval-Harness | `[BLOCK][LLM]` |
| F3 | Output-Grounding | LLM-Output durch Quelle/Kontext gedeckt | Custom | `[WARN][LLM]` |
| F4 | Output-Schema | strukturierte Outputs schema-valide | JSON-Schema | `[BLOCK]` |
| F5 | Datenmigration | Migrationen reversibel, getestet | Migration-Test | `[WARN]` |
| F6 | Referenz-Drift | Golden-Set-Abweichung unter Schwelle | Diff | `[WARN]` |

### G · Performance & Resilienz
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| G1 | Last-Szenario | z. B. 50 Mandanten · 1k Views ohne Fehler | k6 | `[BLOCK]` |
| G2 | p95-Latenz | unter Schwelle | k6 + Grafana | `[WARN]` |
| G3 | Memory/Leak | kein Leak unter Last | Profiler | `[WARN]` |
| G4 | Zero-Downtime | Rolling-Update ohne Ausfall | Deploy-Test | `[BLOCK]` |
| G5 | Rollback | Rollback-Pfad funktioniert | Deploy-Test | `[BLOCK]` |
| G6 | Ressourcen-Budget | CPU/RAM im Container-Limit | cgroup-Check | `[WARN]` |

### H · Wartbarkeit & Dokumentation
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| H1 | Lint/Format | Stil konsistent | ESLint/Prettier/ruff | `[BLOCK]` |
| H2 | Komplexität | zyklomatische Komplexität unter Schwelle | eslint-complexity | `[WARN]` |
| H3 | Selbst-Doku | komplexe Strukturen dokumentiert (nicht trivial) | Review | `[WARN]` |
| H4 | CHANGELOG-Append | append-only-Eintrag vorhanden | Git-Hook | `[BLOCK]` |
| H5 | Namens-Konvention | R-/L-/LH-Präfixe eingehalten | Linter | `[WARN]` |
| H6 | **Drift-Audit** | PRD ↔ Implementierung pro Epic gediffed | Custom | `[WARN][LLM]` |

### I · Branchen-Module *(pro Kunde zuschaltbar)*
| # | Gate | Prüft | Werkzeug | Typ |
|---|---|---|---|---|
| I1 | Bau/Handwerk | VOB/DIN-Bezug, Aufmaß-/Kalkulations-Logik | Rule-Check | `[WARN][BRANCHE]` |
| I2 | Finanzen/ERP | SKR03/04, § 14 UStG, DATEV-Format, Skonto/Rundung | Rule-Check | `[BLOCK][BRANCHE]` |
| I3 | Recht/Compliance | Aufbewahrungsfristen, Mandantentrennung | Rule-Check | `[BLOCK][BRANCHE]` |
| I4 | GIS/Immobilien | Koordinatensysteme, WMS/WFS, Kataster | Rule-Check | `[WARN][BRANCHE]` |
| I5 | IoT/Embedded | MQTT/Modbus-Konformität, Edge-Constraints | Rule-Check | `[WARN][BRANCHE]` |
| I6 | Public Sector | BITV-Audit verpflichtend, Barrierefreiheit | axe-core + Manuell | `[BLOCK][BRANCHE]` |

**62 Gates gesamt.** Pro Kundenprojekt aktivierst du das passende Branchen-Modul (I) + die Pflichtblöcke (A–H); der Rest ist Konfiguration, nicht Neubau.

### Der Wächter-Agent
- **Rolle:** dedizierter QA-/Hardening-Agent, der die Pipeline orchestriert (Name passt zu `Junge`: **`Wächter`**). Fusioniert konzeptionell deinen `reviewer` + `tester` zu einem Gate-Runner und übernimmt BMADs TEA-Workflow.
- **Deployment:** eigener LXC, geklont aus `golden template CT 999`; läuft als blockierende **Gitea-Action** vor Merge und vor Deploy (spiegelt das Staging-Gate aus dem Vortrag). Ergebnisse → Dashboard:5000 + Grafana.
- **Modell-Strategie:** Gros der Gates sind **deterministische Tools = kein LLM** (schnell, billig). Nur `[LLM]`-Gates routen über deinen Stack — Analyse-Urteile via S2/S4 (Mistral EU), die härtesten (Prompt-Injection-Red-Team, Eval-on-Bump) via **S6 Claude Bedrock Frankfurt**, confirm-gated. Das macht die Pipeline **gründlicher als der Vortrag und zugleich günstiger**.
- **Blocking-Logik:** Deploy nur bei *allen* `[BLOCK]` grün; `[WARN]` erzeugt Findings, blockiert aber nicht — schärfbar pro Projektreife.

---

## 4 · Skills/Agenten via GitHub aktuell halten

> „GitHub-Methode, die Wissen um Agenten/Projekte stets aktuell zieht — clever für Skills?"

**Kurz: ja — und du hast die Bausteine schon** (`inveloveritas123/claude_skills`, temp/final-Labels, skills-mcp:8487). Aber „stets aktuell" muss **„aktuell nach kontrolliertem Review"** heißen, sonst importierst du genau die Modell-/Dependency-Drift aus §2/#5.

**Quelle der Wahrheit:** `claude_skills`-Repo hält Skills, Agenten, Gate-Definitionen **und** dein BMAD-House-Profil.

**Sync-Mechanik (kontrollierte Promotion):**
1. **Session-Start-Hook** → `git pull` des Skills-Repos: Agenten laden immer den **letzten `final`-Stand**.
2. **Nightly systemd-Timer** → `fetch` von (a) Upstream-BMAD-Releases und (b) deinem Repo in einen **Staging-Branch**.
3. **Promotion-Gate:** gezogene Änderungen landen als `temp` → **Vier-Augen-Review** (im PDCA-Mittwochs-Slot) → `final`. **Nur `final` wird produktiv geladen.** Kein Auto-Merge.
4. **Optionaler Docs-Refresh:** Job zieht aktuelle Dependency-Docs/READMEs in den **MCP-Wissens-Layer** (skills-mcp / `kolonie-wissen`), damit Grounding-Gates (F3, H6) gegen aktuellen Stand prüfen.

**Sicherheit (Pflicht):** BMAD-Version **pinnen**, Release-Diffs reviewen, signierte Commits, kein `curl | bash`. Supply-Chain-Bewusstsein — Upstream ist fremd-kontrolliert.

**Warum das passt:** nutzt dein bestehendes Repo, deine temp/final-Semantik, deine PDCA-Kadenz und deinen MCP-Layer — null Neuerfindung, nur Verdrahtung. Der Effekt: deine Skills sind nie veraltet *und* nie ungeprüft.

---

## 5 · Nächste Schritte (Vorschlag)
1. **Bootstrap-Audit** auf dem Server fahren (separater Prompt) — Ist-Zustand + Routing-Knackpunkt (1.3) klären.
2. **BMAD-House-Profil-Brief** schreiben → Claude Code generiert via BMB deine vorkonfigurierte BMAD-Variante (Konventionen, DSGVO-Gates, EU-Routing fest verdrahtet).
3. **Wächter-Agent** als LXC aus CT 999 klonen, Gate-Katalog (A–H) als Gitea-Action verdrahten, ein Branchen-Modul (I) für ein Pilot-Kundenprojekt aktivieren.
4. **Skill-Sync** als systemd-Timer + Session-Hook mit Promotion-Gate aufsetzen.

> Reihenfolge bewusst: erst sehen (1), dann das Werkzeug auf dich zuschneiden (2), dann härten (3), dann aktuell halten (4).
