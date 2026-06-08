"""GP05 — Breach-/Incident-Runbook-Generator (stdlib-only).

Aus einem strukturierten Vorfall erzeugt generate() vier Dokumente:
BREACH-RUNBOOK · INCIDENT-TIMELINE · NOTIFICATION-CHECKLIST · LESSONS-LEARNED.
Die Meldeentscheidung ist eine begründete EINSCHÄTZUNG mit bedingter Sprache — keine
verbindliche Rechtsaussage (Art. 33/34). Kein Rechtsrat; finale Entscheidung durch DSB/Verantwortlichen.
"""
from datetime import datetime, timedelta

DISCLAIMER = ("> Kein Rechtsrat — fachliche Prüfung und finale Meldeentscheidung durch "
             "DSB/Verantwortlichen bzw. Anwalt. Dies ist eine strukturierte Einschätzung, "
             "keine verbindliche Rechtsauskunft.")


def _parse(ts):
    return datetime.fromisoformat(ts)


def assess(incident):
    detected = _parse(incident["detected_at"])
    deadline = detected + timedelta(hours=72)
    high_risk = bool(incident.get("special_categories")) or \
        any(w in incident["type"].lower() for w in ("unbefugt", "zugriff", "diebstahl", "leak", "ransom"))
    return {
        "detected": detected,
        "deadline": deadline,
        "high_risk": high_risk,
        # Art. 33: Meldung, außer das Risiko ist voraussichtlich unwahrscheinlich.
        "notify_authority": True,
        # Art. 34: Benachrichtigung Betroffener nur bei voraussichtlich hohem Risiko.
        "notify_subjects": high_risk,
    }


def _runbook(incident, a):
    dts = ", ".join(incident["data_types"])
    risk = "voraussichtlich hoch" if a["high_risk"] else "voraussichtlich nicht hoch"
    return "\n".join([
        "# BREACH-RUNBOOK — %s" % incident["type"],
        "",
        DISCLAIMER,
        "",
        "**Betroffene Systeme:** %s" % ", ".join(incident["systems"]),
        "**Betroffene Datenarten:** %s" % dts,
        "**Erkennung:** %s (%s)" % (incident["detection"], incident["detected_at"]),
        "**Möglicher Umfang:** %s" % incident["scope"],
        "",
        "## Ablauf (Maßnahmen)",
        "1. **Erkennung & Eindämmung** — betroffene Systeme isolieren, Zugänge sperren, Logs sichern (Freeze).",
        "2. **Bewertung** des Risikos für die Rechte und Freiheiten der betroffenen Personen "
        "(Einschätzung: Risiko %s)." % risk,
        "3. **Meldung** an die Aufsichtsbehörde nach Art. 33 prüfen (Frist siehe NOTIFICATION-CHECKLIST).",
        "4. Bei hohem Risiko **Benachrichtigung** der Betroffenen nach Art. 34 vorbereiten.",
        "5. **Dokumentation** des Vorfalls und aller Schritte (auch wenn keine Meldung erfolgt, Art. 33 Abs. 5).",
        "",
        "## Sofortmaßnahmen-Liste",
        "- Zugangsdaten rotieren, kompromittierte Sessions invalidieren",
        "- Forensische Sicherung der relevanten Logs",
        "- Kommunikationswege zu DSB und Geschäftsführung aktivieren",
    ]) + "\n"


def _timeline(incident, a):
    rows = []
    if incident.get("occurred_at"):
        rows.append("| %s | mutmaßlicher Eintritt | %s |" % (incident["occurred_at"], incident["type"]))
    rows.append("| %s | Erkennung | %s |" % (incident["detected_at"], incident["detection"]))
    rows.append("| %s | Meldefrist Art. 33 (72 h ab Erkennung) | Aufsichtsbehörde |"
                % a["deadline"].isoformat())
    return "\n".join([
        "# INCIDENT-TIMELINE — %s" % incident["type"],
        "",
        DISCLAIMER,
        "",
        "| Zeitpunkt | Ereignis | Detail |",
        "|---|---|---|",
    ] + rows) + "\n"


def _checklist(incident, a):
    auth = ("Ja — voraussichtlich meldepflichtig, da ein Risiko für die Rechte und Freiheiten "
            "nicht als unwahrscheinlich eingeschätzt wird (Art. 33 Abs. 1). Finale Entscheidung DSB.")
    subj = ("Ja — vorbereiten, da das Risiko als voraussichtlich hoch eingeschätzt wird (Art. 34)."
            if a["high_risk"] else
            "Nach aktueller Einschätzung voraussichtlich nicht erforderlich (Risiko nicht hoch, "
            "Art. 34); Entscheidung dokumentieren und durch DSB bestätigen lassen.")
    return "\n".join([
        "# NOTIFICATION-CHECKLIST — %s" % incident["type"],
        "",
        DISCLAIMER,
        "",
        "## 72-Stunden-Prüfung (Art. 33 Abs. 1)",
        "- Erkennung: %s" % incident["detected_at"],
        "- **Meldefrist (Erkennung + 72 h): %s**" % a["deadline"].isoformat(),
        "- Verzug ist gegenüber der Aufsichtsbehörde zu begründen (Art. 33 Abs. 1 Satz 2).",
        "",
        "## Meldung an die Aufsichtsbehörde (Art. 33)",
        "- Einschätzung: %s" % auth,
        "- Inhalt: Art und Umfang, Kategorien/Zahl Betroffener, wahrscheinliche Folgen, ergriffene Maßnahmen.",
        "",
        "## Benachrichtigung der Betroffenen (Art. 34)",
        "- Einschätzung: %s" % subj,
        "",
        "## Betroffene Datenarten",
        "- %s" % ", ".join(incident["data_types"]),
    ]) + "\n"


def _lessons(incident, a):
    return "\n".join([
        "# LESSONS-LEARNED — %s" % incident["type"],
        "",
        DISCLAIMER,
        "",
        "## Ursache (vorläufige Einschätzung)",
        "- Auf Basis von: %s. Forensische Bestätigung ausstehend." % incident["detection"],
        "## Verbesserungen (Vorschlag)",
        "- Zugangskontrollen und Monitoring-Schwellen überprüfen",
        "- Reaktionszeiten und Meldewege üben (Tabletop-Übung)",
        "- Datenminimierung prüfen, um künftigen Umfang zu reduzieren",
        "## Nachhaltung",
        "- Maßnahmen mit Verantwortlichen und Fristen versehen und nachverfolgen.",
    ]) + "\n"


def generate(incident):
    a = assess(incident)
    return {
        "BREACH-RUNBOOK.md": _runbook(incident, a),
        "INCIDENT-TIMELINE.md": _timeline(incident, a),
        "NOTIFICATION-CHECKLIST.md": _checklist(incident, a),
        "LESSONS-LEARNED.md": _lessons(incident, a),
    }
