# DSAR-RIGHTS — Betroffenenrechte (Art. 12–22), GP02

- **Umgesetzte Rechte im Dienst:**
  - Auskunft (Art. 15) & Datenübertragbarkeit (Art. 20): `export(subject_id, access_token)` liefert
    den vollständigen eigenen Datensatz in strukturierter Form (JSON).
  - Löschung (Art. 17): `delete(subject_id, access_token)` entfernt den eigenen Datensatz unverzüglich.
- **Identitäts-/Zugriffsschutz:** Jede Anfrage erhält ein Access-Token; Export und Löschung sind nur
  mit dem zum Datensatz gehörenden Token möglich. Fremde oder ungültige Token werden abgewiesen
  (`AccessDenied`). At-rest wird nur der Token-Hash gehalten.
- **Mandantentrennung:** Die Admin-Sicht ist je `tenant` gefiltert; ein Mandant sieht keine Datensätze
  eines anderen.
- **Prozess:** Eingang der Anfrage → Token-Prüfung (Identität) → Auskunft/Löschung → pseudonyme
  Protokollierung des Vorgangs. Gesetzliche Frist von einem Monat (Art. 12 Abs. 3) wird durch die
  unmittelbare technische Umsetzbarkeit eingehalten.
- **Nicht im Beispiel umgesetzt:** Berichtigung (Art. 16), Einschränkung (Art. 18) und Widerspruch
  (Art. 21) sind organisatorisch über den Datenschutz-Kontakt abzubilden; technisch erweiterbar.
