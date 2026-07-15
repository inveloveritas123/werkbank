# Starter-Stacks (Projekt-Startvorlagen)

Greenfield heißt nicht Rohbau: Für wiederkehrende Projekttypen startet WERKBANK von einer
**geprüften, lauffähigen Startvorlage** statt von null. Ein Starter-Stack ist ein Repo, das die
tragende Architektur bereits mitbringt (Auth, Schichten, Async-Pipeline, Deploy) — die
BMAD-Architektur-Phase entscheidet dann nur noch **ob er passt**, nicht wie man ihn baut.

## Prinzip (wie branch-modules: Entscheidung erzwingen, nicht raten)

1. **Wahl in der Konzept-Phase:** Workflow `01-konzipieren` prüft nach der Architektur gegen
   die Eignungs-Kriterien des Stacks (`stack.yaml: eignung`) und dokumentiert die Entscheidung
   **im SPEC als Architektur-Entscheid** — auch ein bewusstes „kein Stack, echtes Greenfield"
   ist eine dokumentierte Entscheidung.
2. **Gates unverändert:** Ein Starter-Stack umgeht kein einziges Gate. Er startet lediglich mit
   mehr bestandener Substanz (Tests, Auth, Migrations) — das GATE-REPORT bleibt der Maßstab.
3. **Vorlage bleibt Vorlage:** Projekte klonen den Stack und initialisieren ihn
   (`init`-Kommando aus `stack.yaml`); Verbesserungen, die generisch sind, fließen als PR in
   das Vorlagen-Repo zurück — nie umgekehrt Projekt-Spezifika in die Vorlage.

## Einen Stack registrieren

`starter-stacks/<name>/stack.yaml`:

```yaml
name: backend-go-graphql
repo: https://github.com/zkbandfriends/ZukunftsApp_Vorlage_Backend_Framework
desc: "Go + GraphQL + Postgres Backend (aus filumio_backend extrahiert)"
eignung_doc: docs/EIGNUNG.md        # Pflicht: dokumentierte Passung/Grenzen im Stack-Repo
init: ./scripts/init_project.sh     # macht aus der Vorlage das benannte Projekt
verify: "make db-up && make test"   # muss auf frischem Klon grün sein
```

Aktivieren pro Projekt: `starter_stack: <name>` in den Settings (oder leer = Greenfield).

## Registrierte Stacks

| Stack | Wofür | Repo |
|---|---|---|
| [`backend-go-graphql/`](backend-go-graphql/stack.yaml) | Web-/SaaS-Backends mit Login, Hintergrund-Jobs, KI-Features; **nicht** für Echtzeit/Streaming (siehe EIGNUNG.md im Repo) | `zkbandfriends/ZukunftsApp_Vorlage_Backend_Framework` (privat) |

Weitere Kandidaten entstehen, sobald sich ein Muster zum zweiten Mal wiederholt
(Frontend-Next.js, n8n-Automationspaket, …) — Regel: erst extrahieren, wenn es zweimal
gebraucht wurde, nicht auf Vorrat.
