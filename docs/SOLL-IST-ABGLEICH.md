# WERKBANK — SOLL-IST-Abgleich (ehrlich, Stand 2026-06-08)

> Was ist **wirklich** implementiert, was ist **Stub/Platzhalter**, was wurde **vergessen**.
> Maßstab: `WERKBANK-Blueprint.md` (§2 Autonomie, §3 Struktur) + BMAD + kiln-Muster.
> Legende: ✅ implementiert · 🟡 teilweise/nur Doku · ❌ Platzhalter/nicht gebaut.

> **Update T9 (2026-06-08):** C1 (Tests), F1 (Modell-Pinning), H4 (CHANGELOG) nachgebaut →
> **9 von 41 Gates** implementiert. Die Lücke „93 Tests, aber kein Gate führt sie aus" ist geschlossen.

## Kurzfassung (die unbequeme Wahrheit)
- **WERKBANK (Governance)** ist echt gebaut: Gate-Runner + **9 von 41 Gates**
  (E1/E2/E3/E4/E5/D3 + C1/F1/H4), 6 Golden Projects, Installer, Tier-Policy.
- **BMAD (Methode)** ist **installiert, aber NIE GENUTZT** — die Golden Projects wurden direkt gebaut,
  nicht über BMADs PRD/Architektur/Story-Fluss. `workflows/01-konzipieren` ist ein Stub. `_bmad-output` leer.
- **kiln/Ralph (Autonomie)** ist als **Muster dokumentiert, aber NICHT automatisiert** — kein Stop-Hook,
  kein `completion-promise`-Konsum, kein `--max-iterations`. Den Loop habe **ich** manuell gefahren.
- 35 Gates, der Thin-Slice, Budget/Kill-Switch, die LLM-Urteils-Gates, die 3 Review-Ebenen: ❌.

## 1 · BMAD (Methode) — SOLL vs IST
| Soll (Blueprint §1/§2) | Ist | Status |
|---|---|---|
| BMAD installiert (Rollen/Skills) | core+bmm v6.8.0, 6 Rollen, 44 Skills | ✅ |
| Konzipieren über BMAD: Brief→PRD→Architektur→Stories | nie ausgeführt; direkt gebaut | ❌ vergessen |
| BMAD Scrum-Master/Dev-Story-Fluss | nicht genutzt | ❌ |
| TEA (Test-Architect), Code-Review-Rolle | nicht genutzt | ❌ |
| Handoff PM→Architect (Gate A3) | nie exerziert | ❌ |
| `templates/SPEC/ARCHITECTURE/TASKS.md` real befüllt | nur leere Vorlagen | 🟡 |

## 2 · kiln / Ralph-Loop (Autonomie) — SOLL vs IST
| Soll (Blueprint §2) | Ist | Status |
|---|---|---|
| Verification-first (Tests+Gates als Orakel) | durchgängig RED→GREEN | ✅ |
| Ralph-Loop: Stop-Hook + `completion-promise GRUEN` + `--max-iterations` | **implementiert (T9): `ralph/ralph-loop.sh` Fresh-Context-Motor + `stop_hook.py` + Engine, 10 Tests** | ✅ |
| Drift-Pausegate (Qualität sinkt → anhalten) | **implementiert in `ralph_decide` (rote Gates gestiegen → HALT)** | ✅ |
| `STATE.md` crash-sicher (Pipeline-Position) | Datei existiert, manuell gepflegt; kein Code liest/schreibt | 🟡 |
| Persistente Minds + frische Worker | frische Worker (Subagenten) ja; persistente Minds nein | 🟡 |
| 3 Review-Ebenen: Paar→QA-Tribunal→Deployment-Val. | nur Ebene 1 (Paar-Review/GP) | 🟡 (2/3 fehlen) |
| Cross-Model-Diversität (Reviewer ≠ Implementer) | im Bau lief BEIDES auf Opus; Diversität erst jetzt per Tier-Router möglich, nicht nachgeholt | ❌ war nicht erfüllt |

