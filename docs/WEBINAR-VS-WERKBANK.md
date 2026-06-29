# Webinar (meinGPT Coding-Agenten) vs. WERKBANK — Vergleich & Ableitungen

`Stand: 2026-06-29 · Quelle: meinGPT-Webinar „3× schneller entwickeln mit Coding-Agenten" (Zusammenfassung + FAQ)`

> Zweck: Die durablen Erkenntnisse des Webinars gegen den Ist-Zustand von WERKBANK halten —
> was übernehmen wir, was ist an WERKBANK altbacken, und wo ist WERKBANK dem State of the Art voraus.
> Maßstab: das Agenten-Modell des Webinars selbst (**Retrieve · Act · Verify**).

---

## 1 · Die belastbaren Erkenntnisse des Webinars

- **Agenten-Modell:** Ein Agent kann **Abrufen (Retrieve)**, **Handeln (Act)**, **Verifizieren (Verify)**.
  Fehlt eine Spitze, ist es ein besserer Chatbot. *Verify* ist die Spitze, die fast alle vergessen.
- **Der Engpass hat sich verschoben:** nicht mehr Code *schreiben*, sondern Code *reviewen* (66→201 MR/Monat).
- **Kontextfenster ist die harte Grenze:** „ab 30 % kritisch, ab 50 % unbrauchbar". Rohe MCP-Outputs
  (Playwright-Snapshot ~10–15k Token) fressen Kontext → context-mode (Rohdaten in Sandbox/SQLite, nur
  Zusammenfassungen ins Modell, ~98 % Reduktion).
- **Deterministisch zuerst, LLM danach** (Token sparen, schneller, verlässlicher).
- **Routing nach Stärke** statt ein Modell für alles (Codex=Backend/Security, Claude=Frontend/Tool-Calling).
- **Governance als System, nicht als Schimpfen** — Konventionen erzwingen; „Chain"/Governance-CLI,
  die pro Commit *was* und *was bewusst nicht* gebaut wurde begründen lässt.
- **Q&A-Wahrheiten:** Metriken sind irreführend; Mensch = Schutzschild gegen Prompt Injection; keine
  spezielle „AI-Security" (Least Privilege/Container/Supply-Chain); Agent-Burnout & Review-Fatigue real;
  Prozess → Kanban, Microteams, „Ticket = Prompt".

---

## 2 · Vergleichsraster (Retrieve · Act · Verify)

| Spitze | meinGPT | WERKBANK | Urteil |
|---|---|---|---|
| **Retrieve** | Linear/Sentry/Context7/Notion-MCP, Chrome-DevTools, agent-browser, live gegen echte App | dünn: stdlib-Golden-Projects, kein Issue-MCP, kein Context7, kein Live-Browser, `STATE.md` **manuell** | **schwach** |
| **Act** | Claude Code + Codex, `/mr`, Skills, 8–9 Läufe/Tag/Dev | BMAD-Stories + Ralph-Loop, aber kreative Phasen = `claude -p`; Loop in Praxis manuell gefahren | **mittel** |
| **Verify** | CodeRabbit, `/review`, agent-browser-Smoke, Oxlint, Knip, Hooks | **44 Gates/10 Stufen, hartes Grün (SKIP=ROT), Cross-Model-Tribunal, DSGVO-Gates, menschl. Freigabe J1/J2** | **stark — der Moat** |

**Kernaussage:** meinGPT hat eine exzellente, täglich gefahrene Retrieve+Act-Maschine und schraubt
Governance nachträglich dran. WERKBANK hat die Verify/Governance-Kathedrale, aber eine dünnere
Retrieve+Act-Maschine. *Risiko: Compliance-Gates für einen Loop, den noch niemand mit voller
Intensität fährt.*

---

## 3 · Wo WERKBANK voraus ist (Moat — vom Webinar bestätigt)

1. **DSGVO als prüfbare Gates** (Art. 25/28/30/32/35). meinGPT bleibt bei „EU-Hosting" — nach unserem
   eigenen, korrekten Argument *nicht hinreichend*.
