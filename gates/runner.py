#!/usr/bin/env python3
"""WERKBANK Gate-Runner (deterministisch, kein LLM-Bedarf fuer T1).

- Liest gates/gates.yaml (eigener, eng umrissener YAML-Subset-Parser — keine Dependency).
- Fuehrt Gates gestaffelt aus (Reihenfolge = Ausfuehrung). Block-FAIL bricht ab (fail_fast).
- Implementierte Checks (T1): E1, E2, D3. Nicht-implementierte Gates -> SKIP (ehrlich, nicht 'gruen').
- Schreibt GATE-REPORT.md (ohne Klartext-Secrets/PII).

CLI:  python3 gates/runner.py --target <dir> --report GATE-REPORT.md
"""
import argparse
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import verdict  # noqa: E402
from checks import (  # noqa: E402
    a_spec,
    b_gates,
    c1_tests,
    c2_coverage,
    common,
    d1_sast,
    d3_secret_scan,
    e1_eu_routing,
    e2_pii_scan,
    e3_tenant_isolation,
    e4_audit_log,
    e5_artefakte,
    e6_dpia,
    e7_third_country,
    e8_minimization,
    f1_model_pinning,
    h4_changelog,
)

# Registry: Gate-ID -> Check-Funktion(target, exclude_dirs, exclude_abs, **ctx) -> CheckResult
REGISTRY = {
    "A1": a_spec.run_a1,
    "A2": a_spec.run_a2,
    "A3": a_spec.run_a3,
    "B1": b_gates.run_b1,
    "B2": b_gates.run_b2,
    "B3": b_gates.run_b3,
    "C1": c1_tests.run,
    "C2": c2_coverage.run,
    "D1": d1_sast.run,
    "D3": d3_secret_scan.run,
    "E1": e1_eu_routing.run,
    "E2": e2_pii_scan.run,
    "E3": e3_tenant_isolation.run,
    "E4": e4_audit_log.run,
    "E5": e5_artefakte.run,
    "E6": e6_dpia.run,
    "E7": e7_third_country.run,
    "E8": e8_minimization.run,
    "F1": f1_model_pinning.run,
    "H4": h4_changelog.run,
}


# ---------- Mini-YAML-Parser (nur fuer die Struktur von gates.yaml) ----------

def _scalar(v):
    v = v.strip()
    # gequotete Werte: Inhalt bis zum schliessenden Quote (Inline-Kommentar danach ignorieren)
    q = re.match(r'^"([^"]*)"', v) or re.match(r"^'([^']*)'", v)
    if q:
        return q.group(1)
    # ungequotet: Inline-Kommentar ' # ...' abschneiden
    v = re.split(r"\s+#", v, maxsplit=1)[0].strip()
    if v in ("true", "false"):
        return v == "true"
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def _parse_inline_gate(body):
    gid = re.search(r"\bid:\s*([A-Za-z0-9]+)", body)
    name = re.search(r'\bname:\s*"([^"]*)"', body)
    flags = re.search(r"\bflags:\s*\[([^\]]*)\]", body)
    return {
        "id": gid.group(1) if gid else "?",
        "name": name.group(1) if name else "",
        "flags": [f.strip() for f in flags.group(1).split(",")] if flags else [],
    }


def load_gates(path):
    meta, stages = {}, []
    cur, section, in_gates = None, None, False
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if re.match(r"^[A-Za-z_]+:", line):                # Top-Level-Key
                key = line.split(":", 1)[0]
                section = {"meta": "meta", "stages": "stages",
                           "branch_modules": "branch"}.get(key)
                in_gates = False
                continue
            if section == "meta":
                m = re.match(r"\s+([A-Za-z_]+):\s*(.+?)\s*$", line)
                if m:
                    meta[m.group(1)] = _scalar(m.group(2))
                continue
            if section == "stages":
                sm = re.match(r"\s*-\s*stage:\s*(.+?)\s*$", line)
                if sm:
                    cur = {"stage": sm.group(1).strip(), "desc": "", "gates": []}
                    stages.append(cur)
                    in_gates = False
                    continue
                if cur is not None and not in_gates:
                    dm = re.match(r"\s*desc:\s*(.+?)\s*$", line)
                    if dm:
                        cur["desc"] = _scalar(dm.group(1))
                        continue
                if re.match(r"\s*gates:\s*$", line):
                    in_gates = True
                    continue
                gm = re.match(r"\s*-\s*\{(.+)\}\s*$", line)
                if gm and cur is not None:
                    cur["gates"].append(_parse_inline_gate(gm.group(1)))
                    continue
    return {"meta": meta, "stages": stages}


# ---------- Ausfuehrung ----------