## 3 · WERKBANK Gates — SOLL (41 in gates.yaml) vs IST (6)
| Stufe | Gates | Status |
|---|---|---|
| A Spec-Integrität (A1–A4) | „vor jedem Bau" gefordert | ❌ kein Check |
| B Statisch (B1 Lint, B2 Typecheck, B3 Build) | — | ❌ |
| C1 Unit-Tests (Suite läuft als Gate) | implementiert (T9) | ✅ |
| C2 Coverage, C3 Integration, C4 E2E, C5/C6 | — | ❌ |
| D Sicherheit: D1 SAST, D2 SCA, D4 Lizenz | — | ❌ |
| D3 Secret-Scan | implementiert | ✅ |
| E1 EU-Routing | implementiert (statisch) | ✅/🟡 |
| E2 PII · E3 Tenant · E4 Audit-Schema · E5 Artefakte | implementiert | ✅ |
| E6 DPIA-Erzwingung · E7 Drittland · E8 Datenminimierung | — | ❌ |
| F1 Modell-Pinning (kein 'latest') | implementiert (T9) | ✅ |
| F2 Eval-on-Bump, F3 Snapshots | — | ❌ |
| G Performance (G1–G3) | — | ❌ |
| H4 CHANGELOG-Gate (vorhanden, newest-top) | implementiert (T9) | ✅ |
| H1–H3, H6 Drift-Audit | — | ❌ |
| I LLM-Urteil: I1 Vier-Augen, I2 QA-Tribunal, I3 Deployment-Val. | manuell als Paar-Review gemacht, nicht verdrahtet | ❌ |

## 4 · WERKBANK-Features (Blueprint §1 „dein Moat") — SOLL vs IST
| Soll | Ist | Status |
|---|---|---|
| EU-Routing **erzwingen** | E1 statischer Scan; kein Laufzeit-Proxy | 🟡 |
| 62 Gates | 41 im Manifest, 6 implementiert | 🟡/❌ |
| DSGVO-Artefakte | Vorlagen + E5 | ✅ |
| Audit-Log | nur in GP03; kein globales WERKBANK-Audit eigener Aktionen | 🟡 |
| Mandantentrennung (Plattform) | in GP03 demonstriert, keine Plattform-Funktion | 🟡 |
| Budget/Kill-Switch | **kein Code**; settings-Werte 0 | ❌ |
| Kanzler (Ops) | Stub, disabled | ❌ (bewusst) |
| Branchen-Module (bau/finanzen/gis/iot) | leer | ❌ |

## 5 · Struktur (Blueprint §3) — SOLL vs IST
| Pfad | Status |
|---|---|
| `gates/` Runner+Checks | ✅ |
| `agents/*.md` (junge/waechter/kanzler/privacy-analyst) | 🟡 **deskriptive Stubs** — kein lauffähiger Orchestrator, keine `.claude/agents/`-Definitionen |
| `workflows/01–04` | 🟡 **Stubs** („Aktiv ab T2" — nie verdrahtet) |
| `templates/` | ✅ Vorlagen |
| `privacy/` Artefakt-Vorlagen | ✅ |
| `.werkbank/STATE.md`,`BENCHMARK.md` | ✅ (manuell gepflegt) |
| `examples/pilot-app/` Thin-Slice durch 01→04 | ❌ **nie gebaut** — Golden Projects ersetzten ihn |
| `.github/workflows/werkbank-gates.yml` | ✅ (CI läuft) |
| `settings.example.yaml` Werte | 🟡 Platzhalter (by design) |
| `orchestrator/tier_router.py` | ✅ (neu) — aber Orchestrator setzt `model=` manuell |

## 6 · Was das praktisch bedeutet
Die **drei Schichten als „Einheit"** existieren als Gerüst + Doku (`CLAUDE.md`), aber:
- **BMAD und kiln sind nicht automatisiert** — sie werden von der menschlich gestarteten Claude-Code-
  Session (mir) „gespielt". Es gibt keinen selbstlaufenden Loop und keinen echten BMAD-Aufruf.
- Der **Governance-Kern** (Gates E1–E5/D3 + Golden Projects + Installer + Tier-Policy) ist das, was
  wirklich steht und trägt.

## 7 · Empfohlene Schließreihenfolge (klein → großer Hebel)
1. ~~**C-Gate**: Tests als Block-Gate~~ — **erledigt (T9, C1)**. Offen: C2 Coverage.
2. ~~**H4** CHANGELOG · **F1** Modell-Pinning~~ — **erledigt (T9)**.
3. **B-Gates**: Lint/Typecheck/Build (ruff/mypy) — sobald ein echtes Projekt damit läuft.
4. ~~**Ralph-Loop echt**~~ — **erledigt (T9): `ralph/ralph-loop.sh` + Stop-Hook + Drift-Pausegate.**
5. **BMAD wirklich nutzen**: 01-konzipieren an die BMAD-Rollen anbinden (1 echter Durchstich). ← nächster großer Brocken
6. **I2/I3** (QA-Tribunal, Deployment-Validierung), **E6/E7** (DPIA/Drittland), **Budget/Kill-Switch**.