2. **Hartes Grün (SKIP/WARN ⇒ ROT).** „Nicht geprüft ist nie grün." Fehlt meinGPT.
3. **Spec-verankerte Selbstverbesserung** (Anti-Goodhart) — die Antwort auf meinGPTs eingestandenes
   Metrik-Problem.
4. **Deterministisch zuerst — bereits gebaut** (meinGPT wünscht sich das erst: „Hooks noch integrieren").
5. **Menschliche Abnahme als blockierendes Gate (J1/J2, kein Self-Sign).**

---

## 4 · Wo WERKBANK altbacken ist (ehrlich, nach Hebel sortiert)

1. **Kontext-Management** — `STATE.md` manuell, kein context-mode-Äquivalent, keine Komprimierungs-Strategie.
   Größter Rückstand.
2. **Verify gegen Synthetik** statt gegen die laufende App (stdlib-Golden-Projects statt Browser-Smoke).
3. **Claude-/`CLAUDE.md`-zentrisch** in einer Multi-Modell-Welt → `AGENTS.md` als SSoT (Cross-Tool-Standard);
   nötig, weil unser eigenes Tribunal Cross-Model will.
4. **Retrieve-Schenkel fehlt** (kein Context7/Linear/Sentry-MCP).
5. **Autonomie unter-exerziert** (Ralph-Loop da, aber manuell gefahren).
6. **Kein Dead-Code-/Slop-Gate** (Knip operationalisiert unsere „null Tech-Debt"-Regel).
7. **Skills nicht paketiert/versioniert** (skills.sh-Modell: installierbar, teilbar an Codex).

---

## 5 · Ableitungen — was wir holen (priorisiert)

| Prio | Von meinGPT | Konkret für WERKBANK | Status |
|---|---|---|---|
| 1 | context-mode | ersetzt manuelles `STATE.md` durch SQLite-State + Tool-Output-Suppression | offen |
| 2 | agent-browser / Chrome-DevTools | **C4-Gate um agent-browser-Smoke erweitert** (live gegen App, bevorzugt vor Playwright) | **erledigt (dieser PR)** |
| 3 | `AGENTS.md` als SSoT | AGENTS.md kanonisch, `CLAUDE.md` dünner `@`-Zeiger; Installer append-aware (kein BMAD-Clash) | **erledigt (dieser PR)** |
| 4 | Context7-MCP | aktuelle Lib-Docs gegen veraltetes Modellwissen | offen |
| 5 | CodeRabbit-Muster | externes „Vogelperspektive"-Review auf MR-Ebene als zusätzliches I-Gate | offen |
| 6 | Knip + anti-slop | Dead-Code-Gate, das „null Tech-Debt" erzwingt | offen |
| 7 | Linear/Issue-MCP | „Ticket = Prompt" — Spec-Pflichtfelder sind schon prompt-fähig | offen |

---

## 6 · Empfehlung

Energie für die nächsten Wochen **weg von „Gate 45–62", hin zur Maschine**: context-mode →
Live-Browser-Verify → AGENTS.md + Context7. Das hebt WERKBANK vom „governten Bauplan" (Eigenschätzung
~15 % Produkt) zum **Daily Driver mit Governance-Vorsprung** — eine Kombination, die kein anderes der
verglichenen Setups hat.

> Hinweis zur Architektur (häufige Rückfrage): **WERKBANK kollidiert nicht mit BMAD.** WERKBANK ist die
> Governance-/Souveränitäts-Schicht *über* BMAD (Methode) + kiln/Ralph (Autonomie). `AGENTS.md` enthält
> ausschließlich WERKBANK-Inhalte und *referenziert* BMAD (`_bmad/`), dupliziert es nicht. Der Installer
> fügt bei bereits vorhandener `AGENTS.md` (z. B. von BMAD `--tools codex`) nur einen abgegrenzten
> `WERKBANK`-Block ein statt zu überschreiben.
