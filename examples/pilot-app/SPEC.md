# SPEC — Einwilligungs-Logbuch (Thin-Slice)

> Abgeleitet aus `docs/PRD.md` + `docs/ARCHITECTURE.md` (BMAD). Bestanden durch A-Gates.

## 1. Ziel / Problem
Einwilligungen nach Art. 7 DSGVO nachweisbar protokollieren und so einfach widerrufbar machen wie erteilt.

## 2. Scope (in / out)
- In: Einwilligung erteilen, widerrufen, Status prüfen, je Betroffenem auflisten, PII-armes Log, Persistenz.
- Out: UI/Consent-Banner, Mehrmandantenfähigkeit, Ablauflogik, Export, Rechtsberatung.

## 3. Datenarten & DSGVO-Relevanz
Pseudonyme `subject_ref`, `purpose`, Status, Zeitstempel. Keine Klartext-PII im Log (Art. 5 Datenminimierung).

## 4. Akzeptanzkriterien (testbar)
- [ ] `grant(subject_ref, purpose)` liefert eine consent_id; danach ist `is_active(subject_ref, purpose)` wahr
- [ ] nach `withdraw(consent_id)` ist `is_active` falsch; Widerruf eines unbekannten Tokens schlägt sauber fehl
- [ ] `list_active(subject_ref)` zeigt nur aktive Einwilligungen dieses Betroffenen
- [ ] das Log enthält weder Name noch E-Mail (Gate E2 grün); Persistenz übersteht einen Neustart

## 5. Nicht-Ziele / Annahmen
Kein Frontend; subject_ref ist bereits pseudonymisiert (Verantwortung des Aufrufers). Betrieb EU-only.

## 6. Handoff PM → Architect (Gate A3)
- [x] Kontext, Constraints (stdlib, EU-only, PII-arm) und offene Entscheidungen (Out-of-Scope) dokumentiert
