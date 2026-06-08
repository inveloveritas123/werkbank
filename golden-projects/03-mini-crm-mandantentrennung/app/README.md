# GP03 — Mini-CRM mit Mandantentrennung (lauffähige App)

stdlib-only (Python 3), keine externen Abhängigkeiten.

## Module
- `crm_service.py` — `Principal`, `CrmService` mit `create_customer`, `get_customer`,
  `list_customers`. Mandant kommt aus dem Principal; Cross-Tenant/forged tenant_id → `AccessDenied`.
  Schreibt ein schema-konformes, PII-freies Audit-Log (`templates/AUDIT-LOG.schema.json`).
- `demo.py` — End-to-End-Durchlauf inkl. Cross-Tenant- und Manipulations-Negativfall.

## Ausführen
```bash
python3 demo.py                 # Audit-Log im Temp-Verzeichnis
python3 demo.py ../evidence/audit.log   # reproduzierbares Audit-Log als Gate-Evidence
```

## Mandantentrennung (DSGVO-relevant)
- `tenant` ausschließlich aus dem authentifizierten Principal, nie aus Client-Parametern.
- Jeder Zugriff mandantengeprüft; Cross-Tenant- und manipulierte-`tenant_id`-Zugriffe → `AccessDenied`.
- Audit-Log nur mit IDs/Mandant/Event (keine PII) → Gate **E2** grün; **E3** prüft Tenant-Lecks,
  **E4** prüft Schema-Konformität.

## Tests
`python3 -m unittest discover -s gates/checks/tests -p "test_gp03.py"`
