# CHANGELOG

> Append, neuster Eintrag oben (Gate H4).

## 2026-06-08 — T0 · Fundament
- Ziel-Struktur aus Blueprint §3 angelegt: `agents/` (junge, waechter, kanzler[disabled], privacy-analyst),
  `workflows/` (01-konzipieren … 04-uebergeben), `gates/checks/`, `templates/`
  (SPEC, ARCHITECTURE, TASKS, GATE-REPORT, AUDIT-LOG.schema.json), `examples/pilot-app/`,
  `.github/workflows/werkbank-gates.yml` (CI-Stub).
- `privacy/`: 11 DSGVO-Artefakt-Vorlagen aus `DSGVO-ARTEFAKTE.md` als einzeln befüllbare Dateien.
- BMAD installiert ins `examples/pilot-app/` (core + bmm v6.8.0, 44 Skills, 6 Rollen) — Methoden-/Rollenschicht.
  Install-Artefakte gitignored (reinstallierbar, Blueprint §1 "installieren, nicht nachbauen").
- `.werkbank/STATE.md` initialisiert (crash-sicherer Pipeline-State; lokal/gitignored).
- Branch `werkbank-build` von GitHub-`main` (@9807fa7).
