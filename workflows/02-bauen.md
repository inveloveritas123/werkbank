# Workflow 02 — Bauen (Ralph-Loop)

> Verification-first. Story → RED → GREEN → REFACTOR → Chunk-Review.
> `completion-promise = <promise>GRUEN</promise>`, `--max-iterations 15` als Sicherheitsnetz.

## Ablauf
1. Tests zuerst (RED). Implementierung bis grün (GREEN). Aufräumen (REFACTOR).
2. Pro Chunk Paar-Review: **Reviewer-Modell ≠ Implementer-Modell** (Cross-Model, Gate I1).
3. Frischer Worker pro Chunk (Kontext-Isolation); persistente Reviewer/Architekt-Minds.
4. **Drift-Pausegate:** sinkt Test/Gate ggü. Vorrunde → anhalten, Ursache nennen, eskalieren.
5. `.werkbank/STATE.md` nach jeder Runde aktualisieren.

## Abbruch / Stopp
- max-iterations erreicht ohne GRUEN ⇒ anhalten, Lage melden.
- Block-Gate rot ⇒ kein Fortschritt, zurück in den Loop oder STOPP.

## Übergabe an
`workflows/03-pruefen.md`

## Status
Stub (T0). Loop-Mechanik wird ab T2 verdrahtet.
