"""Auto-Labeler (Issue #5): Aufgabentext -> Label -> Modell; Lint für Agent-Defs ohne model:."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "orchestrator"))

import autolabel  # noqa: E402


class Labeling(unittest.TestCase):
    def test_keywords_map_to_labels(self):
        cases = {
            "Prüfe adversarial die Zugriffskontrolle": "review",
            "Fasse die README in 3 Sätzen zusammen": "doku",
            "Schreibe einen Unittest für portal.py": "test",
            "Implementiere die Export-Funktion": "impl",
            "Erzeuge die DSGVO-Artefakte (Datenschutz)": "privacy",
            "Plane die Architektur des Moduls": "plan",
        }
        for text, label in cases.items():
            self.assertEqual(autolabel.autolabel(text), label, text)

    def test_unknown_defaults_to_impl(self):
        self.assertEqual(autolabel.autolabel("mach mal irgendwas"), "impl")

    def test_route_returns_model(self):
        self.assertEqual(autolabel.route("Prüfe adversarial")["model"], "opus")
        self.assertEqual(autolabel.route("Fasse zusammen")["model"], "haiku")
        self.assertEqual(autolabel.route("Implementiere X")["model"], "sonnet")


class AgentLint(unittest.TestCase):
    def test_flags_agent_without_model_frontmatter(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "ok.md"), "w") as f:
                f.write("---\nname: x\nmodel: opus\n---\n# X\n")
            with open(os.path.join(d, "bad.md"), "w") as f:
                f.write("# Y\nkein frontmatter\n")
            missing = autolabel.lint_agent_dir(d)
            self.assertIn("bad.md", missing)
            self.assertNotIn("ok.md", missing)


class Cli(unittest.TestCase):
    def test_cli_prints_label_and_model(self):
        import subprocess
        out = subprocess.run([sys.executable, os.path.join(REPO_ROOT, "orchestrator", "autolabel.py"),
                              "Prüfe adversarial die Logik"], stdout=subprocess.PIPE, text=True).stdout
        self.assertIn("review", out)
        self.assertIn("opus", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
