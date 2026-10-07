"""Go-Unterstützung für die Gates (B1/B2/B3, C1/C2, D1/D2, H2) — stdlib only.

Keine neuen Gate-IDs: dieselben Gates bekommen eine Go-Variante. Die Sprache wird erkannt:
**Go, wenn ein `go.mod` gefunden wird** — im Root oder in Unterordnern (Monorepo), unter
Beachtung der bestehenden Ausschlüsse (`exclude_dirs`/`exclude_abs`, `.werkbank/framework-dirs`)
sowie `vendor/`, `node_modules/`, `.git/`, `testdata/`. Mehrere Module → jedes wird geprüft.

Kompatibilität (oberste Regel):
- Ohne `go.mod` liefert `combine()` exakt das Ergebnis der bisherigen Python-Funktion zurück
  (gleiche Objekte, gleiche Texte). Python-Projekte merken nichts von dieser Datei.
- Mit `go.mod` und Python-Code laufen beide Sprachen; das Ergebnis ist das strengste
  (`common.merge_results`: FAIL > SKIP > WARN > PASS; „nicht anwendbar“ zählt nicht mit).
- Mit `go.mod` und ohne Python-Code läuft der Python-Teil gar nicht (kein „kein Python-Code“-Rot,
  kein ruff/mypy-Lauf ins Leere).
- Werkzeug fehlt → SKIP/TOOL_MISSING (kein Vortäuschen).

Zuordnung (Details: README, Abschnitt „Go-Projekte“):
    B1 gofmt -l .            B2 go vet ./...           B3 go build ./...
    C1 go test ./...         C2 go test -coverprofile + go tool cover -func (Schwelle C2_MIN)
    D1 gosec -fmt=json       D2 govulncheck (nur erreichbare Schwachstellen)
    H2 gocyclo (optional)    D4 bewusst nicht (siehe CHANGELOG)

Konfiguration über Umgebungsvariablen (Wert wird per shlex zerlegt, damit auch ein
Docker-Wrapper wie `docker run --rm -v $PWD:/src -w /src golang:1.25 go` funktioniert):
    WERKBANK_GO            Go-Aufruf (Default `go`)
    WERKBANK_GOFMT         gofmt-Aufruf (Default: aus WERKBANK_GO abgeleitet, sonst `gofmt`)
    WERKBANK_GOSEC         gosec-Aufruf (Default `gosec`)
    WERKBANK_GOVULNCHECK   govulncheck-Aufruf (Default `govulncheck`)
    WERKBANK_GOCYCLO       gocyclo-Aufruf (Default `gocyclo`)
    WERKBANK_GO_TIMEOUT    Timeout je Subprozess in Sekunden (Default 900)
"""
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional, Tuple

try:
    from . import common
except ImportError:
    import common  # type: ignore

GO_MOD = "go.mod"
DEFAULT_TIMEOUT = 900
_MAX_FINDINGS = 20

# Nur für die Go-Erkennung ausgeschlossen (ändert nichts am Verhalten der Python-Checks):
# Vendor-/Testdaten-Verzeichnisse und Python-Umgebungen, in denen ein go.mod nie Projektcode ist.
_GO_PRUNE = {"vendor", "node_modules", ".git", "testdata", ".venv", "venv", "site-packages"}
# Pfadsegmente, deren .go-Dateien gofmt/Komplexität nicht bewerten.
_GO_SKIP_SEGMENTS = {"vendor", "testdata", "node_modules"}


# ---------- Erkennung ----------

@dataclass
class GoModule:
    path: str    # absoluter Pfad des Modulverzeichnisses
    rel: str     # relativ zum Scan-Ziel ("." = Root)

    @property
    def label(self) -> str:
        return "Go" if self.rel == "." else "Go %s" % self.rel


