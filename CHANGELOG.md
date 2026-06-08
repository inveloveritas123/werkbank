# CHANGELOG

> Append, neuster Eintrag oben (Gate H4).

## 2026-06-08 — T1 · Gate-Runner + 3 deterministische Gates (E1/D3/E2)
- `gates/runner.py` (+ `gates/runner`-Shim): liest `gates.yaml` (eigener YAML-Subset-Parser, kein Dependency),
  führt Gates gestaffelt aus (fail-fast bei Block-FAIL), schreibt `GATE-REPORT.md`. Nicht-implementierte Gates → SKIP (ehrlich).
- Checks (stdlib, kein LLM): **E1** EU-Routing (AWS/GCP/Azure-non-EU-Regionen, `us.*`-Model-IDs, openai.com),
  **E2** PII in Logs/Prompts/Outputs (Mail, +49-Tel, DE-IBAN, Kreditkarte+Luhn), **D3** Secret-Scan (Built-in-Regex + optional gitleaks).
- Redaction: GATE-REPORT enthält nie Klartext-Secrets/PII (per Test abgesichert).
- Self-Lauf-Schutz: Runner schließt das Gate-Tooling-Verzeichnis automatisch aus, wenn es unter dem Scan-Ziel liegt.
- **Tests:** 19/19 grün; Negativtests synthetisieren je einen Verstoß zur Laufzeit (Repo bleibt secret-/PII-frei).
- **ACT (PDCA):** Paar-Review (Reviewer ≠ Implementer) → E1-Marker erweitert (Azure-US, `us.anthropic.*`), keine Regression. Siehe `.werkbank/BENCHMARK.md`.
- Repo-Self-Gate-Lauf: **GRUEN**, 0 Block-Gates rot, 0 Secrets, 0 PII.

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
