"""Gate F2 — Eval-on-Bump (Evidenz-basiert, deterministisch). Tests.

Reine Tempdir-Faelle (kein Monkeypatching noetig):
- Modell gepinnt + keine Eval -> FAIL
- Modell gepinnt + evals/-Dir -> PASS
- kein Modell                 -> SKIP/NOT_APPLICABLE
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, f2_eval_on_bump  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class ModelPinnedNoEvalFails(unittest.TestCase):
    def test_model_pinned_without_eval_is_fail(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "config.yaml", "model: claude-opus-4-20250514\n")
            res = f2_eval_on_bump.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertIn("Eval-on-Bump", res.summary)


class ModelPinnedWithEvalsDirPasses(unittest.TestCase):
    def test_model_pinned_with_evals_dir_is_pass(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "config.json", '{"model": "gpt-4o"}\n')
            _write(d, "evals/case_01.json", '{"prompt": "x", "expected": "y"}\n')
            res = f2_eval_on_bump.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertIn("Baseline", res.summary)

    def test_model_pinned_with_werkbank_baseline_is_pass(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "settings.toml", 'model_id = "claude-sonnet-4"\n')
            _write(d, ".werkbank/eval-baseline.json", '{"score": 0.9}\n')
            res = f2_eval_on_bump.run(d)
            self.assertEqual(res.status, common.PASS)


class NoModelSkips(unittest.TestCase):
    def test_no_model_reference_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "config.yaml", "service: web\nport: 8080\n")
            res = f2_eval_on_bump.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertIn("kein Modell", res.summary)


class EmptyEvalsDirStillFails(unittest.TestCase):
    def test_model_pinned_with_empty_evals_dir_is_fail(self):
        # leeres evals/ ist KEINE Evidenz -> FAIL
        with tempfile.TemporaryDirectory() as d:
            _write(d, "config.yaml", "model: claude-opus-4\n")
            os.makedirs(os.path.join(d, "evals"))
            res = f2_eval_on_bump.run(d)
            self.assertEqual(res.status, common.FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