def find_modules(target, exclude_dirs=None, exclude_abs=None) -> List[GoModule]:
    """Alle Go-Module (Verzeichnisse mit go.mod) unter target, sortiert nach Pfad."""
    excl = set(exclude_dirs or common.DEFAULT_EXCLUDE_DIRS) | _GO_PRUNE
    root = os.path.abspath(target)
    mods = []
    for ap, rel in common.iter_files(root, name_suffixes=(GO_MOD,),
                                     exclude_dirs=excl, exclude_abs=exclude_abs):
        if os.path.basename(ap) != GO_MOD:
            continue
        d = os.path.dirname(rel)
        mods.append(GoModule(os.path.dirname(ap), d if d else "."))
    return sorted(mods, key=lambda m: m.rel)


def has_python(target, exclude_dirs=None, exclude_abs=None) -> bool:
    for _ap, _rel in common.iter_files(target, exts={".py"},
                                       exclude_dirs=exclude_dirs, exclude_abs=exclude_abs):
        return True
    return False


def combine(gate, target, exclude_dirs, exclude_abs,
            py: Callable[[], "common.CheckResult"],
            go: Callable[[GoModule], "common.CheckResult"],
            py_relevant: Optional[Callable[[], bool]] = None) -> "common.CheckResult":
    """Zentrale Weiche. Ohne go.mod: exakt das bisherige Python-Ergebnis (py())."""
    mods = find_modules(target, exclude_dirs, exclude_abs)
    if not mods:
        return py()
    parts = []
    relevant = py_relevant() if py_relevant else has_python(target, exclude_dirs, exclude_abs)
    if relevant:
        parts.append(("Python", py()))
    for m in mods:
        parts.append((m.label, go(m)))
    return common.merge_results(gate, parts)


# ---------- Werkzeug-Aufrufe ----------

def _cmd(env_name: str, default: str) -> List[str]:
    raw = os.environ.get(env_name, "").strip()
    if raw:
        try:
            parts = shlex.split(raw)
        except ValueError:
            parts = []
        if parts:
            return parts
    return [default]


def go_cmd() -> List[str]:
    return _cmd("WERKBANK_GO", "go")


def gofmt_cmd() -> List[str]:
    """WERKBANK_GOFMT > aus WERKBANK_GO abgeleitet (letztes Token `go` → `gofmt`) > `gofmt`."""
    if os.environ.get("WERKBANK_GOFMT", "").strip():
        return _cmd("WERKBANK_GOFMT", "gofmt")
    if os.environ.get("WERKBANK_GO", "").strip():
        parts = go_cmd()
        if os.path.basename(parts[-1]) == "go":
            return parts[:-1] + [os.path.join(os.path.dirname(parts[-1]), "gofmt")]
    return ["gofmt"]


def _available(cmd: List[str]) -> bool:
    return bool(shutil.which(cmd[0]))


def _timeout() -> int:
    try:
        v = int(os.environ.get("WERKBANK_GO_TIMEOUT", ""))
        return v if v > 0 else DEFAULT_TIMEOUT
    except ValueError:
        return DEFAULT_TIMEOUT


class _Timeout(Exception):
    pass


def _run(cmd: List[str], cwd: str) -> Tuple[int, str, str]:
    """Führt cmd aus -> (rc, stdout, stderr). Timeout beendet die ganze Prozessgruppe
    (go startet Kindprozesse; sonst bliebe die Pipe offen und der Aufruf hinge)."""
    kw = {"start_new_session": True} if os.name == "posix" else {}
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace", **kw)  # type: ignore[call-overload]
    try:
        out, err = proc.communicate(timeout=_timeout())
    except subprocess.TimeoutExpired:
        try:
            if os.name == "posix":
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
        except OSError:
            pass
        try:
            proc.communicate(timeout=10)
        except (subprocess.SubprocessError, OSError):
            pass
        raise _Timeout() from None
    return proc.returncode, out or "", err or ""


