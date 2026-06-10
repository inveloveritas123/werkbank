"""Gate D1 — SAST via bandit (deterministisch). Tests.

bandit ist in dieser Umgebung NICHT installiert -> der TOOL_MISSING-Pfad wird real
ausgeloest. Die Output-Parsing-Pfade (FAIL/PASS) werden ueber Monkeypatching von
`subprocess.run` und `shutil.which` auf dem d1_sast-Modul deterministisch getestet
(kein echter bandit-Lauf noetig).
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, d1_sast  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class _FakeProc:
    def __init__(self, stdout):
        self.stdout = stdout
        self.returncode = 0


def _bandit_json(results):
    return json.dumps({"results": results})


def _result(filename, severity, test_id="B602", line=7, test_name="subprocess_popen_with_shell_equals_true"):
    return {
        "filename": filename,
        "issue_severity": severity,
        "test_id": test_id,
        "line_number": line,
        "test_name": test_name,
    }


class NoPythonSkips(unittest.TestCase):
    def test_no_python_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "kein Python hier\n")
            res = d1_sast.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertIn("kein Python", res.summary)


class BanditMissingSkips(unittest.TestCase):
    def test_python_present_but_bandit_missing_is_tool_missing(self):
        # bandit-Abwesenheit deterministisch erzwingen (unabhaengig davon, ob in der
        # Umgebung bandit installiert ist) -> TOOL_MISSING-Pfad.
        orig_which = d1_sast.shutil.which
        d1_sast.shutil.which = lambda name: None
        try:
            with tempfile.TemporaryDirectory() as d:
                _write(d, "app.py", "x = 1\n")
                res = d1_sast.run(d)
                self.assertEqual(res.status, common.SKIP)
                self.assertEqual(res.skip_reason, common.TOOL_MISSING)
                self.assertIn("bandit", res.summary)
        finally:
            d1_sast.shutil.which = orig_which


class BanditOutputParsing(unittest.TestCase):
    def setUp(self):
        # bandit als vorhanden vortaeuschen + subprocess.run kapern.
        self._orig_which = d1_sast.shutil.which
        self._orig_run = d1_sast.subprocess.run
        d1_sast.shutil.which = lambda name: "/usr/bin/bandit"

    def tearDown(self):
        d1_sast.shutil.which = self._orig_which
        d1_sast.subprocess.run = self._orig_run

    def _patch_run(self, results):
        def fake_run(cmd, *a, **kw):
            return _FakeProc(_bandit_json(results))
        d1_sast.subprocess.run = fake_run

    def test_high_severity_fails_with_one_sast_finding(self):
        with tempfile.TemporaryDirectory() as d:
            ap = _write(d, "vuln.py", "import os\nos.system('x')\n")
            self._patch_run([_result(ap, "HIGH")])
            res = d1_sast.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)
            self.assertIn("sast", res.findings[0].kind)
            self.assertIn("high", res.findings[0].kind)

    def test_progress_line_before_json_is_tolerated(self):
        # Regression: bandit schreibt eine 'Working... 100%'-Fortschrittszeile vor das
        # JSON auf stdout. Der Parser muss ab dem ersten '{' lesen, sonst faelschlich FAIL.
        with tempfile.TemporaryDirectory() as d:
            ap = _write(d, "vuln.py", "import os\nos.system('x')\n")
            noisy = "Working... ━━━ 100% 0:00:00\n" + _bandit_json([_result(ap, "HIGH")])
            d1_sast.subprocess.run = lambda cmd, *a, **kw: _FakeProc(noisy)
            res = d1_sast.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)

    def test_only_low_severity_passes(self):
        with tempfile.TemporaryDirectory() as d:
            ap = _write(d, "mild.py", "assert True\n")
            self._patch_run([_result(ap, "LOW")])
            res = d1_sast.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)
            self.assertIn("Low", res.summary)

    def test_empty_results_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "clean.py", "x = 1\n")
            self._patch_run([])
            res = d1_sast.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
