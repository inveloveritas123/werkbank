"""Gate C4 — E2E via Playwright (deterministisch). Tests.

Kein Node/Playwright nötig: SKIP-NOT_APPLICABLE bei fehlender Config, SKIP-TOOL_MISSING bei
vorhandener Config ohne npx, und PASS/FAIL über Monkeypatching von `c4_e2e.shutil.which`
und `c4_e2e.subprocess.run` (present-tool + Returncode simuliert).
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import c4_e2e, common  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p) or d, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class NoConfigSkips(unittest.TestCase):
    def test_no_playwright_config_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "nix\n")
            res = c4_e2e.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertIn("E2E", res.summary)


class ConfigButNoTool(unittest.TestCase):
    def test_config_present_but_npx_missing_is_tool_missing(self):
        orig = c4_e2e.shutil.which
        c4_e2e.shutil.which = lambda name: None
        try:
            with tempfile.TemporaryDirectory() as d:
                _write(d, "playwright.config.ts", "export default {};\n")
                res = c4_e2e.run(d)
                self.assertEqual(res.status, common.SKIP)
                self.assertEqual(res.skip_reason, common.TOOL_MISSING)
        finally:
            c4_e2e.shutil.which = orig


class ToolPresentRuns(unittest.TestCase):
    def setUp(self):
        self._orig_which = c4_e2e.shutil.which
        self._orig_run = c4_e2e.subprocess.run
        c4_e2e.shutil.which = lambda name: "/usr/bin/npx"

    def tearDown(self):
        c4_e2e.shutil.which = self._orig_which
        c4_e2e.subprocess.run = self._orig_run

    def test_returncode_zero_passes(self):
        c4_e2e.subprocess.run = lambda *a, **kw: _FakeProc(0, stdout="3 passed\n")
        with tempfile.TemporaryDirectory() as d:
            _write(d, "playwright.config.js", "module.exports = {};\n")
            res = c4_e2e.run(d)
            self.assertEqual(res.status, common.PASS)

    def test_returncode_nonzero_fails_with_redacted_tail(self):
        c4_e2e.subprocess.run = lambda *a, **kw: _FakeProc(1, stdout="1 failed\nError: boom\n")
        with tempfile.TemporaryDirectory() as d:
            _write(d, "playwright.config.mjs", "export default {};\n")
            res = c4_e2e.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)

    def test_subprocess_error_fails_gracefully(self):
        def boom(*a, **kw):
            raise OSError("spawn failed")
        c4_e2e.subprocess.run = boom
        with tempfile.TemporaryDirectory() as d:
            _write(d, "playwright.config.ts", "export default {};\n")
            res = c4_e2e.run(d)
            self.assertEqual(res.status, common.FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
