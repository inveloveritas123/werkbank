"""kiln — persistente Minds: Reviewer/Architekt behalten Historie, Builder bleiben frisch."""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ORCH = os.path.join(REPO_ROOT, "orchestrator")
sys.path.insert(0, ORCH)

import mind  # noqa: E402

MIND_PY = os.path.join(ORCH, "mind.py")


class Store(unittest.TestCase):
    def test_append_accumulates_and_persists(self):
        with tempfile.TemporaryDirectory() as d:
            mind.append(d, "reviewer", "GP02: fail-closed Auth wichtig")
            mind.append(d, "reviewer", "GP03: E3-Regex-Evasion beachten")
            # frische Instanz/Aufruf -> Historie bleibt
            ctx = mind.context(d, "reviewer")
            self.assertIn("fail-closed", ctx)
            self.assertIn("E3-Regex", ctx)

    def test_context_returns_recent_limited(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(5):
                mind.append(d, "reviewer", "Eintrag-%d" % i)
            ctx = mind.context(d, "reviewer", limit=2)
            self.assertIn("Eintrag-4", ctx)
            self.assertIn("Eintrag-3", ctx)
            self.assertNotIn("Eintrag-0", ctx)

    def test_roles_isolated(self):
        with tempfile.TemporaryDirectory() as d:
            mind.append(d, "reviewer", "R-Notiz")
            mind.append(d, "architect", "A-Notiz")
            self.assertNotIn("A-Notiz", mind.context(d, "reviewer"))
            self.assertNotIn("R-Notiz", mind.context(d, "architect"))

    def test_empty_role_empty_context(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(mind.context(d, "reviewer").strip(), "")


class PersistencePolicy(unittest.TestCase):
    def test_reviewer_architect_persistent(self):
        self.assertTrue(mind.is_persistent("reviewer"))
        self.assertTrue(mind.is_persistent("architect"))

    def test_builder_is_fresh(self):
        self.assertFalse(mind.is_persistent("builder"))
        self.assertFalse(mind.is_persistent("impl"))
        self.assertFalse(mind.is_persistent("dev"))


class Cli(unittest.TestCase):
    def test_append_then_context(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([sys.executable, MIND_PY, "append", "reviewer", "CLI-Notiz", d], check=True)
            out = subprocess.run([sys.executable, MIND_PY, "context", "reviewer", "10", d],
                                 stdout=subprocess.PIPE, text=True).stdout
            self.assertIn("CLI-Notiz", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
