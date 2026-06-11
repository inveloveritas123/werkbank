"""Gate A — Spec-Integrität (A1 Pflichtfelder, A2 Akzeptanz testbar, A3 Handoff). Tests."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import a_spec, common  # noqa: E402

FILLED = """# SPEC — Beispiel

## 1. Ziel / Problem
Kundenportal-Terminbuchung für einen Handwerksbetrieb.

## 2. Scope (in / out)
- In: Terminbuchung, Anfragen
- Out: Zahlungsabwicklung

## 3. Datenarten & DSGVO-Relevanz
Name, E-Mail, Telefon. Keine Art-9-Daten.

## 4. Akzeptanzkriterien (testbar)
- [ ] Kunde kann einen Termin buchen und erhält eine Bestätigung
- [ ] Stornierung entfernt den Termin aus der Liste

## 5. Nicht-Ziele / Annahmen
Keine Mehrsprachigkeit in v1.

## 6. Handoff PM → Architect (Gate A3)
- [x] Kontext, Constraints, offene Entscheidungen dokumentiert
"""


def _w(d, name, content):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class SkipWithoutContext(unittest.TestCase):
    def test_a1_skip_without_spec(self):
        res = a_spec.run_a1(".")
        self.assertEqual(res.status, common.SKIP)
        self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
        self.assertIn("kein SPEC", res.summary)

    def test_all_a_gates_skip_without_spec(self):
        for fn in (a_spec.run_a1, a_spec.run_a2, a_spec.run_a3):
            with self.subTest(gate=fn.__name__):
                res = fn(".")
                self.assertEqual(res.status, common.SKIP)
                self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
                self.assertIn("kein SPEC", res.summary)


class FilledSpecPasses(unittest.TestCase):
    def test_a1_a2_a3_pass(self):
        with tempfile.TemporaryDirectory() as d:
            sp = _w(d, "SPEC.md", FILLED)
            self.assertEqual(a_spec.run_a1(d, spec_file=sp).status, common.PASS)
            self.assertEqual(a_spec.run_a2(d, spec_file=sp).status, common.PASS)
            self.assertEqual(a_spec.run_a3(d, spec_file=sp).status, common.PASS)


class UnfilledSpecFails(unittest.TestCase):
    def test_a1_fails_on_placeholders(self):
        with tempfile.TemporaryDirectory() as d:
            sp = _w(d, "SPEC.md", "# SPEC\n\n## 1. Ziel / Problem\n<was wird gelöst>\n")
            self.assertEqual(a_spec.run_a1(d, spec_file=sp).status, common.FAIL)

    def test_a1_fails_on_missing_section(self):
        with tempfile.TemporaryDirectory() as d:
            sp = _w(d, "SPEC.md", "# SPEC\n\n## 1. Ziel\nText\n## 2. Scope\nText\n")
            self.assertEqual(a_spec.run_a1(d, spec_file=sp).status, common.FAIL)

    def test_a2_fails_without_acceptance_items(self):
        with tempfile.TemporaryDirectory() as d:
            txt = FILLED.replace("- [ ] Kunde kann einen Termin buchen und erhält eine Bestätigung\n", "") \
                        .replace("- [ ] Stornierung entfernt den Termin aus der Liste\n", "")
            sp = _w(d, "SPEC.md", txt)
            self.assertEqual(a_spec.run_a2(d, spec_file=sp).status, common.FAIL)

    def test_a3_fails_without_handoff_check(self):
        with tempfile.TemporaryDirectory() as d:
            txt = FILLED.replace("- [x] Kontext, Constraints, offene Entscheidungen dokumentiert",
                                 "- [ ] Kontext, Constraints, offene Entscheidungen dokumentiert")
            sp = _w(d, "SPEC.md", txt)
            self.assertEqual(a_spec.run_a3(d, spec_file=sp).status, common.FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
