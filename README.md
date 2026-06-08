# WERKBANK — Spec-Driven Production Framework

Ein **EU-souveränes, agentisches Framework**, das Software *konzipiert, baut, prüft und übergibt* —
und sich gegen feste Prüfprojekte selbst verbessert. Modular: nicht jeder braucht alles.

**Architektur (drei Schichten):**
- **Methode:** [BMAD v6](https://github.com/bmad-code-org/BMAD-METHOD) (unverändert) — PRD, Architektur, Stories, Test-Architekt.
- **Autonomie:** Ralph-Loop + bewährte Muster — Verification-first, crash-sicherer State, kontrollierte Iteration.
- **Governance:** WERKBANK — EU-Routing erzwingen, Quality-Gates, DSGVO-Artefakte, Audit-Log, Budget/Kill-Switch.

> WERKBANK ist **kein Ersatz** für BMAD, sondern eine **DSGVO-/Souveränitäts-Schicht darüber.**

## Neues System — ein Befehl (Knopfdruck)
Klont WERKBANK und richtet das aktuelle Projekt komplett ein (Gates, Loop, Tribunal, Feedback, CLAUDE.md):
```bash
curl -fsSL https://raw.githubusercontent.com/inveloveritas123/werkbank/main/bootstrap.sh | bash
# Zielprojekt + Optionen: ... | bash -s -- /pfad/zum/projekt --ralph-hook
```
Voraussetzung: **git, python3 ≥ 3.9**. Optional (degradiert sauber): node 20+ (BMAD), gh (PR/Issues), gitleaks (D3+).

## In ein eigenes Projekt — ein Befehl (bereits geklont)
BMAD (Methode) + kiln-Loop (Autonomie) + WERKBANK-Gates (Governance) als **eine Einheit**:
```bash
git clone https://github.com/inveloveritas123/werkbank.git ~/werkbank   # einmalig
~/werkbank/werkbank-init.sh /pfad/zum/projekt                            # pro Projekt
```
Das richtet `gates/`, `templates/`, `agents/`, `workflows/`, CI, kiln-`STATE.md`, gehärtetes
`.gitignore` und eine vereinende `CLAUDE.md` ein, installiert BMAD und macht einen Gate-Baseline-Lauf.
Optionen: `--no-bmad` (BMAD überspringen), `--force` (überschreiben). Voraussetzung: Python 3.9+, Git (Node 20+ für BMAD).
Danach **Claude Code** im Projekt öffnen (CLI `claude` oder VS-Code-Extension) — `CLAUDE.md` wird automatisch gelesen.

> **Geltung: intern, OHNE echte personenbezogene Kundendaten** (siehe `docs/produktivfreigabe/`).

## Selbstverbesserung (im WERKBANK-Repo selbst)
```bash
cd werkbank
# Bootstrap-Prompt in Claude Code einfügen: bootstrap/BOOTSTRAP-CLAUDE-CODE.md
```
Der Agent liest `BACKLOG.md`, arbeitet die Aufgaben ab, misst gegen `SCORING-MATRIX.md`
und verbessert sich gemäß `SELF-IMPROVEMENT.md` — gegen die `golden-projects/`, nicht frei.

## Inhalt
| Pfad | Zweck |
|---|---|
| `WERKBANK-Blueprint.md` | Architektur & Bau-Reihenfolge |
| `BACKLOG.md` | Aufgabenliste, die der Agent abarbeitet |
| `SCORING-MATRIX.md` | objektive 100-Punkte-Bewertung |
| `SELF-IMPROVEMENT.md` | Regeln kontrollierter Selbstverbesserung |
| `gates/gates.yaml` | Quality-Gate-Manifest (deterministisch zuerst) |
| `privacy/DSGVO-ARTEFAKTE.md` | DSGVO-Vorlagen (Art. 6/25/28/30/32/35 …) |
| `golden-projects/` | 6 standardisierte Prüfprojekte (Scores 97–99) |
| `examples/pilot-app/` | Thin-Slice-Durchstich 01→04 (Einwilligungs-Logbuch) |
| `bootstrap.sh` · `werkbank-init.sh` | Fresh-System- / pro-Projekt-Installer |
| `gates/runner.py` + `gates/checks/` | Gate-Runner + 19 Checks (A1–A3·B1–B3·C1/C2·D3·E1–E8·F1·H4) |
| `ralph/` | Ralph-Loop (Fresh-Context, Drift-Pausegate, Kill-Switch) |
| `tribunal/` · `deploy/` | I2 QA-Tribunal (Cross-Model) · I3 Deployment-Validierung |
| `orchestrator/` | Tier-Routing · Budget/Kill-Switch · persistente Minds (kiln) |
| `feedback/` | selbstheilend: rote Gates → Backlog/GitHub-Issues (Egress-redigiert) |
| `templates/CLAUDE.werkbank.md` | vereinende `CLAUDE.md` (Bindeglied der drei Schichten) |
| `docs/produktivfreigabe/` · `docs/SOLL-IST-ABGLEICH.md` | Freigaben · ehrlicher Soll-Ist |
| `bootstrap/` | Bootstrap-Prompt (Agent: bauen/selbst-verbessern) |

## Reife
Lauffähig: 6/6 Golden Projects grün, 178 Tests, 19 Gates, Ralph-Loop, Tribunal, selbstheilende
Feedback-Schleife, BMAD-Durchstich live. **Geltung: intern, ohne echte Kundendaten** — für echte
Kundendaten gelten die Auflagen aus `docs/produktivfreigabe/`. Ehrlicher Stand: `docs/SOLL-IST-ABGLEICH.md`.

## Lizenz
MIT — siehe `LICENSE`.

> Kein Rechtsrat. Die DSGVO-Vorlagen sind Vorlagen, kein Ersatz für DSB/anwaltliche Prüfung.
