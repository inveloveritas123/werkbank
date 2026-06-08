# WERKBANK v2 — Das beste aus allen Welten

**Architektur-Blueprint · Stand: Juni 2026 · Reife: Bauplan (Thin-Slice steht aus)**

> **North Star:** EU-souveräne, agentische Software-Produktion für den Mittelstand —
> **BMAD als Methode, Ralph/kiln als Autonomie, WERKBANK als DSGVO-/Infra-Layer-Governance.**
> Nicht „WERKBANK statt BMAD", sondern WERKBANK **über** BMAD.

---

## 1 · Die drei Schichten (so passt alles zusammen)

| Schicht | Quelle | Was sie liefert | Status |
|---|---|---|---|
| **Methode** | **BMAD v6** (unverändert) | Analyst/PM, Architect, Scrum-Master, Dev, TEA-Test, PRD, Architektur, Stories, Code-Review | übernehmen, nicht nachbauen |
| **Autonomie** | **Ralph-Loop** + **kiln-Muster** | Verification-first-Schleife, die baut/testet/iteriert bis grün; crash-sicherer State; persistente Minds + frische Worker; 3 Review-Ebenen | adaptieren |
| **Governance** | **WERKBANK** (dein Moat) | EU-Routing erzwingen, 62 Gates, DSGVO-Artefakte, Audit-Log, Mandantentrennung, Budget/Kill-Switch, Kanzler | **selbst bauen** |

**Konsequenz:** Deine Energie gehört *ausschließlich* in Schicht 3. Schicht 1 installierst du
(`npx bmad-method install`). Schicht 2 klaust du als Muster. Schicht 3 ist das, was BMAD und
kiln nicht haben — und was deine deutschen Kunden bezahlen.

---

## 2 · Die Autonomie-Maschine (das beste aus allen Welten)

**Fundament — Verification-first (Boris Cherny):** Kein autonomer Lauf ohne Orakel.
Die Akzeptanzkriterien aus der Spec + die Tests + die deterministischen Gates *sind* das Orakel.
Ohne das läuft jede Schleife ewig oder bricht zu früh ab.

**Motor — Ralph-Loop (Huntley / offizielles Anthropic-Plugin):**
Ein Stop-Hook fängt „fertig" ab und speist den Auftrag neu ein, bis ein `completion-promise`
(z. B. `<promise>GRUEN</promise>`) erscheint **und** alle Block-Gates grün sind.
`--max-iterations` ist das Sicherheitsnetz. Fresh-context-Bash-Variante > Plugin-Variante
für große Aufgaben (frischer Kontext pro Runde statt einer wachsenden Session).

**Sicherheit — Spec-Anker statt Metrik (Kitchen Loop, arXiv 2026):**
Selbstverbesserung **konvergiert gegen die Spec + ein Regressions-Orakel**, sie *optimiert keine
Kennzahl*. Das verhindert Goodharting (Agent trimmt eine Zahl, Produkt verrottet woanders) —
dein RDO-Risiko K-03. **Drift-Pausegate:** fällt die Qualität (Tests/Gates) zwischen zwei
Runden, hält die Schleife an und eskaliert, statt blind weiterzulaufen.

**Gedächtnis & Teamform — kiln-Muster:**
- `STATE.md` (crash-sicher): Pipeline-Position; jeder Lauf nimmt auf, wo der letzte stoppte.
- **Persistente Minds + frische Worker:** Reviewer/Architekt-„Minds" behalten Historie; Builder
  werden pro Chunk frisch gespawnt (sauberer Kontext).
- **3 Review-Ebenen:** Paar-Reviewer (pro Chunk) → QA-Tribunal (Meilenstein, möglichst
  Cross-Model) → Deployment-Validierung gegen echte User-Flows.
