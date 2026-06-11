"""Gate G3 — N+1 / Query-in-Loop-Heuristik (deterministisch). Tests.

Reale Tempdirs: Query-Call in einer for-Schleife -> WARN (mit Fundstelle); sauberer Code
(Query außerhalb von Schleifen, oder Query in im Schleifenkörper verschachtelter Funktion)
-> PASS; kein .py -> SKIP/NOT_APPLICABLE.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, g3_nplus1  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


_NPLUS1 = """\
def load(ids, session):
    out = []
    for i in ids:
        row = session.query(User).filter(User.id == i).get()
        out.append(row)
    return out
"""

_CLEAN = """\
def load(ids, session):
    rows = session.query(User).filter(User.id.in_(ids)).all()
    return [r for r in rows]
"""

_NESTED_FUNC = """\
def make_handlers(items):
    handlers = []
    for it in items:
        def handler(db):
            return db.query(Thing).get()
        handlers.append(handler)
    return handlers
"""


class NoPythonSkips(unittest.TestCase):
    def test_no_python_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "kein Python\n")
            res = g3_nplus1.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


class QueryInLoopWarns(unittest.TestCase):
    def test_query_in_for_loop_warns_with_finding(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "repo.py", _NPLUS1)
            res = g3_nplus1.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertTrue(res.findings)
            self.assertEqual(res.findings[0].kind, "n+1-query")
            self.assertEqual(res.findings[0].file, "repo.py")
            self.assertGreater(res.findings[0].line, 0)


class CleanCodePasses(unittest.TestCase):
    def test_bulk_query_outside_loop_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "repo.py", _CLEAN)
            res = g3_nplus1.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertEqual(len(res.findings), 0)

    def test_query_in_nested_func_in_loop_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "repo.py", _NESTED_FUNC)
            res = g3_nplus1.run(d)
            self.assertEqual(res.status, common.PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
