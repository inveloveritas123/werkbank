# Doktrin: Self-Contained Wellen

> Übernommen aus BMAD (dort: „jede Story ist vollständig self-contained, ohne Verweis-Kette").
> Gilt für `TASKS.md`. Gate **H5** erzwingt sie deterministisch.

## Problem

Der WERKBANK-Bau-Loop (`02 Bauen`, `ralph/ralph-loop.sh`) ruft den Worker mit **frischem
Kontext pro Runde** auf (`claude -p "Arbeite die oberste offene Welle …"`). Trägt eine Welle
nur Verweise — „siehe ARCHITECTURE §3", „wie in Welle 1 entschieden" —, muss der Worker den
Kontext jede Runde neu zusammensuchen. Das ist:

- **teuer** — Tokens für explorative Re-Reads statt für die Arbeit,
- **fehleranfällig** — ein übersehener Constraint → Drift → rotes Drift-Gate → verschwendete Iteration,
- **fragil bei Resume/Kompaktierung** — nach Kontext-Kompaktierung sind die Verweise weg.

## Regel

**Jede OFFENE Welle in `TASKS.md` trägt inline alles, was der Worker braucht — ohne nachzulesen:**

| Feld | Inhalt |
|---|---|
| **Dateien** | exakte Pfade, die angefasst werden dürfen — nur diese |
| **Verbote** | was NICHT angefasst werden darf (z. B. `gates/*`, Schema, Public-API) |
| **Smoke** | der EXAKTE Verifikationsbefehl (`python3 -m pytest tests/test_x.py -q`) |
| **Akzeptanz** | das Orakel — wann ist die Welle fertig, beobachtbar formuliert |
| Entscheide (optional) | die 1-3 bindenden Entscheidungen aus früheren Wellen, inline |

Format: `### Welle N — Titel` als Block; erledigte Welle mit `[x]` im Heading. Siehe
`templates/TASKS.md`.

## Nutzen

1. **Resume-/Kompaktierungs-Härte** — Worker führt blind aus, kein Nachlesen.
2. **Weniger Drift-Halts** — übersehbare Constraints stehen direkt da → billigere Nacht-Läufe.
3. **Tokensparsam** — ein kuratierter Ausschnitt schlägt explorative Reads über das ganze Repo.
4. **Weniger Halluzination** — Inline-Fakten statt Verweise, die zum Raten einladen.
5. **Echte Übergabe** — eine self-contained Welle ist zugleich eine Spec für einen Menschen.

## Haken & Mitigation

**Duplikation** — Inline-Inhalt kann von der Single-Source-of-Truth (`ARCHITECTURE.md`) abdriften.
Mitigation: nur den *relevanten Ausschnitt* inlinen, und die Welle in **Phase 01 (Konzipieren)**
generieren statt ewig von Hand pflegen.

## Durchsetzung

Gate **H5** (`gates/checks/h5_waves.py`, `warn`/deterministisch) prüft: jede offene Welle hat
`Dateien`/`Verbote`/`Smoke`/`Akzeptanz` inline und ohne Platzhalter (`<…>`, `TODO`, `TBD`). Wer
es hart will, nimmt **H5 ins Profil** (`gates/pflichtenheft.yaml`) auf — dann ist eine unvollständige
Welle ROT, nicht nur eine Warnung.