def _exec(gate: str, cmd: List[str], cwd: str):
    """-> ((rc, out, err), None) oder (None, FAIL-Ergebnis) bei Timeout/Startfehler."""
    try:
        return _run(cmd, cwd), None
    except _Timeout:
        return None, common.CheckResult(
            gate, common.FAIL, "Zeitüberschreitung nach %d s (%s)" % (_timeout(), " ".join(cmd[-2:])[:60]))
    except (subprocess.SubprocessError, OSError) as ex:
        return None, common.CheckResult(gate, common.FAIL, "%s-Lauf fehlgeschlagen: %s" % (cmd[0], ex))


def _missing(gate: str, name: str, hint: str = "") -> "common.CheckResult":
    return common.skipped(gate, "%s nicht installiert%s" % (name, (" (%s)" % hint) if hint else ""),
                          common.TOOL_MISSING)


def _fp(module: GoModule, rel: str) -> str:
    rel = rel.replace(os.sep, "/")
    return rel if module.rel == "." else "%s/%s" % (module.rel, rel)


_ERR_LINE = re.compile(r"^(?:vet:\s*)?(?P<f>[^\s:][^:]*\.go):(?P<l>\d+)(?::\d+)?:\s*(?P<m>.*)$")


def _strip_dot(p: str) -> str:
    return p[2:] if p.startswith("./") else p


def _error_findings(module: GoModule, text: str, kind: str) -> List["common.Finding"]:
    out: List[common.Finding] = []
    for line in text.splitlines():
        m = _ERR_LINE.match(line.strip())
        if m and len(out) < _MAX_FINDINGS:
            out.append(common.Finding(_fp(module, _strip_dot(m.group("f"))), int(m.group("l")),
                                      kind, m.group("m")[:80]))
    return out


def _first_line(*texts: str) -> str:
    for t in texts:
        for ln in t.splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                return ln[:80]
    return ""


def _has_go_tests(module: GoModule) -> bool:
    for _root, dirs, files in os.walk(module.path):
        dirs[:] = [d for d in dirs if d not in _GO_SKIP_SEGMENTS and not d.startswith(".")]
        if any(f.endswith("_test.go") for f in files):
            return True
    return False


# ---------- B1 / B2 / B3 ----------

def _resolve_gofmt() -> Optional[List[str]]:
    fmt = gofmt_cmd()
    if _available(fmt):
        return fmt
    # Fallback: gofmt liegt neben der Toolchain (GOROOT/bin), aber nicht auf dem PATH.
    if not os.environ.get("WERKBANK_GOFMT") and not os.environ.get("WERKBANK_GO") and _available(go_cmd()):
        try:
            rc, out, _ = _run(go_cmd() + ["env", "GOROOT"], os.getcwd())
        except (_Timeout, subprocess.SubprocessError, OSError):
            return None
        cand = os.path.join(out.strip(), "bin", "gofmt")
        if rc == 0 and out.strip() and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return [cand]
    return None


def lint(module: GoModule) -> "common.CheckResult":
    """B1: gofmt -l . — leere Ausgabe = PASS."""
    fmt = _resolve_gofmt()
    if fmt is None:
        return _missing("B1", "gofmt", "WERKBANK_GOFMT oder WERKBANK_GO setzen")
    res, fail = _exec("B1", fmt + ["-l", "."], module.path)
    if fail:
        return fail
    rc, out, err = res
    if rc != 0:
        return common.CheckResult("B1", common.FAIL, "gofmt meldet Fehler: %s" % _first_line(err, out),
                                  _error_findings(module, err, "gofmt-error"))
    files = []
    for ln in out.splitlines():
        ln = ln.strip()
        segs = ln.replace("\\", "/").split("/")
        if not ln or any(s in _GO_SKIP_SEGMENTS or (s.startswith(".") and s not in (".", "..")) for s in segs[:-1]):
            continue
        files.append(ln)
    if files:
        return common.CheckResult(
            "B1", common.FAIL, "%d Datei(en) nicht gofmt-formatiert" % len(files),
            [common.Finding(_fp(module, f), 0, "gofmt", "nicht formatiert (gofmt -w)")
             for f in files[:_MAX_FINDINGS]])
    return common.CheckResult("B1", common.PASS, "gofmt sauber")