def _self_tooling_exclude(target):
    """Schliesst die Gate-Tooling-Signaturen (gates/checks) aus — aber nur, wenn sie
    UNTERHALB des Scan-Ziels liegen (Self-Lauf). Ein Scanner flaggt nicht seine eigene
    Signaturliste; ein echtes Zielprojekt enthaelt dieses Verzeichnis nicht."""
    tooling = os.path.abspath(os.path.join(HERE, "checks"))
    tgt = os.path.abspath(target)
    if tooling != tgt and (tooling == tgt or tooling.startswith(tgt + os.sep)):
        return {tooling}
    return set()


def run_gates(gates_path, target, report_path, exclude_dirs=None, privacy_dir=None,
              privacy_required=None, audit_log=None, schema_path=None, spec_file=None,
              profile=None, pflichtenheft_path=None):
    spec = load_gates(gates_path)
    fail_fast = spec["meta"].get("fail_fast", True)
    exclude_abs = _self_tooling_exclude(target)
    ctx = {"privacy_dir": privacy_dir, "required": privacy_required,
           "audit_log": audit_log, "schema_path": schema_path, "spec_file": spec_file}

    # Pflichtmenge VOR der Schleife bestimmen: fail_fast darf nur bei einem PFLICHT-Gate
    # abbrechen. Ein nicht-gefordertes block-Gate (z. B. ruff in einem schmalen Profil)
    # darf die Ausfuehrung der geforderten Gates NICHT verhindern (sonst falsches "ungedeckt").
    pflicht = verdict.load_pflichtenheft(pflichtenheft_path or verdict.DEFAULT_PATH)
    profile_name = verdict.select_profile(pflicht, profile)
    required = verdict.resolve_required(pflicht["profiles"], profile_name)
    required_set = set(required)

    results, stage_log = {}, []
    block_fail_gates = []

    for st in spec["stages"]:
        rows = []
        stage_aborted = False
        for g in st["gates"]:
            gid, flags = g["id"], g["flags"]
            is_block = "block" in flags
            if gid in REGISTRY:
                res = REGISTRY[gid](target, exclude_dirs=exclude_dirs, exclude_abs=exclude_abs, **ctx)
            else:
                res = common.skipped(gid, "kein Check implementiert (offen)", common.NOT_IMPLEMENTED)
            results[gid] = {"status": res.status, "summary": res.summary,
                            "findings": res.to_report_lines()[1:], "flags": flags,
                            "name": g["name"], "skip_reason": res.skip_reason}
            rows.append((g, res))
            if is_block and res.status == common.FAIL:
                block_fail_gates.append(gid)
                if gid in required_set:        # nur ein PFLICHT-Block-FAIL bricht ab
                    stage_aborted = True
                    break
        stage_log.append((st, rows, stage_aborted))
        if stage_aborted and fail_fast:
            break

    # Hartes Verdikt aus dem Pflichtenheft (nicht mehr "kein block-FAIL => gruen").
    vd = verdict.compute_verdict(required, results, block_fail_gates)
    overall = vd["verdict"]
    profile_desc = pflicht["profiles"].get(profile_name, {}).get("desc", "")
    _write_report(report_path, spec, stage_log, overall, target, vd, profile_name, profile_desc)
    return {"overall": overall, "results": results, "verdict": vd, "profile": profile_name}


