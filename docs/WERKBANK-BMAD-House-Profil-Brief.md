# WERKBANK — BMAD House-Profil · Anforderungs-Brief

`R-WERKBANK-HOUSE-PROFIL-BRIEF` · 2026-06-05 · ZUKUNFTSBUND GmbH

> **Zweck:** Eingabe-Brief, aus dem **Claude Code via BMad Builder (BMB)** eine vorkonfigurierte, auf ZUKUNFTSBUND zugeschnittene BMAD-Variante generiert — das *House-Profil*. Der Brief ist selbst spec-driven aufgebaut (die sechs Pflichtfelder), damit BMB ihn direkt als Spec konsumieren kann.

---

## 0 · Auftrag an Claude Code / BMB
Generiere ein **BMAD-House-Profil** für ZUKUNFTSBUND auf Basis dieses Briefs. Reihenfolge: **erst** der separate Bootstrap-Audit (Ist-Zustand, read-only), **dann** ein Profil-**Vorschlag** zur Freigabe, **erst nach `GO`** die Generierung. Kein Auto-Apply.

---

## 1 · Outcomes — was am Ende wahr sein muss
- Vanilla-BMAD wird zur **House-Variante**, die meine Konventionen, EU-Routing, DSGVO-Gates, die 4-Phasen-Pipeline und den Übergabe-Vertrag **fest verdrahtet** — nicht bei jedem Projekt neu konfiguriert.
- Reproduzierbar via `npx bmad-method install` + Profil + `--set`-Flags, ohne manuelles Nachziehen.
- Der Output **jedes** Projekts ist **übergabefertig an einen menschlichen Entwickler** (Artefakt-Bündel, siehe §7).
- Das Profil ist **universell**: pro Kundenprojekt nur Branchen-Modul + Pflichtblöcke aktivieren, kein Neubau.

## 2 · Scope-Grenzen
- **IN:** Planung → Implementierung → Test. Module **BMM** (Core), **TEA** (Tests/Gates), **BMB** (Profil-Erzeugung). Konkret: Agenten-Definitionen, Workflows, PRD/Spec-Template, Gate-Definitionen, Routing-Hinweise, Konventions-Config.
- **OUT:** Deploy, Staging-Gate, Last/Monitoring, Multi-Tenant-Bereitstellung → bleibt **KOLONIE**. **Kein zweites `CLAUDE.md`** neben BMADs Config — eine Quelle der Wahrheit.

## 3 · Constraints — harte Leitplanken
- **EU/DSGVO (nicht verhandelbar):** jeder Modell-Call über EU-Endpunkt — Claude-Tier → **Bedrock Frankfurt**, übrige Tiers → **Requesty EU / Mistral EU**. Agenten müssen **backend-agnostisch** sein und über den **LLM-Proxy (:8080)** routen. Gate **E1** erzwingt das.
- **Modell-Tiers:** Haiku 80 % / Sonnet 15 % / Opus 5 %. Tiers **S5/S6 confirm-gated** mit Kostenschätzung.
- **Sicherheit:** Secrets nur via Env/Secret-Manager, nie im Code/Repo. Kein `curl | bash`. Produktiv-Modellversionen **gepinnt**.
- **Konventionen:** Datei-Präfixe **R-/L-/LH-**, **append-only** `CHANGELOG-ki.md`, **INDEX-first** Session-Start (`/zukunftsbund/INDEX.md` + `/zukunftsbund/ki/CHANGELOG-ki.md`).
- **Coding-Best-Practices (9 Regeln):** 1) erst reflektieren · 2) minimal & wiederverwendungsgetrieben · 3) null Tech-Debt · 4) selbst-dokumentierend · 5) Doku-Disziplin (nur komplexe Strukturen) · 6) Drop-in-Vollständigkeit + Integrationsnotizen · 7) opportunistische Verbesserung · 8) Trade-offs mit Pro/Contra eskalieren · 9) einmal fragen, dann stoppen. **Pragmatik vor verfrühter Abstraktion.**
- **Sprache:** Deutsch. **Naming:** deutsche Agentennamen (Coordinator = `Junge`, Verifier = `Wächter`).

