"""Gate F3 — Golden-Output-Snapshot-Stabilitaet (WARN-Gate). Tests.

Reine Tempdir-Faelle:
- Snapshot-Dir mit Datei -> PASS
- Snapshot-Dir leer      -> WARN
- kein Snapshot-Dir      -> SKIP/NOT_APPLICABLE
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, GATES_DIR)

from checks import common, f3_snapshots  # noqa: E402


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class SnapshotsPresentPasses(unittest.TestCase):
    def test_snapshot_dir_with_file_is_pass(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "__snapshots__/render.snap", "golden output\n")
            res = f3_snapshots.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertIn("1", res.summary)
            self.assertIn("Golden-Snapshot", res.summary)

    def test_golden_dirname_is_recognized(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "golden/a.txt", "x\n")
            _write(d, "golden/b.txt", "y\n")
            res = f3_snapshots.run(d)
            self.assertEqual(res.status, common.PASS)
            self.assertIn("2", res.summary)


class EmptySnapshotDirWarns(unittest.TestCase):
    def test_empty_snapshot_dir_is_warn(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "snapshots"))
            res = f3_snapshots.run(d)
            self.assertEqual(res.status, common.WARN)
            self.assertIn("leer", res.summary)


class NoSnapshotDirSkips(unittest.TestCase):
    def test_no_snapshot_dir_is_skip_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "src/app.py", "x = 1\n")
            res = f3_snapshots.run(d)
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
