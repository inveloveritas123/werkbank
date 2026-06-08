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

## Status
T0: BMAD installiert (core + bmm v6.8.0, 44 Skills, 6 Rollen: Analyst/PM/Architect/UX/Dev/Tech-Writer).
Thin-Slice (Durchstich 01→04) folgt ab T2.
