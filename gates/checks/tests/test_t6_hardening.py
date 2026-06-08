"""T6-Härtung (Paar-Review GP04): Redactor + E2 dürfen reale PII nicht durchlassen.

Adversariales Korpus: Telefon mit (0), Namen ohne Anrede (Grußformel/„Mein Name ist"),
Auslands-IBAN. Zwei Eigenschaften je Fall:
 (a) der Redactor maskiert die PII (Prompt-Dump pattern-clean per unabhängigem E2-Scan),
 (b) E2 fängt die ROHE PII (unabhängiger, breiterer Scanner — Defense-in-Depth).
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
APP_DIR = os.path.join(REPO_ROOT, "golden-projects", "04-upload-pii-redaction", "app")
sys.path.insert(0, GATES_DIR)
sys.path.insert(0, APP_DIR)

from checks import common, e2_pii_scan  # noqa: E402
import pii_redactor as red  # noqa: E402

# (Label, Text, rohe-PII-Teilstrings die verschwinden müssen)
CORPUS = [
    ("phone-0",        "Tel: +49 (0)151 2345678 erreichbar", ["+49 (0)151 2345678", "(0)151 2345678"]),
    ("phone-0049",     "Rueckruf 0049 (0)151 2345678 bitte",  ["0049 (0)151 2345678"]),
    ("name-greeting",  "Mit freundlichen Gruessen, Anna Schmidt", ["Anna Schmidt"]),
    ("name-selbst",    "Mein Name ist Max Mustermann und ich frage an", ["Max Mustermann"]),
    ("iban-at",        "Erstattung auf AT61 1904 3002 3457 3201 bitte", ["AT61 1904 3002 3457 3201"]),
]


def _e2_on_text(text, name):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "logs")
        os.makedirs(p)
        with open(os.path.join(p, name + ".log"), "w", encoding="utf-8") as f:
            f.write(text + "\n")
        return e2_pii_scan.run(d).status


class RedactorCatchesCorpus(unittest.TestCase):
    def test_redactor_masks_all(self):
        for label, text, raws in CORPUS:
            redacted, findings = red.redact(text)
            self.assertTrue(findings, "%s: nichts erkannt" % label)
            for raw in raws:
                self.assertNotIn(raw, redacted, "%s: '%s' nicht maskiert" % (label, raw))

    def test_prompt_dump_pattern_clean(self):
        # Der redigierte Text (Prompt-Dump) muss vom unabhängigen E2-Scanner als sauber gelten.
        for label, text, _ in CORPUS:
            redacted, _ = red.redact(text)
            self.assertEqual(_e2_on_text(redacted, label), common.PASS, "%s: Residual-PII" % label)


class E2CatchesCorpusRaw(unittest.TestCase):
    def test_e2_flags_raw_pii(self):
        for label, text, _ in CORPUS:
            self.assertEqual(_e2_on_text(text, label), common.FAIL, "%s: E2 blind" % label)


if __name__ == "__main__":
    unittest.main(verbosity=2)
