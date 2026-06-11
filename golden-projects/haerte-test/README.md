# Härte-Test — beweist, dass die Gates wirklich ROT werden

Antwort auf den stärksten Einwand gegen jedes Gate-System: *„GRÜN heißt vielleicht nur,
dass nichts scharf geprüft wurde."* Dieser Härte-Test pflanzt fünf reale Verstöße und zeigt,
dass jeder vom zuständigen Gate gefangen wird — und der Gesamtlauf ROT liefert.

## Die fünf gepflanzten Verstöße → welches Gate sie fängt

| # | Verstoß | Gate | Ergebnis |
|---|---|---|---|
| 1 | Non-EU-LLM-Endpunkt (`api.openai.com`) | **E1** EU-Routing | FAIL |
| 2 | SQL-Injection (`"… WHERE id='" + uid + "'"`) | **D1** SAST (bandit B608) | FAIL |
| 3 | Hardcoded Secret (`AKIA…`) | **D3** Secret-Scan | FAIL |
| 4 | Klartext-PII im Log (E-Mail + Telefon) | **E2** PII-Scan | FAIL |
| 5 | Fehlende DSGVO-Artefakte (TOMs, Löschfrist) | **E5** Artefakte | FAIL |

→ Gesamt: **ROT**. Unter dem alten „kein block-FAIL ⇒ grün" wäre ein Teil davon durchgerutscht;
unter dem Pflichtenheft-Verdikt ist jeder dieser Pflicht-Verstöße hart rot.

## Warum hier kein Code liegt (sondern ein Test)

**Verification-first, wie im ganzen Repo:** Die Verstöße werden zur **Laufzeit** in einem
Tempdir synthetisiert (gesplittete Literale) und **nie committet**. Würden Secret/PII/SQLi
hier eingecheckt, fänden die repo-eigenen Gates (D3/E2/D1) sie beim `werkbank_self`-Lauf —
das Repo wäre dauerhaft rot und hätte Klartext-Secrets in der Historie.

Der ausführbare Beweis liegt daher in:
**`gates/checks/tests/test_haerte.py`** — er pflanzt die Verstöße, prüft jeden Gate-Fund
einzeln und lässt einen vollen Runner-Lauf gegen `pii_stdlib` laufen (Erwartung: ROT).

```bash
python3 -m unittest discover -s gates/checks/tests -p "test_haerte.py"
```
