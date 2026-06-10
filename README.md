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

## Entwicklung — Tests & Gates
Das Framework selbst ist **stdlib-only** (keine Laufzeit-Abhängigkeiten). Die Dev-Tools
(ruff, mypy, coverage, bandit, pytest) sind **dev-only** und in `requirements-dev.txt` gepinnt.

```bash
make dev-setup   # Dev-Tools installieren (pip install -r requirements-dev.txt)
make check       # Pre-Push-Set: lint + type + sast + test (schnell, lokal)
make all         # check + harter Gate-Lauf (Profil werkbank_self)
```

| Ziel | Bewirkt |
|---|---|
| `make lint`  | `ruff check .` |
| `make type`  | `mypy gates` (lenient — bewusst kein strict-Mode) |
| `make sast`  | `bandit -r gates -q` |
| `make test`  | `python3 -m unittest discover -s gates/checks/tests -p "test_*.py"` |
| `make cover` | `coverage run … && coverage report` |
| `make gate`  | harter Gate-Lauf gegen `--profile werkbank_self` |

### Pflichtenheft & hartes Grün
`gates/pflichtenheft.yaml` bindet die abstrakten Gates an konkrete **Profile**
(`static_min`, `basis`, `spec_driven`, `pii`, `multi_tenant`, `werkbank_self`).
Ein Profil legt fest, welche Gates **aktiv bestanden** sein müssen.

> **Hartes Grün:** GRÜN ⇔ *jedes* Pflicht-Gate des aktiven Profils hat Status **PASS**.
> Ein Pflicht-Gate, das **FAIL** ist → VERLETZT → **ROT**.
> Ein Pflicht-Gate, das **SKIP/WARN** ist (Tool fehlt, kein Check, kein Kontext) → UNGEDECKT → **ROT**.
> "Nicht geprüft" ist nie grün — so kann kein Projekt grün aussehen, nur weil Pflichttools fehlen.

Das Repo selbst läuft unter `werkbank_self` (Pflicht: B1 ruff · B2 mypy · B3 build ·
C1 tests · C2 coverage · D1 SAST · D3 secret-scan · F1 model-pinning · H4 changelog).
Es wird **nur** grün, wenn ruff/mypy/coverage/bandit installiert sind **und** durchlaufen.

Profil wählen über `--profile`:
```bash
python3 gates/runner.py --target . --report GATE-REPORT.md --profile werkbank_self --ci
```

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