def _go_tool_gate(gate: str, module: GoModule, args: List[str], label: str, kind: str) -> "common.CheckResult":
    go = go_cmd()
    if not _available(go):
        return _missing(gate, "go", "WERKBANK_GO setzen")
    res, fail = _exec(gate, go + args, module.path)
    if fail:
        return fail
    rc, out, err = res
    if rc == 0:
        return common.CheckResult(gate, common.PASS, "%s sauber" % label)
    return common.CheckResult(gate, common.FAIL, "%s meldet Befunde: %s" % (label, _first_line(err, out)),
                              _error_findings(module, err + "\n" + out, kind))


def typecheck(module: GoModule) -> "common.CheckResult":
    """B2: go vet ./... — typprüft alle Pakete inkl. Testdateien (go build übersieht diese)
    und führt die vet-Analyzer aus. Bewusst NICHT go build (das ist B3): keine Doppelung."""
    return _go_tool_gate("B2", module, ["vet", "./..."], "go vet", "vet")


def build(module: GoModule) -> "common.CheckResult":
    """B3: go build ./..."""
    return _go_tool_gate("B3", module, ["build", "./..."], "go build", "build-error")


# ---------- C1 / C2 ----------

def tests(module: GoModule) -> "common.CheckResult":
    """C1: go test ./..."""
    if not _has_go_tests(module):
        return common.skipped("C1", "keine Go-Tests (*_test.go)", common.NOT_APPLICABLE)
    go = go_cmd()
    if not _available(go):
        return _missing("C1", "go", "WERKBANK_GO setzen")
    res, fail = _exec("C1", go + ["test", "./..."], module.path)
    if fail:
        return fail
    rc, out, err = res
    text = out + "\n" + err
    ok_pkgs = len(re.findall(r"^ok\s", text, flags=re.M))
    if rc == 0:
        return common.CheckResult("C1", common.PASS, "Tests grün (%d Pakete, go test)" % ok_pkgs)
    bad_pkgs = re.findall(r"^FAIL[ \t]+(\S+)", text, flags=re.M)
    summary = "go test rot — %d Paket(e) fehlgeschlagen" % max(len(bad_pkgs), 1)
    findings = [common.Finding(module.rel, 0, "test-failure", p[:80]) for p in bad_pkgs[:_MAX_FINDINGS]]
    return common.CheckResult("C1", common.FAIL, summary,
                              findings or [common.Finding(module.rel, 0, "test-failure", _first_line(err, out) or "go test rot")])


_COVER_TOTAL = re.compile(r"^total:\s+\(statements\)\s+([\d.]+)%", re.M)
_COVER_FILE = ".werkbank-go-cover.out"


def coverage(module: GoModule) -> "common.CheckResult":
    """C2: go test -coverprofile + go tool cover -func; Gesamtwert gegen C2_MIN (Default 70)."""
    if not _has_go_tests(module):
        return common.skipped("C2", "keine Go-Tests (*_test.go)", common.NOT_APPLICABLE)
    go = go_cmd()
    if not _available(go):
        return _missing("C2", "go", "WERKBANK_GO setzen")
    try:
        minimum = float(os.environ.get("C2_MIN", "70"))
    except ValueError:
        minimum = 70.0
    prof = os.path.join(module.path, _COVER_FILE)
    try:
        res, fail = _exec("C2", go + ["test", "-coverprofile=%s" % _COVER_FILE, "./..."], module.path)
        if fail:
            return fail
        rc = res[0]
        if not os.path.isfile(prof):
            return common.CheckResult("C2", common.SKIP, "Coverage-Profil nicht erzeugt (go test rc=%d)" % rc)
        res, fail = _exec("C2", go + ["tool", "cover", "-func=%s" % _COVER_FILE], module.path)
        if fail:
            return fail
        m = _COVER_TOTAL.search(res[1])
    finally:
        try:
            os.remove(prof)
        except OSError:
            pass
    if not m:
        return common.CheckResult("C2", common.SKIP, "Coverage-Report nicht lesbar")
    pct = float(m.group(1))
    if pct >= minimum:
        return common.CheckResult("C2", common.PASS, "Coverage %.1f%% >= %g%%" % (pct, minimum))
    return common.CheckResult("C2", common.FAIL, "Coverage %.1f%% < %g%%" % (pct, minimum))


