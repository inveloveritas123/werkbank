"""Tests für den WERKBANK Tier-Router (Policy-Engine für Modellwahl je Subagent)."""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "orchestrator"))

import tier_router as tr  # noqa: E402


class Routing(unittest.TestCase):
    def test_cheap_tasks_to_haiku(self):
        for t in ("doku", "summary", "format", "lint"):
            self.assertEqual(tr.route(t)["model"], "haiku", t)

    def test_build_tasks_to_sonnet(self):
        for t in ("impl", "test", "refactor", "build"):
            self.assertEqual(tr.route(t)["model"], "sonnet", t)

    def test_judgement_tasks_to_opus(self):
        for t in ("review", "security", "privacy", "plan", "architecture", "judge"):
            self.assertEqual(tr.route(t)["model"], "opus", t)

    def test_unknown_falls_back_to_default(self):
        self.assertEqual(tr.route("voellig-unbekannt")["model"], "sonnet")

    def test_case_insensitive(self):
        self.assertEqual(tr.route("REVIEW")["model"], "opus")


class ConfirmGate(unittest.TestCase):
    def test_opus_requires_confirm(self):
        self.assertTrue(tr.route("review")["confirm"])

    def test_cheaper_tiers_no_confirm(self):
        self.assertFalse(tr.route("doku")["confirm"])
        self.assertFalse(tr.route("impl")["confirm"])


class PolicyOverride(unittest.TestCase):
    def test_file_policy_overrides_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "policy.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"routing": {"doku": "opus"}}, f)
            pol = tr.load_policy(p)
            self.assertEqual(tr.route("doku", pol)["model"], "opus")
            # nicht überschriebene Defaults bleiben erhalten
            self.assertEqual(tr.route("review", pol)["model"], "opus")

    def test_committed_policy_loads(self):
        pol = tr.load_policy()  # orchestrator/werkbank.tiers.json
        self.assertEqual(tr.route("doku", pol)["model"], "haiku")
        self.assertEqual(tr.route("security", pol)["model"], "opus")


if __name__ == "__main__":
    unittest.main(verbosity=2)
