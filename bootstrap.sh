#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# bootstrap.sh — WERKBANK auf einem NEUEN System mit EINEM Befehl einrichten.
#
#   curl -fsSL https://raw.githubusercontent.com/inveloveritas123/werkbank/main/bootstrap.sh | bash
#   # oder ein Zielprojekt angeben (+ optionale werkbank-init-Flags):
#   curl -fsSL .../bootstrap.sh | bash -s -- /pfad/zum/projekt --ralph-hook
#
# Klont WERKBANK nach $WERKBANK_HOME (Default ~/werkbank) und richtet das Zielprojekt ein.
# Voraussetzung: git, python3 (>=3.9). Optional: node 20+ (BMAD), gh (PR/Issues), gitleaks (D3+).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
REPO="${WERKBANK_REPO:-https://github.com/inveloveritas123/werkbank.git}"
WERKBANK_HOME="${WERKBANK_HOME:-$HOME/werkbank}"
TARGET="${1:-$PWD}"; [ "$#" -gt 0 ] && shift || true   # Rest = werkbank-init-Flags

echo "▶ WERKBANK-Bootstrap  (HOME=$WERKBANK_HOME, target=$TARGET)"

# --- Prereqs ---
command -v git >/dev/null     || { echo "✗ git fehlt"; exit 1; }
command -v python3 >/dev/null || { echo "✗ python3 (>=3.9) fehlt"; exit 1; }
python3 - <<'PY' || { echo "✗ python3 >= 3.9 nötig"; exit 1; }
import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)
PY
INIT_FLAGS=("$@")
if ! command -v node >/dev/null; then
  echo "  ! node fehlt → BMAD wird übersprungen (Gate-Layer läuft trotzdem)."
  INIT_FLAGS+=("--no-bmad")
fi
command -v gh >/dev/null || echo "  ! gh fehlt → PR/Issue-Features eingeschränkt (Gates/Loop unberührt)."
command -v gitleaks >/dev/null || echo "  ! gitleaks fehlt → D3 nutzt Built-in-Regex (ok)."

# --- WERKBANK holen/aktualisieren ---
if [ -d "$WERKBANK_HOME/.git" ]; then
  echo "▶ WERKBANK aktualisieren"; git -C "$WERKBANK_HOME" pull --ff-only --quiet || echo "  ! pull übersprungen (lokale Änderungen)"
else
  echo "▶ WERKBANK klonen"; git clone --depth 1 --quiet "$REPO" "$WERKBANK_HOME"
fi

# --- Zielprojekt einrichten ---
echo "▶ Projekt einrichten"
bash "$WERKBANK_HOME/werkbank-init.sh" "$TARGET" "${INIT_FLAGS[@]}"

cat <<EOF

✅ Bootstrap fertig. WERKBANK liegt in $WERKBANK_HOME, Projekt in $TARGET ist eingerichtet.
Nächster Schritt: in $TARGET 'claude' öffnen (CLAUDE.md wird gelesen) oder
  python3 gates/runner.py --target . --report GATE-REPORT.md
EOF
