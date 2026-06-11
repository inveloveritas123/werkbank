"""Gate G1 — Lasttest via k6 (deterministisch). Tests.

k6 ist in dieser Umgebung typischerweise NICHT installiert. Die PASS/WARN-Pfade werden
über Monkeypatching von `shutil.which` und `subprocess.run` auf dem g1_loadtest-Modul
deterministisch getestet (kein echter k6-Lauf). TOOL_MISSING und NOT_APPLICABLE werden
über reale Tempdirs ausgelöst.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, g1_loadtest  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class NoScriptSkips(unittest.TestCase):
    def test_no_script_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "kein Lasttest\n")
            res = g1_loadtest.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertIn("kein Lasttest konfiguriert", res.summary)


class K6MissingSkips(unittest.TestCase):
    def setUp(self):
        self._orig_which = g1_loadtest.shutil.which

    def tearDown(self):
        g1_loadtest.shutil.which = self._orig_which

    def test_script_present_but_k6_missing_is_tool_missing(self):
        g1_loadtest.shutil.which = lambda name: None
        with tempfile.TemporaryDirectory() as d:
            _write(d, "smoke.k6.js", "export default function () {}\n")
            res = g1_loadtest.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.TOOL_MISSING)
            self.assertIn("k6", res.summary)


class K6RunParsing(unittest.TestCase):
    def setUp(self):
        self._orig_which = g1_loadtest.shutil.which
        self._orig_run = g1_loadtest.subprocess.run
        g1_loadtest.shutil.which = lambda name: "/usr/bin/k6"

    def tearDown(self):
        g1_loadtest.shutil.which = self._orig_which
        g1_loadtest.subprocess.run = self._orig_run

    def test_returncode_zero_passes(self):
        g1_loadtest.subprocess.run = lambda *a, **kw: _FakeProc(0, "ok\n")
        with tempfile.TemporaryDirectory() as d:
            _write(d, "loadtest-main.js", "export default function () {}\n")
            res = g1_loadtest.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)

    def test_nonzero_returncode_warns_with_finding(self):
        g1_loadtest.subprocess.run = lambda *a, **kw: _FakeProc(99, "", "threshold p(95) exceeded\n")
        with tempfile.TemporaryDirectory() as d:
            _write(d, "k6/scenario.js", "export default function () {}\n")
            res = g1_loadtest.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(len(res.findings), 1)
            self.assertEqual(res.findings[0].kind, "loadtest-failure")

    def test_subprocess_error_is_warn_not_fail(self):
        def boom(*a, **kw):
            raise OSError("no exec")
        g1_loadtest.subprocess.run = boom
        with tempfile.TemporaryDirectory() as d:
            _write(d, "smoke.k6.js", "export default function () {}\n")
            res = g1_loadtest.run(d)
            self.assertEqual(res.status, common.WARN)


if __name__ == "__main__":
    unittest.main(verbosity=2)
