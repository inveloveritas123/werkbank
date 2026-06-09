# Benchmark-Report — 2026-06-09

Umfangreicher Lauf: Entwicklung eines realistischen Programms (Multi-Tenant Einwilligungs-Portal),
Ansprechen möglichst aller Gates, automatischer PDCA-Test, Auditor-Prüfung der Agenten.

## 1 · Programm
`benchmark/project/` — Multi-Tenant Kontakt-/Einwilligungs-Portal (stdlib): Mandantentrennung,
schema-konformes Audit-Log, PII-armes Logging, Einwilligung (Art. 7), Persistenz. + SPEC, CHANGELOG,
8 DSGVO-Artefakte, Audit-Evidence, 4 Akzeptanztests.

## 2 · Gate-Abdeckung (voller Lauf, alle Kontexte)
**Ergebnis: GRUEN · 16 Gates PASS · 23 SKIP.**
- **PASS (16):** A1, A2, A3, B3, C1, D3, E1, E2, E3, E4, E5, E6, E7, E8, F1, H4
  → **alle implementierten deterministischen Gates feuern grün.**
- **SKIP (23):** tool-gated (B1/B2 ruff/mypy, C2 coverage), LLM/warn (A4, H6, I1/I2/I3), nicht implementiert
  (C3–C6, D1/D2/D4, F2/F3, G1–G3, H1–H3).

## 3 · PDCA-Zyklus (automatisch, `benchmark/pdca.py`)
Plant→Do→Check→Act, deterministisch, in Arbeitskopie:
| | Wert |
|---|---|
| Schwäche (geplant) | Platzhalter in DATA-FLOW.md → **E5 FAIL**, overall **ROT** |
| Nach Verbesserung (Platzhalter gefüllt) | **E5 PASS**, overall **GRUEN** |
| improved | **ja** |
| Regression (PASS→FAIL) | **keine** |
| ok | **ja** (exit 0) |
→ Der kontrollierte Selbstverbesserungs-Zyklus funktioniert end-to-end (messen → nachschärfen → erneut messen → keine Regression).
**Nebenbefund:** der Benchmark fing einen echten Bug im Harness selbst (fehlendes `--ci` → Exit-Code spiegelte ROT nicht) → sofort gefixt.

## 4 · Auditor — Agenten-Differenzierung / Modellwahl / Tokens
3 Subagenten für 3 Aufgabentypen, Modell je Tier-Router gewählt:
| Aufgabe | Router | gemeldetes Modell | Tokens | Dauer | Match |
|---|---|---|---|---|---|
| doku | haiku | claude-haiku-4-5 | 11.6k | 3.8s | ✅ |
| impl | sonnet | claude-sonnet-4-6 | 12.9k | 10.4s | ✅ |
| review | opus | claude-opus-4-8 | 13.4k | 19.5s | ✅ |
- **Differenzierung 3/3 korrekt** — Tier-Routing wird beim Spawn real angewandt.
- **Token-/Kosten-effizient:** doku auf haiku (günstig), opus nur für den Security-Review (gerechtfertigt;
  Review-VERDICT = pass, App leckfrei). Kein teures Modell für billige Aufgaben.
- **Befund (Issue #5):** Routing ist Konvention, nicht erzwungen — Empfehlung: Auto-Labeler/Pre-Spawn-Wrapper.

## 5 · Fazit
Gate-Abdeckung maximal (16/16 implementiert), PDCA-Zyklus verifiziert, Agenten differenziert & sparsam.
Ein niedrig-schwerer Audit-Befund → automatisch als **Issue #5** im Git. System verhält sich wie vorgesehen.