def _write_report(path, spec, stage_log, overall, target, vd, profile_name, profile_desc):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    required = set(vd["required"])
    n_req = len(vd["required"])
    n_pass = len(vd["passed"])
    n_warn = sum(1 for st, rows, _ in stage_log for g, r in rows
                 if r.status in (common.WARN, common.FAIL) and "warn" in g["flags"])

    out = []
    out.append("# GATE-REPORT — target=`%s` — %s" % (os.path.relpath(target), ts))
    out.append("")
    out.append("## Zusammenfassung")
    out.append("- **Ergebnis:** %s" % overall)
    out.append("- **Profil (Pflichtenheft):** `%s` — %s" % (profile_name, profile_desc))
    out.append("- **Pflicht-Gates bestanden:** %d/%d" % (n_pass, n_req))
    out.append("- **Pflicht-Gates VERLETZT (FAIL):** %d" % len(vd["violated"]))
    out.append("- **Pflicht-Gates UNGEDECKT (nicht geprueft):** %d" % len(vd["uncovered"]))
    # Stabile maschinenlesbare Zeile (Ralph-Drift-Gate / stop-hook lesen genau diese):
    out.append("- **Pflicht-Gates ohne PASS:** %d" % (len(vd["violated"]) + len(vd["uncovered"])))
    out.append("- **Optionale Befunde (warn):** %d" % n_warn)
    if vd["extra_block_fails"]:
        out.append("- **Hinweis — Block-Gates rot ausserhalb des Profils (nicht blockend):** %d" % len(vd["extra_block_fails"]))
    out.append("")
    out.append("> **Hartes Gruen:** GRUEN gilt NUR, wenn alle %d Pflicht-Gates aktiv bestanden sind. "
               "SKIP eines Pflicht-Gates (Tool fehlt / kein Check / kein Kontext) ⇒ UNGEDECKT ⇒ ROT." % n_req)
    out.append("")

    if vd["violated"] or vd["uncovered"]:
        out.append("## Warum ROT — Pflicht-Gates ohne PASS")
        for v in vd["violated"]:
            out.append("- **%s VERLETZT** — %s" % (v["gate"], v["summary"]))
        for u in vd["uncovered"]:
            label = common.SKIP_REASON_LABEL.get(u["reason"], u["reason"])
            out.append("- **%s UNGEDECKT** (%s) — %s" % (u["gate"], label, u["summary"]))
        out.append("")

    if vd["extra_block_fails"]:
        out.append("## Hinweis — rote Block-Gates ausserhalb des Profils (beratend, nicht verdikt-relevant)")
        out.append("> Diese Gates sind nicht Teil von `%s`. Fuer harte Pflicht ins Profil aufnehmen." % profile_name)
        for e in vd["extra_block_fails"]:
            out.append("- **%s ROT** — %s" % (e["gate"], e["summary"]))
        out.append("")

    out.append("## Detail je Stufe (Flags ★pflicht = Pflicht-Gate dieses Profils)")
    out.append("| Stufe | Gate | Flags | Ergebnis | Notiz |")
    out.append("|---|---|---|---|---|")
    for st, rows, aborted in stage_log:
        for g, r in rows:
            flags = ",".join(g["flags"]) + (",★pflicht" if g["id"] in required else "")
            out.append("| %s | %s | %s | %s | %s |" % (
                st["stage"], g["id"], flags, r.status, r.summary))
        if aborted:
            out.append("| %s | — | — | ABBRUCH | Stufe nach Block-FAIL abgebrochen (fail_fast) |" % st["stage"])
    # Findings (redigiert)
    findings_lines = []
    for _st, rows, _ in stage_log:
        for _g, r in rows:
            if r.findings:
                findings_lines.extend(r.to_report_lines())
    if findings_lines:
        out.append("")
        out.append("## Funde (redigiert — keine Klartext-Secrets/PII)")
        out.extend(findings_lines)
    out.append("")
    out.append("## Block-Regel")
    out.append("Mind. 1 Block-Gate rot ⇒ kein Push, kein Abhaken. E-Gate rot ⇒ STOPP + Mensch.")
    out.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def main(argv=None):
    ap = argparse.ArgumentParser(description="WERKBANK Gate-Runner")
    ap.add_argument("--target", default=".", help="zu pruefendes Verzeichnis")
    ap.add_argument("--gates", default=os.path.join(HERE, "gates.yaml"))
    ap.add_argument("--report", default="GATE-REPORT.md")
    ap.add_argument("--privacy-dir", default=None, help="Verzeichnis mit DSGVO-Artefakten (aktiviert E5)")
    ap.add_argument("--privacy-required", default=None,
                    help="kommagetrennte Soll-Artefaktliste fuer E5 (statt Default-Set)")
    ap.add_argument("--spec-file", default=None, help="SPEC.md -> aktiviert A1/A2/A3 (Spec-Integrität)")
    ap.add_argument("--audit-log", default=None, help="Audit-Log (JSONL) -> aktiviert E3/E4")
    ap.add_argument("--audit-schema", default=None, help="Schema fuer E4 (Default: templates/AUDIT-LOG.schema.json)")
    ap.add_argument("--exclude", default="", help="zusaetzliche Verzeichnisnamen, kommagetrennt")
    ap.add_argument("--profile", default=None,
                    help="Pflichtenheft-Profil (basis|spec_driven|pii|multi_tenant|werkbank_self); Default aus pflichtenheft.yaml")
    ap.add_argument("--pflichtenheft", default=None, help="Pfad zu pflichtenheft.yaml (Default: gates/pflichtenheft.yaml)")
    ap.add_argument("--ci", action="store_true", help="Exit-Code 1 bei ROT (fuer CI)")
    a = ap.parse_args(argv)
    exclude = set(common.DEFAULT_EXCLUDE_DIRS)
    if a.exclude:
        exclude |= {x.strip() for x in a.exclude.split(",") if x.strip()}
    required = [x.strip() for x in a.privacy_required.split(",")] if a.privacy_required else None
    res = run_gates(a.gates, a.target, a.report, exclude_dirs=exclude,
                    privacy_dir=a.privacy_dir, privacy_required=required,
                    audit_log=a.audit_log, schema_path=a.audit_schema, spec_file=a.spec_file,
                    profile=a.profile, pflichtenheft_path=a.pflichtenheft)
    vd = res["verdict"]
    print("Gate-Runner: %s  Profil=%s  Pflicht bestanden=%d/%d  verletzt=%d  ungedeckt=%d  (Report: %s)" % (
        res["overall"], res["profile"], len(vd["passed"]), len(vd["required"]),
        len(vd["violated"]), len(vd["uncovered"]), a.report))
    if a.ci and res["overall"] == "ROT":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
