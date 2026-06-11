#!/usr/bin/env bash
# Cross-Model-QA: ein ANDERES Modell als der Builder reviewt das Projekt (BMAD-Review-Skills)
# und schreibt .werkbank/qa-evidence.json mit Verdikten fuer die LLM-Urteils-Gates A4/H6/I1/I2/I3.
# Reviewer != Implementer erfuellt das Vier-Augen-Prinzip (Gate I1/I2 pruefen das hart).
set -uo pipefail
PROJ="${1:?Projektpfad noetig}"
REVIEWER="${WERKBANK_QA_MODEL:-sonnet}"
IMPL="${WERKBANK_BUILD_MODEL:-opus}"
mkdir -p "$PROJ/.werkbank"

read -r -d '' PROMPT <<EOF || true
Du bist der WERKBANK-QA-Reviewer und nutzt ein ANDERES Modell als der Implementer (Vier-Augen).
Pruefe das Projekt unter $PROJ mit den BMAD-Review-Skills (bmad-code-review,
bmad-review-adversarial-general). Schreibe AUSSCHLIESSLICH die Datei
$PROJ/.werkbank/qa-evidence.json mit GENAU dieser Struktur und gueltigem JSON:
{
  "source":"bmad-qa","model":"$REVIEWER","implementer_model":"$IMPL","reviewed_at":"<ISO-8601>",
  "gates":{
    "A4":{"verdict":"pass|fail","summary":"Spec-Widersprueche?","reviewer_model":"$REVIEWER"},
    "H6":{"verdict":"pass|fail","summary":"Drift PRD<->Architektur?","reviewer_model":"$REVIEWER"},
    "I1":{"verdict":"pass|fail","summary":"Vier-Augen-Review Befund","reviewer_model":"$REVIEWER"},
    "I2":{"verdict":"pass|fail","summary":"QA-Tribunal Befund","reviewer_model":"$REVIEWER"},
    "I3":{"verdict":"pass|fail","summary":"Deployment-Validierung gegen User-Flows","reviewer_model":"$REVIEWER"}
  }
}
Setze verdict ehrlich auf "fail", wenn ein echtes Problem vorliegt, sonst "pass". Nur die Datei schreiben.
EOF

claude -p --model "$REVIEWER" --dangerously-skip-permissions "$PROMPT" >/dev/null 2>&1 || true
if [ -f "$PROJ/.werkbank/qa-evidence.json" ]; then
  echo "QA-Evidence geschrieben ($REVIEWER vs $IMPL)"
else
  echo "QA-Evidence FEHLT — LLM-Gates bleiben UNGEDECKT"
fi
