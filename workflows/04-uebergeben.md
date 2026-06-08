# Workflow 04 — Übergeben

> Übergabe-Bündel: Spec + Architektur + Tests + Doku + Audit-Log. Kein Selbst-Merge — immer PR.

## Ablauf
1. Nur wenn Done-Tor erfüllt (Score ≥ 85, alle Block-Gates grün, keine Regression).
2. Bündel: `SPEC.md`, `ARCHITECTURE.md`, Test-Artefakte, `GATE-REPORT.md`, Audit-Log, CHANGELOG-Eintrag.
3. `BACKLOG.md`-Aufgabe auf `[x]`. `.werkbank/STATE.md` + `.werkbank/BENCHMARK.md` aktuell.
4. `git push origin werkbank-build` → **PR gegen `main`** (Mensch merged).

## Sicherung
- Kein Push bei rotem Block-Gate. Kein Selbst-Merge. Rollback bei Regression.
- Geltung beachten: intern, ohne echte Kundendaten (siehe `docs/produktivfreigabe/`).
