#!/usr/bin/env python3
"""Benchmark — automatischer PDCA-Test (Plan-Do-Check-Act).

Testet den kontrollierten Selbstverbesserungs-Zyklus end-to-end:
1. PLAN/DO: in einer Arbeitskopie eine bekannte Schwäche pflanzen (Platzhalter in einem Artefakt → E5 FAIL).
2. CHECK (vorher): Gate-Lauf, Status erfassen.
3. ACT: die erlaubte kleinste Verbesserung anwenden (Platzhalter füllen/entfernen).
4. CHECK (nachher): Gate-Lauf erneut.
5. Asserten: Schwäche behoben (E5 FAIL→PASS) UND keine Regression (kein Gate PASS→FAIL).
Liefert ein Ergebnis-Dict; nicht-bestanden -> der Aufrufer erstellt ein Issue.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RUNNER = os.path.join(ROOT, "gates", "runner.py")
REQUIRED = ("DATA-FLOW.md,PROCESSING-REGISTER.md,LAWFUL-BASIS.md,DPIA-SCREENING.md,"
            "TOMs.md,PROCESSORS-SUBPROCESSORS.md,RETENTION-DELETION.md")
_ROW = re.compile(r"^\|[^|\n]+\|\s*([A-Z]\d)\s*\|[^|\n]*\|\s*(PASS|FAIL|SKIP|WARN)\s*\|", re.M)


def run_gates(project):
    rep = os.path.join(project, "GATE-REPORT.md")
    cmd = [sys.executable, RUNNER, "--target", project, "--spec-file", os.path.join(project, "SPEC.md"),
           "--privacy-dir", os.path.join(project, "artefakte"), "--privacy-required", REQUIRED,
           "--audit-log", os.path.join(project, "evidence", "audit.log"), "--report", rep, "--ci"]
    rc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300).returncode
    with open(rep, encoding="utf-8") as f:
        text = f.read()
    gates = {m.group(1): m.group(2) for m in _ROW.finditer(text)}
    return {"overall": "GRUEN" if rc == 0 else "ROT", "gates": gates}


def cycle(src_project):
    with tempfile.TemporaryDirectory() as work:
        proj = os.path.join(work, "project")
        shutil.copytree(src_project, proj)
        df = os.path.join(proj, "artefakte", "DATA-FLOW.md")
        with open(df, encoding="utf-8") as f:
            original = f.read()

        # PLAN/DO: Schwäche pflanzen (unausgefüllter Platzhalter -> E5 FAIL)
        with open(df, "w", encoding="utf-8") as f:
            f.write(original + "\n- Offener Punkt: <noch zu ergaenzen>\n")
        before = run_gates(proj)

        # ACT: erlaubte kleinste Verbesserung — Platzhalter entfernen/füllen
        with open(df, "w", encoding="utf-8") as f:
            f.write(original + "\n- Offener Punkt: keiner; Datenfluss vollständig dokumentiert.\n")
        after = run_gates(proj)

        improved = before["gates"].get("E5") == "FAIL" and after["gates"].get("E5") == "PASS"
        regressed = [g for g, s in before["gates"].items()
                     if s == "PASS" and after["gates"].get(g) == "FAIL"]
        return {
            "weakness": "E5 Platzhalter in DATA-FLOW.md",
            "before_E5": before["gates"].get("E5"), "after_E5": after["gates"].get("E5"),
            "before_overall": before["overall"], "after_overall": after["overall"],
            "improved": improved, "regressed": regressed,
            "ok": improved and not regressed and after["overall"] == "GRUEN",
        }


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "project")
    res = cycle(src)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    sys.exit(0 if res["ok"] else 1)
