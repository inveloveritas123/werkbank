# AGENTS.md — Arbeit AM WERKBANK-Framework (SSoT)

> **Kanonische Quelle der Wahrheit** für jeden Coding-Agenten (Claude, Codex, …), der an *diesem*
> Repo arbeitet. `CLAUDE.md` verweist per `@AGENTS.md` hierher — **nicht** duplizieren.
> Unterscheidung: Diese Datei betrifft die Entwicklung **des Frameworks**. Die Datei, die in
> Zielprojekte ausgerollt wird, ist `templates/AGENTS.werkbank.md`.

## Was WERKBANK ist
EU-souveräne Governance-/Souveränitäts-Schicht **über** BMAD (Methode) + Ralph/kiln (Autonomie).
**Kein Ersatz** für BMAD. Framework-Code ist **stdlib-only** (keine Laufzeit-Abhängigkeiten);
Dev-Tools (ruff/mypy/coverage/bandit/pytest) sind dev-only (`requirements-dev.txt`).

## Harte Regeln (nicht verhandelbar)
- **Nie direkt auf `main`** — Feature-Branch + PR, **kein Selbst-Merge**, Mensch gibt frei.
- **Hartes Grün:** ein Pflicht-Gate des aktiven Profils ist nur grün bei Status PASS; FAIL **oder**
  SKIP/WARN ⇒ ROT. „Nicht geprüft ist nie grün."
- **Keine Secrets/PII** im Repo — nur Env-Referenzen. Kein `curl | bash` in Code/Doku empfehlen.
- **Verification-first:** keine Änderung ohne grüne Tests/Gates als Orakel. Assertions nie aufweichen.
- **Selbstverbesserung kontrolliert:** kleinste Änderung, größter Hebel, messen, Regression prüfen,
  sonst zurückrollen — gegen `golden-projects/`, nicht frei. Spec-verankert, **keine Metrik optimieren**.

## Dev-Befehle
```bash
make dev-setup   # Dev-Tools installieren (pip install -r requirements-dev.txt)
make check       # Pre-Push: lint + type + sast + test (schnell, lokal)
make all         # check + harter Gate-Lauf (Profil werkbank_self)
python3 -m unittest discover -s gates/checks/tests -p "test_*.py"   # nur Tests (stdlib, ohne Dev-Tools)
python3 gates/runner.py --target . --report GATE-REPORT.md --profile werkbank_self --ci
```
> Ohne ruff/mypy/coverage/bandit ist `werkbank_self` lokal ROT (SKIP=ROT) — das ist gewollt.
> Die volle Grün-Prüfung macht die CI (`.github/workflows/werkbank-gates.yml`).

## Modell-Tier-Routing (verbindlich beim Spawnen von Subagenten)
Quelle der Wahrheit: `orchestrator/werkbank.tiers.json`. doku/summary/lint → **haiku**;
impl/test/refactor/build → **sonnet**; plan/architecture/review/security/privacy/judge → **opus**.
Paar-Review **immer** mit anderem Modell als der Implementer (Cross-Model).
```bash
python3 orchestrator/tier_router.py --table
python3 orchestrator/autolabel.py "<aufgabentext>"
```

## Konventionen
- **CHANGELOG.md**: append, **neuster Eintrag oben** (Gate H4).
- **Modell-Versionen pinnen** (kein `latest`/`*` — Gate F1).
- Neue Gates: Check unter `gates/checks/`, Test unter `gates/checks/tests/test_*.py`, Eintrag in
  `gates.yaml`; Pflicht-Zuordnung in `gates/pflichtenheft.yaml` (nur in ein Profil aufnehmen, wenn das
  Gate real implementiert ist — sonst macht es Profile ROT).
- Deutsche Agentennamen: `Junge` (Coordinator), `Wächter` (Verifier).

## Erste Aktion für den Agenten
Lies `.werkbank/STATE.md` und `BACKLOG.md`, mach den Gate-Lauf, melde Stand + Plan in ≤ 8 Zeilen,
**warte auf „GO"**.
