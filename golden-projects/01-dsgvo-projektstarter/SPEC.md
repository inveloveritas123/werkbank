# GP01 — DSGVO-Projektstarter

**Ziel:** Aus strukturierten Projektangaben erzeugt WERKBANK die DSGVO-Grundartefakte —
sauber, vollständig, ohne Platzhalter.

## Input (Beispiel-Eingabe, die der Lauf verarbeitet)
```
Projektname, Zweck, Datenarten, Betroffenengruppen, Systeme,
Hosting-Region, Subdienstleister, Speicherdauer, Zugriffsrollen
```

## Akzeptanzkriterien (testbar)
- Alle Soll-Artefakte aus EXPECTED_OUTPUTS.md werden erzeugt.
- Alle Pflichtfelder gefüllt; **keine** `TODO`/`TBD`/`[...]`-Platzhalter.
- Hosting-Region = EU; Subdienstleister gelistet.
- DPIA-Screening ergibt einen nachvollziehbaren Score (Begründung vorhanden).
- E-Gates (E1/E2/E5) grün; GATE-REPORT.md geschrieben.
- Score >= 85 (siehe ../../SCORING-MATRIX.md).
