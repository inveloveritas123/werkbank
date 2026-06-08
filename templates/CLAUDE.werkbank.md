# Projekt-Leitfaden — BMAD · kiln · WERKBANK als eine Einheit

> Diese Datei macht die drei Schichten zu **einem** Arbeitsmodell. Claude Code liest sie automatisch.
> **Geltung: interner Einsatz, KEINE echten personenbezogenen Kundendaten** (siehe WERKBANK-Freigabe).

## Die drei Schichten — und wie sie zusammenspielen
| Schicht | Quelle | Rolle hier |
|---|---|---|
| **Methode** | **BMAD** (`_bmad/`, via `npx bmad-method`) | Analyst/PM/Architect/SM/Dev — Brief → PRD → Architektur → Stories |
| **Autonomie** | **kiln-Muster** (adaptiert) | `.werkbank/STATE.md` (crash-sicher), Ralph-Loop bis `<promise>GRUEN</promise>`, persistente Reviewer-Minds + frische Builder, 3 Review-Ebenen, Drift-Pausegate |
| **Governance** | **WERKBANK** (`gates/`) | deterministische Block-Gates (E1/E2/E3/E4/E5/D3) — **müssen grün sein vor Push** |

kiln ist ein **Muster**, kein installiertes Tool — es lebt in `.werkbank/STATE.md`, den `agents/`/`workflows/`-Definitionen und diesem Loop.

## Der Arbeitsloop (BMAD → kiln → WERKBANK)
1. **Konzipieren (BMAD):** Story/PRD/Architektur über die BMAD-Rollen (`workflows/01-konzipieren.md`).
2. **Bauen (kiln/Ralph):** Test zuerst (RED → GREEN → REFACTOR). Pro Chunk **Paar-Review: Reviewer-Modell ≠ Implementer**. `STATE.md` nach jeder Runde. Drift-Pausegate: sinkt Test/Gate ggü. Vorrunde → anhalten.
3. **Prüfen (WERKBANK):** `python3 gates/runner.py --target . --report GATE-REPORT.md`. Rote Block-Gates ⇒ kein Fortschritt.
4. **Übergeben:** CHANGELOG + `.werkbank/BENCHMARK.md` (Vorher/Nachher), Branch pushen, **PR** — **kein Selbst-Merge**, Mensch gibt frei.

## Harte Regeln (nicht verhandelbar)
- Nie direkt auf `main`/Prod — Branch `werkbank-build`. Alles reversibel.
- **Block-Gate rot ⇒ kein Push.** E-Gate (E*) rot ⇒ STOPP, Mensch fragen.
- **Keine Secrets/PII committen** — nur Env-Referenzen. Verstöße in Tests zur Laufzeit synthetisieren.
- Verification-first: kein Lauf ohne Orakel (Akzeptanz + Tests + Gates). Assertions nie aufweichen.
- Selbstverbesserung nur kontrolliert (kleinste Änderung, größter Hebel, messen, Regression prüfen, sonst zurückrollen).

## Die Gates (kurz)
- **E1** EU-Routing (kein Non-EU-Endpunkt/Region in Code/Config) · **E2** keine Klartext-PII in Logs/Prompts/Outputs · **D3** keine Secrets · **E3** Mandantentrennung (Audit-Log) · **E4** Audit-Log-Schema · **E5** DSGVO-Artefakt-Vollständigkeit (`--privacy-dir`).
- Nicht-implementierte Gates erscheinen als **SKIP** (ehrlich, nicht „grün"). E1 ist statisch (kein Laufzeit-Zwang); PII-Erkennung ist heuristisch — siehe WERKBANK-Grenzen.

## Befehle
```bash
python3 gates/runner.py --target . --report GATE-REPORT.md   # Gate-Lauf
python3 gates/runner.py --target . --ci                       # CI (Exit 1 bei ROT)
npx bmad-method status                                        # BMAD-Status
```

## Erste Aktion für den Agenten
Lies `.werkbank/STATE.md`, führe den Gate-Lauf aus, melde rote Gates + Plan in ≤ 8 Zeilen, **warte auf „GO"**.
