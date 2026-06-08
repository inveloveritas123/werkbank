"""GP06 — kompakter PII-Filter für RAG-Antworten (stdlib-only).

Ersetzt E-Mail/Telefon/IBAN/Name durch Platzhalter, damit Antworten keine unnötige PII ausgeben.
Gleiche Heuristik wie das gehärtete E2-Gate (Defense-in-Depth, eigenständig für dieses Projekt).
"""
import re

_NAME = r"([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+)"
_SAL_RE = re.compile(r"(?:Herr|Frau|Dr\.?|Hr\.?|Fr\.?)\s+" + _NAME)
# Namen ohne Anrede: zwei+ aufeinanderfolgende großgeschriebene Wörter. Im Deutschen sind Nomen
# großgeschrieben -> wir schließen häufige satzeinleitende/funktionale Wörter aus (STOPCAPS).
# Privacy-by-default: lieber ein Nomen zu viel maskieren als einen echten Namen ausgeben.
_BIGRAM_RE = re.compile(r"\b([A-ZÄÖÜ][a-zäöüß]+)((?:\s+[A-ZÄÖÜ][a-zäöüß]+)+)\b")
_STOPCAPS = {
    "Die", "Der", "Das", "Den", "Dem", "Ein", "Eine", "Einen", "Einem", "Einer",
    "Im", "In", "Am", "An", "Auf", "Aus", "Bei", "Beim", "Mit", "Von", "Vom",
    "Zum", "Zur", "Und", "Oder", "Wir", "Sie", "Er", "Es", "Ich", "Ihr",
    "Fuer", "Für", "Nach", "Vor", "Ueber", "Über", "Sehr", "Herr", "Frau",
    "Dr", "Hr", "Fr", "Diese", "Dieser", "Dieses", "Kein", "Keine",
}
_CONTACT_PATS = [
    ("[EMAIL]", re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    ("[PHONE]", re.compile(r"(?:\+49|0049)[\s\-/]?(?:\(0\))?[\s\-/]?\(?\d{2,5}\)?[\s\-/]?\d{3,}(?:[\s\-/]?\d{2,})?")),
    ("[PHONE]", re.compile(r"(?<![\d/])0\d{1,4}[\s/\-]\d{3,}(?:[\s/\-]?\d{2,})?\b")),
]
_IBAN_CAND = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]){11,30}\b")


def _bigram_repl(m):
    return m.group(0) if m.group(1) in _STOPCAPS else "[NAME]"


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


def redact(text):
    # 1. Name nach Anrede: nur den Namensteil ersetzen, Anrede behalten.
    text = _SAL_RE.sub(lambda m: m.group(0)[:m.start(1) - m.start(0)] + "[NAME]", text)
    # 2. Namen ohne Anrede (großgeschriebene Wortpaare, STOPCAPS ausgenommen).
    text = _BIGRAM_RE.sub(_bigram_repl, text)
    # 3. Kontakt-PII.
    for placeholder, pat in _CONTACT_PATS:
        text = pat.sub(placeholder, text)
    text = _IBAN_CAND.sub(lambda m: "[IBAN]" if _iban_ok(m.group(0)) else m.group(0), text)
    return text
