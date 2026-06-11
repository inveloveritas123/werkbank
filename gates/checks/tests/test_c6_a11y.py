"""Gate C6 — a11y via axe (deterministisch). Tests.

Kein Node/axe nötig: SKIP-NOT_APPLICABLE ohne Setup, SKIP-TOOL_MISSING bei vorhandenem
Setup ohne npx, und PASS/FAIL über Monkeypatching von `c6_a11y.shutil.which` und
`c6_a11y.subprocess.run`.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import c6_a11y, common  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p) or d, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


def _pkg(d, scripts=None, deps=None, devdeps=None):
    obj = {"name": "x", "version": "1.0.0"}
    if scripts is not None:
        obj["scripts"] = scripts
    if deps is not None:
        obj["dependencies"] = deps
    if devdeps is not None:
        obj["devDependencies"] = devdeps
    _write(d, "package.json", json.dumps(obj))


class _FakeProc:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class NoSetupSkips(unittest.TestCase):
    def test_empty_project_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "nix\n")
            res = c6_a11y.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)

    def test_package_json_without_a11y_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            _pkg(d, scripts={"build": "tsc"}, deps={"react": "^18"})
            res = c6_a11y.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


class SetupButNoTool(unittest.TestCase):
    def test_axe_core_dep_but_npx_missing_is_tool_missing(self):
        orig = c6_a11y.shutil.which
        c6_a11y.shutil.which = lambda name: None
        try:
            with tempfile.TemporaryDirectory() as d:
                _pkg(d, devdeps={"axe-core": "^4.0"})
                res = c6_a11y.run(d)
                self.assertEqual(res.status, common.SKIP)
                self.assertEqual(res.skip_reason, common.TOOL_MISSING)
        finally:
            c6_a11y.shutil.which = orig


class ToolPresentRuns(unittest.TestCase):
    def setUp(self):
        self._orig_which = c6_a11y.shutil.which
        self._orig_run = c6_a11y.subprocess.run
        c6_a11y.shutil.which = lambda name: "/usr/bin/npx"

    def tearDown(self):
        c6_a11y.shutil.which = self._orig_which
        c6_a11y.subprocess.run = self._orig_run

    def test_a11y_script_passes(self):
        c6_a11y.subprocess.run = lambda *a, **kw: _FakeProc(0, stdout="0 violations\n")
        with tempfile.TemporaryDirectory() as d:
            _pkg(d, scripts={"a11y": "axe http://localhost"})
            res = c6_a11y.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertIn("script:a11y", res.summary)

    def test_axe_core_dep_fails_on_nonzero(self):
        c6_a11y.subprocess.run = lambda *a, **kw: _FakeProc(2, stdout="3 violations found\n")
        with tempfile.TemporaryDirectory() as d:
            _pkg(d, deps={"axe-core": "^4.0"})
            res = c6_a11y.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)

    def test_config_file_passes(self):
        c6_a11y.subprocess.run = lambda *a, **kw: _FakeProc(0)
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".axerc.json", "{}\n")
            res = c6_a11y.run(d)
            self.assertEqual(res.status, common.PASS)

    def test_subprocess_error_fails_gracefully(self):
        def boom(*a, **kw):
            raise OSError("spawn failed")
        c6_a11y.subprocess.run = boom
        with tempfile.TemporaryDirectory() as d:
            _pkg(d, scripts={"axe": "axe ."})
            res = c6_a11y.run(d)
            self.assertEqual(res.status, common.FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
