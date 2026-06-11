"""Gate D2 — SCA via pip-audit/safety (deterministisch). Tests.

pip-audit/safety sind in dieser Umgebung NICHT installiert -> der TOOL_MISSING-Pfad
wird real ausgeloest (bei vorhandenem Manifest). Die Output-Parsing-Pfade (FAIL/PASS)
werden ueber Monkeypatching von `subprocess.run` und `shutil.which` auf dem d2_sca-Modul
deterministisch getestet (kein echter Tool-Lauf noetig).
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, d2_sca  # noqa: E402


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


class NoManifestSkips(unittest.TestCase):
    def test_no_manifest_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "kein Manifest\n")
            res = d2_sca.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertIn("Manifest", res.summary)


class ToolMissingSkips(unittest.TestCase):
    def test_manifest_present_but_tool_missing_is_tool_missing(self):
        orig_which = d2_sca.shutil.which
        d2_sca.shutil.which = lambda name: None
        try:
            with tempfile.TemporaryDirectory() as d:
                _write(d, "requirements.txt", "requests==2.0.0\n")
                res = d2_sca.run(d)
                self.assertEqual(res.status, common.SKIP)
                self.assertEqual(res.skip_reason, common.TOOL_MISSING)
        finally:
            d2_sca.shutil.which = orig_which


class PipAuditParsing(unittest.TestCase):
    def setUp(self):
        self._orig_which = d2_sca.shutil.which
        self._orig_run = d2_sca.subprocess.run
        d2_sca.shutil.which = lambda name: "/usr/bin/pip-audit" if name == "pip-audit" else None

    def tearDown(self):
        d2_sca.shutil.which = self._orig_which
        d2_sca.subprocess.run = self._orig_run

    def _patch_run(self, stdout):
        d2_sca.subprocess.run = lambda cmd, *a, **kw: _FakeProc(stdout)

    def test_vulnerabilities_fail_with_redacted_packages(self):
        payload = {"dependencies": [
            {"name": "requests", "vulns": [{"id": "PYSEC-1", "description": "secret advisory text"}]},
            {"name": "urllib3", "vulns": []},
        ]}
        with tempfile.TemporaryDirectory() as d:
            _write(d, "requirements.txt", "requests==2.0.0\n")
            self._patch_run(json.dumps(payload))
            res = d2_sca.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)
            self.assertIn("1", res.summary)
            # kein Roh-Advisory-Text im Report
            joined = " ".join(line for f in res.findings for line in (f.evidence, f.kind))
            self.assertNotIn("secret advisory text", joined)

    def test_no_vulnerabilities_passes(self):
        payload = {"dependencies": [{"name": "requests", "vulns": []}]}
        with tempfile.TemporaryDirectory() as d:
            _write(d, "pyproject.toml", "[project]\nname='x'\n")
            self._patch_run(json.dumps(payload))
            res = d2_sca.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)

    def test_progress_line_before_json_is_tolerated(self):
        payload = {"dependencies": [{"name": "requests", "vulns": [{"id": "PYSEC-1"}]}]}
        noisy = "Found 12 known vulnerabilities...\n" + json.dumps(payload)
        with tempfile.TemporaryDirectory() as d:
            _write(d, "requirements.txt", "requests==2.0.0\n")
            self._patch_run(noisy)
            res = d2_sca.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)


class SafetyFallback(unittest.TestCase):
    def setUp(self):
        self._orig_which = d2_sca.shutil.which
        self._orig_run = d2_sca.subprocess.run
        # pip-audit fehlt, safety vorhanden -> Fallback-Pfad
        d2_sca.shutil.which = lambda name: "/usr/bin/safety" if name == "safety" else None

    def tearDown(self):
        d2_sca.shutil.which = self._orig_which
        d2_sca.subprocess.run = self._orig_run

    def test_safety_vulnerabilities_fail(self):
        payload = [["requests", "<2.20.0", "2.0.0", "advisory body", "CVE-2018"]]
        with tempfile.TemporaryDirectory() as d:
            _write(d, "requirements.txt", "requests==2.0.0\n")
            d2_sca.subprocess.run = lambda cmd, *a, **kw: _FakeProc(json.dumps(payload))
            res = d2_sca.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 1)
            self.assertIn("safety", res.summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
