"""Tests fuer K1/K2 — Branchenregeln (branchenspezifische Pflicht-Artefakte + Fachabnahme).

Nutzt das mitgelieferte Beispiel-Regelpaket branch-modules/finanzen/rules.yaml.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from checks import branch, common  # noqa: E402

FINANZ_ARTEFACTS = ("AUDIT-TRAIL.md", "AUFBEWAHRUNG.md", "MARISK-MAPPING.md")


def _write(d, rel, content="inhalt\n"):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


def _branch_marker(d, name):
    os.makedirs(os.path.join(d, ".werkbank"), exist_ok=True)
    with open(os.path.join(d, ".werkbank", "branch.txt"), "w", encoding="utf-8") as f:
        f.write(name + "\n")


def _signoff(d, section, granted=True):
    p = os.path.join(d, "docs", "produktivfreigabe")
    os.makedirs(p, exist_ok=True)
    val = "true" if granted else "false"
    with open(os.path.join(p, "FREIGABE.yaml"), "w", encoding="utf-8") as f:
        f.write("%s:\n  freigegeben: %s\n  von: \"Compliance\"\n  datum: \"2026-06-11\"\n" % (section, val))


class BranchK1(unittest.TestCase):
    def test_no_branch_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            res = branch.run_k1(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)

    def test_unknown_branch_fails(self):
        with tempfile.TemporaryDirectory() as d:
            res = branch.run_k1(d, branch="gibtsnicht")
            self.assertEqual(res.status, common.FAIL)
            self.assertIn("Regelpaket", res.summary)

    def test_missing_artefacts_fail(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AUDIT-TRAIL.md")   # nur eines von dreien
            res = branch.run_k1(d, branch="finanzen")
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual(len(res.findings), 2)   # zwei fehlen

    def test_all_artefacts_present_pass(self):
        with tempfile.TemporaryDirectory() as d:
            for a in FINANZ_ARTEFACTS:
                _write(d, a)
            res = branch.run_k1(d, branch="finanzen")
            self.assertEqual(res.status, common.PASS)

    def test_branch_from_marker_file(self):
        with tempfile.TemporaryDirectory() as d:
            _branch_marker(d, "finanzen")
            for a in FINANZ_ARTEFACTS:
                _write(d, a)
            res = branch.run_k1(d)   # ohne branch-Param -> aus .werkbank/branch.txt
            self.assertEqual(res.status, common.PASS)


class BranchK2(unittest.TestCase):
    def test_no_branch_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(branch.run_k2(d).status, common.SKIP)

    def test_signoff_granted_pass(self):
        with tempfile.TemporaryDirectory() as d:
            _signoff(d, "fachaufsicht", granted=True)
            res = branch.run_k2(d, branch="finanzen")
            self.assertEqual(res.status, common.PASS)

    def test_signoff_not_granted_fail(self):
        with tempfile.TemporaryDirectory() as d:
            _signoff(d, "fachaufsicht", granted=False)
            res = branch.run_k2(d, branch="finanzen")
            self.assertEqual(res.status, common.FAIL)

    def test_signoff_missing_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            res = branch.run_k2(d, branch="finanzen")   # keine FREIGABE.yaml
            self.assertEqual(res.status, common.SKIP)


if __name__ == "__main__":
    unittest.main(verbosity=2)
