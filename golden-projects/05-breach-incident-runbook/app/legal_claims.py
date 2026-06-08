"""GP05 — Linter gegen Fake-Rechtsaussagen (deterministisch).

Flaggt absolute juristische Scheinsicherheiten ("garantiert rechtssicher",
"definitiv nicht meldepflichtig", "100% DSGVO-konform", Haftungsausschlüsse) und das Fehlen
des "Kein Rechtsrat"-Disclaimers. Ein Breach-Runbook darf Einschätzungen geben, aber keine
verbindlichen Rechtsgarantien vortäuschen.
"""
import re

FORBIDDEN = [
    ("absolute-konformitaet", re.compile(r"(?i)\b(100\s?%|zu hundert prozent)\b.{0,20}(dsgvo|rechts|konform)")),
    ("rechtssicher",          re.compile(r"(?i)\brechts(sicher|verbindlich)\b")),
    ("garantie",              re.compile(r"(?i)\bgarantiert\b.{0,40}(konform|sicher|keine|nicht|recht)")),
    ("definitive-meldeaussage", re.compile(r"(?i)\bdefinitiv\b.{0,25}(nicht|keine)\b.{0,25}(meld|erforderlich)")),
    ("absolut-keine-meldung", re.compile(r"(?i)\b(keinesfalls|in keinem fall|auf keinen fall)\b.{0,25}meld")),
    ("haftungsausschluss",    re.compile(r"(?i)\bwir haften nicht\b")),
    ("scheinsicherheit",      re.compile(r"(?i)\b(zweifelsfrei|unzweifelhaft|mit sicherheit)\b.{0,25}(konform|meld|recht)")),
]
DISCLAIMER_RE = re.compile(r"(?i)kein\s+rechtsrat")

# Kahle, unbedingte Meldeaussagen — gefährlich NUR ohne Hedge auf derselben Zeile.
BALD_RE = re.compile(r"(?i)\b(nicht meldepflichtig|keine meldepflicht|besteht keine meldepflicht|"
                     r"nicht erforderlich|nicht notwendig|auf der sicheren seite|kann unterbleiben)\b")
HEDGE_RE = re.compile(r"(?i)(voraussichtlich|einsch[aä]tzung|nach aktueller|sofern|"
                      r"dsb|zu pr[üu]fen|dokumentier|best[aä]tigen|entscheidung|abh[aä]ngig)")


def lint(text, name="?"):
    findings = []
    for ln, line in enumerate(text.splitlines(), 1):
        for kind, pat in FORBIDDEN:
            m = pat.search(line)
            if m:
                findings.append({"file": name, "line": ln, "kind": kind, "snippet": m.group(0)[:60]})
        bm = BALD_RE.search(line)
        if bm and not HEDGE_RE.search(line):
            findings.append({"file": name, "line": ln, "kind": "kahle-meldeaussage",
                             "snippet": line.strip()[:60]})
    return findings


def lint_texts(docs):
    """docs: {name: text}. Liefert Liste von Befunden inkl. fehlendem Disclaimer."""
    findings = []
    for name, text in docs.items():
        findings.extend(lint(text, name))
    combined = "\n".join(docs.values())
    if not DISCLAIMER_RE.search(combined):
        findings.append({"file": "*", "line": 0, "kind": "missing-disclaimer",
                         "snippet": "kein 'Kein Rechtsrat'-Hinweis"})
    return findings


if __name__ == "__main__":
    import sys
    import os
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    docs = {}
    for fn in os.listdir(d):
        if fn.endswith(".md"):
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                docs[fn] = f.read()
    res = lint_texts(docs)
    for f in res:
        print("%(file)s:%(line)d [%(kind)s] %(snippet)s" % f)
    sys.exit(1 if res else 0)
