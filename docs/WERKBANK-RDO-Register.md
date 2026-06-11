# WERKBANK — Risiko-, Entscheidungs- & Offene-Punkte-Register (RDO)

`R-WERKBANK-RDO-REGISTER` · 2026-06-05 · ZUKUNFTSBUND GmbH · **lebendes Dokument, append-only**

> Zweck: das eine Dokument, das das große Ganze festhält, Entscheidungen protokolliert und Drift/Feature-Creep sichtbar macht — auf dem *Produkt* **und** auf dem *Framework selbst*.

---

## 0 · North Star (nicht vergessen)
Produktiv nutzbare, **EU-souveräne**, best-dokumentierte und getestete Software — von Agenten konzipiert/gebaut/geprüft, **übergabefertig**, freigegeben durch Robert. **Erster realer Lauf: die App-Druck-Plattform (§7).** Erfolg = die Plattform läuft, ist getestet/dokumentiert, und das Framework hat dabei *nur das* gelernt, was sie wirklich gebraucht hat.

---

## 1 · Bestätigte Entscheidungen (Log)
- **D-01** Union statt Ersatz: BMAD-Workflow + KOLONIE-Infra. *(R3)*
- **D-02** Lean-Orchestrator: Junge hält Task-Graph + Zeiger, Worker halten Arbeitskontext isoliert. **Gilt auch für den Kanzler.** *(R9)*
- **D-03** Bau-Isolation: großes/mehrdienstliches/kundennahes Projekt → **Incus**-Systemcontainer; kleines, zustandsloses Tool → **Docker**-App-Container. *(R9)*
- **D-04** Quality-Gates deterministisch zuerst, LLM nur auf Durchläufer. *(R6)*
- **D-05** Selbst-Optimierung nur „propose, never apply"; `_invariants.md` unantastbar; nur `final` produktiv. *(R7)*
- **D-06** Kanzler als **Regler, nicht Schalter**: Grün autonom / Gelb handeln+melden / Rot vorschlagen+eskalieren. *(R8)*
- **D-07** Skills in git, an **sinnvollen Meilensteinen** aktualisiert (nicht im Sekundentakt), temp → Freigabe → final. *(R8)*
- **D-08** **Access-/Capability-Modell** als versionierte `access-policy.yaml`: deny-by-default, Least-Privilege, Matrix Actor × Ressource × Aktion. *(R9, neu)*
- **D-09** Per-Projekt-Scaffold = Container + Repo/Branch + House-Profil + Gates + Branchen-Modul + Access-Eintrag + Kanzler-Registrierung (BMAD ist *eine* Zutat). *(R9)*

---

## 2 · Offene kritische Fragen & Risiken (priorisiert — Entscheidung durch Robert)

| # | Risiko / Frage | Warum es weh tut | Vorschlag |
|---|---|---|---|
| **K-01** | **Framework-Feature-Creep.** 5 Runden Design, 0 Produkt. | Wir optimieren das Werkzeug statt zu liefern — exakt der Drift, den wir bekämpfen. | **Thin-Slice-Disziplin (§6).** Pilot bauen, Framework nur erweitern, wenn der Pilot es erzwingt. |
| **K-02** | **Human-Approval-Bottleneck.** Alles (Gates, Loop, Kanzler-Rot, Scaffolds) braucht Roberts Freigabe. | Robert = Single Point of Failure für *Durchsatz*. Urlaub/Stress → Stillstand oder Gummistempel. | Freigaben **batchen**; Zeitfenster + Auto-Eskalation; Default **fail-safe** (stehenbleiben), nicht fail-open; ggf. Stellvertreter-Regel. |
| **K-03** | **Spec-Validität (Garbage-Spec).** Gates prüfen, ob Code zur Spec passt — nicht, ob die Spec *richtig* ist. | Perfekt gebautes Falsches. Die tiefste Lücke. | Spec-Review mit *Business*-Stakeholder; Abnahme gegen echte Nutzer-Outcomes, nicht nur interne Kriterien. |
| **K-04** | **Kanzler-Credential-Blast-Radius.** Daemon mit Tokens für Asana + GitHub + M365. | Lohnendstes Einzel-Kompromittierungsziel des ganzen Systems. | Kurzlebige, eng-scoped Tokens via Secret-Manager; kein Standing-Admin; an `access-policy.yaml` gebunden. |
| **K-05** | **Always-on-Kosten.** Kanzler + Dauer-Agenten verbrennen 24/7 Tokens. | Lineare Kosten-Schwäche kehrt durch die Hintertür zurück. | Heartbeat-Kadenz statt Dauerlauf; Routine deterministisch; harter Perioden-Budget-Cap + Kill-Switch. |
| **K-06** | **Brownfield.** Design ist greenfield-lastig; Kunden haben Altsysteme. | Dein Beratungs-Alltag ist Bestandscode, nicht grüne Wiese. | Ingestion/Verstehens-Schritt für Bestandscode (Context-Engine/OpenSpec-Muster) vor dem Spec-Schritt. |
| **K-07** | **Fleet-/Versions-Management.** Viele Kundenprojekte auf House-Profil vN; Upgrade auf vN+1? | Stiller Bruch bestehender Projekte bei Profil-Änderung. | Pro-Projekt **Pinning** + Opt-in-Upgrade, kein erzwungenes Nachziehen. |
| **K-08** | **DR / Break-Glass.** Fehl-Autonomie oder korruptes Repo. | Code-Rollback ja — aber Ops-DR, Backups, „alles stoppen"-Schalter fehlen. | Dokumentierter Not-Aus; Backup-/Restore-Drill; unveränderliches Audit als Forensik-Basis. |
| **K-09** | **Review-Fatigue / Trust-Kalibrierung.** Mensch reviewt AI-Output im Akkord. | Übergabe-Bündel hilft, aber Mensch muss fremden Code verstehen → Ermüdung → Wegschauen. | Risiko-basiertes Review (nur Rot/Gelb tief prüfen); Trust-Score pro Agent steuert Review-Tiefe. |

