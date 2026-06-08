"""GP04 — PII-Erkennung & Redaction (stdlib-only).

Erkennt E-Mail, Telefon (intl + deutsche Nationalformate), deutsche IBAN, Kreditkarte (Luhn)
und einfache Namens-Muster (nach Anrede). `redact()` ersetzt Fundstellen durch Platzhalter
([EMAIL]/[PHONE]/[IBAN]/[CARD]/[NAME]) und liefert maskierte Befunde (nie Klartext).
"""
import re
from dataclasses import dataclass

_NAME = r"([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+)"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# Telefon intl: erlaubt optionales (0) zwischen Landes- und Vorwahl ("+49 (0)151 …").
PHONE_INTL_RE = re.compile(r"(?:\+49|0049)[\s\-/]?(?:\(0\))?[\s\-/]?\(?\d{2,5}\)?[\s\-/]?\d{3,}(?:[\s\-/]?\d{2,})?")
PHONE_NAT_RE = re.compile(r"(?<![\d/])0\d{1,4}[\s/\-]\d{3,}(?:[\s/\-]?\d{2,})?\b")
# IBAN beliebiges Land (Kandidat) — Gültigkeit via mod-97 (gegen False Positives).
IBAN_CAND_RE = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]){11,30}\b")
CC_RE = re.compile(r"\b(?:\d[ -]?){13,16}\b")
# Namen: nach Anrede, nach Grußformel ("Mit freundlichen Grüßen, X Y") oder Selbstnennung.
NAME_SAL_RE = re.compile(r"(?:Herr|Frau|Dr\.?|Hr\.?|Fr\.?)\s+" + _NAME)
NAME_GREET_RE = re.compile(
    r"(?:Mit freundlichen|Viele|Beste|Mit besten|Herzliche|Freundliche)\s+"
    r"Gr[üu]e?(?:ß|ss)e[n]?[,\s]+" + _NAME)
NAME_SELF_RE = re.compile(r"(?:Mein Name ist|Ich heiße|Ich heisse|Ansprechpartner(?:in)?:?|Unterschrift:?)\s+" + _NAME)
NAME_PATS = (NAME_SAL_RE, NAME_GREET_RE, NAME_SELF_RE)

PLACEHOLDER = {
    "email": "[EMAIL]", "phone-intl": "[PHONE]", "phone-national": "[PHONE]",
    "iban": "[IBAN]", "credit-card": "[CARD]", "name": "[NAME]",
}


@dataclass
class Finding:
    kind: str
    start: int
    end: int
    masked: str


def _luhn_ok(digits):
    s, alt = 0, False
    for ch in reversed(digits):
        d = ord(ch) - 48
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        s += d
        alt = not alt
    return s % 10 == 0


def _iban_ok(raw):
    s = re.sub(r"\s", "", raw).upper()
    if not (15 <= len(s) <= 34) or not s[:2].isalpha() or not s[2:4].isdigit():
        return False
    rearr = s[4:] + s[:4]
    num = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearr)
    try:
        return int(num) % 97 == 1
    except ValueError:
        return False


def _mask(kind, raw):
    raw = raw.replace("\n", " ").strip()
    if kind == "name":
        return raw.split()[0][0] + "***"          # nur Initiale
    if len(raw) <= 4:
        return "*" * len(raw)
    return raw[:2] + "…" + raw[-2:]


def _collect(text):
    spans = []
    def add(kind, m, group=0):
        spans.append((m.start(group), m.end(group), kind))
    for m in EMAIL_RE.finditer(text):
        add("email", m)
    for m in PHONE_INTL_RE.finditer(text):
        add("phone-intl", m)
    for m in PHONE_NAT_RE.finditer(text):
        add("phone-national", m)
    for m in IBAN_CAND_RE.finditer(text):
        if _iban_ok(m.group(0)):
            add("iban", m)
    for m in CC_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 16 and _luhn_ok(digits):
            add("credit-card", m)
    for pat in NAME_PATS:
        for m in pat.finditer(text):
            add("name", m, 1)
    # nach Position sortieren, Überlappungen verwerfen (erste gewinnt)
    spans.sort()
    out, last_end = [], -1
    for s, e, kind in spans:
        if s >= last_end:
            out.append((s, e, kind))
            last_end = e
    return out


def redact(text):
    spans = _collect(text)
    findings, pieces, cursor = [], [], 0
    for s, e, kind in spans:
        pieces.append(text[cursor:s])
        pieces.append(PLACEHOLDER.get(kind, "[REDACTED]"))
        findings.append(Finding(kind, s, e, _mask(kind, text[s:e])))
        cursor = e
    pieces.append(text[cursor:])
    return "".join(pieces), findings
