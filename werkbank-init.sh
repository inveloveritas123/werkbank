#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# werkbank-init.sh — richtet BMAD + kiln-Loop + WERKBANK-Gates in EINEM Projekt ein.
#
#   BMAD     = Methode (Rollen/PRD/Stories)        -> via npx installiert
#   kiln     = Autonomie-Muster (STATE, Loop, 3 Reviews) -> als Scaffolding adaptiert
#   WERKBANK = Governance (deterministische Gates) -> kopiert, sofort lauffähig
#
# Aufruf (ein Befehl pro Projekt):
#   ~/werkbank/werkbank-init.sh [zielverzeichnis]      # default: aktuelles Verzeichnis
#   Optionen:  --no-bmad   BMAD-Install überspringen
#              --force     vorhandene WERKBANK-Dateien überschreiben
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # dieses WERKBANK-Repo
TARGET="."; WITH_BMAD=1; FORCE=0; RALPH_HOOK=0
for arg in "$@"; do
  case "$arg" in
    --no-bmad)    WITH_BMAD=0 ;;
    --force)      FORCE=1 ;;
    --ralph-hook) RALPH_HOOK=1 ;;
    -*)           echo "Unbekannte Option: $arg" >&2; exit 2 ;;
    *)            TARGET="$arg" ;;
  esac
done

mkdir -p "$TARGET"; TARGET="$(cd "$TARGET" && pwd)"
echo "▶ WERKBANK-Init in: $TARGET"
command -v python3 >/dev/null || { echo "✗ python3 fehlt (3.9+ nötig)"; exit 1; }

cp_safe() {  # quelle ziel
  if [ -e "$TARGET/$2" ] && [ "$FORCE" -eq 0 ]; then echo "  · $2 existiert (übersprungen, --force zum Überschreiben)"; return; fi
  mkdir -p "$TARGET/$(dirname "$2")"; cp -R "$SRC/$1" "$TARGET/$2"; echo "  ✓ $2"
}

echo "▶ WERKBANK-Governance kopieren"
if [ ! -e "$TARGET/gates" ] || [ "$FORCE" -eq 1 ]; then
  rm -rf "$TARGET/gates"; cp -R "$SRC/gates" "$TARGET/gates"
  # WERKBANK-interne Tests NICHT mitliefern — das Zielprojekt bringt eigene Tests (unter tests/).
  rm -rf "$TARGET/gates/checks/tests" "$TARGET/gates/checks/__pycache__"
  echo "  ✓ gates (Runner+Checks, ohne interne Tests)"
else
  echo "  · gates existiert (übersprungen, --force zum Überschreiben)"
fi
cp_safe templates templates
cp_safe agents agents
cp_safe workflows workflows
cp_safe orchestrator orchestrator
cp_safe ralph ralph
cp_safe tribunal tribunal
mkdir -p "$TARGET/.github/workflows"
cp_safe .github/workflows/werkbank-gates.yml .github/workflows/werkbank-gates.yml

echo "▶ kiln-State initialisieren"
mkdir -p "$TARGET/.werkbank"
if [ ! -f "$TARGET/.werkbank/STATE.md" ] || [ "$FORCE" -eq 1 ]; then
  cat > "$TARGET/.werkbank/STATE.md" <<EOF
# STATE (kiln, crash-sicher) — $(basename "$TARGET")
## Stand
- Phase: initialisiert. Nächster Schritt: Gate-Baseline + erste Story.
- Pipeline-Position: 00 (Konzipieren ausstehend).
## Letzter Lauf
- werkbank-init ausgeführt.
EOF
  echo "  ✓ .werkbank/STATE.md"
fi
[ -f "$TARGET/.werkbank/BENCHMARK.md" ] || printf '# BENCHMARK (PDCA, neuster oben)\n' > "$TARGET/.werkbank/BENCHMARK.md"
# CHANGELOG fuer Gate H4 (sonst rot beim ersten Lauf)
[ -f "$TARGET/CHANGELOG.md" ] || printf '# CHANGELOG\n\n## %s — init\n- WERKBANK eingerichtet.\n' "$(date +%Y-%m-%d 2>/dev/null || echo 2026-01-01)" > "$TARGET/CHANGELOG.md"

