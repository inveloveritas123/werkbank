# PRD: Einwilligungs-Logbuch

> Nach BMAD-PRD-Template (Small-scope all-inclusive). Rolle: PM (John). Status: final.

## 0. Document Purpose
Schlankes PRD für einen Thin-Slice, der Art.-7-Einwilligungen nachweisbar protokolliert.

## 1. Vision
Ein nachweisbares, PII-armes Logbuch, das Einwilligungen erteilt, widerruft und belegt — so einfach
widerrufbar wie erteilt (Art. 7 Abs. 3).

## 2. Target User
Kleine Teams, die Einwilligungen rechtssicher dokumentieren müssen.
### 2.1 Jobs To Be Done
„Wenn jemand einwilligt oder widerruft, will ich das nachweisbar festhalten, ohne unnötige PII zu speichern."
### 2.3 Key User Journey
Betroffener willigt ein → System protokolliert (pseudonym) → später Widerruf → Status sofort inaktiv → Nachweis vorhanden.

## 3. Glossary
- **subject_ref:** pseudonyme Referenz auf die betroffene Person (kein Klartext-Name/-Mail).
- **purpose:** Zweck der Einwilligung (z. B. „newsletter").
- **active:** gültige, nicht widerrufene Einwilligung.

## 4. Features
### 4.1 Einwilligungs-Ledger
#### FR-1: Einwilligung erteilen (`grant(subject_ref, purpose) -> consent_id`)
#### FR-2: Widerruf (`withdraw(consent_id)`) — so einfach wie die Erteilung (Art. 7 Abs. 3)
#### FR-3: Status prüfen (`is_active(subject_ref, purpose)`)
#### FR-4: Auflisten je Betroffenem (`list_active(subject_ref)`)
#### FR-5: Nachweis-Log ohne unnötige PII (nur consent_id/purpose/Event)

## 5. Non-Goals (Explicit)
- Kein Consent-Banner/Frontend, keine UI. Keine Rechtsberatung. Keine Klartext-PII-Speicherung.

## 6. MVP Scope
### 6.1 In Scope
grant · withdraw · is_active · list_active · PII-armes Log · Persistenz.
### 6.2 Out of Scope for MVP
Mehrmandantenfähigkeit, Ablauf-/Erneuerungslogik, Export.

## 7. Success Metrics
Alle Akzeptanzkriterien grün; Gate E2 (keine PII im Log) grün.

## 8. Regulated Domain (GDPR)
Art. 7 (Einwilligung, Nachweisbarkeit, einfacher Widerruf), Art. 5 (Datenminimierung im Log).

## Stories
- **Story-1:** Als Verantwortlicher kann ich eine Einwilligung erteilen und erhalte eine consent_id. Acceptance: `grant` liefert eine ID; `is_active` = true.
- **Story-2:** Als Verantwortlicher kann ich widerrufen. Acceptance: nach `withdraw` ist `is_active` = false; Widerruf eines unbekannten Tokens schlägt sauber fehl.
- **Story-3:** Als Auditor sehe ich ein Protokoll ohne Klartext-PII. Acceptance: Log enthält weder Name noch E-Mail; Gate E2 grün.