## 4 · Prior Decisions — entschieden, mit Begründung
- **Union statt Ersatz.** BMAD liefert die überlegene Workflow-/Dokumentenschicht; KOLONIE liefert Souveränität/Infra. Begründung: 6 von 9 von BMAD selbst benannten Schwächen löst KOLONIE direkt.
- **Rollen-Mapping (Soll):**
  - `Junge` (Coordinator) — **behalten**, Orchestrierung/Routing/Budget.
  - Analyst/PM — **BMAD übernehmen** (`researcher`/Haiku als Vorstufe). Lücke heute.
  - Architect — `architect`/Opus, **BMAD-Workflow** übernehmen.
  - Scrum Master — **BMAD übernehmen**. Lücke heute.
  - Developer — `implementer`/Sonnet, **BMAD-Dev-Loop** ersetzt Ad-hoc-Prompt.
  - Verifier — `Wächter` (fusioniert `tester` + `reviewer`), führt **TEA + 62 Gates + Vier-Augen** aus.
  - Explorer — `explorer`/Haiku, **behalten** (billige Recon; BMAD fehlt das).
  - Memory — MCP-Layer, **behalten** (Grounding, Living-Spec-Basis).
- **Living-spec statt static-spec:** über das **Drift-Audit-Gate (H6)** (PRD ↔ Implementierung pro Epic) — meldet nur *beabsichtigte* Verhaltensänderungen, kein Voll-Sync (Token-sparend).
- **Gates deterministisch zuerst, LLM danach.** Senkt Kosten und adressiert die „lineare Token-Skalierung".

## 5 · Task-Breakdown — was BMB generieren soll
1. **Agenten** gemäß Mapping (§4) — als BMAD-Agenten-Configs, deutsche Namen, Tier-Zuordnung.
2. **PRD/Spec-Template** mit den **sechs Pflichtfeldern**: Outcomes · Scope-Grenzen · Constraints · Prior Decisions · Task-Breakdown · Verification — schema-validiert (Gate **A1**).
3. **Workflow** *Konzipieren → Bauen → Prüfen → Übergeben* mit **drei menschlichen Freigabe-Checkpoints** (Spec-Review · Plan-Review · Execution-Freigabe).
4. **TEA-Gate-Set:** die **62 Gates** (Kategorien A–I) mit Tags `BLOCK/WARN/LLM/BRANCHE`; `Wächter` als Runner; als **blockierende Gitea-Action** vor Merge/Deploy. Quelle: WERKBANK-Framework, Abschnitt 05.
5. **Living-Spec-Hook:** Drift-Audit-Gate (H6), beabsichtigt vs. unbeabsichtigt.
6. **Übergabe-Bündel-Generator** (siehe §7-Artefakte).
7. **Branchen-Module** (zuschaltbar pro Kunde): Bau/VOB · Finanzen/§14 UStG/DATEV · Recht/Aufbewahrungsfristen · GIS · IoT · Public-Sector/BITV.
8. **Routing-Config + confirm-gate-Logik** (EU-Endpunkte, Tier-Schwellen, Kostenschätzung bei S5/S6).
9. **Ablage-/Sync-Konvention:** git, Markdown-Quelle **+ HTML-Begleitdatei (stets beides)**, Promotion `temp → Vier-Augen → final`, nur `final` produktiv.

## 6 · Install-/Config-Flags — Startvorschlag
```
npx bmad-method install \
  --modules bmm,tea,bmb --tools claude-code --yes \
  --set bmm.user_skill_level=expert \
  --set bmm.project_knowledge=<von BMB vorschlagen>
```
BMB soll die vollständige, für mich passende `--set`-Liste **vorschlagen** (nicht raten) und begründen.

## 7 · Verifikation — Akzeptanzkriterien (= Definition of Done)
- Ein **Pilot-Feature** läuft komplett durch alle vier Phasen + drei Freigaben.
- Gate **E1** erzwingt EU-Endpunkt; im Trace **kein** US-Modell-Call.
- **Übergabe-Bündel vollständig:** `SPEC.md` · `ARCHITECTURE.md` · `TASKS.md` · `/decisions/*.md` (ADRs) · `/tests/*` (grün) · `GATE-REPORT.html` · `AUDIT-LOG.jsonl` · `README` + `RUNBOOK`.
- Konventionen (Präfixe, append-only CHANGELOG) werden **automatisch** eingehalten.
- Kosten-Telemetrie zeigt: deterministische Gates **ohne** Token-Verbrauch, LLM nur auf Durchläufer.

## 8 · Nächster Schritt
1. Bootstrap-Audit fahren (`KOLONIE-BMAD-Bootstrap-Audit-Prompt.md`).
2. Diesen Brief an BMB geben → Profil-**Vorschlag**.
3. Vorschlag reviewen → `GO`.
4. Profil generieren, Pilot-Feature gegen §7 prüfen.
