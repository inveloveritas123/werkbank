"""Gate C4 — E2E-Smoke grün (deterministisch, kein LLM).

Bevorzugt **agent-browser** (Vercel) für einen Live-Smoke gegen die laufende App — token-effizient,
emuliert echte Nutzung; Fallback ist **Playwright**. Begründung siehe `docs/WEBINAR-VS-WERKBANK.md`.

Erkennung & Verhalten (kein Vortäuschen):
- agent-browser-Config vorhanden   -> `npx agent-browser test`  (bevorzugt)
- sonst Playwright-Config vorhanden -> `npx playwright test`     (Fallback)
- gar keine E2E-Config             -> SKIP/NOT_APPLICABLE (kein E2E konfiguriert)
- Config vorhanden, aber npx fehlt  -> SKIP/TOOL_MISSING
Returncode 0 -> PASS, sonst FAIL mit redigiertem Output-Tail. Block-Gate.
"""
import os
import shutil
import subprocess
import sys

try:
    from . import common
except ImportError:
    import common  # type: ignore

GATE = "C4"
_PW_CONFIG_NAMES = ("playwright.config.js", "playwright.config.ts", "playwright.config.mjs")
_AB_CONFIG_NAMES = ("agent-browser.config.js", "agent-browser.config.ts", "agent-browser.config.mjs")


def _find_config(target, names):
    for ap, rel in common.iter_files(target):
        if os.path.basename(rel) in names:
            return ap, rel
    return None, None


def _redacted_tail(text, lines=12):
    tail = (text or "").strip().splitlines()[-lines:]
    return "\n".join(common.redact(ln, 64, 0) for ln in tail) if tail else "(keine Ausgabe)"


def _run_e2e(target, argv, tool, cfg_rel):
    """Führt einen E2E-Runner aus. Nutzt die Modul-Globals subprocess/shutil (monkeypatch-bar)."""
    if shutil.which("npx") is None:
        return common.skipped(GATE, "npx/%s nicht installiert" % tool, common.TOOL_MISSING)
    try:
        proc = subprocess.run(
            argv, cwd=os.path.abspath(target), capture_output=True, text=True, timeout=900)
    except (subprocess.SubprocessError, OSError) as ex:
        return common.CheckResult(GATE, common.FAIL, "%s-Lauf nicht möglich: %s" % (tool, ex))
    if proc.returncode == 0:
        return common.CheckResult(GATE, common.PASS, "E2E grün (%s, %s)" % (tool, cfg_rel))
    out = (proc.stdout or "") + (proc.stderr or "")
    return common.CheckResult(GATE, common.FAIL, "E2E rot (%s, %s)" % (tool, cfg_rel),
                              [common.Finding(cfg_rel, 0, "e2e-failure", _redacted_tail(out))])


def run(target, exclude_dirs=None, exclude_abs=None, **_):
    # 1) bevorzugt: agent-browser (Live-Smoke gegen die laufende App, Webinar-Empfehlung)
    ab_abs, ab_rel = _find_config(target, _AB_CONFIG_NAMES)
    if ab_abs:
        return _run_e2e(target, ["npx", "agent-browser", "test"], "agent-browser", ab_rel)
    # 2) Fallback: Playwright
    pw_abs, pw_rel = _find_config(target, _PW_CONFIG_NAMES)
    if pw_abs:
        return _run_e2e(target, ["npx", "playwright", "test"], "Playwright", pw_rel)
    return common.skipped(GATE, "kein E2E konfiguriert (agent-browser/Playwright)", common.NOT_APPLICABLE)


if __name__ == "__main__":
    res = run(sys.argv[1] if len(sys.argv) > 1 else ".")
    print("\n".join(res.to_report_lines()))
    sys.exit(0 if res.status in (common.PASS, common.SKIP) else 1)
