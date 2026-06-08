# WERKBANK — Spec-Driven Production Framework

Ein **EU-souveränes, agentisches Framework**, das Software *konzipiert, baut, prüft und übergibt* —
und sich gegen feste Prüfprojekte selbst verbessert. Modular: nicht jeder braucht alles.

**Architektur (drei Schichten):**
- **Methode:** [BMAD v6](https://github.com/bmad-code-org/BMAD-METHOD) (unverändert) — PRD, Architektur, Stories, Test-Architekt.
- **Autonomie:** Ralph-Loop + bewährte Muster — Verification-first, crash-sicherer State, kontrollierte Iteration.
- **Governance:** WERKBANK — EU-Routing erzwingen, Quality-Gates, DSGVO-Artefakte, Audit-Log, Budget/Kill-Switch.

> WERKBANK ist **kein Ersatz** für BMAD, sondern eine **DSGVO-/Souveränitäts-Schicht darüber.**

## In ein eigenes Projekt — ein Befehl
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
| `golden-projects/` | standardisierte Prüfprojekte mit festem Soll |
| `werkbank-init.sh` | Ein-Befehl-Installer pro Projekt (BMAD+kiln+WERKBANK) |
| `templates/CLAUDE.werkbank.md` | vereinende `CLAUDE.md`-Vorlage (Bindeglied der drei Schichten) |
| `docs/produktivfreigabe/` | Grenzen/Haftung, Security-/Datenschutz-Review |
| `bootstrap/` | Bootstrap-Prompt für Claude Code |

## Reife
Bauplan + Prüfgerüst. Der Beweis entsteht beim ersten Durchlauf der Golden Projects (siehe `BACKLOG.md`).

## Lizenz
MIT — siehe `LICENSE`.

> Kein Rechtsrat. Die DSGVO-Vorlagen sind Vorlagen, kein Ersatz für DSB/anwaltliche Prüfung.
