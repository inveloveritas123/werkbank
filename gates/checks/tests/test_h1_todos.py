"""Gate H1 — TODO/FIXME ohne Ticket-Referenz. Tests (hermetisch, kein externes Tool).

Deckt PASS (alle Marker getrackt / keine), WARN (Marker ohne Ticket) und
SKIP/NOT_APPLICABLE (kein Code-File) ab.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from checks import common, h1_todos  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class NoCodeSkips(unittest.TestCase):
    def test_no_code_file_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "# TODO without code file\n")
            res = h1_todos.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


class UntrackedWarns(unittest.TestCase):
    def test_todo_without_ticket_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "app.py", "x = 1\n# TODO: refactor this later\n")
            res = h1_todos.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(len(res.findings), 1)
            self.assertEqual(res.findings[0].kind, "todo-no-ticket")
            self.assertEqual(res.findings[0].line, 2)

    def test_multiple_markers_across_extensions(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.js", "// FIXME broken\n")
            _write(d, "b.go", "// XXX hack here\n")
            res = h1_todos.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertEqual(len(res.findings), 2)


class TrackedPasses(unittest.TestCase):
    def test_marker_with_hash_ticket_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "app.py", "# TODO(#123): tracked\n")
            res = h1_todos.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)

    def test_marker_with_jira_and_url_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a.ts", "// FIXME JIRA-42 see https://example.com/x\n")
            _write(d, "b.java", "// TODO GH-7\n")
            res = h1_todos.run(d)
            self.assertEqual(res.status, common.PASS)

    def test_no_markers_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "clean.py", "def f():\n    return 1\n")
            res = h1_todos.run(d)
            self.assertEqual(res.status, common.PASS)

    def test_word_boundary_no_false_positive(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "x.py", "size = 'XXXL'\nfixme_table = {}\n")
            res = h1_todos.run(d)
            self.assertEqual(res.status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
