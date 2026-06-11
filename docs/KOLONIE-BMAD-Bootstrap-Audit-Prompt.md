# KOLONIE × BMAD — Bootstrap-Audit & Umbau-Analyse

> **Verwendung:** Diesen kompletten Text in Claude Code auf dem Server (SSH, User `meister`) als ersten Prompt einer frischen Session einfügen. Claude Code arbeitet damit **read-only** und liefert am Ende einen Report + Entscheidungsmenü. Es wird **nichts** installiert oder verändert, bis du explizit `GO` sagst.

---

## ROLLE & ZIEL

Du bist Senior Platform-Engineer und auditierst mein bestehendes KOLONIE-Setup, um es in Richtung eines **optimalen agentischen Entwicklungssystems** umzubauen. Zielbild: die **BMAD-Methodik (Spec → PRD → Architektur → Stories → Implementierung → QA-Gates)** als Workflow-Layer **über** meiner bestehenden Infrastruktur — ohne meinen Moat aufzugeben (EU/DSGVO-Datensouveränität, Self-Hosting, 6-Tier-Routing, Budget-Kontrolle, Multi-Tenant).

Klare Arbeitsteilung, die du in der ganzen Analyse durchhältst:
- **BMAD-Territorium:** Planung, Spezifikation, Story-Zerlegung, Implementierung, Test/QA.
- **KOLONIE-Territorium:** Deploy, Staging-Gate, Last/Monitoring, Multi-Tenant-Bereitstellung, EU-Routing, Budget, Datensouveränität.

Deine Aufgabe ist **Analyse + Vorschlag**, nicht Umsetzung.

---

## HARTE REGELN (nicht verhandelbar)

1. **Read-only.** Keine Installation, kein `npx ... install`, kein Edit, kein Commit, kein Service-Restart, kein `docker`-Eingriff. Nur lesen, auflisten, prüfen. Einzige Schreibaktion: **ein** Report-Markdown am Ende (siehe AUSGABE).
2. **Keine Secrets ausgeben.** Bei Config-Dateien (`config.json`, `.env`, Tokens, API-Keys): nur **Existenz, Struktur und Schlüssel-Namen** bestätigen — niemals Werte drucken, loggen oder in den Report schreiben. Bei Fund von Secrets im Klartext an falscher Stelle: als Finding melden, Wert maskieren.
3. **DSGVO/EU-Souveränität ist Pflichtkriterium.** Jeder Vorschlag, der einen Modell-Call oder Kundendaten potenziell über Nicht-EU-Endpunkte schickt, wird **explizit als solcher markiert** inkl. Alternative.
4. **Nichts erfinden.** Wenn ein erwarteter Pfad/Service fehlt oder du unsicher bist: als „nicht gefunden / unklar" kennzeichnen, nicht raten.
5. **Idempotent denken.** Vorschläge müssen wiederholbar/reversibel sein; keine Big-Bang-Umbauten.

---

## ARBEITSPRINZIPIEN (meine Standards)

- Erst reflektieren, dann analysieren.
- Minimal & wiederverwendungsgetrieben — Bestehendes nutzen statt neu bauen.
- Null technische Schulden; pragmatische Flexibilität vor verfrühter Abstraktion.
- Selbsterklärend für künftige Maintainer.
- Trade-offs eskalieren mit Pro/Contra, nicht still entscheiden.
- Am Ende einmal fragen, dann stoppen.

---

## PHASE 1 — DISCOVERY (Inventar, read-only)

Starte, falls vorhanden, mit meiner Session-Start-Konvention: lies `/zukunftsbund/INDEX.md` und `/zukunftsbund/ki/CHANGELOG-ki.md`, um Stand und Konventionen zu erfassen. Die folgenden Landmarken sind **Stand laut meiner Doku — verifizieren, nicht vertrauen**.

**1.1 System & BMAD-Voraussetzungen**
- OS/Kernel, RAM, Disk frei.
- `node --version` (BMAD braucht ≥ v20.12), `python3 --version` (≥ 3.10), `uv --version`, `git --version`, `docker --version`.
- Ist BMAD schon irgendwo installiert? Suche nach `bmad`, `.bmad`, `bmad-method`, `bmm` in Home, Projektordnern, `package.json`.

