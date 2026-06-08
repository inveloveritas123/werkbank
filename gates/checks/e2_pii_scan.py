"""Gate E2 — PII-Scan in Logs/Prompts/Outputs (deterministisch, kein LLM).

Scope (bewusst eng = Intent des Gates): Log-/Prompt-/Output-Artefakte. Konfig/Doku
mit legitimen Kontakt-Mails (z. B. DSB) werden nicht geflaggt.
Hochpraezise Muster: E-Mail, +49-Telefon, deutsche IBAN, Kreditkarte (mit Luhn).
"""
import re
import sys

try:
    from . import common
except ImportError:
    import common  # type: ignore

GATE = "E2"

NAME_SUFFIXES = (".log", ".out", ".prompt")
PATH_CONTAINS = ("logs/", "log/", "prompts/", "prompt/", "outputs/", "output/")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+49[\s\-/]?\d{2,4}[\s\-/]?\d{3,}[\s\-/]?\d{2,}")
IBAN_RE = re.compile(r"\bDE\d{2}(?:\s?\d{4}){4}\s?\d{2}\b")
CC_RE = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def _luhn_ok(digits: str) -> bool:
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


def _scan_line(line):
    out = []
    for m in EMAIL_RE.finditer(line):
        out.append(("email", m.group(0)))
    for m in PHONE_RE.finditer(line):
        out.append(("phone-de", m.group(0)))
    for m in IBAN_RE.finditer(line):
        out.append(("iban-de", m.group(0)))
    for m in CC_RE.finditer(line):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 16 and _luhn_ok(digits):
            out.append(("credit-card", m.group(0)))
    return out


def run(target, exclude_dirs=None, exclude_abs=None):
    findings = []
    for ap, rel in common.iter_files(target, name_suffixes=NAME_SUFFIXES,
                                     path_contains=PATH_CONTAINS,
                                     exclude_dirs=exclude_dirs,
                                     exclude_abs=exclude_abs):
        lines = common.read_lines(ap)
        if lines is None:
            continue
        for i, line in enumerate(lines, 1):
            for kind, raw in _scan_line(line):
                findings.append(common.Finding(rel, i, "pii:" + kind, common.redact(raw)))
    if findings:
        return common.CheckResult(GATE, common.FAIL,
                                  "%d Klartext-PII in Logs/Prompts/Outputs" % len(findings), findings)
    return common.CheckResult(GATE, common.PASS, "keine Klartext-PII in Logs/Prompts/Outputs")


if __name__ == "__main__":
    res = run(sys.argv[1] if len(sys.argv) > 1 else ".")
    print("\n".join(res.to_report_lines()))
    sys.exit(0 if res.status == common.PASS else 1)
