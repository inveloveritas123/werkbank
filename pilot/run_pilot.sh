#!/usr/bin/env bash
# Faehrt EINEN audit-tauglichen WERKBANK-Piloten end-to-end und misst Zeit/Verdikt/Gate-Bilanz.
# Aufruf:  bash pilot/run_pilot.sh <name> <profil> "<brief>"
# Erzeugt ein privates GitHub-Repo (Live-Issues bei roten Gates) und ein METRICS.md.
set -uo pipefail
NAME="${1:?name}"; PROFILE="${2:?profil}"; BRIEF="${3:?brief}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_MODEL="${WERKBANK_BUILD_MODEL:-opus}"
PROJ="$HOME/werkbank-pilots/$NAME"
REQ="DATA-FLOW.md,PROCESSING-REGISTER.md,LAWFUL-BASIS.md,DPIA-SCREENING.md,TOMs.md,PROCESSORS-SUBPROCESSORS.md,RETENTION-DELETION.md"

echo "════════ PILOT: $NAME  (Profil $PROFILE) ════════"
rm -rf "$PROJ"; mkdir -p "$PROJ/evidence" "$PROJ/artefakte"; ( cd "$PROJ" && git init -q )

# 1) WERKBANK + BMAD ins Projekt (BMAD-Install lebt hier wirklich)
echo "▶ WERKBANK/BMAD einrichten"
bash "$ROOT/werkbank-init.sh" "$PROJ" >/dev/null 2>&1 || echo "  ! init teilweise"

# 2) GitHub-Repo fuer Live-Issues (privat)
( cd "$PROJ" && gh repo create "$NAME" --private --source=. --remote=origin >/dev/null 2>&1 ) \
  && echo "▶ GitHub-Repo angelegt (privat): $NAME" || echo "  ! gh repo create uebersprungen (existiert?)"

# 3) Phasen-Kommandos (headless, mit Permission-Flag + gepinntem Builder-Modell)
KONZ="claude -p --model $BUILD_MODEL --permission-mode acceptEdits \"Konzipiere mit BMAD (Skills bmad-prd, bmad-create-architecture, bmad-create-epics-and-stories) aus diesem Brief: $BRIEF . Schreibe ALLE Dateien direkt ins AKTUELLE Verzeichnis (KEIN Unterordner anlegen). Erzeuge: SPEC.md (6 Pflichtfelder Ziel/Scope/Datenarten/Akzeptanz/Nicht-Ziele/Handoff, >=2 testbare Akzeptanzkriterien, Handoff-Checkliste [x]); ARCHITECTURE.md; TASKS.md mit self-contained Wellen (Dateien/Verbote/Smoke/Akzeptanz inline); DSGVO-Artefakte unter artefakte/ ($REQ); evidence/audit.log (JSONL). EU-Routing, keine Klartext-PII/Secrets, Modelle gepinnt (kein latest). CHANGELOG.md anlegen.\""
BAUEN="claude -p --model $BUILD_MODEL --permission-mode acceptEdits \"Arbeite die oberste offene Welle in TASKS.md test-first (RED->GREEN->REFACTOR) bis alle Block-Gates gruen sind. Halte EU-Routing/PII-Freiheit/Audit-Log ein. Gib bei fertig exakt <promise>GRUEN</promise> aus.\""
QA="bash $ROOT/pilot/qa_evidence.sh '$PROJ'"

# 4) Pipeline 01->04 mit vollem Kontext, Cross-Model-QA und Live-Issues
echo "▶ Pipeline 01->04 (Profil $PROFILE, max-iter 3, Live-Issues)"
start=$SECONDS
bash "$ROOT/pipeline/run_pipeline.sh" --project "$PROJ" \
  --konzipieren-cmd "$KONZ" --bauen-cmd "$BAUEN" --qa-cmd "$QA" \
  --max-iterations 3 --profile "$PROFILE" --build-profile basis \
  --privacy-dir "$PROJ/artefakte" --privacy-required "$REQ" \
  --audit-log "$PROJ/evidence/audit.log" \
  --gh-issues --apply
rc=$?
dur=$((SECONDS - start))

# 5) Audit-Bilanz aus dem Gate-Report
REP="$PROJ/GATE-REPORT.md"
verdict=$(grep -m1 "Ergebnis:" "$REP" 2>/dev/null | grep -oE "GRUEN|ROT" || echo "?")
pass=$(grep -cE "\| (PASS) \|" "$REP" 2>/dev/null || echo 0)
fail=$(grep -cE "\| (FAIL) \|" "$REP" 2>/dev/null || echo 0)
skip=$(grep -cE "\| (SKIP) \|" "$REP" 2>/dev/null || echo 0)
issues=$( ( cd "$PROJ" && gh issue list --label werkbank-gate --state open --json number -q 'length' ) 2>/dev/null || echo "?")

cat > "$PROJ/METRICS.md" <<EOF
# Pilot-Metriken — $NAME
- Profil: $PROFILE
- Pipeline-Exit: $rc (0=gruen 3=halt)
- Verdikt: $verdict
- Gate-Bilanz: PASS=$pass FAIL=$fail SKIP=$skip
- Offene werkbank-gate-Issues: $issues
- Laufzeit: ${dur}s (~$((dur/60)) min)
EOF
echo "════════ FERTIG $NAME: verdict=$verdict pass=$pass fail=$fail skip=$skip issues=$issues  ${dur}s ════════"
cat "$PROJ/METRICS.md"