# ---------- D1 (gosec) ----------

def _slice_json(raw: str) -> str:
    i = raw.find("{")
    return raw[i:] if i >= 0 else ""


def sast(module: GoModule) -> "common.CheckResult":
    """D1: gosec -fmt=json ./... ; High/Medium = FAIL, Low beraten (analog bandit)."""
    sec = _cmd("WERKBANK_GOSEC", "gosec")
    if not _available(sec):
        return _missing("D1", "gosec", "go install github.com/securego/gosec/v2/cmd/gosec@latest")
    res, fail = _exec("D1", sec + ["-fmt=json", "-exclude-dir=vendor", "./..."], module.path)
    if fail:
        return fail
    rc, out, err = res
    try:
        data = json.loads(_slice_json(out) or "null")
    except json.JSONDecodeError:
        data = None
    if not isinstance(data, dict):
        return common.CheckResult("D1", common.FAIL, "gosec-Ausgabe nicht lesbar (rc=%d): %s" % (rc, _first_line(err)))
    blocking, low = [], 0
    for r in data.get("Issues") or []:
        sev = (r.get("severity") or "").upper()
        if sev in ("HIGH", "MEDIUM"):
            f = str(r.get("file", "?")).replace(os.sep, "/")
            if os.path.isabs(f) and f.startswith(module.path.replace(os.sep, "/") + "/"):
                f = _fp(module, f[len(module.path) + 1:])
            m = re.match(r"\d+", str(r.get("line", "0")))
            blocking.append(common.Finding(f, int(m.group(0)) if m else 0,
                                           "sast:%s/%s" % (sev.lower(), r.get("rule_id", "?")),
                                           str(r.get("details", ""))[:60]))
        elif sev == "LOW":
            low += 1
    if blocking:
        return common.CheckResult("D1", common.FAIL, "%d High/Medium-SAST-Befund(e)" % len(blocking),
                                  blocking[:_MAX_FINDINGS])
    errs = data.get("Golang errors") or {}
    if errs:
        n = sum(len(v) if isinstance(v, list) else 1 for v in errs.values())
        return common.CheckResult("D1", common.FAIL,
                                  "gosec konnte %d Quelldatei(en) nicht analysieren (Build-Fehler?)" % n)
    if low:
        return common.CheckResult("D1", common.PASS, "kein High/Medium (%d Low, beraten)" % low)
    return common.CheckResult("D1", common.PASS, "kein SAST-Befund (gosec)")


# ---------- D2 (govulncheck) ----------

def _json_objects(raw: str) -> Iterator[dict]:
    """Liest hintereinander stehende JSON-Objekte (pretty-printed Stream von govulncheck);
    toleriert Text vor dem ersten '{'. Wirft ValueError bei abgebrochenem/ungültigem JSON."""
    dec = json.JSONDecoder()
    i = raw.find("{")
    while 0 <= i < len(raw):
        try:
            obj, end = dec.raw_decode(raw, i)
        except json.JSONDecodeError as ex:
            raise ValueError(str(ex)) from None
        if isinstance(obj, dict):
            yield obj
        i = raw.find("{", end)


