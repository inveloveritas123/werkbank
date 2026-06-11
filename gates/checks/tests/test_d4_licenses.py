"""Gate D4 — Lizenz-Compliance via pip-licenses. Tests (hermetisch, kein echtes Tool).

pip-licenses ist hier nicht zwingend installiert. Der TOOL_MISSING-Pfad wird per
Monkeypatch von `shutil.which` erzwungen; die Parsing-Pfade (PASS/WARN) per
Monkeypatch von `subprocess.run` mit einem Fake-Proc (json-stdout + returncode).
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from checks import common, d4_licenses  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class _FakeProc:
    def __init__(self, stdout, returncode=0):
        self.stdout = stdout
        self.returncode = returncode


def _entry(name, lic):
    return {"Name": name, "Version": "1.0", "License": lic}


class ToolMissingSkips(unittest.TestCase):
    def test_pip_licenses_missing_is_tool_missing(self):
        orig = d4_licenses.shutil.which
        d4_licenses.shutil.which = lambda name: None
        try:
            with tempfile.TemporaryDirectory() as d:
                _write(d, "requirements.txt", "requests\n")
                res = d4_licenses.run(d)
                self.assertEqual(res.status, common.SKIP)
                self.assertEqual(res.skip_reason, common.TOOL_MISSING)
                self.assertIn("pip-licenses", res.summary)
        finally:
            d4_licenses.shutil.which = orig


class OutputParsing(unittest.TestCase):
    def setUp(self):
        self._orig_which = d4_licenses.shutil.which
        self._orig_run = d4_licenses.subprocess.run
        d4_licenses.shutil.which = lambda name: "/usr/bin/pip-licenses"

    def tearDown(self):
        d4_licenses.shutil.which = self._orig_which
        d4_licenses.subprocess.run = self._orig_run

    def _patch_run(self, entries, returncode=0):
        stdout = json.dumps(entries)

        def fake_run(cmd, *a, **kw):
            return _FakeProc(stdout, returncode)
        d4_licenses.subprocess.run = fake_run

    def test_copyleft_license_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._patch_run([
                _entry("requests", "Apache 2.0"),
                _entry("readline", "GPLv3"),
            ])
            res = d4_licenses.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(len(res.findings), 1)
            self.assertEqual(res.findings[0].kind, "license-copyleft")
            self.assertIn("readline", res.findings[0].evidence)

    def test_unknown_license_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._patch_run([
                _entry("foo", "UNKNOWN"),
                _entry("bar", ""),
            ])
            res = d4_licenses.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(len(res.findings), 2)

    def test_all_permissive_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._patch_run([
                _entry("requests", "Apache 2.0"),
                _entry("click", "BSD License"),
                _entry("rich", "MIT License"),
            ])
            res = d4_licenses.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)
            self.assertIn("3 Pakete", res.summary)

    def test_nonzero_returncode_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self._patch_run([], returncode=2)
            res = d4_licenses.run(d)
            self.assertEqual(res.status, common.FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