**1.2 KOLONIE-Infrastruktur (verifizieren)**
- Proxmox-Host, Container-Topologie: Junge (CT 101, Orchestrator), claw-coder (CT 201), claw-architect (CT 202), golden template (CT 999) — laufend? Rollen?
- Netze: `vmbr1` 10.10.1.0/24 (mgmt), `vmbr2` 10.20.0.0/24 (Worker, kein Internet), `wg0` 10.10.0.0/24 (VPN). Stimmen Isolation und „kein Internet" für Worker?
- LLM-Proxy auf `:8080` inkl. Budget-API — erreichbar? Welche Backends hängen dran?
- Gitea `:3000`, Dashboard `:5000` — Status, welche Repos?
- `config.json` unter `/opt/kolonie/director/config.json` — **nur** bestätigen, dass es existiert und welche Schlüssel-Kategorien es enthält (z. B. „enthält Keys für: anthropic, mistral, requesty"). **Keine Werte.**

**1.3 Claude-Code-Konfiguration (der DSGVO-Knackpunkt)**
- `~/.claude/`, vorhandene `CLAUDE.md` (projektweit und global), installierte Skills, registrierte Subagents.
- **Wie erreicht Claude Code aktuell die Modelle?** Prüfe `ANTHROPIC_BASE_URL`, Bedrock-Region (erwartet: Frankfurt/`eu-central-1` für Souveränität), ob ein Proxy/Router (Requesty EU `router.eu.requesty.ai`) vorgeschaltet ist — oder ob direkt die US-Anthropic-API genutzt wird. Das entscheidet, ob mein Implementierungs-Tier souverän ist.

**1.4 Meine 6 Subagents**
- Verifiziere `/zukunftsbund/ki/Ressourcen/Subagents/` und lies die Definitionen. Fasse pro Agent zusammen: Rolle + zugewiesenes Modell (erwartet: explorer/Haiku, researcher/Haiku, implementer/Sonnet, reviewer/Sonnet, architect/Opus, tester/Sonnet).
- Gibt es Beobachtungen unter `.../beobachtungen/` bzw. eine `BILANZ-*.md`? Stand?

**1.5 Workflow- & Konventions-Layer**
- Existiert ein **pro-Feature**-Ablauf (PRD → Stories → Done-Kriterien → QA-Gate) — oder läuft es ad-hoc + CHANGELOG?
- Datei-Präfixe (R-/L-/LH-), append-only CHANGELOG, INDEX-first — wo dokumentiert, wie konsequent gelebt?
- Coding-Best-Practices-Dokument, Brand-Voice, LLM-Routing-Definition (6-Tier S1–S6) — wo abgelegt?

**1.6 Qualitäts- & Test-Stack (Ist-Zustand)**
- Vorhandene Test-Runner (Vitest/Playwright/k6/axe-core o. ä.), Coverage, Lint, CI-Konfiguration (GitHub Actions / Gitea Actions).
- **Werden Gates erzwungen** (Merge/Deploy blockiert ohne grün) oder sind sie optional?

---

## PHASE 2 — GAP-ANALYSE

Vergleiche Ist (Phase 1) gegen das Zielbild. Arbeite mindestens diese Achsen ab:

1. **Workflow-Ritus:** Fehlt der erzwungene Spec→Story→QA-Fluss pro Feature? Wo genau bricht heute der Kontext über Sessions (Context-Drift)?
2. **Rollen-Überlappung:** Welche meiner 6 Subagents decken welche BMAD-Rollen (PM, Architect, Scrum Master, Dev, QA) ab? Wo entstünde **Doppelung** bei einer BMAD-Einführung, wo eine echte Lücke?
3. **DSGVO-Achse:** Läuft die Implementierung heute über EU-Endpunkte oder US-API? Wie ist die Datenresidenz für Kunden-Repos? Wo ist BMAD (das nativ Claude Code = US annimmt) mit meiner Souveränität in Konflikt — und wo nicht (die Markdown-Workflows sind modell-agnostisch und könnten gegen mein EU-Routing laufen)?
4. **Gate-Achse:** Sind meine Quality Gates (Unit/Integration, E2E, a11y/BITV/WCAG, Concurrency, Staging-Smoke, Last) als erzwungene Gates verdrahtet oder nur vorhanden?
5. **Grenze BMAD↔KOLONIE:** Was deckt BMAD ab (bis Test), was muss in KOLONIE bleiben (Deploy/Ops/Multi-Tenant/Souveränität)?

---

## PHASE 3 — UMBAUVORSCHLÄGE

Liefere eine **priorisierte** Liste konkreter Vorschläge. Für **jeden** Vorschlag:
`Was` · `Warum` · `Aufwand (S/M/L)` · `Trade-offs (Pro/Contra)` · `DSGVO-Berührung (ja/nein + Mitigation)` · `Reversibel?`

Decke dabei mindestens ab:
- **(a) BMAD-Integration:** Welche Module (Start mit BMM-Core; TEA für Tests; BMB für eigene Agenten) — und was bewusst weglassen, um keinen Overhead zu erzeugen.
- **(b) Rollen-Mapping:** Konkretes Mapping BMAD-Rollen ↔ meine 6 Subagents; was wird ersetzt, was bleibt, was wird zusammengelegt.
- **(c) EU-Routing-Erhalt:** Wie BMAD-Workflows gegen mein souveränes Backend laufen (Claude-Tier → Bedrock Frankfurt; restliche Tiers → Requesty EU / LLM-Proxy), statt gegen die US-API. Konkret: welche Env/Config-Schalter.
- **(d) Konventions-Verdrahtung:** Wie meine Präfixe, append-only CHANGELOG, INDEX-first und Coding-Best-Practices in BMADs Config/Agenten verankert werden (eine Quelle der Wahrheit, kein widersprüchliches CLAUDE.md daneben).
- **(e) Quality-Gate-Verdrahtung:** Meine Testpyramide als erzwungene BMAD-QA/TEA-Gates (Definition of Done = QA-Sign-off gegen Akzeptanzkriterien pro Story).
- **(f) Ops-Grenze:** Was nach dem Test in KOLONIE bleibt (Staging-Gate, k6, Monitoring, Multi-Tenant-Deploy) und wie die Übergabe BMAD→KOLONIE aussieht.

---

## PHASE 4 — SPEZIALAUFTRAG: BMAD auf meine Anforderungen vordefinieren

Beantworte konkret und mit Beleg aus der lokalen Doku bzw. (falls Netz erlaubt) den offiziellen BMAD-Quellen:
1. Welche **Install-Config-Optionen** (`--set bmm.<key>=<value>`) sind für mich relevant?
2. Kann **BMad Builder (BMB)** ein **House-Profil** erzeugen, das meine Anforderungen (DSGVO-Gates, EU-Routing-Hinweise, Konventionen, Mittelstand-Kontext) als eigene Agenten/Workflows kodiert?
3. Entwirf — **als Vorschlag, nicht ausführen** — die Struktur eines solchen House-Profils: welche Agenten/Workflows ich anpasse, welche Felder ich setze, und einen Skizzen-Brief, aus dem Claude Code dieses Profil später generieren könnte.

---

## AUSGABE

1. **Report-Datei** (einzige Schreibaktion): Lege einen Markdown-Report nach meiner Konvention an. Schlage den Pfad/Namen anhand der gefundenen INDEX-/Präfix-Konvention vor (Default-Vorschlag, falls unklar: `/zukunftsbund/ki/Ressourcen/R-KOLONIE-BMAD-AUDIT-<YYYY-MM-DD>.md`). Struktur: Discovery → Gap-Analyse → Umbauvorschläge (priorisiert) → BMAD-House-Profil-Skizze.
2. **CHANGELOG:** Schlage die passende append-only-Zeile für `CHANGELOG-ki.md` **vor**, committe sie aber **nicht**.
3. **Konsolen-Zusammenfassung:** Gib mir am Ende eine kompakte Zusammenfassung (max. ~20 Zeilen).

---

## ABSCHLUSS

Stelle mir am Ende **ein** Entscheidungsmenü mit den 3–5 Weichen, die ich stellen muss (je als klare Wahl mit deiner Empfehlung in 1 Satz). Dann **stopp** und warte auf mein `GO`, bevor irgendetwas umgesetzt wird.
