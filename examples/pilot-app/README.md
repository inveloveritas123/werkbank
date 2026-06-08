# pilot-app — Thin-Slice (Blueprint §5)

> Der Durchstich-Beweis: *eine* winzige App end-to-end durch Workflow 01→04.
> Hier wird `npx bmad-method install` ausgeführt (BMAD = Methode/Rollen, T0-Schritt).

## BMAD-Install (reproduzierbar, nicht vendored)
BMAD ist die Methoden-/Rollenschicht (Blueprint §1: installieren, nicht nachbauen). Die
Install-Artefakte (`_bmad/`, `.claude/skills`) sind gitignored — reproduzierbar mit:

```bash
npx bmad-method@6.8.0 install --yes --directory . --modules bmm --tools claude-code \
  --communication-language German --document-output-language German --user-name WERKBANK \
  --output-folder _bmad-output
```

Status prüfen: `npx bmad-method status`.

## Status — Thin-Slice-Durchstich (01→04) LIVE
BMAD installiert + **echter Durchstich gefahren**: „Einwilligungs-Logbuch" (Art. 7 DSGVO).
- **01 Konzipieren (BMAD):** `docs/PRODUCT-BRIEF.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md` → `SPEC.md` (A-Gates grün).
- **02 Bauen:** `app/consent_ledger.py` + `tests/` (9 Tests, RED→GREEN), Ralph-Loop schließt GRUEN+promise.
- **03 Prüfen:** voller Gate-Lauf GRUEN (A1/A2/A3, C1, D3, E1/E2, F1, H4) — `GATE-REPORT.md`.
- **04 Übergeben:** PR (kein Selbst-Merge). Cross-Model-Review (opus) fand keine Live-Bugs, ergänzte Art.-7-Tests.

Lauf: `python3 app/consent_ledger.py` (Bibliothek) · Tests: `python3 -m unittest discover -s tests`.
