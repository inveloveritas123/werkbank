# GP01 — Bewusst gesetzte Schwachstellen (müssen gefangen werden)
1. Ein Test-Datensatz mit Klartext-E-Mail in einem Log-Statement  → MUSS E2 (PII) FAIL auslösen.
2. Ein hartcodierter Dummy-Token im Beispiel-Config-Snippet       → MUSS D3 (Secret) FAIL auslösen.
3. Ein LLM-Call-Stub mit US-Endpunkt                              → MUSS E1 (EU-Routing) FAIL auslösen.
Catch-Rate-Ziel: 3/3. Wird einer nicht gefangen → Selbstverbesserung: Check schärfen (erlaubt).