echo "▶ .gitignore härten"
touch "$TARGET/.gitignore"
for line in ".env" ".env.*" "*.key" "*.pem" "secrets/" ".werkbank/STATE.md" "node_modules/" "__pycache__/" "_bmad/" "_bmad-output/" ".claude/"; do
  grep -qxF "$line" "$TARGET/.gitignore" 2>/dev/null || echo "$line" >> "$TARGET/.gitignore"
done
echo "  ✓ .gitignore"

# Bindeglied: CLAUDE.md macht die drei Schichten zu EINER Einheit für den Agenten.
if [ ! -f "$TARGET/CLAUDE.md" ] || [ "$FORCE" -eq 1 ]; then
  cp "$SRC/templates/CLAUDE.werkbank.md" "$TARGET/CLAUDE.md" 2>/dev/null && echo "  ✓ CLAUDE.md (Einheit BMAD+kiln+WERKBANK)"
fi

echo "▶ Git vorbereiten"
if [ ! -d "$TARGET/.git" ]; then ( cd "$TARGET" && git init -q ); echo "  ✓ git init"; fi
( cd "$TARGET" && git rev-parse --verify werkbank-build >/dev/null 2>&1 || git checkout -q -b werkbank-build ) && echo "  ✓ Branch werkbank-build"

if [ "$WITH_BMAD" -eq 1 ]; then
  if command -v npx >/dev/null && command -v node >/dev/null; then
    echo "▶ BMAD installieren (Methode/Rollen) …"
    ( cd "$TARGET" && npx -y bmad-method@6.8.0 install --yes --directory . --modules bmm \
        --tools claude-code --communication-language German --document-output-language German \
        --user-name WERKBANK --output-folder _bmad-output >/dev/null 2>&1 ) \
      && echo "  ✓ BMAD (core+bmm) installiert" \
      || echo "  ! BMAD-Install übersprungen/fehlgeschlagen — später: npx bmad-method install --tools claude-code"
    rm -rf "$TARGET/{output_folder}" 2>/dev/null || true
  else
    echo "  ! node/npx fehlt — BMAD übersprungen. Später: npx bmad-method@6.8.0 install --tools claude-code"
  fi
fi

if [ "$RALPH_HOOK" -eq 1 ]; then
  echo "▶ Ralph-Stop-Hook in .claude/settings.json mergen"
  ( cd "$TARGET" && python3 - <<'PY'
import json, os
p = os.path.join(".claude", "settings.json")
os.makedirs(".claude", exist_ok=True)
try:
    cfg = json.load(open(p, encoding="utf-8"))
except (OSError, ValueError):
    cfg = {}
hook = {"matcher": "*", "hooks": [{"type": "command", "command": "python3 ralph/stop_hook.py"}]}
stop = cfg.setdefault("hooks", {}).setdefault("Stop", [])
if not any("ralph/stop_hook.py" in str(h) for h in stop):
    stop.append(hook)
json.dump(cfg, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("  ✓ .claude/settings.json (Stop-Hook)")
PY
  ) || echo "  ! Hook-Merge übersprungen"
fi

echo "▶ Gate-Baseline"
( cd "$TARGET" && python3 gates/runner.py --target . --report GATE-REPORT.md ) || true

cat <<EOF

✅ Fertig. BMAD + kiln + WERKBANK sind eingerichtet (Einheit via CLAUDE.md).
   Geltung: intern, OHNE echte personenbezogene Kundendaten.

Sofort arbeiten:
  1. Gate-Lauf:   python3 gates/runner.py --target . --report GATE-REPORT.md
  2. Claude Code im Projekt öffnen (CLI 'claude' oder VS-Code-Extension).
     CLAUDE.md wird automatisch gelesen — der Agent kennt damit die Einheit.
  3. Loslegen:    "Lies CLAUDE.md und .werkbank/STATE.md, mach den Gate-Lauf,
                   melde rote Gates + Plan, warte auf GO."
EOF
