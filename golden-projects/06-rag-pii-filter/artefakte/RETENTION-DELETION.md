# RETENTION-DELETION — RAG mit PII-Filter (GP06)

| Datenart | Aufbewahrung | Rechtsgrund | Löschmechanismus |
|---|---|---|---|
| Indexierte Dokumente | solange fachlich erforderlich | berechtigtes Interesse / Vertrag | `delete(doc_id)` entfernt das Dokument aus dem Index |
| Antwort-/Anwendungs-Log (pseudonym) | 30 Tage | Betrieb/Sicherheit | rotierende Löschung |

- **Index-Löschung:** `RagIndex.delete(doc_id)` entfernt ein Dokument vollständig aus dem Index;
  nachfolgende Anfragen können es nicht mehr als Quelle nutzen (verifiziert per Test).
- **Betroffenenrechte:** Wird die Löschung personenbezogener Daten verlangt (Art. 17), werden die
  betreffenden Dokumente aus dem Index entfernt; zusätzlich maskiert der PII-Filter Ausgaben.
- **Backups:** In einer Produktivumgebung folgt der Index-Speicher der Backup-Rotation; gelöschte
  Dokumente fallen mit der nächsten Rotation auch dort weg.
