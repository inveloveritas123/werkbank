"""Go-Unterstützung in den Gates (B1/B2/B3, C1/C2, D1/D2, H2). Tests.

Die Go-Werkzeuge werden mit Fake-Binaries (Shell-Skripte auf dem PATH) simuliert:
Je Werkzeug/Unterbefehl steuern Dateien <tool>.<key>.{out,err,rc,sleep} im Fake-Verzeichnis
Ausgabe, Returncode und Laufzeit. Der echte Smoke-Test am Ende läuft nur, wenn `go` installiert ist.
"""
import json
import os
import shutil
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
sys.path.insert(0, GATES_DIR)

import runner  # noqa: E402
from checks import (  # noqa: E402
    b_gates,
    c1_tests,
    c2_coverage,
    common,
    d1_sast,
    d2_sca,
    golang,
    h2_complexity,
)

GATES_YAML = os.path.join(REPO_ROOT, "gates", "gates.yaml")

_FAKE = textwrap.dedent("""\
    #!/bin/sh
    D="$(cd "$(dirname "$0")" && pwd)"
    N="$(basename "$0")"
    echo "$N|$PWD|$*" >> "$D/calls.log"
    key=main
    if [ "$N" = "go" ] || [ "$N" = "wgo" ]; then
      key="$1"
      case "$2" in
        -coverprofile=*) key=cover; echo "mode: set" > "${2#-coverprofile=}";;
      esac
    fi
    [ -f "$D/$N.$key.sleep" ] && sleep "$(cat "$D/$N.$key.sleep")"
    [ -f "$D/$N.$key.out" ] && cat "$D/$N.$key.out"
    [ -f "$D/$N.$key.err" ] && cat "$D/$N.$key.err" >&2
    rc=0
    [ -f "$D/$N.$key.rc" ] && rc="$(cat "$D/$N.$key.rc")"
    exit "$rc"
    """)

_WRAPPER = textwrap.dedent("""\
    #!/bin/sh
    # simuliert einen Docker-Wrapper: `wgo go ...` -> ruft das Fake-Werkzeug `go` (bzw. gofmt)
    D="$(cd "$(dirname "$0")" && pwd)"
    echo "wgo|$*" >> "$D/calls.log"
    t="$1"; shift
    exec "$D/$t" "$@"
    """)