---

## 3 · Access-/Capability-Modell (Skelett · `access-policy.yaml`)
Prinzip: **deny-by-default**, Least-Privilege, explizite Grants. Durchgesetzt auf drei Ebenen: Netz (vmbr-Isolation) + Token-Scope + MCP-Allow-Lists.

| Actor | Repo | Container | MCP-Server | Modelle | Tenant-Daten | Board | Externe API |
|---|---|---|---|---|---|---|---|
| Robert (GF) | admin | admin | admin | admin | admin | admin | admin |
| Kanzler | read + PR | start/stop (eigene) | read | Tier-begrenzt | **read** | read+write | scoped |
| Junge | read+write (Projekt) | nutzen | read | Tier-begrenzt | nein | read | nein |
| Implementor | write (Branch) | nutzen | nein | Sonnet | nein | nein | nein |
| Wächter | read | nein | read | LLM-Gate-Tier | nein | read | nein |
| Kunde/Nutzer | nein | nur eigener | nein | nein | **nur eigene** | eigenes | nein |

→ Jeder neue Projekt-Scaffold (D-09) legt automatisch den passenden Actor-Eintrag an.

---

## 4 · Bau-Isolations-Policy (Entscheidungsregel)
- **Incus (Systemcontainer):** mehrere Dienste · persistenter Zustand · kundennah · multi-tenant · eigene Netz-/Ops-Anforderung.
- **Docker (App-Container):** Einzel-Tool · zustandslos · intern · kurzlebig.
- Grenzfall → Default Incus (mehr Isolation), dokumentiert im Projekt-Scaffold.

---

## 5 · Distribution: „mein optimales Claude-Code-Setup" als modulares Paket
Ziel: jeder zieht es sich in sein Claude — **nicht jeder braucht alles**.
- **Repo** (z. B. `werkbank`), modular: `core` · `gates` · `kanzler` · `branch-modules` · `sovereignty` · `distribution`.
- **Bezug:** `git clone` / `degit` / `npx werkbank init`.
- **Interaktiver Installer (die „Fragestellungen"):**
  1. Greenfield oder Brownfield?
  2. Projektgröße → Incus oder Docker (D-03)?
  3. Branche? → passendes Modul (Bau/Finanzen/GIS/IoT/Public-Sector …)
  4. Kanzler nötig (autonome Ops/QA) oder nur Pipeline?
  5. Multi-Tenant?
  6. EU-Routing erzwingen?
  7. Skill-Level (beeinflusst Planungstiefe)?
- Installer setzt daraus die richtige Modul-Teilmenge + `--set`-Flags zusammen. Spiegelt BMADs `npx … install`-Logik.

---

## 6 · Meta-Risiko & Disziplin: Thin-Slice statt Weiterdesign
**Stoppregel:** Bevor eine weitere Framework-Schicht entworfen wird, muss der Pilot (§7) einen End-to-End-Durchlauf durch einen *minimalen* Schnitt geschafft haben (1 echtes Feature: Konzipieren→Bauen→Prüfen→Übergeben, mit EU-Routing + den Pflicht-Gates). Was der Pilot **nicht** braucht, wird **nicht** gebaut. Der Pilot ist die Eval des Frameworks.

---

## 7 · Pilot: App-Druck-Plattform
**Roberts Anforderungen → wo das Framework sie abdeckt:**
- *Best-dokumentiert & getestet vor Freigabe* → Übergabe-Bündel (SPEC/ARCH/TASKS/ADR/tests/GATE-REPORT/AUDIT-LOG/README+RUNBOOK) + Gate C2 Coverage + Gate H3 Doku. Freigabe = Phase-04-Freigabe.
- *Drift im Blick* → Drift-Audit-Gate (H6), living-spec.
- *Feature-Creep im Blick* → Spec-Feld „Scope-Grenzen" + Gate A5 (kein Code außerhalb Scope) + ein **Scope-Creep-Detektor** (neue Stories gegen North-Star prüfen).
- *Das große Ganze* → Spec-Feld „Outcomes" als North-Star, vom Kanzler im Briefing wiederholt.

**OFFEN (K-Pilot):** Was *ist* die App-Druck-Plattform genau? Davon hängen Branchen-Modul + domänenspezifische Gates ab. Optionen: (a) Print-on-Demand / Druckdienst (Bestellungen, Druckdateien, Fulfillment, Zahlung/PCI), (b) Plattform zum schnellen *Erzeugen/Ausliefern von Apps*, (c) etwas anderes. → **vor Scaffold klären.**
