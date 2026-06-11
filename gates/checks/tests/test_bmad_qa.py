"""Tests fuer die LLM-Urteils-Gates als BMAD-QA-Evidence-Leser (A4/H6/I1/I2/I3)."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from checks import bmad_qa, common  # noqa: E402


def _evidence(d, gates, model="claude-reviewer", implementer=None):
    payload = {"source": "bmad-qa", "model": model, "gates": gates}
    if implementer:
        payload["implementer_model"] = implementer
    wd = os.path.join(d, ".werkbank")
    os.makedirs(wd, exist_ok=True)
    with open(os.path.join(wd, "qa-evidence.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return d


class BmadQaEvidence(unittest.TestCase):
    def test_no_evidence_file_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            res = bmad_qa.run_i2(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)

    def test_pass_verdict_is_pass(self):
        with tempfile.TemporaryDirectory() as d:
            _evidence(d, {"H6": {"verdict": "pass", "summary": "kein Drift"}})
            res = bmad_qa.run_h6(d)
            self.assertEqual(res.status, common.PASS)
            self.assertIn("BMAD-QA", res.summary)

    def test_fail_verdict_is_fail(self):
        with tempfile.TemporaryDirectory() as d:
            _evidence(d, {"I3": {"verdict": "fail", "summary": "Flow X bricht"}})
            res = bmad_qa.run_i3(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertIn("Flow X", res.summary)

    def test_missing_gate_entry_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            _evidence(d, {"A4": {"verdict": "pass"}})   # I1 fehlt
            res = bmad_qa.run_i1(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)

    def test_unknown_verdict_is_skip_not_silent_pass(self):
        with tempfile.TemporaryDirectory() as d:
            _evidence(d, {"A4": {"verdict": "vielleicht"}})
            res = bmad_qa.run_a4(d)
            self.assertEqual(res.status, common.SKIP)

    def test_malformed_json_is_skip(self):
        with tempfile.TemporaryDirectory() as d:
            wd = os.path.join(d, ".werkbank")
            os.makedirs(wd)
            with open(os.path.join(wd, "qa-evidence.json"), "w", encoding="utf-8") as f:
                f.write("{ kaputt :: nicht json")
            res = bmad_qa.run_h6(d)
            self.assertEqual(res.status, common.SKIP)

    def test_cross_model_enforced_for_vier_augen(self):
        # I1 PASS, aber Reviewer == Implementer -> FAIL (kein Vier-Augen)
        with tempfile.TemporaryDirectory() as d:
            _evidence(d, {"I1": {"verdict": "pass", "reviewer_model": "claude-x"}},
                      model="claude-x", implementer="claude-x")
            res = bmad_qa.run_i1(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertIn("Vier-Augen", res.summary)

    def test_cross_model_pass_when_models_differ(self):
        with tempfile.TemporaryDirectory() as d:
            _evidence(d, {"I2": {"verdict": "pass", "reviewer_model": "claude-a"}},
                      model="claude-a", implementer="claude-b")
            res = bmad_qa.run_i2(d)
            self.assertEqual(res.status, common.PASS)

    def test_h6_not_subject_to_cross_model(self):
        # H6 ist kein Vier-Augen-Gate: gleiche Modelle duerfen PASS bleiben
        with tempfile.TemporaryDirectory() as d:
            _evidence(d, {"H6": {"verdict": "pass"}}, model="claude-x", implementer="claude-x")
            res = bmad_qa.run_h6(d)
            self.assertEqual(res.status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
