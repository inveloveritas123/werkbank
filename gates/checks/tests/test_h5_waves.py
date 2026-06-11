"""Tests fuer Gate H5 — Wellen sind self-contained (Dateien/Verbote/Smoke/Akzeptanz inline)."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from checks import common, h5_waves  # noqa: E402

_COMPLETE = """# TASKS

## Wellen

### Welle 1 — Mandantentrennung haerten
- Dateien:   app/crm.py, app/auth.py
- Verbote:   gates/* nicht anfassen; kein Schema-Change
- Smoke:     python3 -m pytest tests/test_tenant.py -q
- Akzeptanz: Cross-Tenant-Read wirft AccessDenied, fail-closed
"""


def _tasks(d, text):
    with open(os.path.join(d, "TASKS.md"), "w", encoding="utf-8") as f:
        f.write(text)
    return d


class H5Waves(unittest.TestCase):
    def test_no_tasks_file_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            res = h5_waves.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)

    def test_no_wave_blocks_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            _tasks(d, "# TASKS\n\n| # | Task | Test | Status |\n|---|---|---|---|\n| 1 | x | unit | [ ] |\n")
            res = h5_waves.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)

    def test_complete_open_wave_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _tasks(d, _COMPLETE)
            res = h5_waves.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertIn("1 offene", res.summary)

    def test_missing_smoke_fails_and_names_field(self):
        text = _COMPLETE.replace("- Smoke:     python3 -m pytest tests/test_tenant.py -q\n", "")
        with tempfile.TemporaryDirectory() as d:
            _tasks(d, text)
            res = h5_waves.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)
            self.assertIn("Smoke", res.findings[0].evidence)

    def test_placeholder_field_counts_as_missing(self):
        text = _COMPLETE.replace("Cross-Tenant-Read wirft AccessDenied, fail-closed",
                                 "<noch zu ergaenzen>")
        with tempfile.TemporaryDirectory() as d:
            _tasks(d, text)
            res = h5_waves.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertIn("Akzeptanz", res.findings[0].evidence)

    def test_done_wave_with_missing_fields_is_ignored(self):
        text = "# TASKS\n\n## Wellen\n\n### Welle 1 — fertig [x]\n- Dateien: app.py\n"
        with tempfile.TemporaryDirectory() as d:
            _tasks(d, text)
            res = h5_waves.run(d)
            # erledigte Welle (kein Pflichtfeld) darf nicht failen; keine offenen -> PASS
            self.assertEqual(res.status, common.PASS)

    def test_multiple_open_waves_one_incomplete(self):
        text = _COMPLETE + (
            "\n### Welle 2 — Export\n"
            "- Dateien:   app/export.py\n"
            "- Verbote:   keine\n"
            "- Akzeptanz: CSV mit BOM\n"   # Smoke fehlt
        )
        with tempfile.TemporaryDirectory() as d:
            _tasks(d, text)
            res = h5_waves.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertTrue(any("Welle 2" in f.evidence and "Smoke" in f.evidence
                                for f in res.findings))
            # Welle 1 ist vollstaendig -> taucht NICHT in den Funden auf
            self.assertFalse(any("Mandantentrennung" in f.evidence for f in res.findings))


if __name__ == "__main__":
    unittest.main(verbosity=2)