def parse_govulncheck(raw: str):
    """-> (erreichbar {osv-id: modul}, nur_importiert {osv-id}, n_objekte).
    Erreichbar = Finding, dessen erste Trace-Stufe eine Funktion nennt (Symbol-Ebene).
    Paket-/Modul-Ebene ohne Funktion ist nicht erreichbar und nur beratend."""
    reachable, weak, n = {}, set(), 0
    for obj in _json_objects(raw):
        n += 1
        f = obj.get("finding")
        if not isinstance(f, dict):
            continue
        trace = f.get("trace") or []
        top = trace[0] if trace and isinstance(trace[0], dict) else {}
        osv = str(f.get("osv", "?"))
        if top.get("function"):
            reachable[osv] = str(top.get("module", "?"))
        else:
            weak.add(osv)
    return reachable, weak - set(reachable), n


def sca(module: GoModule) -> "common.CheckResult":
    """D2: govulncheck -format json ./... ; erreichbare Schwachstellen = FAIL."""
    vuln = _cmd("WERKBANK_GOVULNCHECK", "govulncheck")
    if not _available(vuln):
        return _missing("D2", "govulncheck", "go install golang.org/x/vuln/cmd/govulncheck@latest")
    res, fail = _exec("D2", vuln + ["-format", "json", "./..."], module.path)
    if fail:
        return fail
    rc, out, err = res
    if rc not in (0, 3):    # JSON-Modus endet normal mit 0; 3 = Befunde (Textmodus/ältere Versionen)
        return common.CheckResult("D2", common.FAIL, "govulncheck fehlgeschlagen (rc=%d): %s"
                                  % (rc, _first_line(err, out)))
    try:
        reachable, weak, n = parse_govulncheck(out)
    except ValueError:
        return common.CheckResult("D2", common.FAIL, "govulncheck-Ausgabe nicht lesbar")
    if n == 0:
        return common.CheckResult("D2", common.FAIL, "govulncheck-Ausgabe leer/nicht lesbar")
    if reachable:
        return common.CheckResult(
            "D2", common.FAIL, "%d erreichbare Schwachstelle(n) (govulncheck)" % len(reachable),
            [common.Finding(_fp(module, GO_MOD), 0, "sca:go-vuln",
                            "%s (%s)" % (osv, mod[:40])) for osv, mod in sorted(reachable.items())[:_MAX_FINDINGS]])
    if weak:
        return common.CheckResult("D2", common.PASS,
                                  "keine erreichbaren Schwachstellen (govulncheck; %d nur importiert, beraten)" % len(weak))
    return common.CheckResult("D2", common.PASS, "keine bekannten Schwachstellen (govulncheck)")


# ---------- H2 (gocyclo, optional) ----------

def complexity(module: GoModule, limit: int) -> "common.CheckResult":
    """H2: gocyclo -over <limit> . — optional; ohne Werkzeug SKIP/TOOL_MISSING (warn-Gate)."""
    cyc = _cmd("WERKBANK_GOCYCLO", "gocyclo")
    if not _available(cyc):
        return _missing("H2", "gocyclo", "go install github.com/fzipp/gocyclo/cmd/gocyclo@latest")
    res, fail = _exec("H2", cyc + ["-over", str(limit), "."], module.path)
    if fail:
        return fail
    rc, out, err = res
    findings = []
    for ln in out.splitlines():
        m = re.match(r"^(\d+)\s+(\S+)\s+(\S+)\s+(\S+?):(\d+):\d+\s*$", ln.strip())
        if not m:
            continue
        path = _strip_dot(m.group(4).replace("\\", "/"))
        if any(s in _GO_SKIP_SEGMENTS for s in path.split("/")[:-1]):
            continue
        findings.append(common.Finding(_fp(module, path), int(m.group(5)), "complexity",
                                       "%s() = %s" % (m.group(3), m.group(1))))
    if rc not in (0, 1):
        return common.CheckResult("H2", common.FAIL, "gocyclo fehlgeschlagen (rc=%d): %s" % (rc, _first_line(err, out)))
    if findings:
        return common.CheckResult("H2", common.WARN,
                                  "%d Funktion(en) über Komplexität %d" % (len(findings), limit),
                                  findings[:_MAX_FINDINGS])
    return common.CheckResult("H2", common.PASS, "alle Funktionen <= Komplexität %d (gocyclo)" % limit)
