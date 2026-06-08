"""feedback v2 — rote Gates -> Backlog/GH-Issues, mit Gate-ID-Dedup, Egress-Redaction, Loop-Closure.

Adressiert die 3-Experten-Bewertung: Gate-ID-Dedup (nicht Notiz-Text), robuste Regex,
Egress-Redaction vor GitHub, Closure (PASS -> Backlog abhaken / Issue schließen).
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "feedback"))

import feedback  # noqa: E402

REPORT = """# GATE-REPORT
| Stufe | Gate | Flags | Ergebnis | Notiz |
| 2_static | D3 | block,deterministic | FAIL | 1 potentielle(s) Secret(s) im Diff/Tree |
| 5_integrity | F1 | block,deterministic | FAIL | 2 ungepinnte(s) Modell ('latest') |
| 7_maintainability | H4 | block,deterministic | PASS | CHANGELOG vorhanden |
"""


class Parse(unittest.TestCase):
    def test_only_failures(self):
        self.assertEqual({f["gate"] for f in feedback.parse_failures(REPORT)}, {"D3", "F1"})

    def test_passes_extracted(self):
        self.assertIn("H4", feedback.parse_passes(REPORT))

    def test_multichar_gate(self):
        rep = "| s | AB12 | block | FAIL | irgendwas |\n"
        self.assertEqual(feedback.parse_failures(rep)[0]["gate"], "AB12")

    def test_note_without_trailing_pipe(self):
        rep = "| s | D3 | block | FAIL | 1 Secret ohne End-Pipe\n"   # keine schließende |
        fails = feedback.parse_failures(rep)
        self.assertEqual(fails[0]["gate"], "D3")
        self.assertIn("Secret", fails[0]["note"])


class GateIdDedup(unittest.TestCase):
    def test_count_change_no_duplicate(self):
        existing = "## Auto-Findings\n- [ ] [D3] 1 potentielle(s) Secret(s) (2026-06-09)\n"
        rep = "| s | D3 | block | FAIL | 5 potentielle(s) Secret(s) im Diff/Tree |\n"
        self.assertEqual(feedback.plan(feedback.parse_failures(rep), existing), [])  # gleiche Gate-ID -> kein Dup

    def test_reopen_after_done(self):
        existing = "## Auto-Findings\n- [x] [D3] alt (2026-06-01)\n"   # erledigt
        rep = "| s | D3 | block | FAIL | wieder rot |\n"
        self.assertEqual({f["gate"] for f in feedback.plan(feedback.parse_failures(rep), existing)}, {"D3"})


class EgressRedaction(unittest.TestCase):
    def test_sanitize_masks_secret_pii_path(self):
        s = feedback.sanitize("secret in /home/u/id_rsa: AKIAQURTZ7XMPLE4KLMN mail a@b.de")
        self.assertNotIn("AKIAQURTZ7XMPLE4KLMN", s)
        self.assertNotIn("/home/u/id_rsa", s)
        self.assertNotIn("a@b.de", s)

    def test_legit_summary_survives(self):
        s = feedback.sanitize("2 ungepinnte(s) Modell ('latest')")
        self.assertIn("ungepinnte", s)

    def test_prose_single_slash_not_overmasked(self):
        s = feedback.sanitize("siehe /docs Abschnitt; aber /etc/passwd maskieren")
        self.assertIn("/docs", s)               # einzelnes /wort bleibt
        self.assertNotIn("/etc/passwd", s)      # echter Pfad maskiert

    def test_gh_body_is_sanitized(self):
        cmd = feedback.gh_issue_cmd({"gate": "D3", "note": "leak a@b.de /etc/passwd"})
        joined = " ".join(cmd)
        self.assertNotIn("a@b.de", joined)
        self.assertNotIn("/etc/passwd", joined)


class BacklogAppendAndClose(unittest.TestCase):
    def test_append_idempotent_by_gate(self):
        with tempfile.TemporaryDirectory() as d:
            bl = os.path.join(d, "BACKLOG.md")
            open(bl, "w").write("# BACKLOG\n")
            fails = feedback.parse_failures(REPORT)
            self.assertEqual(feedback.append_backlog(bl, fails), 2)
            self.assertEqual(feedback.append_backlog(bl, fails), 0)  # Gate-ID-Dedup

    def test_close_resolved_checks_off(self):
        with tempfile.TemporaryDirectory() as d:
            bl = os.path.join(d, "BACKLOG.md")
            open(bl, "w").write("# BACKLOG\n\n## Auto-Findings\n- [ ] [H4] CHANGELOG fehlt (2026-06-09)\n")
            closed = feedback.close_resolved_backlog(bl, ["H4"])
            self.assertEqual(closed, 1)
            txt = open(bl).read()
            self.assertIn("- [x] [H4]", txt)


class DryRun(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            bl = os.path.join(d, "BACKLOG.md")
            open(bl, "w").write("# BACKLOG\n")
            rc = feedback.main(["--report", _write(d, REPORT), "--backlog", bl])
            self.assertEqual(rc, 0)
            self.assertEqual(open(bl).read(), "# BACKLOG\n")


def _write(d, content):
    p = os.path.join(d, "rep.md")
    open(p, "w").write(content)
    return p


if __name__ == "__main__":
    unittest.main(verbosity=2)