- **Cross-Model-Diversität:** Reviewer ≠ Implementer-Modell (deckt direkt BMADs „Haftungs"-Lücke).

**Ankerregel für dich:** Autonomie automatisiert das *Mechanische*, nicht die *Entscheidung*.
Brainstorm/Spec-Freigabe bleibt bei dir; Research→Bauen→Prüfen→Übergeben läuft autonom;
alles mit DSGVO-Relevanz oder „rot" hält für deine Freigabe an.

---

## 3 · Ziel-Struktur (was die leeren Ordner endlich füllt)

```text
werkbank/
  agents/                      # Claude-Code-Subagenten (Markdown-Definitionen)
    junge.md                   # Orchestrator (schlank; nutzt nativen Bash-Subagent zur Kontext-Isolation)
    waechter.md                # Gate-Runner / Verifizierer (hartes Block-Gate)
    kanzler.md                 # Ops/Chief-of-Staff (erst zuletzt; default: disabled)
    privacy-analyst.md         # DSGVO-Prüfer (erzeugt/prüft die privacy/-Artefakte)
  workflows/
    01-konzipieren.md          # ruft BMAD: Brief → PRD → Architektur → Stories
    02-bauen.md                # Ralph-Loop: Story → RED/GREEN/REFACTOR → Chunk-Review
    03-pruefen.md              # gates/runner über alle Block-Gates + QA-Tribunal
    04-uebergeben.md           # Übergabe-Bündel: Spec+Arch+Tests+Doku+Audit-Log
  gates/
    gates.yaml                 # 62-Gate-Manifest (deterministisch zuerst) — liegt bei
    runner.(sh|ts|py)          # führt Gates gestaffelt aus, schreibt GATE-REPORT
    checks/                    # je ein deterministischer Check pro Gate
      e1-eu-routing.*          # FAIL, wenn ein Call nicht über EU-Endpunkt lief
      d3-secret-scan.*         # FAIL bei Secret im Diff
      e2-pii-log-scan.*        # FAIL bei PII in Logs/Prompts
      h6-drift-audit.*         # diff PRD ↔ implementierte Architektur
  templates/
    SPEC.md  ARCHITECTURE.md  TASKS.md  GATE-REPORT.md  AUDIT-LOG.schema.json
  privacy/                     # DSGVO-Artefakte (Vorlagen liegen bei) — der echte Moat
    DATA-FLOW.md  PROCESSING-REGISTER.md  LAWFUL-BASIS.md
    DPIA-SCREENING.md  DPIA.md  TOMs.md  RETENTION-DELETION.md
    DSAR-RIGHTS.md  PROCESSORS-SUBPROCESSORS.md  THIRD-COUNTRY-TRANSFERS.md
    BREACH-RUNBOOK.md
  .kiln/ | .werkbank/
    STATE.md                   # crash-sicherer Pipeline-State
    BENCHMARK.md               # PDCA-Messwerte je Lauf
  examples/
    pilot-app/                 # der Thin-Slice (Beweis, dass alles läuft)
  .gitea/ | .github/workflows/
    werkbank-gates.yml         # CI: Block-Gates müssen grün sein vor Merge
  settings.example.yaml        # (vorhanden) EU-Routing, Tiers, Budget, Module
```

---

## 4 · DSGVO ist mehr als EU-Routing (die korrigierte Lücke)

EU-Endpunkte sind **notwendig, nicht hinreichend**. DSGVO verlangt zusätzlich u. a.
Datenschutz durch Technikgestaltung & Datenminimierung (Art. 25), ein Verzeichnis von
Verarbeitungstätigkeiten (Art. 30), TOMs (Art. 32), eine DSFA bei hohem Risiko (Art. 35),
Auftragsverarbeitung (Art. 28), Drittlandtransfers (Kap. V) und Meldepflichten (Art. 33/34).

WERKBANK v2 macht daraus **prüfbare Artefakte** (Vorlagen liegen in `privacy/` bei) und
verdrahtet sie als Gates der Kategorie E (Souveränität/DSGVO): ein Projekt ist erst
„übergabefertig", wenn die relevanten Artefakte ausgefüllt **und** die E-Gates grün sind.
Das ist der Unterschied zwischen „wir hosten in der EU" und „wir sind DSGVO-konform".

---

## 5 · Bau-Reihenfolge (Thin-Slice zuerst — nicht philosophieren)

1. **Fundament:** `npx bmad-method install` ins Pilotprojekt. BMAD übernimmt Methode/Rollen.
2. **Souveränität verdrahten:** `settings.yaml` mit echten EU-Routing-Werten füllen
   (EU-Endpunkte (z. B. EU-Region eines Anbieters + EU-Router)). Gate **E1 (EU-Routing)** als erstes scharf schalten.
3. **Deterministische Gates zuerst:** `runner` + `checks/` für E1, D3 (Secret), E2 (PII).
   Kein LLM nötig, in Stunden lauffähig.
4. **Ralph-Loop um BMADs Dev-Story:** Story → Tests → Implementierung → Chunk-Review,
   `completion-promise = GRUEN`, `max-iterations` als Netz, Drift-Pausegate aktiv.
5. **Thin-Slice-Pilot:** *eine* winzige App end-to-end durch 01→04. Das ist der Beweis.
6. **PDCA:** benchmarken → messen → spec-verankert verbessern → erneut laufen → pushen.
7. **Kanzler & restliche Gates später** — erst wenn der Durchstich steht.

---

## 6 · Ehrliche Reife

Dies ist ein **Bauplan**, kein laufendes System. Gemessen an „fertiges Produkt": ~15 %.
Gemessen an „Plan, um Infra-Layer auf BMAD-Basis aufzubohren": ~75 %. Der einzige Weg, das zu
heben, ist der Thin-Slice unter §5 — der `BOOTSTRAP-CLAUDE-CODE.md` setzt genau das um.
