# WERKBANK — Spec-Driven Production Framework

Ein **EU-souveränes, agentisches Framework**, das Software *konzipiert, baut, prüft und übergibt* —
und sich gegen feste Prüfprojekte selbst verbessert. Modular: nicht jeder braucht alles.

**Architektur (drei Schichten):**
- **Methode:** [BMAD v6](https://github.com/bmad-code-org/BMAD-METHOD) (unverändert) — PRD, Architektur, Stories, Test-Architekt.
- **Autonomie:** Ralph-Loop + bewährte Muster — Verification-first, crash-sicherer State, kontrollierte Iteration.
- **Governance:** WERKBANK — EU-Routing erzwingen, Quality-Gates, DSGVO-Artefakte, Audit-Log, Budget/Kill-Switch.

> WERKBANK ist **kein Ersatz** für BMAD, sondern eine **DSGVO-/Souveränitäts-Schicht darüber.**

## Schnellstart
```bash
git clone https://github.com/inveloveritas123/werkbank.git
cd werkbank
# Den Bootstrap-Prompt in Claude Code einfügen:
#   bootstrap/BOOTSTRAP-CLAUDE-CODE.md
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
| `bootstrap/` | Bootstrap-Prompt für Claude Code |

## Reife
Bauplan + Prüfgerüst. Der Beweis entsteht beim ersten Durchlauf der Golden Projects (siehe `BACKLOG.md`).

## Lizenz
MIT — siehe `LICENSE`.

> Kein Rechtsrat. Die DSGVO-Vorlagen sind Vorlagen, kein Ersatz für DSB/anwaltliche Prüfung.
