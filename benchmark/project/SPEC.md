# SPEC — Multi-Tenant Einwilligungs-Portal (Benchmark)

## 1. Ziel / Problem
Mandantengetrennte Kontakt- und Einwilligungsverwaltung (Art. 7) mit nachvollziehbarem, PII-armem Audit.

## 2. Scope (in / out)
- In: Kontakt anlegen, lesen (mandantengeprüft), Einwilligung erteilen/widerrufen, Auflisten, Audit-Log.
- Out: UI, Mehrsprachigkeit, Export.

## 3. Datenarten & DSGVO-Relevanz
Name, E-Mail, Mandant, Einwilligungszwecke. Besondere Kategorien nach Art. 9: keine.

## 4. Akzeptanzkriterien (testbar)
- [ ] Mandant A kann B's Kontakt nicht lesen; `list_contacts` zeigt nur den eigenen Mandanten
- [ ] Einwilligung erteilen/widerrufen ändert `is_consented` korrekt
- [ ] das Log enthält weder Name noch E-Mail; Persistenz übersteht einen Neustart
- [ ] jeder Zugriff erzeugt einen schema-konformen Audit-Eintrag (kein Cross-Tenant-Erfolg)

## 5. Nicht-Ziele / Annahmen
Kein Frontend; subject/Token-Pseudonymisierung Aufrufer-Verantwortung. Betrieb EU-only.

## 6. Handoff PM → Architect (Gate A3)
- [x] Kontext, Constraints (stdlib, EU-only, PII-arm, mandantengetrennt) und offene Punkte dokumentiert