def _w(base, rel, content=""):
    p = os.path.join(base, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class Fakes:
    """Fake-Werkzeugverzeichnis; set() steuert das Verhalten je Unterbefehl."""

    def __init__(self, base, tools=("go", "gofmt", "gosec", "govulncheck", "gocyclo")):
        self.dir = os.path.join(base, "fakebin")
        os.makedirs(self.dir)
        for t in tools:
            self._install(t, _FAKE)

    def _install(self, name, body):
        p = os.path.join(self.dir, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        os.chmod(p, 0o755)

    def add_wrapper(self):
        self._install("wgo", _WRAPPER)

    def set(self, tool, key, rc=0, out="", err="", sleep=None):
        base = os.path.join(self.dir, "%s.%s" % (tool, key))
        for suffix, val in (("rc", str(rc)), ("out", out), ("err", err)):
            with open("%s.%s" % (base, suffix), "w", encoding="utf-8") as f:
                f.write(val)
        if sleep is not None:
            with open(base + ".sleep", "w", encoding="utf-8") as f:
                f.write(str(sleep))

    def calls(self):
        p = os.path.join(self.dir, "calls.log")
        if not os.path.exists(p):
            return []
        with open(p, encoding="utf-8") as f:
            return [ln.rstrip("\n") for ln in f]


_WB_ENV = ("WERKBANK_GO", "WERKBANK_GOFMT", "WERKBANK_GOSEC", "WERKBANK_GOVULNCHECK",
           "WERKBANK_GOCYCLO", "WERKBANK_GO_TIMEOUT", "C2_MIN", "H2_MAX")


class GoTestCase(unittest.TestCase):
    """Temp-Projekt + Fake-Werkzeuge auf dem PATH; WERKBANK_*-Variablen der Umgebung neutralisiert."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = os.path.join(self._tmp.name, "proj")
        os.makedirs(self.root)
        self.fakes = Fakes(self._tmp.name)
        env = {k: v for k, v in os.environ.items() if k not in _WB_ENV}
        # Minimaler PATH: nur Fakes + System-Basis (sh/cat/sleep). Dadurch sind weder ein echtes
        # go noch ruff/mypy/bandit aus der Entwicklungsumgebung sichtbar -> deterministisch.
        env["PATH"] = self.fakes.dir + os.pathsep + "/usr/bin" + os.pathsep + "/bin"
        p = mock.patch.dict(os.environ, env, clear=True)
        p.start()
        self.addCleanup(p.stop)

    def no_tools(self):
        """PATH ohne jedes Go-Werkzeug (TOOL_MISSING-Pfad)."""
        empty = os.path.join(self._tmp.name, "empty")
        os.makedirs(empty, exist_ok=True)
        p = mock.patch.dict(os.environ, {"PATH": empty})
        p.start()
        self.addCleanup(p.stop)

    def go_project(self, sub=None, tests=True):
        base = os.path.join(self.root, sub) if sub else self.root
        _w(base, "go.mod", "module example.com/app\n\ngo 1.25\n")
        _w(base, "main.go", "package main\n\nfunc main() {}\n")
        if tests:
            _w(base, "main_test.go", "package main\n\nimport \"testing\"\n\nfunc TestX(t *testing.T) {}\n")
        return base


# ---------------------------------------------------------------- Erkennung

class ModuleDetection(GoTestCase):
    def test_root_module(self):
        self.go_project()
        mods = golang.find_modules(self.root)
        self.assertEqual([m.rel for m in mods], ["."])
        self.assertEqual(mods[0].label, "Go")

    def test_subdir_and_multiple_modules_sorted(self):
        self.go_project("backend")
        self.go_project("tools/gen")
        mods = golang.find_modules(self.root)
        self.assertEqual([m.rel for m in mods], ["backend", "tools/gen"])
        self.assertEqual(mods[0].label, "Go backend")

    def test_vendor_node_modules_git_testdata_ignored(self):
        for d in ("vendor/x", "node_modules/y", ".git/z", "pkg/testdata/m", ".venv/lib", "venv/lib"):
            _w(self.root, os.path.join(d, "go.mod"), "module m\n")
        self.assertEqual(golang.find_modules(self.root), [])

    def test_exclude_dirs_and_exclude_abs_respected(self):
        self.go_project("deploy")
        self.go_project("backend")
        got = golang.find_modules(self.root, exclude_dirs=common.DEFAULT_EXCLUDE_DIRS | {"deploy"})
        self.assertEqual([m.rel for m in got], ["backend"])
        got = golang.find_modules(self.root, exclude_abs={os.path.join(self.root, "backend")})
        self.assertEqual([m.rel for m in got], ["deploy"])

    def test_no_go_mod_means_no_module(self):
        _w(self.root, "app.py", "x = 1\n")
        _w(self.root, "main.go", "package main\n")     # .go ohne go.mod -> kein Go-Projekt
        self.assertEqual(golang.find_modules(self.root), [])

    def test_framework_dirs_marker_excludes_go_module(self):
        self.go_project("deploy")
        _w(self.root, ".werkbank/framework-dirs", "deploy\n")
        fw = runner._framework_exclude(self.root)
        self.assertEqual(golang.find_modules(self.root, set(common.DEFAULT_EXCLUDE_DIRS) | fw), [])


# ---------------------------------------------------------------- Weiche / Kompatibilität

class PythonUnchanged(GoTestCase):
    def test_combine_without_go_mod_returns_python_result_object(self):
        _w(self.root, "app.py", "x = 1\n")
        sentinel = common.CheckResult("B3", common.PASS, "genau so wie früher")
        got = golang.combine("B3", self.root, None, None, py=lambda: sentinel,
                             go=lambda m: self.fail("Go-Zweig darf nicht laufen"))
        self.assertIs(got, sentinel)

    def test_python_project_texts_identical(self):
        _w(self.root, "app.py", "x = 1\n")
        self.assertEqual(b_gates.run_b3(self.root).summary, "Build/Compile sauber (1 .py)")
        res = h2_complexity.run(self.root)
        self.assertEqual(res.summary, "alle Funktionen <= Komplexitaet 12 (1 .py)")
        self.assertEqual(self.fakes.calls(), [])           # kein Go-Werkzeug berührt

    def test_python_only_no_python_code_still_not_applicable(self):
        _w(self.root, "README.md", "x\n")
        for res in (b_gates.run_b3(self.root), d1_sast.run(self.root), h2_complexity.run(self.root)):
            self.assertEqual(res.status, common.SKIP)
            self.assertEqual(res.skip_reason, common.NOT_APPLICABLE)
            self.assertEqual(res.summary, "kein Python-Code")

    def test_go_module_only_in_framework_dir_does_not_count(self):
        # Python-Projekt mit kopiertem Framework, das ein go.mod enthält -> verhält sich wie vorher.
        _w(self.root, "app.py", "x = 1\n")
        self.go_project("deploy")
        excl = set(common.DEFAULT_EXCLUDE_DIRS) | {"deploy"}
        res = b_gates.run_b3(self.root, exclude_dirs=excl)
        self.assertEqual((res.status, res.summary), (common.PASS, "Build/Compile sauber (1 .py)"))
        self.assertEqual(self.fakes.calls(), [])


class MergeResults(unittest.TestCase):
    def R(self, status, summary="s", reason=None):
        return common.CheckResult("X", status, summary, skip_reason=reason)

    def test_strictest_wins(self):
        m = common.merge_results
        self.assertEqual(m("X", [("A", self.R(common.PASS)), ("B", self.R(common.FAIL))]).status, common.FAIL)
        self.assertEqual(m("X", [("A", self.R(common.SKIP, reason=common.TOOL_MISSING)),
                                 ("B", self.R(common.FAIL))]).status, common.FAIL)
        self.assertEqual(m("X", [("A", self.R(common.PASS)),
                                 ("B", self.R(common.SKIP, reason=common.TOOL_MISSING))]).status, common.SKIP)
        self.assertEqual(m("X", [("A", self.R(common.PASS)), ("B", self.R(common.WARN))]).status, common.WARN)
        self.assertEqual(m("X", [("A", self.R(common.WARN)),
                                 ("B", self.R(common.SKIP, reason=common.TOOL_MISSING))]).status, common.SKIP)
        self.assertEqual(m("X", [("A", self.R(common.PASS)), ("B", self.R(common.PASS))]).status, common.PASS)

    def test_not_applicable_does_not_count_but_is_mentioned(self):
        res = common.merge_results("X", [("Python", self.R(common.SKIP, "kein Python-Code", common.NOT_APPLICABLE)),
                                         ("Go", self.R(common.PASS, "sauber"))])
        self.assertEqual(res.status, common.PASS)
        self.assertIn("nicht anwendbar: Python: kein Python-Code", res.summary)

    def test_all_not_applicable_stays_not_applicable(self):
        res = common.merge_results("X", [("A", self.R(common.SKIP, "n1", common.NOT_APPLICABLE)),
                                         ("B", self.R(common.SKIP, "n2", common.NOT_APPLICABLE))])
        self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.NOT_APPLICABLE))

    def test_skip_reason_priority_and_findings_kept(self):
        f = common.Finding("a.go", 3, "k", "e")
        res = common.merge_results("X", [
            ("A", self.R(common.SKIP, "x", None)),
            ("B", self.R(common.SKIP, "y", common.TOOL_MISSING)),
            ("C", common.CheckResult("X", common.PASS, "z", [f]))])
        self.assertEqual(res.skip_reason, common.TOOL_MISSING)
        self.assertEqual(res.findings, [f])

    def test_identical_summaries_grouped(self):
        res = common.merge_results("X", [("Go a", self.R(common.PASS, "ok")), ("Go b", self.R(common.PASS, "ok"))])
        self.assertEqual(res.summary, "Go a, Go b: ok")


# ---------------------------------------------------------------- Konfiguration

class CommandConfig(unittest.TestCase):
    def _env(self, **kw):
        env = {k: v for k, v in os.environ.items() if k not in _WB_ENV}
        env.update(kw)
        return mock.patch.dict(os.environ, env, clear=True)

    def test_defaults(self):
        with self._env():
            self.assertEqual(golang.go_cmd(), ["go"])
            self.assertEqual(golang.gofmt_cmd(), ["gofmt"])

    def test_wrapper_is_split_and_gofmt_derived(self):
        with self._env(WERKBANK_GO="docker run --rm -v /a:/src -w /src golang:1.25 go"):
            self.assertEqual(golang.go_cmd()[-2:], ["golang:1.25", "go"])
            self.assertEqual(golang.gofmt_cmd()[-2:], ["golang:1.25", "gofmt"])
            self.assertEqual(golang.gofmt_cmd()[:3], ["docker", "run", "--rm"])

    def test_gofmt_derived_from_path_and_explicit_override(self):
        with self._env(WERKBANK_GO="/opt/go/bin/go"):
            self.assertEqual(golang.gofmt_cmd(), ["/opt/go/bin/gofmt"])
        with self._env(WERKBANK_GO="/opt/go/bin/go", WERKBANK_GOFMT="mygofmt -x"):
            self.assertEqual(golang.gofmt_cmd(), ["mygofmt", "-x"])

    def test_broken_quoting_falls_back_to_default(self):
        with self._env(WERKBANK_GO="go 'unbalanced"):
            self.assertEqual(golang.go_cmd(), ["go"])

    def test_timeout_parsing(self):
        with self._env():
            self.assertEqual(golang._timeout(), golang.DEFAULT_TIMEOUT)
        with self._env(WERKBANK_GO_TIMEOUT="7"):
            self.assertEqual(golang._timeout(), 7)
        with self._env(WERKBANK_GO_TIMEOUT="abc"):
            self.assertEqual(golang._timeout(), golang.DEFAULT_TIMEOUT)
        with self._env(WERKBANK_GO_TIMEOUT="0"):
            self.assertEqual(golang._timeout(), golang.DEFAULT_TIMEOUT)


class WrapperIsUsed(GoTestCase):
    def test_wrapper_runs_go_and_gofmt(self):
        self.fakes.add_wrapper()
        self.go_project()
        os.environ["WERKBANK_GO"] = "wgo go"
        self.assertEqual(b_gates.run_b1(self.root).status, common.PASS)
        self.assertEqual(b_gates.run_b3(self.root).status, common.PASS)
        log = "\n".join(self.fakes.calls())
        self.assertIn("wgo|gofmt -l .", log)
        self.assertIn("wgo|go build ./...", log)


# ---------------------------------------------------------------- B1/B2/B3

class BGatesGo(GoTestCase):
    def test_pure_go_all_pass_without_python(self):
        self.go_project()
        for fn in (b_gates.run_b1, b_gates.run_b2, b_gates.run_b3):
            res = fn(self.root)
            self.assertEqual(res.status, common.PASS, res.summary)
            self.assertTrue(res.summary.startswith("Go: "), res.summary)
        calls = self.fakes.calls()
        self.assertTrue(any(c.startswith("gofmt|") and c.endswith("|-l .") for c in calls))
        self.assertTrue(any(c.endswith("|vet ./...") for c in calls))
        self.assertTrue(any(c.endswith("|build ./...") for c in calls))
        self.assertFalse(any(c.startswith(("ruff", "mypy")) for c in calls))

    def test_subdir_module_runs_in_module_dir(self):
        self.go_project("backend")
        self.assertEqual(b_gates.run_b3(self.root).status, common.PASS)
        self.assertTrue(any(c.startswith("go|") and c.split("|")[1].endswith("/backend") for c in self.fakes.calls()))

    def test_gofmt_output_fails_with_finding(self):
        self.go_project("backend")
        self.fakes.set("gofmt", "main", out="main.go\ninternal/x.go\nvendor/dep/a.go\ntestdata/t.go\n")
        res = b_gates.run_b1(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("2 Datei(en)", res.summary)
        self.assertEqual([f.file for f in res.findings], ["backend/main.go", "backend/internal/x.go"])

    def test_gofmt_vendor_only_output_is_pass(self):
        self.go_project()
        self.fakes.set("gofmt", "main", out="vendor/dep/a.go\n")
        self.assertEqual(b_gates.run_b1(self.root).status, common.PASS)

    def test_gofmt_error_fails(self):
        self.go_project()
        self.fakes.set("gofmt", "main", rc=2, err="main.go:3:1: expected declaration\n")
        res = b_gates.run_b1(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("expected declaration", res.summary)

    def test_vet_and_build_failures_parse_findings(self):
        self.go_project()
        self.fakes.set("go", "vet", rc=1, err="# example.com/app\nvet: ./main.go:7:2: undefined: foo\n")
        self.fakes.set("go", "build", rc=1, err="# example.com/app\n./main.go:7:2: undefined: foo\n")
        for fn, kind in ((b_gates.run_b2, "vet"), (b_gates.run_b3, "build-error")):
            res = fn(self.root)
            self.assertEqual(res.status, common.FAIL)
            self.assertEqual((res.findings[0].file, res.findings[0].line, res.findings[0].kind),
                             ("main.go", 7, kind))
            self.assertIn("undefined: foo", res.summary)

    def test_tool_missing_is_skip_tool_missing(self):
        self.go_project()
        self.no_tools()
        for fn in (b_gates.run_b1, b_gates.run_b2, b_gates.run_b3):
            res = fn(self.root)
            self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.TOOL_MISSING))

    def test_gofmt_missing_but_go_present_is_tool_missing(self):
        self.go_project()
        os.remove(os.path.join(self.fakes.dir, "gofmt"))
        self.fakes.set("go", "env", out="/nonexistent-goroot\n")
        res = b_gates.run_b1(self.root)
        self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.TOOL_MISSING))
        self.assertIn("gofmt", res.summary)

    def test_gofmt_found_via_goroot_fallback(self):
        self.go_project()
        goroot = os.path.join(self._tmp.name, "goroot")
        os.makedirs(os.path.join(goroot, "bin"))
        shutil.move(os.path.join(self.fakes.dir, "gofmt"), os.path.join(goroot, "bin", "gofmt"))
        self.fakes.set("go", "env", out=goroot + "\n")
        self.assertEqual(b_gates.run_b1(self.root).status, common.PASS)

    def test_timeout_is_fail_with_note(self):
        self.go_project()
        self.fakes.set("go", "build", sleep=30)
        os.environ["WERKBANK_GO_TIMEOUT"] = "1"
        res = b_gates.run_b3(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("Zeitüberschreitung nach 1 s", res.summary)

    def test_mixed_python_and_go_strictest(self):
        self.go_project("backend")
        _w(self.root, "tools/helper.py", "x = 1\n")
        res = b_gates.run_b3(self.root)
        self.assertEqual(res.status, common.PASS)
        self.assertIn("Python: Build/Compile sauber (1 .py)", res.summary)
        self.assertIn("Go backend: go build sauber", res.summary)
        # Python kaputt, Go grün -> FAIL
        _w(self.root, "tools/bad.py", "def f(:\n")
        res = b_gates.run_b3(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertEqual(res.findings[0].file, "tools/bad.py")
        # Python grün, Go rot -> FAIL
        os.remove(os.path.join(self.root, "tools", "bad.py"))
        self.fakes.set("go", "build", rc=1, err="./main.go:1:1: boom\n")
        res = b_gates.run_b3(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("Go backend", res.summary)
        self.assertNotIn("Python:", res.summary)

    def test_mixed_go_tool_missing_beats_python_pass(self):
        self.go_project("backend")
        _w(self.root, "tools/helper.py", "x = 1\n")
        self.no_tools()
        res = b_gates.run_b3(self.root)
        self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.TOOL_MISSING))


# ---------------------------------------------------------------- C1/C2

class TestGatesGo(GoTestCase):
    def test_c1_pass_and_counts_packages(self):
        self.go_project()
        self.fakes.set("go", "test", out="ok  \texample.com/app\t0.01s\nok  \texample.com/app/x\t0.02s\n"
                                         "?   \texample.com/app/y\t[no test files]\n")
        res = c1_tests.run(self.root)
        self.assertEqual(res.status, common.PASS)
        self.assertIn("2 Pakete", res.summary)

    def test_c1_fail_names_failed_packages(self):
        self.go_project("backend")
        self.fakes.set("go", "test", rc=1, out="--- FAIL: TestX (0.00s)\nFAIL\nFAIL\texample.com/app\t0.01s\n"
                                               "FAIL\texample.com/app/z [build failed]\n")
        res = c1_tests.run(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("2 Paket(e)", res.summary)
        self.assertEqual([f.evidence for f in res.findings], ["example.com/app", "example.com/app/z"])

    def test_c1_module_without_tests_is_not_applicable(self):
        self.go_project(tests=False)
        res = c1_tests.run(self.root)
        self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.NOT_APPLICABLE))
        self.assertEqual(self.fakes.calls(), [])

    def test_c1_multi_module_one_without_tests_still_checks_others(self):
        self.go_project("backend")
        self.go_project("tools", tests=False)
        res = c1_tests.run(self.root)
        self.assertEqual(res.status, common.PASS)
        self.assertIn("nicht anwendbar: Go tools", res.summary)

    def test_c1_go_present_python_tests_dir_runs_both(self):
        self.go_project("backend")
        _w(self.root, "tests/test_a.py", "import unittest\n\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.assertTrue(True)\n")
        res = c1_tests.run(self.root)
        self.assertEqual(res.status, common.PASS)
        self.assertIn("Python: Tests grün", res.summary)
        self.assertIn("Go backend: Tests grün", res.summary)

    def test_c1_go_with_non_python_tests_dir_does_not_run_python(self):
        # tests/ enthält z. B. GDScript-Tests, aber keinen Python-Code -> kein unittest-Lauf.
        self.go_project("backend")
        _w(self.root, "tests/test_ui.gd", "extends Node\n")
        res = c1_tests.run(self.root)
        self.assertEqual(res.status, common.PASS)
        self.assertNotIn("Python", res.summary)

    def _cover(self, pct):
        self.fakes.set("go", "tool", out="example.com/app/main.go:3:\tmain\t100.0%%\ntotal:\t\t\t(statements)\t%s%%\n" % pct)

    def test_c2_threshold_default_70(self):
        self.go_project()
        self._cover("83.3")
        res = c2_coverage.run(self.root)
        self.assertEqual((res.status, res.summary), (common.PASS, "Go: Coverage 83.3% >= 70%"))
        self._cover("55.0")
        res = c2_coverage.run(self.root)
        self.assertEqual((res.status, res.summary), (common.FAIL, "Go: Coverage 55.0% < 70%"))

    def test_c2_threshold_from_env_and_profile_cleanup(self):
        self.go_project()
        self._cover("55.0")
        os.environ["C2_MIN"] = "50"
        self.assertEqual(c2_coverage.run(self.root).status, common.PASS)
        self.assertFalse(os.path.exists(os.path.join(self.root, golang._COVER_FILE)))
        calls = "\n".join(self.fakes.calls())
        self.assertIn("test -coverprofile=%s ./..." % golang._COVER_FILE, calls)
        self.assertIn("tool cover -func=%s" % golang._COVER_FILE, calls)

    def test_c2_unreadable_report_is_skip(self):
        self.go_project()
        self.fakes.set("go", "tool", out="kaputt\n")
        res = c2_coverage.run(self.root)
        self.assertEqual(res.status, common.SKIP)

    def test_c2_no_tests_not_applicable_and_tool_missing(self):
        self.go_project(tests=False)
        self.assertEqual(c2_coverage.run(self.root).skip_reason, common.NOT_APPLICABLE)
        self.go_project()
        self.no_tools()
        self.assertEqual(c2_coverage.run(self.root).skip_reason, common.TOOL_MISSING)

    def test_c2_each_module_must_reach_threshold(self):
        self.go_project("a")
        self.go_project("b")
        self._cover("90.0")
        self.assertEqual(c2_coverage.run(self.root).status, common.PASS)
        self._cover("10.0")
        res = c2_coverage.run(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("Go a, Go b", res.summary)


# ---------------------------------------------------------------- D1

def _gosec(*issues, errors=None):
    return json.dumps({"Golang errors": errors or {}, "Issues": list(issues), "Stats": {"files": 1}})


def _issue(sev, rule="G101", file="/x/backend/main.go", line="12", details="Potential hardcoded credentials"):
    return {"severity": sev, "confidence": "HIGH", "rule_id": rule, "details": details,
            "file": file, "line": line, "code": "password := \"geheim\""}


class SastGo(GoTestCase):
    def test_high_and_medium_fail_without_code_snippet(self):
        self.go_project("backend")
        f = os.path.join(self.root, "backend", "main.go")
        self.fakes.set("gosec", "main", rc=1, out=_gosec(_issue("HIGH", file=f), _issue("MEDIUM", "G401", f, "7-9"), _issue("LOW", "G104", f)))
        res = d1_sast.run(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("2 High/Medium", res.summary)
        self.assertEqual([(x.file, x.line, x.kind) for x in res.findings],
                         [("backend/main.go", 12, "sast:high/G101"), ("backend/main.go", 7, "sast:medium/G401")])
        self.assertNotIn("geheim", "\n".join(res.to_report_lines()))

    def test_low_only_passes_clean_passes(self):
        self.go_project()
        self.fakes.set("gosec", "main", rc=1, out=_gosec(_issue("LOW"), _issue("LOW")))
        res = d1_sast.run(self.root)
        self.assertEqual(res.status, common.PASS)
        self.assertIn("2 Low", res.summary)
        self.fakes.set("gosec", "main", out=_gosec())
        self.assertEqual(d1_sast.run(self.root).summary, "Go: kein SAST-Befund (gosec)")

    def test_log_noise_before_json_tolerated(self):
        self.go_project()
        self.fakes.set("gosec", "main", out="[gosec] 2026/01/01 Including rules: default\n" + _gosec(_issue("HIGH")))
        self.assertEqual(d1_sast.run(self.root).status, common.FAIL)

    def test_golang_errors_fail(self):
        self.go_project()
        self.fakes.set("gosec", "main", out=_gosec(errors={"main.go": [{"line": 1, "column": 1, "error": "x"}]}))
        res = d1_sast.run(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("nicht analysieren", res.summary)

    def test_unreadable_output_fails(self):
        self.go_project()
        self.fakes.set("gosec", "main", rc=1, out="", err="boom\n")
        res = d1_sast.run(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("nicht lesbar", res.summary)

    def test_gosec_missing_is_tool_missing(self):
        self.go_project()
        os.remove(os.path.join(self.fakes.dir, "gosec"))
        res = d1_sast.run(self.root)
        self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.TOOL_MISSING))
        self.assertIn("gosec", res.summary)

    def test_pure_go_not_red_for_missing_python(self):
        self.go_project()
        self.fakes.set("gosec", "main", out=_gosec())
        self.assertNotIn("kein Python", d1_sast.run(self.root).summary)

    def test_mixed_project_bandit_missing_makes_it_tool_missing(self):
        self.go_project("backend")
        _w(self.root, "tools/x.py", "x = 1\n")
        self.fakes.set("gosec", "main", out=_gosec())
        res = d1_sast.run(self.root)
        self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.TOOL_MISSING))
        self.assertIn("bandit nicht installiert", res.summary)

    def test_mixed_project_both_clean_and_python_finding_blocks(self):
        self.go_project("backend")
        _w(self.root, "tools/x.py", "x = 1\n")
        self.fakes._install("bandit", _FAKE)
        self.fakes.set("bandit", "main", out=json.dumps({"results": []}))
        self.fakes.set("gosec", "main", out=_gosec())
        res = d1_sast.run(self.root)
        self.assertEqual(res.status, common.PASS)
        self.assertIn("Python: kein SAST-Befund (bandit)", res.summary)
        self.assertIn("Go backend: kein SAST-Befund (gosec)", res.summary)
        self.fakes.set("bandit", "main", out=json.dumps({"results": [
            {"filename": os.path.join(self.root, "tools", "x.py"), "issue_severity": "HIGH",
             "test_id": "B602", "line_number": 1, "test_name": "shell"}]}))
        self.assertEqual(d1_sast.run(self.root).status, common.FAIL)


# ---------------------------------------------------------------- D2

def _vuln_stream(*findings):
    """Pretty-printed Stream wie bei govulncheck (hintereinander stehende JSON-Objekte)."""
    parts = [json.dumps({"config": {"protocol_version": "v1.0.0"}}, indent=2),
             json.dumps({"progress": {"message": "Scanning"}}, indent=2),
             json.dumps({"osv": {"id": "GO-2024-0001", "summary": "Geheimer Advisory-Text"}}, indent=2)]
    for osv, trace in findings:
        parts.append(json.dumps({"finding": {"osv": osv, "fixed_version": "v1.2.3", "trace": trace}}, indent=2))
    return "\n".join(parts) + "\n"


_SYMBOL = [{"module": "golang.org/x/net", "version": "v0.1.0", "package": "golang.org/x/net/html",
            "function": "Parse", "position": {"filename": "x.go", "line": 1}},
           {"module": "example.com/app", "function": "main"}]
_PACKAGE_ONLY = [{"module": "golang.org/x/net", "version": "v0.1.0", "package": "golang.org/x/net/html"}]
_MODULE_ONLY = [{"module": "golang.org/x/net", "version": "v0.1.0"}]


class ScaGo(GoTestCase):
    def test_parser_reachable_vs_weak(self):
        raw = _vuln_stream(("GO-1", _SYMBOL), ("GO-2", _PACKAGE_ONLY), ("GO-3", _MODULE_ONLY), ("GO-1", _MODULE_ONLY))
        reachable, weak, n = golang.parse_govulncheck(raw)
        self.assertEqual(reachable, {"GO-1": "golang.org/x/net"})
        self.assertEqual(weak, {"GO-2", "GO-3"})
        self.assertEqual(n, 7)

    def test_parser_ndjson_and_leading_noise(self):
        raw = "govulncheck: Scanning\n" + json.dumps({"config": {}}) + "\n" + json.dumps(
            {"finding": {"osv": "GO-9", "trace": _SYMBOL}}) + "\n"
        reachable, weak, n = golang.parse_govulncheck(raw)
        self.assertEqual((list(reachable), weak, n), (["GO-9"], set(), 2))

    def test_parser_truncated_json_raises(self):
        with self.assertRaises(ValueError):
            golang.parse_govulncheck('{"config": {}}\n{"finding": {"osv": ')

    def test_reachable_fails_without_advisory_text(self):
        self.go_project("backend")
        self.fakes.set("govulncheck", "main", out=_vuln_stream(("GO-2024-0042", _SYMBOL)))
        res = d2_sca.run(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("1 erreichbare Schwachstelle", res.summary)
        self.assertEqual(res.findings[0].file, "backend/go.mod")
        self.assertIn("GO-2024-0042", res.findings[0].evidence)
        self.assertNotIn("Geheimer Advisory-Text", "\n".join(res.to_report_lines()))

    def test_only_imported_vulns_pass_with_note(self):
        self.go_project()
        self.fakes.set("govulncheck", "main", out=_vuln_stream(("GO-2", _PACKAGE_ONLY), ("GO-3", _MODULE_ONLY)))
        res = d2_sca.run(self.root)
        self.assertEqual(res.status, common.PASS)
        self.assertIn("2 nur importiert", res.summary)

    def test_clean_passes(self):
        self.go_project()
        self.fakes.set("govulncheck", "main", out=_vuln_stream())
        self.assertEqual(d2_sca.run(self.root).status, common.PASS)

    def test_tool_error_with_partial_output_fails(self):
        # Reale Beobachtung: Ladefehler -> rc=1, stdout enthält nur das config-Objekt.
        self.go_project()
        self.fakes.set("govulncheck", "main", rc=1, out=json.dumps({"config": {}}),
                       err="govulncheck: loading packages:\nThere are errors\n")
        res = d2_sca.run(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("rc=1", res.summary)

    def test_rc3_findings_are_parsed(self):
        self.go_project()
        self.fakes.set("govulncheck", "main", rc=3, out=_vuln_stream(("GO-1", _SYMBOL)))
        self.assertEqual(d2_sca.run(self.root).status, common.FAIL)

    def test_empty_and_garbage_output_fail(self):
        self.go_project()
        self.fakes.set("govulncheck", "main", out="")
        self.assertEqual(d2_sca.run(self.root).status, common.FAIL)
        self.fakes.set("govulncheck", "main", out='{"config": {}}\n{"finding": ')
        self.assertEqual(d2_sca.run(self.root).status, common.FAIL)

    def test_missing_is_tool_missing(self):
        self.go_project()
        os.remove(os.path.join(self.fakes.dir, "govulncheck"))
        res = d2_sca.run(self.root)
        self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.TOOL_MISSING))

    def test_args_use_format_json(self):
        self.go_project()
        self.fakes.set("govulncheck", "main", out=_vuln_stream())
        d2_sca.run(self.root)
        self.assertTrue(any(c.endswith("|-format json ./...") for c in self.fakes.calls()))


# ---------------------------------------------------------------- H2

class ComplexityGo(GoTestCase):
    def test_over_threshold_warns(self):
        self.go_project("backend")
        self.fakes.set("gocyclo", "main", rc=1, out="15 main Run main.go:10:1\n13 store (*DB).Load internal/db.go:4:1\n"
                                                     "20 dep Gen vendor/dep/gen.go:1:1\n")
        res = h2_complexity.run(self.root)
        self.assertEqual(res.status, common.WARN)
        self.assertIn("2 Funktion(en) über Komplexität 12", res.summary)
        self.assertEqual((res.findings[0].file, res.findings[0].line), ("backend/main.go", 10))
        self.assertTrue(any("-over 12" in c for c in self.fakes.calls()))

    def test_threshold_from_env_and_clean(self):
        self.go_project()
        os.environ["H2_MAX"] = "5"
        self.assertEqual(h2_complexity.run(self.root).status, common.PASS)
        self.assertTrue(any("-over 5" in c for c in self.fakes.calls()))

    def test_gocyclo_optional_tool_missing(self):
        self.go_project()
        os.remove(os.path.join(self.fakes.dir, "gocyclo"))
        res = h2_complexity.run(self.root)
        self.assertEqual((res.status, res.skip_reason), (common.SKIP, common.TOOL_MISSING))


# ---------------------------------------------------------------- Runner / hartes Grün

PFLICHT = """\
default_profile: go_basis
profiles:
  go_basis:
    desc: "Go-Projekt hermetisch"
    required: [B1, B2, B3, C1, C2, D1, D2]
"""


class RunnerHardGreen(GoTestCase):
    def _run(self, **kw):
        ph = _w(self._tmp.name, "ph.yaml", PFLICHT)
        out = os.path.join(self._tmp.name, "report.md")
        return runner.run_gates(GATES_YAML, self.root, out, profile="go_basis", pflichtenheft_path=ph,
                                fail_fast=False, **kw)

    def _healthy(self):
        self.fakes.set("go", "test", out="ok  \texample.com/app\t0.01s\n")
        self.fakes.set("go", "tool", out="total:\t(statements)\t91.0%\n")
        self.fakes.set("gosec", "main", out=_gosec())
        self.fakes.set("govulncheck", "main", out=_vuln_stream())

    def test_pure_go_project_becomes_green(self):
        self.go_project("backend")
        self._healthy()
        res = self._run()
        self.assertEqual(res["overall"], "GRUEN", res["verdict"])
        for gid in ("B1", "B2", "B3", "C1", "C2", "D1", "D2"):
            self.assertEqual(res["results"][gid]["status"], common.PASS, gid)

    def test_missing_go_tools_make_required_gates_uncovered(self):
        self.go_project("backend")
        self.no_tools()
        res = self._run()
        self.assertEqual(res["overall"], "ROT")
        unc = {u["gate"]: u["reason"] for u in res["verdict"]["uncovered"]}
        self.assertEqual(unc, {g: common.TOOL_MISSING for g in ("B1", "B2", "B3", "C1", "C2", "D1", "D2")})

    def test_go_failure_makes_it_red(self):
        self.go_project("backend")
        self._healthy()
        self.fakes.set("go", "build", rc=1, err="./main.go:1:1: kaputt\n")
        res = self._run()
        self.assertEqual(res["overall"], "ROT")
        self.assertEqual([v["gate"] for v in res["verdict"]["violated"]], ["B3"])

    def test_framework_dir_go_module_is_not_checked_in_runner(self):
        _w(self.root, "app.py", "x = 1\n")
        self.go_project("deploy")
        _w(self.root, ".werkbank/framework-dirs", "deploy\n")
        ph = _w(self._tmp.name, "ph2.yaml", "default_profile: p\nprofiles:\n  p:\n    desc: x\n    required: [B3]\n")
        res = runner.run_gates(GATES_YAML, self.root, os.path.join(self._tmp.name, "r.md"),
                               profile="p", pflichtenheft_path=ph)
        self.assertEqual(res["results"]["B3"]["summary"], "Build/Compile sauber (1 .py)")
        self.assertEqual(self.fakes.calls(), [])


# ---------------------------------------------------------------- echter Smoke-Test

@unittest.skipUnless(shutil.which("go"), "go nicht installiert")
class RealGoSmoke(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        env = {k: v for k, v in os.environ.items() if k not in _WB_ENV}
        env.update({"GOTOOLCHAIN": "local", "GOPROXY": "off"})   # offline, kein Toolchain-Download
        p = mock.patch.dict(os.environ, env, clear=True)
        p.start()
        self.addCleanup(p.stop)
        base = os.path.join(self.root, "backend")
        _w(base, "go.mod", "module example.com/smoke\n\ngo 1.20\n")
        _w(base, "calc/calc.go", "package calc\n\n// Add addiert zwei Zahlen.\nfunc Add(a, b int) int { return a + b }\n")
        _w(base, "calc/calc_test.go",
           "package calc\n\nimport \"testing\"\n\nfunc TestAdd(t *testing.T) {\n\tif Add(1, 2) != 3 {\n\t\tt.Fatal(\"falsch\")\n\t}\n}\n")
        self.base = base

    def test_real_go_gates_green(self):
        for fn in (b_gates.run_b1, b_gates.run_b2, b_gates.run_b3, c1_tests.run, c2_coverage.run):
            res = fn(self.root)
            self.assertEqual(res.status, common.PASS, "%s: %s" % (res.gate, res.summary))
        self.assertFalse(os.path.exists(os.path.join(self.base, golang._COVER_FILE)))

    def test_real_go_defects_are_found(self):
        _w(self.base, "calc/unformatted.go", "package calc\n\nfunc  Sub(a,b int) int {return a-b}\n")
        self.assertEqual(b_gates.run_b1(self.root).status, common.FAIL)
        _w(self.base, "calc/broken.go", "package calc\n\nfunc Broken() int { return \"x\" }\n")
        res = b_gates.run_b3(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertEqual(res.findings[0].file, "backend/calc/broken.go")
        self.assertEqual(b_gates.run_b2(self.root).status, common.FAIL)
        # C2: ungetestete Funktion drückt unter die Schwelle
        os.remove(os.path.join(self.base, "calc", "broken.go"))
        _w(self.base, "calc/more.go", "package calc\n\nfunc A() int {\n\treturn 1\n}\n\nfunc B() int {\n\treturn 2\n}\n")
        os.environ["C2_MIN"] = "99"
        self.assertEqual(c2_coverage.run(self.root).status, common.FAIL)

    def test_real_failing_test_is_red(self):
        _w(self.base, "calc/calc_test.go",
           "package calc\n\nimport \"testing\"\n\nfunc TestAdd(t *testing.T) {\n\tt.Fatal(\"rot\")\n}\n")
        res = c1_tests.run(self.root)
        self.assertEqual(res.status, common.FAIL)
        self.assertIn("example.com/smoke/calc", res.findings[0].evidence)


if __name__ == "__main__":
    unittest.main(verbosity=2)
