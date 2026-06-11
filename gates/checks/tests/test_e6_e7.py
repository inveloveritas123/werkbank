"""Gate E6 (DSFA-Erzwingung, Art. 35) + E7 (Drittland, Kap. V). Tests."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, e6_dpia, e7_third_country  # noqa: E402


def _w(d, name, content):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(content)


class E6Dpia(unittest.TestCase):
    def test_skip_without_context(self):
        res = e6_dpia.run(".")
        self.assertEqual(res.status, common.SKIP)
        self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
        self.assertIn("kein Privacy-Kontext", res.summary)

    def test_low_risk_passes_without_dpia(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "DPIA-SCREENING.md", "| Indikator | Zutreffend |\n| Profiling | nein |\n\n**Ergebnis:** keine DSFA erforderlich.\n")
            self.assertEqual(e6_dpia.run(d, privacy_dir=d).status, common.PASS)

    def test_high_risk_without_dpia_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "DPIA-SCREENING.md", "| Indikator | Zutreffend |\n| Profiling | ja |\n\n**Ergebnis:** DSFA erforderlich.\n")
            self.assertEqual(e6_dpia.run(d, privacy_dir=d).status, common.FAIL)

    def test_high_risk_with_filled_dpia_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "DPIA-SCREENING.md", "| Profiling | ja |\n")
            _w(d, "DPIA.md", "# DSFA\nSystematische Beschreibung der Verarbeitung. Risiken bewertet. Abhilfemaßnahmen definiert.\n")
            self.assertEqual(e6_dpia.run(d, privacy_dir=d).status, common.PASS)

    def test_high_risk_checkbox_form(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "DPIA-SCREENING.md", "- [x] Neue Technologie / KI mit unklaren Risiken\n")
            self.assertEqual(e6_dpia.run(d, privacy_dir=d).status, common.FAIL)


class E7ThirdCountry(unittest.TestCase):
    def test_skip_without_file(self):
        with tempfile.TemporaryDirectory() as d:
            res = e7_third_country.run(d, privacy_dir=d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertIn("kein Drittland-Artefakt", res.summary)

    def test_eu_only_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "THIRD-COUNTRY-TRANSFERS.md", "Findet eine Übermittlung außerhalb der EU/EWR statt? nein\n")
            self.assertEqual(e7_third_country.run(d, privacy_dir=d).status, common.PASS)

    def test_transfer_with_safeguard_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "THIRD-COUNTRY-TRANSFERS.md",
               "Übermittlung außerhalb der EU/EWR statt? ja\nGarantie: SCC (Standardvertragsklauseln) abgeschlossen.\n")
            self.assertEqual(e7_third_country.run(d, privacy_dir=d).status, common.PASS)

    def test_transfer_without_safeguard_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, "THIRD-COUNTRY-TRANSFERS.md", "Übermittlung außerhalb der EU/EWR statt? ja\nKeine weiteren Angaben.\n")
            self.assertEqual(e7_third_country.run(d, privacy_dir=d).status, common.FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
