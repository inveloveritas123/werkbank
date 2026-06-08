# BREACH-RUNBOOK — Unbefugter Zugriff auf die Kundendatenbank

> Kein Rechtsrat — fachliche Prüfung und finale Meldeentscheidung durch DSB/Verantwortlichen bzw. Anwalt. Dies ist eine strukturierte Einschätzung, keine verbindliche Rechtsauskunft.

**Betroffene Systeme:** Kundendatenbank, Web-App
**Betroffene Datenarten:** Name, E-Mail, Telefon, Auftragsdaten
**Erkennung:** Auffaellige Login-Muster im Monitoring (2026-06-08T08:00:00+00:00)
**Möglicher Umfang:** ca. 1.200 Kundendatensaetze potenziell betroffen

## Ablauf (Maßnahmen)
1. **Erkennung & Eindämmung** — betroffene Systeme isolieren, Zugänge sperren, Logs sichern (Freeze).
2. **Bewertung** des Risikos für die Rechte und Freiheiten der betroffenen Personen (Einschätzung: Risiko voraussichtlich hoch).
3. **Meldung** an die Aufsichtsbehörde nach Art. 33 prüfen (Frist siehe NOTIFICATION-CHECKLIST).
4. Bei hohem Risiko **Benachrichtigung** der Betroffenen nach Art. 34 vorbereiten.
5. **Dokumentation** des Vorfalls und aller Schritte (auch wenn keine Meldung erfolgt, Art. 33 Abs. 5).

## Sofortmaßnahmen-Liste
- Zugangsdaten rotieren, kompromittierte Sessions invalidieren
- Forensische Sicherung der relevanten Logs
- Kommunikationswege zu DSB und Geschäftsführung aktivieren
