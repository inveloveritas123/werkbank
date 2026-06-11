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
#
# ─────────────────────────────────────────────────────────────────────────────
# SICHERHEIT — "curl | bash" lädt und führt fremden Code ungeprüft aus.
# Für Wegwerf-/Testsysteme ist die Convenience-Pipe oben ok. Für echte oder
# Kundensysteme NICHT blind pipen, sondern erst herunterladen, prüfen, dann starten:
#
#   # 1) Herunterladen — auf einen RELEASE-TAG gepinnt (nicht 'main'):
#   curl -fsSL https://raw.githubusercontent.com/inveloveritas123/werkbank/v1.0/bootstrap.sh -o bootstrap.sh
#   # 2) Prüfsumme gegen den veröffentlichten Hash vergleichen:
#   shasum -a 256 bootstrap.sh
#   # 3) Selbst lesen — verstehen, was läuft:
#   less bootstrap.sh
#   # 4) Erst dann ausführen, gepinnt auf denselben Ref:
#   WERKBANK_REF=v1.0 bash bootstrap.sh
#
# Pinning (empfohlen für Produktiv-/Kundensysteme):
#   WERKBANK_REF=<tag|branch|commit>   Genau diesen Ref klonen/auschecken (Default: main).
#   WERKBANK_EXPECT_SHA=<commit-sha>   Harter Integritäts-Pin: bricht ab, wenn der
#                                      ausgecheckte Commit nicht exakt diesem SHA entspricht.
# Details: docs/SICHERE-INSTALLATION.md
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
REPO="${WERKBANK_REPO:-https://github.com/inveloveritas123/werkbank.git}"
WERKBANK_HOME="${WERKBANK_HOME:-$HOME/werkbank}"
WERKBANK_REF="${WERKBANK_REF:-main}"          # git-Ref (Tag/Branch/Commit), der installiert wird
WERKBANK_EXPECT_SHA="${WERKBANK_EXPECT_SHA:-}" # optionaler harter Integritäts-Pin (Commit-SHA)
TARGET="${1:-$PWD}"; [ "$#" -gt 0 ] && shift || true   # Rest = werkbank-init-Flags

echo "▶ WERKBANK-Bootstrap  (HOME=$WERKBANK_HOME, target=$TARGET, ref=$WERKBANK_REF)"

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

# --- WERKBANK holen/aktualisieren (gepinnt auf $WERKBANK_REF) ---
if [ -d "$WERKBANK_HOME/.git" ]; then
  # Bestehender Klon: deterministisch auf den gepinnten Ref bringen (Tag/Branch/Commit).
  echo "▶ WERKBANK aktualisieren → ref=$WERKBANK_REF"
  git -C "$WERKBANK_HOME" fetch --depth 1 --quiet origin "$WERKBANK_REF"
  git -C "$WERKBANK_HOME" checkout --quiet --force FETCH_HEAD
  git -C "$WERKBANK_HOME" reset --hard --quiet FETCH_HEAD
else
  echo "▶ WERKBANK klonen → ref=$WERKBANK_REF"
  # --branch akzeptiert sowohl Branches als auch Tags.
  git clone --depth 1 --quiet --branch "$WERKBANK_REF" "$REPO" "$WERKBANK_HOME"
fi

# --- Integrität: ausgecheckten Commit ermitteln, optional hart pinnen ---
ACTUAL_SHA="$(git -C "$WERKBANK_HOME" rev-parse HEAD)"
if [ -n "$WERKBANK_EXPECT_SHA" ] && [ "$ACTUAL_SHA" != "$WERKBANK_EXPECT_SHA" ]; then
  echo "✗ Integritäts-Pin verletzt:"
  echo "    erwartet: $WERKBANK_EXPECT_SHA"
  echo "    erhalten: $ACTUAL_SHA"
  echo "  Installation abgebrochen — kein Setup ausgeführt."
  exit 1
fi
echo "▶ WERKBANK @ $ACTUAL_SHA (ref=$WERKBANK_REF)"

# --- Zielprojekt einrichten ---
echo "▶ Projekt einrichten"
bash "$WERKBANK_HOME/werkbank-init.sh" "$TARGET" ${INIT_FLAGS[@]+"${INIT_FLAGS[@]}"}

cat <<EOF

✅ Bootstrap fertig. WERKBANK liegt in $WERKBANK_HOME, Projekt in $TARGET ist eingerichtet.
Nächster Schritt: in $TARGET 'claude' öffnen (CLAUDE.md wird gelesen) oder
  python3 gates/runner.py --target . --report GATE-REPORT.md
EOF
