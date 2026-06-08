"""T3 — kontrollierte Selbstverbesserung (PDCA): E2-Telefonerkennung.

Hebel: E2 fing nur '+49'-Format. Deutsche Nationalformate (0151…, 0351-…) und 0049
fehlten — hohes False-Negative-Risiko für ein DE-DSGVO-Tool. Vorher 2/5 → Ziel 5/5.
False-Positive-Schutz: typische Log-Zahlen (status=200, id=req-001) dürfen NICHT als
Telefon gelten (sonst E2-Regression auf clean-Fixtures).
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import e2_pii_scan as e2  # noqa: E402

PHONE_FORMATS = [
    "+49 151 23456789",
    "+4915123456789",
    "0151 23456789",
    "0351-1234567",
    "0049 151 23456789",
]

# Diese duerfen NIE als Telefon gelten (False-Positive-Schutz).
NON_PHONE = [
    "id=req-001 status=200 tokens_in=128 tokens_out=64",
    "blocks_red=0 tenant=t-42 region=eu-central-1",
    "version=2 count=12 port=8080",
    "order 0 of 0 retries=3",
]


def _is_phone(line):
    return any(k.startswith("phone") for k, _ in e2._scan_line(line))


class PhoneCoverage(unittest.TestCase):
    def test_all_german_formats_caught(self):
        missed = [s for s in PHONE_FORMATS if not _is_phone("kontakt %s" % s)]
        self.assertEqual(missed, [], "nicht gefangen: %r" % missed)

    def test_no_false_positive_on_log_numbers(self):
        fp = [s for s in NON_PHONE if _is_phone(s)]
        self.assertEqual(fp, [], "False Positive: %r" % fp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
