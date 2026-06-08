# ARCHITECTURE — Einwilligungs-Logbuch

> Nach BMAD-Methode (Rolle: Architect, Winston). „Boring technology": Python stdlib, dateibasiert.

## Überblick
Ein In-Process-Service `ConsentLedger` mit dateibasierter Persistenz (JSON) und einem PII-armen
Append-Log. Kein Netzdienst, kein externer Endpunkt (EU-neutral, Gate E1 trivial grün).

## Komponenten
| Komponente | Verantwortung | Schnittstellen |
|---|---|---|
| `ConsentLedger` | grant/withdraw/is_active/list_active | Python-API |
| Persistenz | `consents.json` (atomar via os.replace) | Datei |
| Audit-Log | `app.log` — nur consent_id/purpose/Event | Datei (.log) |

## Datenfluss & PII
Eingang: `subject_ref` (pseudonym) + `purpose`. Gespeichert werden subject_ref/purpose/Status/Zeit.
**Im Log nur** consent_id + purpose + Event — **nie** subject_ref-Klartextname/-Mail (Datenminimierung, Gate E2).

## Entscheidungen
- subject_ref ist eine pseudonyme Referenz; der Aufrufer ist für die Pseudonymisierung verantwortlich (dokumentiert).
- Widerruf = Statuswechsel + Log; Datensatz bleibt als Nachweis erhalten (Art. 7 Nachweisbarkeit).
- Atomare Schreibvorgänge für Integrität.

## Handoff PM → Architect
Übergabe vollständig: Scope, Constraints (stdlib, EU-only, PII-arm), offene Punkte (Out-of-Scope) dokumentiert.
