# GP03 — Mini-CRM mit Mandantentrennung
**Ziel:** Multi-Tenant-Basissystem (für Infra-Layer/intern zentral).
**Feature:** Mandant A sieht nur A · Mandant B sieht nur B · Admin-Rolle getrennt · API blockt Cross-Tenant.
**Soll-Ist (alle grün):**
- A liest A · A liest B NICHT · B liest B · B liest A NICHT
- API-Test gegen manipulierte tenant_id schlägt fehl · Audit-Log ohne unnötige PII
**Soll-Outputs:** App + Tests (inkl. Cross-Tenant-Negativtest) + TOMs.md (Mandantentrennung) + GATE-REPORT.md
**Akzeptanz:** Score >= 85, E3 grün, Regression GP01–02 grün.
