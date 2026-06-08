# WERKBANK — SELF-IMPROVEMENT (kontrollierte Selbstverbesserung)

> Der Agent liest diese Regeln **aus dem Repo** vor jeder ACT-Phase. Selbstverbesserung heißt:
> *„WERKBANK verbessert sich gegen Golden Projects, Gates, Benchmarks und Regressionstests"* —
> **nicht** „KI optimiert sich frei". Spec-Anker statt Metrik (Anti-Goodhart).

## Grundregel
Eine Änderung ist nur zulässig, wenn sie das System **messbar näher an Spec + grüne Gates**
bringt **und keine Regression** über frühere Golden Projects erzeugt. Sonst: zurückrollen.

## Erlaubt (autonom, ohne Rückfrage)
- fehlenden Check / Testfall ergänzen
- Regex/Heuristik eines PII-Scans verbessern
- Gate-Report strukturieren/lesbarer machen
- Doku/CHANGELOG nachziehen
- zu teures Modell durch günstigeres ersetzen, wenn Qualität gleich bleibt (Tier-Optimierung)
- Runner robuster machen (Fehlerbehandlung, Resume)
- Flaky-Test stabilisieren (ohne die Assertion aufzuweichen)

## Verboten ohne menschliche Freigabe (STOPP & fragen)
- Architektur ändern
- Berechtigungs-/Capability-Modell ändern
- ein Security-Gate entschärfen oder abschalten
- ein DSGVO-Gate (E*) entfernen oder aufweichen
- Budget/Kill-Switch erhöhen
- Produktivdaten verwenden
- Kanzler-Rechte erweitern
- eine Akzeptanz-/Assertion absenken, damit ein Test „grün" wird

## Ablauf jeder ACT-Runde (gegen Git)
1. Lies `.werkbank/BENCHMARK.md` (Historie) + den aktuellen `GATE-REPORT.md` aus dem Repo.
2. Identifiziere die **eine** kleinste Schwäche mit dem größten Hebel (erlaubte Liste).
3. Wende sie an. Re-run: betroffenes Golden Project **+ alle bisher grünen** (Regression).
4. Vergleiche Score vorher/nachher.
   - besser **und** keine Regression **und** Block-Gates grün → behalten, BENCHMARK-Eintrag, weiter.
   - schlechter / Regression / Gate rot → `git revert`/zurückrollen, Lernpunkt notieren.
5. Höre auf, wenn keine erlaubte Verbesserung mehr messbaren Effekt bringt (kein endloses Wühlen).

## Persistenz (damit Lernen über Läufe hält)
- Jede angewandte/zurückgerollte Verbesserung als Zeile in `.werkbank/BENCHMARK.md` (Datum, Hebel, Effekt).
- Wiederkehrende Muster als kurze Regel in dieses Dokument vorschlagen (per PR, nicht selbst mergen).

## Anti-Goodhart-Merksatz
> Konvergiere gegen die Spec, nicht gegen die Zahl. Eine steigende Punktzahl bei sinkender
> realer Qualität ist ein Fehler, kein Erfolg — und ein Grund zum Zurückrollen.
